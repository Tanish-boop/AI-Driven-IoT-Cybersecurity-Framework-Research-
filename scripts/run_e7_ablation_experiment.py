"""
Experiment E7 Execution Script: Integrated Framework Ablation Benchmark
Compares:
  - Variant 0: Base Paper Architecture (Fixed Threshold + Static Rule + No PQC + Salted SHA-256)
  - Variant 1: Ablation -NoAdaptive (Fixed Threshold + Q-Learning + ML-KEM-768 + Blockchain Log)
  - Variant 2: Ablation -NoRLDefense (Excluded EWMA + Static Rule + ML-KEM-768 + Blockchain Log)
  - Variant 3: Ablation -NoPQC (Excluded EWMA + Q-Learning + No PQC + Blockchain Log)
  - Variant 4: Ablation -NoBlockchain (Excluded EWMA + Q-Learning + ML-KEM-768 + Salted SHA-256)
  - Variant 5: Full Proposed Framework (Excluded EWMA + Q-Learning + ML-KEM-768 + Blockchain Log)

Evaluates over 5 Random Seeds (42, 123, 456, 789, 2026):
  - Detection F1, Precision, Recall, FPR
  - Attack Containment Rate (%)
  - Benign False Block Rate (%)
  - Service Availability (%)
  - End-to-End Latency per Event (ms)
  - System Throughput (events/sec, MB/s)
  - Storage Overhead per Event (Bytes)
  - Quantum Resistance & Tamper Immunity Flags
"""

import os
import sys
import json
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch

sys.path.append(os.path.abspath('.'))

from src.detection.autoencoders import DenseAutoencoder
from src.response.policies import QLearningPolicy, RuleBasedPolicy
from src.response.environment import IoTDefenseEnv
from src.pipeline.integrated_framework import FrameworkConfig, IntegratedPipeline


SEEDS = [42, 123, 456, 789, 2026]


def run_ablation_experiments():
    print("=" * 60, flush=True)
    print("STARTING EXPERIMENT E7: INTEGRATED FRAMEWORK ABLATION STUDY", flush=True)
    print("=" * 60, flush=True)

    metrics_dir = 'results/metrics'
    tables_dir = 'results/tables'
    figures_dir = 'results/figures'
    paper_tables_dir = 'paper/tables'
    paper_figures_dir = 'paper/figures'

    for d in [metrics_dir, tables_dir, figures_dir, paper_tables_dir, paper_figures_dir]:
        os.makedirs(d, exist_ok=True)

    # Load dataset
    data_path = 'data/processed/recovery/recovery_processed.npz'
    assert os.path.exists(data_path), f"Data file missing at {data_path}"
    data = np.load(data_path, allow_pickle=True)
    X_train = data['X_train']
    X_val = data['X_val']
    X_sup = data['X_sup']
    y_sup = data['y_sup']
    X_test = data['X_test']
    y_test = data['y_test_binary']

    n_eval_samples = 5000  # Stream evaluation slice for end-to-end benchmark

    # Define Ablation Variants
    variants = [
        {
            'id': 'Base_Paper_Baseline',
            'name': 'Base Paper Architecture',
            'threshold_type': 'fixed_95',
            'mitigation_type': 'rule_based',
            'pqc_type': 'none',
            'integrity_type': 'salted_sha256',
            'quantum_safe': 'No (Vulnerable)',
            'tamper_immune': 'No (Unkeyed Hash)'
        },
        {
            'id': 'Ablation_NoAdaptive',
            'name': 'Ablation (-Adaptive Threshold)',
            'threshold_type': 'fixed_95',
            'mitigation_type': 'q_learning',
            'pqc_type': 'ml_kem_768',
            'integrity_type': 'blockchain_log',
            'quantum_safe': 'Yes (NIST ML-KEM)',
            'tamper_immune': 'Yes (Hash Chain)'
        },
        {
            'id': 'Ablation_NoRL',
            'name': 'Ablation (-RL Defense)',
            'threshold_type': 'excluded_ewma',
            'mitigation_type': 'rule_based',
            'pqc_type': 'ml_kem_768',
            'integrity_type': 'blockchain_log',
            'quantum_safe': 'Yes (NIST ML-KEM)',
            'tamper_immune': 'Yes (Hash Chain)'
        },
        {
            'id': 'Ablation_NoPQC',
            'name': 'Ablation (-PQC)',
            'threshold_type': 'excluded_ewma',
            'mitigation_type': 'q_learning',
            'pqc_type': 'none',
            'integrity_type': 'blockchain_log',
            'quantum_safe': 'No (Vulnerable)',
            'tamper_immune': 'Yes (Hash Chain)'
        },
        {
            'id': 'Ablation_NoBlockchain',
            'name': 'Ablation (-Blockchain Log)',
            'threshold_type': 'excluded_ewma',
            'mitigation_type': 'q_learning',
            'pqc_type': 'ml_kem_768',
            'integrity_type': 'salted_sha256',
            'quantum_safe': 'Yes (NIST ML-KEM)',
            'tamper_immune': 'No (Unkeyed Hash)'
        },
        {
            'id': 'Full_Proposed_Framework',
            'name': 'Full Proposed Framework',
            'threshold_type': 'excluded_ewma',
            'mitigation_type': 'q_learning',
            'pqc_type': 'ml_kem_768',
            'integrity_type': 'blockchain_log',
            'quantum_safe': 'Yes (NIST ML-KEM)',
            'tamper_immune': 'Yes (Hash Chain)'
        }
    ]

    raw_results = []

    for seed in SEEDS:
        print(f"\n--- Running Seed {seed} ---", flush=True)
        torch.manual_seed(seed)
        np.random.seed(seed)

        # Train baseline DenseAutoencoder on benign training split
        model = DenseAutoencoder(input_dim=39)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        criterion = torch.nn.MSELoss()
        train_sample = torch.tensor(X_train[:15000], dtype=torch.float32)
        
        model.train()
        for epoch in range(5):
            optimizer.zero_grad()
            rec = model(train_sample)
            loss = criterion(rec, train_sample)
            loss.backward()
            optimizer.step()
        model.eval()

        # Compute validation error distribution for adaptive & fixed thresholds
        with torch.no_grad():
            val_sample = torch.tensor(X_val[:5000], dtype=torch.float32)
            val_rec = model(val_sample)
            val_errs = torch.mean((val_sample - val_rec) ** 2, dim=1).numpy()
            
            sup_sample = torch.tensor(X_sup[:2000], dtype=torch.float32)
            sup_rec = model(sup_sample)
            sup_errs = torch.mean((sup_sample - sup_rec) ** 2, dim=1).numpy()

        tau_fixed = float(np.percentile(val_errs, 95))
        val_mu = float(np.mean(val_errs))
        val_var = float(np.var(val_errs))
        val_std = float(np.sqrt(val_var + 1e-8))

        sup_rates = X_sup[:2000, 3]
        err_quantiles = np.percentile(sup_errs, [50, 90, 98]).tolist()
        rate_quantiles = np.percentile(sup_rates, [50, 90, 98]).tolist()

        # Train un-contaminated Q-learning defense policy strictly on supervisory split X_sup
        q_policy = QLearningPolicy(n_states=64, n_actions=4, lr=0.1, gamma=0.95, epsilon=1.0)
        train_env = IoTDefenseEnv(sup_errs, sup_rates, y_sup[:2000], max_steps=2000, benign_block_penalty=-10.0)
        for ep in range(15):
            state_id, _ = train_env.reset()
            done = False
            while not done:
                act = q_policy.select_action(state_id)
                (next_sid, _), r, done, _ = train_env.step(act)
                q_policy.update(state_id, act, r, next_sid, done)
                state_id = next_sid

        # Stream slice for evaluation (un-contaminated held-out X_test)
        X_eval = X_test[:n_eval_samples]
        y_eval = y_test[:n_eval_samples]

        for v in variants:
            cfg = FrameworkConfig(
                name=v['id'],
                threshold_type=v['threshold_type'],
                mitigation_type=v['mitigation_type'],
                pqc_type=v['pqc_type'],
                integrity_type=v['integrity_type'],
                tau_fixed=tau_fixed,
                ewma_alpha=0.02,
                ewma_k=2.5,
                val_mu=val_mu,
                val_var=val_var,
                val_std=val_std,
                err_quantiles=err_quantiles,
                rate_quantiles=rate_quantiles
            )

            pipeline = IntegratedPipeline(cfg, model, q_policy=q_policy)

            latencies = []
            anomalies = []
            actions = []
            attacks_contained = 0
            benign_false_blocks = 0
            total_attacks = int(np.sum(y_eval))
            total_benign = len(y_eval) - total_attacks
            overheads = []

            for i in range(len(X_eval)):
                res = pipeline.process_event(X_eval[i], y_eval[i], timestep=i + 1)
                latencies.append(res.latency_ms)
                anomalies.append(res.is_anomaly)
                actions.append(res.action_taken)
                if res.was_attack_contained:
                    attacks_contained += 1
                if res.was_benign_falsely_blocked:
                    benign_false_blocks += 1
                overheads.append(res.integrity_overhead_bytes)

            anomalies = np.array(anomalies)
            tp = int(np.sum((anomalies == 1) & (y_eval == 1)))
            fp = int(np.sum((anomalies == 1) & (y_eval == 0)))
            tn = int(np.sum((anomalies == 0) & (y_eval == 0)))
            fn = int(np.sum((anomalies == 0) & (y_eval == 1)))

            precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
            recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
            f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
            fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0

            containment_rate = float(attacks_contained / total_attacks * 100.0) if total_attacks > 0 else 0.0
            false_block_rate = float(benign_false_blocks / total_benign * 100.0) if total_benign > 0 else 0.0
            availability = 100.0 - false_block_rate
            mean_latency = float(np.mean(latencies))
            throughput = float(1000.0 / mean_latency) if mean_latency > 0 else 0.0
            mean_overhead = float(np.mean(overheads))

            raw_results.append({
                'seed': seed,
                'variant_id': v['id'],
                'variant_name': v['name'],
                'threshold_type': v['threshold_type'],
                'mitigation_type': v['mitigation_type'],
                'pqc_type': v['pqc_type'],
                'integrity_type': v['integrity_type'],
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'fpr': fpr,
                'containment_rate_pct': containment_rate,
                'false_block_rate_pct': false_block_rate,
                'availability_pct': availability,
                'latency_mean_ms': mean_latency,
                'throughput_events_s': throughput,
                'storage_overhead_bytes': mean_overhead,
                'quantum_safe': v['quantum_safe'],
                'tamper_immune': v['tamper_immune']
            })

    df_raw = pd.DataFrame(raw_results)
    df_raw.to_csv(os.path.join(metrics_dir, 'e7_ablation_results.csv'), index=False)

    # Aggregate over seeds
    summary_list = []
    for v in variants:
        v_df = df_raw[df_raw['variant_id'] == v['id']]
        summary_list.append({
            'Variant': v['name'],
            'F1-Score': f"{v_df['f1_score'].mean():.4f} ± {v_df['f1_score'].std():.4f}",
            'Recall (%)': f"{v_df['recall'].mean() * 100:.2f}% ± {v_df['recall'].std() * 100:.2f}%",
            'Containment (%)': f"{v_df['containment_rate_pct'].mean():.2f}% ± {v_df['containment_rate_pct'].std():.2f}%",
            'False Block (%)': f"{v_df['false_block_rate_pct'].mean():.2f}% ± {v_df['false_block_rate_pct'].std():.2f}%",
            'Availability (%)': f"{v_df['availability_pct'].mean():.2f}% ± {v_df['availability_pct'].std():.2f}%",
            'Latency (ms)': f"{v_df['latency_mean_ms'].mean():.4f} ± {v_df['latency_mean_ms'].std():.4f}",
            'Throughput (ev/s)': f"{v_df['throughput_events_s'].mean():.1f} ± {v_df['throughput_events_s'].std():.1f}",
            'Overhead (B)': f"{int(round(v_df['storage_overhead_bytes'].mean()))} B",
            'Quantum Safe': v['quantum_safe'],
            'Audit Immutability': v['tamper_immune']
        })

    df_summary = pd.DataFrame(summary_list)
    df_summary.to_csv(os.path.join(metrics_dir, 'e7_ablation_summary.csv'), index=False)
    df_summary.to_csv(os.path.join(tables_dir, 'table7_ablation_comparison.csv'), index=False)

    with open(os.path.join(tables_dir, 'table7_ablation_comparison.md'), 'w') as f:
        f.write(df_summary.to_markdown(index=False))

    with open(os.path.join(paper_tables_dir, 'table7_ablation_comparison.tex'), 'w') as f:
        f.write(df_summary.to_latex(index=False))

    print("\n=== E7 INTEGRATED FRAMEWORK ABLATION SUMMARY ===", flush=True)
    print(df_summary.to_string(index=False), flush=True)

    # Generate Figure 7: Radar / Comparison Bar Chart
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    names = [v['name'] for v in variants]
    short_names = ['Base Paper', '-Adaptive', '-RL Defense', '-PQC', '-Blockchain', 'Full Proposed']
    x = np.arange(len(short_names))
    width = 0.35

    # Subplot 1: Detection F1 vs Service Availability
    f1_means = [df_raw[df_raw['variant_id'] == v['id']]['f1_score'].mean() * 100 for v in variants]
    avail_means = [df_raw[df_raw['variant_id'] == v['id']]['availability_pct'].mean() for v in variants]

    ax1.bar(x - width/2, f1_means, width, label='F1-Score (%)', color='#1f77b4')
    ax1.bar(x + width/2, avail_means, width, label='Service Availability (%)', color='#2ca02c')
    ax1.set_ylabel('Score (%)', fontweight='bold')
    ax1.set_title('A: Detection Accuracy vs Service Availability', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(short_names, rotation=25, ha='right')
    ax1.set_ylim(0, 110)
    ax1.legend(loc='lower left')

    # Subplot 2: End-to-End Latency Comparison
    lat_means = [df_raw[df_raw['variant_id'] == v['id']]['latency_mean_ms'].mean() for v in variants]
    colors = ['#7f7f7f', '#aec7e8', '#ff7f0e', '#2ca02c', '#98df8a', '#d62728']

    ax2.bar(x, lat_means, width=0.55, color=colors)
    ax2.set_ylabel('End-to-End Latency per Event (ms)', fontweight='bold')
    ax2.set_title('B: End-to-End Processing Latency by Architecture', fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(short_names, rotation=25, ha='right')

    plt.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'figure7_ablation_comparison.png'), dpi=300)
    fig.savefig(os.path.join(paper_figures_dir, 'figure7_ablation_comparison.png'), dpi=300)
    plt.close()

    print("\nExperiment E7 executed and artifacts saved successfully!", flush=True)


if __name__ == '__main__':
    run_ablation_experiments()
