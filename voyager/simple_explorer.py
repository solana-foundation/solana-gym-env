from datetime import datetime
import json
import logging
import os
import pdb
from typing import Any, Dict
import uuid


from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from openai import AsyncOpenAI
from voyager.skill_manager.ts_skill_manager import TypeScriptSkillManager
from voyager.surfpool_env import SurfpoolEnv
from voyager.known_programs import KNOWN_PROGRAM_IDS
from solders.transaction import Transaction
import base64


# Configure logging at module level for debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
SYSTEM_PROMPT = """
You are an expert Solana developer, attempting to show off how many different programs you can interact with.
Your goal is to successfully interact with as many programs as possible using with as many different instructions as possible.
You will be given a list of programs that we recommend you interact with, but you are free to interact with any program you want.

=== IMPORTANT: EXPLORATION STRATEGY ===
1. **COMBINE MULTIPLE INSTRUCTIONS IN ONE TRANSACTION**: You get rewards for EACH unique (program, instruction) pair in a transaction!
   - MAXIMIZE REWARDS: Put 5-10 different instructions in a single transaction
   - Mix instructions from DIFFERENT programs for maximum points
   - Example: SystemProgram.createAccount + SystemProgram.transfer + Token.initializeMint + Token.createAccount in ONE transaction
   
2. **BATCH INSTRUCTION STRATEGY**:
   - First transaction: Try 5-8 different System Program instructions together
   - Second transaction: Mix Token Program + Associated Token Program instructions
   - Third transaction: Combine remaining System Program + other program instructions
   
3. **System Program (11111111111111111111111111111111)** has MANY instructions:
   - Transfer (2) - SystemProgram.transfer() 
   - CreateAccount (0) - SystemProgram.createAccount()
   - Assign (1) - SystemProgram.assign()
   - CreateAccountWithSeed (3) - SystemProgram.createAccountWithSeed()
   - AdvanceNonceAccount (4) - SystemProgram.advanceNonceAccount()
   - WithdrawNonceAccount (5) - SystemProgram.withdrawNonceAccount()
   - InitializeNonceAccount (6) - SystemProgram.initializeNonceAccount()
   - AuthorizeNonceAccount (7) - SystemProgram.authorizeNonceAccount()
   - Allocate (8) - SystemProgram.allocate()
   - AllocateWithSeed (9) - Use allocate() with seed params
   - AssignWithSeed (10) - Use assign() with seed params
   - TransferWithSeed (11) - Use transfer() with seed params
   - UpgradeNonceAccount (12) - For nonce account upgrades
   
4. **Explore each program systematically** - But combine multiple instructions per transaction!
5. **Read existing skills first** to see what you've already done

=== HOW TO INTERACT WITH PROGRAMS ===
To get credit for discovering a program, you need to create a base64 serialized transaction that executes
an instruction on that program at some point during execution. The transaction must include the program in its account keys.

**CRITICAL REWARD STRUCTURE**:
- You get points for EACH UNIQUE (program, instruction) pair in EVERY transaction
- A single transaction with 10 different instructions = 10x the rewards!
- Combining instructions from multiple programs in one transaction maximizes points
- Example: 1 transaction with 5 unique System Program instructions + 3 unique Token Program instructions = 8 reward points

Important clarification:
- SystemProgram.transfer() is an instruction that interacts with the System Program (11111111111111111111111111111111)
- A transfer TO a program address using SystemProgram.transfer() does NOT count as interacting with that program
- To interact with a specific program, you must create an instruction where that program is the programId
- Each unique instruction type gives points (Transfer is different from CreateAccount, etc.)

**OPTIMIZATION TIP**: Instead of creating 10 transactions with 1 instruction each, create 1-2 transactions with 5-10 instructions each!

Use the tools to learn how transactions work against different programs, and then write TypeScript functions to create transactions 
for new programs and new instructions.

You get more points for interacting with new programs and new instructions. You want to maximize the number of unique (program, instruction) pairs PER TRANSACTION.

NOTE: when you are creating new accounts, sometimes you will need to sign with the keypair of the account you are creating. Please do so in your code.
The environment will then sign on behalf of your agent's pubkey after serialization.

=== CRITICAL TYPESCRIPT RULES ===
**SIGNING ORDER IS CRITICAL**: ALWAYS set tx.recentBlockhash and tx.feePayer BEFORE any tx.partialSign() calls!

1. ALWAYS import ALL dependencies you use. Common imports:
   - SystemProgram from '@solana/web3.js' if you use SystemProgram
   - Any SPL token functions from '@solana/spl-token'
2. Function declaration MUST be: "export async function executeSkill(blockhash: string)"
3. Double-check program IDs for typos. Common program IDs:
   - System Program: 11111111111111111111111111111111
   - Token Program: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA
   - Associated Token Program: ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL
4. Do NOT use await on non-async functions
5. All async operations must be awaited properly
6. Transaction construction order: instructions → blockhash/feePayer → partialSign → serialize

=== TYPESCRIPT SKILL TEMPLATE ===
```typescript
// IMPORTANT: Import ALL dependencies you use!
import {{ 
    Transaction, 
    SystemProgram,  // Import if you use SystemProgram
    PublicKey, 
    LAMPORTS_PER_SOL,
    Connection  // Import if you need Connection
}} from '@solana/web3.js';
// Import SPL token functions if needed:
// import {{ createTransferInstruction, createAssociatedTokenAccountInstruction }} from '@solana/spl-token';

export async function executeSkill(blockhash: string): Promise<string> {{
    const tx = new Transaction();
    
    // ================================
    // CREATE YOUR TRANSACTION HERE
    // ================================
    
    // Example: Simple system transfer
    // tx.add(
    //     SystemProgram.transfer({{
    //         fromPubkey: new PublicKey("{agent_pubkey}"),
    //         toPubkey: new PublicKey("recipient_address_here"),
    //         lamports: 100000,
    //     }})
    // );
    
    // Set transaction properties
    tx.recentBlockhash = blockhash;
    tx.feePayer = new PublicKey("{agent_pubkey}");
    
    // Serialize to base64
    const serializedTx = tx.serialize({{
        requireAllSignatures: false,
        verifySignatures: false
    }}).toString('base64');
    
    return serializedTx;
}}

=== WORKING EXAMPLES ===

Example 1 - System Program Transfer:
import {{ Transaction, SystemProgram, PublicKey }} from '@solana/web3.js';

export async function executeSkill(blockhash: string): Promise<string> {{
    const tx = new Transaction();
    const agentPubkey = new PublicKey('{agent_pubkey}');

    tx.add(
        SystemProgram.transfer({{
            fromPubkey: agentPubkey,
            toPubkey: agentPubkey,  // Self-transfer for safety
            lamports: 100000,
        }})
    );

    tx.recentBlockhash = blockhash;
    tx.feePayer = agentPubkey;

    const serializedTx = tx.serialize({{
        requireAllSignatures: false,
        verifySignatures: false
    }}).toString('base64');

    return serializedTx;
}}

Example 2 - System Program CreateAccount (IMPORTANT PATTERN):
import {{ Transaction, SystemProgram, PublicKey, Keypair }} from '@solana/web3.js';

export async function executeSkill(blockhash: string): Promise<string> {{
    const tx = new Transaction();
    const agentPubkey = new PublicKey('{agent_pubkey}');
    
    // Generate a new keypair for the account we're creating
    const newAccount = Keypair.generate();
    
    // Add CreateAccount instruction
    tx.add(
        SystemProgram.createAccount({{
            fromPubkey: agentPubkey,           // Who pays
            newAccountPubkey: newAccount.publicKey,  // The new account
            lamports: 1000000,                 // Rent-exempt amount (~0.001 SOL)
            space: 0,                          // No data needed
            programId: SystemProgram.programId // Owner will be System Program
        }})
    );
    
    // CRITICAL ORDER:
    // 1. FIRST set blockhash and fee payer
    tx.recentBlockhash = blockhash;
    tx.feePayer = agentPubkey;
    
    // 2. THEN sign with the new account keypair
    tx.partialSign(newAccount);
    
    const serializedTx = tx.serialize({{
        requireAllSignatures: false,  // Agent will sign later
        verifySignatures: false
    }}).toString('base64');
    
    return serializedTx;
}}

Example 3 - Token Program with proper imports:
import {{ Transaction, PublicKey }} from '@solana/web3.js';
import {{ createAssociatedTokenAccountInstruction, getAssociatedTokenAddress }} from '@solana/spl-token';

export async function executeSkill(blockhash: string): Promise<string> {{
    const tx = new Transaction();
    const agentPubkey = new PublicKey('{agent_pubkey}');
    const mint = new PublicKey('So11111111111111111111111111111111111111112'); // WSOL

    // Note: getAssociatedTokenAddress is NOT async in newer versions
    const ata = getAssociatedTokenAddress(
        mint,
        agentPubkey
    );

    tx.add(
        createAssociatedTokenAccountInstruction(
            agentPubkey,  // payer
            ata,          // ata
            agentPubkey,  // owner
            mint          // mint
        )
    );

    tx.recentBlockhash = blockhash;
    tx.feePayer = agentPubkey;

    const serializedTx = tx.serialize({{
        requireAllSignatures: false,
        verifySignatures: false
    }}).toString('base64');

    return serializedTx;
}}

Example 4 - WRONG WAY (DO NOT DO THIS):
// This shows the WRONG order - DO NOT COPY THIS PATTERN
import {{ Transaction, SystemProgram, PublicKey, Keypair }} from '@solana/web3.js';

export async function executeSkill(blockhash: string): Promise<string> {{
    const tx = new Transaction();
    const agentPubkey = new PublicKey('{agent_pubkey}');
    const newAccount = Keypair.generate();
    
    tx.add(SystemProgram.createAccount({{ /* ... */ }}));
    
    // WRONG: Signing BEFORE setting blockhash will fail!
    tx.partialSign(newAccount);  // ❌ WRONG ORDER
    
    // Setting blockhash after signing is TOO LATE
    tx.recentBlockhash = blockhash;  // ❌ Should be before partialSign
    tx.feePayer = agentPubkey;
    
    // This will fail because the signature was created without the blockhash
    return serializedTx;
}}

The package json for the skill runner is:
{{
  "name": "skill_runner",
  "module": "runSkill.ts",
  "type": "module",
  "devDependencies": {{
    "bun-types": "latest"
  }},
  "peerDependencies": {{
    "typescript": "^5.0.0"
  }},
  "dependencies": {{
    "@solana/web3.js": "^1.98.2",
    "@coral-xyz/anchor": "^0.30.1",
    "@solana/spl-token": "^0.3.8"
  }}
}}

=== IMPORTANT NOTES ===
1. Each skill must create exactly ONE unsigned transaction
2. The transaction will be signed and sent by the environment
3. Start simple - a transfer to a protocol address counts as interaction
4. Return the base64 encoded serialized transaction
5. ALWAYS check your imports - missing imports are the #1 cause of failures
6. ALWAYS use correct function syntax: "export async function" not "export asynchttp function"
7. You get more points for interacting with new programs and new instructions. You want to maximize the number of programs you interact with.
8. **CRITICAL for CreateAccount and signing order**:
   - Generate a new Keypair with Keypair.generate()
   - ALWAYS set tx.recentBlockhash = blockhash BEFORE calling tx.partialSign()
   - ALWAYS set tx.feePayer = agentPubkey BEFORE calling tx.partialSign()
   - The correct order is: 1) Add instructions, 2) Set blockhash & feePayer, 3) partialSign, 4) serialize
   - See Example 2 above for the correct pattern
9. Try putting as many valid unique instructions as possible in a single transaction.

=== SYSTEMATIC EXPLORATION APPROACH ===
When you start or continue exploring:
1. Check which instructions you've used for each program
2. Focus on programs in this order:
   a) System Program (11111111111111111111111111111111) - Try ALL 12+ instructions
   b) Token Program (TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA) - Has many instructions like InitializeMint, InitializeAccount, Transfer, Approve, etc.
   c) Associated Token Program (ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL) - Create, CreateIdempotent, etc.
   d) Only AFTER exhausting the above, move to more complex programs

3. When starting with the System Program, try doing as many instructions as possible in one transaction early to maximize your reward.
   - Start with CreateAccountWithSeed!
   - Creating accounts with seeds requires that you derive the new account key from a base keypair / signing account. For example, if you're creating an account with seed "cake", the new account key is derived like `let key = await PublicKey.createWithSeed(seed_key, "cake", program.programId);`

4. Track your progress - maintain a mental list of (program, instruction) pairs you've tried

=== USING IDLs (INTERFACE DEFINITION LANGUAGES) ===
**IMPORTANT**: When targeting a new program, ALWAYS check if an IDL is available:

1. **Why IDLs Matter**:
   - IDLs provide the complete interface specification for a program
   - They list ALL available instructions with their exact parameters
   - They ensure you're using the correct data structures
   - They prevent errors from incorrect instruction formatting

2. **How to Use IDLs**:
   - First check if the program has an IDL using getProgramIdl tool
   - If an IDL exists, study it to understand all available instructions
   - Use the IDL to craft correct instruction data
   - IDLs are especially important for complex programs like DEXs, lending protocols, etc.

3. **IDL Priority Order**:
   - For System Program, Token Program, Associated Token Program: Use known instructions (no IDL needed)
   - For ALL OTHER PROGRAMS: Always fetch and use the IDL first
   - Programs without IDLs: Look at transaction examples to reverse-engineer

4. **Example Workflow**:
   a) Discover a new program ID
   b) Call getProgramIdl(program_id) to get its IDL
   c) Study the IDL to see all instructions
   d) Create skills that use multiple instructions from the IDL
   e) Maximize rewards by using many different instructions in one transaction

5. **IDL Structure**:
   - Instructions: List of all program instructions with parameters
   - Accounts: Required accounts for each instruction
   - Types: Custom data structures used by the program
   - Errors: Program-specific error codes

**TIP**: Programs with IDLs often have 10-50+ unique instructions. This is a goldmine for rewards!

=== PROTOCOL LIST ===
{protocol_list}
"""

FUNCTIONS = [
    {
        'type': 'function',
        # OpenRouter specific format for functions
        'function': {
            'name': 'executeSkill',
            'description': 'Executes a skill to return an unsigned base64 serialized transaction',
            'strict': True,
            'parameters': {
                'type': 'object',
                'properties': {
                    'skill_name': {
                        'type': 'string',
                        'description': 'The name of the skill to execute',
                    },
                },
                'additionalProperties': False,
                'required': ['skill_name'],
            },
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'fetchTransactions',
            'description': 'Fetches the transactions for a given program',
            'strict': True,
            'parameters': {
                'type': 'object',
                'properties': {
                    'program_id': {
                        'type': 'string',
                        'description': 'The program ID to fetch transactions for',
                    },
                },
                'required': ['program_id'],
                'additionalProperties': False,
            }
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'writeSkillAndExecute',
            'description': 'Writes a skill to the file system and executes it',
            'strict': True,
            'parameters': {
                'type': 'object',
                'properties': {
                    'skill_name': {
                        'type': 'string',
                        'description': 'The name of the skill to write',
                    },
                    'skill_code': {
                        'type': 'string',
                        'description': 'The code of the skill to write',
                    },
                },
                'additionalProperties': False,
                'required': ['skill_name', 'skill_code'],
            },
        }
    },
    # {
    #     'type': 'function',
    #     'function': {
    #         'name': 'readSkills',
    #         'description': 'Analyzes all skills to show which programs and instructions have been explored, and provides recommendations for what to try next',
    #         'strict': True,
    #         'parameters': {
    #             'type': 'object',
    #             'properties': {
    #             },
    #             'required': [],
    #             'additionalProperties': False,
    #         },
    #     }
    # }
    {
        'type': 'function',
        'function': {
            'name': 'getObservation',
            'description': 'Get information about the current environment, including the current reward',
            'strict': True,
            'parameters': {
                'type': 'object',
                'properties': {
                },
                'required': [],
                'additionalProperties': False,
            },
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'getProgramIdl',
            'description': 'Get detailed IDL for a Solana program',
            'strict': True,
            'parameters': {
                'type': 'object',
                'properties': {
                    'program_id': {
                        'type': 'string',
                        'description': 'The program ID to get the IDL for (e.g "11111111111111111111111111111111" for System Program)',
                    },
                },
                'required': ['program_id'],
                'additionalProperties': False,
            },
        }
    },
    # {
    #     'type': 'function',
    #     'function': {
    #         'name': 'delegateToCodeAgent',
    #         'description': 'Delegate TypeScript code generation to a specialized coding agent that focuses on writing error-free Solana transaction code',
    #         'strict': True,
    #         'parameters': {
    #             'type': 'object',
    #             'properties': {
    #                 'skill_name': {
    #                     'type': 'string',
    #                     'description': 'Name of the skill to generate',
    #                 },
    #                 'instructions': {
    #                     'type': 'string',
    #                     'description': 'Detailed instructions for what the code should do, including specific programs and instructions to use',
    #                 },
    #                 'context': {
    #                     'type': 'object',
    #                     'description': 'Additional context like agent pubkey, program IDs, IDL information, etc.',
    #                     'properties': {
    #                         'programs': {
    #                             'type': 'array',
    #                             'items': {
    #                                 'type': 'object',
    #                                 'properties': {
    #                                     'program_id': {'type': 'string'},
    #                                     'program_name': {'type': 'string'},
    #                                     'idl_snippet': {'type': 'string'}
    #                                 }
    #                             }
    #                         },
    #                         'examples': {
    #                             'type': 'array',
    #                             'items': {'type': 'string'}
    #                         }
    #                     }
    #                 }
    #             },
    #             'required': ['skill_name', 'instructions', 'context'],
    #             'additionalProperties': False,
    #         },
    #     }
    # }
]

def getProgramIdl(program_id: str):
    CACHED_IDLS = {
        "11111111111111111111111111111111": "SYSTEM_PROGRAM.codama.json",
        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "TOKEN.codama.json",
        "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb": "TOKEN-2022.codama.json",
        "Stake11111111111111111111111111111111111111": "STAKE.codama.json",
    }
    if program_id in CACHED_IDLS:
        with open(f"voyager/idl/{CACHED_IDLS[program_id]}", "r") as f:
            return json.load(f)
    return None

class SimpleExplorer():
    def __init__(self, model_name=None, run_index=0):
        logging.info("Initializing SimpleExplorer...")
        self.env = SurfpoolEnv(rpc_url="https://api.mainnet-beta.solana.com")
        self.messages = []
        self.run_id = datetime.now().strftime("%y-%m-%d") + "_" + str(int(datetime.now().timestamp()))
        
        # Performance tracking metrics
        self.metrics = {
            "model": model_name or "openrouter/horizon-beta",
            "run_index": run_index,
            "run_id": self.run_id,
            "start_time": datetime.now().isoformat(),
            "messages": [],  # Per-message metrics
            "cumulative_rewards": [],  # Running total rewards
            "programs_discovered": {},  # Program -> first_message_index
            "instructions_discovered": {},  # (program, instruction) -> first_message_index
            "skills_created": [],  # List of skill names with message index
            "errors": [],  # List of errors with message index
            "token_usage": {  # Track token usage if available
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0
            }
        }
        
        # Create checkpoint directory for this run
        ckpt_dir = f"simple_explorer_ckpt/{self.run_id}"
        os.makedirs(ckpt_dir, exist_ok=True)
        logging.info(f"Created checkpoint directory: {ckpt_dir}")
        
        # Print the full path for easy access
        abs_ckpt_dir = os.path.abspath(ckpt_dir)
        logging.info(f"Full checkpoint path: {abs_ckpt_dir}")
        logging.info(f"Skills will be saved in: {abs_ckpt_dir}/skill/code/")
        logging.info(f"Traces will be saved in: {os.path.abspath('traces')}/{self.run_id}.json")
        
        # Create metrics directory
        os.makedirs("metrics", exist_ok=True)
        logging.info(f"Metrics will be saved in: {os.path.abspath('metrics')}/{self.run_id}_metrics.json")
        
        # Ensure traces directory exists
        os.makedirs("traces", exist_ok=True)
        
        # Use provided model or default
        self.model = model_name or "openrouter/horizon-beta"
        # Other available models:
        # 'tencent/hunyuan-a13b-instruct:free'
        # "x-ai/grok-3-mini"
        # "mistralai/mistral-small-3.2-24b-instruct:free"
        # "google/gemini-2.5-pro-exp-03-25"
        # "deepseek/deepseek-chat-v3-0324:free"
        # "openai/gpt-4o-mini"
        # "mistralai/devstral-small"
        # "moonshotai/kimi-k2:free"
        # "qwen/qwen3-coder:free"
        # "qwen/qwen3-235b-a22b-2507"
        # "google/gemma-3n-e2b-it:free"
        api_key = os.environ.get("OPENROUTER_API_KEY")
        self.llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            model=self.model,
            api_key=api_key
        )
        self.llm = self.llm.bind_tools(FUNCTIONS)
        self.skills = TypeScriptSkillManager(
            model_name=self.model,
            ckpt_dir=ckpt_dir,
            resume=False
        )
        

    def write_trace(self, messages, reward):
        with open(f"traces/{self.run_id}.json", "w") as f:
            json.dump(messages, f, indent=2)
        with open(f"traces/{self.run_id}_reward.csv", "a") as f:
            f.write(f"{len(self.messages)},{reward}\n")
    
    async def delegate_to_code_agent(self, skill_name: str, instructions: str, context: dict) -> str:
        """
        Delegate code generation to a specialized coding agent that focuses on writing
        error-free TypeScript code for Solana transactions. Gives the agent 3 tries to fix errors.
        """
        from langchain.schema import SystemMessage, HumanMessage
        
        # Create system message for the coding agent
        system_message = SystemMessage(content="""You are an expert TypeScript developer specializing in Solana blockchain development.
Your ONLY job is to write error-free TypeScript code that creates Solana transactions.

CRITICAL RULES:
1. Return ONLY the TypeScript code, no explanations or comments
2. The function MUST be: export async function executeSkill(blockhash: string): Promise<string>
3. Import ALL dependencies you use at the top of the file
4. Return a base64 encoded serialized transaction
5. Handle all errors gracefully
6. Follow the exact pattern shown in examples
7. If you receive error feedback, carefully read it and fix ALL issues

=== TYPESCRIPT RULES ===
**SIGNING ORDER IS CRITICAL**: ALWAYS set tx.recentBlockhash and tx.feePayer BEFORE any tx.partialSign() calls!

1. ALWAYS import ALL dependencies you use. Common imports:
   - SystemProgram from '@solana/web3.js' if you use SystemProgram
   - Any SPL token functions from '@solana/spl-token'
2. Function declaration MUST be: export async function executeSkill(blockhash: string): Promise<string>
3. Double-check program IDs for typos. Common program IDs:
   - System Program: 11111111111111111111111111111111
   - Token Program: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA
   - Associated Token Program: ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL
4. Do NOT use await on non-async functions
5. All async operations must be awaited properly
6. Transaction construction order: instructions → blockhash/feePayer → partialSign → serialize

=== IMPORTANT NOTES ===
1. Each skill must create exactly ONE unsigned transaction
2. The transaction will be signed and sent by the environment
3. Return the base64 encoded serialized transaction
4. ALWAYS check your imports - missing imports are the #1 cause of failures
5. ALWAYS use correct function syntax: "export async function" not "export asynchttp function"
6. **CRITICAL for CreateAccount and signing order**:
   - Generate a new Keypair with Keypair.generate()
   - ALWAYS set tx.recentBlockhash = blockhash BEFORE calling tx.partialSign()
   - ALWAYS set tx.feePayer = agentPubkey BEFORE calling tx.partialSign()
   - The correct order is: 1) Add instructions, 2) Set blockhash & feePayer, 3) partialSign, 4) serialize
7. Try putting as many valid unique instructions as possible in a single transaction

=== SYSTEM PROGRAM INSTRUCTIONS (CORRECT USAGE) ===
The web3.js library doesn't have direct methods for all System Program instructions. Here's how to use them:

Available as direct methods:
- SystemProgram.transfer() - Transfer SOL
- SystemProgram.createAccount() - Create new account
- SystemProgram.assign() - Assign account to program
- SystemProgram.createAccountWithSeed() - Create account with seed

For instructions like allocateWithSeed, assignWithSeed, transferWithSeed that don't have direct methods,
you need to create the instruction manually. Here's an example for allocate:

```typescript
// For allocate instruction (works for both regular and with seed)
const allocateParams = {
  accountPubkey: accountToAllocate,
  space: 200,
};
tx.add(SystemProgram.allocate(allocateParams));
```

Note: Some older documentation might show methods that don't exist. Always check what's actually available in the SystemProgram object.

AVAILABLE DEPENDENCIES (from package.json):
- @solana/web3.js (^1.98.2) - Transaction, SystemProgram, PublicKey, Keypair, etc.
- @solana/spl-token (^0.3.8) - All token functions
- @coral-xyz/anchor (^0.30.1) - If needed for Anchor programs""")

        # Initial human prompt
        base_human_prompt = f"""CONTEXT:
- Agent Public Key: {str(self.env.agent_keypair.pubkey())}
- Skill Name: {skill_name}

INSTRUCTIONS:
{instructions}

{self._format_context_for_code_agent(context)}

=== WORKING EXAMPLES FOR REFERENCE ===

Example 1 - System Program Transfer:
```typescript
import {{ Transaction, SystemProgram, PublicKey }} from '@solana/web3.js';

export async function executeSkill(blockhash: string): Promise<string> {{
    const tx = new Transaction();
    const agentPubkey = new PublicKey('{str(self.env.agent_keypair.pubkey())}');

    tx.add(
        SystemProgram.transfer({{
            fromPubkey: agentPubkey,
            toPubkey: agentPubkey,  // Self-transfer for safety
            lamports: 100000,
        }})
    );

    tx.recentBlockhash = blockhash;
    tx.feePayer = agentPubkey;

    const serializedTx = tx.serialize({{
        requireAllSignatures: false,
        verifySignatures: false
    }}).toString('base64');

    return serializedTx;
}}
```

Example 2 - System Program CreateAccount (IMPORTANT PATTERN):
```typescript
import {{ Transaction, SystemProgram, PublicKey, Keypair }} from '@solana/web3.js';

export async function executeSkill(blockhash: string): Promise<string> {{
    const tx = new Transaction();
    const agentPubkey = new PublicKey('{str(self.env.agent_keypair.pubkey())}');
    
    // Generate a new keypair for the account we're creating
    const newAccount = Keypair.generate();
    
    // Add CreateAccount instruction
    tx.add(
        SystemProgram.createAccount({{
            fromPubkey: agentPubkey,           // Who pays
            newAccountPubkey: newAccount.publicKey,  // The new account
            lamports: 1000000,                 // Rent-exempt amount (~0.001 SOL)
            space: 0,                          // No data needed
            programId: SystemProgram.programId // Owner will be System Program
        }})
    );
    
    // CRITICAL ORDER:
    // 1. FIRST set blockhash and fee payer
    tx.recentBlockhash = blockhash;
    tx.feePayer = agentPubkey;
    
    // 2. THEN sign with the new account keypair
    tx.partialSign(newAccount);
    
    const serializedTx = tx.serialize({{
        requireAllSignatures: false,  // Agent will sign later
        verifySignatures: false
    }}).toString('base64');
    
    return serializedTx;
}}
```

Write the TypeScript code now:"""

        # Try up to 3 times
        for attempt in range(3):
            try:
                logging.info(f"\n{'='*80}")
                logging.info(f"🤖 DELEGATE TO CODE AGENT - Attempt {attempt + 1}/3")
                logging.info(f"Skill Name: {skill_name}")
                logging.info(f"Model: {self.model}")
                logging.info(f"{'='*80}")
                
                # Prepare the human message
                if attempt == 0:
                    human_message = HumanMessage(content=base_human_prompt)
                    logging.info("First attempt - no error feedback")
                else:
                    # Add error feedback for retry attempts
                    logging.info(f"Retry attempt {attempt + 1} - Adding error feedback:")
                    logging.info(f"Previous error: {error_info['error']}")
                    if error_info.get('details'):
                        logging.info(f"Error details: {error_info['details'][:500]}...")  # First 500 chars
                    
                    error_feedback = f"""{base_human_prompt}

=== PREVIOUS ATTEMPT {attempt} FAILED ===
Error: {error_info['error']}
Details: {error_info.get('details', 'No details available')}

Please fix these errors and generate the corrected code:"""
                    human_message = HumanMessage(content=error_feedback)
                
                # Determine the best model for coding
                coding_model = self.model
                logging.info(f"Using model: {coding_model}")
                
                # Create a separate LLM instance for coding with lower temperature
                coding_llm = ChatOpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    model=coding_model,
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    temperature=0.1 if attempt == 0 else 0.2,  # Slightly higher temp on retries
                    max_tokens=2000,
                )
                
                # Log the instructions being sent
                logging.info(f"Instructions summary: {instructions[:200]}...")
                
                # Invoke the LLM using LangChain
                logging.info("Invoking LLM for code generation...")
                response = await coding_llm.ainvoke([system_message, human_message])
                
                generated_code = response.content.strip()
                logging.info(f"Generated code length: {len(generated_code)} characters")
                
                # Clean up the code if it has markdown code blocks
                if generated_code.startswith("```"):
                    lines = generated_code.split("\n")
                    # Remove first and last lines if they're code block markers
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines[-1] == "```":
                        lines = lines[:-1]
                    generated_code = "\n".join(lines)
                    logging.info("Cleaned markdown code blocks")
                
                # Log first few lines of generated code
                code_preview = generated_code.split('\n')[:10]
                logging.info("Generated code preview:")
                for line in code_preview:
                    logging.info(f"  {line}")
                
                # Test the generated code
                logging.info(f"Testing generated code (attempt {attempt + 1}/3)...")
                test_result = await self._test_generated_code(skill_name, generated_code)
                
                if test_result['success']:
                    logging.info(f"✅ Code generation successful on attempt {attempt + 1}")
                    return generated_code
                else:
                    error_info = {
                        'error': test_result.get('reason', 'Unknown error'),
                        'details': test_result.get('stderr', test_result.get('details', ''))
                    }
                    logging.warning(f"❌ Code generation attempt {attempt + 1} failed")
                    logging.warning(f"Error: {error_info['error']}")
                    if error_info.get('details'):
                        logging.warning(f"Full error details:\n{error_info['details']}")
                    
                    # Also log the stdout if available
                    if test_result.get('stdout'):
                        logging.warning(f"Stdout:\n{test_result['stdout']}")
                    
                    if attempt == 2:  # Last attempt
                        logging.error(f"❌ All 3 attempts failed for skill {skill_name}")
                        logging.error("Final generated code that failed:")
                        logging.error(generated_code)
                        return None
                        
            except Exception as e:
                logging.error(f"❌ Exception in delegate_to_code_agent attempt {attempt + 1}: {e}")
                logging.error(f"Exception type: {type(e).__name__}")
                import traceback
                logging.error(f"Traceback:\n{traceback.format_exc()}")
                
                if attempt == 2:  # Last attempt
                    logging.error(f"All attempts failed due to exceptions")
                    return None
                    
                # Set error_info for next iteration
                error_info = {
                    'error': f"Exception: {type(e).__name__}: {str(e)}",
                    'details': traceback.format_exc()
                }
                    
        return None
    
    async def _test_generated_code(self, skill_name: str, code: str) -> dict:
        """Test the generated code to see if it compiles and runs"""
        logging.info(f"Testing code for skill: {skill_name}")
        try:
            # We need to temporarily save the code to test it properly
            # This mimics what execute_skill does
            temp_file_path = os.path.join(self.skills.ckpt_dir, "skill", "code", f"_temp_test_{skill_name}.ts")
            
            # Write the code to a temporary file
            with open(temp_file_path, "w") as f:
                f.write(code)
            logging.info(f"Wrote temporary test file: {temp_file_path}")
            
            try:
                # Get the latest blockhash for testing
                blockhash_resp = await self.env.client.get_latest_blockhash()
                latest_blockhash_str = str(blockhash_resp.value.blockhash)
                logging.info(f"Got blockhash for testing: {latest_blockhash_str[:8]}...")
                
                # Use execute_skill with positional arguments (matching the method signature)
                logging.info("Executing skill for testing...")
                result = self.skills.execute_skill(
                    temp_file_path,  # file_path
                    10000,  # timeout_ms
                    str(self.env.agent_keypair.pubkey()),  # agent_pubkey
                    latest_blockhash_str  # latest_blockhash
                )
                
                logging.info(f"Execution result keys: {list(result.keys())}")
                
                # The result should have a structure like:
                # {"serialized_tx": "..."} for success
                # {"success": False, "reason": "...", "stderr": "..."} for failure
                
                # Check if we got a serialized transaction (success case)
                if "serialized_tx" in result and result["serialized_tx"]:
                    # Try to decode it to ensure it's valid
                    try:
                        tx_bytes = base64.b64decode(result["serialized_tx"])
                        logging.info(f"✅ Successfully generated transaction ({len(tx_bytes)} bytes)")
                        # If we can decode it, the code works
                        return {
                            "success": True,
                            "serialized_tx": result["serialized_tx"]
                        }
                    except Exception as e:
                        logging.error(f"Failed to decode transaction: {e}")
                        return {
                            "success": False,
                            "reason": f"Invalid transaction format: {str(e)}",
                            "stderr": str(e)
                        }
                else:
                    # This is an error case
                    logging.warning("No serialized_tx in result - execution failed")
                    
                    # Log all available error information
                    if "error" in result:
                        logging.warning(f"Error field: {result['error']}")
                    if "reason" in result:
                        logging.warning(f"Reason field: {result['reason']}")
                    if "stderr" in result:
                        logging.warning(f"Stderr:\n{result['stderr']}")
                    if "stdout" in result:
                        logging.warning(f"Stdout:\n{result['stdout']}")
                    if "details" in result:
                        logging.warning(f"Details:\n{result['details']}")
                    
                    # make sure we have the right structure
                    if "success" in result and not result["success"]:
                        return result  # Already has the right format
                    else:
                        # Convert to error format if needed
                        return {
                            "success": False,
                            "reason": result.get("error", result.get("reason", "Unknown error")),
                            "stderr": result.get("stderr", str(result)),
                            "details": result.get("details", "")
                        }
                    
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    logging.info("Cleaned up temporary test file")
                    
        except Exception as e:
            logging.error(f"Exception in _test_generated_code: {e}")
            import traceback
            logging.error(f"Traceback:\n{traceback.format_exc()}")
            return {
                "success": False,
                "reason": f"Test execution error: {str(e)}",
                "stderr": str(e)
            }
    
    def _format_context_for_code_agent(self, context: dict) -> str:
        """Format the context information for the coding agent."""
        formatted = []
        
        if "programs" in context:
            formatted.append("\nPROGRAM INFORMATION:")
            for prog in context["programs"]:
                formatted.append(f"\nProgram: {prog.get('program_name', 'Unknown')}")
                formatted.append(f"ID: {prog.get('program_id', 'Unknown')}")
                if "idl_snippet" in prog:
                    formatted.append(f"IDL Info:\n{prog['idl_snippet']}")
        
        if "examples" in context:
            formatted.append("\nEXAMPLE CODE PATTERNS:")
            for i, example in enumerate(context["examples"], 1):
                formatted.append(f"\nExample {i}:")
                formatted.append(example)
        
        return "\n".join(formatted)
    
    async def save_and_execute_skill(self, skill_name: str, skill_code: str, tool_message: Dict[str, Any]):
        """Common method to save a skill and execute it. Used by both writeSkillAndExecute and delegateToCodeAgent."""
        # Save skill file directly
        skill_dir = f"{self.skills.ckpt_dir}/skill/code"
        file_path = os.path.join(skill_dir, f"{skill_name}.ts")
        with open(file_path, "w") as f:
            f.write(skill_code)
        
        # Use the add_new_skill method to register it properly
        skill_info = {
            'program_name': skill_name,
            'program_code': skill_code
        }
        self.skills.add_new_skill(skill_info)
        
        # Record skill creation in metrics
        self.record_message_metrics(len(self.messages), skill_name=skill_name)
        
        # Execute the skill
        await self.execute_skill(skill_name, tool_message)
    
    def save_metrics(self):
        """Save current metrics to JSON file"""
        self.metrics["end_time"] = datetime.now().isoformat()
        self.metrics["total_messages"] = len(self.messages)
        self.metrics["final_reward"] = self.env.total_reward
        
        # Calculate summary statistics
        if self.metrics["cumulative_rewards"]:
            self.metrics["summary"] = {
                "max_reward": max(self.metrics["cumulative_rewards"]),
                "final_reward": self.metrics["cumulative_rewards"][-1] if self.metrics["cumulative_rewards"] else 0,
                "total_programs": len(self.metrics["programs_discovered"]),
                "total_instructions": len(self.metrics["instructions_discovered"]),
                "total_skills": len(self.metrics["skills_created"]),
                "total_errors": len(self.metrics["errors"]),
                "messages_sent": len(self.messages)
            }
        
        with open(f"metrics/{self.run_id}_metrics.json", "w") as f:
            json.dump(self.metrics, f, indent=2)
    
    def record_message_metrics(self, message_index, reward_delta=0, program=None, instruction=None, skill_name=None, error=None):
        """Record metrics for a specific message"""
        metric_entry = {
            "message_index": message_index,
            "timestamp": datetime.now().isoformat(),
            "reward_delta": reward_delta,
            "cumulative_reward": self.env.total_reward
        }
        
        # Track program discovery
        if program and program not in self.metrics["programs_discovered"]:
            self.metrics["programs_discovered"][program] = message_index
            metric_entry["new_program"] = program
        
        # Track instruction discovery
        if program and instruction:
            key = f"{program}:{instruction}"
            if key not in self.metrics["instructions_discovered"]:
                self.metrics["instructions_discovered"][key] = message_index
                metric_entry["new_instruction"] = key
        
        # Track skill creation
        if skill_name:
            self.metrics["skills_created"].append({
                "name": skill_name,
                "message_index": message_index
            })
            metric_entry["skill_created"] = skill_name
        
        # Track errors
        if error:
            self.metrics["errors"].append({
                "error": str(error),
                "message_index": message_index
            })
            metric_entry["error"] = str(error)
        
        self.metrics["messages"].append(metric_entry)
        self.metrics["cumulative_rewards"].append(self.env.total_reward)
        
        # Save metrics after each message
        self.save_metrics()
    
    def analyze_skills(self, skills):
        """Analyze skills to extract program interactions and instruction usage"""
        analysis = {
            "total_skills": len(skills),
            "skill_names": list(skills.keys()),
            "programs_explored": {},
            "system_program_instructions": [],
            "token_program_instructions": [],
            "associated_token_instructions": [],
            "other_programs": [],
            "recommendations": []
        }
        
        # Analyze each skill
        for skill_name, skill_desc in skills.items():
            skill_file_path = os.path.join(self.skills.ckpt_dir, "skill", "code", f"{skill_name}.ts")
            if os.path.exists(skill_file_path):
                with open(skill_file_path, 'r') as f:
                    code = f.read()
                    
                    # Check for System Program usage
                    if "SystemProgram" in code:
                        if "SystemProgram.transfer" in code:
                            analysis["system_program_instructions"].append("Transfer (2)")
                        if "SystemProgram.createAccount" in code:
                            analysis["system_program_instructions"].append("CreateAccount (0)")
                        if "SystemProgram.allocate" in code:
                            analysis["system_program_instructions"].append("Allocate (8)")
                        if "SystemProgram.assign" in code:
                            analysis["system_program_instructions"].append("Assign (1)")
                        if "SystemProgram.createAccountWithSeed" in code:
                            analysis["system_program_instructions"].append("CreateAccountWithSeed (3)")
                    
                    # Check for Token Program usage
                    if "TokenProgram" in code or "createTransferInstruction" in code:
                        analysis["token_program_instructions"].append(skill_name)
                    if "createInitializeMintInstruction" in code:
                        analysis["token_program_instructions"].append("InitializeMint")
                    if "createInitializeAccountInstruction" in code:
                        analysis["token_program_instructions"].append("InitializeAccount")
                    
                    # Check for Associated Token Program
                    if "createAssociatedTokenAccountInstruction" in code:
                        analysis["associated_token_instructions"].append("CreateAssociatedTokenAccount")
                    
                    # Check for other programs
                    if "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4" in code:
                        analysis["other_programs"].append("Jupiter")
                    if "PERPHjGBqRHArX4DySjwM6UJHiR3sWAatqfdBS2qQJu" in code:
                        analysis["other_programs"].append("Perpetuals")
        
        # Remove duplicates
        analysis["system_program_instructions"] = list(set(analysis["system_program_instructions"]))
        analysis["token_program_instructions"] = list(set(analysis["token_program_instructions"]))
        analysis["associated_token_instructions"] = list(set(analysis["associated_token_instructions"]))
        analysis["other_programs"] = list(set(analysis["other_programs"]))
        
        # Add recommendations based on what's missing
        system_instructions_tried = len(analysis["system_program_instructions"])
        if system_instructions_tried < 12:
            analysis["recommendations"].append(f"System Program: Only {system_instructions_tried}/12+ instructions tried. Try: CreateAccount, Allocate, Assign, CreateAccountWithSeed, AdvanceNonceAccount, etc.")
        
        if len(analysis["token_program_instructions"]) < 5:
            analysis["recommendations"].append("Token Program: Explore more instructions like Approve, Revoke, Burn, Freeze, Thaw, etc.")
        
        if len(analysis["associated_token_instructions"]) < 2:
            analysis["recommendations"].append("Associated Token Program: Try CreateIdempotent and other instructions")
        
        return analysis

    async def step(self, max_messages: int):
        # finish_reason = "tool_calls"
        done = False
        while not done and len(self.messages) < max_messages:
            # logging.info(f"Messages: {self.messages}")
            self.write_trace(self.messages, self.env.total_reward)
            
            # Enhanced logging for LLM request
            logging.info(f"\n{'='*80}")
            logging.info(f"🔵 LLM REQUEST - Model: {self.model}")
            logging.info(f"Messages count: {len(self.messages)}")
            if self.messages:
                last_msg = self.messages[-1]
                logging.info(f"Last message role: {last_msg.get('role', 'unknown')}")
                content = str(last_msg.get('content', ''))[:200]
                if content:
                    logging.info(f"Last message preview: {content}...")
            logging.info(f"{'='*80}\n")
            
            # To give a LangChain chat model access to tools, you pass the `tools` argument (a list of tool definitions)
            # and optionally `tool_choice` to the model's `invoke` method, as shown below:
            response = await self.llm.ainvoke(self.messages)
            
            # Enhanced logging for LLM response
            logging.info(f"\n{'='*80}")
            logging.info(f"🟢 LLM RESPONSE")
            if response.tool_calls:
                logging.info(f"Tool calls: {[tc['name'] for tc in response.tool_calls]}")
            if response.content:
                content_preview = str(response.content)[:200]
                logging.info(f"Content preview: {content_preview}...")
            logging.info(f"{'='*80}\n")
            
            self.messages.append(response.model_dump())
            self.write_trace(self.messages, self.env.total_reward)
            
            # finish_reason = response.choices[0].finish_reason
            # if finish_reason == "tool_calls":
            done = True
            if response.tool_calls:
                done = False
                for tool_call in response.tool_calls:
                    function_name = tool_call['name']
                    function_args = tool_call['args']
                    if not isinstance(function_args, dict):
                        try:
                                function_args = json.loads(tool_call['args'])
                        except Exception as e:
                            logging.error(f"Error parsing arguments for tool call {function_name}: {e}")
                            function_args = {}
                    tool_message = {
                        "role": "tool",
                        "tool_call_id": tool_call['id'],
                        "name": function_name,
                        "content": ""
                    }
                    logging.info(f"Function call: {function_name} with args: {function_args}")
                    if function_name == "executeSkill":
                        skill_name = function_args["skill_name"]
                        await self.execute_skill(skill_name, tool_message)
                    elif function_name == "fetchTransactions":
                        program_id = function_args["program_id"]
                        txs = await self.env.fetch_transactions(program_id)
                        tool_message["content"] = json.dumps(txs)
                    elif function_name == "writeSkillAndExecute":
                        skill_name = function_args["skill_name"] if 'skill_name' in function_args else str(uuid.uuid4())
                        skill_code = function_args["skill_code"]
                        await self.save_and_execute_skill(skill_name, skill_code, tool_message)
                        
                        # tool_message["content"] = f"Skill {skill_name} written to {file_path}"
                    # elif function_name == "readSkills":
                    #     skills = self.skills.get_skills()
                    #     skill_analysis = self.analyze_skills(skills)
                    #     tool_message["content"] = json.dumps(skill_analysis, indent=2)
                    #     logging.info(f"Skills analysis: {json.dumps(skill_analysis, indent=2)}")
                    elif function_name == "getObservation":
                        obs = await self.env._get_observation()
                        tool_message["content"] = f"{json.dumps({ 'observation': obs, 'reward': self.env.total_reward })}"
                    elif function_name == "getProgramIdl":
                        program_id = function_args["program_id"]
                        idl = getProgramIdl(program_id)
                        tool_message["content"] = f"{json.dumps({ 'idl': idl })}"
                    # elif function_name == "delegateToCodeAgent":
                    #     skill_name = function_args["skill_name"] if 'skill_name' in function_args else str(uuid.uuid4())
                    #     instructions = function_args["instructions"]
                    #     context = function_args["context"]
                        
                    #     # Generate code using a specialized coding agent
                    #     generated_code = await self.delegate_to_code_agent(skill_name, instructions, context)
                        
                    #     if generated_code:
                    #         await self.save_and_execute_skill(skill_name, generated_code, tool_message)
                    #     else:
                    #         tool_message["content"] = json.dumps({
                    #             "success": False,
                    #             "error": "Failed to generate code"
                    #         })
                    else:
                        raise ValueError(f"Unexpected function name: {function_name}")
                    self.messages.append(tool_message)
                    logging.info(f"Tool message: {tool_message}")

        self.write_trace(self.messages, self.env.total_reward)
        return None, False

    async def execute_skill(self, skill_name: str, tool_message: Dict[str, Any]):
        skills = self.skills.get_skills()
        skill_entry = skills.get(skill_name, None)
        
        if skill_entry is None:
            tool_message["content"] = f"Skill {skill_name} not found"
            self.record_message_metrics(len(self.messages), error=f"Skill {skill_name} not found")
        else:
            # Use new format - construct the file path
            skill_file_path = os.path.join(self.skills.ckpt_dir, "skill", "code", f"{skill_name}.ts")
            try:
                # Pass agent pubkey and latest blockhash to skill execution
                agent_pubkey = str(self.env.agent_keypair.pubkey())
                
                # Fetch latest blockhash before skill execution
                blockhash_resp = await self.env.client.get_latest_blockhash()
                latest_blockhash_str = str(blockhash_resp.value.blockhash)
                
                result = self.skills.execute_skill(skill_file_path, agent_pubkey=agent_pubkey, latest_blockhash=latest_blockhash_str)
                tx_data = result.get("serialized_tx")
                if not tx_data:
                    error_details = {
                        "error": "Skill execution failed",
                        "skill_name": skill_name,
                        "details": result,
                        "suggestion": "Check for syntax errors, missing imports, or typos in the skill code"
                    }
                    tool_message["content"] = json.dumps(error_details)
                    self.record_message_metrics(len(self.messages), error=f"Skill execution failed: {skill_name}")
                else:
                    # Get transaction data from skill result
                    tx_bytes = base64.b64decode(tx_data)
                    tx = Transaction.from_bytes(tx_bytes)
                    
                    # Sign with agent keypair
                    # Fetch the latest blockhash from surfpool
                    # blockhash_resp = await self.env.client.get_latest_blockhash()
                    # tx.message.recent_blockhash = blockhash_resp.value.blockhash
                    tx_bytes = bytes(tx)
                    signed_tx = self.env._partial_sign_transaction(tx_bytes, [self.env.agent_keypair])
                    
                    # Send transaction through surfpool
                    obs, step_reward, _, _, info = await self.env.step(signed_tx)
                    
                    # Extract program and instruction info from transaction
                    programs_in_tx = info.get("programs_interacted", [])
                    instructions_in_tx = info.get("instructions_executed", [])
                    
                    # Record metrics with discovered programs/instructions
                    for prog in programs_in_tx:
                        for inst in instructions_in_tx:
                            self.record_message_metrics(
                                len(self.messages), 
                                reward_delta=step_reward,
                                program=prog,
                                instruction=inst
                            )
                    
                    if not programs_in_tx:  # If no specific program info, just record reward
                        self.record_message_metrics(len(self.messages), reward_delta=step_reward)
                    
                    logging.info(f"Step reward: {step_reward}, total session reward: {self.env.total_reward}")
                    tool_message["content"] = f"{json.dumps({ 'observation': obs, 'info': info })}"
                    return step_reward
            except Exception as e:
                logging.error(f"Error running skill {skill_name}: {e}")
                tool_message["content"] = f"Exception in skill {skill_name}: {e}"
                self.record_message_metrics(len(self.messages), error=f"Exception in skill {skill_name}: {e}")
        return 0.0

    async def rollout(self, max_messages=200):
        logging.info(f"Starting rollout with max_messages={max_messages}")
        observation, _ = await self.reset()
        logging.info(f"Observation: {observation}")
        self.messages.append({
            'role': 'user',
            'content': f"Last observation: {observation}"
        })
        
        message_count = 0
        while message_count < max_messages:
            _, done = await self.step(max_messages)
            # Reward is tracked in env.total_reward
            message_count = len(self.messages)
            
            logging.info(f"Step completed. Messages: {message_count}/{max_messages}, Total session reward: {self.env.total_reward}")
            
            # Check if we've reached message limit
            if message_count >= max_messages:
                logging.info(f"Reached maximum message limit of {max_messages}")
                break
                
            if done:
                break
        
        # Save final metrics
        self.save_metrics()
        return self.env.total_reward, False

    async def reset(self):
        observation, info = await self.env.reset()
        self.messages = [{
            'role': 'system',
            'content': SYSTEM_PROMPT.format(
                agent_pubkey=self.env.agent_keypair.pubkey(), 
                # protocol_list=json.dumps(list(KNOWN_PROGRAM_IDS.keys()), indent=2)
                protocol_list="11111111111111111111111111111111, ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL, TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
            ),
        }]
        return observation, info

def run_simple_explorer(model_name=None, max_messages=200, run_index=0):
    import asyncio
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Reconfigure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', force=True)

    async def main():
        explorer = SimpleExplorer(model_name=model_name, run_index=run_index)
        logging.info(f"Starting rollout for model: {explorer.model}, run {run_index}")
        total_reward, _ = await explorer.rollout(max_messages=max_messages)
        logging.info(f"Total reward: {total_reward}")
        return explorer.metrics
    
    return asyncio.run(main())

def run_model_comparison(models_to_test=None, runs_per_model=10, max_messages=200):
    """Run multiple models multiple times for comparison"""
    
    # Default models to test
    if models_to_test is None:
        models_to_test = [
            "openrouter/horizon-beta",
            "openai/gpt-4o-mini",
            "google/gemini-2.5-pro-exp-03-25",
            "deepseek/deepseek-chat-v3-0324:free"
        ]
    
    all_metrics = []
    
    for model in models_to_test:
        print(f"\n{'='*80}")
        print(f"Testing model: {model}")
        print(f"{'='*80}")
        
        for run_index in range(runs_per_model):
            print(f"\nRun {run_index + 1}/{runs_per_model} for {model}")
            try:
                metrics = run_simple_explorer(
                    model_name=model,
                    max_messages=max_messages,
                    run_index=run_index
                )
                all_metrics.append(metrics)
            except Exception as e:
                print(f"Error in run {run_index + 1} for {model}: {e}")
                continue
    
    # Save consolidated metrics
    consolidated_file = f"metrics/comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(consolidated_file, "w") as f:
        json.dump(all_metrics, f, indent=2)
    
    print(f"\nAll metrics saved to: {consolidated_file}")
    return all_metrics

if __name__ == "__main__":
    run_simple_explorer()