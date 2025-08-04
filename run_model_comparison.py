#!/usr/bin/env python3
"""
Script to run model comparison experiments for simple_explorer.
"""

import sys
import argparse
from datetime import datetime
from voyager.simple_explorer import run_model_comparison, run_simple_explorer

def main():
    parser = argparse.ArgumentParser(description='Run model comparison experiments')
    parser.add_argument('--models', nargs='+', help='List of models to test')
    parser.add_argument('--runs', type=int, default=10, help='Number of runs per model (default: 10)')
    parser.add_argument('--max-messages', type=int, default=200, help='Maximum messages per run (default: 200)')
    parser.add_argument('--single', type=str, help='Run a single model once (for testing)')
    
    args = parser.parse_args()
    
    if args.single:
        # Run single model for testing
        print(f"Running single test with model: {args.single}")
        print(f"Max messages: {args.max_messages}")
        metrics = run_simple_explorer(
            model_name=args.single,
            max_messages=args.max_messages,
            run_index=0
        )
        print(f"\nTest complete! Metrics saved to: metrics/{metrics['run_id']}_metrics.json")
    else:
        # Run full comparison
        models = args.models or [
            "openrouter/horizon-beta",
            "openai/gpt-4o-mini",
            "google/gemini-2.5-pro-exp-03-25",
            "deepseek/deepseek-chat-v3-0324:free",
            "mistralai/mistral-small-3.2-24b-instruct:free",
            "qwen/qwen3-coder:free"
        ]
        
        print(f"Running model comparison:")
        print(f"Models: {models}")
        print(f"Runs per model: {args.runs}")
        print(f"Max messages per run: {args.max_messages}")
        print(f"Total runs: {len(models) * args.runs}")
        print(f"Estimated time: {len(models) * args.runs * 5} minutes (assuming ~5 min per run)")
        
        response = input("\nProceed? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled")
            return
        
        all_metrics = run_model_comparison(
            models_to_test=models,
            runs_per_model=args.runs,
            max_messages=args.max_messages
        )
        
        print(f"\nComparison complete! {len(all_metrics)} total runs")
        print("Run 'python analyze_model_performance.py' to generate charts")

if __name__ == "__main__":
    main()