# Phase C Independent Review: Data Pipeline & Preprocessing Protocol

**Review Date**: October 9, 2026  
**Auditor**: Senior Research Engineer  
**Target Module**: `src/preprocessing/recovery_pipeline.py` & `tests/test_recovery_pipeline.py`  
**Status**: **COMPLETED. DATA PIPELINE DECISION: CONDITIONALLY APPROVED (GO WITH RESTRICTION).**

---

## 1. Code Inspection & Verification Results

### Requirement 1: Train-Only Transformation Fitting
* **Code Evidence**: In `src/preprocessing/recovery_pipeline.py` (lines 76-82):
  ```python
  scaler = StandardScaler()
  X_train = scaler.fit_transform(X_train_raw)
  X_val = scaler.transform(X_val_raw)
  X_sup = scaler.transform(X_sup_raw)
  X_test = scaler.transform(X_test_raw)
```
* **Verification**: `StandardScaler.fit()` is executed **exclusively on `X_train_raw`**. Validation, Supervised Train, and Test sets are transformed using `scaler.transform()` without recalculating mean or variance parameters.
* **Unit Test Verification**: `test_pipeline_execution_and_leakage` confirms `mean(X_train) == 0.0` and `std(X_train) == 1.0` for non-constant features.

---

### Requirement 2: Feature Selection & Label Exclusion
* **Code Evidence**: `FEATURE_SCHEMA` explicitly defines 39 numerical flow features. Target labels (`Label`, `attack_class`, `label`) and non-numeric identifiers (`src_ip`, `dst_ip`, `src_port`, `dst_port`, `Timestamp`) are explicitly excluded.
* **Unit Test Verification**: `test_label_exclusion` confirms `X_train.shape[1] == 39`.

---

### Requirement 3: Schema & Transformation Order Alignment
* **Verification**: All partitions (`X_train_raw`, `X_val_raw`, `X_sup_raw`, `X_test_raw`) extract columns using the exact same frozen list: `df[FEATURE_SCHEMA].values`. Column order, count, and data types are identical across all partitions.

---

### Requirement 4: Consistent Label Mapping & Zero Test-Label Tuning
* **Verification**:
  - Binary label mapping: `(df['Label'] != 'BenignTraffic').astype(int)` (0 = Benign, 1 = Attack).
  - Test labels (`y_test_binary`, `y_test_subclass`, `y_test_class`) are stored in `recovery_processed.npz` for post-hoc metric computation.
  - Test labels are **never** passed into `StandardScaler`, model loss functions, or threshold update formulas.

---

### Requirement 5: Duplicate Records & Overlap Interpretation

* **Raw Parquet Duplicates**:
  - `data/raw/train.parquet`: 84,370 complete row duplicates (7.86%), 103,704 feature vector duplicates (9.66%).
  - `data/raw/test.parquet`: 9,434 complete row duplicates (3.51%), 13,340 feature vector duplicates (4.97%).
* **Processed Partition Duplicates**:
  - `X_train` (Unsupervised Benign): 285 duplicates (0.29%).
  - `X_test`: 2,473 duplicates (2.47%).
  - `X_train` vs. `X_test` feature overlap: 81 unique feature vectors.
* **Scientific Interpretation**:
  - In high-rate network traffic (e.g. DDoS floods or periodic telemetry), multiple packets during a short window share identical protocol headers, flag counts, and sizes.
  - Repeated feature vectors in high-rate attack traffic represent **genuine network volume events**, not corrupt data. Blanket deletion of duplicate feature vectors would destroy volume properties.
  - However, because the raw HuggingFace Parquet files applied a random row-level shuffle across the entire dataset, identical packet flow records were randomly split into both `train.parquet` and `test.parquet` (resulting in 201,148 overlapping raw rows).

---

### Requirement 6: Comprehensive Unit Test Suite
The unit test suite in `tests/test_recovery_pipeline.py` was expanded and verified (**4 tests passed in 17.34s**):
1. `test_pipeline_execution_and_leakage`: Confirms train-only fitting ($\mu=0, \sigma=1$) and schema dimensions.
2. `test_label_exclusion`: Confirms target/metadata columns are excluded.
3. `test_missing_and_infinite_values`: Confirms zero `NaN` or `Inf` values across all output matrices.
4. `test_reproducible_splitting`: Confirms deterministic output equality across repeated pipeline executions (`RandomState(42)`).

---

### Requirement 7: Availability & Suitability of Official Capture Files

* **Official Source**: University of New Brunswick (UNB CIC) provides 169 individual capture CSV files (e.g., `DDoS-ICMP_Flood_1.csv`, `Benign_1.csv`).
* **Local Artifact Source**: Downloaded Parquet files (`data/raw/train.parquet` & `data/raw/test.parquet`) originated from HuggingFace (`siyam21/CIC-IoT-2023/random/`).
* **Critical Finding**: HuggingFace merged and **randomly row-shuffled** all flow records before saving to Parquet files.
* **Unsupported Research Claims**: The local HuggingFace Parquet files **CANNOT** support the following claims:
  1. *Capture-aware session splitting* (Session boundaries were destroyed during random row shuffling).
  2. *Chronological / temporal anomaly evaluation* (Packet flow sequence order was randomized).
  3. *Dynamic concept drift over sequential capture windows*.

---

## 2. Confirmed Issues & Unresolved Risks

| Issue / Risk | Severity | Description & Required Mitigation |
| :--- | :--- | :--- |
| **1. HuggingFace Shuffled Origin** | **HIGH** | Local raw Parquet files are randomly row-shuffled samples. The pipeline MUST explicitly label partitions as "sample-level pre-shuffled splits" and MUST NOT claim temporal or capture-aware splitting. |
| **2. Scale Shift Between Files** | **HIGH** | `train.parquet` benign samples and `test.parquet` benign samples exhibit scale differences. Future model baseline evaluations MUST ensure validation thresholds are tuned on scale-aligned validation data. |
| **3. Lack of Raw Index Manifest** | **LOW** | `recovery_pipeline.py` samples rows without recording raw row index arrays. A stable index manifest should be saved to `data/processed/recovery/index_manifest.json`. |

---

## 3. GO / NO-GO Decision for Data Pipeline

### Decision: **CONDITIONALLY APPROVED (GO WITH RESTRICTION)**

* **Approved Scope**: The updated `recovery_pipeline.py` and `tests/test_recovery_pipeline.py` correctly enforce strict train-only fitting, schema freezing, NaN/Inf cleaning, label exclusion, and deterministic reproducibility.
* **Mandatory Restriction**: All future experiment descriptions, code comments, tables, and manuscript text **MUST** state that the evaluation uses **pre-shuffled sample-level partitions**, and **MUST NOT** claim capture-aware chronological temporal splits unless raw UNB CIC capture files are fetched directly.
