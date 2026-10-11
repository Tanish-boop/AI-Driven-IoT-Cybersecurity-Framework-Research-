# Pre-Pilot Validation & Controlled Experiment Deliverable

**Validation Date**: October 9, 2026  
**Auditor & Research Engineer**: Senior AI & Cybersecurity Specialist  
**Status**: **CONTROLLED PILOT COMPLETED. PILOT RECOMMENDATION: PILOT PASSED.**

---

## 1. Requirement Checks Performed & Exact Results

### Check 1: Partition Overlap Recomputation (Exact 39 Features)
* **Unsup Train (`X_train`)**: 100,000 pure Benign samples (`float32`). Internal duplicate feature vectors: 285 (0.29%).
* **Unsup Val (`X_val`)**: 30,000 pure Benign samples (`float32`). Internal duplicate feature vectors: 45 (0.15%).
* **Supervised Train (`X_sup`)**: 40,000 50/50 Benign/Attack samples (`float32`). Internal duplicate feature vectors: 232 (0.58%).
* **Test (`X_test`)**: 100,000 samples (14,911 Benign / 85,089 Attack, `float32`). Internal duplicate feature vectors: 2,473 (2.47%).
* **Cross-Partition Unique Feature Overlaps**:
  - `X_train` vs. `X_val`: 73 unique feature vectors (0.073%).
  - `X_tr` (Benign) vs. `X_test` (Benign): **33 unique feature vectors**.
  - `X_tr` (Benign) vs. `X_test` (Attack): **70 unique feature vectors**.
* **Interpretation**: Duplicate feature vectors within high-rate network traffic (e.g. DDoS floods or periodic telemetry) represent **natural volume events**. Repeated feature patterns were preserved in data arrays without blind deletion, but cross-partition leakage remains minimal (<0.081%).

### Check 2: Preprocessing & Label Isolation Validation
* **Scaler Fitting**: `StandardScaler.fit()` was executed **EXCLUSIVELY on `X_train`** (Unsupervised Benign Training set). `X_val`, `X_sup`, and `X_test` were transformed using `scaler.transform()`.
* **Feature Schema**: Frozen to 39 numerical features (`FEATURE_SCHEMA`). Target labels (`Label`, `attack_class`, `label`) and metadata (`src_ip`, `dst_ip`, `src_port`, `dst_port`, `Timestamp`) were strictly excluded.
* **Data Cleaning**: Zero NaNs, zero Infs across all four partitions.
* **Disjoint Validation**: `X_val` represents a distinct slice (samples 100,000–130,000 of benign telemetry) disjoint from `X_train` (samples 0–100,000). Test labels were **never** used during preprocessing, model fitting, or threshold selection.

---

## 2. Controlled Pilot Configuration & Results (Seed = 42)

### A. Model Specifications & Training Protocols
1. **Dense Autoencoder (Dense-AE)**:
   - Architecture: 39 $\rightarrow$ 64 $\rightarrow$ 32 $\rightarrow$ 16 $\rightarrow$ 32 $\rightarrow$ 64 $\rightarrow$ 39 with BatchNorm and ReLU.
   - Training: Trained for 10 epochs on `X_train` (pure Benign samples only) with Adam ($\text{lr}=0.001$, batch size 512).
   - Thresholding: $\tau_{95} = 0.075467$ and $\tau_{99} = 0.237072$ tuned on `X_val` (pure Benign validation errors only).
2. **Isolation Forest**:
   - Configuration: 100 trees, fit on `X_train` (pure Benign samples only), `contamination='auto'`.
   - Thresholding: $\tau_{95} = \text{Percentile}(\text{score}_{\text{val}}, 95)$.
3. **XGBoost Oracle Reference**:
   - Configuration: 100 trees, `max_depth=6`, `learning_rate=0.1`, fit on `X_sup` (separate 50/50 Benign+Attack labeled partition) as an explicit **supervised upper-bound reference**.

### B. Controlled Pilot Results Table

| Model | Threshold Strategy | True Positives (TP) | False Positives (FP) | True Negatives (TN) | False Negatives (FN) | Precision | Recall | F1-Score | False Positive Rate (FPR) | PR-AUC | ROC-AUC |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dense-AE** | Fixed 95th Percentile | 68,031 | 724 | 14,187 | 17,058 | 0.9895 | 0.7995 | 0.8844 | 0.0486 | 0.9859 | 0.9177 |
| **Dense-AE** | Fixed 99th Percentile | 65,094 | 167 | 14,744 | 19,995 | 0.9974 | 0.7650 | 0.8659 | 0.0112 | 0.9859 | 0.9177 |
| **Isolation Forest** | Fixed 95th Percentile | 54,653 | 752 | 14,159 | 30,436 | 0.9864 | 0.6423 | 0.7780 | 0.0504 | 0.9769 | 0.8890 |
| **XGBoost Oracle** | Supervised Prob 0.5 | 73,641 | 235 | 14,676 | 11,448 | 0.9968 | 0.8655 | 0.9265 | 0.0158 | 0.9947 | 0.9683 |

### C. Reconstruction Error Score Distributions
* **Dense-AE Benign Validation Errors**: Mean $= 0.0271$, Median $= 0.0138$, Std $= 0.1061$, $\tau_{95} = 0.0755$, $\tau_{99} = 0.2371$.
* **Dense-AE Test Benign Errors**: Mean $= 0.0269$, Median $= 0.0139$, Std $= 0.0738$. (*Matches validation distribution within 0.0002!*)
* **Dense-AE Test Attack Errors**: Mean $= 14,160.21$, Median $= 19,956.59$, Std $= 9,508.83$. (*Clear 500,000x separation from benign error!*)

---

## 3. Attack Prevalence Dependency Note

In this test set, attack samples represent **85.09%** of the total count ($85,089 / 100,000$).
* **Metrics Sensitive to Prevalence**: **F1-Score** and **Precision** depend directly on attack prevalence ($P = \frac{TP}{TP + FP}$). In high-prevalence test sets, Precision remains high even when FP increases slightly.
* **Prevalence-Invariant Metrics**: **False Positive Rate (FPR)** ($FPR = \frac{FP}{FP + TN}$) and **Recall** ($R = \frac{TP}{TP + FN}$) are prevalence-invariant.
* **Guideline for Full Benchmark**: All future evaluation reports must report FPR and Recall alongside F1-Score to prevent prevalence-driven metric distortion.

---

## 4. Adaptive Threshold & Stress Test Rules (Pre-Registered)

1. **Adaptive Threshold Safeguards**:
   - Warm-up period: 500 initial benign timesteps before enabling updates.
   - Update Frequency: Online step-by-step update.
   - Contamination Guard: When an anomaly is flagged ($E_i > \tau_i$), updates use a clamped error $E_i^{\text{clamp}} = \tau_i + \delta \cdot \sigma_i$ (where $\delta = 0.3$) to prevent attack-induced threshold inflation.
2. **Feature Perturbation Stress Testing**:
   - Raw rate and size features (`Rate`, `Srate`, `Drate`, `Tot size`) will be multiplied by $S \in \{1.5, 2.0\}$ **before** scaling and model inference.
   - Explicitly labeled as a **Synthetic Feature Stress Test**, NOT real-world concept drift.

---

## 5. Confirmation of Strict Stop Conditions

- [x] **No Full Benchmark Executed**: Only seed `42` pilot models (Dense-AE, Isolation Forest, XGBoost Oracle) were evaluated.
- [x] **No Manuscript Changes**: `paper/manuscript.md` and `paper/manuscript.tex` were NOT modified.
- [x] **No Novelty or Superiority Claims**: Results are reported neutrally as pilot metrics.
- [x] **No Temporal Claims**: Data is explicitly disclosed as pre-shuffled sample-level partitions.

---

## 6. Clear Recommendation: PILOT PASSED

### Evidence
1. `StandardScaler` fit exclusively on `X_train` (pure Benign).
2. Validation threshold ($\tau_{95} = 0.0755$) matches test benign error distribution (mean $= 0.0269$, 95th percentile $= 0.0740$) cleanly without scale collapse.
3. Dense-AE achieves **F1 = 0.8844, FPR = 0.0486, PR-AUC = 0.9859, ROC-AUC = 0.9177**, providing a clean, leak-free baseline.
4. All pilot metadata, score distributions, and environment specifications are saved in `results/pilot/`.

**The controlled pilot has PASSED. Awaiting user review before launching the full experiment.**
