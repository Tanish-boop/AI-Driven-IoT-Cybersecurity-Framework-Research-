# Dataset Provenance and Source Inspection

**Document Date**: October 9, 2026  
**Status**: Research Recovery Phase A Deliverable  

---

## 1. Local Parquet Artifact Metadata

| File Path | Exact Size (Bytes) | MD5 Checksum | SHA256 Checksum | Total Rows | Total Columns |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `data/raw/train.parquet` | 53,328,937 (~50.86 MB) | `53239f028d0a9ca7f6b33035decc543c` | `4a9c585c6c1c7ef4cbaea624e71d0d960736ed8ed40006dc4bd918abfa09cc1d` | 1,073,851 | 42 |
| `data/raw/test.parquet` | 13,455,741 (~12.83 MB) | `7f4a7154ffab0c54fa7053b6faa68186` | `dbbaa3a7842d193cd04b6e5eba87e04b5d75b8951a62029dc29f80ae0e358ac2` | 268,463 | 42 |

---

## 2. Remote Provenance & Download Source

* **Repository Platform**: Hugging Face Datasets Hub
* **Repository ID**: `siyam21/CIC-IoT-2023`
* **Direct File Paths**:
  - `https://huggingface.co/datasets/siyam21/CIC-IoT-2023/resolve/main/random/train-00000-of-00001.parquet`
  - `https://huggingface.co/datasets/siyam21/CIC-IoT-2023/resolve/main/random/test-00000-of-00001.parquet`
* **Origin**: These Parquet files were created by an independent community user on HuggingFace who concatenated the original CICIoT2023 CSV files and applied a **random 80/20 train/test row-level shuffle** before saving to Parquet.

---

## 3. Official Source vs. Local Artifact Structure

### Official Dataset Source (University of New Brunswick)
* **Official URL**: https://www.unb.ca/cic/datasets/iotdataset-2023.html
* **Official Structure**: 169 individual CSV files corresponding to distinct, sequential capture sessions across 105 physical IoT devices (e.g., `DDoS-ICMP_Flood_1.csv`, `DDoS-ICMP_Flood_2.csv`, `Benign_1.csv`, etc.).
* **Chronological Availability**: The official UNB dataset provides individual capture session files, allowing capture-aware splitting when original CSV files are processed in capture sequence.

### Local Parquet Limitations
* **Status**: **NOT CHRONOLOGICAL / NOT CAPTURE-AWARE**.
* **Reason**: The HuggingFace files (`random/train-...`) represent a pre-shuffled row mixture. Capture session boundaries, inter-session timestamps, and device session order were destroyed during the random partitioning on HuggingFace.
* **Mandatory Guideline**: The local Parquet dataset must **NEVER** be described as a "capture-aware chronological split". It must be explicitly disclosed as a pre-shuffled, sample-level benchmark dataset.
