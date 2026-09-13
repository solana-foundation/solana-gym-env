import asyncio
import base64
import logging
import os
import re
import json
import uuid
from datetime import datetime
from typing import List

from langchain.schema import SystemMessage, HumanMessage, AIMessage
from solders.transaction import Transaction
from dotenv import load_dotenv

from voyager.code_extract import (
    create_skill_code,
    extract_code_blocks,
    load_system_prompt_template,
    render_system_prompt,
)
from voyager.llm_providers import FIXTURE_PROVIDERS, create_llm, resolve_provider_name
from voyager.skill_manager.ts_skill_manager import TypeScriptSkillManager
from voyager.surfpool_env import SurfpoolEnv, _surfpool_validator

load_dotenv()

DEFAULT_ENVIRONMENT_CONFIG = "voyager/environments/basic_env.json"

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
        code_file: str = None,
        environment_config: str = None,
        llm=None,
        llm_provider: str = None,
        metrics_dir: str = None,
    ):
        self.model_name = model_name
        self.run_index = run_index
        self.max_messages = max_messages
        self.checkpoint_dir = checkpoint_dir
        self.resume = resume
        self.verbose = verbose
        self.code_file = code_file or "voyager/skill_runner/code_loop_code.ts"
        self.environment_config_path = environment_config
        self.llm_provider = resolve_provider_name(model_name, llm_provider)
        self.metrics_dir = metrics_dir or os.getenv("METRICS_DIR", "metrics")
        
        # Load environment configuration if provided
        self.env_config = None
        if environment_config:
            self.load_environment_config(environment_config)
        
        # Generate unique run ID
        self.run_id = f"code_loop_{datetime.now().strftime('%y-%m-%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        self.llm = llm if llm is not None else create_llm(model_name, self.llm_provider)
        
        # Initialize skill manager (execution only; LLM is unused for code-loop)
        self.skill_manager = TypeScriptSkillManager(
            model_name=model_name,
            temperature=0.0,
            retrieval_top_k=5,
            request_timeout=120,
            ckpt_dir=checkpoint_dir,
            resume=resume,
            skip_llm=True,
        )
        
        # Metrics tracking
        self.metrics = {
            "model": model_name,
            "llm_provider": self.llm_provider,
            "run_index": run_index,
            "run_id": self.run_id,
            "start_time": datetime.now().isoformat(),
            "environment_config": environment_config,
            "messages": [],
            "cumulative_rewards": [],
            "raw_unfiltered_rewards": [],
            "programs_discovered": {},
            "instructions_by_program": {},  # Track unique instructions per program
            "code_blocks_extracted": [],
            "errors": [],
        }
        
        self.message_count = 0
        self.messages = []  # List of LangChain message objects
        
    def load_environment_config(self, config_path: str):
        """Load environment configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                self.env_config = json.load(f)
                logging.info(f"Loaded environment config: {self.env_config['name']}")
        except Exception as e:
            logging.error(f"Failed to load environment config: {e}")
            self.env_config = None
        
    def extract_code_blocks(self, message_content: str) -> List[str]:
        """
        Extract TypeScript/JavaScript code blocks from the message content.
        Returns a list of code strings found in the message.
        """
        return extract_code_blocks(message_content)
    
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
        return create_skill_code(code_blocks)
    
    async def get_system_prompt(self, env: SurfpoolEnv) -> str:
        """Build the system prompt for the agent."""
        observation = await env._get_observation()
        obs_dict = observation[0][1] if observation else {}
        agent_pubkey = str(env.agent_keypair.pubkey())
        template = load_system_prompt_template(self.env_config)
        return render_system_prompt(
            template,
            agent_pubkey=agent_pubkey,
            sol_balance=obs_dict.get('sol_balance', 0),
            block_height=obs_dict.get('block_height', 0),
            total_reward=getattr(env, 'total_reward', 0),
            max_messages=self.max_messages,
        )

    def _skill_timeout_ms(self) -> int:
        return int((self.env_config or {}).get("timeout", 30000))

    def _partial_sign_skill_tx(self, env: SurfpoolEnv, tx_bytes: bytes):
        """Sign skill bytes with the sandbox agent key. Prefer versioned txs."""
        try:
            return env._partial_sign_transaction(tx_bytes, [env.agent_keypair])
        except Exception:
            legacy = Transaction.from_bytes(tx_bytes)
            return env._partial_sign_transaction(bytes(legacy), [env.agent_keypair])
    
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
                reward = 0
                instructions_discovered = {}
                
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
                        self.code_file,
                        self._skill_timeout_ms(),
                    )
                    logging.info(f"📦 Execution result: success={result.get('success', False)}, has_tx={bool(result.get('serialized_tx'))}")

                    execution_feedback = ""
                    reward = 0
                    instructions_discovered = {}

                    tx_data = result.get("serialized_tx")
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
                            signed_tx = self._partial_sign_skill_tx(env, tx_bytes)
                            
                            # Execute the transaction
                            obs, step_reward, _, _, info = await env.step(signed_tx)
                            
                            # Log success
                            if step_reward > 0:
                                logging.info(f"✅ Transaction successful! Reward: {step_reward} | Total: {env.total_reward}")
                                
                                # Log instructions discovered this step
                                if 'unique_instructions' in info:
                                    instructions_this_step = {}
                                    for program_id, discriminators in info['unique_instructions'].items():
                                        instructions_this_step[program_id] = list(set(discriminators))
                                    
                                    if instructions_this_step:
                                        logging.info(f"📊 Instructions in this transaction:")
                                        for prog, count in instructions_this_step.items():
                                            logging.info(f"   • {prog}: {count} instructions")
                                    instructions_discovered = instructions_this_step
                                
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
                self.metrics['raw_unfiltered_rewards'] = self.metrics.get(
                    'raw_unfiltered_rewards', []
                )
                self.metrics['raw_unfiltered_rewards'].append(
                    getattr(env, 'raw_unfiltered_reward', env.total_reward)
                )
                
                # Build message metrics
                message_metrics = {
                    'index': self.message_count,
                    'timestamp': message_start_time.isoformat(),
                    'duration': (datetime.now() - message_start_time).total_seconds(),
                    'reward': reward,
                    'total_reward': env.total_reward,
                    'raw_unfiltered_reward': getattr(
                        env, 'raw_unfiltered_reward', env.total_reward
                    ),
                    'instructions_discovered': instructions_discovered,
                    'code_extracted': bool(code_blocks),
                }
                
                self.metrics['messages'].append(message_metrics)
                
                # Save checkpoint after every message (force metrics flush)
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
                
                # Save checkpoint after error as well (force metrics flush)
                self.save_checkpoint()
    
    def save_checkpoint(self):
        """Save current metrics and conversation history."""
        os.makedirs(self.metrics_dir, exist_ok=True)
        
        # Convert sets to lists for JSON serialization
        metrics_copy = self.metrics.copy()
        if 'instructions_by_program' in metrics_copy:
            metrics_copy['instructions_by_program'] = {
                prog: list(instructions) if isinstance(instructions, set) else instructions
                for prog, instructions in metrics_copy['instructions_by_program'].items()
            }
        
        # Save metrics
        metrics_path = os.path.join(self.metrics_dir, f"{self.run_id}_metrics.json")
        with open(metrics_path, 'w') as f:
            json.dump(metrics_copy, f, indent=2)
            f.flush()  # Force flush to disk
            os.fsync(f.fileno())  # Ensure it's written to disk
        
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
        conv_path = os.path.join(self.metrics_dir, f"{self.run_id}_conversation.json")
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
    model_name = os.getenv("MODEL_NAME", "google/gemini-2.5-flash")
    llm_provider = os.getenv("LLM_PROVIDER")
    resolved_provider = resolve_provider_name(model_name, llm_provider)
    if resolved_provider in FIXTURE_PROVIDERS:
        model_name = os.getenv("MODEL_NAME", "fixture")
    max_messages = int(os.getenv("MAX_MESSAGES", "50"))
    run_index = int(os.getenv("RUN_INDEX", "0"))  # Get run index from environment
    code_file = os.getenv("CODE_FILE", None)  # Get code file from environment
    environment_config = os.getenv("ENVIRONMENT_CONFIG") or DEFAULT_ENVIRONMENT_CONFIG
    use_external_surfpool = os.getenv("USE_EXTERNAL_SURFPOOL", "false").lower() == "true"
    
    logging.info(f"Starting Code Loop Explorer with model: {model_name}")
    logging.info(f"LLM provider: {resolved_provider}")
    logging.info(f"Max messages: {max_messages}")
    logging.info(f"Run index: {run_index}")
    logging.info(f"Code file: {code_file or 'voyager/skill_runner/code_loop_code.ts (default)'}")
    logging.info(f"Environment config: {environment_config}")
    logging.info(f"Use external surfpool: {use_external_surfpool}")
    if resolved_provider not in FIXTURE_PROVIDERS:
        logging.info("Paid API providers are opt-in. Offline tests should use LLM_PROVIDER=fixture.")
    
    # Initialize explorer
    logging.info("Initializing explorer...")
    explorer = CodeLoopExplorer(
        model_name=model_name,
        run_index=run_index,
        max_messages=max_messages,
        verbose=True,
        code_file=code_file,
        environment_config=environment_config,
        llm_provider=resolved_provider,
    )
    
    # Get allowed programs from environment config if available
    allowed_programs = []
    if explorer.env_config and 'reward_config' in explorer.env_config:
        allowed_programs = explorer.env_config['reward_config'].get('allowed_programs', [])
    
    # Choose whether to start surfpool or connect to existing instance
    if use_external_surfpool:
        logging.info("Connecting to existing surfpool on localhost:8899...")
        if allowed_programs:
            logging.info(f"Program filter enabled: {len(allowed_programs)} programs allowed")
        
        env = SurfpoolEnv(allowed_programs=allowed_programs, use_external_surfpool=True)
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
            if allowed_programs:
                logging.info(f"Program filter enabled: {len(allowed_programs)} programs allowed")
            
            env = SurfpoolEnv(allowed_programs=allowed_programs, use_external_surfpool=True)
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