import asyncio
import base64
import logging
import os
import re
import json
import uuid
import pdb
from datetime import datetime
from typing import Dict, Any, List, Optional

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from solders.transaction import Transaction
from dotenv import load_dotenv

from voyager.skill_manager.ts_skill_manager import TypeScriptSkillManager
from voyager.surfpool_env import SurfpoolEnv, _surfpool_validator
from voyager.prompts import load_prompt

load_dotenv()

class CodeLoopExplorer:
    """
    A simplified explorer that extracts TypeScript code blocks from agent responses
    and executes them directly without using function calling.
    """
    
    def __init__(
        self,
        model_name: str = "openrouter/horizon-beta",
        run_index: int = 0,
        max_messages: int = 200,
        checkpoint_dir: str = "ckpt/code_loop",
        resume: bool = False,
        verbose: bool = True,
        code_file: str = None
    ):
        self.model_name = model_name
        self.run_index = run_index
        self.max_messages = max_messages
        self.checkpoint_dir = checkpoint_dir
        self.resume = resume
        self.verbose = verbose
        self.code_file = code_file or "voyager/skill_runner/code_loop_code.ts"
        
        # Generate unique run ID
        self.run_id = f"code_loop_{datetime.now().strftime('%y-%m-%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Initialize LangChain ChatOpenAI for OpenRouter
        self.llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            model=model_name,
            api_key=os.getenv("OPENROUTER_API_KEY"),
            temperature=0.7,
        )
        
        # Initialize skill manager
        self.skill_manager = TypeScriptSkillManager(
            model_name=model_name,
            temperature=0.0,
            retrieval_top_k=5,
            request_timeout=120,
            ckpt_dir=checkpoint_dir,
            resume=resume,
        )
        
        # Regex pattern for extracting TypeScript/JavaScript code blocks
        self.code_pattern = re.compile(r"```(?:javascript|js|typescript|ts)(.*?)```", re.DOTALL)
        
        # Metrics tracking
        self.metrics = {
            "model": model_name,
            "run_index": run_index,
            "run_id": self.run_id,
            "start_time": datetime.now().isoformat(),
            "messages": [],
            "cumulative_rewards": [],
            "programs_discovered": {},
            "instructions_discovered": {},
            "instructions_by_program": {},  # New: Track unique instructions per program
            "code_blocks_extracted": [],
            "errors": [],
        }
        
        self.message_count = 0
        self.messages = []  # List of LangChain message objects
        
    def extract_code_blocks(self, message_content: str) -> List[str]:
        """
        Extract TypeScript/JavaScript code blocks from the message content.
        Returns a list of code strings found in the message.
        """
        code_blocks = self.code_pattern.findall(message_content)
        return [block.strip() for block in code_blocks if block.strip()]
    
    def _log_formatted_response(self, content: str):
        """Log the response with highlighted TypeScript code blocks."""
        # ANSI color codes
        CYAN = '\033[96m'
        YELLOW = '\033[93m'
        GREEN = '\033[92m'
        RESET = '\033[0m'
        BOLD = '\033[1m'
        
        # Split content by code blocks
        parts = re.split(r'(```(?:typescript|ts|javascript|js).*?```)', content, flags=re.DOTALL)
        
        for part in parts:
            if part.startswith('```'):
                # This is a code block
                lines = part.split('\n')
                logging.info(f"{CYAN}{BOLD}╔══ TypeScript Code Block ══╗{RESET}")
                logging.info(f"{CYAN}║{RESET}")
                
                # Skip the opening ``` line and closing ``` line
                code_lines = lines[1:-1] if len(lines) > 2 else lines[1:]
                for line in code_lines:
                    logging.info(f"{CYAN}║{RESET} {YELLOW}{line}{RESET}")
                
                logging.info(f"{CYAN}║{RESET}")
                logging.info(f"{CYAN}{BOLD}╚═══════════════════════════╝{RESET}")
            else:
                # Regular text - log each line separately for better formatting
                for line in part.split('\n'):
                    if line.strip():
                        logging.info(line)
    
    def create_skill_code(self, code_blocks: List[str]) -> str:
        """
        Use the first code block that contains the executeSkill function.
        If none found, return the first code block as-is.
        """
        if not code_blocks:
            return ""
        
        # Look for a code block with the executeSkill function
        for block in code_blocks:
            if 'export async function executeSkill' in block:
                return block.strip()
        
        # If no executeSkill found, return the first block
        # This allows the error handling to provide feedback
        return code_blocks[0].strip()
    
    async def get_system_prompt(self, env: SurfpoolEnv) -> str:
        """Build the system prompt for the agent."""
        observation = await env._get_observation()
        obs_dict = observation[0][1] if observation else {}
        agent_pubkey = str(env.agent_keypair.pubkey())
        
        # Custom system prompt emphasizing TypeScript code blocks with correct function signature
        system_prompt = f"""You are an expert Solana blockchain developer. Your ONLY way to interact with the blockchain is by writing TypeScript code.

🚨 CRITICAL REQUIREMENTS 🚨
1. You MUST respond with TypeScript code in ```typescript blocks
2. The function signature MUST be: export async function executeSkill(blockhash: string): Promise<string>
3. You MUST return a base64 encoded serialized transaction
4. Each response SHOULD contain at least one ```typescript code block
5. If you don't include code, nothing will happen!

⏰ TIME LIMIT: You have ONLY {self.max_messages} messages total to maximize rewards!
BE EFFICIENT: Pack many instructions per transaction to get maximum rewards!
URGENCY: Every message counts - make each transaction count with as many instructions as you can!

=== CURRENT STATE ===
SOL Balance: {obs_dict.get('sol_balance', 0):.4f} SOL
Agent Pubkey: {agent_pubkey}
Block Height: {obs_dict.get('block_height', 0)}
Programs Discovered: {obs_dict.get('discovered_programs', 0)}
Total Reward: {env.total_reward}

=== CONNECTION INFO ===
You are connected to Solana mainnet through Surfpool - a safe sandbox proxy.
Surfpool allows you to interact with real mainnet data in a sandboxed environment.
RPC Endpoint: http://localhost:8899 or http://127.0.0.1:8899
⚠️ IMPORTANT: If you need to create a Connection object, ONLY use localhost:8899
Example: const connection = new Connection('http://localhost:8899');
✅ The environment is pre-configured - focus on building transactions!

=== AVAILABLE DEPENDENCIES ===
You can import from these packages:
- @solana/web3.js (v1.98.2) - Core Solana SDK
- @solana/spl-token (v0.4.13) - SPL Token operations
- @coral-xyz/anchor (v0.30.1) - Anchor framework
- @coral-xyz/borsh (v0.31.1) - Borsh serialization
- @solana/kit (v2.3.0) - Solana development kit
- @codama/nodes-from-anchor (v1.2.3) - Codama IDL support
- buffer - Node.js Buffer for binary data

=== EXACT CODE PATTERN (MUST FOLLOW) ===
```typescript
import {{ Transaction, SystemProgram, PublicKey }} from '@solana/web3.js';

export async function executeSkill(blockhash: string): Promise<string> {{
    const tx = new Transaction();
    const agentPubkey = new PublicKey('{agent_pubkey}');
    
    // Add your instructions here
    tx.add(
        SystemProgram.transfer({{
            fromPubkey: agentPubkey,
            toPubkey: new PublicKey("11111111111111111111111111111111"),
            lamports: 100000
        }})
    );
    
    // Set transaction properties
    tx.recentBlockhash = blockhash;
    tx.feePayer = agentPubkey;
    
    // Return base64 encoded transaction
    return tx.serialize({{
        requireAllSignatures: false,
        verifySignatures: false
    }}).toString('base64');
}}
```

=== 🎯 MAXIMIZE REWARDS: START SIMPLE, THEN SCALE UP! 🎯 ===
- You earn +1 reward for EACH unique (program_id, instruction_discriminator) pair

📈 WINNING STRATEGY:
1. START SIMPLE: Begin with 2-3 instructions you KNOW work (e.g., self-transfers, memos)
2. BUILD CONFIDENCE: Once those work, gradually add more instructions
3. SCALE UP: After success, pack 10-20+ instructions per transaction
4. MIX PROGRAMS: Combine System, Memo, Compute Budget, Token, Token-2022 programs
5. USE TOKEN-2022: Token-2022 (TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb) has many extensions!
   - Each extension instruction = unique reward!
   - Try: transfer fees, interest bearing, confidential transfers, metadata, etc.

Why this works:
- ✅ Early success builds momentum
- ✅ You learn what works in this environment
- ✅ Failed transactions = 0 rewards, so start safe!
- ✅ Once confident, go aggressive with 15+ instructions

TARGET PROGRESSION:
- Message 1-3: 2-5 safe instructions (test the waters)
- Message 4-10: 5-10 instructions (gaining confidence)  
- Message 11+: 10-20+ instructions (maximize rewards!)

Remember: 1 transaction with 20 instructions > 20 transactions with 1 instruction!

=== MULTI-INSTRUCTION EXAMPLE (MORE REWARDS!) ===
```typescript
import {{ Transaction, SystemProgram, PublicKey, Keypair }} from '@solana/web3.js';

export async function executeSkill(blockhash: string): Promise<string> {{
    const tx = new Transaction();
    const agentPubkey = new PublicKey('{agent_pubkey}');
    const newAccount = Keypair.generate();
    
    // Add multiple instructions for more rewards!
    tx.add(
        SystemProgram.createAccount({{
            fromPubkey: agentPubkey,
            newAccountPubkey: newAccount.publicKey,
            lamports: 1000000,
            space: 0,
            programId: SystemProgram.programId
        }}),
        SystemProgram.transfer({{
            fromPubkey: agentPubkey,
            toPubkey: newAccount.publicKey,
            lamports: 50000
        }}),
        SystemProgram.assign({{
            accountPubkey: newAccount.publicKey,
            programId: SystemProgram.programId
        }})
    );
    
    tx.recentBlockhash = blockhash;
    tx.feePayer = agentPubkey;
    tx.partialSign(newAccount);
    
    return tx.serialize({{
        requireAllSignatures: false,
        verifySignatures: false
    }}).toString('base64');
}}
```

=== IMPORTANT RULES & COMMON PITFALLS ===
1. Function MUST be: export async function executeSkill(blockhash: string): Promise<string>
2. Import ALL dependencies at the top
3. Return base64 encoded serialized transaction
4. Use the provided blockhash parameter
5. Set tx.feePayer = agentPubkey
6. For new accounts, use partialSign(newAccount)

❌ AVOID THESE COMMON ERRORS:
- DON'T add duplicate ComputeBudgetProgram instructions (only ONE setComputeUnitLimit and ONE setComputeUnitPrice per tx)
- DON'T transfer to program IDs - only transfer to regular accounts
- DON'T use undefined variables - declare ALL variables before use
- DON'T create accounts without signing with them (use partialSign)

✅ WHAT WORKS RELIABLY:
- SystemProgram.transfer to your own address (self-transfer)
- ONE ComputeBudgetProgram.setComputeUnitLimit per transaction
- ONE ComputeBudgetProgram.setComputeUnitPrice per transaction
- Creating new Keypairs and accounts (but remember to partialSign)
- Token-2022 instructions (huge potential for unique rewards!):
  * InitializeMint2 with extensions
  * InitializeAccount3 
  * Transfer with fee
  * Metadata instructions
  * Each extension type = new unique instructions!

=== COMMON PROGRAM IDS ===
- System Program: 11111111111111111111111111111111
- Token Program: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA
- Token-2022 Program: TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb (MORE REWARDS!)
- Associated Token Program: ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL
- Memo Program: MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr
- Compute Budget: ComputeBudget111111111111111111111111111111

REMEMBER: No ```typescript blocks = No blockchain interaction = No rewards!
ALWAYS use: export async function executeSkill(blockhash: string): Promise<string>"""
        
        return system_prompt
    
    async def run_exploration_loop(self, env: SurfpoolEnv):
        """Main exploration loop that extracts and executes code from agent responses."""
        
        # Initialize conversation with LangChain messages
        system_prompt = await self.get_system_prompt(env)
        self.messages = [
            SystemMessage(content=system_prompt)
        ]
        
        # Add initial user prompt
        initial_prompt = """
Begin exploring the Solana blockchain. Try to discover new programs and instructions.
Write TypeScript code to create and execute transactions that will earn rewards.
Remember to use ```typescript code blocks for your transaction code.
"""
        self.messages.append(HumanMessage(content=initial_prompt))
        
        while self.message_count < self.max_messages:
            self.message_count += 1
            message_start_time = datetime.now()
            
            try:
                # Get agent response using LangChain
                response = await self.llm.ainvoke(self.messages)
                # pdb.set_trace()
                
                # Add AI message to conversation
                self.messages.append(response)
                
                if self.verbose:
                    logging.info(f"\n{'='*80}")
                    logging.info(f"📤 MESSAGE {self.message_count}/{self.max_messages}")
                    logging.info(f"{'='*80}")
                    
                    # Log the full response with TypeScript blocks highlighted
                    self._log_formatted_response(response.content)
                    logging.info(f"{'='*80}\n")
                
                # Extract code blocks
                code_blocks = self.extract_code_blocks(response.content)
                
                if code_blocks:
                    logging.info(f"\n🔍 Found {len(code_blocks)} TypeScript code block(s)")
                    for i, block in enumerate(code_blocks, 1):
                        lines = block.split('\n')
                        logging.info(f"   Block {i}: {len(lines)} lines, {len(block)} characters")
                    
                    # Create skill code
                    skill_code = self.create_skill_code(code_blocks)
                    logging.info(f"📝 Skill code extracted, length: {len(skill_code)} chars")
                    
                    # Get the latest blockhash
                    blockhash_response = await env.client.get_latest_blockhash()
                    blockhash = str(blockhash_response.value.blockhash)
                    logging.info(f"🔑 Blockhash: {blockhash[:8]}...")
                    
                    # Execute the code
                    logging.info(f"🚀 Executing TypeScript code...")
                    result = self.skill_manager.run_code_loop_code(
                        skill_code,
                        str(env.agent_keypair.pubkey()),
                        blockhash,
                        self.code_file
                    )
                    logging.info(f"📦 Execution result: success={result.get('success', False)}, has_tx={bool(result.get('serialized_tx'))}")

                    execution_feedback = ""
                    reward = 0

                    tx_data = result.get("serialized_tx")
                    # pdb.set_trace()
                    if not tx_data:
                        execution_feedback = json.dumps({
                            "error": "Skill execution failed",
                            "details": result,
                            "suggestion": "Check for syntax errors, missing imports, or typos in the skill code"
                        })
                        logging.info(f"❌ Transaction creation failed. Info: {result}")
                        self.metrics['errors'].append({
                            'message_index': self.message_count,
                            'error': execution_feedback
                        })
                    else:
                        try:
                            # Decode and sign the transaction
                            tx_bytes = base64.b64decode(tx_data)
                            tx = Transaction.from_bytes(tx_bytes)
                            signed_tx = env._partial_sign_transaction(bytes(tx), [env.agent_keypair])
                            
                            # Execute the transaction
                            obs, step_reward, _, _, info = await env.step(signed_tx)
                            
                            # Log success
                            if step_reward > 0:
                                logging.info(f"✅ Transaction successful! Reward: {step_reward} | Total: {env.total_reward}")
                                logging.info(f"✅ Obs: {obs}\n\nInfo: {info}")
                                execution_feedback = f"✅ Transaction executed successfully! Earned {step_reward} reward points.\nTotal rewards: {env.total_reward}\n[Message {self.message_count}/{self.max_messages}] - {self.max_messages - self.message_count} messages remaining\nInfo: {info}\n\nObs: {obs}"
                            else:
                                logging.info(f"❌ Transaction failed. Info: {info}")
                                execution_feedback = f"❌ Transaction failed: {info}\n[Message {self.message_count}/{self.max_messages}] - {self.max_messages - self.message_count} messages remaining"
                            
                            reward = step_reward
                            
                            # Track new discoveries if reward > 0
                            if reward > 0:
                                # Track programs discovered
                                if 'programs_interacted' in info:
                                    for prog in info['programs_interacted']:
                                        if prog not in self.metrics['programs_discovered']:
                                            self.metrics['programs_discovered'][prog] = self.message_count
                                
                                # Track unique instructions per program
                                if 'unique_instructions' in info:
                                    # info['unique_instructions'] should be a dict of program_id -> set of instruction discriminators
                                    for prog_id, instructions in info['unique_instructions'].items():
                                        if prog_id not in self.metrics['instructions_by_program']:
                                            self.metrics['instructions_by_program'][prog_id] = set()
                                        # Add new instructions to the set
                                        if isinstance(instructions, (list, set)):
                                            self.metrics['instructions_by_program'][prog_id].update(instructions)
                                        else:
                                            self.metrics['instructions_by_program'][prog_id].add(instructions)
                                        
                        except Exception as tx_error:
                            logging.error(f"Transaction execution error: {tx_error}")
                            execution_feedback = f"❌ Transaction execution failed: {str(tx_error)}"
                            reward = 0
                    
                    # Add execution feedback to conversation
                    self.messages.append(HumanMessage(content=execution_feedback))
                    
                    # Record metrics
                    self.metrics['code_blocks_extracted'].append({
                        'message_index': self.message_count,
                        'num_blocks': len(code_blocks),
                        'success': reward > 0,
                        'reward': reward
                    })
                else:
                    # No code blocks found
                    # pdb.set_trace()
                    logging.info("No code blocks found in response")
                    self.messages.append(
                        HumanMessage(content="Please provide TypeScript code in ```typescript blocks to create Solana transactions. We could not find any code blocks in your response.")
                    )
                
                # Update cumulative metrics
                self.metrics['cumulative_rewards'].append(env.total_reward)
                self.metrics['messages'].append({
                    'index': self.message_count,
                    'timestamp': message_start_time.isoformat(),
                    'duration': (datetime.now() - message_start_time).total_seconds(),
                    'reward': reward if 'reward' in locals() else 0,
                    'total_reward': env.total_reward
                })
                
                # Save checkpoint periodically
                if self.message_count % 10 == 0:
                    self.save_checkpoint()
                    
            except Exception as e:
                logging.error(f"Error in message {self.message_count}: {e}")
                self.metrics['errors'].append({
                    'message_index': self.message_count,
                    'error': str(e)
                })
                
                # Add error feedback
                self.messages.append(
                    HumanMessage(content=f"An error occurred: {str(e)}. Please try a different approach.")
                )
    
    def save_checkpoint(self):
        """Save current metrics and conversation history."""
        os.makedirs(f"metrics", exist_ok=True)
        
        # Convert sets to lists for JSON serialization
        metrics_copy = self.metrics.copy()
        if 'instructions_by_program' in metrics_copy:
            metrics_copy['instructions_by_program'] = {
                prog: list(instructions) if isinstance(instructions, set) else instructions
                for prog, instructions in metrics_copy['instructions_by_program'].items()
            }
        
        # Save metrics
        metrics_path = f"metrics/{self.run_id}_metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics_copy, f, indent=2)
        
        # Convert LangChain messages to dict format for saving
        conversation_dict = []
        for msg in self.messages:
            if isinstance(msg, SystemMessage):
                conversation_dict.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                conversation_dict.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                conversation_dict.append({"role": "assistant", "content": msg.content})
        
        # Save conversation history
        conv_path = f"metrics/{self.run_id}_conversation.json"
        with open(conv_path, 'w') as f:
            json.dump(conversation_dict, f, indent=2)
        
        logging.info(f"Checkpoint saved: {metrics_path}")

async def main():
    """Run the code loop explorer."""
    # Force logging configuration
    import sys
    logging.basicConfig(
        level=logging.INFO,  # Temporarily set to DEBUG to see surfpool output
        format='%(asctime)s - %(levelname)s - %(message)s',
        force=True,  # Force reconfiguration
        handlers=[logging.StreamHandler(sys.stdout)]  # Ensure output to stdout
    )
    
    # Configuration
    model_name = os.getenv("MODEL_NAME", "openrouter/horizon-beta")
    max_messages = int(os.getenv("MAX_MESSAGES", "50"))
    run_index = int(os.getenv("RUN_INDEX", "0"))  # Get run index from environment
    code_file = os.getenv("CODE_FILE", None)  # Get code file from environment
    use_external_surfpool = os.getenv("USE_EXTERNAL_SURFPOOL", "false").lower() == "true"
    
    logging.info(f"Starting Code Loop Explorer with model: {model_name}")
    logging.info(f"Max messages: {max_messages}")
    logging.info(f"Run index: {run_index}")
    logging.info(f"Code file: {code_file or 'voyager/skill_runner/code_loop_code.ts (default)'}")
    logging.info(f"Use external surfpool: {use_external_surfpool}")
    
    # Initialize explorer
    logging.info("Initializing explorer...")
    explorer = CodeLoopExplorer(
        model_name=model_name,
        run_index=run_index,
        max_messages=max_messages,
        verbose=True,
        code_file=code_file
    )
    
    # Choose whether to start surfpool or connect to existing instance
    if use_external_surfpool:
        logging.info("Connecting to existing surfpool on localhost:8899...")
        
        env = SurfpoolEnv()
        logging.info("Resetting environment...")
        
        await env.reset()
        logging.info("Environment ready!")

        try:
            await explorer.run_exploration_loop(env)

            # Save final checkpoint
            explorer.save_checkpoint()
            
            # Log summary
            logging.info("\n=== Exploration Summary ===")
            logging.info(f"Total messages: {explorer.message_count}")
            logging.info(f"Total reward: {env.total_reward}")
            logging.info(f"Programs discovered: {len(explorer.metrics['programs_discovered'])}")
            logging.info(f"Total errors: {len(explorer.metrics['errors'])}")
        finally:
            await env.close()
    else:
        # Original behavior - start surfpool
        logging.info("Starting surfpool validator...")
        
        async with _surfpool_validator("https://api.mainnet-beta.solana.com") as proc:
            logging.info("Surfpool validator started, initializing environment...")
            
            env = SurfpoolEnv()
            logging.info("Resetting environment...")
            
            await env.reset()
            logging.info("Environment ready!")

            try:
                await explorer.run_exploration_loop(env)

                # Save final checkpoint
                explorer.save_checkpoint()
                
                # Log summary
                logging.info("\n=== Exploration Summary ===")
                logging.info(f"Total messages: {explorer.message_count}")
                logging.info(f"Total reward: {env.total_reward}")
                logging.info(f"Programs discovered: {len(explorer.metrics['programs_discovered'])}")
                logging.info(f"Total errors: {len(explorer.metrics['errors'])}")
            finally:
                await env.close()

if __name__ == "__main__":
    asyncio.run(main())