#!/usr/bin/env python3
"""
Simple runner script for the code loop explorer.
This extracts TypeScript code blocks from agent responses and executes them directly.

Usage:
    # Use default model (horizon-beta)
    uv run python run_code_loop.py
    
    # Use a specific model
    uv run python run_code_loop.py --model "openai/gpt-4o-mini"
    
    # Run for more messages
    uv run python run_code_loop.py --max-messages 100
"""

import argparse
import asyncio
import os
from code_loop_explorer import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the code loop explorer")
    parser.add_argument(
        "--model", 
        default="openrouter/horizon-beta",
        help="Model to use (default: openrouter/horizon-beta)"
    )
    parser.add_argument(
        "--max-messages",
        type=int,
        default=50,
        help="Maximum number of messages (default: 50)"
    )
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ["MODEL_NAME"] = args.model
    os.environ["MAX_MESSAGES"] = str(args.max_messages)
    
    # Run the explorer
    asyncio.run(main())