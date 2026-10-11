# Recovery Experimental Blueprint: Rigorous Evaluation Protocol for IoT Anomaly Detection

**Document Date**: October 9, 2026  
**Primary Author**: Senior Research Engineer  
**Status**: Experimental Blueprint (Pre-Execution Blueprint for User Review)  

---

## 1. Scientific Philosophy & Core Objectives

The primary goal of this research recovery pipeline is **scientific rigor, leak-free evaluation, and exact independent reproducibility**, rather than chasing artificially high metrics.

### Key Principles
1. **Zero Data Leakage**: Scalers, imputers, and learned transformations are fit **exclusively on the Unsupervised Benign Training partition**.
2. **Pre-Shuffled Sample-Level Disclosures**: Since raw Parquet files from HuggingFace (`siyam21/CIC-IoT-2023/random/`) are randomly row-shuffled, evaluations are explicitly conducted and disclosed as **sample-level flow benchmarks**, NOT capture-aware chronological streams.
3. **No Score Multiplier Hacks**: Synthetic rate-scaling stress tests must transform **actual input feature vectors** (`Rate`, `Srate`, `Drate`, `Tot size`) before model evaluation, rather than multiplying output anomaly score arrays by scalars.
4. **Complete Metric Reporting**: F1-Score must **never** be reported in isolation. Every evaluation table must explicitly report Precision, Recall, F1-Score, False Positive Rate (FPR), PR-AUC, ROC-AUC, and complete Confusion Matrices ($\text{TP}, \text{FP}, \text{TN}, \text{FN}$).

---

## 2. Dataset Partitioning & Preprocessing Architecture

### Partition Summary (`data/processed/recovery/recovery_processed.npz`)

| Partition | Row Count | Composition | Label Availability | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Unsup Train (`X_train`)** | 100,000 | 100% Pure Benign | Benign Only ($y=0$) | Fitting `StandardScaler` and Autoencoder loss |
| **Unsup Val (`X_val`)** | 30,000 | 100% Pure Benign | Benign Only ($y=0$) | Convergence check & Threshold selection ($\tau_{95}, \tau_{99}$) |
| **Supervised Train (`X_sup`)**| 40,000 | 50% Benign / 50% Attack | Labeled ($y \in \{0, 1\}$)| Training XGBoost Supervised Oracle Reference |
| **Test Set (`X_test`)** | 100,000 | 14,911 Benign / 85,089 Attack | Labeled ($y \in \{0, 1\}$)| Final leakage-free evaluation |

---

## 3. Anomaly Detector & Baseline Specifications

### A. Unsupervised Anomaly Detectors
1. **Dense Autoencoder (Dense-AE)**:
   - Architecture: 39 $\rightarrow$ 64 $\rightarrow$ 32 $\rightarrow$ 16 $\rightarrow$ 32 $\rightarrow$ 64 $\rightarrow$ 39 with BatchNorm and ReLU.
   - Input: Single sample vector $X_i \in \mathbb{R}^{39}$.
   - Reconstruction Error: $E_i = \frac{1}{39} \sum_{j=1}^{39} (X_{i,j} - \hat{X}_{i,j})^2$.
2. **Isolation Forest (iForest)**:
   - Configuration: 100 trees, fit on `X_train`.
   - Score: $- \text{decision\_function}(X_i)$.

### B. Supervised Oracle Reference
* **XGBoost Classifier**:
  - Trained on `X_sup` (separate labeled partition).
  - Decision Rule: $\hat{y}_i = 1$ if $P(y_i=1 \mid X_i) \ge 0.5$, else $0$.
  - Purpose: Quantify upper-bound classification performance with known labels.

---

## 4. Comparative Threshold Update Strategies

Let $E_i$ represent the reconstruction error of test sample $i$.

### Strategy 1: Fixed Threshold ($\tau_{fixed}$)
* $\tau_{95} = \text{Percentile}(E_{\text{val}}, 95)$ or $\tau_{99} = \text{Percentile}(E_{\text{val}}, 99)$.
* Decision: $\hat{y}_i = 1$ if $E_i > \tau$, else $0$. Static boundary.

### Strategy 2: Un-Guarded EWMA Adaptive Threshold ($\tau_{unguarded}$)
* $\mu_i = (1-\alpha)\mu_{i-1} + \alpha E_i$
* $\sigma_i^2 = (1-\alpha)\sigma_{i-1}^2 + \alpha (E_i - \mu_i)^2$
* $\tau_i = \mu_i + k \cdot \sqrt{\sigma_i^2}$
* Updates on **all incoming telemetry**. Evaluates vulnerability to threshold inflation under attack floods.

### Strategy 3: Guarded Winsorized Adaptive Threshold ($\tau_{guarded}$)
* Clamps error if flagged: $E_i^{\text{clamp}} = \tau_i + \delta \cdot \sqrt{\sigma_i^2}$ if $E_i > \tau_i$, else $E_i$.
* Updates $\mu_i, \sigma_i^2$ using $E_i^{\text{clamp}}$. Evaluates resistance to threshold inflation.

---

## 5. Feature-Level Stress Test Specifications

1. **Synthetic Feature Rate Scaling Stress Test**:
   - Apply feature transformation to benign test samples: $X_{i, \text{rate}} = X_{i, \text{rate}} \times S$ (where $S \in \{1.5, 2.0\}$ for features `Rate`, `Srate`, `Drate`, `Tot size`).
   - Pass modified $X_{i, \text{stress}}$ through fitted `StandardScaler` and trained models.
   - Measure FPR degradation under feature-level surges.
2. **Controlled Attack Prevalence Shift Test**:
   - Evaluate performance under test streams re-balanced to $1\%, 5\%, 10\%, 20\%, 50\%, 80\%$ attack prevalence.

---

## 6. Pre-Registered Reproducibility Manifest

* **Random Seeds**: Seeds $42, 123, 456, 789, 2026$ used for repeated runs.
* **Paired Statistical Inference**: Two-tailed paired Wilcoxon signed-rank tests ($p < 0.05$) across 31 attack sub-types.
* **All Artifacts Saved**: `results/metrics/recomputed_metrics.csv`, `data/processed/recovery/recovery_manifest.json`.
