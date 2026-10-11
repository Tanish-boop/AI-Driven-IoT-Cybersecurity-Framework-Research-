# Recovery Stress-Test and Distribution Shift Protocol

**Document Date**: October 9, 2026  
**Status**: Research Recovery Phase E Deliverable  

---

## 1. Rejection of Score Multiplication Hack

* **Flaw in Initial Script**: In `scripts/run_threshold_experiments.py`, benign test errors were multiplied by 2.0 (`stress_test_err[burst_indices] = stress_test_err[burst_indices] * 2.0`).
* **Rejection**: Multiplying anomaly output scores by a constant scalar is a mathematical artifact, NOT a network experiment.
* **Mandatory Rule**: All future stress tests must apply transformations **at the input feature level** before passing telemetry through trained models.

---

## 2. Four Separate Scientifically Justified Shift Experiments

### Experiment 1: Feature-Level Traffic Rate Scaling (Synthetic Stress Test)
* **Transformed Features**: `Rate`, `Srate`, `Drate`, `Header_Length`, `Tot size`.
* **Transformation Method**: Apply a multiplier $S \in \{1.5, 2.0, 3.0\}$ to packet rate and header volume features during a 5,000-sample benign window to emulate a legitimate network surge.
* **Fixed Factors**: All flag counts (`fin_flag_number`, `syn_flag_number`), protocol types, and attack labels remain unchanged.
* **Label Handling**: Sample labels remain 100% Benign ($y=0$).
* **Measured Metrics**: False Positive Rate (FPR), Precision-Recall AUC, and Threshold adaptation velocity.
* **Classification**: Explicitly labeled as a **Synthetic Feature Stress Test**, NOT naturally occurring concept drift.

### Experiment 2: Feature Distribution Shift Across Capture Batches
* **Method**: Group test telemetry by distinct attack sub-types or device protocol types (e.g. HTTP vs. ICMP vs. UDP floods).
* **Fixed Factors**: Model weights, feature scaling, and static threshold.
* **Measured Metrics**: Per-attack category Recall, Precision, F1-Score.

### Experiment 3: Attack Prevalence Shift Analysis
* **Motivation**: In real networks, attack traffic is rare (1% to 5% of total flow count). Testing on 85% attack datasets artificially inflates F1 scores for all-1 dummy predictors.
* **Method**: Construct test streams with controlled attack prevalence $P_{attack} \in \{1\%, 5\%, 10\%, 20\%, 50\%, 80\%\}$.
* **Measured Metrics**: Precision, Recall, F1-Score, False Positive Rate, and Precision-Recall AUC.

### Experiment 4: Guarded Threshold Adaptation Under Benign Shift
* **Method**: Introduce a sustained 2.0x benign feature scaling step function. Evaluate whether Guarded EWMA thresholding adapts to the new benign baseline within $K$ timesteps without triggering permanent false alarms.
* **Comparison**: Fixed Threshold vs. Un-Guarded EWMA vs. Guarded Winsorized EWMA.
