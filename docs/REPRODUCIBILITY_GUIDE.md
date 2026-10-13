# COMPREHENSIVE REPRODUCIBILITY GUIDE: AI-DRIVEN IOT CYBERSECURITY FRAMEWORK

**Target Submission**: IEEE Access  
**Repository**: `C:\Users\hp\OneDrive\Desktop\Research Experiments`  
**GitHub Link**: `https://github.com/Tanish-boop/AI-Driven-IoT-Cybersecurity-Framework-Research-.git`  
**Date**: October 2026  
**Status**: 100% Deterministic, Clean-Room Verified  

---

## 1. System Requirements & Environment Specifications

The entire research pipeline is designed for complete, clean-room reproducibility without proprietary hardware accelerators. All benchmarks are verified on standard x86-64 CPU hardware.

### 1.1. Recommended Hardware
- **Processor**: Intel Core i5/i7 (11th Gen or later) / AMD Ryzen 5/7 (4 cores, 8 threads minimum).
- **RAM**: 16 GB minimum (32 GB recommended for in-memory NetFlow processing).
- **Storage**: 15 GB available disk space (for raw parquet files, processed npz arrays, and model checkpoints).
- **Operating System**: Windows 10/11 (PowerShell 7+), Linux (Ubuntu 22.04+ LTS), or macOS.

### 1.2. Software & Dependencies
- **Python Runtime**: Python 3.11, 3.12, or 3.13 (Verified on Python 3.13.4).
- **Core Dependencies**:
  ```text
  torch>=2.2.0
  scikit-learn>=1.4.0
  xgboost>=2.0.0
  cryptography>=42.0.0
  numpy>=1.26.0
  pandas>=2.2.0
  scipy>=1.12.0
  matplotlib>=3.8.0
  seaborn>=0.13.0
  reportlab>=4.1.0
  pytest>=8.0.0
  ```

---

## 2. Environment Setup

### 2.1. Clone Repository & Setup Virtual Environment
```bash
# Clone the verified research repository
git clone https://github.com/Tanish-boop/AI-Driven-IoT-Cybersecurity-Framework-Research-.git
cd AI-Driven-IoT-Cybersecurity-Framework-Research-

# Create virtual environment
python -m venv venv

# Activate environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate environment (Linux / macOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2.2. Run Test Suite
Before executing experiments, run the 30-case validation test suite to confirm mathematical and functional integrity:
```bash
python -m pytest tests/ -v
# Expected result: 30 passed in ~40 seconds
```

---

## 3. Data Provenance & Split Verification

The experiments utilize the **CICIoT2023** benchmark dataset (University of New Brunswick). The preprocessed partition file is stored at `data/processed/recovery/recovery_processed.npz`.

### 3.1. Partition Specifications
- **$X_{\text{train}}$**: 100,000 samples, 100% Benign traffic (Unsupervised baseline training).
- **$X_{\text{val}}$**: 30,000 samples, 100% Benign traffic (Threshold calibration).
- **$X_{\text{sup}}$**: 40,000 samples, 85% Attack / 15% Benign (Supervised reference & RL training).
- **$X_{\text{test}}$**: 100,000 samples, 85% Attack / 15% Benign (Identical held-out evaluation).
- **Feature Dimension**: 39 normalized NetFlow statistical attributes.

### 3.2. Data Integrity Verification
```python
import numpy as np
data = np.load('data/processed/recovery/recovery_processed.npz')
print("Train shape:", data['X_train'].shape) # (100000, 39)
print("Val shape:  ", data['X_val'].shape)   # (30000, 39)
print("Sup shape:  ", data['X_sup'].shape)   # (40000, 39)
print("Test shape: ", data['X_test'].shape)  # (100000, 39)
```

---

## 4. Step-by-Step Reproduction Workflow (E1–E8)

Each experiment can be executed individually or in an automated batch sequence.

### Phase 1: Model Selection & Baseline Comparison (E1)
Evaluates Dense-AE, Saeed-adapted LSTM-AE ($L=1$), GRU-AE, Isolation Forest, and XGBoost Oracle across 5 random seeds:
```bash
python scripts/run_fair_head_to_head_comparison.py
# Outputs:
#   docs/FAIR_COMPARISON_RESULTS.csv
#   results/metrics/fair_comparison_results.csv
#   results/metrics/fair_comparison_per_seed.csv
```

### Phase 2: Full Benchmark & Adaptive Thresholding (E2 & E3)
Evaluates Fixed 95th/99th, UnGuarded EWMA, Excluded EWMA, Guarded EWMA, and synthetic feature scaling stress tests (1.5x, 2.0x):
```bash
python scripts/run_full_benchmark.py
# Outputs:
#   results/metrics/full_benchmark_results.csv
#   results/metrics/full_benchmark_summary.csv
#   results/metrics/statistical_tests.json
```

### Phase 3: Deduplication Sensitivity & Leakage Audit (E8)
Evaluates sensitivity to cross-split duplicate removal across 5 random seeds (Full $N=100,000$ vs Clean $N=98,543$):
```bash
python scripts/evaluate_deduplication_sensitivity.py
# Outputs:
#   results/metrics/deduplication_sensitivity_summary.csv
#   results/metrics/deduplication_sensitivity_per_seed.csv
```

### Phase 4: Defensive Incident Response RL Policy (E4)
Evaluates Rule-Based, Tabular Q-Learning, and Deep Q-Network under strict un-contaminated split isolation ($X_{\text{sup}}$ train, $X_{\text{test}}$ eval):
```bash
python scripts/run_e4_defense_experiment.py
# Outputs:
#   results/metrics/e4_policy_results_corrected.csv
#   results/metrics/e4_policy_summary_corrected.csv
#   results/metrics/e4_reward_sensitivity.csv
```

### Phase 5: NIST FIPS 203 ML-KEM PQC Benchmark (E5)
Evaluates post-quantum key encapsulation latency, throughput, and ciphertext expansion across ML-KEM-512, 768, and 1024:
```bash
python scripts/run_e5_crypto_benchmark.py
# Outputs:
#   results/metrics/e5_raw_results.csv
#   results/metrics/e5_summary.csv
#   results/metrics/e5_crypto_environment.json
```

### Phase 6: Tamper-Evident Hash Chain Audit Log (E6)
Evaluates append throughput, verification latency, storage overhead, and tamper detection against single-bit, payload, and pointer attacks:
```bash
python scripts/run_e6_integrity_benchmark.py
# Outputs:
#   results/metrics/e6_raw_results.csv
#   results/metrics/e6_summary.csv
#   results/metrics/e6_scaling_summary.csv
#   results/metrics/e6_integrity_environment.json
```

### Phase 7: Integrated Multi-Stage Pipeline Ablation (E7)
Evaluates end-to-end integration across all 5 architectural modules and records single-stage ablation impacts:
```bash
python scripts/run_e7_ablation_experiment.py
# Outputs:
#   results/metrics/e7_ablation_results.csv
#   results/metrics/e7_ablation_summary.csv
#   results/tables/table7_ablation_comparison.md
```

### Phase 8: Statistical Hypothesis Testing
Computes Wilcoxon signed-rank tests, Mann-Whitney U tests, Cohen's $d$, and 95% confidence intervals:
```bash
python scripts/compute_extended_statistics.py
# Outputs:
#   results/metrics/extended_statistical_tests.json
#   results/tables/extended_statistical_tests.md
```

### Phase 9: Figure & Table Regeneration
Regenerates all publication figures and LaTeX/Markdown tables strictly from raw metric CSVs:
```bash
python scripts/generate_all_verified_figures.py
python scripts/generate_tables.py
# Outputs:
#   paper/figures/fig1_architecture.png
#   paper/figures/fig2_roc_curves.png
#   paper/figures/fig3_threshold_adaptation.png
#   paper/figures/fig4_per_attack_recall.png
#   paper/figures/fig5_deduplication_delta.png
#   paper/figures/fig6_rl_containment.png
#   paper/figures/fig7_pqc_tradeoff.png
#   paper/figures/fig8_pipeline_latency.png
```

### Phase 10: PDF Compilation
Compiles the complete double-column IEEE Access manuscript using ReportLab:
```bash
python scripts/build_full_ieee_access_pdf.py
# Outputs:
#   paper/IEEE_Access_Final_Manuscript.pdf (1.75 MB, 6 pages, verified)
```

---

## 5. Automated Master Reproduction Runner

To execute all benchmarks (E1–E8) in a single verifiable sequence with automatic environment logging, SHA-256 artifact hashing, and archive backup:

```bash
python scripts/run_audit_reproduction.py
```
This produces `results/audit_rerun_20261011/audit_reproduction_manifest.json` containing exact start times, runtimes, exit codes, and output cryptographic hashes.

---

## 6. Expected Execution Times

| Step | Script | Expected Wall-Clock Duration |
| :--- | :--- | :--- |
| Test Suite | `pytest tests/` | ~38 seconds |
| E1 Comparison | `run_fair_head_to_head_comparison.py` | ~180 seconds |
| E2 & E3 Benchmark | `run_full_benchmark.py` | ~120 seconds |
| E8 Deduplication | `evaluate_deduplication_sensitivity.py` | ~45 seconds |
| E4 RL Defense | `run_e4_defense_experiment.py` | ~60 seconds |
| E5 PQC Crypto | `run_e5_crypto_benchmark.py` | ~35 seconds |
| E6 Hash Logging | `run_e6_integrity_benchmark.py` | ~45 seconds |
| E7 Ablation | `run_e7_ablation_experiment.py` | ~90 seconds |
| Figures & Tables | `generate_all_verified_figures.py` | ~25 seconds |
| PDF Build | `build_full_ieee_access_pdf.py` | ~15 seconds |
| **Total Pipeline** | **Full End-to-End Execution** | **~11 minutes** |

---

## 7. Troubleshooting & Verification Gates

1. **Memory Errors**: If encountering `MemoryError` during sequence loading, ensure that NetFlow data is processed in batches (default `batch_size=512` or `1024`).
2. **Missing Checkpoints**: If evaluating standalone inference, ensure model checkpoints exist in `data/models/` (`dense_ae.pt`, `lstm_ae.pt`, `gru_ae.pt`, `xgb_oracle.pkl`, `isolation_forest.pkl`). Running `scripts/run_baselines.py` or `scripts/run_fair_head_to_head_comparison.py` automatically generates all checkpoints.
3. **Reproducibility Guarantee**: All random seeds are explicitly fixed (`[42, 123, 456, 789, 2026]`). Python's `random.seed()`, NumPy's `np.random.seed()`, and PyTorch's `torch.manual_seed()` are initialized deterministically in every training loop.
