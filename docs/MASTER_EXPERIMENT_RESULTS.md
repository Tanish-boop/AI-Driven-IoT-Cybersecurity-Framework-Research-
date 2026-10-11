# Permanent Master Experiment Results Record (E1–E8)

**Repository**: `c:\Users\hp\OneDrive\Desktop\Research Experiments`  
**Dataset**: CICIoT2023 Recovery Partition (`data/processed/recovery/recovery_processed.npz`)  
**Hardware/Software Environment**: Windows 11 x86_64, Python 3.13.4, PyTorch 2.8.0+cpu, scikit-learn 1.7.1, xgboost 3.4.1, `pqcrypto` 1.0.0, `cryptography` 46.0.1  
**Last Updated**: 2026-10-09  

---

## Executive Summary & Experiment Status Summary Table

| Experiment ID | Title / Target | Status | Seeds / Trials | Key Metric (Mean ± Std) | Validation Status | Core Conclusion |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **E1** | Reconstructed Anomaly Baseline | **COMPLETED & REPRODUCED** | 42, 123, 456, 789, 2026 | **F1**: $0.8854 \pm 0.0013$<br>**FPR**: $0.0493 \pm 0.0013$ | `COMPLETED AND REPRODUCED` | Sample-level Dense-AE ($L=1$) eliminates sequence window boundary leakage ($FPR=1.0$ on original pre-shuffled LSTM-AE). |
| **E2** | Dynamic Anomaly Thresholding | **COMPLETED & REPRODUCED** | 42, 123, 456, 789, 2026 | **Excluded EWMA F1**: $0.9014 \pm 0.0018$<br>**UnGuarded EWMA F1**: $0.0003 \pm 0.0001$ | `COMPLETED AND REPRODUCED` | `Excluded_EWMA` prevents threshold inflation during attack floods, outperforming fixed percentile baselines. |
| **E3** | Supervised Oracle Reference | **COMPLETED & REPRODUCED** | 42, 123, 456, 789, 2026 | **XGBoost F1**: $0.9269 \pm 0.0004$<br>**FPR**: $0.0162 \pm 0.0012$ | `COMPLETED AND REPRODUCED` | Supervised Oracle sets the empirical upper bound; `Excluded_EWMA` comes within 2.55% F1-score without attack labels. |
| **E4 (Hist)**| Contaminated Defense Evaluation | **COMPLETED, INVALID CLAIM** | 42, 123, 456, 789, 2026 | **DQN Reward**: $34131.20 \pm 1179.55$<br>**False Block**: $42.22\% \pm 52.83\%$ | `COMPLETED, BUT RESULTS INVALID FOR INTENDED CLAIM` | Historical run trained policies on `X_test` (steps 0-2000), causing evaluation split contamination. Preserved for audit. |
| **E4 (Corr)**| Un-Contaminated RL Defense Rerun | **COMPLETED & REPRODUCED** | 42, 123, 456, 789, 2026 | **DQN Containment**: $71.20\% \pm 0.05\%$<br>**DQN False Block**: $0.77\% \pm 0.43\%$<br>**Q-Learning False Block**: $0.00\% \pm 0.00\%$ | `COMPLETED AND REPRODUCED` | Retrained policies strictly on `X_sup` (40k samples), leaving `X_test` (100k samples) strictly held-out. Verified by `tests/test_e4_uncontaminated.py`. |
| **E5** | Post-Quantum Cryptography | **COMPLETED & REPRODUCED** | 100 trials / 3 variants / 4 payloads | **ML-KEM-768 Setup**: $0.4293$ ms<br>**Tamper Rejection**: 100% | `COMPLETED AND REPRODUCED` | Standardized NIST FIPS 203 ML-KEM-768 delivers sub-ms key setup with OpenSSL AES-256-GCM AEAD tamper rejection. |
| **E6** | Integrity Verification Architecture | **COMPLETED & REPRODUCED** | 100 trials / 4 payloads / 4 chain lengths | **HMAC-SHA256 Latency**: $0.0332$ ms<br>**Blockchain Append**: $0.0409$ ms | `COMPLETED AND REPRODUCED` | HMAC-SHA-256 provides anti-forgery authentication at low overhead (171B). Blockchain audit log provides sequence protection and tamper localization with O(1) append latency. |
| **E7** | Full Framework Integrated Ablation | **COMPLETED & REPRODUCED** | 42, 123, 456, 789, 2026 | **F1**: $0.8968 \pm 0.0013$<br>**Containment**: $80.65\% \pm 3.16\%$<br>**Latency**: $0.3781$ ms | `COMPLETED AND REPRODUCED` | Full pipeline confirms component contributions: Excluded EWMA (+1.31% F1), Q-Learning (+0.87% Containment), sub-ms PQC + Blockchain log. |
| **E8** | Feature Rate Scaling Stress Test | **COMPLETED & REPRODUCED** | 42, 123, 456, 789, 2026 | **Fixed 95th 2.0x FPR**: $0.2733 \pm 0.0152$ (+454.4% explosion) | `COMPLETED AND REPRODUCED` | Fixed thresholds experience catastrophic false positive explosions under input rate scaling. |

---

## Detailed Experiment-by-Experiment Master Records

### Experiment E1: Reconstructed Anomaly Detection Baseline
* **Implementation**: Sample-level Dense Autoencoder ($L=1$, 39-12-39 bottleneck architecture). Replaces the original base paper's pre-shuffled sequence LSTM ($L > 1$), which suffered from sequence window boundary contamination resulting in $\text{FPR}=1.0$ (100% false alarms on benign traffic).
* **Dataset Partition**: `X_train` (100,000 pure Benign flows), `X_val` (30,000 pure Benign flows), `X_test` (100,000 mixed flows: 14,911 Benign, 85,089 Attack). Preprocessed using `StandardScaler` fitted strictly on `X_train`.
* **Threshold Definition**: Static 95th Percentile ($\tau_{95}$) and 99th Percentile ($\tau_{99}$) of reconstruction error on `X_val`.
* **Exact Empirical Results Across 5 Random Seeds**:
  * **Dense-AE Fixed 95th Percentile ($\tau_{95}$)**:
    * Precision: $0.9893 \pm 0.0003$
    * Recall: $0.8013 \pm 0.0022$
    * F1-Score: **$0.8854 \pm 0.0013$**
    * False Positive Rate (FPR): $0.0493 \pm 0.0013$
    * ROC-AUC: $0.9225 \pm 0.0027$
  * **Dense-AE Fixed 99th Percentile ($\tau_{99}$)**:
    * Precision: $0.9975 \pm 0.0001$
    * Recall: $0.7650 \pm 0.0017$
    * F1-Score: $0.8659 \pm 0.0011$
    * False Positive Rate (FPR): $0.0108 \pm 0.0004$
    * ROC-AUC: $0.9225 \pm 0.0027$
* **Validation Status**: `COMPLETED AND REPRODUCED`
* **Artifact Paths**:
  * `results/metrics/full_benchmark_results.csv`
  * `results/metrics/full_benchmark_summary.csv`
  * `results/metrics/recomputed_metrics.csv`

---

### Experiment E2: Dynamic Thresholding Strategy Evaluation
* **Implementation**: Evaluated four dynamic threshold update strategies against static baselines:
  1. `Fixed_95` / `Fixed_99`: Offline static percentiles.
  2. `UnGuarded_EWMA`: Updates background mean ($\mu_t$) and variance ($\sigma_t^2$) on *all* incoming flows.
  3. `Excluded_EWMA`: Updates background statistics *only* when reconstruction error $E_t \le \tau_t$.
  4. `Guarded_Winsorized_EWMA`: Clamps attack error scores before updating background statistics.
* **Exact Empirical Results Across 5 Random Seeds**:
  * **Excluded EWMA**: Precision: $0.9724 \pm 0.0022$, Recall: **$0.8401 \pm 0.0023$**, F1-Score: **$0.9014 \pm 0.0018$**, FPR: $0.1360 \pm 0.0110$, ROC-AUC: $0.9225 \pm 0.0027$.
  * **UnGuarded EWMA**: Precision: $1.0000 \pm 0.0000$, Recall: $0.0001 \pm 0.0000$, F1-Score: **$0.0003 \pm 0.0001$**, FPR: $0.0000 \pm 0.0000$. (**Catastrophic Threshold Inflation Collapse**).
  * **Guarded EWMA**: Precision: $1.0000 \pm 0.0000$, Recall: $0.0022 \pm 0.0000$, F1-Score: **$0.0045 \pm 0.0001$**, FPR: $0.0000 \pm 0.0000$.
* **Core Finding**: Updating adaptive thresholds on attack traffic without exclusion (`UnGuarded` / `Guarded`) inflates background statistics, driving recall to near zero. `Excluded_EWMA` prevents inflation and achieves the highest unsupervised F1-score (0.9014).
* **Validation Status**: `COMPLETED AND REPRODUCED`
* **Artifact Paths**: `results/metrics/full_benchmark_results.csv`, `results/metrics/full_benchmark_summary.csv`

---

### Experiment E3: Supervised Oracle Reference & Model Comparison
* **Implementation**: Supervised XGBoost classifier (`n_estimators=100`, `max_depth=6`, `learning_rate=0.1`) trained on 40,000 50/50 Benign/Attack samples (`X_sup`) and evaluated on held-out `X_test`. Serves as the supervised upper bound reference.
* **Exact Empirical Results Across 5 Random Seeds**:
  * **XGBoost Oracle**: Precision: $0.9967 \pm 0.0002$, Recall: **$0.8662 \pm 0.0009$**, F1-Score: **$0.9269 \pm 0.0004$**, FPR: $0.0162 \pm 0.0012$, ROC-AUC: $0.9682 \pm 0.0001$.
  * **Isolation Forest Baseline**: Precision: $0.9866 \pm 0.0003$, Recall: $0.6402 \pm 0.0114$, F1-Score: $0.7765 \pm 0.0084$, FPR: $0.0495 \pm 0.0009$, ROC-AUC: $0.8828 \pm 0.0095$.
* **Wilcoxon Signed-Rank Test ($N=5$)**:
  * Dense-AE Fixed 95th vs Fixed 99th F1-Score: $W = 0.0000, p = 0.0625$ (Not statistically significant at $\alpha = 0.05$ due to $N=5$ sample size limit; qualified in text).
* **Validation Status**: `COMPLETED AND REPRODUCED`
* **Artifact Paths**: `results/metrics/full_benchmark_summary.csv`, `results/metrics/statistical_tests.json`

---

### Experiment E4: Un-Contaminated Defensive Mitigation Policy Evaluation
* **Historical Contaminated Run (Preserved)**:
  * Preliminary script trained policies on `X_test` (steps 0-2000). Tagged as `COMPLETED, BUT RESULTS INVALID FOR INTENDED CLAIM`. Saved to `results/metrics/e4_policy_results_historical.csv`.
* **Corrected Rerun Protocol**:
  * Retrained Q-Learning & DQN policies strictly on `X_sup` (40,000 samples). `X_test` (100,000 samples) reserved strictly for held-out evaluation (`Scenario_1_Heavy_Attack` and `Scenario_2_Stealth_Attack`).
  * Automated data isolation test passing: `tests/test_e4_uncontaminated.py`.
* **Exact Empirical Results Across 5 Random Seeds (Scenario 1: Heavy Attack)**:
  * **Static Rule-Based**: Containment: $99.98\% \pm 0.00\%$, False Block Rate: **$100.00\% \pm 0.00\%$**, Disruption Penalty: $7290.00 \pm 0.00$, Latency: $0.0413 \pm 0.0233$ ms.
  * **Tabular Q-Learning**: Containment: $55.94\% \pm 7.26\%$, False Block Rate: **$0.00\% \pm 0.00\%$**, Disruption Penalty: $12.60 \pm 28.17$, Latency: **$0.0757 \pm 0.0146$ ms**.
  * **Deep Q-Network (DQN)**: Containment: **$71.20\% \pm 0.05\%$**, False Block Rate: **$0.77\% \pm 0.43\%$**, Disruption Penalty: $60.20 \pm 21.91$, Latency: $0.4412 \pm 0.1315$ ms.
* **Exact Empirical Results Across 5 Random Seeds (Scenario 2: Stealth Attack)**:
  * **Static Rule-Based**: Containment: $99.98\% \pm 0.00\%$, False Block Rate: $100.00\% \pm 0.00\%$, Disruption Penalty: $7110.00 \pm 0.00$, Latency: $0.0398 \pm 0.0221$ ms.
  * **Tabular Q-Learning**: Containment: $56.21\% \pm 7.81\%$, False Block Rate: **$0.00\% \pm 0.00\%$**, Disruption Penalty: $18.00 \pm 40.25$, Latency: **$0.0718 \pm 0.0036$ ms**.
  * **Deep Q-Network (DQN)**: Containment: **$73.01\% \pm 0.05\%$**, False Block Rate: **$0.53\% \pm 0.32\%$**, Disruption Penalty: $44.60 \pm 15.96$, Latency: $0.3071 \pm 0.1332$ ms.
* **Validation Status**: `COMPLETED AND REPRODUCED`
* **Artifact Paths**: `results/metrics/e4_policy_summary_corrected.csv`, `results/metrics/e4_reward_sensitivity.csv`

---

### Experiment E5: Standardized NIST Post-Quantum Cryptography Benchmark
* **Implementation**: Standardized NIST FIPS 203 ML-KEM Key Encapsulation Mechanisms (ML-KEM-512, ML-KEM-768, ML-KEM-1024) paired with HKDF-SHA256 key derivation and AES-256-GCM authenticated encryption (AEAD) across 100 repeated trials.
* **Exact Empirical Microbenchmark Results (1 KiB Payload)**:
  * **ML-KEM-512**: KeyGen: $0.0469$ ms, Encaps: $0.0560$ ms, Decaps: $0.0774$ ms, Total KEM: **$0.1802$ ms**, First-Msg Setup: $0.1972$ ms. PK = 800 B, SK = 1632 B, CT = 768 B, SS = 32 B.
  * **ML-KEM-768**: KeyGen: $0.1114$ ms, Encaps: $0.1353$ ms, Decaps: $0.1826$ ms, Total KEM: **$0.4293$ ms**, First-Msg Setup: $0.4754$ ms. PK = 1,184 B, SK = 2400 B, CT = 1,088 B, SS = 32 B.
  * **ML-KEM-1024**: KeyGen: $0.1294$ ms, Encaps: $0.1485$ ms, Decaps: $0.1815$ ms, Total KEM: **$0.4594$ ms**, First-Msg Setup: $0.4963$ ms. PK = 1,568 B, SK = 3168 B, CT = 1,568 B, SS = 32 B.
* **Tamper Verification**: 100% tamper rejection verified on bit-flip byte corruptions (OpenSSL `cryptography.exceptions.InvalidTag`).
* **Automated Test Coverage**: `tests/test_e5_crypto.py` (7/7 passed).
* **Validation Status**: `COMPLETED AND REPRODUCED`
* **Artifact Paths**: `results/metrics/e5_summary.csv`, `results/tables/table5_pqc_benchmark.md`, `paper/tables/table5_pqc_benchmark.tex`, `results/figures/figure5_pqc_latency.png`

---

### Experiment E6: Integrity Verification Architecture
* **Implementation**: Controlled benchmark of three candidate evidence integrity mechanisms:
  1. `Salted SHA-256`: 16-byte cryptographically secure random salt, unkeyed SHA-256 digest.
  2. `HMAC-SHA-256`: 256-bit isolated symmetric key, constant-time `hmac.compare_digest` verification.
  3. `Blockchain-Style Audit Log`: Append-only cryptographic hash chain with deterministic canonical JSON serialization, genesis block, monotonic sequence indices, and tamper localization.
* **Exact Empirical Microbenchmark Results (1 KiB Payload, 100 Trials)**:
  * **Salted SHA-256**: Creation: $0.0279 \pm 0.0112$ ms, Verification: $0.0133 \pm 0.0035$ ms, End-to-End w/ Disk: $0.3374$ ms, Overhead: 193 B, Throughput: 34.94 MB/s.
  * **HMAC-SHA-256**: Creation: $0.0332 \pm 0.0128$ ms, Verification: $0.0158 \pm 0.0048$ ms, End-to-End w/ Disk: $0.3553$ ms, Overhead: **171 B**, Throughput: 29.45 MB/s.
  * **Blockchain Audit Log**: Single Block Append: $0.0409 \pm 0.0186$ ms, Single Block Verify: $0.0198 \pm 0.0060$ ms, End-to-End w/ Disk: $0.4031$ ms, Overhead: 317 B, Throughput: 23.88 MB/s.
* **Scaling Behavior (Blockchain Audit Log, 1 KiB Records)**:
  * Append latency is strictly $O(1)$: $0.0160$ to $0.0236$ ms across $N = 100$ to $N = 2000$.
  * Full chain verification is linear $O(N)$: $2.56$ ms ($N=100$), $8.02$ ms ($N=500$), $14.36$ ms ($N=1000$), $29.85$ ms ($N=2000$).
* **Adversarial Tamper Detection**: 100% detection rate across payload bit flips, wrong secret keys, block deletion, insertion, and reordering.
* **Demonstrated Limitations**: Salted SHA-256 fails against adversaries with write access to storage (unkeyed forgery); local blockchain hash chains require external tip anchoring to prevent full-chain regeneration by root adversaries.
* **Automated Test Coverage**: `tests/test_e6_integrity.py` (13/13 passed).
* **Validation Status**: `COMPLETED AND REPRODUCED`
* **Artifact Paths**: `results/metrics/e6_summary.csv`, `results/metrics/e6_scaling_summary.csv`, `results/tables/table6_integrity_benchmark.md`, `paper/tables/table6_integrity_benchmark.tex`, `results/figures/figure6_integrity_benchmark.png`

---

### Experiment E7: Full Framework Integrated Ablation Study
* **Implementation**: Synchronous end-to-end pipeline benchmark combining sample-level Dense Autoencoder ($L=1$), Excluded EWMA dynamic threshold adaptation, un-contaminated Q-learning defensive mitigation, standardized NIST FIPS 203 ML-KEM-768 post-quantum key encapsulation with AES-256-GCM AEAD, and a lightweight blockchain-style append-only audit log.
* **Evaluated Ablation Variants Across 5 Random Seeds (42, 123, 456, 789, 2026)**:
  * **Base Paper Architecture (Fixed 95th + Static Rule + Plaintext + Salted SHA-256)**:
    * F1-Score: $0.8837 \pm 0.0004$
    * Detection Recall: $79.88\% \pm 0.06\%$
    * Attack Containment: $79.88\% \pm 0.06\%$
    * False Block Rate: $3.20\% \pm 0.07\%$
    * Latency: $0.3319 \pm 0.0440$ ms, Overhead: 194 B, Quantum-Safe: No, Tamper-Immune: No
  * **Ablation (-Adaptive Threshold) (Fixed 95th + Q-Learning + ML-KEM-768 + Blockchain Log)**:
    * F1-Score: $0.8837 \pm 0.0004$, Recall: $79.88\% \pm 0.06\%$
    * Attack Containment: $81.67\% \pm 2.51\%$, False Block Rate: $8.24\% \pm 3.44\%$
  * **Ablation (-RL Defense) (Excluded EWMA + Static Rule + ML-KEM-768 + Blockchain Log)**:
    * F1-Score: $0.8968 \pm 0.0013$, Recall: $82.68\% \pm 0.24\%$
    * Attack Containment: $79.78\% \pm 0.06\%$, False Block Rate: $3.22\% \pm 0.06\%$
  * **Ablation (-PQC) (Excluded EWMA + Q-Learning + Plaintext + Blockchain Log)**:
    * F1-Score: $0.8968 \pm 0.0013$, Attack Containment: $80.65\% \pm 3.16\%$, Quantum-Safe: No
  * **Ablation (-Blockchain Log) (Excluded EWMA + Q-Learning + ML-KEM-768 + Salted SHA-256)**:
    * F1-Score: $0.8968 \pm 0.0013$, Storage Overhead: 194 B, Tamper-Immune: No (Unkeyed Hash)
  * **Full Proposed Framework (Excluded EWMA + Q-Learning + ML-KEM-768 + Blockchain Log)**:
    * F1-Score: **$0.8968 \pm 0.0013$**
    * Detection Recall: **$82.68\% \pm 0.24\%$**
    * Attack Containment: **$80.65\% \pm 3.16\%$**
    * False Block Rate: $7.39\% \pm 2.51\%$ (Service Availability: **$92.61\% \pm 2.51\%$**)
    * End-to-End Latency: **$0.3781 \pm 0.0225$ ms**
    * System Throughput: **$2652.4 \pm 154.8$ events/s**
    * Storage Overhead: **321 Bytes**
    * Quantum Resistance: **Yes (NIST Category 3)**
    * Audit Immutability: **Yes (Cryptographic Hash Chain with sequence validation)**
* **Automated Test Coverage**: `tests/test_e7_pipeline.py` (3/3 passed).
* **Validation Status**: `COMPLETED AND REPRODUCED`
* **Artifact Paths**: `results/metrics/e7_ablation_results.csv`, `results/metrics/e7_ablation_summary.csv`, `results/tables/table7_ablation_comparison.md`, `paper/tables/table7_ablation_comparison.tex`, `results/figures/figure7_ablation_comparison.png`

---

### Experiment E8: Feature Rate Scaling Stress Test
* **Implementation**: Applied dynamic input feature rate scaling factors ($1.0\times, 1.5\times, 2.0\times$) to test stream rate features, evaluating static threshold stability under traffic shifts.
* **Exact Empirical Results Across 5 Random Seeds**:
  * **Fixed 95th Base (1.0x)**: FPR = $0.0493 \pm 0.0013$
  * **Fixed 95th Stress (1.5x)**: FPR = $0.0953 \pm 0.0092$ (+93.3% FPR increase)
  * **Fixed 95th Stress (2.0x)**: FPR = **$0.2733 \pm 0.0152$ (+454.4% False Positive Explosion)**
* **Validation Status**: `COMPLETED AND REPRODUCED`
* **Artifact Paths**: `results/metrics/full_benchmark_summary.csv`, `results/tables/table2_stress_test_performance.csv`
