# Contributing to Solana Bench

## Priority Tasks

- Improve simple_explorer.py as much as possible
- Improve trajectory visualization & sanity checks

## Constraints

- Keep for loop simple
- Minimize additional LLM / agent usage in simple_explorer for now
- Focus on improving the tool calls & decompilation of Solana transactions

## Current Benchmarks

Current benchmark for simple_explorer is `9` rewards over 150 iterations. Reward is # of unique instructions from successfully executed transactions. Iteration = # of LLM messages.

We want to get this >25 rewards in 150 iterations, ideally as high as 100. Expectation is that a fine-tuned agent should get >10 reward in the first step, from a well constructed prompt.

## How to Contribute

### Getting Started

1. **Fork the repo**: [github.com/ngundotra/solana-gym-env](https://github.com/ngundotra/solana-gym-env)
2. **Pick a protocol**: Choose one you know well
3. **Create your environment**: Use our template as a starting point
4. **Test with multiple models**: Ensure it works across different LLMs
5. **Submit a PR**: Include example runs and performance metrics

### What Makes a Great Contribution

✅ **Clear, Protocol-Specific Prompts**: Models should understand what they're exploring

✅ **Comprehensive SDK Examples**: Real code that works on mainnet

✅ **Meaningful Reward Shaping**: Incentivize learning the protocol deeply

✅ **Documentation**: Explain why your approach teaches models effectively

✅ **Evaluation Metrics**: Show how different models perform

## Building Protocol-Specific Environments

### Step 1: Fork the Template

```bash
cp code_loop_explorer.py protocols/your_protocol_explorer.py
```

### Step 2: Add Your Protocol's Concepts

- System prompts with your terminology
- SDK examples from your docs
- Common patterns and gotchas

### Step 3: Design Reward Functions

- What indicates basic understanding?
- What shows advanced mastery?
- What would impress your protocol team?

### Step 4: Test with Multiple Models

- Ensure it's not too easy or too hard
- Verify rewards align with actual understanding

### Step 5: Submit Your PR

- Include sample runs
- Document what your rewards measure
- Explain why these metrics matter

## Example: Kamino-Specific Environment

Here's what a Kamino contribution might look like:

```python
class KaminoLendingExplorer(CodeLoopExplorer):
    def get_system_prompt(self):
        return f"""
        You are exploring Kamino Lending Protocol.

        Core Concepts:
        - Obligations: User's borrow/lend positions
        - Reserves: Lending pools for different assets
        - kTokens: Receipt tokens for deposits

        Available SDK: @kamino-finance/klend-sdk

        Examples:
        {self.load_kamino_examples()}
        """

    def calculate_reward(self, tx_info):
        base_reward = super().calculate_reward(tx_info)

        # Kamino-specific bonus rewards
        if self.completed_deposit_borrow_repay_cycle():
            base_reward += 10  # Full lending cycle bonus

        if self.used_leverage_properly():
            base_reward += 5   # Advanced feature bonus

        if self.interacted_with_new_reserve():
            base_reward += 3   # Exploration bonus

        return base_reward
```

## Protocol Environments We Need

### DeFi Protocols (each needs its own environment!)

- **Kamino**: Test obligation management, multi-asset lending, leverage loops
- **Drift**: Evaluate perpetuals trading, DLOB understanding, liquidations
- **Phoenix**: Assess limit order placement, market making strategies
- **Orca/Raydium**: Measure pool interaction, concentrated liquidity understanding
- **Jupiter**: Test aggregation logic, route optimization

### Infrastructure Protocols

- **Metaplex**: NFT minting, metadata, collections
- **Squads**: Multisig creation and management
- **Pyth**: Oracle price feed integration

## SDK Environments We Need

### TypeScript/JavaScript

- **@solana/kit**: Modern, composable Solana development
- **@coral-xyz/anchor**: IDL-based program interactions
- **@metaplex-foundation/js**: NFT-specific operations

### Other Languages

- **Rust**: Native Solana program interactions
- **Python**: solana-py, anchorpy ecosystems
- **Go**: gagliardetto/solana-go patterns

## What We Need From the Community

**Right now, we're basically just testing if models know @solana/web3.js.** That's not enough. We need YOUR help to build comprehensive evaluation suites for the entire Solana ecosystem.

### The Vision: Protocol-Specific Mini-Environments

Every major protocol should have its own evaluation environment. Why? Because knowing how to transfer SOL is vastly different from understanding Kamino's lending markets or Drift's perpetuals.

**What Protocols Should Submit**:
1. **Custom System Prompts** with your protocol's concepts
2. **SDK Integration Examples** showing real usage patterns
3. **Reward Functions** that measure protocol mastery
4. **Success Criteria** specific to your protocol

### Why Protocol-Specific Rewards Matter

Generic instruction discovery only tells part of the story. Protocol-specific rewards measure if models actually understand your protocol:

**Kamino Rewards**:
- Deposit → Borrow → Repay cycle = **Understanding lending**
- Leverage loops = **Understanding capital efficiency**
- Liquidation execution = **Understanding risk**

**Drift Rewards**:
- Open → Modify → Close position = **Understanding perps**
- Place limit orders on DLOB = **Understanding orderbook**
- Execute JIT liquidity = **Understanding MEV**

**Phoenix Rewards**:
- Place bid/ask spreads = **Understanding market making**
- Cancel and replace orders = **Understanding order management**
- Consume liquidity efficiently = **Understanding execution**

## Open Research Challenges

### The Multiplication Problem

If we need 10 protocols × 3 SDKs × 3 languages = 90 unique environments, we're probably doing something wrong. 

**What might work better:**
- **"Raw" Environments**: Force models to build everything from scratch with ONLY @solana/web3.js
- **Auto-discovery from IDLs**: Automatically generate rewards from program IDLs
- **Transaction Mining**: Learn protocol patterns from historical transactions
- **Cross-protocol transfer**: Can knowledge of one DEX help with another?

### Protocol-Agnostic Discovery

The holy grail would be an environment where models can discover and interact with ANY protocol without protocol-specific prompts.

**Dream contribution**: A system that can:
1. Take any program ID
2. Fetch its IDL (if available) or reverse-engineer from transactions
3. Generate exploration strategies
4. Create meaningful rewards without human intervention

### Concrete Research Ideas

**"Raw" Environment Challenge #1: Pure Discovery**

Start with a raw environment using ONLY @solana/web3.js - no protocol SDKs allowed. Can a model figure out how to swap on Jupiter just from the program ID and fetched transactions? This tests true protocol understanding.

**"Raw" Environment Challenge #2: Auto-Generated SDKs with @solana/kit**

What if we could make ANY protocol work automatically? Here's the idea:

1. **Pick any Solana program** (like Jupiter or Drift)
2. **Fetch its IDL** from the chain
3. **Use Codama to auto-generate a TypeScript SDK** from that IDL
4. **Include the SDK in the model's prompt** ("Here's how to interact with this program...")
5. **Prepend the SDK to whatever code the model writes** (so it actually compiles)
6. **Run it with @solana/kit** (Codama SDKs only work with kit, not web3.js)

This would be a separate "raw" environment - just Codama + @solana/kit. No manual protocol-specific work needed! Point at a program ID and go. The model sees nice TypeScript functions instead of raw instruction building.

Even better: After collecting successful runs, export them to OpenPipe or similar for fine-tuning. Build first, train later.

## Testing Your Contribution

1. Run against at least 3 different models
2. Verify rewards correlate with actual understanding
3. Include metrics showing performance distribution
4. Document any model-specific quirks you discover

## Code Style Guidelines

- Follow existing patterns in `code_loop_explorer.py`
- Keep system prompts clear and concise
- Document reward calculations thoroughly
- Include type hints where appropriate
- Add docstrings to all public methods

## Debugging Your Experiments

### 🔍 LangGraph Studio - See Everything

LangGraph Studio is invaluable for debugging your agent's behavior. It shows you the complete input/output for every LLM call, making it easy to spot where things go wrong.

**Setup**:

```bash
# Add to your .env file
LANGGRAPH_API_KEY=your_api_key_here

# LangGraph will automatically log all LangChain interactions
```

**What You'll See**:

- Full message history with token counts
- Exact tool calls and responses
- Model reasoning in real-time
- Where models get stuck or confused

This visibility was crucial for discovering that models were making variable name errors in tool calls but not in code blocks.

### 📊 Metrics and Traces

Every run generates detailed traces in `metrics/` and `traces/`:

- Transaction success/failure patterns
- Reward progression over time
- Which programs and instructions were discovered
- Error frequencies and types

## Questions?

Open an issue on GitHub with the `question` label and we'll help you get started!