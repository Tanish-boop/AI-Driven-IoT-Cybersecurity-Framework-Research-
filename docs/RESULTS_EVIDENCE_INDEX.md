# Results Evidence Index & Provenance Mapping

**Repository**: `c:\Users\hp\OneDrive\Desktop\Research Experiments`  
**Dataset**: CICIoT2023 Recovery Partition (`data/processed/recovery/recovery_processed.npz`)  
**Date**: 2026-10-09  

---

## Metric Mapping Matrix

Every reported number across the manuscript, tables, and documentation is mapped directly to its underlying empirical artifact and exact line item below.

| Claim / Reported Metric | Reported Value | Primary Source Artifact Path | Row / Column / Key in Source Artifact | Verification Method & Script | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Dense-AE Fixed 95th F1** | $0.8854 \pm 0.0013$ | `results/metrics/full_benchmark_summary.csv` | Line 3, Column `F1-Score` | `python scripts/audit_and_recompute.py` | `VERIFIED FROM CODE` |
| **Dense-AE Fixed 95th Precision** | $0.9893 \pm 0.0003$ | `results/metrics/full_benchmark_summary.csv` | Line 3, Column `Precision` | `python scripts/audit_and_recompute.py` | `VERIFIED FROM CODE` |
| **Dense-AE Fixed 95th Recall** | $0.8013 \pm 0.0022$ | `results/metrics/full_benchmark_summary.csv` | Line 3, Column `Recall` | `python scripts/audit_and_recompute.py` | `VERIFIED FROM CODE` |
| **Dense-AE Fixed 95th FPR** | $0.0493 \pm 0.0013$ | `results/metrics/full_benchmark_summary.csv` | Line 3, Column `FPR` | `python scripts/audit_and_recompute.py` | `VERIFIED FROM CODE` |
| **Dense-AE Excluded EWMA F1** | $0.9014 \pm 0.0018$ | `results/metrics/full_benchmark_summary.csv` | Line 2, Column `F1-Score` | `python scripts/audit_and_recompute.py` | `VERIFIED FROM CODE` |
| **Dense-AE Excluded EWMA Recall** | $0.8401 \pm 0.0023$ | `results/metrics/full_benchmark_summary.csv` | Line 2, Column `Recall` | `python scripts/audit_and_recompute.py` | `VERIFIED FROM CODE` |
| **Dense-AE UnGuarded EWMA F1** | $0.0003 \pm 0.0001$ | `results/metrics/full_benchmark_summary.csv` | Line 6, Column `F1-Score` | `python scripts/audit_and_recompute.py` | `VERIFIED FROM CODE` |
| **Dense-AE Fixed 95th 2.0x Stress FPR** | $0.2733 \pm 0.0152$ | `results/metrics/full_benchmark_summary.csv` | Line 10, Column `FPR` | `python scripts/audit_and_recompute.py` | `VERIFIED FROM CODE` |
| **XGBoost Oracle F1** | $0.9269 \pm 0.0004$ | `results/metrics/full_benchmark_summary.csv` | Line 8, Column `F1-Score` | `python scripts/audit_and_recompute.py` | `VERIFIED FROM CODE` |
| **Wilcoxon Signed-Rank Test** | $W = 0.0, p = 0.0625$ | `results/metrics/statistical_tests.json` | Key `dense_ae_fixed95_vs_fixed99` | `python scripts/run_full_benchmark.py` | `RECOMPUTED FROM SAVED CSV` |
| **Corrected DQN Attack Containment** | $71.20\% \pm 0.05\%$ | `results/metrics/e4_policy_summary_corrected.csv` | Line 2, Column `Attack Containment (%)` | `tests/test_e4_uncontaminated.py` | `VERIFIED FROM CODE` |
| **Corrected DQN False Block Rate** | $0.77\% \pm 0.43\%$ | `results/metrics/e4_policy_summary_corrected.csv` | Line 2, Column `False Block Rate (%)` | `tests/test_e4_uncontaminated.py` | `VERIFIED FROM CODE` |
| **Corrected Q-Learning False Block** | $0.00\% \pm 0.00\%$ | `results/metrics/e4_policy_summary_corrected.csv` | Line 3, Column `False Block Rate (%)` | `tests/test_e4_uncontaminated.py` | `VERIFIED FROM CODE` |
| **ML-KEM-768 Total KEM Latency** | $0.4293$ ms | `results/metrics/e5_summary.csv` | Line 7, Column `total_kem_mean_ms` | `tests/test_e5_crypto.py` | `VERIFIED FROM CODE` |
| **ML-KEM-768 First-Msg Setup** | $0.4754$ ms | `results/metrics/e5_summary.csv` | Line 7, Column `first_msg_mean_ms` | `tests/test_e5_crypto.py` | `VERIFIED FROM CODE` |
| **ML-KEM Tamper Rejection** | 100% Pass (`InvalidTag`) | `results/metrics/e5_crypto_environment.json` | Tamper output log | `tests/test_e5_crypto.py` | `VERIFIED FROM CODE` |
| **Salted SHA-256 Creation (1KiB)** | $0.0279$ ms | `results/metrics/e6_summary.csv` | Line 8, Column `create_mean_ms` | `tests/test_e6_integrity.py` | `VERIFIED FROM CODE` |
| **HMAC-SHA-256 Creation (1KiB)** | $0.0332$ ms | `results/metrics/e6_summary.csv` | Line 9, Column `create_mean_ms` | `tests/test_e6_integrity.py` | `VERIFIED FROM CODE` |
| **HMAC-SHA-256 Storage Overhead** | 171 Bytes | `results/metrics/e6_summary.csv` | Line 9, Column `overhead_bytes` | `tests/test_e6_integrity.py` | `VERIFIED FROM CODE` |
| **Blockchain Single Append (1KiB)** | $0.0409$ ms | `results/metrics/e6_summary.csv` | Line 10, Column `create_mean_ms` | `tests/test_e6_integrity.py` | `VERIFIED FROM CODE` |
| **Blockchain Full Verify (N=2000)** | $29.85$ ms | `results/metrics/e6_scaling_summary.csv` | Line 5, Column `full_chain_verify_total_ms` | `tests/test_e6_integrity.py` | `VERIFIED FROM CODE` |
| **E6 Tamper Detection Rate** | 100% (6 attack vectors) | `docs/e6_validation_report.md` | Section 3 Matrix | `tests/test_e6_integrity.py` | `VERIFIED FROM CODE` |
| **Full Framework Integrated F1** | $0.8968 \pm 0.0013$ | `results/metrics/e7_ablation_summary.csv` | Line 7, Column `F1-Score` | `python scripts/run_e7_ablation_experiment.py` | `VERIFIED FROM CODE` |
| **Full Framework Attack Containment** | $80.65\% \pm 3.16\%$ | `results/metrics/e7_ablation_summary.csv` | Line 7, Column `Containment (%)` | `python scripts/run_e7_ablation_experiment.py` | `VERIFIED FROM CODE` |
| **Full Framework False Block Rate** | $7.39\% \pm 2.51\%$ | `results/metrics/e7_ablation_summary.csv` | Line 7, Column `False Block (%)` | `python scripts/run_e7_ablation_experiment.py` | `VERIFIED FROM CODE` |
| **Full Framework Pipeline Latency** | $0.3781 \pm 0.0225$ ms | `results/metrics/e7_ablation_summary.csv` | Line 7, Column `Latency (ms)` | `python scripts/run_e7_ablation_experiment.py` | `VERIFIED FROM CODE` |
| **Full Framework System Throughput** | $2652.4 \pm 154.8$ ev/s | `results/metrics/e7_ablation_summary.csv` | Line 7, Column `Throughput (ev/s)` | `python scripts/run_e7_ablation_experiment.py` | `VERIFIED FROM CODE` |
| **Full Framework Storage Overhead** | 321 Bytes | `results/metrics/e7_ablation_summary.csv` | Line 7, Column `Overhead (B)` | `python scripts/run_e7_ablation_experiment.py` | `VERIFIED FROM CODE` |

---

## Raw Artifact File Manifest

1. `results/metrics/full_benchmark_results.csv`: Contains per-seed raw metrics (Seeds 42, 123, 456, 789, 2026) for E1, E2, E3, E8.
2. `results/metrics/full_benchmark_summary.csv`: Contains mean ± std aggregate metrics for E1, E2, E3, E8.
3. `results/metrics/recomputed_metrics.csv`: Contains exact confusion matrix breakdown (TP, FP, TN, FN) for Seed 42.
4. `results/metrics/e4_policy_results_historical.csv`: Historical contaminated E4 seed results.
5. `results/metrics/e4_policy_results_corrected.csv`: Corrected un-contaminated E4 seed results.
6. `results/metrics/e4_policy_summary_corrected.csv`: Corrected un-contaminated E4 mean ± std summary.
7. `results/metrics/e4_reward_sensitivity.csv`: Q-learning penalty sensitivity across $C_{\text{benign\_block}} \in [-10, -25, -50, -100]$.
8. `results/metrics/e5_raw_results.csv`: Raw 100-trial microbenchmark outputs across ML-KEM-512/768/1024 and 4 payload sizes.
9. `results/metrics/e5_summary.csv`: Summary timing, artifact sizes, and throughput metrics for E5.
10. `results/metrics/statistical_tests.json`: Wilcoxon signed-rank statistical test outcomes.
11. `results/metrics/e6_raw_results.csv`: Raw repeated-trial microbenchmark outputs for E6 integrity mechanisms.
12. `results/metrics/e6_summary.csv`: Aggregated timing, throughput, and storage overhead metrics across payload sizes for E6.
13. `results/metrics/e6_scaling_summary.csv`: Blockchain audit log scaling metrics across chain lengths (N = 100, 500, 1000, 2000).
14. `results/metrics/e6_integrity_environment.json`: Hardware/software environment and provider metadata for E6.
15. `results/metrics/e7_ablation_results.csv`: Raw 5-seed metrics across all 6 ablation variants for E7.
16. `results/metrics/e7_ablation_summary.csv`: Aggregated mean ± std metrics for E7 ablation benchmark.
17. `results/tables/table7_ablation_comparison.md`: Formatted Markdown comparative ablation table for E7.
18. `paper/tables/table7_ablation_comparison.tex`: Publication LaTeX table for E7 ablation benchmark.
19. `results/figures/figure7_ablation_comparison.png`: Multi-panel comparison figure visualizing E7 ablation metrics.
