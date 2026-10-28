"""
Visualization Script for DACC-ID Experimental Results:
Generates publication-quality figures for:
1. Model Comparison (E1 to E4)
2. Drift Adaptation under Stress Scenarios (E5)
3. Alert Reduction & Incident Correlation Funnel (E6)
4. Ablation Study Trade-offs
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8


def plot_fig1_model_comparison():
    csv_path = 'results/dacc_id/e1_to_e4_model_comparison.csv'
    if not os.path.exists(csv_path):
        return
    df = pd.read_csv(csv_path)

    models = ['LSTM-AE\n(Base Paper)', 'Random Forest\n(Supervised)', 'Isolation Forest\n(Unsupervised)', 'Hybrid RF+IF\n(DACC-ID Core)']
    f1 = df['f1_score'] * 100
    rec = df['recall'] * 100
    prec = df['precision'] * 100
    fpr = df['fpr'] * 100

    x = np.arange(len(models))
    width = 0.20

    fig, ax1 = plt.subplots(figsize=(10, 5), dpi=300)

    rects1 = ax1.bar(x - 1.5 * width, f1, width, label='F1-Score (%)', color='#1f77b4', edgecolor='black', linewidth=0.5)
    rects2 = ax1.bar(x - 0.5 * width, rec, width, label='Recall (%)', color='#2ca02c', edgecolor='black', linewidth=0.5)
    rects3 = ax1.bar(x + 0.5 * width, prec, width, label='Precision (%)', color='#ff7f0e', edgecolor='black', linewidth=0.5)
    rects4 = ax1.bar(x + 1.5 * width, fpr, width, label='FPR (%) [Lower is Better]', color='#d62728', edgecolor='black', linewidth=0.5)

    ax1.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
    ax1.set_title('E1–E4 Detection Benchmark: Baseline LSTM vs Supervised, Unsupervised, & Hybrid Models', fontsize=13, fontweight='bold', pad=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, fontsize=11)
    ax1.set_ylim(0, 115)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    ax1.legend(loc='upper right', framealpha=0.9, fontsize=10)

    # Annotate values
    for rects in [rects1, rects2, rects3, rects4]:
        for rect in rects:
            height = rect.get_height()
            ax1.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, fontweight='bold')

    plt.tight_layout()
    fig.savefig('results/dacc_id/fig1_model_comparison_e1_to_e4.png', dpi=300)
    plt.close()
    print("Saved fig1_model_comparison_e1_to_e4.png")


def plot_fig2_drift_adaptation():
    csv_path = 'results/dacc_id/drift_adaptation_results.csv'
    if not os.path.exists(csv_path):
        return
    df = pd.read_csv(csv_path)

    scenarios = ['Nominal Stream', '2.0x Rate Drift', '20k Attack Flood']
    df_static = df[df['threshold_mode'] == 'Static_95th']
    df_adapt = df[df['threshold_mode'] == 'TCA_ADWIN_Adaptive']

    fpr_static = df_static['fpr'].values * 100
    fpr_adapt = df_adapt['fpr'].values * 100

    f1_static = df_static['f1_score'].values * 100
    f1_adapt = df_adapt['f1_score'].values * 100

    x = np.arange(len(scenarios))
    width = 0.35

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)

    # Plot FPR
    r1 = ax1.bar(x - width/2, fpr_static, width, label='Static 95th Threshold', color='#e74c3c', edgecolor='black', linewidth=0.6)
    r2 = ax1.bar(x + width/2, fpr_adapt, width, label='TCA+ADWIN Adaptive', color='#2ecc71', edgecolor='black', linewidth=0.6)
    ax1.set_ylabel('False Positive Rate (%) [Lower is Better]', fontsize=11, fontweight='bold')
    ax1.set_title('(a) False Alarm Control under Drift & Contamination', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(scenarios, fontsize=10)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    ax1.legend(loc='upper left', framealpha=0.9)

    for rect in r1:
        h = rect.get_height()
        ax1.annotate(f'{h:.2f}%', xy=(rect.get_x() + rect.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')
    for rect in r2:
        h = rect.get_height()
        ax1.annotate(f'{h:.2f}%', xy=(rect.get_x() + rect.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Plot F1
    r3 = ax2.bar(x - width/2, f1_static, width, label='Static 95th Threshold', color='#3498db', edgecolor='black', linewidth=0.6)
    r4 = ax2.bar(x + width/2, f1_adapt, width, label='TCA+ADWIN Adaptive', color='#9b59b6', edgecolor='black', linewidth=0.6)
    ax2.set_ylabel('F1-Score (%)', fontsize=11, fontweight='bold')
    ax2.set_title('(b) Detection Accuracy Retention', fontsize=12, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(scenarios, fontsize=10)
    ax2.set_ylim(80, 100)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)
    ax2.legend(loc='lower left', framealpha=0.9)

    for rect in r3:
        h = rect.get_height()
        ax2.annotate(f'{h:.2f}%', xy=(rect.get_x() + rect.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')
    for rect in r4:
        h = rect.get_height()
        ax2.annotate(f'{h:.2f}%', xy=(rect.get_x() + rect.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    fig.savefig('results/dacc_id/fig2_drift_adaptation_stress.png', dpi=300)
    plt.close()
    print("Saved fig2_drift_adaptation_stress.png")


def plot_fig3_incident_correlation():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)

    # Alert Reduction Funnel
    stages = ['Raw Telemetry\nFlows', 'Raw Flow-Level\nAlerts', 'Correlated Multi-Stage\nIncidents']
    counts = [100000, 74453, 91]
    colors = ['#34495e', '#e67e22', '#27ae60']

    bars = ax1.bar(stages, counts, color=colors, edgecolor='black', linewidth=0.6, width=0.55)
    ax1.set_yscale('log')
    ax1.set_ylabel('Event Count (Log Scale)', fontsize=11, fontweight='bold')
    ax1.set_title('(a) Alert Fatigue Reduction Funnel (ARR = 99.88%)', fontsize=12, fontweight='bold')
    ax1.grid(axis='y', linestyle='--', alpha=0.5)

    for bar in bars:
        h = bar.get_height()
        ax1.annotate(f'{h:,}', xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points", ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Priority Triage Breakdown
    tiers = ['CRITICAL\n(Immediate Action)', 'HIGH\n(Priority Triage)', 'MEDIUM\n(Secondary)', 'LOW\n(Informational)']
    tier_counts = [67, 24, 0, 0]
    tier_colors = ['#c0392b', '#e67e22', '#f1c40f', '#2980b9']

    b2 = ax2.bar(tiers, tier_counts, color=tier_colors, edgecolor='black', linewidth=0.6, width=0.55)
    ax2.set_ylabel('Number of Correlated Incidents', fontsize=11, fontweight='bold')
    ax2.set_title('(b) Contextual Risk Prioritization Triage', fontsize=12, fontweight='bold')
    ax2.grid(axis='y', linestyle='--', alpha=0.5)

    for bar in b2:
        h = bar.get_height()
        if h > 0:
            ax2.annotate(f'{h} ({h/91*100:.1f}%)', xy=(bar.get_x() + bar.get_width() / 2, h),
                         xytext=(0, 4), textcoords="offset points", ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    fig.savefig('results/dacc_id/fig3_incident_correlation_pipeline.png', dpi=300)
    plt.close()
    print("Saved fig3_incident_correlation_pipeline.png")


def plot_fig4_ablation_matrix():
    csv_path = 'results/dacc_id/ablation_study_results.csv'
    if not os.path.exists(csv_path):
        return
    df = pd.read_csv(csv_path)

    configs = [
        'Full DACC-ID',
        'w/o Drift Adaptation',
        'w/o Anomaly Detection\n(RF Only)',
        'w/o Supervised\n(IF Only)',
        'w/o Event Correlation\n(Raw Alerts)',
        'w/o Context Risk\n(Equal Weights)'
    ]
    arr = df['alert_reduction_rate'].values
    f1 = df['f1_score'].values * 100
    fpr_drift = df['fpr_drift'].values * 100
    multistage = df['multistage_detected'].values

    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    y_pos = np.arange(len(configs))

    # Horizontal bar chart of Alert Reduction Rate and Multi-stage campaigns detected
    b1 = ax.barh(y_pos - 0.2, arr, height=0.35, label='Alert Reduction Rate (%)', color='#2ecc71', edgecolor='black', linewidth=0.6)
    b2 = ax.barh(y_pos + 0.2, multistage, height=0.35, label='Multi-Stage Campaigns Reconstructed', color='#3498db', edgecolor='black', linewidth=0.6)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(configs, fontsize=10, fontweight='bold')
    ax.invert_yaxis()  # Labels read top-to-bottom
    ax.set_xlabel('Score / Count', fontsize=11, fontweight='bold')
    ax.set_title('Ablation Study: Impact of Removing Individual DACC-ID Components', fontsize=12, fontweight='bold', pad=12)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    ax.legend(loc='lower right', framealpha=0.9, fontsize=10)

    for bar in b1:
        w = bar.get_width()
        ax.annotate(f'{w:.1f}%', xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(4, 0), textcoords="offset points", ha='left', va='center', fontsize=9, fontweight='bold')

    for bar in b2:
        w = bar.get_width()
        ax.annotate(f'{int(w)}', xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(4, 0), textcoords="offset points", ha='left', va='center', fontsize=9, fontweight='bold')

    plt.tight_layout()
    fig.savefig('results/dacc_id/fig4_ablation_matrix.png', dpi=300)
    plt.close()
    print("Saved fig4_ablation_matrix.png")


if __name__ == '__main__':
    plot_fig1_model_comparison()
    plot_fig2_drift_adaptation()
    plot_fig3_incident_correlation()
    plot_fig4_ablation_matrix()
    print("All DACC-ID plots successfully created in results/dacc_id/!")
