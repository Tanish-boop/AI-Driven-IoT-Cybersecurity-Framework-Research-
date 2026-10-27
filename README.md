# AI-Driven-IoT-Cybersecurity-Framework-Research-

## An AI-Driven Adaptive Cybersecurity Framework for IoT: Anomaly Detection, Dynamic Thresholding, Un-Contaminated Reinforcement Learning Defense, Post-Quantum Cryptography, and Tamper-Evident Audit Logging

**Repository**: `https://github.com/Tanish-boop/AI-Driven-IoT-Cybersecurity-Framework-Research-`  
**Target Submission**: IEEE Access (Empirical Benchmark Track)  
**Public Benchmark**: CICIoT2023 (*Neto et al., Sensors 2023*)  
**Reference Base Paper**: M. M. Saeed, *"An AI-Driven Cybersecurity Framework for IoT: Integrating LSTM-Based Anomaly Detection, Reinforcement Learning, and Post-Quantum Encryption,"* *IEEE Access*, vol. 13, pp. 104027–104036, 2025.  
**Methodological Synthesis**: Grounded in the Cross-Layer Critical Review Paper (*"Beyond Component Stacking: A Critical Methodological Review of Hybrid IoT Intrusion Detection Architectures"*, 2026), Mazinani et al. (*Future Internet*, 2026), and Sun et al. (*ICML*, 2024).

---

## 1. Executive Summary & Research Mission

This repository provides an open-source, scientifically validated implementation study evaluating an integrated five-stage IoT cybersecurity framework on **CICIoT2023** across 5 standardized random seeds ($42, 123, 456, 789, 2026$) under strictly isolated partitions.

### Core Problems Addressed from Existing Literature:
1. **The Saeed (2025) Baseline Gap**:
   - Saeed (*IEEE Access 2025*) proposed combining LSTM anomaly detection, Q-learning mitigation, and lattice cryptography, but reported zero global test-stream metrics (F1, Precision, Recall) and explicitly cited static thresholding as a key limitation, calling for dynamic thresholding.
   - We implement and benchmark this architecture on the public **CICIoT2023** dataset, providing the empirical baseline that was missing.
2. **The Sequence Modeling Fallacy on Tabular NetFlows**:
   - Applying sliding-window recurrent models (LSTM-AE, GRU-AE) to tabular flow rows without temporal continuity creates sequence boundary corruption and severe false-alarm inflation.
   - Mazinani et al. (*Future Internet*, 2026) demonstrated on an STM32H7 microcontroller that MLP and TCN achieve the highest trade-off scores with INT8 quantization, whereas LSTM incurs high latency and memory overhead.
   - We show that sample-level Dense Autoencoders ($L=1$) achieve $\text{F1} = 88.54\% \pm 0.13\%$ with $1.35\,\mu\text{s}$ latency and 10,775 parameters ($12.0\times$ fewer parameters and $3.67\times$ faster than LSTM-AE).
3. **The Score-to-Decision Breakdown (Thresholding Failures)**:
   - **Raw EWMA**: Suffers from **Upward Inflation Collapse** during attacks (threshold inflates by $2.4\times 10^6\times$, Recall drops to $0.03\%$, FNR $99.97\%$).
   - **Excluded EWMA**: Suffers from **Downward Censoring Collapse** (excluding samples above threshold truncates the upper tail, causing estimated mean/variance to steadily decline; the threshold drops by ~90%, blowing up nominal False Positive Rate to $13.60\%$).
   - **Fixed 95th Percentile**: Completely brittle under traffic rate surges (under $2.0\times$ feature rate drift, FPR explodes from $5.00\%$ to $23.75\%$).
   - **Our Solution (TCA-Adaptive & CGB-Adaptive)**: Implements truncation-bias correction factor $\kappa = \tau_{\text{calib}} / (\mu_{\text{trunc}} + k \cdot \sigma_{\text{trunc}})$, envelope bounding $[\rho_{\min} \cdot \tau_{\text{calib}}, \rho_{\max} \cdot \tau_{\text{calib}}]$, winsorized updates, and incident freeze. TCA eliminates downward drift (FPR $3.08\% - 5.01\%$ on nominal stream) and cuts false alarms under $2.0\times$ feature rate drift by up to $65\%$ (FPR $8.25\% - 11.25\%$).

---

## 2. Experimental Benchmark Results (5-Seed Verified Summary)

All benchmarks are evaluated across 5 random seeds ($42, 123, 456, 789, 2026$) on the held-out test split of CICIoT2023 ($N=100,000$, 14,911 benign, 85,089 attack) under an enforced **Test-Label Firewall**.

### A. Performance Across Five Evaluated Scenarios

| Scenario | Threshold Method | Precision | Recall | F1-Score | False Positive Rate (FPR) | Max Inflation |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **Scenario 1: Nominal Clean Stream** | **Fixed 95th** | $98.93\% \pm 0.03\%$ | $80.13\% \pm 0.22\%$ | $88.54\% \pm 0.13\%$ | $4.93\% \pm 0.13\%$ | $1.00\times$ |
| | **Excluded EWMA** | $97.24\% \pm 0.22\%$ | $84.01\% \pm 0.23\%$ | $90.14\% \pm 0.18\%$ | $13.60\% \pm 1.10\%$ | $4.07\times$ |
| | **Raw EWMA (Un-Guarded)** | $100.00\% \pm 0.00\%$ | $0.01\% \pm 0.00\%$ | $0.03\% \pm 0.01\%$ | $0.00\% \pm 0.00\%$ | **$2,403,808\times$** *(Collapse)* |
| | **CGB Adaptive** | $98.19\% \pm 0.05\%$ | $82.01\% \pm 0.33\%$ | $89.37\% \pm 0.21\%$ | $8.64\% \pm 0.23\%$ | $0.68\times$ |
| | **TCA-Adaptive (Proposed)** | $98.91\% \pm 0.06\%$ | $80.00\% \pm 0.20\%$ | $88.46\% \pm 0.15\%$ | **$5.01\% \pm 0.15\%$** | $1.42\times$ |
| | **Supervised XGBoost Oracle** | $99.67\% \pm 0.02\%$ | $86.62\% \pm 0.09\%$ | $92.69\% \pm 0.04\%$ | $1.62\% \pm 0.12\%$ | N/A |
| **Scenario 2: Synthetic Score Shift (1.8x)** | **Fixed 95th** | $97.53\% \pm 0.11\%$ | $80.13\% \pm 0.22\%$ | $87.98\% \pm 0.16\%$ | $11.56\% \pm 0.51\%$ | $1.00\times$ |
| | **Excluded EWMA** | $95.64\% \pm 0.40\%$ | $82.20\% \pm 0.28\%$ | $88.41\% \pm 0.19\%$ | $21.41\% \pm 2.08\%$ | $4.07\times$ |
| | **TCA-Adaptive (Proposed)** | $98.71\% \pm 0.08\%$ | $78.08\% \pm 0.22\%$ | $87.21\% \pm 0.18\%$ | **$5.75\% \pm 0.21\%$** | $2.14\times$ |
| **Scenario 3: Feature-Level Rate Drift (2.0x)** | **Fixed 95th** | $94.36\% \pm 0.30\%$ | $80.13\% \pm 0.22\%$ | $86.66\% \pm 0.21\%$ | $27.33\% \pm 1.52\%$ | $1.00\times$ |
| | **Excluded EWMA** | $92.27\% \pm 0.48\%$ | $82.89\% \pm 0.50\%$ | $87.33\% \pm 0.15\%$ | $39.63\% \pm 2.86\%$ | $4.07\times$ |
| | **TCA-Adaptive (Fast)** | $98.16\% \pm 0.12\%$ | $77.07\% \pm 0.25\%$ | $86.35\% \pm 0.20\%$ | **$8.25\% \pm 0.35\%$** | $2.98\times$ |
| **Scenario 4: Attack Flood Episode (20k flood)** | **Fixed 95th** | $97.51\% \pm 0.06\%$ | $80.05\% \pm 0.20\%$ | $87.92\% \pm 0.13\%$ | $5.02\% \pm 0.12\%$ | $1.00\times$ |
| | **Raw EWMA** | $4.64\% \pm 0.70\%$ | $0.03\% \pm 0.00\%$ | $0.06\% \pm 0.01\%$ | $1.46\% \pm 0.12\%$ | **$2,403,808\times$** *(FNR 99.97%)* |
| | **Excluded EWMA** | $92.31\% \pm 0.38\%$ | $83.66\% \pm 0.27\%$ | $87.78\% \pm 0.24\%$ | $17.09\% \pm 0.92\%$ | $4.07\times$ |
| | **CGB Adaptive** | $95.50\% \pm 0.12\%$ | $82.15\% \pm 0.33\%$ | $88.32\% \pm 0.22\%$ | $9.49\% \pm 0.23\%$ | $0.69\times$ |
| | **TCA-Adaptive (Proposed)** | $97.60\% \pm 0.09\%$ | $79.18\% \pm 0.21\%$ | $87.43\% \pm 0.17\%$ | **$4.77\% \pm 0.16\%$** | $1.64\times$ |
| **Scenario 5: Mixed Drift + Attack Flood** | **Fixed 95th** | $96.42\% \pm 0.11\%$ | $80.08\% \pm 0.20\%$ | $87.49\% \pm 0.14\%$ | $7.31\% \pm 0.22\%$ | $1.00\times$ |
| | **Excluded EWMA** | $91.28\% \pm 0.42\%$ | $83.37\% \pm 0.32\%$ | $87.14\% \pm 0.24\%$ | $19.60\% \pm 1.05\%$ | $4.07\times$ |
| | **TCA-Adaptive (Proposed)** | $97.24\% \pm 0.10\%$ | $78.15\% \pm 0.24\%$ | $86.65\% \pm 0.20\%$ | **$5.47\% \pm 0.22\%$** | $2.73\times$ |

---

## 3. Cross-Layer System Architecture

The pipeline consists of five synchronized defense modules designed for IoT edge nodes:

```
[Raw Network Packets] 
        │
        ▼ (Stage 1: 39 Flow Statistics, Purge Identifiers)
[StandardScaler Normalization] (Fitted strictly on benign X_train)
        │
        ▼ (Stage 2: Sample-Level Dense Autoencoder, L=1)
[Reconstruction Error Et] ──> [TCA / CGB Adaptive Threshold Controller]
        │                           │
        │                           ▼ Binary Alert Decision (yt)
        ▼ (Stage 3: Un-Contaminated Markov Decision Process)
[Reinforcement Learning Defense Policy] (DQN / Tabular Q)
        ├── Action: Allow (0)
        ├── Action: Rate-Limit (1)
        ├── Action: Deep Packet Inspection (2)
        └── Action: Quarantine / Block (3)
        │
        ▼ (Stage 4: Post-Quantum Transport Encryption)
[NIST FIPS 203 ML-KEM-768] ──> HKDF-SHA256 ──> [AES-256-GCM AEAD] (0.2758 ms setup)
        │
        ▼ (Stage 5: Forensic Integrity Audit Logging)
[Tamper-Evident Hash Chain Log] (hi = SHA-256(hi-1 || ri || seq_i), 0.0605 ms append)
```

### Module Performance Highlights:
- **Anomaly Detection**: Dense-AE ($39 \to 24 \to 12 \to 24 \to 39$), ReLU activations, MSE loss, $1.35\,\mu\text{s}$ per-event inference.
- **RL Defense (Stage 3)**: Deep Q-Network achieves **$71.26\% \pm 0.09\%$** attack containment with **$0.63\% \pm 0.46\%$** false block rate on held-out evaluation ($0.1160$~ms decision latency). Tabular Q achieves $0.00\%$ false block rate.
- **Post-Quantum Cryptography (Stage 4)**: NIST FIPS 203 ML-KEM-768 achieves $0.2758$~ms key encapsulation and $0.2905$~ms setup latency with $100\%$ tamper rejection against bit-flip attacks.
- **Evidence Audit Logging (Stage 5)**: Cryptographic hash chain achieves $0.0605$~ms append latency with $\mathcal{O}(1)$ verification scaling and exact tamper localization.
- **End-to-End Integrated Framework**: F1-Score of **$0.8968 \pm 0.0013$**, $81.01\% \pm 2.83\%$ attack containment, $0.9626 \pm 0.6304$~ms edge processing latency ($1,436.2 \pm 759.5$~events/s throughput).

---

## 4. Strict Methodological Safeguards & Data Protocols

1. **Test-Label Firewall**:
   - Ground truth test labels (`y_test`) are strictly blocked from being accessed by the threshold controllers or RL state.
   - Verified by unit test `test_firewall_rejection_of_labels`.
2. **Four-Way Partitioning Protocol**:
   - `X_train` ($100,000$ pure benign flows): Scaler fitting and unsupervised Autoencoder training.
   - `X_val` ($30,000$ pure benign flows): Offline threshold calibration and baseline parameter estimation.
   - `X_sup` ($40,000$ balanced benign/attack flows): Supervised XGBoost reference and RL policy training.
   - `X_test` ($100,000$ flows: 14,911 benign, 85,089 attack): **Strictly held-out evaluation split**.
3. **Cross-Partition Deduplication Sensitivity Audit**:
   - 1,457 cross-partition duplicate feature rows (e.g. uniform SYN flood packets) were purged to create a Clean Deduplicated Test Set ($N=98,543$).
   - Re-evaluation across all 5 seeds showed F1 shifted by at most $-0.0009$ ($-0.10\%$), proving metric stability.

---

## 5. Automated Test Suite Execution

The repository maintains an automated unit test suite verifying all invariants, mathematical constraints, and cryptographic primitives:

```bash
# Run the complete test suite
python -m pytest -v tests/
```

**Verified Test Result**:
```
============================= 40 passed in 35.24s =============================
```
- `test_e4_uncontaminated.py`: Split isolation, reward sensitivity, action bounds.
- `test_e5_crypto.py`: ML-KEM artifact sizes, key generation, tamper rejection.
- `test_e6_integrity.py`: Hash chain, HMAC, tamper detection (modification, deletion, insertion, reordering, rewrite).
- `test_e7_pipeline.py`: Full framework end-to-end and component ablations.
- `test_recovery_pipeline.py`: Leakage prevention, missing/infinite handling, reproducible splitting.
- `test_threshold_adaptation.py`: Fixed, UnGuarded, Excluded, CGB, and TCA controllers, decision invariants, step-size boundedness, flood resistance, label firewall rejection.

---

## 6. How to Reproduce All Experiments

### Step 1: Environment Setup
```bash
git clone https://github.com/Tanish-boop/AI-Driven-IoT-Cybersecurity-Framework-Research-.git
cd AI-Driven-IoT-Cybersecurity-Framework-Research-
pip install -r requirements.txt
```

### Step 2: Run the 5-Seed Validated Benchmark
```bash
python experiments/valid_evaluation_20261016/run_valid_evaluation.py
```
*Outputs*: `results_per_seed.csv`, `results_summary.csv`, `threshold_traces.npz`, `scenario_manifest.json`

### Step 3: Generate Publication Figures
```bash
python experiments/valid_evaluation_20261016/plot_valid_evaluation_figures.py
```
*Outputs*: `fig_tradeoff_f1_vs_fpr.png`, `fig_threshold_traces.png`, `fig_scenario_comparison.png`

### Step 4: Run the TCA Adaptive Threshold Calibration & Test
```bash
python experiments/tune_and_validate_tca.py
```

### Step 5: Run Component Microbenchmarks (E4, E5, E6, E7)
```bash
# E4: Un-contaminated RL defense
python scripts/run_e4_defense_experiment.py

# E5: NIST FIPS 203 ML-KEM cryptography
python scripts/run_e5_crypto_benchmark.py

# E6: Cryptographic audit logging
python scripts/run_e6_integrity_benchmark.py

# E7: Full integrated framework ablation
python scripts/run_e7_ablation_experiment.py
```

---

## 7. Repository Structure

```
├── configs/
│   └── preregistered_evaluation.yaml   # Pre-registered benchmark specifications
├── data/
│   └── processed/recovery/             # Preprocessed partitions (recovery_processed.npz) & scaler
├── docs/                               # Formal research audit reports & literature matrices
│   ├── VALIDITY_AUDIT.md               # Diagnosis and remediation of experimental issues
│   ├── RESULTS_RECONCILIATION.md       # Exact numerical reconciliation of all metrics
│   ├── RESEARCH_DIRECTION_DECISION.md  # Formulation of defensible research contributions
│   └── NEAREST_PRIOR_WORK.csv          # Matrix of 7 closest literature methods
├── experiments/                        # Verified experimental runners and evaluation results
│   ├── valid_evaluation_20261016/      # Pre-registered 5-seed benchmark scripts and outputs
│   ├── test_improved_thresholding.py   # Truncation-bias corrected adaptive controller test
│   ├── tune_and_validate_tca.py        # Supervisory calibration and 5-scenario evaluation
│   ├── test_percentile_sweep.py        # Pareto trade-off curve across target percentiles
│   └── test_feature_error_pooling.py   # Top-k and feature-normalized reconstruction analysis
├── paper/                              # IEEE Access draft manuscript and assets
│   ├── figures/                        # Publication figures (300 DPI)
│   ├── references.bib                  # BibTeX references
│   └── IEEE_Access_Final_Manuscript.pdf# Working preprint PDF
├── scripts/                            # Standalone execution and PDF compilation scripts
├── src/                                # Framework modular implementation
│   ├── detection/                      # Dense Autoencoders and anomaly estimators
│   ├── thresholding/                   # Fixed, EWMA, CGB, and TCA threshold controllers
│   ├── response/                       # IoTDefenseEnv, Q-Learning, DQN mitigation policies
│   ├── crypto/                         # NIST FIPS 203 ML-KEM-768 and AES-256-GCM AEAD
│   └── integrity/                      # Tamper-evident hash chain audit logging
└── tests/                              # Pytest test suite (40/40 passing)
```

---

## 8. Citation & Licensing

- **Code License**: Open-source under the MIT License.
- **Dataset License**: CICIoT2023 is released under the Creative Commons Attribution 4.0 International (CC BY 4.0) License by the Canadian Institute for Cybersecurity.
- **Citation**:
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
