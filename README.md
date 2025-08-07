# Voyager: Autonomous Solana Exploration

> **An implementation of the NVIDIA Voyager paper adapted for Solana blockchain exploration, where AI agents learn to autonomously discover and interact with DeFi protocols through self-generated TypeScript skills.**

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