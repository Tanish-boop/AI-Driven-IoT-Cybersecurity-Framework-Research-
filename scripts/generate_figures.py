"""
Generate Publication-Quality Figures for Paper from Full 5-Seed Benchmark Results
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
    metrics_dir = 'results/metrics'
    results_file = os.path.join(metrics_dir, 'full_benchmark_results.csv')
    figures_dir = 'results/figures'
    paper_figures_dir = 'paper/figures'

    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(paper_figures_dir, exist_ok=True)

    if not os.path.exists(results_file):
        print(f"Results file missing: {results_file}")
        return

    df_res = pd.read_csv(results_file)

    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.size'] = 10

    # 1. Figure 1: F1-Score & FPR Comparison across Threshold Strategies (Dense-AE & Baselines)
    base_res = df_res[df_res['experiment'] == 'base_stream'].copy()
    grouped = base_res.groupby(['model', 'strategy']).agg(
        f1_mean=('f1_score', 'mean'), f1_std=('f1_score', 'std'),
        fpr_mean=('fpr', 'mean'), fpr_std=('fpr', 'std')
    ).reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    strategies = grouped['strategy'].unique()
    
    # Filter Dense-AE strategies
    dense_strats = ['Fixed_95', 'Fixed_99', 'UnGuarded_EWMA', 'Excluded_EWMA', 'Guarded_EWMA']
    dense_df = grouped[grouped['model'] == 'Dense-AE'].set_index('strategy').reindex(dense_strats).reset_index()

    x = np.arange(len(dense_strats))
    width = 0.35

    rects1 = ax.bar(x - width/2, dense_df['f1_mean'], width, yerr=dense_df['f1_std'], label='F1-Score', color='#1f77b4', capsize=5)
    rects2 = ax.bar(x + width/2, dense_df['fpr_mean'], width, yerr=dense_df['fpr_std'], label='False Positive Rate (FPR)', color='#d62728', capsize=5)

    ax.set_xlabel('Threshold Strategy (Dense-AE)', fontweight='bold')
    ax.set_ylabel('Score / Rate', fontweight='bold')
    ax.set_title('Dense-AE Performance Across Threshold Strategies (5 Random Seeds, Mean ± Std)', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(dense_strats, rotation=15)
    ax.legend()
    ax.set_ylim(0, 1.1)

    plt.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'figure1_threshold_comparison.png'), dpi=300)
    fig.savefig(os.path.join(paper_figures_dir, 'figure1_threshold_comparison.png'), dpi=300)
    plt.close()

    # 2. Figure 2: Rate-Scaling Stress Test (1.0x vs 1.5x vs 2.0x)
    stress_res = df_res[df_res['experiment'].isin(['base_stream', 'feature_stress_test']) & (df_res['model'] == 'Dense-AE')].copy()
    stress_res = stress_res[stress_res['strategy'].str.contains('Fixed_95')]
    
    stress_summary = stress_res.groupby('strategy').agg(
        fpr_mean=('fpr', 'mean'), fpr_std=('fpr', 'std'),
        f1_mean=('f1_score', 'mean'), f1_std=('f1_score', 'std')
    ).reset_index()

    fig, ax = plt.subplots(figsize=(8, 4.5))
    x_stress = np.arange(len(stress_summary))
    ax.bar(x_stress, stress_summary['fpr_mean'], yerr=stress_summary['fpr_std'], color='#ff7f0e', capsize=5, width=0.4)
    ax.set_xlabel('Rate Scaling Condition', fontweight='bold')
    ax.set_ylabel('False Positive Rate (FPR)', fontweight='bold')
    ax.set_title('False Positive Rate under Input Feature Rate-Scaling Stress Tests', fontweight='bold')
    ax.set_xticks(x_stress)
    ax.set_xticklabels(stress_summary['strategy'], rotation=15)
    ax.set_ylim(0, 1.05)

    plt.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'figure2_rate_stress_test.png'), dpi=300)
    fig.savefig(os.path.join(paper_figures_dir, 'figure2_rate_stress_test.png'), dpi=300)
    plt.close()

    print("Figures generated successfully in results/figures and paper/figures!")

if __name__ == '__main__':
    main()
