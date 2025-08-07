#!/usr/bin/env python3
"""
Run batch model comparison for code_loop_explorer.
Tests multiple models with specified runs and messages.
"""

import asyncio
import os
import sys
import time
from datetime import datetime

# Add to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from code_loop_explorer import main as run_code_loop


async def run_comparison():
    """Run model comparison for specified models."""
    
    # Configuration
    models = [
        # "google/gemini-2.5-flash",  # Already has 10 runs
        # "openai/gpt-4o-mini",       # Already has 9 runs
        # "openai/gpt-oss-120b",      # Already has 4 runs
        "qwen/qwen3-coder"            # Missing ALL runs
    ]
    runs_per_model = 5
    max_messages = 50
    
    # Check if surfpool is already running
    use_external_surfpool = os.getenv("USE_EXTERNAL_SURFPOOL", "false").lower() == "true"
    
    print("="*60)
    print("CODE LOOP MODEL COMPARISON BATCH")
    print("="*60)
    print(f"Models to test: {len(models)}")
    for m in models:
        print(f"  - {m}")
    print(f"Runs per model: {runs_per_model}")
    print(f"Messages per run: {max_messages}")
    print(f"Total experiments: {len(models) * runs_per_model}")
    print(f"Estimated time: {len(models) * runs_per_model * 5} minutes")
    if use_external_surfpool:
        print("\n⚠️  Using EXTERNAL surfpool instance on localhost:8899")
        print("   Make sure surfpool is already running!")
    else:
        print("\n   Will start/stop surfpool for each run")
    print("="*60)
    
    # Confirm
    response = input("\nProceed? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled")
        return
    
    start_time = time.time()
    experiment_num = 0
    total_experiments = len(models) * runs_per_model
    
    for model in models:
        print(f"\n{'='*50}")
        print(f"Testing: {model}")
        print(f"{'='*50}")
        
        for run_idx in range(runs_per_model):
            experiment_num += 1
            run_start = time.time()
            
            print(f"\n[{experiment_num}/{total_experiments}] {model} - Run {run_idx + 1}/{runs_per_model}")
            print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
            
            # Set environment variables
            os.environ['MODEL_NAME'] = model
            os.environ['MAX_MESSAGES'] = str(max_messages)
            os.environ['RUN_INDEX'] = str(run_idx)  # Pass the run index!
            # USE_EXTERNAL_SURFPOOL is already set in environment if needed
            
            try:
                # Run the code_loop_explorer
                await run_code_loop()
                
                run_duration = time.time() - run_start
                print(f"✓ Run completed in {run_duration:.1f} seconds")
                
            except Exception as e:
                print(f"✗ Error in run: {e}")
            
            # Small delay between runs
            if experiment_num < total_experiments:
                print("Waiting 5 seconds before next run...")
                await asyncio.sleep(5)
    
    # Summary
    total_duration = time.time() - start_time
    print(f"\n{'='*60}")
    print("COMPARISON COMPLETE!")
    print(f"{'='*60}")
    print(f"Total time: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
    print(f"Average per run: {total_duration/total_experiments:.1f} seconds")
    print(f"\nTo analyze results, run:")
    print("  uv run python analyze_code_loop_performance.py")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(run_comparison())