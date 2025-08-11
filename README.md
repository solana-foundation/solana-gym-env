# Solana Bench

> **Benchmarking AI's Understanding of Blockchain - An evaluation framework that measures how well AI models understand and interact with the Solana blockchain through direct code generation and protocol discovery.**

## 🚀 Latest: Code Loop Explorer (Best Performance)

The **Code Loop Explorer** is our newest and highest-performing experiment. It uses a streamlined architecture where the LLM directly generates TypeScript code blocks in response, eliminating complex parsing and achieving superior results.

### Quick Start - Code Loop Explorer

```bash
# Run a single exploration session
export MODEL_NAME="google/gemini-2.5-flash"  # or "openai/gpt-4o-mini", "openai/gpt-oss-120b", etc.
export MAX_MESSAGES=50
uv run python code_loop_explorer.py

# Run model comparison batch (recommended)
uv run python run_model_comparison_batch.py

# Analyze results with advanced visualizations
uv run python analyze_code_loop_performance.py
```

### Key Achievements

- **34 unique instruction rewards** in a single run (Gemini 2.5 Flash)
- **60% success rate** for transaction execution (best run)
- **Simplified architecture**: Direct code generation without complex parsing
- **Statistical analysis**: Error bars, violin plots, and trajectory visualizations

## Overview

This project adapts the groundbreaking [Voyager paper](https://voyager.minedojo.org/) from Minecraft to the Solana blockchain. Instead of exploring a 3D world, our agents explore the DeFi ecosystem, discovering new protocols and building a library of reusable skills.

### Key Features

- **Self-Learning**: Agents generate their own TypeScript code to interact with Solana
- **Skill Library**: Accumulated knowledge persists across episodes
- **Protocol Discovery**: Rewards for finding new program instructions
- **Safe Environment**: Runs against local Solana test validator (surfpool)
- **Model Comparison**: Built-in tools for comparing different LLMs
- **Advanced Analytics**: Comprehensive visualization with error bands and distributions

## Architecture Evolution

### Current Best: Code Loop Explorer

```
┌─────────────────────────────────────────┐
│         Code Loop Explorer              │
├─────────────────────────────────────────┤
│  • Direct TypeScript code extraction    │
│  • No complex parsing or AST analysis   │
│  • Immediate execution feedback         │
│  • Streamlined message flow             │
└────────────────┬───────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      TypeScript Skill Runner (Bun)      │
├─────────────────────────────────────────┤
│  • Executes generated TypeScript code   │
│  • Returns serialized transactions      │
│  • Single transaction per skill         │
└────────────────┬───────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│    Surfpool (Local Solana Validator)    │
├─────────────────────────────────────────┤
│  • Mainnet fork with real programs      │
│  • Safe sandbox environment             │
│  • Instant transaction feedback         │
└─────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.8+ with [uv](https://github.com/astral-sh/uv)
- [Bun](https://bun.sh) v1.1.42+
- [Surfpool](https://github.com/novy4/surfpool) (Solana test environment)
- OpenRouter API key for LLM access

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd voyager

# Install Python dependencies
uv sync

# Install TypeScript dependencies
cd voyager/skill_runner && bun install
cd ../..

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

## Running Experiments

### 1. Code Loop Explorer (Recommended)

The Code Loop Explorer is the latest and most effective approach:

```bash
# Single run with specific model
export MODEL_NAME="google/gemini-2.5-flash"
export MAX_MESSAGES=50
uv run python code_loop_explorer.py

# Batch comparison of multiple models
uv run python run_model_comparison_batch.py
```

### 2. Simple Explorer

A simplified version using OpenAI function calling:

```bash
uv run python simple_explorer.py
```

### 3. Original Voyager (Legacy)

The full multi-agent system from the original paper:

```bash
uv run python voyager/voyager_clone.py
```

## Model Comparison & Analysis

### Running Comparisons

```bash
# Run batch comparison (4 models, 3 runs each, 50 messages)
uv run python run_model_comparison_batch.py

# Analyze results with comprehensive visualizations
uv run python analyze_code_loop_performance.py
```

### Analysis Features

The analysis script generates:

- **Reward progression with error bands**: Shows mean performance with confidence intervals
- **Individual trajectory plots**: Visualizes each run's path
- **Bar charts with error bars**: Statistical comparison across models
- **Violin plots**: Full distribution of performance metrics
- **Correlation heatmaps**: Relationships between different metrics

### Top Performing Models (Based on Testing)

1. **Google Gemini 2.5 Flash**: Highest peak performance (34 rewards)
2. **Qwen3 Coder**: Most consistent performance
3. **OpenAI GPT-4o-mini**: Good balance of speed and performance
4. **GPT-OSS-120b**: Reliable but slower

## Key Improvements in Code Loop Explorer

1. **Direct Code Extraction**: Uses regex to extract TypeScript blocks directly from LLM responses
2. **No AST Parsing**: Eliminates complex Babel parsing that was causing errors
3. **Immediate Feedback**: Each code execution gets instant reward feedback
4. **Better Prompting**: Clear examples and error prevention guidelines
5. **Statistical Analysis**: Built-in tools for comparing model performance

## Project Structure

```
voyager/
├── code_loop_explorer.py      # Latest and best performing experiment
├── simple_explorer.py          # OpenAI function calling version
├── voyager_env.py             # Gymnasium environment wrapper
├── surfpool_env.py            # Low-level Solana interaction
├── voyager/
│   ├── agents/                # Multi-agent components
│   ├── skill_manager/         # TypeScript skill management
│   ├── skill_runner/          # Bun execution environment
│   └── prompts/               # System prompts for agents
├── analyze_code_loop_performance.py  # Advanced visualization
├── run_model_comparison_batch.py     # Batch testing script
└── metrics/                   # Performance data and results
```

## Reward System

Agents earn rewards by discovering unique (program_id, instruction_discriminator) pairs:

- **+1 reward** per unique instruction discovered
- **0 reward** for failed transactions
- **0 reward** for duplicate discoveries

Common discoveries include:

- System Program: Transfer, CreateAccount, Allocate
- Token Programs: InitializeMint, Transfer, MintTo
- DeFi Protocols: Swap, AddLiquidity, Stake

## Metrics & Monitoring

### Real-time Progress

```bash
# View live progress during exploration
python view_progress.py
```

### Post-run Analysis

```bash
# Generate comprehensive performance reports
uv run python analyze_code_loop_performance.py
```

### Metrics Tracked

- Total rewards earned
- Success rate per model
- Programs discovered
- Error frequency
- Reward efficiency (reward per message)

## Tips for Best Results

1. **Start Simple**: Begin with 10-20 messages to test setup
2. **Model Selection**: Gemini 2.5 Flash shows best peak performance
3. **Batch Size**: 3-5 runs per model for statistical significance
4. **Message Count**: 50 messages provides good exploration depth
5. **Analysis**: Always run analysis script after experiments

## Environment Variables

```bash
# Required
OPENROUTER_API_KEY=your_key_here

# Optional (for specific models)
OPENAI_API_KEY=your_key_here        # For GPT-4o-mini
ANTHROPIC_API_KEY=your_key_here     # For Claude models

# Experiment Configuration
MODEL_NAME=google/gemini-2.5-flash  # Model to use
MAX_MESSAGES=50                      # Messages per run
```

## Troubleshooting

### Surfpool Issues

```bash
# Check if surfpool is installed
which surfpool

# Test surfpool with custom port
surfpool start -u https://api.mainnet-beta.solana.com -p 8901 --no-tui
```

### Bun/TypeScript Issues

```bash
# Ensure you're in the skill_runner directory
cd voyager/skill_runner
bun install
bun test
```

### Model API Issues

- Verify API keys are set correctly
- Check rate limits for your model
- Consider using free tier models for testing

## Contributing

Contributions are welcome! Areas of interest:

- New exploration strategies
- Additional model integrations
- Enhanced reward mechanisms
- Protocol-specific exploration

## Running the Benchmark

It costs about $75 USD to run all the models in this benchmark at once.
The costs primarily come from `anthropic/claude-sonnet-4`. It is nearly 10x
more expensive than `google/gemini-2.5-flash` which is the next most performant
model we measured on this benchmark.

Running the main script will run all the models at once against a `surfpool` instance.
You must have `surfpool start` running in a different terminal.

```bash
$ USE_EXTERNAL_SURFPOOL=true uv run run_model_comparison_batch.py
============================================================
CODE LOOP MODEL COMPARISON BATCH (PARALLEL)
============================================================
Models to test: 4
  - google/gemini-2.5-flash
  - openai/gpt-oss-120b
  - anthropic/claude-sonnet-4
  - qwen/qwen3-coder
Runs per model: 5
Messages per run: 50
Total experiments: 20
Parallel batch size: 20

⏱️  Time Estimates:
  Sequential: ~240 minutes
  Parallel: ~12 minutes
  Speedup: ~20.0x

✅ Using EXTERNAL surfpool instance on localhost:8899
============================================================

Proceed with parallel execution? (y/n): y

🚀 Starting 20 experiments in batches of 20

📦 Batch 1/1 (20 experiments)
──────────────────────────────────────────────────
  🚀 Starting google/gemini-2.5-flash run 0 (file: batch_google_gemini_2.5_flash_0_164011.ts)
  🚀 Starting google/gemini-2.5-flash run 1 (file: batch_google_gemini_2.5_flash_1_164011.ts)
  🚀 Starting google/gemini-2.5-flash run 2 (file: batch_google_gemini_2.5_flash_2_164011.ts)
  🚀 Starting google/gemini-2.5-flash run 3 (file: batch_google_gemini_2.5_flash_3_164011.ts)
  🚀 Starting google/gemini-2.5-flash run 4 (file: batch_google_gemini_2.5_flash_4_164011.ts)
  🚀 Starting openai/gpt-oss-120b run 0 (file: batch_openai_gpt_oss_120b_0_164011.ts)
  🚀 Starting openai/gpt-oss-120b run 1 (file: batch_openai_gpt_oss_120b_1_164011.ts)
  🚀 Starting openai/gpt-oss-120b run 2 (file: batch_openai_gpt_oss_120b_2_164011.ts)
  🚀 Starting openai/gpt-oss-120b run 3 (file: batch_openai_gpt_oss_120b_3_164011.ts)
  🚀 Starting openai/gpt-oss-120b run 4 (file: batch_openai_gpt_oss_120b_4_164011.ts)
  🚀 Starting anthropic/claude-sonnet-4 run 0 (file: batch_anthropic_claude_sonnet_4_0_164011.ts)
  🚀 Starting anthropic/claude-sonnet-4 run 1 (file: batch_anthropic_claude_sonnet_4_1_164011.ts)
  🚀 Starting anthropic/claude-sonnet-4 run 2 (file: batch_anthropic_claude_sonnet_4_2_164011.ts)
  🚀 Starting anthropic/claude-sonnet-4 run 3 (file: batch_anthropic_claude_sonnet_4_3_164011.ts)
  🚀 Starting anthropic/claude-sonnet-4 run 4 (file: batch_anthropic_claude_sonnet_4_4_164011.ts)
  🚀 Starting qwen/qwen3-coder run 0 (file: batch_qwen_qwen3_coder_0_164011.ts)
  🚀 Starting qwen/qwen3-coder run 1 (file: batch_qwen_qwen3_coder_1_164011.ts)
  🚀 Starting qwen/qwen3-coder run 2 (file: batch_qwen_qwen3_coder_2_164011.ts)
  🚀 Starting qwen/qwen3-coder run 3 (file: batch_qwen_qwen3_coder_3_164011.ts)
  🚀 Starting qwen/qwen3-coder run 4 (file: batch_qwen_qwen3_coder_4_164011.ts)
  ✅ google/gemini-2.5-flash run 4 completed
  ✅ google/gemini-2.5-flash run 2 completed
  ✅ qwen/qwen3-coder run 3 completed
  ✅ qwen/qwen3-coder run 2 completed
  ✅ qwen/qwen3-coder run 4 completed
  ✅ google/gemini-2.5-flash run 3 completed
  ✅ google/gemini-2.5-flash run 0 completed
  ✅ google/gemini-2.5-flash run 1 completed
  ✅ qwen/qwen3-coder run 0 completed
  ✅ qwen/qwen3-coder run 1 completed
  ✅ anthropic/claude-sonnet-4 run 2 completed
  ✅ openai/gpt-oss-120b run 1 completed
  ✅ openai/gpt-oss-120b run 3 completed
  ✅ openai/gpt-oss-120b run 2 completed
  ✅ openai/gpt-oss-120b run 4 completed
  ✅ openai/gpt-oss-120b run 0 completed
  ✅ anthropic/claude-sonnet-4 run 3 completed
  ✅ anthropic/claude-sonnet-4 run 0 completed
  ✅ anthropic/claude-sonnet-4 run 1 completed
  ✅ anthropic/claude-sonnet-4 run 4 completed
  ⏱️  Batch completed in 1072.0 seconds
============================================================
Total experiments: 20
Successful: 20/20
Failed: 0

⏱️  Performance:
  Total time: 1072.0 seconds (17.9 minutes)
  Average per experiment: 53.6 seconds
  Effective speedup: ~13.4x

📊 Results by Model:
  google/gemini-2.5-flash: 5/5 successful
  openai/gpt-oss-120b: 5/5 successful
  anthropic/claude-sonnet-4: 5/5 successful
  qwen/qwen3-coder: 5/5 successful

📈 To analyze results, run:
  uv run python analyze_code_loop_performance.py
============================================================
```

You can then generate all the graphs with

```bash
$ uv run analyze_code_loop_performance.py
warning: `VIRTUAL_ENV=/Users/noahgundotra/gemini/solana-gym/solana-gym/.venv` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead
============================================================
CODE LOOP EXPLORER ANALYSIS
============================================================

📁 Created output directory: analysis_results/code_loop_20250808_170341

📂 Loading code_loop metrics...
✅ Found 20 code_loop runs to analyze

============================================================
PROGRAMS DISCOVERED BY MODEL
============================================================

📊 anthropic/claude-sonnet-4:
   Total unique programs: 6
   - Token 2022                     (TokenzQd...): 35 interactions
   - Token Program                  (Tokenkeg...): 32 interactions
   - Associated Token Account       (ATokenGP...): 32 interactions
   - Memo Program                   (MemoSq4g...): 11 interactions
   - System Program                 (11111111...): 5 interactions
   - Compute Budget                 (ComputeB...): 5 interactions

📊 google/gemini-2.5-flash:
   Total unique programs: 7
   - Compute Budget                 (ComputeB...): 58 interactions
   - Unknown Program                (Vote1111...): 46 interactions
   - Token Program                  (Tokenkeg...): 38 interactions
   - Token 2022                     (TokenzQd...): 36 interactions
   - Associated Token Account       (ATokenGP...): 25 interactions
   - Memo Program                   (MemoSq4g...): 23 interactions
   - System Program                 (11111111...): 19 interactions

📊 openai/gpt-oss-120b:
   Total unique programs: 7
   - Associated Token Account       (ATokenGP...): 55 interactions
   - Stake Program                  (Stake111...): 49 interactions
   - Token 2022                     (TokenzQd...): 43 interactions
   - Token Program                  (Tokenkeg...): 28 interactions
   - System Program                 (11111111...): 15 interactions
   - Memo Program                   (MemoSq4g...): 15 interactions
   - Compute Budget                 (ComputeB...): 15 interactions

📊 qwen/qwen3-coder:
   Total unique programs: 5
   - Memo Program                   (MemoSq4g...): 87 interactions
   - Compute Budget                 (ComputeB...): 9 interactions
   - System Program                 (11111111...): 9 interactions
   - Associated Token Account       (ATokenGP...): 4 interactions
   - Token Program                  (Tokenkeg...): 4 interactions
📊 Program discovery plots saved to: analysis_results/code_loop_20250808_170341/program_discovery.png

============================================================
CODE LOOP PERFORMANCE SUMMARY
============================================================

By Model:
                          total_reward             success_rate      programs_discovered     unique_instructions
                                  mean    std  max         mean  std                mean max                mean max
model
anthropic/claude-sonnet-4         72.2  51.26  139          0.0  0.0                 5.0   6                 0.0   0
google/gemini-2.5-flash           29.4  16.99   42          0.0  0.0                 5.0   7                 0.0   0
openai/gpt-oss-120b               18.4   6.07   26          0.0  0.0                 5.8   7                 0.0   0
qwen/qwen3-coder                  13.6   3.05   17          0.0  0.0                 3.4   5                 0.0   0

🏆 Top 5 Runs by Total Reward:
                    model                             run_id  total_reward  programs_discovered
anthropic/claude-sonnet-4 code_loop_25-08-08_164012_9138bbf9           139                    5
anthropic/claude-sonnet-4 code_loop_25-08-08_164012_93f08ce9           110                    4
anthropic/claude-sonnet-4 code_loop_25-08-08_164012_2b5128e5            56                    6
anthropic/claude-sonnet-4 code_loop_25-08-08_164012_264a312e            43                    6
  google/gemini-2.5-flash code_loop_25-08-08_164012_f60de86f            42                    6

✅ Top 5 Runs by Success Rate:
                    model                             run_id  success_rate  total_reward
anthropic/claude-sonnet-4 code_loop_25-08-08_164012_9138bbf9             0           139
anthropic/claude-sonnet-4 code_loop_25-08-08_164012_93f08ce9             0           110
anthropic/claude-sonnet-4 code_loop_25-08-08_164012_2b5128e5             0            56
anthropic/claude-sonnet-4 code_loop_25-08-08_164012_264a312e             0            43
  google/gemini-2.5-flash code_loop_25-08-08_164012_f60de86f             0            42

💾 Summary statistics saved to: analysis_results/code_loop_20250808_170341/summary_statistics.csv

📊 Creating visualizations...
📊 Performance plots saved to: analysis_results/code_loop_20250808_170341/performance_overview.png
📊 Error bar plots saved to: analysis_results/code_loop_20250808_170341/error_bars.png
📊 Reward progression plot saved to: analysis_results/code_loop_20250808_170341/reward_progression.png
📊 Individual trajectories plot saved to: analysis_results/code_loop_20250808_170341/individual_trajectories.png

✅ Analysis complete! All results saved to: analysis_results/code_loop_20250808_170341
📁 analysis_results/code_loop_20250808_170341/
   ├── summary_statistics.csv
   ├── program_discovery.png
   ├── performance_overview.png
   ├── error_bars.png
   ├── reward_progression.png
   └── individual_trajectories.png
```

## Citation

If you use this code in your research, please cite:

```bibtex
@article{voyager2023,
  title={Voyager: An Open-Ended Embodied Agent with Large Language Models},
  author={Wang, Guanzhi and Xie, Yuqi and Jiang, Yunfan and others},
  journal={arXiv preprint arXiv:2305.16291},
  year={2023}
}
```

## License

MIT License - See LICENSE file for details

## Acknowledgments

- NVIDIA MineDojo team for the original Voyager paper
- Solana Foundation for blockchain infrastructure
- OpenRouter for unified LLM access
- The Surfpool team for the testing environment
