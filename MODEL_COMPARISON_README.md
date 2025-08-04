# Model Performance Comparison for Simple Explorer

This feature enables comprehensive performance tracking and comparison of different models running the Simple Explorer agent.

## Features

- **Detailed Metrics Tracking**: Records rewards, programs discovered, instructions executed, skills created, and errors for each message
- **Multi-Model Comparison**: Run multiple models multiple times to compare performance
- **Visualization**: Generate charts showing performance over time with confidence intervals (10th, 50th, 90th percentiles)
- **Summary Statistics**: Aggregate statistics for each model including average rewards, programs discovered, etc.

## Usage

### 1. Run a Single Model Test

Test a single model with metrics recording:

```bash
uv run python run_model_comparison.py --single "openai/gpt-4o-mini" --max-messages 50
```

### 2. Run Full Model Comparison

Compare multiple models (10 runs each by default):

```bash
# Use default models
uv run python run_model_comparison.py --runs 10 --max-messages 200

# Or specify custom models
uv run python run_model_comparison.py \
    --models "openai/gpt-4o-mini" "google/gemini-2.5-pro-exp-03-25" \
    --runs 10 \
    --max-messages 200
```

### 3. Analyze Results

Generate comparison charts and summary statistics:

```bash
# Analyze the latest comparison
uv run python analyze_model_performance.py

# Or specify a specific metrics file
uv run python analyze_model_performance.py --metrics-file metrics/comparison_20240315_143022.json
```

## Output Files

### Metrics Files
- **Individual runs**: `metrics/{run_id}_metrics.json` - Detailed metrics for each run
- **Comparison data**: `metrics/comparison_{timestamp}.json` - Consolidated metrics from all runs

### Analysis Outputs
- **Chart**: `model_comparison.png` - Visual comparison with confidence intervals
- **Summary**: `model_comparison_summary.csv` - Statistical summary table

## Metrics Tracked

### Per-Message Metrics
- Message index and timestamp
- Reward delta and cumulative reward
- New programs discovered
- New instructions discovered
- Skills created
- Errors encountered

### Summary Metrics
- Total messages sent
- Final reward achieved
- Total unique programs discovered
- Total unique instructions discovered
- Total skills created
- Total errors encountered

## Chart Interpretation

The comparison chart shows:

1. **Top Panel**: Cumulative reward over messages
   - Solid line: Median performance (50th percentile)
   - Shaded area: 10th to 90th percentile range
   - Light lines: Individual runs

2. **Bottom Panel**: Box plot of final rewards
   - Shows distribution of final rewards for each model
   - Useful for understanding consistency

## Available Models

Common models to test:
- `openrouter/horizon-beta`
- `openai/gpt-4o-mini`
- `openai/gpt-4o`
- `google/gemini-2.5-pro-exp-03-25`
- `deepseek/deepseek-chat-v3-0324:free`
- `mistralai/mistral-small-3.2-24b-instruct:free`
- `qwen/qwen3-coder:free`
- `x-ai/grok-3-mini`

## Tips for Comparison

1. **Sample Size**: Run at least 10 iterations per model for statistical significance
2. **Message Limit**: 200 messages is usually sufficient to see performance differences
3. **Environment**: Ensure consistent environment conditions across runs
4. **Time**: Each run takes ~5-10 minutes depending on model and message count

## Example Workflow

```bash
# 1. Run comparison with 3 models, 10 runs each, 200 messages max
uv run python run_model_comparison.py \
    --models "openai/gpt-4o-mini" "google/gemini-2.5-pro-exp-03-25" "deepseek/deepseek-chat-v3-0324:free" \
    --runs 10 \
    --max-messages 200

# 2. Generate analysis and charts
uv run python analyze_model_performance.py

# 3. View results
open model_comparison.png
cat model_comparison_summary.csv
```

## Interpreting Results

Key metrics to compare:
- **Final Reward**: Higher is better, indicates more successful exploration
- **Programs Discovered**: More unique programs shows broader exploration
- **Error Rate**: Lower is better, indicates more reliable code generation
- **Convergence Speed**: How quickly the model reaches high rewards

The 10th-90th percentile range shows consistency - narrower bands indicate more reliable performance.