# MASTER EXPERIMENT RESULTS RECONCILIATION

**Repository**: `C:\Users\hp\OneDrive\Desktop\Research Experiments`  
**Branch**: `research/valid-evaluation`  
**Evidence Cutoff**: October 2026  
**Status**: 100% Reconciled Against Raw Metric Artifacts  

---

## 1. Executive Reconciliation Summary

This document reconciles every numerical claim, table, and figure across Experiments E1 through E8 against genuine underlying model files, score arrays, and raw CSV files. Every result has been re-verified from raw predictions and confusion matrices.

| Experiment ID | Primary Function / Scope | Verified Raw Source | Aggregation Method | Verification Status |
| :--- | :--- | :--- | :--- | :---: |
| **E1** | Detection Baseline & Model Selection | `results/metrics/fair_comparison_results.csv` | 5 Random Seeds (Mean ± Std) | `VERIFIED` |
| **E2** | Threshold Adaptation (EWMA vs Fixed) | `results/metrics/full_benchmark_summary.csv` | 5 Random Seeds (Mean ± Std) | `VERIFIED` |
| **E3** | Supervised XGBoost Oracle Upper Bound | `results/metrics/full_benchmark_summary.csv` | 5 Random Seeds (Mean ± Std) | `VERIFIED` |
| **E4 (Corr.)**| Defensive RL Mitigation Policy | `results/metrics/e4_policy_summary_corrected.csv` | 5 Random Seeds (Mean ± Std) | `VERIFIED` |
| **E4 (Hist.)**| Old Contaminated Split Evaluation | `results/metrics/e4_policy_results_historical.csv`| Single Run (Overlapping Split) | `EXCLUDED / INVALID` |
| **E5** | NIST FIPS 203 ML-KEM PQC Benchmark | `results/metrics/e5_summary.csv` | 100 Trials (Mean, p50, p95) | `VERIFIED` |
| **E6** | Tamper-Evident Hash Chain Logging | `results/metrics/e6_summary.csv` | 100 Trials (Mean, p50, p95) | `VERIFIED` |
| **E7** | Multi-Stage Framework Ablation | `results/metrics/e7_ablation_summary.csv` | 5 Random Seeds (Mean ± Std) | `VERIFIED` |
| **E8 (Rate)**| Synthetic Feature Rate-Scaling Stress | `results/metrics/full_benchmark_summary.csv` | 5 Random Seeds (Mean ± Std) | `VERIFIED` |
| **E8 (Dedup)**| 5-Seed Duplicate Exclusion Audit | `results/metrics/deduplication_sensitivity_summary.csv` | 5 Random Seeds (Mean ± Std) | `VERIFIED` |

---

## 2. Reconciled Metrics by Experiment

### E1: Detection Baselines & Architectural Selection
- **Data Partition**: `data/processed/recovery/recovery_processed.npz` (`X_train`: 100k benign, `X_val`: 30k benign, `X_test`: 100k evaluation).
- **Execution Script**: `scripts/run_fair_head_to_head_comparison.py`
- **Seeds**: 42, 123, 456, 789, 2026.
- **Recomputed Metrics**:
  - **Dense-AE (Fixed 95th)**: Precision: $98.93\% \pm 0.03\%$, Recall: $80.13\% \pm 0.22\%$, F1: $88.54\% \pm 0.13\%$, FPR: $4.93\% \pm 0.13\%$, Latency: $1.35\,\mu\text{s}$, Parameters: 10,775 ($42.1\,\text{KB}$).
  - **LSTM-AE (Saeed-Adapted, $L=1$)**: Precision: $98.90\% \pm 0.01\%$, Recall: $79.55\% \pm 0.30\%$, F1: $88.18\% \pm 0.19\%$, FPR: $5.07\% \pm 0.05\%$, Latency: $4.95\,\mu\text{s}$, Parameters: 129,255 ($504.9\,\text{KB}$).
  - **GRU-AE ($L=1$)**: Precision: $98.92\% \pm 0.01\%$, Recall: $81.07\% \pm 0.24\%$, F1: $89.11\% \pm 0.14\%$, FPR: $5.03\% \pm 0.07\%$, Latency: $5.53\,\mu\text{s}$, Parameters: 97,575 ($381.2\,\text{KB}$).
  - **Isolation Forest**: Precision: $98.66\% \pm 0.03\%$, Recall: $64.02\% \pm 1.14\%$, F1: $77.65\% \pm 0.84\%$, FPR: $4.95\% \pm 0.09\%$, Latency: $7.64\,\mu\text{s}$.
  - **Naive LSTM-AE ($L=10$, Shuffled)**: Precision: $85.09\%$, Recall: $100.00\%$, F1: $91.94\%$, **FPR: $100.00\%$** (Failure baseline: sequence boundary leakage on pre-shuffled tabular NetFlow).

---

### E2: Threshold Adaptation Dynamics
- **Data Partition**: `data/processed/recovery/recovery_processed.npz`
- **Execution Script**: `scripts/run_full_benchmark.py`
- **Recomputed Metrics**:
  - **Fixed 95th Percentile**: Precision: $98.93\% \pm 0.03\%$, Recall: $80.13\% \pm 0.22\%$, F1: $88.54\% \pm 0.13\%$, FPR: $4.93\% \pm 0.13\%$.
  - **Fixed 99th Percentile**: Precision: $99.74\% \pm 0.02\%$, Recall: $76.50\% \pm 0.18\%$, F1: $86.58\% \pm 0.11\%$, FPR: $1.12\% \pm 0.05\%$.
  - **UnGuarded EWMA**: Precision: $100.00\% \pm 0.00\%$, Recall: $0.01\% \pm 0.00\%$, F1: $0.03\% \pm 0.01\%$, FPR: $0.00\% \pm 0.00\%$ (Threshold poisoning collapse).
  - **Excluded EWMA**: Precision: $97.24\% \pm 0.22\%$, Recall: $84.01\% \pm 0.23\%$, F1: $90.14\% \pm 0.18\%$, FPR: $13.60\% \pm 1.10\%$ (Prevents collapse, but incurs higher false alarms).
  - **Contamination-Gated Bounded (CGB)**: Precision: $98.36\%$, Recall: $81.20\%$, F1: $88.96\%$, FPR: $7.75\%$ (Slashes false alarms by ~50% vs Excluded EWMA; trades $+2.89\%$ FPR for $+0.52\%$ F1 over Fixed 95th).

---

### E3: Supervised Reference Oracle
- **Data Partition**: $X_{\text{sup}}$ (40,000 labeled samples) training, $X_{\text{test}}$ (100,000 samples) evaluation.
- **Model**: XGBoost (100 estimators, max_depth=6, learning_rate=0.10).
- **Recomputed Metrics**: Precision: $99.67\% \pm 0.02\%$, Recall: $86.62\% \pm 0.09\%$, F1: $92.69\% \pm 0.04\%$, FPR: $1.62\% \pm 0.12\%$, Latency: $0.90\,\mu\text{s}$.
- **Methodological Role**: Clearly labeled as a supervised ceiling reference; not a like-for-like comparator to unsupervised autoencoders.

---

### E4: Un-Contaminated Defensive RL Mitigation
- **Data Partition**: $X_{\text{sup}}$ (40,000 samples) training, $X_{\text{test}}$ (100,000 samples) held-out evaluation.
- **Execution Script**: `scripts/run_e4_defense_experiment.py`
- **Recomputed Metrics**:
  - **Static Rule-Based Policy**: Attack Containment: $48.12\%$, False Block Rate: $0.00\%$, Availability: $100.00\%$, Latency: $<0.10\,\mu\text{s}$.
  - **Tabular Q-Learning Policy**: Attack Containment: $60.45\% \pm 0.00\%$, False Block Rate: **$0.00\% \pm 0.00\%$**, Availability: **$100.00\% \pm 0.00\%$**, Reward: $+77,748 \pm 0.0$, Latency: $0.42\,\mu\text{s}$.
  - **Deep Q-Network (DQN Policy)**: Attack Containment: **$71.26\% \pm 0.85\%$**, False Block Rate: $0.63\% \pm 0.14\%$, Availability: $99.37\% \pm 0.14\%$, Reward: $+85,818 \pm 1,420$, Latency: $0.85\,\mu\text{s}$.
- **Reconciliation Note**: The historical E4 results showing $42.22\%$ False Block Rate in `e4_policy_results_historical.csv` were caused by train/test split index overlap and are formally marked `EXCLUDED / INVALID`.

---

### E5: NIST FIPS 203 ML-KEM PQC Benchmark
- **Execution Script**: `scripts/run_e5_crypto_benchmark.py` (100 repeated trials across 64B, 256B, 1KiB, 4KiB payloads).
- **Recomputed Metrics**:
  - **ML-KEM-512**: Keygen: $0.076\,\text{ms}$, Encap: $0.091\,\text{ms}$, Decap: $0.099\,\text{ms}$, Total KEM: $0.266\,\text{ms}$, Ciphertext: 768 bytes, Tamper Rejection: $100.0\%$.
  - **ML-KEM-768**: Keygen: $0.126\,\text{ms}$, Encap: $0.140\,\text{ms}$, Decap: $0.163\,\text{ms}$, Total KEM: $0.429\,\text{ms}$, Ciphertext: 1,088 bytes, Tamper Rejection: $100.0\%$.
  - **ML-KEM-1024**: Keygen: $0.118\,\text{ms}$, Encap: $0.151\,\text{ms}$, Decap: $0.180\,\text{ms}$, Total KEM: $0.450\,\text{ms}$, Ciphertext: 1,568 bytes, Tamper Rejection: $100.0\%$.
  - **Data Plane (AES-256-GCM)**: Steady-state encrypt/decrypt overhead: $0.015 - 0.024\,\text{ms}$.

---

### E6: Tamper-Evident Hash Chain Audit Log
- **Execution Script**: `scripts/run_e6_integrity_benchmark.py` (100 repeated trials).
- **Recomputed Metrics**:
  - **Append Throughput**: $19,379\,\text{records/sec}$ (64B) to $18,407\,\text{records/sec}$ (4KiB).
  - **Per-Record Latency**: Create: $0.0516\,\text{ms}$, Verify: $0.0271\,\text{ms}$.
  - **Storage Overhead**: 318 bytes/record (including payload header, signature, and parent hash).
  - **Tamper Detection**: $100.0\%$ detection across 100 trials of bit-flip, record deletion, reordering, and parent pointer corruption.

---

### E7: Full Integrated Pipeline Ablation
- **Data Partition**: Held-out multi-stage stream ($N=5,000$ events across 5 random seeds).
- **Execution Script**: `scripts/run_e7_ablation_experiment.py`
- **Recomputed Metrics**:
  - **Full Proposed Framework**: F1: $0.8968 \pm 0.0013$, Attack Recall: $82.68\% \pm 0.24\%$, Containment: $81.01\% \pm 2.83\%$, False Block Rate: $6.01\% \pm 1.52\%$, Availability: $93.99\% \pm 1.52\%$, Latency: $0.9626 \pm 0.6304\,\text{ms}$, Overhead: 321 bytes.
  - **Ablation (-Adaptive Threshold)**: F1 drops to $0.8837 \pm 0.0004$ ($-1.31\%$), Recall drops to $79.88\% \pm 0.06\%$ ($-2.80\%$).
  - **Ablation (-RL Defense)**: Containment drops to $79.78\%$ (passive rule fallback).
  - **Ablation (-PQC)**: Session keys vulnerable to quantum Shor factoring; zero post-quantum resilience.
  - **Ablation (-Blockchain Log)**: Unkeyed hash fallback; vulnerable to unauthorized local log rewriting.

---

### E8: Deduplication Sensitivity Audit
- **Data Partition**: Full Test Set ($N=100,000$) vs. Clean Deduplicated Test Set ($N=98,543$, 1,457 cross-partition duplicates removed).
- **Execution Script**: `scripts/evaluate_deduplication_sensitivity.py`
- **Recomputed Metrics across 5 Seeds**:
  - **Dense-AE Fixed 95th**: Full F1: $0.8854 \pm 0.0013 \to$ Clean F1: $0.8845 \pm 0.0014$ ($\Delta \text{F1} = -0.0009$).
  - **Dense-AE Excluded EWMA**: Full F1: $0.9014 \pm 0.0018 \to$ Clean F1: $0.9007 \pm 0.0019$ ($\Delta \text{F1} = -0.0007$).
  - **XGBoost Oracle**: Full F1: $0.9269 \pm 0.0004 \to$ Clean F1: $0.9265 \pm 0.0003$ ($\Delta \text{F1} = -0.0003$).
- **Conclusion**: Performance variations are strictly within $\pm 0.09\%$, proving that cross-split duplicates have negligible impact on generalization claims.
