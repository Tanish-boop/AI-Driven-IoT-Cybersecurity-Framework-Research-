# Independent Scientific and Implementation Audit Report

**Audit Date**: October 9, 2026  
**Auditor**: Senior Research Engineer  
**Target Repository**: `iot-cybersecurity-research`  
**Status**: **COMPLETED. NO-GO FOR CURRENT MANUSCRIPT / PUBLICATION. MAJOR METHODOLOGICAL AND IMPLEMENTATION DEFECTS CONFIRMED.**

---

## Executive Summary

An independent, non-destructive audit of the codebase, data pipelines, model evaluations, and manuscript was conducted. **No new features were added, no models were retrained, and no manuscript text was altered to inflate results.**

The audit revealed **critical methodological flaws, data leakage at the source level, metric misinterpretations, and invalid experimental representations** that render the current manuscript claims scientifically unsupportable.

---

## 1. Task 1 Audit: Dataset Integrity, Splitting & Leakage

### A. Source Data Origin
* **Discovered Reality**: The downloaded raw Parquet files (`data/raw/train.parquet` and `data/raw/test.parquet`) originated from HuggingFace (`siyam21/CIC-IoT-2023/random/`).
* **Flaw**: The source dataset on HuggingFace was **randomly row-shuffled before parquet partitioning**. It does NOT represent a capture-aware or chronological stream.
* **Impact**: The paper's claim of evaluating a "capture-aware chronological temporal split" is **false and unsupported** by the underlying raw data files.

### B. Overlap and Duplicate Records
* **Train Duplicate Rows**: 84,370 duplicate rows (7.86%).
* **Test Duplicate Rows**: 9,434 duplicate rows (3.51%).
* **Severe Row Overlap**: An exact feature row overlap of **201,148 rows** exists between `df_train` and `df_test`.
* **Impact**: Because identical flow feature vectors appear in both `df_train` and `df_test`, model evaluation suffered from massive **data leakage at the dataset source level**.

### C. Distribution Mismatch Between Train and Test Benign Telemetry
* Benign samples in `df_train` had feature values resulting in reconstruction errors $\le 0.9675$.
* Benign samples in `df_test` had feature scales resulting in minimum reconstruction errors $\ge 14.95$ (mean ~9,736).
* **Impact**: The benign test telemetry was drawn from a completely different scale/distribution than the benign training telemetry, causing sequence models trained on `df_train` to fail catastrophically on `df_test`.

---

## 2. Task 2 Audit: Verification of Reported Metrics & Model Failures

### A. Recomputed Baseline Metrics (`results/metrics/recomputed_metrics.csv`)

| Model | Strategy | Precision | Recall | F1-Score | FPR | PR-AUC | ROC-AUC | TP | FP | TN | FN |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dense-AE** | Fixed_95 | 0.9895 | 0.7995 | 0.8844 | 0.0486 | 0.9859 | 0.9177 | 68,031 | 724 | 14,187 | 17,058 |
| **Dense-AE** | Fixed_99 | 0.9974 | 0.7650 | 0.8659 | 0.0112 | 0.9859 | 0.9177 | 65,094 | 167 | 14,744 | 19,995 |
| **LSTM-AE** | **Fixed_95** | **0.8509** | **1.0000** | **0.9194** | **1.0000** | **0.9045** | **0.6294** | **85,082** | **14,909** | **0** | **0** |
| **GRU-AE** | **Fixed_95** | **0.8509** | **1.0000** | **0.9194** | **1.0000** | **0.9043** | **0.6288** | **85,082** | **14,909** | **0** | **0** |
| **Isolation Forest** | Fixed_95 | 0.9864 | 0.6423 | 0.7780 | 0.0504 | 0.9769 | 0.8890 | 54,653 | 752 | 14,159 | 30,436 |
| **XGBoost Oracle** | Supervised 0.5 | 0.9968 | 0.8655 | 0.9265 | 0.0158 | 0.9947 | 0.9683 | 73,641 | 235 | 14,676 | 11,448 |

### B. Key Metric Audit Findings

1. **Why LSTM-AE and GRU-AE Reported Identical Metrics**:
   - Both LSTM-AE and GRU-AE predicted **1 for every single test sample** (TP = 85,082, FP = 14,909, TN = 0, FN = 0).
   - This occurred because the validation 95th percentile threshold ($\tau_{95} \approx 0.96$) was orders of magnitude smaller than the test error range (minimum test error $= 14.95$).
   - The reported F1-Score of **0.9194** was purely an artifact of high attack class imbalance (85% attack samples), **NOT model performance**.
2. **Why FPR = 1.0000**:
   - Every single benign sample in the test set exceeded $\tau_{95}$, forcing the false positive rate to $14,909 / 14,909 = 1.0000$.
3. **Why EWMA Recall Approached Zero**:
   - Streaming EWMA initialized on test errors ~10,800 rapidly inflated its running threshold $\tau_t = \mu_t + 2.5\sigma_t$ to ~23,000.
   - Because median test errors were ~10,850, almost no samples exceeded 23,000, forcing the model to predict 0 for almost all samples, driving recall to near zero ($0.0002$).

---

## 3. Task 3 Audit: Claimed Traffic-Shift Experiment (Score Multiplication Flaw)

* **Code Inspection (`scripts/run_threshold_experiments.py`, Lines 113-118)**:
  ```python
  stress_test_err = test_err.copy()
  benign_indices = np.where(y_true == 0)[0]
  burst_indices = benign_indices[: min(5000, len(benign_indices))]
  stress_test_err[burst_indices] = (
      stress_test_err[burst_indices] * 2.0
  )  # 2x error scaling stress test
```
* **Severe Methodological Flaw**: The script did **NOT** simulate or apply a network traffic rate shift or feature transformation. It literally took output anomaly error scores and multiplied numbers by 2.0 (`stress_test_err * 2.0`)!
* **Conclusion**: Describing raw error score multiplication as a "synthetic traffic rate-scaling stress test" in the manuscript was an invalid and misleading representation.

---

## 4. Confirmed Bugs, Weaknesses & Unsupported Manuscript Claims

| Area | Confirmed Defect / Flaw | Manuscript Impact / Action Required |
| :--- | :--- | :--- |
| **Data Origin** | HuggingFace raw dataset was randomly shuffled, causing 201,148 duplicate/overlapping rows between train and test splits. | **REMOVE** claim of "capture-aware chronological split". Must rebuild dataset pipeline from raw UNB CIC CSV files. |
| **LSTM/GRU Metric Interpretation** | LSTM-AE/GRU-AE predicted 1 for all samples due to train/test scale mismatch. F1=0.9194 was an artifact of 85% attack imbalance while FPR=1.0. | **REMOVE** claims of superior LSTM/GRU anomaly detection. Acknowledge catastrophic scale drift. |
| **Traffic Shift Experiment** | "Rate scaling stress test" was just raw error score multiplication ($E_t \times 2.0$). | **REMOVE** claims of dynamic traffic rate-scaling evaluation. |
| **Adaptive Thresholding** | Un-guarded and guarded EWMA caused total threshold inflation and recall collapse under attack floods. | **REVISE** findings to state that simple online EWMA fails under continuous attack streams without label feedback. |
| **Publication Readiness** | Paper claims to be "submission-ready for IEEE Access". | **REJECT**. Paper is unpublishable in current state. |

---

## 5. Go / No-Go Recommendation

### Final Recommendation: **NO-GO FOR CURRENT PAPER / RESULTS**

### Mandatory Corrective Requirements Before Re-Evaluating:
1. **Rebuild Data Pipeline from Official Source**: Download official raw CICIoT2023 CSV files directly from University of New Brunswick (UNB CIC), enforce genuine capture-file temporal splitting, and perform exact deduplication to eliminate row overlap.
2. **Fix Sequence Model Preprocessing**: Ensure feature scaling and temporal discretization are consistent across benign train, validation, and test splits so baseline errors are on a common scale.
3. **Implement Genuine Feature-Level Stress Tests**: If evaluating traffic rate surges, transform actual input features (e.g. `Rate`, `Srate`, `Drate`, `IAT`) before passing through trained models, rather than multiplying output anomaly scores by 2.0.
4. **Rewrite Manuscript Honestly**: Position the paper as an empirical study highlighting the severe vulnerabilities of static and online adaptive thresholding in IoT anomaly detection.
