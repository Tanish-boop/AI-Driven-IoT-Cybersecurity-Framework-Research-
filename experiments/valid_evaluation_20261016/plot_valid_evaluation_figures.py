"""
Generates publication-quality figures for the pre-registered valid evaluation benchmark.
Produces:
  1. fig_tradeoff_f1_vs_fpr.png (Nominal Trade-off)
  2. fig_threshold_traces.png (Contamination Flood Trajectory)
  3. fig_scenario_comparison.png (Performance Across Scenarios)
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('default')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['grid.linestyle'] = '--'

out_dir = 'experiments/valid_evaluation_20261016'
df_per_seed = pd.read_csv(os.path.join(out_dir, 'results_per_seed.csv'))
traces_data = np.load(os.path.join(out_dir, 'threshold_traces.npz'))

# -------------------------------------------------------------
# Figure 1: F1-Score vs FPR Trade-off on Nominal Stream
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
df_nom = df_per_seed[df_per_seed['scenario'] == 'scenario_1_nominal']
summary_nom = df_nom.groupby('method').agg({'f1_score': ['mean', 'std'], 'fpr': ['mean', 'std']}).reset_index()

colors = {
    'Fixed_95': '#1f77b4',
    'Fixed_99': '#aec7e8',
    'Raw_EWMA': '#d62728',
    'Excluded_EWMA': '#ff7f0e',
    'CGB_Adaptive': '#2ca02c',
    'Gated_Rolling_Quantile': '#9467bd',
    'Robust_Median_MAD': '#8c564b'
}

for _, row in summary_nom.iterrows():
    m = row['method'].values[0] if hasattr(row['method'], 'values') else row['method']
    f1_m = row[('f1_score', 'mean')]
    f1_s = row[('f1_score', 'std')]
    fpr_m = row[('fpr', 'mean')]
    fpr_s = row[('fpr', 'std')]

    c = colors.get(m, '#333333')
    ax.errorbar(fpr_m * 100, f1_m * 100, xerr=fpr_s * 100, yerr=f1_s * 100,
                fmt='o', color=c, markersize=8, capsize=4, label=m)
    # Text offset
    dx = 0.3 if fpr_m * 100 < 10 else -2.5
    dy = 0.3 if f1_m * 100 > 50 else 2.0
    ax.annotate(m, (fpr_m * 100 + dx, f1_m * 100 + dy), fontsize=8, weight='bold', color=c)

ax.set_xlabel('False Positive Rate (FPR %)', weight='bold')
ax.set_ylabel('F1-Score (%)', weight='bold')
ax.set_title('Nominal Stream Evaluation: F1-Score vs. False Positive Rate Trade-Off\n(5 Random Seeds, CICIoT2023 Held-Out N=100,000)', weight='bold', pad=12)
ax.set_ylim(-5, 95)
ax.set_xlim(-1, 16)
ax.legend(loc='lower right', frameon=True)
plt.tight_layout()
fig1_path = os.path.join(out_dir, 'fig_tradeoff_f1_vs_fpr.png')
plt.savefig(fig1_path)
plt.close()
print(f"Saved {fig1_path}")

# -------------------------------------------------------------
# Figure 2: Threshold Trajectories under Attack Contamination
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, dpi=300)

subsample = 100 # Plot every 100th sample for clarity
steps = np.arange(0, 100000, subsample)

# Upper plot: Raw EWMA (Log scale due to millions inflation)
raw_trace = traces_data['scenario_4_adversarial_contamination__Raw_EWMA'][::subsample]
ax1.plot(steps, raw_trace, color='#d62728', lw=1.8, label='Raw_EWMA (Un-Guarded)')
ax1.axvspan(10000, 30000, color='red', alpha=0.15, label='20k Attack Flood Episode')
ax1.axvspan(30000, 50000, color='green', alpha=0.15, label='20k Recovery Window')
ax1.set_yscale('log')
ax1.set_ylabel('Threshold tau_t (Log Scale)', weight='bold', color='#d62728')
ax1.set_title('Adversarial Contamination Episode: Threshold Inflation & Recovery Traces', weight='bold')
ax1.legend(loc='upper right')

# Lower plot: Stable & Controlled Methods
f95_trace = traces_data['scenario_4_adversarial_contamination__Fixed_95'][::subsample]
cgb_trace = traces_data['scenario_4_adversarial_contamination__CGB_Adaptive'][::subsample]
ex_trace = traces_data['scenario_4_adversarial_contamination__Excluded_EWMA'][::subsample]
rq_trace = traces_data['scenario_4_adversarial_contamination__Gated_Rolling_Quantile'][::subsample]

ax2.plot(steps, f95_trace, color='#1f77b4', lw=1.5, linestyle='--', label='Fixed_95 (Static Baseline)')
ax2.plot(steps, ex_trace, color='#ff7f0e', lw=1.5, label='Excluded_EWMA')
ax2.plot(steps, cgb_trace, color='#2ca02c', lw=2.0, label='CGB_Adaptive (Gated Controller)')
ax2.plot(steps, rq_trace, color='#9467bd', lw=1.5, linestyle=':', label='Gated_Rolling_Quantile')
ax2.axvspan(10000, 30000, color='red', alpha=0.15)
ax2.axvspan(30000, 50000, color='green', alpha=0.15)
ax2.set_ylabel('Threshold tau_t (Linear Scale)', weight='bold')
ax2.set_xlabel('Stream Event Index (t)', weight='bold')
ax2.legend(loc='upper right')

plt.tight_layout()
fig2_path = os.path.join(out_dir, 'fig_threshold_traces.png')
plt.savefig(fig2_path)
plt.close()
print(f"Saved {fig2_path}")

# -------------------------------------------------------------
# Figure 3: Grouped Bar Chart Across 5 Scenarios
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), dpi=300)

scenarios = ['scenario_1_nominal', 'scenario_2_synthetic_score_shift', 'scenario_3_feature_benign_drift', 'scenario_4_adversarial_contamination', 'scenario_5_mixed_drift_and_contamination']
scenario_labels = ['Nominal', 'Score Shift (1.8x)', 'Feature Drift (2.0x)', 'Attack Flood', 'Mixed']
selected_methods = ['Fixed_95', 'Excluded_EWMA', 'CGB_Adaptive', 'Gated_Rolling_Quantile']

f1_means = {m: [] for m in selected_methods}
fpr_means = {m: [] for m in selected_methods}

for sc in scenarios:
    df_sc = df_per_seed[df_per_seed['scenario'] == sc]
    for m in selected_methods:
        sub = df_sc[df_sc['method'] == m]
        f1_means[m].append(sub['f1_score'].mean() * 100)
        fpr_means[m].append(sub['fpr'].mean() * 100)

x = np.arange(len(scenarios))
width = 0.2

for idx, m in enumerate(selected_methods):
    ax1.bar(x + (idx - 1.5) * width, f1_means[m], width, label=m, color=colors[m])
    ax2.bar(x + (idx - 1.5) * width, fpr_means[m], width, label=m, color=colors[m])

ax1.set_ylabel('F1-Score (%)', weight='bold')
ax1.set_title('(a) F1-Score Across Scenarios', weight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(scenario_labels, rotation=15, ha='right')
ax1.set_ylim(80, 95)
ax1.legend(loc='lower left')

ax2.set_ylabel('False Positive Rate (FPR %)', weight='bold')
ax2.set_title('(b) False Positive Rate Across Scenarios', weight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(scenario_labels, rotation=15, ha='right')
ax2.set_ylim(0, 45)
ax2.legend(loc='upper left')

plt.tight_layout()
fig3_path = os.path.join(out_dir, 'fig_scenario_comparison.png')
plt.savefig(fig3_path)
plt.close()
print(f"Saved {fig3_path}")
print("All figures generated successfully.")
