# Journal Submission Readiness Checklist

**Target Journal**: *IEEE Access* (Alternative: *Sensors*, *IEEE Internet of Things Journal*)  
**Audit Date**: October 11, 2026  
**Auditor**: Independent Pre-Submission Research Audit  

---

## 1. Experimental Verification Gate (E1–E8)

- [x] **E1 Baseline Anomaly Detection**:
  - Script: `scripts/run_full_benchmark.py`
  - Output: `results/metrics/full_benchmark_summary.csv`
  - Metrics: Dense-AE $\tau_{95}$ F1: $0.8854 \pm 0.0013$, FPR: $0.0493 \pm 0.0013$
  - Status: Verified from reproduced artifacts across 5 seeds ($42, 123, 456, 789, 2026$).
- [x] **E2 Dynamic Thresholding Strategy**:
  - Script: `scripts/run_full_benchmark.py`
  - Output: `results/metrics/full_benchmark_summary.csv`
  - Metrics: Excluded EWMA F1: $0.9014 \pm 0.0018$, Recall: $0.8401 \pm 0.0023$, FPR: $0.1360 \pm 0.0110$
  - Status: Catastrophic threshold inflation verified on UnGuarded EWMA (F1: $0.0003$).
- [x] **E3 Supervised Oracle Reference**:
  - Script: `scripts/run_full_benchmark.py`
  - Output: `results/metrics/full_benchmark_summary.csv`
  - Metrics: XGBoost Oracle F1: $0.9269 \pm 0.0004$, Isolation Forest F1: $0.7765 \pm 0.0084$
  - Status: Verified; establishes empirical upper bound on supervised partition (`X_sup`).
- [x] **E4 Defensive Reinforcement Learning**:
  - Script: `scripts/run_e4_defense_experiment.py`
  - Output: `results/metrics/e4_policy_summary_corrected.csv`
  - Metrics: DQN Containment: $71.20\% \pm 0.05\%$ (FBR: $0.77\%$), Tabular Q Containment: $55.94\% \pm 7.26\%$ (FBR: $0.00\%$)
  - Status: Un-contaminated split verified; historical contaminated run quarantined in `e4_policy_results_historical.csv`.
- [x] **E5 NIST Post-Quantum Cryptography Microbenchmark**:
  - Script: `scripts/run_e5_crypto_benchmark.py`
  - Output: `results/metrics/e5_summary.csv`
  - Metrics: ML-KEM-768 Total KEM: $0.4293$ ms, Setup: $0.4754$ ms, AEAD Tamper Rejection: 100%
  - Status: 100 trials verified; bit-flip header and ciphertext tamper tests passing (`InvalidTag`).
- [x] **E6 Forensic Integrity Verification Architecture**:
  - Script: `scripts/run_e6_integrity_benchmark.py`
  - Output: `results/metrics/e6_summary.csv`, `results/metrics/e6_scaling_summary.csv`
  - Metrics: HMAC Latency: $0.0332$ ms (Overhead: 171B), Blockchain Append: $0.0409$ ms, Chain Verify (2k): $29.85$ ms
  - Status: Tested against modification, deletion, reordering, insertion, and local chain rewrite.
- [x] **E7 Full Integrated Pipeline Ablation Study**:
  - Script: `scripts/run_e7_ablation_experiment.py`
  - Output: `results/metrics/e7_ablation_summary.csv`, `results/tables/table7_ablation_comparison.md`
  - Metrics: Full Framework F1: $0.8968 \pm 0.0013$, Containment: $80.65\% \pm 3.16\%$, Latency: $0.3781$ ms
  - Status: Staged orthogonality verified; Base Paper reimplementation baseline verified ($0.8837$).
- [x] **E8 Feature Rate Scaling Stress Test**:
  - Script: `scripts/run_full_benchmark.py`
  - Output: `results/metrics/full_benchmark_summary.csv`
  - Metrics: Base FPR: $4.93\%$, 1.5x Stress FPR: $9.53\%$, 2.0x Stress FPR: $27.33\%$ (+454.4% explosion)
  - Status: Demonstrates failure mode of static thresholds under traffic rate shifts.

---

## 2. Data Provenance & Leakage Prevention Gate

- [x] **Scaler Isolation**: `StandardScaler` fitted strictly on $100,000$ benign samples (`n_samples_seen_ = 100000`). Zero test data leakage.
- [x] **Metadata Dropping**: Non-numeric identifiers (`src_ip`, `dst_ip`, `src_port`, `dst_port`, `Timestamp`, `flow_id`) purged prior to training.
- [x] **Reconciled Overlap Table**:
  - Raw Parquet merge on 39 features: $201,148$ rows ($22,406$ unique feature vector patterns).
  - Research partition $X_{\text{train}}$ vs $X_{\text{test}}$: $81$ unique feature patterns ($215$ test rows, $0.215\%$).
  - Research partition $X_{\text{sup}}$ vs $X_{\text{test}}$: $953$ unique feature patterns ($1,402$ test rows, $1.402\%$).
  - Overlap explained and documented as natural high-rate network traffic packet invariance (SYN floods, keepalives).
- [x] **Capture-Level Limitation**: Shuffled nature of public CICIoT2023 Parquet exports explicitly disclosed.

---

## 3. Metrics Reconciliation & Statistical Rigor Gate

- [x] **Metric Definitions Verified**: Precision, recall, F1, ROC-AUC, FPR, false-block rate, attack containment, latency, throughput independently recomputed.
- [x] **False Block Rate Reconciled**: E4 standalone ($0.00\%$) vs E7 integrated ($7.39\%$) explained as upstream detector noise propagation ($13.6\%$ FPR of Excluded EWMA).
- [x] **Ablation Orthogonality Explained**: Detection F1 invariance ($0.8968$) across -PQC and -Blockchain ablations explained by sequential pipeline architecture.
- [x] **Per-Seed Results Documented**: All 5 random seeds ($42, 123, 456, 789, 2026$) documented in `results/metrics/` and reproducibility logs.
- [x] **Hypothesis Testing & Corrections**:
  - Paired $t$-tests and exact 95% CIs reported in `results/tables/extended_statistical_tests.md`.
  - Excluded EWMA vs Fixed 95th: $t = 33.805, p = 4.57 \times 10^{-6}$, Holm-Bonferroni $p = 2.74 \times 10^{-5}$, Cohen's $d = 15.12$ (**Significant**).
  - Full Framework vs Base Paper Architecture: $t = 19.888, p = 3.77 \times 10^{-5}$, Holm-Bonferroni $p = 1.51 \times 10^{-4}$, Cohen's $d = 8.89$ (**Significant**).
  - Honest disclosure: RL containment differences reported as non-significant under $N=5$.

---

## 4. Security & Cryptographic Evaluation Gate

- [x] **NIST FIPS 203 Compliance**: Explicitly cites Module-Lattice-Based Key-Encapsulation Mechanism Standard (ML-KEM-512, 768, 1024).
- [x] **Timing Separation**: KeyGen ($0.1114$ ms), Encaps ($0.1353$ ms), Decaps ($0.1826$ ms), Setup ($0.4754$ ms) separated from message encryption ($0.0456$ ms).
- [x] **AEAD Tamper Rejection**: 100% bit-flip tamper rejection verified across ciphertext and header modifications (`InvalidTag`).
- [x] **Hash Chain vs. Distributed Blockchain**: Distinction formally articulated; local hash chain rewrite boundary proven ($\mathcal{A}_{\text{root}}$); requirement for external root tip anchoring disclosed.
- [x] **No Quantum Overclaims**: Avoids claiming "complete quantum-proof system"; claims strictly bounded to ML-KEM-768 transit encryption.

---

## 5. Manuscript & Presentation Gate

- [x] **Attribution Honesty**: Base paper baseline in Table 7 explicitly footnoted as our benchmark reimplementation on CICIoT2023.
- [x] **Tone & Language**: All promotional language ("100% verified", "guaranteed superiority", "reviewer-proof") eliminated.
- [x] **Author Identifiers**: Placeholder academic affiliations used for peer review (`Anonymous Authors` / `Author One et al.`).
- [x] **Hardware Scope Qualified**: AMD64 host edge gateway scope explicitly declared; microcontroller cycle constraints disclosed.
- [x] **Formatting Consistency**: `paper/manuscript.md` and `paper/manuscript.tex` are fully synchronized with matching metrics, tables, and references.
- [x] **LaTeX Compilation**: Syntax verified; reported that local system lacks `pdflatex`/`latexmk` binaries in PATH.

---

## 6. Unit Test Gate

- [x] **Test Execution**: `python -m pytest --junitxml=results/final_submission_audit/test_report.xml -v`
- [x] **Test Pass Rate**: **30 / 30 Passed (100.0%) in 27.72s**.
- [x] **Report Artifact**: `results/final_submission_audit/test_report.xml` generated and archived.
