#!/usr/bin/env python3
"""
Analyze and visualize code_loop_explorer performance metrics.
All outputs are saved to a timestamped folder in analysis_results/
"""

import json
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
from pathlib import Path

def create_output_dir():
    """Create a timestamped output directory for analysis results"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(f"analysis_results/code_loop_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 Created output directory: {output_dir}")
    return output_dir

def load_code_loop_metrics():
    """Load all code_loop metrics from the metrics directory"""
    metrics_files = glob.glob("metrics/code_loop_*.json")
    all_metrics = []
    
    for file in metrics_files:
        # Skip conversation files
        if "_conversation.json" in file:
            continue
            
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                # Only include if it has the expected structure
                if 'model' in data and 'messages' in data:
                    all_metrics.append(data)
        except Exception as e:
            print(f"Error loading {file}: {e}")
            continue
    
    return all_metrics

def analyze_metrics(metrics_list, output_dir):
    """Analyze code_loop metrics and generate insights"""
    
    if not metrics_list:
        print("No metrics found!")
        return pd.DataFrame()
    
    # Create summary dataframe
    summary_data = []
    for m in metrics_list:
        # Calculate total rewards
        total_reward = m['cumulative_rewards'][-1] if m.get('cumulative_rewards') else 0
        
        # Count successful code blocks
        successful_blocks = sum(1 for msg in m.get('messages', []) 
                               if msg.get('code_extracted') and msg.get('reward', 0) > 0)
        
        # Calculate success rate
        total_blocks = sum(1 for msg in m.get('messages', []) 
                          if msg.get('code_extracted'))
        
        success_rate = successful_blocks / total_blocks if total_blocks > 0 else 0
        
        # Count unique programs and instructions
        programs = set()
        instructions = set()
        for msg in m.get('messages', []):
            if msg.get('instructions_discovered'):
                for inst in msg['instructions_discovered']:
                    programs.add(inst.get('program_id'))
                    instructions.add((inst.get('program_id'), inst.get('instruction_name')))
        
        summary_data.append({
            'model': m['model'],
            'run_id': m.get('run_id', 'unknown'),
            'run_index': m.get('run_index', 0),
            'total_messages': len(m.get('messages', [])),
            'total_reward': total_reward,
            'successful_blocks': successful_blocks,
            'total_blocks': total_blocks,
            'success_rate': success_rate,
            'programs_discovered': len(programs),
            'unique_instructions': len(instructions),
            'avg_reward_per_message': total_reward / len(m.get('messages', [])) if m.get('messages') else 0,
            'errors': sum(1 for msg in m.get('messages', []) if msg.get('error'))
        })
    
    df = pd.DataFrame(summary_data)
    
    # Sort by total reward
    df = df.sort_values('total_reward', ascending=False)
    
    # Print summary statistics
    print("\n" + "="*60)
    print("CODE LOOP PERFORMANCE SUMMARY")
    print("="*60)
    
    # Group by model
    if 'model' in df.columns:
        print("\nBy Model:")
        model_summary = df.groupby('model').agg({
            'total_reward': ['mean', 'std', 'max'],
            'success_rate': ['mean', 'std'],
            'programs_discovered': ['mean', 'max'],
            'unique_instructions': ['mean', 'max']
        }).round(2)
        print(model_summary)
    
    # Best runs
    print("\n🏆 Top 5 Runs by Total Reward:")
    top_runs = df.nlargest(5, 'total_reward')[['model', 'run_id', 'total_reward', 'programs_discovered', 'unique_instructions']]
    print(top_runs.to_string(index=False))
    
    # Best success rate
    print("\n✅ Top 5 Runs by Success Rate:")
    best_success = df.nlargest(5, 'success_rate')[['model', 'run_id', 'success_rate', 'total_reward']]
    print(best_success.to_string(index=False))
    
    # Save summary to CSV
    csv_file = output_dir / 'summary_statistics.csv'
    df.to_csv(csv_file, index=False)
    print(f"\n💾 Summary statistics saved to: {csv_file}")
    
    return df

def plot_model_error_bars(df, output_dir):
    """Create error bar plots for model performance with confidence intervals"""
    
    # Set style
    sns.set_style("whitegrid")
    
    # Calculate statistics per model
    model_stats = df.groupby('model').agg({
        'total_reward': ['mean', 'std', 'count'],
        'avg_reward_per_message': ['mean', 'std'],
        'success_rate': ['mean', 'std'],
        'programs_discovered': ['mean', 'std']
    })
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Total Reward with Error Bars
    ax1 = axes[0, 0]
    models = model_stats.index
    means = model_stats[('total_reward', 'mean')]
    stds = model_stats[('total_reward', 'std')]
    counts = model_stats[('total_reward', 'count')]
    
    # Calculate standard error
    std_errors = stds / np.sqrt(counts)
    
    x_pos = np.arange(len(models))
    ax1.bar(x_pos, means, yerr=std_errors, capsize=5, alpha=0.7, color='steelblue')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(models, rotation=45, ha='right')
    ax1.set_ylabel('Total Reward')
    ax1.set_title('Average Total Reward by Model (with Standard Error)')
    ax1.grid(axis='y', alpha=0.3)
    
    # Add sample size annotations
    for i, (mean, se, count) in enumerate(zip(means, std_errors, counts)):
        ax1.text(i, mean + se + 0.5, f'n={int(count)}', ha='center', fontsize=9)
    
    # 2. Success Rate with Error Bars
    ax2 = axes[0, 1]
    means = model_stats[('success_rate', 'mean')]
    stds = model_stats[('success_rate', 'std')]
    
    ax2.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7, color='green')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(models, rotation=45, ha='right')
    ax2.set_ylabel('Success Rate')
    ax2.set_title('Average Success Rate by Model (with Std Dev)')
    ax2.grid(axis='y', alpha=0.3)
    
    # 3. Reward per Message with Error Bars
    ax3 = axes[1, 0]
    means = model_stats[('avg_reward_per_message', 'mean')]
    stds = model_stats[('avg_reward_per_message', 'std')]
    
    ax3.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7, color='orange')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(models, rotation=45, ha='right')
    ax3.set_ylabel('Avg Reward per Message')
    ax3.set_title('Reward Efficiency by Model (with Std Dev)')
    ax3.grid(axis='y', alpha=0.3)
    
    # 4. Programs Discovered with Error Bars
    ax4 = axes[1, 1]
    means = model_stats[('programs_discovered', 'mean')]
    stds = model_stats[('programs_discovered', 'std')]
    
    ax4.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7, color='purple')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(models, rotation=45, ha='right')
    ax4.set_ylabel('Programs Discovered')
    ax4.set_title('Average Programs Discovered by Model (with Std Dev)')
    ax4.grid(axis='y', alpha=0.3)
    
    plt.suptitle('Model Performance Comparison with Error Bars', fontsize=16, y=1.02)
    plt.tight_layout()
    
    # Save figure
    filename = output_dir / 'error_bars.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"📊 Error bar plots saved to: {filename}")
    plt.show()
    
    return model_stats

def plot_code_loop_performance(df, output_dir):
    """Create visualizations for code_loop performance"""
    
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (15, 10)
    
    # Create subplots
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # 1. Total Reward by Model
    ax1 = axes[0, 0]
    if 'model' in df.columns:
        model_rewards = df.groupby('model')['total_reward'].apply(list)
        for model, rewards in model_rewards.items():
            ax1.scatter([model] * len(rewards), rewards, alpha=0.6, s=50)
        
        # Add mean line
        model_means = df.groupby('model')['total_reward'].mean()
        ax1.hlines(model_means.values, 
                  xmin=np.arange(len(model_means)) - 0.3,
                  xmax=np.arange(len(model_means)) + 0.3,
                  colors='red', linestyles='solid', linewidth=2, label='Mean')
        
    ax1.set_xlabel('Model')
    ax1.set_ylabel('Total Reward')
    ax1.set_title('Total Rewards Distribution by Model')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Rotate x labels
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 2. Success Rate Distribution
    ax2 = axes[0, 1]
    if 'model' in df.columns:
        for model in df['model'].unique():
            model_data = df[df['model'] == model]['success_rate']
            ax2.hist(model_data, alpha=0.5, label=model, bins=10)
    
    ax2.set_xlabel('Success Rate')
    ax2.set_ylabel('Count')
    ax2.set_title('Success Rate Distribution')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Programs Discovered
    ax3 = axes[0, 2]
    if 'model' in df.columns:
        model_programs = df.groupby('model')['programs_discovered'].apply(list)
        for model, programs in model_programs.items():
            ax3.scatter([model] * len(programs), programs, alpha=0.6, s=50)
    
    ax3.set_xlabel('Model')
    ax3.set_ylabel('Programs Discovered')
    ax3.set_title('Programs Discovered by Model')
    ax3.grid(True, alpha=0.3)
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 4. Reward Efficiency (Reward per Message)
    ax4 = axes[1, 0]
    if 'model' in df.columns:
        model_efficiency = df.groupby('model')['avg_reward_per_message'].mean().sort_values()
        ax4.barh(model_efficiency.index, model_efficiency.values, color='steelblue')
    
    ax4.set_xlabel('Average Reward per Message')
    ax4.set_ylabel('Model')
    ax4.set_title('Reward Efficiency by Model')
    ax4.grid(True, alpha=0.3)
    
    # 5. Success Rate vs Total Reward
    ax5 = axes[1, 1]
    if 'model' in df.columns:
        for model in df['model'].unique():
            model_data = df[df['model'] == model]
            ax5.scatter(model_data['success_rate'], 
                       model_data['total_reward'], 
                       label=model, alpha=0.6, s=50)
    
    ax5.set_xlabel('Success Rate')
    ax5.set_ylabel('Total Reward')
    ax5.set_title('Success Rate vs Total Reward')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Error Count Distribution
    ax6 = axes[1, 2]
    if 'model' in df.columns:
        model_errors = df.groupby('model')['errors'].mean().sort_values()
        ax6.bar(model_errors.index, model_errors.values, color='coral')
    
    ax6.set_xlabel('Model')
    ax6.set_ylabel('Average Errors per Run')
    ax6.set_title('Error Frequency by Model')
    ax6.grid(True, alpha=0.3)
    plt.setp(ax6.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.suptitle('Code Loop Explorer Performance Analysis', fontsize=16, y=1.02)
    plt.tight_layout()
    
    # Save figure
    filename = output_dir / 'performance_overview.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"📊 Performance plots saved to: {filename}")
    
    plt.show()

def analyze_reward_progression(output_dir):
    """Analyze how rewards progress over messages with error bands"""
    
    # Load metrics with full message history
    metrics_files = glob.glob("metrics/code_loop_*_metrics.json")
    model_progressions = {}
    
    for file in metrics_files:
        if "_conversation.json" in file:
            continue
            
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                if 'model' in data and 'cumulative_rewards' in data:
                    model = data['model']
                    if model not in model_progressions:
                        model_progressions[model] = []
                    model_progressions[model].append(data['cumulative_rewards'])
        except:
            continue
    
    if not model_progressions:
        print("No reward progression data found")
        return
    
    # Create plot
    plt.figure(figsize=(14, 8))
    
    for model, progressions in model_progressions.items():
        # Pad progressions to same length
        max_len = max(len(p) for p in progressions)
        padded = []
        for p in progressions:
            padded_p = p + [p[-1]] * (max_len - len(p)) if p else [0] * max_len
            padded.append(padded_p)
        
        # Calculate mean and std
        progressions_array = np.array(padded)
        mean_progression = np.mean(progressions_array, axis=0)
        std_progression = np.std(progressions_array, axis=0)
        
        # Plot mean with error band
        x = np.arange(len(mean_progression))
        plt.plot(x, mean_progression, label=f'{model} (n={len(progressions)})', linewidth=2)
        plt.fill_between(x, 
                        mean_progression - std_progression,
                        mean_progression + std_progression,
                        alpha=0.3)
    
    plt.xlabel('Message Number')
    plt.ylabel('Cumulative Reward')
    plt.title('Reward Progression Over Time (Mean ± Std Dev)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save figure
    filename = output_dir / 'reward_progression.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"📊 Reward progression plot saved to: {filename}")
    plt.show()

def analyze_reward_progression_individual(output_dir):
    """Show individual trajectories for each model"""
    
    # Load metrics with full message history
    metrics_files = glob.glob("metrics/code_loop_*_metrics.json")
    model_progressions = {}
    
    for file in metrics_files:
        if "_conversation.json" in file:
            continue
            
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                if 'model' in data and 'cumulative_rewards' in data:
                    model = data['model']
                    if model not in model_progressions:
                        model_progressions[model] = []
                    model_progressions[model].append(data['cumulative_rewards'])
        except:
            continue
    
    if not model_progressions:
        print("No reward progression data found")
        return
    
    # Create subplots for each model
    n_models = len(model_progressions)
    fig, axes = plt.subplots(1, n_models, figsize=(5*n_models, 6), sharey=True)
    
    if n_models == 1:
        axes = [axes]
    
    for idx, (model, progressions) in enumerate(model_progressions.items()):
        ax = axes[idx]
        
        # Plot each individual trajectory
        for i, progression in enumerate(progressions):
            x = np.arange(len(progression))
            ax.plot(x, progression, alpha=0.5, linewidth=1)
        
        # Add mean line
        max_len = max(len(p) for p in progressions)
        padded = []
        for p in progressions:
            padded_p = p + [p[-1]] * (max_len - len(p)) if p else [0] * max_len
            padded.append(padded_p)
        
        mean_progression = np.mean(padded, axis=0)
        ax.plot(np.arange(len(mean_progression)), mean_progression, 
               color='red', linewidth=3, label='Mean', linestyle='--')
        
        ax.set_xlabel('Message Number')
        ax.set_title(f'{model}\n({len(progressions)} runs)')
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    axes[0].set_ylabel('Cumulative Reward')
    plt.suptitle('Individual Reward Trajectories by Model', fontsize=14, y=1.02)
    plt.tight_layout()
    
    # Save figure
    filename = output_dir / 'individual_trajectories.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"📊 Individual trajectories plot saved to: {filename}")
    plt.show()

def main():
    print("="*60)
    print("CODE LOOP EXPLORER ANALYSIS")
    print("="*60)
    
    # Create output directory
    output_dir = create_output_dir()
    
    print("\n📂 Loading code_loop metrics...")
    metrics = load_code_loop_metrics()
    
    if not metrics:
        print("❌ No code_loop metrics found in metrics/ directory!")
        return
    
    print(f"✅ Found {len(metrics)} code_loop runs to analyze")
    
    # Analyze metrics
    df = analyze_metrics(metrics, output_dir)
    
    # Create visualizations
    if len(df) > 0:
        print("\n📊 Creating visualizations...")
        
        # Original plots
        plot_code_loop_performance(df, output_dir)
        
        # Error bar plots
        if df['model'].nunique() > 1:
            plot_model_error_bars(df, output_dir)
        
        # Reward progression with error bands
        analyze_reward_progression(output_dir)
        
        # Individual trajectories
        analyze_reward_progression_individual(output_dir)
        
        print(f"\n✅ Analysis complete! All results saved to: {output_dir}")
        print(f"📁 {output_dir}/")
        print(f"   ├── summary_statistics.csv")
        print(f"   ├── performance_overview.png")
        print(f"   ├── error_bars.png")
        print(f"   ├── reward_progression.png")
        print(f"   └── individual_trajectories.png")

if __name__ == "__main__":
    main()