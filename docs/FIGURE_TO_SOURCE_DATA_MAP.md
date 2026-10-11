# Figure-to-Source-Data Traceability Matrix

This document provides complete, transparent mapping between every figure and table published in the manuscript and its underlying raw experimental data artifacts.

---

## 1. Publication Figures Mapping

| Figure Number | Caption / Description | Generating Script | Primary Source Data File | Plotted Metrics & Data Columns | Verification Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Figure 1** (Fig 0 in code) | Five-Stage AI-Driven Adaptive Cybersecurity Framework Architecture | `scripts/generate_architecture_figure.py` | Conceptual / Architectural Specification | Modular pipeline blocks (Ingestion, Dense-AE, RL Defense, PQC, Hash-Chain) | **VERIFIED** | Conceptual architectural diagram; no experimental data plotted. |
| **Figure 2** (Fig 1 in code) | Dense-AE Performance and FPR Across Threshold Strategies (5 Seeds) | `scripts/generate_all_verified_figures.py` | `results/metrics/full_benchmark_results.csv` | `f1_score`, `fpr` across `Fixed_95`, `Fixed_99`, `UnGuarded_EWMA`, `Excluded_EWMA`, `Guarded_EWMA` | **VERIFIED** | Evaluates Dense-AE across 5 random seeds (42, 123, 456, 789, 2026). Legacy LSTM/GRU removed. |
| **Figure 3** (Fig 2 in code) | False Positive Rate Explosion under Synthetic Rate Scaling (E8) | `scripts/generate_all_verified_figures.py` | `results/metrics/full_benchmark_results.csv` | `fpr`, `f1_score` across `Fixed_95` at 1.0×, 1.5×, 2.0× scaling | **VERIFIED** | Plotted exclusively for Dense-AE Fixed 95th; no adaptive models implied under E8 scaling. |
| **Figure 4** (Fig 3 in code) | Dense-AE Detection Recall Breakdown Across 7 Attack Categories | `scripts/generate_all_verified_figures.py` | `results/metrics/per_attack_class_breakdown.csv` | `Fixed_95_Recall`, `Excluded_EWMA_Recall` per attack class | **VERIFIED** | Computed from true test set class labels (`data/processed/recovery/recovery_processed.npz`). |
| **Figure 5** (Fig 4 in code) | Cumulative Reward and Containment vs. Disruption Trade-off (E4) | `scripts/generate_all_verified_figures.py` | `results/metrics/e4_policy_summary_corrected.csv` | `Cumulative Reward`, `Attack Containment (%)`, `False Block Rate (%)` for Rule-Based, Q-Learning, DQN | **VERIFIED** | Evaluated under strict un-contaminated split isolation ($X_{\text{sup}}$ training, $X_{\text{test}}$ evaluation). |
| **Figure 6** (Fig 5 in code) | Post-Quantum Key Encapsulation Latency and Artifact Footprints (E5) | `scripts/generate_all_verified_figures.py` | `results/metrics/e5_summary.csv` | `keygen_mean_ms`, `encaps_mean_ms`, `decaps_mean_ms`, `pk_size_bytes`, `ct_size_bytes` for ML-KEM-512/768/1024 | **VERIFIED** | PQC microbenchmarks on AMD64 CPU for 1024-byte payload. |
| **Figure 7** (Fig 6 in code) | Processing Latency and Throughput of Integrity Architectures (E6) | `scripts/generate_all_verified_figures.py` | `results/metrics/e6_summary.csv` | `create_mean_ms`, `verify_mean_ms`, `throughput_mb_s` for 1 KiB payload | **VERIFIED** | Evaluates Salted SHA-256, HMAC-SHA-256, and Hash-Chain Log. |
| **Figure 8** (Fig 7 in code) | Multi-Metric Ablation Comparison Across All 6 Configurations (E7) | `scripts/generate_all_verified_figures.py` | `results/metrics/e7_ablation_summary.csv` | Detection F1, Containment (%), and End-to-End Latency (ms) | **VERIFIED** | Latency bars (0.81, 0.86, 0.97, 0.91, 1.21, 0.96 ms) exactly match Table VIII raw data. |

---

## 2. Publication Tables Mapping

| Table Number | Table Title | Primary Source Data File | Plotted Configurations & Metrics | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **Table I** | Base Test Stream Anomaly Detection Benchmark (5 Seeds) | `results/metrics/full_benchmark_summary.csv` | Precision, Recall, F1, FPR, PR-AUC, ROC-AUC across Dense-AE strategies, Isolation Forest, XGBoost Oracle | **VERIFIED** |
| **Table II** | Deduplication Sensitivity Analysis (5 Seeds) | `results/metrics/deduplication_sensitivity_summary.csv` | Full F1 vs. Clean F1 ($\Delta$), Full FPR vs. Clean FPR across 5 seeds | **VERIFIED** |
| **Table III** | Rate Feature Stress Test Performance (E8) | `results/metrics/full_benchmark_summary.csv` | Fixed 95th Percentile at 1.0×, 1.5×, 2.0× scaling | **VERIFIED** |
| **Table IV** | Dense-AE Detection Recall Across 7 Attack Classes | `results/metrics/per_attack_class_breakdown.csv` | Per-class sample counts and recall for Fixed 95th vs. Excluded EWMA | **VERIFIED** |
| **Table V** | Defensive Mitigation Policy Performance (E4) | `results/metrics/e4_policy_summary_corrected.csv` | Reward, Containment, False Block, Latency across Scenarios 1 & 2 | **VERIFIED** |
| **Table VI** | NIST FIPS 203 PQC Microbenchmark (1024-Byte Payload) | `results/metrics/e5_summary.csv` | PK, SK, CT, Total KEM, First-Msg setup for ML-KEM-512/768/1024 | **VERIFIED** |
| **Table VII** | Cryptographic Integrity Verification Microbenchmarks (1 KiB) | `results/metrics/e6_summary.csv` | Create latency, Verify latency, Overhead bytes, Throughput (MB/s) | **VERIFIED** |
| **Table VIII** | Full Framework Integrated Ablation Study (5 Seeds, E7) | `results/metrics/e7_ablation_summary.csv` | F1, Recall, Containment, False Block, Availability, Latency, Throughput, Overhead | **VERIFIED** |
| **Table IX** | Hypothesis Testing and Effect Size (5 Seeds) | `results/metrics/extended_statistical_tests.json` | Paired $t$, adjusted $p$-values, Cohen's $d$, 95% Confidence Intervals | **VERIFIED** |

---

## 3. Discrepancy Reconciliation Summary

1. **Figure 2 (Threshold Strategies)**:
   - Previous legacy plot erroneously contained LSTM-AE and GRU-AE bars.
   - **Resolution**: Replaced with `figure1_threshold_comparison.png`, plotting only the genuine 5-seed Dense-AE models evaluated in E1/E2.
2. **Figure 3 (E8 Rate Scaling)**:
   - Previous legacy plot erroneously included Excluded EWMA in the E8 legend.
   - **Resolution**: Replaced with `figure2_rate_stress_test.png`, plotting exclusively the Fixed 95th Percentile under 1.0×, 1.5×, and 2.0× scaling as executed in E8.
3. **Figure 4 & Table IV (Attack-Class Recall)**:
   - Previous draft text cited unsupported Reconnaissance and Web-based recall figures.
   - **Resolution**: Recomputed recall directly from test-set predictions and ground-truth classes. Exact recall: DDoS: 100.0%, DoS: 100.0%, Mirai: 100.0%, BruteForce: 42.80% (Fixed 95th) vs. 55.54% (Excluded EWMA), Recon: 38.18% vs. 49.19%, Spoofing: 23.38% vs. 39.15%, Web-based: 20.42% vs. 37.88%.
4. **Figure 8 & Table VIII (E7 Latency Mismatch)**:
   - Previous manuscript text and table reported preliminary latencies (0.3781 ms), while Figure 8 plotted 0.81–1.21 ms.
   - **Resolution**: Harmonized Table VIII and Figure 8 to the audited 5-seed summary: Baseline: $0.8103 \pm 0.5338$ ms, -Adaptive: $0.8579 \pm 0.5443$ ms, -RL: $0.9737 \pm 0.7128$ ms, -PQC: $0.9103 \pm 0.5070$ ms, -Hash Chain: $1.2107 \pm 0.7004$ ms, Full Proposed: $0.9626 \pm 0.6304$ ms.
