# Metric Diagnosis & Model Failure Investigation

**Document Date**: October 9, 2026  
**Status**: Research Recovery Phase D Deliverable  

---

## 1. Recomputed Confusion Matrices & Performance Summary

Using saved error arrays from `results/metrics/baseline_errors.npz` without retraining models:

| Model | Strategy | TP | FP | TN | FN | Precision | Recall | F1-Score | FPR | PR-AUC | ROC-AUC |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dense-AE** | Fixed_95 | 68,031 | 724 | 14,187 | 17,058 | 0.9895 | 0.7995 | 0.8844 | 0.0486 | 0.9859 | 0.9177 |
| **Dense-AE** | Fixed_99 | 65,094 | 167 | 14,744 | 19,995 | 0.9974 | 0.7650 | 0.8659 | 0.0112 | 0.9859 | 0.9177 |
| **LSTM-AE** | **Fixed_95** | **85,082** | **14,909** | **0** | **0** | **0.8509** | **1.0000** | **0.9194** | **1.0000** | **0.9045** | **0.6294** |
| **GRU-AE** | **Fixed_95** | **85,082** | **14,909** | **0** | **0** | **0.8509** | **1.0000** | **0.9194** | **1.0000** | **0.9043** | **0.6288** |
| **Isolation Forest** | Fixed_95 | 54,653 | 752 | 14,159 | 30,436 | 0.9864 | 0.6423 | 0.7780 | 0.0504 | 0.9769 | 0.8890 |
| **XGBoost Oracle** | Supervised 0.5| 73,641 | 235 | 14,676 | 11,448 | 0.9968 | 0.8655 | 0.9265 | 0.0158 | 0.9947 | 0.9683 |

---

## 2. Confirmation of Model Prediction Behavior

* **LSTM-AE Confusion Matrix**:
  $$\begin{bmatrix} \text{TN}=0 & \text{FP}=14,909 \\ \text{FN}=0 & \text{TP}=85,082 \end{bmatrix}$$
* **GRU-AE Confusion Matrix**:
  $$\begin{bmatrix} \text{TN}=0 & \text{FP}=14,909 \\ \text{FN}=0 & \text{TP}=85,082 \end{bmatrix}$$
* **Confirmed Finding**: Both LSTM-AE and GRU-AE predicted **1 (Attack) for 100% of test samples**. They did not perform any selective classification.

---

## 3. Class Prevalence Analysis & The F1-Score Fallacy

* **Test Partition Imbalance**: 85.09% Attack samples ($85,082 / 99,991$), 14.91% Benign samples ($14,909 / 99,991$).
* **F1 Formula Under All-1 Predictor**:
  $$\text{Precision} = \frac{85082}{85082 + 14909} = 0.850897$$
  $$\text{Recall} = \frac{85082}{85082 + 0} = 1.000000$$
  $$\text{F1-Score} = \frac{2 \times 0.850897 \times 1.0}{0.850897 + 1.0} = 0.919443$$
* **Conclusion**: An all-1 dummy classifier on an 85% attack test set automatically yields an F1-Score of **0.9194**, despite having a **100% false alarm rate ($\text{FPR}=1.0$)**. Reporting F1 alone masked a catastrophic model failure.

---

## 4. Root-Cause Code Path Diagnosis

### Confirmed Root Causes

#### 1. Train-Test Scale Mismatch in `scripts/prepare_dataset.py`
* `X_train_unsup` was sampled from benign rows in `train.parquet`.
* `X_test` was sampled from benign and attack rows in `test.parquet`.
* Due to feature scale differences between the two Parquet files, benign samples in `test.parquet` produced reconstruction errors with minimum value $= 14.9501$ and mean $= 9736.26$.
* However, `tau_95_lstm` was computed on validation benign samples from `train.parquet`, where 95% of errors were $\le 0.9675$.
* **Result**: Every single sample in the test set ($E_t \ge 14.95 > 0.9675$) exceeded the threshold, forcing all predictions to 1.

#### 2. EWMA Inflation Logic in `src/thresholding/threshold_methods.py`
* In `UnGuardedAdaptiveThreshold`, the running mean $\mu_t$ updated on every test sample.
* Because test errors averaged ~10,800, $\mu_t$ rose to ~10,800 and $\tau_t$ rose to ~23,000 within 50 timesteps.
* Since median error was ~10,850, almost no samples exceeded 23,000, forcing predictions to 0 and driving recall to near zero.

#### 3. Identical Metrics Cause in `scripts/run_baselines.py`
* LSTM-AE and GRU-AE had different validation thresholds ($\tau_{lstm} = 0.9675$ vs $\tau_{gru} = 0.8089$).
* However, because test errors for BOTH models were minimum $> 1.71$, BOTH models triggered predictions = 1 for ALL test samples, yielding identical confusion matrices.

### Hypotheses Disproved
* *Hypothesis that PyTorch models failed to train*: Disproved. Both models converged during training loss output. The failure occurred during **thresholding on scale-shifted test data**.

---

## 5. Artifact & Reproducibility Verification

* **Random Seeds**: Seeds $42, 123, 456, 789, 2026$ were listed in text, but script ran a single seed (`42`).
* **Statistical Tests**: Wilcoxon signed-rank tests were claimed in prose but were **NOT executed** in any saved Python script.
* **Tables & Figures**: `table1`, `table2`, `table3`, `figure1`, `figure2`, `figure3` exist in `results/` but contain numbers derived from the flawed evaluation pipeline.
