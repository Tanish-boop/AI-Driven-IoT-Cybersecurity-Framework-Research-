# Experiment-to-Artifact Mapping Matrix

This document provides a machine-verifiable mapping between every experiment (E1–E8), its underlying execution script, configuration, raw data partition, output metrics file, and corresponding table/figure in the IEEE Access manuscript.

---

## 1. Experiment Mapping Table

| Exp ID | Experiment Focus | Execution Script | Training & Evaluation Splits | Primary Metric Output File | Paper Table / Figure | Automated Verification Test |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **E1** | Dense Autoencoder vs. Sequence Windows | `scripts/run_full_benchmark.py` | Train: $X_{\text{train}}$ ($100\text{k}$ benign)<br>Val: $X_{\text{val}}$ ($30\text{k}$ benign)<br>Eval: $X_{\text{test}}$ ($100\text{k}$) | `results/metrics/full_benchmark_summary.csv` | Table I, Fig. 1 | `tests/test_recovery_pipeline.py` |
| **E2** | Adaptive Thresholding (EWMA Methods) | `scripts/run_full_benchmark.py` | Val: $X_{\text{val}}$ (initialization)<br>Eval: $X_{\text{test}}$ ($100\text{k}$ stream) | `results/metrics/full_benchmark_summary.csv` | Table I, Fig. 1 | `tests/test_recovery_pipeline.py` |
| **E3** | Supervised XGBoost Oracle Reference | `scripts/run_full_benchmark.py` | Train: $X_{\text{sup}}$ ($40\text{k}$ balanced)<br>Eval: $X_{\text{test}}$ ($100\text{k}$) | `results/metrics/full_benchmark_summary.csv` | Table I | `tests/test_recovery_pipeline.py` |
| **E4** | Un-Contaminated RL Defense Policies | `scripts/run_e4_defense_experiment.py` | Train: $X_{\text{sup}}$ ($40\text{k}$)<br>Eval: $X_{\text{test}}[5000:10000]$ (S1)<br>$X_{\text{test}}[10000:15000]$ (S2) | `results/metrics/e4_policy_summary_corrected.csv` | Table III, Fig. 4 | `tests/test_e4_uncontaminated.py` |
| **E5** | NIST FIPS 203 Post-Quantum Cryptography | `scripts/run_e5_crypto_benchmark.py` | Microbenchmark on 64B, 256B, 1KiB, 4KiB payloads (100 trials) | `results/metrics/e5_summary.csv` | Table IV, Fig. 5 | `tests/test_e5_crypto.py` |
| **E6** | Tamper-Evident Forensic Audit Logging | `scripts/run_e6_integrity_benchmark.py` | Microbenchmark on 1KiB evidence records (100 trials) | `results/metrics/e6_summary.csv` | Table V, Fig. 6 | `tests/test_e6_integrity.py` |
| **E7** | Full Integrated Pipeline & Ablation Study | `scripts/run_e7_ablation_experiment.py` | Full 5-stage synchronous pipeline on $X_{\text{test}}[:5000]$ (5 seeds) | `results/metrics/e7_ablation_summary.csv` | Table VII, Fig. 7 | `tests/test_e7_pipeline.py` |
| **E8** | Synthetic Traffic Rate Stress Testing | `scripts/run_full_benchmark.py` | Benign test samples with $1.5\times$ and $2.0\times$ rate feature scaling | `results/metrics/full_benchmark_results.csv` | Table VIII, Fig. 2 | `tests/test_recovery_pipeline.py` |
| **Audit** | 5-Seed Deduplication Sensitivity Check | `scripts/evaluate_deduplication_sensitivity.py` | Full $X_{\text{test}}$ ($100\text{k}$) vs. Clean Deduplicated $X_{\text{test\_clean}}$ ($98,543$) | `results/metrics/deduplication_sensitivity_summary.csv` | Table II | `python scripts/evaluate_deduplication_sensitivity.py` |

---

## 2. Seed Directory & Deterministic Parameters
All stochastic experiments are evaluated across 5 random seeds:
- Seed List: `[42, 123, 456, 789, 2026]`
- Torch CPU Seed: `torch.manual_seed(seed)`
- NumPy Seed: `np.random.seed(seed)`
- Scikit-Learn / XGBoost Seed: `random_state=seed`

---

## 3. Data Integrity & Provenance Verification
- Input Data File: `data/processed/recovery/recovery_processed.npz`
- Normalizer Object: `data/processed/recovery/recovery_scaler.pkl`
  - Scaler fit sample count: `scaler.n_samples_seen_ = 100000` (strictly matches $X_{\text{train}}$ length).
- Master Automated Rerun Manifest: `results/audit_rerun_20261011/audit_reproduction_manifest.json` (713.19s execution time, Exit Code 0, 0 errors).
- Regression Test Suite: `results/final_submission_audit/test_report.xml` (30/30 tests passed, Exit Code 0).
