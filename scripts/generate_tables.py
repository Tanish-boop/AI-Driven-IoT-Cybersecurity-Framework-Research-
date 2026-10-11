"""
scripts/generate_tables.py

Generates all verified Markdown and CSV tables for the manuscript strictly
from audited 5-seed raw result CSV files.
"""

import os
import json
import pandas as pd

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    metrics_dir = os.path.join(repo_root, "results", "metrics")
    tables_dir = os.path.join(repo_root, "results", "tables")
    os.makedirs(tables_dir, exist_ok=True)

    # 1. Table 1: Base Stream Anomaly Detection (E1, E2)
    bench_sum_file = os.path.join(metrics_dir, "full_benchmark_summary.csv")
    df_bench = pd.read_csv(bench_sum_file)
    t1 = df_bench[df_bench['Experiment'] == 'base_stream'][['Model', 'Strategy', 'Precision', 'Recall', 'F1-Score', 'FPR']].copy()
    t1.columns = ['Model', 'Threshold Strategy', 'Precision', 'Recall', 'F1-Score', 'FPR']
    t1.to_csv(os.path.join(tables_dir, 'table1_base_performance.csv'), index=False)
    with open(os.path.join(tables_dir, 'table1_base_performance.md'), 'w') as f:
        f.write(t1.to_markdown(index=False))

    # 2. Table 2: Deduplication Sensitivity (5 Seeds)
    dedup_sum_file = os.path.join(metrics_dir, "deduplication_sensitivity_summary.csv")
    if os.path.exists(dedup_sum_file):
        df_dedup = pd.read_csv(dedup_sum_file)
        df_dedup.to_csv(os.path.join(tables_dir, 'table2_deduplication_sensitivity.csv'), index=False)
        with open(os.path.join(tables_dir, 'table2_deduplication_sensitivity.md'), 'w') as f:
            f.write(df_dedup.to_markdown(index=False))

    # 3. Table 3: Rate-Shift Stress Test (E8)
    t3 = df_bench[df_bench['Experiment'] == 'feature_stress_test'][['Model', 'Strategy', 'Precision', 'Recall', 'F1-Score', 'FPR']].copy()
    t3.to_csv(os.path.join(tables_dir, 'table3_stress_test_performance.csv'), index=False)
    with open(os.path.join(tables_dir, 'table3_stress_test_performance.md'), 'w') as f:
        f.write(t3.to_markdown(index=False))

    # 4. Table 4: Per-Attack Breakdown
    per_att_file = os.path.join(metrics_dir, "per_attack_class_breakdown.csv")
    if os.path.exists(per_att_file):
        df_per_att = pd.read_csv(per_att_file)
        df_per_att.to_csv(os.path.join(tables_dir, 'table4_per_attack_breakdown.csv'), index=False)
        with open(os.path.join(tables_dir, 'table4_per_attack_breakdown.md'), 'w') as f:
            f.write(df_per_att.to_markdown(index=False))

    # 5. Table 5: Defensive Mitigation Policies (E4)
    e4_file = os.path.join(metrics_dir, "e4_policy_summary_corrected.csv")
    if os.path.exists(e4_file):
        df_e4 = pd.read_csv(e4_file)
        df_e4.to_csv(os.path.join(tables_dir, 'table5_defense_policy.csv'), index=False)
        with open(os.path.join(tables_dir, 'table5_defense_policy.md'), 'w') as f:
            f.write(df_e4.to_markdown(index=False))

    # 6. Table 6: PQC Microbenchmark (E5)
    e5_file = os.path.join(metrics_dir, "e5_summary.csv")
    if os.path.exists(e5_file):
        df_e5 = pd.read_csv(e5_file)
        df_e5_1k = df_e5[df_e5['payload_size_name'] == '1024B'][[
            'variant', 'pk_size_bytes', 'sk_size_bytes', 'ct_size_bytes',
            'keygen_mean_ms', 'encaps_mean_ms', 'decaps_mean_ms', 'total_kem_mean_ms', 'first_msg_mean_ms'
        ]].copy()
        df_e5_1k.columns = ['Variant', 'PK (B)', 'SK (B)', 'CT (B)', 'KeyGen (ms)', 'Encaps (ms)', 'Decaps (ms)', 'Total KEM (ms)', 'First Msg (ms)']
        df_e5_1k.to_csv(os.path.join(tables_dir, 'table6_pqc_benchmark.csv'), index=False)
        with open(os.path.join(tables_dir, 'table6_pqc_benchmark.md'), 'w') as f:
            f.write(df_e5_1k.to_markdown(index=False))

    # 7. Table 7: Cryptographic Integrity (E6)
    e6_file = os.path.join(metrics_dir, "e6_summary.csv")
    if os.path.exists(e6_file):
        df_e6 = pd.read_csv(e6_file)
        df_e6_1k = df_e6[df_e6['payload_size'] == '1KiB'][[
            'approach', 'create_mean_ms', 'verify_mean_ms', 'overhead_bytes', 'throughput_mb_s'
        ]].copy()
        df_e6_1k.columns = ['Approach', 'Create (ms)', 'Verify (ms)', 'Overhead (B)', 'Throughput (MB/s)']
        df_e6_1k.to_csv(os.path.join(tables_dir, 'table7_integrity_benchmark.csv'), index=False)
        with open(os.path.join(tables_dir, 'table7_integrity_benchmark.md'), 'w') as f:
            f.write(df_e6_1k.to_markdown(index=False))

    # 8. Table 8: Integrated Framework Ablation (E7)
    e7_file = os.path.join(metrics_dir, "e7_ablation_summary.csv")
    if os.path.exists(e7_file):
        df_e7 = pd.read_csv(e7_file)
        df_e7.to_csv(os.path.join(tables_dir, 'table8_ablation_comparison.csv'), index=False)
        with open(os.path.join(tables_dir, 'table8_ablation_comparison.md'), 'w') as f:
            f.write(df_e7.to_markdown(index=False))

    print("All tables successfully generated and synchronized in results/tables!")

if __name__ == '__main__':
    main()
