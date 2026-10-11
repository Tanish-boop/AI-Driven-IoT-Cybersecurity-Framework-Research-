# Recovery Leakage Analysis & Audit Report

**Document Date**: October 9, 2026  
**Status**: Research Recovery Phase B Deliverable  

---

## 1. Executive Summary & Leakage Metrics Summary

| Partition | Total Rows | Complete Row Duplicates | Feature Vector Duplicates | Overlap with Unsup Train | Overlap with Test |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Raw `train.parquet`** | 1,073,851 | 84,370 (7.86%) | 103,704 (9.66%) | N/A | **201,148 rows** |
| **Raw `test.parquet`** | 268,463 | 9,434 (3.51%) | 13,340 (4.97%) | **201,148 rows** | N/A |
| **Unsup Train Split** | 100,000 | 285 (0.29%) | 285 (0.29%) | 0 | 81 |
| **Unsup Val Split** | 30,000 | 45 (0.15%) | 45 (0.15%) | 73 | 57 |
| **Supervised Train Split**| 40,000 | 232 (0.58%) | 232 (0.58%) | N/A | 115 |
| **Processed Test Split** | 100,000 | 2,473 (2.47%) | 2,473 (2.47%) | 81 | 0 |

---

## 2. Distinction: Complete Row Duplicates vs. Feature Vector Duplicates

* **Complete Row Duplicates**: Identical feature values AND identical target labels (`Label`, `attack_class`, `label`). In raw `train.parquet`, 84,370 rows (7.86%) are complete exact duplicates.
* **Feature Vector Duplicates**: Identical feature values, regardless of whether labels match. In raw `train.parquet`, 103,704 rows (9.66%) share duplicate feature vectors.
* **Interpretation of Duplicate Feature Vectors**: In high-rate IoT network telemetry (e.g. DDoS/DoS floods or periodic sensor reporting), multiple packets during a short window share identical protocol headers, packet sizes, and flag counts. Blanket deletion of duplicate feature vectors would destroy natural volume properties of high-rate attack traffic. Deduplication must follow explicit, documented rules.

---

## 3. Detailed Investigation: What the Reported 201,148 Overlapping Rows Represent

* **Audit Finding**: In the initial audit, an inner merge between `df_train[feature_cols]` and `df_test[feature_cols]` yielded 201,148 matching rows.
* **Cause**: Because the source HuggingFace dataset (`siyam21/CIC-IoT-2023`) applied a random row-level shuffle across all concatenated CSV files before saving to Parquet, identical packet flow records captured during the same traffic bursts were randomly split into both `train.parquet` and `test.parquet`.
* **Unique Feature Overlap**: 22,406 distinct feature vector patterns appear in both raw train and test files.
* **Unique Complete Row Overlap**: 21,793 distinct complete rows (features + labels) appear in both train and test files.

---

## 4. Target Leakage & Feature Encoding Analysis

* **Zero-Variance Features**: None found. All 39 features exhibit non-zero variance.
* **Feature-Target Correlations**:
  - `HTTPS`: $-0.532$ (strong inverse correlation; benign traffic uses HTTPS heavily).
  - `Number`: $+0.508$ (packet count per window; attacks generate high packet numbers).
  - `ack_flag_number`: $-0.447$.
  - `Time_To_Live`: $-0.352$.
* **Target Encoding Check**: None of the 39 input numerical features directly encode the string target or attack identity. However, port numbers (`src_port`, `dst_port`) and IP addresses (`src_ip`, `dst_ip`) were dropped in `prepare_dataset.py` to prevent shortcut identity memorization.
