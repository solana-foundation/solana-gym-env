import base64
import pdb
import base58
import gymnasium as gym
import numpy as np
import asyncio
from contextlib import asynccontextmanager
import logging
import json
import shutil
import os
import signal
from dotenv import load_dotenv
from os.path import dirname, join

from solana.rpc.async_api import AsyncClient, GetTransactionResp
from solders.transaction import Transaction
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.system_program import transfer, TransferParams, create_nonce_account
from solders.message import MessageV0, to_bytes_versioned
from solders.pubkey import Pubkey
from solders.null_signer import NullSigner
from solders.signature import Signature

from voyager.known_programs import KNOWN_PROGRAM_IDS
from voyager.skill_manager.ts_skill_manager import TypeScriptSkillManager

load_dotenv(join(dirname(__file__), '.env'))

READY_TOKEN = b"Connection established."          # surfpool prints this when ready
# ──────────────────────────────────────────────────────────────────────────
#  Async context-manager that owns the Surfpool process life-cycle
# ──────────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def _surfpool_validator(rpc_url: str, *, backtrace: bool = True):
    """
    Async context manager that:
      • launches `surfpool start -u <rpc_url>`
      • waits until it prints the READY_TOKEN
      • yields the process object while the validator is live
      • always terminates the whole process-group on exit
    """
    if shutil.which("surfpool") is None:
        raise FileNotFoundError(
            "'surfpool' not found in PATH; install it or adjust PATH."
        )

    env = os.environ.copy()
    if backtrace:
        env["RUST_BACKTRACE"] = "1"
    # Disable raw-mode attempts in many TTY crates (crossterm/termion)
    env["CROSSTERM_DISABLE_RAW_MODE"] = "1"

    cmd = ["surfpool", "start", "--no-tui", "-u", rpc_url]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        start_new_session=True,        # own pgid → easy to kill
        env=env,
    )
    logging.info("surfpool [%s] launched", proc.pid)

    try:
        # Block until Surfpool is actually serving RPC or abort early
        while True:
            line = await proc.stdout.readline()
            if not line:                       # died before ready
                raise RuntimeError("surfpool exited before becoming ready")
            logging.debug("[surfpool] %s", line.decode().rstrip())
            if READY_TOKEN in line:
                break
        yield proc                             # ── control goes back to caller
    finally:
        if proc.returncode is None:
            logging.info("Stopping surfpool [%s] …", proc.pid)
            try:
                os.killpg(proc.pid, signal.SIGTERM)
                await asyncio.wait_for(proc.wait(), timeout=8)
            except asyncio.TimeoutError:
                logging.warning("surfpool unresponsive; killing")
                os.killpg(proc.pid, signal.SIGKILL)
                await proc.wait()
            except ProcessLookupError as e:
                logging.warning("surfpool process already terminated")
                
        logging.info("surfpool shut down")

class SurfpoolEnv(gym.Env):
    """
    The low-level Solana environment that interfaces directly with the surfpool validator.
    This environment is responsible for:
    - Managing the surfpool validator subprocess.
    - Providing a rich observation of the on-chain state.
    - Executing pre-formed transactions.
    """
    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com", ws_url: str = "ws://localhost:8900"):
        super().__init__()

        self.rpc_url = rpc_url
        self.ws_url = ws_url
        # The client for the Voyager environment will connect to the surfpool instance
        self.client = AsyncClient("http://127.0.0.1:8899", "confirmed")
        self.test_validator_process = None
        self.agent_keypair = Keypair()

        self.tx_fetch_rpc_url = os.getenv("SOLANA_TX_FETCH_RPC_URL", "https://api.mainnet-beta.solana.com")
        self.tx_fetch_client = AsyncClient(self.tx_fetch_rpc_url)

        self.program_instructions_seen = {}
        self.last_observation = None
        self.last_tx_receipt = None
        self._validator_cm = None       # will hold the context-manager
        self._validator_proc = None     # the running subprocess
        self.total_reward = 0           # Track cumulative reward for this episode.Process
        
        # Transaction efficiency tracking
        self.last_tx_instruction_count = 0
        self.last_tx_reward = 0


    async def _get_observation(self, last_tx_result=None):
        # In a real implementation, you would fetch this data from the chain
        # Get unique programs from the instructions seen
        unique_programs = {str(k[0]) for k in self.program_instructions_seen.keys()}
        
        # Build discovered_instructions_by_program mapping
        discovered_instructions_by_program = {}
        for (program_id, instruction_id), _ in self.program_instructions_seen.items():
            program_id_str = str(program_id)
            if program_id_str not in discovered_instructions_by_program:
                discovered_instructions_by_program[program_id_str] = []
            if instruction_id not in discovered_instructions_by_program[program_id_str]:
                discovered_instructions_by_program[program_id_str].append(instruction_id)
        
        # Sort instruction IDs for each program for consistency
        for program_id in discovered_instructions_by_program:
            discovered_instructions_by_program[program_id].sort()
        
        obs = {
            "sol_balance": 0,
            "agent_pubkey": str(self.agent_keypair.pubkey()),
            "block_height": 0,
            "discovered_programs": len(unique_programs),
            "discovered_program_list": list(unique_programs),  # Unique program IDs
            "discovered_instructions_by_program": discovered_instructions_by_program,
            "total_reward": len(self.program_instructions_seen),
            "unique_instructions_found": len(self.program_instructions_seen),
            "last_tx_instruction_count": self.last_tx_instruction_count,
            "last_tx_reward": self.last_tx_reward
        }

        try:
            # Get basic block info
            block_height = await self.client.get_block_height()
            obs["block_height"] = block_height.value
            
            # Get agent SOL balance (as the first token)
            balance = await self.client.get_balance(self.agent_keypair.pubkey())
            obs["sol_balance"] = balance.value / 1e9 # Convert lamports to SOL

            # TODO: Get other token balances

        except Exception as e:
            logging.error(f"Error getting observation: {e}", exc_info=True)

        if last_tx_result:
            # The receipt is a JSON string, so we need to parse it
            receipt_dict = json.loads(last_tx_result)
            if receipt_dict.get("meta", {}).get("err") is None:
                obs["last_tx_success"] = 1
            else:
                obs["last_tx_success"] = 0
                obs["last_tx_error"] = str(receipt_dict.get("meta", {}).get("err"))

        return [["observe", obs]]

    def _partial_sign_transaction(self, tx_bytes: bytes, additional_signers: list[Keypair]) -> VersionedTransaction:
        """
        Add additional signatures to a VersionedTransaction without overwriting existing ones.
        
        This implements partial signing for VersionedTransactions, similar to the 
        partialSign method in the legacy Transaction class.
        
        Args:
            tx_bytes: The serialized transaction bytes
            additional_signers: List of Keypair objects to sign with
            
        Returns:
            A VersionedTransaction with the additional signatures
        """
        # Deserialize the transaction
        tx = VersionedTransaction.from_bytes(tx_bytes)
        message = to_bytes_versioned(tx.message)
        
        sigs = tx.signatures
        for idx, signer in enumerate(additional_signers):
            sig = signer.sign_message(message)
            sigs[idx] = sig

        # NOTE: we have to assign the signatures all at once, we cannot assign by index
        # due to quirk in the solders library / rust bridge
        tx.signatures = sigs
        return tx

    async def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        try:
            if self._validator_cm:
                await self._validator_cm.__aexit__(None, None, None)
        except Exception as e:
            logging.error(f"Error closing validator: {e}", exc_info=True)

        # 2. Launch a fresh validator and wait until it’s live
        self._validator_cm = _surfpool_validator(self.rpc_url)
        self._validator_proc = await self._validator_cm.__aenter__()

        # Create a new agent for the episode
        self.agent_keypair = Keypair()
        # DO NOT reset program_instructions_seen - it should persist across episodes!
        # self.program_instructions_seen = {}  # <-- This was the bug!
        # self.total_reward = 0
        
        # Reset transaction tracking
        self.last_tx_instruction_count = 0
        self.last_tx_reward = 0
        
        # Fund the agent
        try:
            logging.info(f"Airdropping SOL to {self.agent_keypair.pubkey()}...")
            airdrop_sig = await self.client.request_airdrop(self.agent_keypair.pubkey(), 2 * 10**9) # 2 SOL
            await self.client.confirm_transaction(airdrop_sig.value, "confirmed", 30.0)
            logging.info("Airdrop successful.")
        except Exception as e:
            logging.error(f"Airdrop failed: {e}", exc_info=True)
            return None, {"error": f"Airdrop failed: {e}"}

        self.last_tx_receipt = None
        observation = await self._get_observation()
        info = {} # No extra info on reset
        return observation, info


    async def step2(self, code: str, programs: list[str], skill_manager: TypeScriptSkillManager):
        """
        Workaround to make it easy to call step()
        """
        result = skill_manager.evaluate_code(
            code,
            programs,
            str(self.agent_keypair.pubkey()),
            60000  # Increased to 60 seconds for slow connections
        )
        events = []
        if result.get('success', False) and result.get('serialized_tx'):
            # Deserialize the transaction
            tx_bytes = base64.b64decode(result['serialized_tx'])
            tx = self._partial_sign_transaction(tx_bytes, [self.agent_keypair])
            
            obs, reward, terminated, truncated, info = await self.step(tx)
            events.append(("info", info))
            # obs is already in the format [["observe", obs_dict]], so we need to extend, not append
            events.extend(obs)
            return events, reward, terminated, truncated, info
        else:
            # Pass error information through
            error_info = {
                "error": result.get("reason", "Unknown error"),
                "trace": result.get("trace", ""),
                "stdout": result.get("stdout", ""),
                "stderr": result.get("stderr", "")
            }
            
            # Get observation with error details
            obs = await self._get_observation()
            # Add error details to the observation
            if obs and len(obs) > 0 and len(obs[0]) > 1:
                obs[0][1]["error"] = error_info["error"]
                obs[0][1]["error_trace"] = error_info["trace"]
            
            events.append(("error", error_info))
            events.extend(obs)
            return events, 0, False, False, error_info

    async def code_loop_step(self, code: str, programs: list[str], skill_manager: TypeScriptSkillManager):
        """
        Workaround to make it easy to call step()
        """
        result = skill_manager.evaluate_code_loop(
            code,
            str(self.agent_keypair.pubkey()),
            blockhash
        )
        events = []
        if result.get('success', False) and result.get('serialized_tx'):
            # Deserialize the transaction
            tx_bytes = base64.b64decode(result['serialized_tx'])
            tx = self._partial_sign_transaction(tx_bytes, [self.agent_keypair])
            
            obs, reward, terminated, truncated, info = await self.step(tx)
            events.append(("info", info))
            # obs is already in the format [["observe", obs_dict]], so we need to extend, not append
            events.extend(obs)
            return events, reward, terminated, truncated, info
        else:
            # Pass error information through
            error_info = {
                "error": result.get("reason", "Unknown error"),
                "trace": result.get("trace", ""),
                "stdout": result.get("stdout", ""),
                "stderr": result.get("stderr", "")
            }
            
            # Get observation with error details
            obs = await self._get_observation()
            # Add error details to the observation
            if obs and len(obs) > 0 and len(obs[0]) > 1:
                obs[0][1]["error"] = error_info["error"]
                obs[0][1]["error_trace"] = error_info["trace"]
            
            events.append(("error", error_info))
            events.extend(obs)
            return events, 0, False, False, error_info


    async def step(self, tx):
        """
        Executes a pre-signed transaction on the Solana network.
        This is the core function of the low-level environment.
        The transaction must be signed before being passed to this method.
        """
        self.last_tx_receipt = None
        try:
            # The modern send_transaction expects a signed transaction
            sig = await self.client.send_transaction(tx)
            
            # The commitment level for confirmation should be high enough
            await self.client.confirm_transaction(sig.value, "confirmed", 30.0)
            
            # Fetch the confirmed transaction
            result = await self.client.get_transaction(sig.value, commitment="confirmed")
            
            if not result or not result.value:
                 raise Exception(f"Transaction result not found for signature {sig.value}")

            tx_receipt = result.value.transaction.to_json()
            self.last_tx_receipt = tx_receipt

        except Exception as e:
            logging.error(f"Error sending transaction: {e}", exc_info=True)
            obs = await self._get_observation()
            # Pass the error in the info dict
            return obs, 0, False, False, {"error": str(e)}
        except BaseException as e:
            logging.error(f"Panic in send_transaction: {e}", exc_info=True)
            obs = await self._get_observation()
            # Pass the error in the info dict
            # For now, treat this specific error as a success for testing
            if "missing field `data`" in str(e):
                # This is likely a parsing issue with the response
                # The transaction might have actually succeeded
                return obs, 0, False, False, {"error": str(e), "possible_success": True}
            return obs, 0, False, False, {"error": str(e)}

        self.last_tx_receipt = tx_receipt
        
        # Extract programs from this transaction for the info dict
        ordered_instructions = self._get_ordered_instructions(result)
        programs_in_tx = list({str(ix['program_id']) for ix in ordered_instructions})
        
        # Track instruction count for this transaction
        self.last_tx_instruction_count = len(ordered_instructions)
        
        reward = self._calculate_reward(result)
        self.last_tx_reward = reward
        self.total_reward += reward
        
        # Get observation after updating metrics
        obs = await self._get_observation(last_tx_result=tx_receipt)
        
        return obs, reward, False, False, { 
            "tx_sig": str(sig.value), 
            "tx_meta": result.value.to_json(),
            "programs_interacted": programs_in_tx,
            "reward": reward
        }

    def _get_ordered_instructions(self, tx_result: GetTransactionResp) -> list[dict[str, bytes]]:
        inner_instructions = {ix.index: ix.instructions for ix in tx_result.value.transaction.meta.inner_instructions}
        message = tx_result.value.transaction.transaction.message
        ordered_instructions = []
        for idx, ix in enumerate(message.instructions):
            ordered_instructions.append({
                'program_id': message.account_keys[ix.program_id_index],
                'data': base58.b58decode(ix.data),
            })
            # pdb.set_trace()
            ordered_instructions.extend(
                [{
                    'program_id': message.account_keys[inner_instruction.program_id_index],
                    'data': base58.b58decode(inner_instruction.data),
                } for inner_instruction in inner_instructions[idx]]
            )
        return ordered_instructions
    
    def _calculate_reward(self, tx_result: GetTransactionResp) -> float:
        if tx_result.value.transaction.meta.err:
            return 0

        ordered_instructions = self._get_ordered_instructions(tx_result)

        reward = 0
        for ix in ordered_instructions:
            # Check if instruction data is not empty before accessing index 0
            if len(ix['data']) > 0:
                discriminator = ix['data'][0]
            else:
                discriminator = 0  # Default discriminator for empty data
            
            key = (ix['program_id'], discriminator)
            if key not in self.program_instructions_seen and key[0] == "KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD":
                reward += 1
                self.program_instructions_seen[key] = True
                logging.info(f"Discovered new program instruction ({str(key[0])}, {str(key[1])})")
        return reward
    
    def render(self, mode="human"):
        logging.info("Rendering not implemented for this environment.")
        pass

    async def close(self):
        if self._validator_cm:
            await self._validator_cm.__aexit__(None, None, None)
            self._validator_cm = self._validator_proc = None

            if self.client:
                await self.client.close()
            logging.info("SurfpoolEnv closed.")
        logging.info("SurfpoolEnv closed.")

    async def fetch_transactions(self, program_id: str = None):
        """Fetches example transactions for a specific program."""
        logging.info(f"=== FETCH_TX_EXAMPLES called for program: {program_id} ===")
        
        try:
            # Fetch recent transactions from the tx fetch RPC (e.g., mainnet)
            # This allows us to get real transaction examples even in local surfpool
            logging.info(f"Fetching signatures from: {self.tx_fetch_rpc_url}")
            signatures = await self.tx_fetch_client.get_signatures_for_address(
                Pubkey.from_string(program_id),
                limit=10  # Limit to avoid too many requests
            )
            
            logging.info(f"Found {len(signatures.value)} signatures")
            
            examples = []
            # Only process first 3 transactions to avoid timeouts
            for i, sig_info in enumerate(signatures.value[:3]):
                try:
                    logging.info(f"Fetching transaction {i+1}/3: {sig_info.signature}")
                    tx = await self.tx_fetch_client.get_transaction(
                        sig_info.signature,
                        encoding="json",
                        max_supported_transaction_version=0
                    )
                    
                    if tx and tx.value:
                        logging.info(f"Successfully fetched transaction {i+1}")
                        # Extract ALL logs - no truncation
                        logs = tx.value.transaction.meta.log_messages or []
                        
                        # Parse ALL instructions (outer + inner) with proper indexing
                        instructions = []
                        
                        # Parse outer instructions
                        outer_ixs = tx.value.transaction.transaction.message.instructions or []
                        for outer_idx, ix in enumerate(outer_ixs):
                            instructions.append({
                                "id": str(outer_idx),
                                "program_id_index": ix.program_id_index,
                                "accounts": [str(a) for a in ix.accounts],
                                "data": ix.data,
                                "depth": 0
                            })
                    
                        # Parse inner instructions
                        inner_ixs = tx.value.transaction.meta.inner_instructions or []
                        for outer_idx, inner_group in enumerate(inner_ixs):
                            if inner_group and inner_group.instructions:
                                for inner_idx, inner_ix in enumerate(inner_group.instructions):
                                    instructions.append({
                                        "id": f"{outer_idx}.{inner_idx}",
                                        "program_id_index": inner_ix.program_id_index,
                                        "accounts": [str(a) for a in inner_ix.accounts],
                                        "data": inner_ix.data,
                                        "depth": 1
                                    })
                    
                        # Sort instructions by execution order
                        # This ensures "0", "0.0", "0.1", "1", "1.0", "2" ordering
                        instructions.sort(key=lambda x: [int(part) for part in x["id"].split(".")])
                        
                        examples.append({
                            "signature": str(sig_info.signature),
                            "success": tx.value.transaction.meta.err is None,
                            "error": str(tx.value.transaction.meta.err),
                            "logs": logs,  # ALL logs, no limit
                            "instructions": instructions,  # Sorted by execution order
                            "accounts": [str(a) for a in tx.value.transaction.transaction.message.account_keys],
                            "slot": tx.value.slot,
                        })
                except Exception as e:
                    logging.warning(f"Failed to fetch transaction {i+1}: {e}")
                    # Continue with next transaction
                    continue
            
            info = {
                "program_id": program_id,
                "program_name": KNOWN_PROGRAM_IDS.get(program_id, "Unknown"),
                "examples": examples,
                "count": len(examples),
                "status": "success"
            }
            
            return info  # No reward for fetching
            
        except Exception as e:
            logging.error(f"Error fetching transactions: {e}")
            logging.error(f"Exception type: {type(e)}")
            logging.error(f"Exception details: {repr(e)}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            return {"error": f"Failed to fetch transactions: {str(e)}"}


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    
    async def main():
        env = SurfpoolEnv()
        obs, info = await env.reset()
        logging.info("Environment reset.")
        logging.info(f"Initial Observation: {obs}")

        async def make_tx(ixs, signers=[]):
            latest_blockhash = await env.client.get_latest_blockhash()
            message = MessageV0.try_compile(
                payer=env.agent_keypair.pubkey(),
                instructions=ixs,
                address_lookup_table_accounts=[],
                recent_blockhash=latest_blockhash.value.blockhash
            )
            tx = VersionedTransaction(message, [env.agent_keypair] + signers)
            return tx

        def render_step(step_result):
            obs, reward, terminated, truncated, info = step_result
            logging.info("\n--- Step Result ---")
            logging.info(f"Observation: {obs}")
            logging.info(f"Reward: {reward}")
            logging.info(f"Terminated: {terminated}")
            logging.info(f"Truncated: {truncated}")
            logging.info(f"Info: {info}")


        if obs is not None:
            # Test 1: Simple transfer
            recipient = Keypair().pubkey()
            instruction = transfer(
                TransferParams(
                    from_pubkey=env.agent_keypair.pubkey(),
                    to_pubkey=recipient,
                    lamports=1000
                )
            )
            tx = await make_tx([instruction])
            render_step(await env.step(tx))
            
            # Test 2: Another transfer with different amount
            instruction = transfer(
                TransferParams(
                    from_pubkey=env.agent_keypair.pubkey(),
                    to_pubkey=recipient,
                    lamports=1001
                )
            )
            tx = await make_tx([instruction])
            render_step(await env.step(tx))

            # Test 3: Nonce account creation (requires multiple signers)
            nonce = Keypair()
            instructions = create_nonce_account(
                env.agent_keypair.pubkey(),
                nonce.pubkey(),
                env.agent_keypair.pubkey(),
                1_447_680,
            )
            tx = await make_tx(instructions, [nonce])
            render_step(await env.step(tx))
            
            # Test 4: Test partial signing with createAccount instruction
            logging.info("\n--- Testing Partial Signing ---")
            
            # Create a transaction that requires multiple signers
            new_account = Keypair()
            from solders.system_program import create_account, CreateAccountParams
            
            # Calculate minimum rent exemption for 0 bytes
            rent_exempt_balance = 890880  # Minimum for 0 bytes on Solana
            
            create_account_ix = create_account(
                CreateAccountParams(
                    from_pubkey=env.agent_keypair.pubkey(),
                    to_pubkey=new_account.pubkey(),
                    lamports=rent_exempt_balance,
                    space=0,
                    owner=Pubkey.from_string("11111111111111111111111111111111")
                )
            )
            
            # Create transaction but only sign with new_account first (simulating partial signing from TS)
            message = MessageV0.try_compile(
                payer=env.agent_keypair.pubkey(),
                instructions=[create_account_ix],
                address_lookup_table_accounts=[],
                recent_blockhash=(await env.client.get_latest_blockhash()).value.blockhash
            )
            
            # Create the transaction with these signatures
            partial_tx = VersionedTransaction(message, [NullSigner(env.agent_keypair.pubkey()), new_account])
            
            # Serialize it
            partial_tx_bytes = bytes(partial_tx)
            logging.info(f"Partial tx: {base64.b64encode(partial_tx_bytes).decode()}")
            
            # Now test our partial signing method
            logging.info(f"Testing partial signing - adding agent signature to partially signed tx")
            fully_signed_tx = env._partial_sign_transaction(partial_tx_bytes, [env.agent_keypair])
            logging.info(f"Fully signed tx: {base64.b64encode(bytes(fully_signed_tx)).decode()}")
            logging.info(f"Fully signed tx: {fully_signed_tx.signatures}")
            logging.info(f"Fully signed tx: {fully_signed_tx.verify_with_results()}")
            
            # Verify signatures
            logging.info(f"Signatures after partial signing:")
            for i, sig in enumerate(fully_signed_tx.signatures):
                if sig and sig != Signature.default():
                    # Convert signature to string for display
                    sig_str = str(sig)
                    logging.info(f"  Index {i}: {sig_str[:8]}... (present)")
                else:
                    logging.info(f"  Index {i}: None or default")
            
            # Send the transaction
            render_step(await env.step(fully_signed_tx))


        await env.close()

    asyncio.run(main())
