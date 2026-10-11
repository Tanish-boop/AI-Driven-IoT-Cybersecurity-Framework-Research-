# An AI-Driven Adaptive Cybersecurity Framework for IoT: Anomaly Detection, Dynamic Thresholding, Un-Contaminated Reinforcement Learning Defense, Post-Quantum Cryptography, and Tamper-Evident Audit Logging

Official empirical replication package and submission bundle for the research article submitted to ***IEEE Access***.

---

## 1. Overview & Research Contributions
This repository contains the complete source code, experimental protocols, trained models, and raw verification logs for our five-stage integrated IoT edge cybersecurity framework evaluated on **CICIoT2023** across 5 standardized random seeds ($42, 123, 456, 789, 2026$):
1. **Unsupervised Anomaly Detection**: Sample-level Dense Autoencoder ($L=1$) that eliminates sliding sequence window boundary leakage.
2. **Adaptive Anomaly Thresholding**: Introduces **Excluded EWMA** thresholding that resolves the catastrophic threshold inflation collapse suffered by un-guarded moving averages during sustained attack floods.
3. **Un-Contaminated Defensive RL Response**: Deep Q-Networks (DQN) and Tabular Q-Learning trained strictly on dedicated supervisory data ($X_{\text{sup}}$) and evaluated on held-out test data ($X_{\text{test}}$).
4. **Post-Quantum Cryptography**: Standardized **NIST FIPS 203 ML-KEM-768** key encapsulation paired with AES-256-GCM AEAD encryption achieving sub-millisecond edge setup ($0.2758$~ms KEM, $0.2905$~ms first-message setup) and 100% tamper rejection.
5. **Tamper-Evident Forensic Logging**: Cryptographic hash-chain sequencing ensuring $\mathcal{O}(1)$ append latency ($0.0605$~ms) and provable sequence tamper localization.

---

## 2. Hardware, OS, & Environment Specifications
All experiments and microbenchmarks were conducted on:
- **Host CPU Architecture**: AMD64 (x86_64, 3.40 GHz base clock)
- **Host Operating System**: Microsoft Windows 11 Enterprise (Build 26100) / Linux compatible
- **System Memory**: 16.0 GB RAM
- **Python Version**: Python 3.13.4 (compatible with $\ge 3.10$)
- **Core Libraries**:
  - `torch`: 2.6.0 (CPU execution mode)
  - `scikit-learn`: 1.6.1
  - `xgboost`: 2.1.4
  - `numpy`: 2.2.3
  - `pandas`: 2.2.3
  - `scipy`: 1.15.2
  - `cryptography`: 44.0.1
  - `pytest`: 9.0.3

---

## 3. Dataset Acquisition & Lawful Access
The evaluation is conducted on **CICIoT2023** (Neto et al., *Sensors*, 2023).
- **Official Dataset Source**: Available through the Canadian Institute for Cybersecurity (CIC), University of New Brunswick:  
  [https://www.unb.ca/cic/datasets/iot-dataset-2023.html](https://www.unb.ca/cic/datasets/iot-dataset-2023.html)
- **HuggingFace Mirror**: `siyam21/CIC-IoT-2023`
- **Feature Schema**: 39 numerical flow statistical features. Identity metadata (`src_ip`, `dst_ip`, `src_port`, `dst_port`, `Timestamp`, `flow_id`) are explicitly excluded.
- **Partition Structure**:
  - $X_{\text{train}}$: 100,000 pure benign flows.
  - $X_{\text{val}}$: 30,000 pure benign flows.
  - $X_{\text{sup}}$: 40,000 50/50 balanced flows.
  - $X_{\text{test}}$: 100,000 held-out flows (14,911 benign, 85,089 attack).

*Data Redistribution Policy*: In accordance with the CICIoT2023 terms of use, raw multi-gigabyte parquet captures are not redistributed inside this repository. Run the preprocessing pipeline below to generate the exact research partitions.

---

## 4. Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Tanish-boop/AI-Driven-IoT-Cybersecurity-Framework-Research-.git
   cd AI-Driven-IoT-Cybersecurity-Framework-Research-
   ```

2. **Create a clean virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Linux / macOS
   # OR on Windows:
   .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 5. Execution Commands for Experiments E1–E8

All experiments are fully deterministic and can be reproduced independently:

### A. Run Experiments E1, E2, E3, and E8 (Full Benchmark)
Executes Dense-AE, Isolation Forest, XGBoost Oracle, EWMA thresholding variants, and synthetic rate feature scaling across 5 seeds ($42, 123, 456, 789, 2026$):
```bash
python scripts/run_full_benchmark.py
```
*Expected Outputs*: `results/metrics/full_benchmark_results.csv`, `results/metrics/full_benchmark_summary.csv`  
*Execution Time*: $\approx 120$ seconds.

### B. Run Experiment E4 (Un-Contaminated RL Defense Policies)
Trains Tabular Q-Learning and Deep Q-Networks on $X_{\text{sup}}$ and evaluates on held-out test scenarios:
```bash
python scripts/run_e4_defense_experiment.py
```
*Expected Outputs*: `results/metrics/e4_policy_results_corrected.csv`, `results/metrics/e4_policy_summary_corrected.csv`  
*Execution Time*: $\approx 90$ seconds.

### C. Run Experiment E5 (NIST FIPS 203 ML-KEM Microbenchmark)
Microbenchmarks ML-KEM-512, 768, 1024, HKDF-SHA256, and AES-256-GCM AEAD over 100 repeated trials:
```bash
python scripts/run_e5_crypto_benchmark.py
```
*Expected Outputs*: `results/metrics/e5_summary.csv`, `results/metrics/e5_crypto_environment.json`  
*Execution Time*: $\approx 30$ seconds.

### D. Run Experiment E6 (Integrity Verification & Audit Logging)
Evaluates Salted SHA-256, HMAC-SHA-256, and Hash-Chain append/verify latencies across 100 trials:
```bash
python scripts/run_e6_integrity_benchmark.py
```
*Expected Outputs*: `results/metrics/e6_summary.csv`  
*Execution Time*: $\approx 45$ seconds.

### E. Run Experiment E7 (Full Integrated Pipeline Ablation)
Evaluates the complete synchronous 5-stage pipeline and 5 component ablation variants across 5 seeds:
```bash
python scripts/run_e7_ablation_experiment.py
```
*Expected Outputs*: `results/metrics/e7_ablation_results.csv`, `results/metrics/e7_ablation_summary.csv`  
*Execution Time*: $\approx 350$ seconds.

### F. Run 5-Seed Deduplication Sensitivity Analysis
Evaluates the core models on the Full Test Set ($N=100\text{k}$) vs. Clean Deduplicated Test Set ($N=98,543$) across all 5 seeds:
```bash
python scripts/evaluate_deduplication_sensitivity.py
```
*Expected Outputs*: `results/metrics/deduplication_sensitivity_per_seed.csv`, `results/metrics/deduplication_sensitivity_summary.csv`  
*Execution Time*: $\approx 75$ seconds.

### G. Master Automated Full Rerun (E1–E8 in One Command)
Reruns all experiments sequentially, verifying exit codes and logging SHA-256 hashes into a master manifest:
```bash
python scripts/run_master_audit_rerun.py
```
*Expected Manifest*: `results/audit_rerun_20261011/audit_reproduction_manifest.json` (713.19s total execution).

---

## 6. Regression Test Suite
Run the 30-item regression test suite covering all modules, threat tests, and mathematical invariant checks:
```bash
python -m pytest --junitxml=results/final_submission_audit/test_report.xml
```
*Expected Result*: **30 passed in ~50 seconds (100.0% pass rate)**.

---

## 7. Instructions for Compiling LaTeX Manuscript to PDF
The complete IEEE Access LaTeX source is located in `submission/paper/`:

### Option A: Overleaf (Recommended)
1. Navigate to [Overleaf](https://www.overleaf.com) and create a **New Project** $\to$ **Upload Project**.
2. Upload the contents of `submission/paper/` (including `ieee_access_manuscript.tex`, `references.bib`, `ieeeaccess.cls`, `IEEEtran.cls`, `Logo.png`, `notaglineLogo.png`, `bullet.png`, and the `figures/` directory).
3. Set compiler to **pdfLaTeX** and compile.

### Option B: Local TeX Live / MiKTeX
```bash
cd submission/paper
pdflatex ieee_access_manuscript.tex
bibtex ieee_access_manuscript
pdflatex ieee_access_manuscript.tex
pdflatex ieee_access_manuscript.tex
```

---

## 8. Limitations & Methodological Disclosures
1. **Pre-Shuffled Dataset Origin**: Public CICIoT2023 records were shuffled across captures by the original dataset authors. Our 5-seed duplicate-exclusion sensitivity test proves that repeated flow feature patterns shift F1-scores by less than $0.1\%$, but cross-environment device generalization requires independent multi-testbed evaluation.
2. **Local Storage Rewrite Boundary**: Append-only cryptographic hash chaining provides sequence tamper localization against unprivileged adversaries ($\mathcal{A}_{\text{proc}}$), but external root tip anchoring is required to resist full local rewrite by privileged root host adversaries ($\mathcal{A}_{\text{root}}$).
3. **Hardware Scope**: Latency ($0.3781$~ms) and throughput ($2,652.4$~events/s) were measured on an AMD64 host edge gateway (3.40 GHz). Constrained microcontrollers (<100 MHz) require fixed-point quantization and assembly optimization.
4. **Adaptive Threshold Trade-Off**: Excluded EWMA gains $+3.88\%$ recall and surge stability, but incurs an empirical $13.6\%$ false positive rate on bursty benign flows.

---

## 9. License & Citation
- Code released under the **MIT License** (see `LICENSE`).
- To cite this work, refer to `CITATION.cff`.
