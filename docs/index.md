{% include nav-header.html %}

# Solana Composability Benchmark: How Well Can LLMs Build Complex Transactions?

Why can’t we simply ask an LLM to write a crypto trading bot—one that listens to token prices, spots price differences between DEXes, and makes money by exploiting them? That would be amazing. The bot could monitor the chain, buy low on one platform, sell high on another, and do it all in seconds. We’re not quite there yet—but this experiment explores how close we can get today by measuring how well LLMs can string together diverse Solana programs in a single transaction.

## The Problem with Today's Blockchain Agents

Building superintelligent blockchain agents that respond to market changes is still one of the biggest challenges in the crypto community. Most current blockchain agents use RAG-augmented LLMs connected to fixed toolsets—sometimes via MCP servers—to execute predefined actions. They handle simple tasks fine, but break down when the environment changes in subtle ways.

On blockchains, the same token can be priced differently across decentralized exchanges, lending protocols, and other on-chain programs. In theory, a bot could exploit those differences. In practice, doing so often requires chaining multiple programs together in the correct order—sometimes within a single transaction—before the opportunity disappears. Most current LLM agents can’t plan and execute these complex, multi-step interactions reliably, so they miss out.

## Why Solana Makes This Harder And More Interesting

Solana’s architecture is uniquely suited for complex transactions. Unlike many EVM-based chains, where one transaction typically calls one contract, Solana allows a single transaction to invoke many different programs. This makes it possible to compose highly efficient multi-protocol operations—but it also demands more reasoning and composability from the agent.

A truly capable Solana agent should be able to:

1. **Compose** complex transactions spanning multiple programs.
2. **Debug** malformed transactions using onchain metadata.
3. **Chain** multiple transactions into coherent long-term strategies.

These capabilities are exactly what's needed to profit from cross-program price differences at scale. They're the missing piece in today's LLM agents.

## The Holy Grail: A True Financial Sandbox

In an ideal world, we could run a perfect financial test: a sandboxed replica of mainnet where an LLM could detect arbitrage opportunities and execute real transactions in response. This would be the holy grail of LLM blockchain agents; a proving ground for the next generation of AI agent engineering.

Thanks to [Surfpool](https://surfpool.run), we can already spin up sandboxed versions of mainnet and let agents submit transactions safely. What we can't yet do is track an agent's entire portfolio in that sandbox with the same accuracy and completeness as Jupiter Portfolio. Running a local test validator with full portfolio tracking is beyond the scope of this project.

## Our Simplified Approach

Since we can’t yet run the perfect arbitrage simulation, we went simpler: measure an LLM’s ability to chain together as many unique Solana program instructions as possible in successful transactions. On Solana, instructions are the atomic building blocks of program interaction, and successfully chaining diverse instructions together signals a deeper understanding of Solana protocols.

This acts as a proxy for deep Solana fluency—testing whether a model can compose, sequence, and execute complex multi-program interactions, even without a direct profit motive. If a model can’t build diverse and valid transactions in a controlled setting, it’s unlikely to succeed in the chaotic world of on-chain arbitrage.

`<image: transaction trace showing composition>`

## Introducing the Solana Composability Benchmark

In this benchmark, each model had 50 messages to work with. In each message, the model could write TypeScript code to generate exactly one transaction. If the transaction succeeded, each unique instruction within it counted toward the model’s total score. The goal: maximize the diversity of instructions within the message limit.

`<image: leaderboard of model performance>`

## Results

The results were clear: Anthropic’s Claude Sonnet 4 outperformed all other models in discovering new programs, exploiting the reward environment, and composing complex Solana transactions. However, its high cost makes it impractical for large-scale deployment.

For a more budget-friendly option, Google’s Gemini 2.5 Flash proved the best at the lower price tier—coming close to its Pro sibling in raw capability while being significantly cheaper.

## The Path Forward

We see this as just the start. The `Surfpool` environment we open-sourced for this project, combined with the Typescript code-action loop, lowers the barrier for creating new benchmarks. An `environment` can be defined as three things

1. **System prompt** encouraging exploration with well-formed examples.
2. **Pre-installed dependencies** listed in `package.json`.
3. **Reward filter** that rewards transactions based on interacting with specific programs

For example, a DeFi-focused environment could modify the system prompt to push the model toward specific DeFi programs, pre-install relevant SDKs, and adjust the reward filter to count only instructions that hit those targets.

## Call to Action

If you're building in this space, help us make more complex DeFi benchmarks. The more realistic the environment, the closer we get to the holy grail of on-chain AI agents. Let’s move beyond toy benchmarks and start building the testbeds that will power the next generation of autonomous blockchain systems.

## Appendix

For in-depth exploration of the code generated by the different LLMs, check out this interactive guide.
`<interactive links to metric traces>`

To cite this blog post please use:

```
Gundotra, N. (2025). Solana Composability Benchmark: How Well Can LLMs Build Complex Transactions? Retrieved from https://ngundotra.github.io/solana-gym-env
```

## Complete Benchmark Results: Top Trajectories

Below are the top 5 runs for each model from our `basic` benchmark, sorted by total reward. The sparklines show how each run progressed over the 50 message limit.

| Model            | Model Rank | Run ID   | Total Reward | Programs |
| ---------------- | ---------- | -------- | ------------ | -------- |
| claude-sonnet-4  | 1          | b617e7c9 | 181          | 5        |
| claude-sonnet-4  | 2          | 2d29757c | 152          | 3        |
| claude-sonnet-4  | 3          | fd778b2b | 115          | 5        |
| gpt-5            | 1          | 726ed2b0 | 66           | 8        |
| gpt-5            | 2          | 782d457a | 62           | 8        |
| gpt-5            | 3          | 58e032e0 | 60           | 8        |
| gpt-5            | 4          | 4582e291 | 58           | 8        |
| gpt-5            | 5          | 76a4aefc | 57           | 9        |
| gemini-2.5-flash | 1          | be22b153 | 44           | 6        |
| gemini-2.5-flash | 2          | 20de4b87 | 43           | 5        |
| gemini-2.5-flash | 3          | 1e439a24 | 40           | 6        |
| gemini-2.5-flash | 4          | 1a94792f | 40           | 6        |
| claude-sonnet-4  | 4          | 4048294e | 37           | 6        |
| claude-sonnet-4  | 5          | 1ee0b97d | 30           | 5        |
| gpt-oss-120b     | 1          | 08ed041e | 25           | 6        |
| gpt-oss-120b     | 2          | badf6979 | 23           | 6        |
| gpt-oss-120b     | 3          | 86529dae | 23           | 6        |
| gemini-2.5-flash | 5          | 0155ef6b | 23           | 5        |
| gpt-oss-120b     | 4          | 9e9c28fb | 22           | 6        |
| gpt-oss-120b     | 5          | d55dfcfc | 16           | 5        |

Defi benchmark

| Model            | Model Rank | Run ID   | Total Reward | Programs |
| ---------------- | ---------- | -------- | ------------ | -------- |
| claude-sonnet-4  | 1          | af0ca062 | 102          | 17       |
| gpt-5            | 1          | 554b09b3 | 34           | 17       |
| claude-sonnet-4  | 2          | 39e1e9ba | 34           | 6        |
| gpt-5            | 2          | 326454b3 | 33           | 18       |
| claude-sonnet-4  | 3          | 1ae19f9a | 33           | 13       |
| claude-sonnet-4  | 4          | c3d7f65d | 31           | 5        |
| gpt-5            | 3          | 7852b1a5 | 30           | 16       |
| gpt-5            | 4          | c1b6e31e | 29           | 14       |
| gpt-5            | 5          | e4655fc5 | 27           | 13       |
| gemini-2.5-flash | 1          | e31e18f6 | 25           | 3        |
| gpt-oss-120b     | 1          | d245d131 | 22           | 7        |
| claude-sonnet-4  | 5          | 92eb80c5 | 19           | 5        |
| gemini-2.5-flash | 2          | 88da4e59 | 19           | 3        |
| gpt-oss-120b     | 2          | 737ebeff | 17           | 4        |
| gpt-oss-120b     | 3          | f17db8ca | 10           | 4        |
| gpt-oss-120b     | 4          | 53e1275c | 9            | 4        |
| gpt-oss-120b     | 5          | eafda598 | 8            | 4        |
| gemini-2.5-flash | 3          | 0b61a27a | 7            | 3        |
| gemini-2.5-flash | 4          | fdb0864d | 0            | 0        |
| gemini-2.5-flash | 5          | acde932c | 0            | 0        |

**Key Observations:**

- Claude Sonnet 4's top run achieved 181 rewards, nearly 3x the best GPT-5 run
- The sparklines reveal distinct learning patterns: explosive growth (Claude) vs steady progress (GPT-5)
- Most models discover 5-8 unique programs, suggesting room for improvement in exploration diversity
- GPT-5 shows remarkable consistency with all runs between 57-66 rewards

====

# Ignore Below

=====

When using LLMs to power agentic applications on Solana, understanding limits of LLM understanding of Solana's runtime is crucial. Models need to deeply understand Solana's runtime and unique constraints when using MCP toolkits. To measure this capability, we propose Solana Bench as a way to measure how well LLMs understand the Solana runtime & how they can exploit it to their advantage. As a first attempt at constructing such a benchmark, we share the learnings of our failed previous benchmarks, and provide a path for community contributions.

# Benchmark Results

Solana Bench is a reinforcement-learning ready benchmark for measuring a LLM's ability to write code that produces sucessful Solana transactions.
LLMs are rewarded for every unique program instruction they execute in a successful transaction.

We reward LLMs this way to encourage maximum diversity of working knowledge of different Solana protocols.

We are excited to present this to the wider community to encourage further experiments with LLMs on Solana.
We believe that with minimal tweaks, protocols can put together their own benchmarks that show which LLMs are best
at developing against their Solana programs. Such tweaks will likely include: modifying the system prompt, adding their SDKs to the `bun` environment, and filtering rewards to only be awarded for interacting with their programs.

We were quite surprised to see how much better Claude Sonnet 4 is compared to every other model. We really wanted to see open
source models like `openai/gpt-oss-120b` perform better, so that we could fine-tune it to higher performance. I guess we were pleasantly surprised to see that Claude Sonnet 4 could learn to get better overall.

This benchmark resets LLM context between runs, so there is no "continual learning" happening. It's just qualitatively measuring
how different LLMs perform when asked to write Solana typescript code.

One note: we expected `qwen/qwen3-coder` to be bad because it is a Chinese model, and crypto is basically illegal in China, but so we were plesantly surprised to see how close it was to `google/gemini-2.5-flash` on performance. This gives us some hope that we could potentially train a model to get to similar performance as `google/gemini-2.5-flash`.

## Why We Built This

Evals are hard. Specifically, evaluating LLMs for their knowledge of Solana is really hard.
Creating a benchmark of general question & answer pairs is difficult to filter and maintain. Projects can change their implementation
without changing their documentation - the Solana Foundation is guilty of this sin too!
We were lucky to get the ability to try this out thanks to Lumo Lab's Fast DS Instruction dataset that they altruistically uploaded to HuggingFace for free.
It's a large corpus of 500,000 question & answer pairs generated by LLMs from protocol documentation across the Solana ecosystem.

Creating a benchmark out of using Solana is also difficult because options are split between 1) measuring LLM's ability to create Solana-related tool calls in a framework or 2) measuring profit and loss of an agent-created wallet over a discrete time period. It's really hard to do 1) well. We tried. We put together >80 benchmark tests in `solana-agent-kit`. The biggest issue is that not everyone will use the same framework! Solid AI startups had already built their own in-house tool sets & evals by the time we published the 80 benchmark suites. Then there is a suite of smaller issues with tool-call evaluations. These evaluations end up testing many features of tool calling models that are distinct:

- multi tool calling ability
- ability to interpet tool call errors
- ability to call tools with complex or nested argument structures (complex schema handling)
- ability to infer what a tool does given its description (nontrivial, especially with open source tooling where descriptions may not be great)
- ability to call multiple tools in a row to accomplish a given task

It's just very hairy, and with any code that's constantly seeing updates, these tests were brittle. But again, the biggest problem was that these evals weren't helping anyone, not even SendAI toolkit developers.

We did not even consider trying 2) because there's enough activity in crypto trading. If there was desire for an AI trading bot competition, we would have seen it. Given the hype wave in december 2024, and following dearth of interest, in crypto trading, we believe there is not any value in AI trading competitions. For a formal explanation: the constantly changing environment of the market conditions, gameability of low-liquidity trading pools, and nature of public competitions like this - make results too noisy to be trustworthy evaluations of anything. Let alone LLM understanding of market micro structure, trading strategies or Solana as a platform itself.

Then a godsend came along. Surfpool. Surfpool turns the local Solana test validator into an exact replica of Mainnet, without spending real funds. It does so by copying state from mainnet before executing transactions. So surfpool runs locally, acts just like Mainnet, but doesn't require actual Sol to be spent in testing. It was perfect for creating dynamic evaluations against real world scenarios.

So now we could do a trading competition - real world understanding of public markets could be tested in private, perfect! The issue is that there is no Jupiter Portfolio for surfpool. Without corresponding read infrastructure, this was basically DOA (dead on arrival). Even humans can't reasonably expect to remember the value of their positions, how could LLMs be expected to do so?

So what can we do? We need something simple to use to measure LLM performance on Solana. Well insight struck by reading old papers, as it usually does -- I suppose this is the point of putting out well written thoughts on the Internet. In 2023, Nvidia put out experiment showcasing GPT-4's ability to explore Minecraft, as measured by **curiosity**. Super fun paper, visually appealing, and the main inspiration for this experiment. Highly recommend reading here. They showed that GPT-4 could explore Minecraft surprisingly well by building up a library of code, and then invoking chosen subroutines to pick up/discover/craft new items. What mattered for us was a demonstration of how to evaluate LLMs in open world settings: code writing & curiosity scores.

For our curiosity score on Surfpool instance, we chose to reward the number of unique instructions executed. An instruction is defined as a tuple of (program id, first byte of instruction data or null). This is not perfect. It means we over-reward programs that don't take any instructions, like the Memo Program, and No-Op programs, of which there are a few. It also means we may under-reward Anchor programs that actually use a full 8-byte discriminator, since some of their instructions may share the same first byte of instruction data. Not saying it's perfect, but you know what, it's simple. Open to suggestions on how to improve this!

Now we just need a way to write code. Turns out this is quite non trivial. The solution we ended up with was code-action-loops, where the agent just writes code in markdown blocks of code, and we parse it out & execute it. Not every LLM can write code via tool call arguments (yes we tried that), but just about every LLM is able to write well formed code via markdown blocks.

Putting it together, Solana Bench is formed of a local Surfpool instance and a code-action loop. We use this to compare and contrast LLMs ability to write Solana code and exploit the nature of Solana's runtime to optimize their reward.

# Analyzing Results - What's worth knowing?

Anthropic's models are just head-and-shoulders above others. Claude-sonnet-4 outperforms every other model, but will also empty your LLM credits beyond belief.
Google's `gemini-2.5-flash` is best bang for buck, and fastest to execute of the lower models.

## Performance Analysis: How Models Learn to Explore

### Reward Progression Over Time

![Reward Progression](/assets/reward_progression.png)

The reward progression graph reveals how different models learn to navigate Solana over 50 messages. Notice Claude Sonnet 4's dominance - the red line soars to 60+ rewards with massive variance (the pink shaded area). This high variance is actually good - it shows the model is capable of breakthrough performances.

Gemini 2.5 Flash (blue) shows steady, consistent progress to ~27 rewards. OpenAI's GPT-OSS-120B and Qwen3 Coder plateau around 20 and 16 rewards respectively. The tight error bands for lower-performing models suggest they're consistently stuck, not occasionally breaking through.

### Individual Learning Trajectories

![Individual Trajectories](/assets/individual_trajectories.png)

Each line represents a single run's journey. The divergence points are fascinating - they show where models either breakthrough to discover new program interactions or get stuck in local optima.

Notice how successful runs share a pattern: gradual exploration for the first 10 messages, then explosive growth. Failed runs flatline early, suggesting the model couldn't recover from initial errors. The red dashed line (mean) shows the average path, but individual variance tells the real story.

### Program Discovery Patterns

![Program Discovery](/assets/program_discovery.png)

This visualization breaks down WHICH programs models discover and HOW they interact with them:

**Stacked Bar Chart (top-left)**: Shows total interactions per program. Token and Token-2022 programs dominate because they offer the most instruction variety. Models that discover Token-2022 extensions score significantly higher.

**Heatmap (top-right)**: Darker cells indicate more interactions. GPT-OSS-120B shows interesting behavior - it discovered the Stake program (which others missed) but failed to explore Token-2022 deeply.

**Diversity Chart (bottom-left)**: Unique programs discovered. More isn't always better - Qwen discovered only 3 programs but achieved decent rewards by deeply exploring each one.

**Distribution Pie (bottom-right)**: Overall program interaction distribution across all models. The "long tail" of rarely-discovered programs represents untapped reward potential.

### The Memo Problem: When Easy Rewards Mislead

Our analysis reveals a critical issue: the Memo program is inflating scores and masking true performance differences.

**Key Findings from Memo Impact Analysis:**

- **Qwen3 Coder**: 63.3% of interactions are with Memo program - heavily gaming the system
- **Claude Sonnet 4**: 24.1% Memo dependency, but achieves 62.4 average reward WITHOUT Memo (best overall)
- **Gemini 2.5 Flash**: 18.7% Memo usage, real performance of ~25 rewards
- **GPT-OSS-120B**: Only 9.6% Memo usage - most "honest" explorer

**Why This Matters:**

The Memo program is trivial - it just stores arbitrary text on-chain. Any model can spam Memo instructions for easy points. But real Solana understanding means:

- Discovering Token-2022 extensions (transfer fees, interest bearing, metadata)
- Finding specialized programs like Stake, Compute Budget, Associated Token Account
- Understanding program relationships and composability

**Claude Sonnet 4's Interesting Pattern:**

Despite being discontinued, Claude Sonnet 4 achieved the highest rewards (64.4 average) through smart exploration:

- Discovered Token-2022 early and exploited its many instruction types
- Found Associated Token Account program (ATokenGP...)
- Minimal reliance on Memo spam
- Most consistent performance across runs

This suggests Claude models have strong blockchain understanding "out of the box" - worth testing newer Claude versions.

### How Code Loop Explorer Works

The Code Loop Explorer (`code_loop_explorer.py`) is elegantly simple, operating in a tight feedback loop that mirrors how developers actually write code:

#### 1. **Initialization Phase**

The explorer starts by:

- Creating a fresh agent wallet with 10 SOL
- Connecting to Surfpool (sandboxed Solana validator) on localhost:8899
- Setting up LangChain with OpenRouter for LLM access
- Initializing metrics tracking for rewards and discoveries

```python
explorer = CodeLoopExplorer(
    model_name="google/gemini-2.5-flash",
    max_messages=50,  # Total iterations allowed
    verbose=True
)
```

#### 2. **The Core Loop**

For up to 50 messages (configurable), the explorer follows this pattern:

**Step A: System Prompt with Current State**

The model receives a detailed system prompt (319 lines!) that includes:

- Current SOL balance and block height
- Total rewards earned so far
- Available TypeScript dependencies (@solana/web3.js, @solana/spl-token, etc.)
- The EXACT function signature required: `export async function executeSkill(blockhash: string): Promise<string>`
- Examples of working code patterns
- Common pitfalls to avoid
- Strategy guidance: "Start with 2-3 safe instructions, then scale to 20+"

**Step B: Model Generates TypeScript Code**

The model responds with TypeScript in markdown blocks:

````markdown
```typescript
import {
  Transaction,
  SystemProgram,
  PublicKey,
  ComputeBudgetProgram,
} from "@solana/web3.js";

export async function executeSkill(blockhash: string): Promise<string> {
  const tx = new Transaction();
  const agentPubkey = new PublicKey(
    "EU2FLmBHBoSGLUidDeTo1RsfEy8G4fzPLMHVEzJNsTX9"
  );

  // Add compute budget for efficiency
  tx.add(ComputeBudgetProgram.setComputeUnitLimit({ units: 200000 }));

  // Add multiple diverse instructions for rewards
  for (let i = 0; i < 5; i++) {
    tx.add(
      SystemProgram.transfer({
        fromPubkey: agentPubkey,
        toPubkey: agentPubkey,
        lamports: 1000 + i,
      })
    );
  }

  // Add memo program interactions
  tx.add({
    keys: [],
    programId: new PublicKey("MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr"),
    data: Buffer.from("Exploring Solana", "utf-8"),
  });

  tx.recentBlockhash = blockhash;
  tx.feePayer = agentPubkey;

  return tx
    .serialize({
      requireAllSignatures: false,
      verifySignatures: false,
    })
    .toString("base64");
}
```
````

**Step C: Code Extraction (No Complex Parsing!)**

````python
# Simple regex - that's it!
code_pattern = re.compile(r"```(?:javascript|js|typescript|ts)(.*?)```", re.DOTALL)
code_blocks = code_pattern.findall(response.content)
````

**Step D: Execution via TypeScript Runtime**

The code is written to a temporary file and executed using Bun:

```python
# Write to file (unique per parallel run)
with open(self.code_file, "w") as f:
    f.write(skill_code)

# Execute via TypeScriptSkillManager
result = self.skill_manager.run_code_loop_code(
    skill_code,
    agent_pubkey,
    latest_blockhash,
    self.code_file  # Allows parallel execution
)
```

The Bun runtime (`runSkill.ts`) loads and executes the code:

```typescript
// Dynamically import and execute the skill
const { executeSkill } = await import(skillPath);
const serializedTx = await executeSkill(blockhash);
```

**Step E: Transaction Submission & Reward Calculation**

```python
# Decode the base64 transaction
tx_bytes = base64.b64decode(result['serialized_tx'])
tx = Transaction.from_bytes(tx_bytes)

# Sign with agent keypair
signed_tx = env._partial_sign_transaction(bytes(tx), [env.agent_keypair])

# Submit to Surfpool
obs, reward, _, _, info = await env.step(signed_tx)

# Reward = number of unique (program_id, instruction_discriminator) pairs
# Each new discovery = +1 point
```

**Step F: Feedback to Model**

The model receives immediate feedback:

```python
if reward > 0:
    feedback = f"""✅ Transaction executed successfully!
    Earned {reward} reward points.
    Total rewards: {env.total_reward}
    [Message {count}/{max}] - {remaining} messages remaining
    Info: {info}"""
else:
    feedback = f"""❌ Transaction failed: {info.get('error')}
    [Message {count}/{max}] - {remaining} messages remaining"""

# Add feedback to conversation
messages.append(HumanMessage(content=feedback))
```

#### 3. **Metrics & Tracking**

Every run generates detailed metrics in JSON:

```json
{
  "model": "google/gemini-2.5-flash",
  "messages": [...],
  "cumulative_rewards": [0, 2, 2, 5, 8, 11, 14, 19, ...],
  "programs_discovered": {
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": 15,
    "11111111111111111111111111111111": 8,
    "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr": 12,
    "ComputeBudget111111111111111111111111111111": 5
  },
  "code_blocks_extracted": [...],
  "errors": [...]
}
```

### The Key Innovation: Simplicity

What makes Code Loop Explorer special is what it DOESN'T have:

- **No tool calling interface** - Models write code naturally in markdown
- **No skill library** - Each iteration starts fresh (no retrieval confusion)
- **No multi-agent coordination** - Single loop, single focus
- **No AST parsing** - Simple regex extraction that never fails
- **No predetermined tasks** - Pure exploration driven by curiosity

The entire core loop is just 150 lines of Python. The magic is in letting models write code exactly as they were trained to - in markdown code blocks with immediate execution feedback.

## The Journey: Why Traditional Evals Failed Us

Before Solana Gym, we tried everything to evaluate LLMs on blockchain knowledge. Every approach hit fundamental roadblocks.

### 📊 Attempt 1: Tool Call Evaluations

We started by building unit tests for SendAI (solana-agent-kit) tool usage with GPT-4o-mini as the judge. The idea was simple: test if models could correctly use tools like `transfer_sol`, `swap_tokens`, `stake_sol`.

**Why It Failed Spectacularly**:

- **Hypersensitivity to Implementation**: Change a parameter name from `amount` to `lamports`? Every eval breaks.
- **No Ground Truth**: Tools like `jupiter_swap` build entire transactions internally. They only work on mainnet. How do you know if the swap would succeed without spending real money?
- **SDK Lock-in**: We were testing knowledge of ONE SDK's abstraction layer, not Solana itself
- **The Mainnet Problem**: Without Surfpool (which didn't exist yet), we were SOL - Shit Out of Luck

**Real Example**:

```python
# This "passes" the eval but would fail on chain:
model_calls_tool("jupiter_swap", {
    "from_token": "SOL",
    "to_token": "USDC",
    "amount": 1.5,  # Is this SOL or lamports? Who knows!
    "slippage": 100  # Is this basis points or percent? SDK-dependent!
})
```

### 📚 Attempt 2: Q&A Knowledge Evals

Next, we looked at Q&A datasets (shoutout Lumo Labs for their dataset). Test models on questions generated from ground-truth documentation.

**Why It Also Failed**:

- **Subjective Scoring**: Is "A PDA is a program-derived address" better or worse than "PDAs let programs own accounts"? Both are correct!
- **Hallucination vs Creativity**: Models would give technically correct but overly creative answers
- **No Practical Signal**: A model could ace every question but fail to write a single working transaction

**Example Frustration**:

```
Q: "How do you create a token account?"
Model A: "Use createAssociatedTokenAccountInstruction"  ✓
Model B: "Call getOrCreateAssociatedTokenAccount"      ✓
Model C: "First derive the ATA address, then..."        ✓
All correct! Which is "better"? 🤷
```

### 💡 The Breakthrough: Surfpool + Voyager

When Surfpool launched (Q2 2024), everything changed. Finally, a sandboxed Solana that behaves like mainnet! But we still didn't know how to evaluate in this open world.

Then we found Voyager. The paper's key insight: **reward curiosity itself**. Don't test specific knowledge - test the ability to explore and discover.

**The Eureka Moment**:

- Every unique (program_id, instruction_discriminator) = 1 point
- No predetermined "correct" answers
- Models that understand Solana deeply will naturally discover more
- The blockchain becomes the judge

## Why This Matters for Blockchain Evaluation

### 1. **Action Over Analysis**

Instead of asking "Can you explain DeFi?", we ask "Can you interact with DeFi protocols?" The difference is profound. Models must understand:

- Transaction composition and signing
- Account relationships and PDAs
- Instruction data encoding
- Program interaction patterns

### 2. **Universal, Not SDK-Specific**

We're not testing if models know `solana-agent-kit` or `@coral-xyz/anchor`. We're testing if they understand Solana itself. Any SDK, any approach, any creative solution - if it works on chain, it scores.

### 3. **Immediate, Objective Feedback**

Every transaction either succeeds or fails. Every new instruction discovered adds to the score. There's no ambiguity in evaluation - the blockchain is the judge.

## What Didn't Work (And Why That's Important)

### ❌ Tool Calling in Simple Explorer

**The Problem**: We built `simple_explorer.py` using OpenAI's function calling paradigm, where the model would invoke tools like:

```python
tools = [
    {"name": "executeSkill", "parameters": {"skill_name": "..."}},
    {"name": "writeSkillAndExecute", "parameters": {"skill_name": "...", "skill_code": "..."}},
    {"name": "fetchTransactions", "parameters": {"program_id": "..."}},
    {"name": "getObservation", "parameters": {}},
    {"name": "getProgramIdl", "parameters": {"program_id": "..."}}
]
```

**Why It Failed**:

- **Variable Name Errors**: When generating code as a JSON parameter, models constantly made typos - `agent_pubkey` became `agentPubkey`, `blockhash` became `blockHash`, etc. This NEVER happens in markdown code blocks!
- **String Escaping Hell**: Code in JSON parameters needed escaped quotes, escaped newlines - models would forget, break the JSON, and couldn't debug it
- **Lost TypeScript Errors**: When code failed, models saw generic tool errors instead of the actual TypeScript compiler output
- **Fighting the Natural Interface**: Models are already trained to write code in markdown code blocks!

**Real Example of What Happened**:

```json
// Model would generate this as a tool call:
{
  "name": "writeSkillAndExecute",
  "parameters": {
    "skill_name": "transfer_sol",
    "skill_code": "export async function executeSkill(blockhash: string): Promise<string> {\n  const tx = new Transaction();\n  const agentPubKey = new PublicKey('...');  // WRONG: agentPubKey vs agentPubkey\n  tx.add(SystemProgram.transfer({\n    fromPubkey: agentPubKey,  // WRONG: mixed casing\n    toPubkey: agentPubKey,\n    lamports: 100000\n  }));\n  tx.recentBlockHash = blockhash;  // WRONG: recentBlockHash vs recentBlockhash\n  return tx.serialize({requireAllSignatures: false}).toString(\"base64\");  // WRONG: unescaped quotes\n}"
  }
}
```

Every single tool call had these issues. But when the same model writes in a code block? Perfect every time:

```typescript
export async function executeSkill(blockhash: string): Promise<string> {
  const tx = new Transaction();
  const agentPubkey = new PublicKey("..."); // Correct!
  tx.add(
    SystemProgram.transfer({
      fromPubkey: agentPubkey, // Consistent!
      toPubkey: agentPubkey,
      lamports: 100000,
    })
  );
  tx.recentBlockhash = blockhash; // Correct property name!
  return tx.serialize({ requireAllSignatures: false }).toString("base64"); // No escaping needed!
}
```

**The Breakthrough Realization**: LLMs already know how to write code! They do it millions of times in training data using ```typescript blocks. Why force them through a different interface?

### ❌ Voyager-Style Skill Library and Code Reuse

**The Problem**: The original Voyager paper achieved great results by building a library of reusable skills in Minecraft. We implemented the same approach with TypeScript skills for Solana:

```typescript
// Skill: "transfer_sol"
async function transferSol(from: PublicKey, to: PublicKey, amount: number) {
    // ... implementation
}

// Later: "complex_defi_operation"
async function complexDefiOp() {
    await transferSol(...);  // Reuse previous skill
    await swapTokens(...);   // Reuse another skill
}
```

**Why It Failed for Blockchain**:

- **Transaction Atomicity**: Each Solana transaction needs ALL instructions in a single Transaction object. You can't compose by calling separate functions sequentially
- **Signature Requirements**: Every transaction needs specific signers. Reusable functions with hardcoded signers don't work
- **Context Dependency**: Each transaction depends heavily on current state (blockhash, account balances, program states)
- **No Real Skill Hierarchy**: Unlike Minecraft where "chop wood" → "craft planks" → "build house", Solana transactions are unique compositions

**What Actually Happened**:

```typescript
// Models kept generating this (WRONG):
await executeSkill1();
await executeSkill2(); // Separate transactions - not what we want!

// Instead of this (RIGHT):
const tx = new Transaction();
tx.add(instruction1, instruction2, instruction3); // All in one transaction
```

**RAG Retrieval Was Useless**:

- Retrieved "similar" skills that had completely different account structures
- Transaction patterns don't generalize well across different protocols
- Models spent more time trying to adapt retrieved code than writing fresh code

### ❌ Multi-Agent Architecture Complexity

**The Problem**: We faithfully implemented Voyager's multi-agent system:

- **Action Agent**: Generates code based on current state
- **Curriculum Agent**: Decides what task to pursue next
- **Critic Agent**: Evaluates if tasks were completed successfully
- **Skill Manager**: Stores and retrieves skills

**Why It Failed**:

- **Context Window Explosion**: Each agent needed full history, tool definitions, examples
- **Agent Coordination Overhead**: Agents waiting for each other, parsing each other's outputs
- **Debugging Impossibility**: Models couldn't see the full flow of what was happening
- **Lost in Translation**: Each agent interaction was another opportunity for misunderstanding

**Specific Failure Mode**:

```python
# Curriculum says: "Explore Token-2022 program"
# Action generates: Code for regular Token program
# Critic evaluates: "Success! Interacted with token program"
# Result: Misaligned objectives, no learning
```

### ❌ Complex AST Parsing with Babel

**The Problem**: In `action.py`, we used Babel to parse JavaScript/TypeScript from AI responses:

```python
babel_generator = import_module("@babel/generator")
parsed = babel.parse(code_string)
# Extract function node, validate structure, extract body...
```

**Why It Failed**:

- **Fragile Parsing**: Slight variations in generated code would crash everything
- **Incomprehensible Errors**: "TypeError: this.m[ffid] is not a function" - how is a model supposed to debug this?
- **Context Waste**: Error messages about AST nodes instead of actual code issues
- **Platform Hell**: Node.js/Babel version mismatches across environments

**Real Example That Broke Everything**:

```javascript
// Model generated this (note the comment):
export async function executeSkill(
    blockhash: string  // the blockhash parameter
): Promise<string> {
```

Parser exploded because of the inline comment. Model's response? Generate the same code again because it looked correct (it was!).

### 🎯 The Ultimate Lesson: Get Out of the Way

After all these failed attempts, we realized the fundamental truth:

**LLMs already know how to write code in a natural way - using markdown code blocks.**

```typescript
// This is how models write code in ChatGPT, Claude, GitHub Copilot, everywhere!
```

Why did we think we needed anything else?

The **Code Loop Explorer** succeeds because it:

1. Lets models write code exactly as they do in their training data
2. Extracts it with a simple regex: ` ```typescript(.*?)``` `
3. Executes it immediately
4. Returns clear success/failure feedback
5. Repeat

**No tools. No agents. No parsers. No abstractions.**

Just code → execution → feedback. The same loop developers use every day.

The best interface for getting code from LLMs isn't an interface at all - it's getting out of their way and letting them write code the way they already know how.

## Surprising Discoveries

### 🎯 Model Performance Varies Wildly

- **Gemini 2.5 Flash**: King of exploration, consistently high rewards
- **Qwen3 Coder**: Struggles with code loops but great at following examples
- **Grok 3 Mini**: Surprisingly effective despite being a smaller model
- **GPT-4o-mini**: Reliable but conservative in exploration

### 🎯 Starting Simple Beats Starting Complex

Models that begin with 2-3 known-working instructions and gradually scale up to 20+ instructions per transaction consistently outperform those that try complex interactions immediately.

### 🎯 Error Messages Are Teaching Moments

The immediate feedback from failed transactions teaches models faster than any prompt engineering. They quickly learn:

- Don't duplicate ComputeBudgetProgram instructions
- Always sign with new Keypairs
- Token-2022 has more instruction variety than Token

## Future Directions

### 🚀 Fine-Tuning on Successful Trajectories

We're collecting thousands of successful transaction trajectories. Imagine fine-tuning models specifically on:

- High-reward exploration paths
- Protocol-specific interaction patterns
- Error recovery strategies

### 🚀 MCP (Model Context Protocol) Integration

Integrating with Anthropic's MCP to provide:

- Real-time blockchain state as context
- Direct transaction submission tools
- Protocol documentation access

## The Bigger Picture: Solving AI Usage of Solana

The current state of AI-Solana integration is fragmented and brittle. The ecosystem of MCP (Model Context Protocol) servers and SDK wrappers is growing rapidly but lacks cohesion:

### The MCP Fragmentation Problem

**What's Happening Now**:

- Every protocol creates their own MCP server with custom tools
- Each SDK has different abstractions and naming conventions
- Models trained on one tool fail when using another
- Breaking changes in any layer cascade through the entire stack

### Our Thesis: Models Will Build Their Own Tools

We believe the long-term solution isn't better MCP servers - it's teaching models to:

1. **Write their own transaction builders** from first principles
2. **Discover SDK patterns** through exploration and documentation
3. **Adapt to new protocols** without explicit tool definitions
4. **Self-correct** when APIs change or tools break

This is why Code Loop Explorer matters. It's not just an eval - it's a training ground for models to learn the fundamental skill of blockchain interaction.

### The Generalizable Evaluation Framework

What we're building isn't protocol-specific or SDK-specific. It's a framework that:

**Measures Core Competencies**:

- Can the model construct valid transactions?
- Does it understand account relationships?
- Can it discover new programs through exploration?
- Does it learn from transaction errors?

**Adapts to Any Environment**:

- Works with raw @solana/web3.js or any SDK
- Evaluates both tool usage AND direct code generation
- Rewards understanding, not memorization

**Scales with Model Capabilities**:

- Today: Models write TypeScript using web3.js
- Tomorrow: Models generate Rust programs
- Future: Models design their own protocols

### Why This Approach Will Win

**1. Antifragility**: When MCP servers break or SDKs change, models that can write code adapt immediately.

**2. Generalization**: A model that understands Solana at the transaction level can use ANY SDK or tool.

**3. Innovation**: Models aren't limited by predefined tools - they can discover novel interaction patterns.

**4. Verification**: Code generation is auditable. You can see exactly what the model is doing.

### The Path Forward

We're not trying to replace MCP servers or SDKs. We're building the evaluation framework that will:

1. **Identify which models truly understand blockchain mechanics**
2. **Generate training data for next-generation blockchain-native models**
3. **Create benchmarks that matter for real-world usage**
4. **Enable protocol teams to evaluate AI readiness for their systems**

The future isn't models calling `swap_tokens()`. It's models that understand what a swap IS and can implement it from scratch when needed.

## Acknowledgments

This project builds on the incredible work of:

- NVIDIA's Voyager team for the foundational paper
- The Surfpool team for the sandboxed Solana environment
- LangGraph for providing invaluable debugging visibility
- The Solana Foundation for ecosystem support
- All the protocol teams whose SDKs make this possible

---

_Solana Bench is open source and MIT licensed. We believe the future of blockchain AI evaluation should be built in the open._

**Ready to contribute?** Start with our [Code Loop Explorer example](./code_loop_explorer.py) and build your own protocol-specific environment. The future of blockchain AI evaluation is in your hands.

---

_The best way to test if a model truly understands blockchain isn't through tool calling - it's whether they can build the tools themselves._
