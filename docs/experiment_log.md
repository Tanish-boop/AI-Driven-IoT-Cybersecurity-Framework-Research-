# Master Experiment Log

**Repository**: `c:\Users\hp\OneDrive\Desktop\Research Experiments`  
**Dataset**: CICIoT2023 (Recovery Partition: `data/processed/recovery/recovery_processed.npz`)  
**Hardware/Software**: Windows 11 x86_64, Python 3.13.4, PyTorch 2.8.0+cpu, scikit-learn 1.7.1, xgboost 3.4.1, `pqcrypto` 1.0.0, `cryptography` 46.0.1  

---

## Completed Experiments Summary

### Log Entry 1: Data Pipeline Audit & Leakage Prevention Fix
- **Date**: 2026-10-09
- **Script**: [src/preprocessing/recovery_pipeline.py](file:///c:/Users/hp/OneDrive/Desktop/Research%20Experiments/src/preprocessing/recovery_pipeline.py)
- **Status**: PASSED (`tests/test_recovery_pipeline.py` 4/4 passed in 19.64s)
- **Configuration**:
  - `X_train`: 100,000 pure Benign samples
  - `X_val`: 30,000 pure Benign samples
  - `X_sup` / `y_sup`: 40,000 50/50 Benign/Attack samples (Supervised Oracle training)
  - `X_test` / `y_test`: 100,000 samples (14.91% Benign, 85.09% Attack)
  - Preprocessing: `StandardScaler.fit()` fit strictly on `X_train`. Frozen 39-feature schema (`FEATURE_SCHEMA`).

---

### Log Entry 2: Controlled Pilot Run (Seed = 42)
- **Date**: 2026-10-09
- **Script**: [scripts/run_controlled_pilot.py](file:///c:/Users/hp/OneDrive/Desktop/Research%20Experiments/scripts/run_controlled_pilot.py)
- **Status**: COMPLETED
- **Metrics Artifact**: `results/pilot/pilot_metrics.csv`

---

### Log Entry 3: Full 5-Random-Seed Benchmark Run (Seeds: 42, 123, 456, 789, 2026)
- **Date**: 2026-10-09
- **Script**: [scripts/run_full_benchmark.py](file:///c:/Users/hp/OneDrive/Desktop/Research%20Experiments/scripts/run_full_benchmark.py)
- **Status**: COMPLETED (Exit Code 0)
- **Results Files**: `results/metrics/full_benchmark_results.csv`, `results/metrics/full_benchmark_summary.csv`

---

### Log Entry 4: Feature-Level Rate Scaling Stress Test (E8)
- **Date**: 2026-10-09
- **Script**: Included in [scripts/run_full_benchmark.py](file:///c:/Users/hp/OneDrive/Desktop/Research%20Experiments/scripts/run_full_benchmark.py)
- **Status**: COMPLETED

---

### Log Entry 5: Statistical Significance Tests (E2 / E3)
- **Date**: 2026-10-09
- **Script**: `scipy.stats.wilcoxon` in [scripts/run_full_benchmark.py](file:///c:/Users/hp/OneDrive/Desktop/Research%20Experiments/scripts/run_full_benchmark.py)
- **Status**: COMPLETED

---

### Log Entry 6: Un-Contaminated Defensive-Response Policy Evaluation (E4 Rerun)
- **Date**: 2026-10-09
- **Script**: [scripts/run_e4_defense_experiment.py](file:///c:/Users/hp/OneDrive/Desktop/Research%20Experiments/scripts/run_e4_defense_experiment.py)
- **Status**: COMPLETED (Exit Code 0)
- **Historical Contaminated Artifact Preserved**: `results/metrics/e4_policy_results_historical.csv`
- **Corrected Artifacts**: `results/metrics/e4_policy_summary_corrected.csv`, `results/metrics/e4_reward_sensitivity.csv`, `tests/test_e4_uncontaminated.py` (3/3 passed)
- **Key Corrected Findings (Scenario 1: Heavy Attack)**:
  - **Rule-Based**: Containment = $99.98\% \pm 0.00\%$, False Block Rate = **$100.00\% \pm 0.00\%$**, Disruption Penalty = $7290.00 \pm 0.00$, Latency = $0.0413 \pm 0.0233$ ms
  - **Q-Learning**: Containment = $55.94\% \pm 7.26\%$, False Block Rate = **$0.00\% \pm 0.00\%$**, Disruption Penalty = $12.60 \pm 28.17$, Latency = $0.0757 \pm 0.0146$ ms
  - **DQN**: Containment = **$71.20\% \pm 0.05\%$**, False Block Rate = **$0.77\% \pm 0.43\%$**, Disruption Penalty = $60.20 \pm 21.91$, Latency = $0.4412 \pm 0.1315$ ms

---

### Log Entry 7: Standardized NIST Post-Quantum Cryptography Benchmark (E5)
- **Date**: 2026-10-09
- **Script**: [scripts/run_e5_crypto_benchmark.py](file:///c:/Users/hp/OneDrive/Desktop/Research%20Experiments/scripts/run_e5_crypto_benchmark.py)
- **Module**: [src/crypto/ml_kem_benchmark.py](file:///c:/Users/hp/OneDrive/Desktop/Research%20Experiments/src/crypto/ml_kem_benchmark.py)
- **Tests**: [tests/test_e5_crypto.py](file:///c:/Users/hp/OneDrive/Desktop/Research%20Experiments/tests/test_e5_crypto.py) (7/7 passed in 0.20s)
- **Status**: COMPLETED (Exit Code 0)
- **Artifacts**: `results/metrics/e5_summary.csv`, `results/tables/table5_pqc_benchmark.md`, `paper/tables/table5_pqc_benchmark.tex`, `results/figures/figure5_pqc_latency.png`
- **Key Findings (1KiB Payload)**:
  - **ML-KEM-512**: KeyGen = $0.0469$ ms, Encaps = $0.0560$ ms, Decaps = $0.0774$ ms, Total KEM = $0.1802$ ms, First-Msg = $0.1972$ ms. PK = 800 B, CT = 768 B.
  - **ML-KEM-768**: KeyGen = $0.1114$ ms, Encaps = $0.1353$ ms, Decaps = $0.1826$ ms, Total KEM = $0.4293$ ms, First-Msg = $0.4754$ ms. PK = 1,184 B, CT = 1,088 B.
  - **ML-KEM-1024**: KeyGen = $0.1294$ ms, Encaps = $0.1485$ ms, Decaps = $0.1815$ ms, Total KEM = $0.4594$ ms, First-Msg = $0.4963$ ms. PK = 1,568 B, CT = 1,568 B.
  - **Tamper Verification**: 100% pass on OpenSSL AES-256-GCM `InvalidTag` corruption rejection.

---

### Log Entry 8: Integrity Verification Architecture Benchmark (E6)
- **Date**: 2026-10-11
- **Script**: [scripts/run_e6_integrity_benchmark.py](file:///c:/Users/hp/OneDrive/Desktop/Research%20Experiments/scripts/run_e6_integrity_benchmark.py)
- **Package**: `src/integrity/` (`salted_sha256.py`, `hmac_sha256.py`, `blockchain_log.py`)
- **Tests**: [tests/test_e6_integrity.py](file:///c:/Users/hp/OneDrive/Desktop/Research%20Experiments/tests/test_e6_integrity.py) (13/13 passed in 0.28s)
- **Status**: COMPLETED (Exit Code 0)
- **Artifacts**: `results/metrics/e6_summary.csv`, `results/metrics/e6_scaling_summary.csv`, `results/tables/table6_integrity_benchmark.md`, `paper/tables/table6_integrity_benchmark.tex`, `results/figures/figure6_integrity_benchmark.png`
- **Key Findings (1KiB Payload)**:
  - **Salted SHA-256**: Creation = $0.0279$ ms, Verification = $0.0133$ ms, End-to-End w/ Disk = $0.3374$ ms, Overhead = 193 B, Throughput = 34.94 MB/s. Unkeyed limitation verified (does not authenticate against active storage adversaries).
  - **HMAC-SHA-256**: Creation = $0.0332$ ms, Verification = $0.0158$ ms, End-to-End w/ Disk = $0.3553$ ms, Overhead = **171 B**, Throughput = 29.45 MB/s. Secret key isolation and constant-time verification prevent forgery.
  - **Blockchain Audit Log**: Single-Block Append = $0.0409$ ms, Single-Block Verify = $0.0198$ ms, End-to-End w/ Disk = $0.4031$ ms, Overhead = 317 B, Throughput = 23.88 MB/s.
  - **Chain Scaling**: Append latency is $O(1)$ (~0.016–0.023 ms); full chain verification is linear $O(N)$ (29.85 ms for $N=2,000$ blocks).
  - **Tamper Detection**: 100% detection rate across 6 attack vectors (bit flip, wrong key, block deletion, insertion, reordering, broken link).

---

---

## [2026-10-11] - Experiment E7: Integrated Framework Ablation Study
- **Script**: `scripts/run_e7_ablation_experiment.py`
- **Seeds**: 42, 123, 456, 789, 2026 (5 random seeds)
- **Unit Tests**: `tests/test_e7_pipeline.py` (3/3 passed). Full test suite: 27/27 passed.
- **Key Empirical Results**:
  - **Full Proposed Framework**:
    - F1-Score: **$0.8968 \pm 0.0013$**
    - Detection Recall: **$82.68\% \pm 0.24\%$**
    - Attack Containment: **$80.65\% \pm 3.16\%$**
    - False Block Rate: **$7.39\% \pm 2.51\%$** (Service Availability: **$92.61\% \pm 2.51\%$**)
    - End-to-End Latency: **$0.3781 \pm 0.0225$ ms** (Sub-millisecond processing)
    - System Throughput: **$2652.4 \pm 154.8$ events/s**
    - Storage Overhead: **321 Bytes**
    - Quantum Safe: Yes (NIST Category 3 ML-KEM-768)
    - Audit Immutability: Yes (Cryptographic Hash Chain with sequence validation)
  - **Component Ablation Findings**:
    - Reverting to Fixed 95th Percentile reduces F1 by $-1.31\%$ ($0.8837$) and recall by $-2.80\%$ ($79.88\%$).
    - Reverting to Static Rule-Based defense reduces attack containment from $80.65\%$ to $79.78\%$.
    - Reverting to Classical encryption eliminates post-quantum security against store-now-decrypt-later attacks.
    - Reverting to Salted SHA-256 sacrifices sequence integrity and enables undetected forgery by storage adversaries.
- **Artifacts Saved**: `results/metrics/e7_ablation_results.csv`, `results/metrics/e7_ablation_summary.csv`, `results/tables/table7_ablation_comparison.md`, `paper/tables/table7_ablation_comparison.tex`, `results/figures/figure7_ablation_comparison.png`.
- **Status**: `COMPLETED AND REPRODUCED`. Full E1–E8 experimental scope is now complete.

