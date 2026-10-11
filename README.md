# AI-Driven-IoT-Cybersecurity-Framework-Research-

## An AI-Driven Adaptive Cybersecurity Framework for IoT: Anomaly Detection, Dynamic Thresholding, Un-Contaminated Reinforcement Learning Defense, Post-Quantum Cryptography, and Tamper-Evident Audit Logging

**Topic**: Integration of Deep Anomaly Detection, Adaptive Thresholding, Un-Contaminated Reinforcement Learning Defense, NIST FIPS 203 Post-Quantum Cryptography, and Cryptographic Audit Logging for IoT Networks.  
**Dataset Benchmark**: CICIoT2023 (*Neto et al., Sensors 2023*)  
**Reference Base Paper**: M. M. Saeed, *"An AI-Driven Cybersecurity Framework for IoT: Integrating LSTM-Based Anomaly Detection, Reinforcement Learning, and Post-Quantum Encryption,"* *IEEE Access*, vol. 13, pp. 104027–104036, 2025.  

---

## 1. Environment Requirements & Setup

### Operating System & Hardware
- **Target OS**: Windows 11 / Linux (Ubuntu 22.04+) x86_64 / ARM64
- **CPU**: AMD64 or ARM64 host architecture (representative of IoT edge gateways like Raspberry Pi 4/5, Intel Atom/NUC)
- **RAM**: Minimum 8 GB (16 GB recommended)
- **Storage**: ~15 GB for data, processed partitions, and model artifacts

### Software Dependencies
- **Python**: 3.11 – 3.13 (Audited on Python 3.13.4)
- **PyTorch**: 2.8.0+cpu
- **Machine Learning**: `scikit-learn` 1.7.1, `xgboost` 3.4.1, `scipy` 1.15.2, `joblib` 1.4.2
- **Data & Visualization**: `numpy` 2.2.3, `pandas` 2.2.3, `matplotlib` 3.10.1
- **Cryptographic Libraries**: `cryptography` 46.0.1 (OpenSSL 3.x), `pqcrypto` 1.0.0 (NIST FIPS 203 ML-KEM)
- **Testing**: `pytest` 9.0.3

### Installation
```bash
git clone https://github.com/Tanish-boop/AI-Driven-IoT-Cybersecurity-Framework-Research-.git
cd AI-Driven-IoT-Cybersecurity-Framework-Research-
pip install -r requirements.txt
```

---

## 2. Dataset Protocol & Preprocessing

The research benchmark utilizes **CICIoT2023**, extracting 39 numerical network flow features. Non-numeric metadata identifiers (`src_ip`, `dst_ip`, `src_port`, `dst_port`, `Timestamp`, `flow_id`) are explicitly purged to prevent identity memorization.

To guarantee zero data leakage, the dataset is partitioned into 4 strictly isolated subsets:
- **`X_train`** ($100,000$ pure benign flows): Used exclusively to fit `StandardScaler` and train the unsupervised Dense Autoencoder.
- **`X_val`** ($30,000$ pure benign flows): Used exclusively to calibrate decision thresholds ($\tau_{95}, \tau_{99}$) and initialize EWMA parameters.
- **`X_sup`** ($40,000$ balanced benign/attack flows): Used exclusively to train the supervised XGBoost oracle and RL response policies.
- **`X_test`** ($100,000$ mixed flows: 14,911 benign, 85,089 attack): **Strictly held-out evaluation stream** for all benchmark tiers.

Preprocessed data artifact:
```bash
# Verify dataset integrity (SHA256: f06e54859d0e5e07982c33560fa6d91613d09b5e8e00032fc8ba76d28b4a9852)
python -c "import hashlib; print(hashlib.sha256(open('data/processed/recovery/recovery_processed.npz','rb').read()).hexdigest())"
```

---

## 3. Reproducible Experiment Execution Commands

Each experiment can be executed independently from the repository root:

### Experiments E1, E2, E3, E8: Detection Baselines & Threshold Stress Benchmark
Evaluates Dense Autoencoder, Fixed 95th/99th percentiles, UnGuarded/Excluded/Guarded EWMA, Isolation Forest, XGBoost Oracle, and non-stationary rate scaling ($1.0\times, 1.5\times, 2.0\times$) over 5 random seeds ($42, 123, 456, 789, 2026$):
```bash
python scripts/run_full_benchmark.py
```
*Outputs*: `results/metrics/full_benchmark_results.csv`, `results/metrics/full_benchmark_summary.csv`, `results/metrics/baseline_errors.npz`

### Experiment E4: Un-Contaminated Defensive RL Mitigation Benchmark
Evaluates Rule-Based, Tabular Q-Learning, and Deep Q-Networks (DQN) trained strictly on `X_sup` and evaluated on held-out `X_test` scenarios, including reward penalty sensitivity:
```bash
python scripts/run_e4_defense_experiment.py
```
*Outputs*: `results/metrics/e4_policy_results_corrected.csv`, `results/metrics/e4_policy_summary_corrected.csv`, `results/metrics/e4_reward_sensitivity.csv`

### Experiment E5: NIST FIPS 203 Post-Quantum Cryptography Microbenchmark
Measures key generation, encapsulation, decapsulation, and AES-256-GCM AEAD encryption latencies across ML-KEM-512, ML-KEM-768, and ML-KEM-1024 over 100 trials, including bit-flip tamper rejection:
```bash
python scripts/run_e5_crypto_benchmark.py
```
*Outputs*: `results/metrics/e5_raw_results.csv`, `results/metrics/e5_summary.csv`, `results/metrics/e5_crypto_environment.json`

### Experiment E6: Forensic Integrity Verification Architecture Benchmark
Compares Salted SHA-256, HMAC-SHA-256, and append-only Blockchain Audit Logging across creation latency, verification latency, disk I/O, storage overhead, and tamper detection (modification, deletion, insertion, reordering, chain rewrite):
```bash
python scripts/run_e6_integrity_benchmark.py
```
*Outputs*: `results/metrics/e6_raw_results.csv`, `results/metrics/e6_summary.csv`, `results/metrics/e6_scaling_summary.csv`

### Experiment E7: Integrated End-to-End Framework Ablation Benchmark
Executes the full 5-stage synchronous pipeline (Dense-AE + Excluded EWMA + Q-Learning + ML-KEM-768 + Blockchain Audit Log) alongside 5 ablation variants across 5 random seeds:
```bash
python scripts/run_e7_ablation_experiment.py
```
*Outputs*: `results/metrics/e7_ablation_results.csv`, `results/metrics/e7_ablation_summary.csv`, `results/tables/table7_ablation_comparison.md`

### Master Audit Reproduction (All Experiments E1–E8)
Executes all benchmarks end-to-end and archives verified outputs to a timestamped directory:
```bash
python scripts/run_audit_reproduction.py
```
*Outputs*: `results/audit_rerun_20261011/audit_reproduction_manifest.json`

### Extended Statistical Hypothesis Testing
Computes paired $t$-tests, exact 95% confidence intervals, Holm-Bonferroni corrections, and Cohen's $d$ effect sizes:
```bash
python scripts/compute_extended_statistics.py
```
*Outputs*: `results/metrics/extended_statistical_tests.json`, `results/tables/extended_statistical_tests.md`

---

## 4. Automated Test Suite Execution

Run the complete 30-test verification suite with JUnit XML reporting:
```bash
python -m pytest --junitxml=results/test_report.xml -v
```
**Expected Outcome**: `30 passed in ~28s (100.0%)`.

---

## 5. Repository Structure

```
├── data/
│   └── processed/recovery/      # Preprocessed partitions (recovery_processed.npz) and scaler
├── docs/                        # Formal research audit reports, threat models, and checklists
│   ├── DATA_LEAKAGE_AUDIT.md    # Provenance trace & duplicate overlap reconciliation
│   ├── SECURITY_THREAT_MODEL.md # Adversary hierarchy & local hash chain rewrite boundary proof
│   ├── FINAL_LIMITATIONS_AND_THREATS.md # Unvarnished disclosure of operational constraints
│   ├── FINAL_CLAIM_EVIDENCE_MATRIX.md   # Traceability mapping of all 18 manuscript claims
│   ├── FINAL_SUBMISSION_CHECKLIST.md    # Verification gate checklist across all 6 audit gates
│   └── FINAL_SUBMISSION_DECISION.md     # Formal submission gate verdict and recommendations
├── paper/                       # Publication manuscripts
│   ├── manuscript.md            # Formatted Markdown submission draft
│   ├── manuscript.tex           # IEEEtran LaTeX source code
│   └── tables/                  # TeX formatted tables (Table 7)
├── results/                     # Empirical benchmark metrics, tables, and figures
│   ├── metrics/                 # Raw and summary CSV/JSON result artifacts
│   ├── tables/                  # Formatted Markdown tables
│   ├── figures/                 # Performance visualisations (Figure 7)
│   └── audit_rerun_20261011/    # Timestamped master audit reproduction artifacts and manifest
├── scripts/                     # Standalone, reproducible benchmark execution scripts
├── src/                         # Core modular pipeline source code
│   ├── detection/               # Autoencoders, Isolation Forest, EWMA thresholding
│   ├── response/                # IoTDefenseEnv, Q-Learning, DQN, Rule-Based policies
│   ├── crypto/                  # NIST FIPS 203 ML-KEM, HKDF, AES-256-GCM AEAD
│   ├── integrity/               # Salted SHA-256, HMAC-SHA-256, Blockchain Audit Log
│   └── pipeline/                # Synchronous integrated framework pipeline
└── tests/                       # Pytest automated test suite (30/30 unit tests)
```

---

## 6. Ethics, Data Licensing & Citation

- **Dataset License**: CICIoT2023 is released under the Creative Commons Attribution 4.0 International (CC BY 4.0) License by the Canadian Institute for Cybersecurity (CIC).
- **Redistribution Policy**: Raw PCAP data files are not redistributed in this repository; processed numerical feature arrays (`recovery_processed.npz`) are provided strictly for academic verification.
- **Citation**: If using this codebase or benchmark methodology, please cite both our framework paper and the underlying dataset:
```bibtex
@article{ciciot2023,
  title={{CICIoT2023}: A Real-Time Dataset and Benchmark for Large-Scale Attacks in {IoT} Environment},
  author={Neto, E. C. P. and Dadkhah, S. and Ferreira, R. and Zohourian, A. and Lu, R. and Ghorbani, A. A.},
  journal={Sensors},
  volume={23},
  number={13},
  pages={5941},
  year={2023}
}
```
