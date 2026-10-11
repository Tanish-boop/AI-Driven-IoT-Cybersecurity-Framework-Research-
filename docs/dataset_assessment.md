# Public IoT Cybersecurity Dataset Assessment

**Assessment Date**: October 9, 2026  
**Primary Auditor**: Senior Research Engineer  
**Scope**: Evaluation of candidate public IoT cybersecurity datasets for an empirical research study.

---

## 1. Candidate Datasets Summary

To conduct an independently reproducible research study, we investigated four major public IoT cybersecurity datasets:
1. **CICIoT2023** (Primary Candidate)
2. **Edge-IIoTset** (Secondary Candidate)
3. **TON_IoT** (Reference Candidate)
4. **N-BAIoT** (Reference Candidate)

---

## 2. Primary Candidate: CICIoT2023

### A. Bibliographic & Access Information
* **Official Source URL**: [https://www.unb.ca/cic/datasets/iotdataset-2023.html](https://www.unb.ca/cic/datasets/iotdataset-2023.html)
* **Associated Publication**: "CICIoT2023: A Real-Time Dataset and Benchmark for Large-Scale Attacks in IoT Environment", *Sensors*, 23(13), 2023. DOI: [10.3390/s23135941](https://doi.org/10.3390/s23135941).
* **Licence & Usage Terms**: Free for academic research with mandatory citation of the UNB CIC dataset paper.
* **Download Formats**: Raw PCAP files (packet captures) and preprocessed CSV flow files (46 extracted network features per packet/window record).

### B. Capture Environment & Scale
* **Topology**: 105 physical IoT devices (smart home sensors, cameras, speakers, microcontrollers, gateways) deployed in a realistic laboratory environment.
* **Total Scale**: Over 300 CSV files comprising tens of millions of network flow records.
* **Attack Profiles**: 33 distinct attack types grouped into **7 major categories**:
  1. **DDoS** (DDoS-ICMP, DDoS-UDP, DDoS-TCP, DDoS-HTTP, DDoS-SYN, etc.)
  2. **DoS** (DoS-UDP, DoS-TCP, DoS-HTTP, DoS-SYN)
  3. **Reconnaissance** (PortScan, OS Scan, Vulnerability Scan, Host Discovery)
  4. **Spoofing** (ARP Spoofing, DNS Spoofing)
  5. **Web-Based Attacks** (SQL Injection, Command Injection, XSS)
  6. **Brute Force** (Dictionary attacks on SSH/Telnet/Web)
  7. **Mirai Botnet** (Mirai-GREeth, Mirai-UDP plain, Mirai-HTTP)

### C. Technical Features & Schema
* **Total Features**: 46 flow-level statistical features including:
  - Header statistics: `Header_Length`, `Protocol_Type`, `Duration`, `Rate`, `Srate`, `Drate`.
  - Packet metrics: `fin_flag_number`, `syn_flag_number`, `rst_flag_number`, `psh_flag_number`, `ack_flag_number`, `ece_flag_number`, `cwr_flag_number`.
  - Statistical aggregates: `Min`, `Max`, `AVG`, `Std`, `Tot size`, `IAT` (Inter-Arrival Time min/max/mean/std), `Number`, `Magn`, `Radius`, `Covariance`, `Variance`, `Weight`.
* **Labeling**: 3 granularity levels available:
  - *Binary*: `Benign` vs. `Malicious`.
  - *Category*: 7 attack classes + `Benign`.
  - *Sub-category*: 33 specific attack types + `Benign`.

### D. Detailed Capability Assessment

| Framework Component | Can CICIoT2023 Support It? | Methodology / Notes |
| :--- | :--- | :--- |
| **1. Anomaly Detection** | **YES (EXCELLENT)** | Train baseline models (LSTM, Autoencoder, XGBoost, GRU) on Benign flow sequences; evaluate on Benign vs 33 Attack types. |
| **2. Adaptive Thresholding**| **YES (EXCELLENT)** | Traffic files contain natural temporal flow dynamics, packet rate variations, and bursty attack arrivals for testing EWMA / Rolling Quantile thresholds. |
| **3. Supervised Multi-class**| **YES (EXCELLENT)** | Supports 8-class (7 attack categories + benign) and 34-class classification. |
| **4. Incident Response Sim**| **YES (INDIRECTLY)** | Flow event probabilities and attack severity levels provide realistic arrival streams for a simulated cost-benefit MDP environment. |
| **5. Cryptographic Bench** | **SEPARATE SETUP** | Network flows do not measure PQC latency directly; ML-KEM benchmarking is conducted via microbenchmarks on traffic payloads. |
| **6. Data Integrity Audit**| **SEPARATE SETUP** | Tested by applying HMAC-SHA256 digests onto packet flows and simulating payload corruption attacks. |

---

## 3. Secondary Candidate: Edge-IIoTset

### A. Bibliographic Information
* **Official Source URL**: [https://ieeexplore.ieee.org/document/9751704](https://ieeexplore.ieee.org/document/9751704) (DOI: [10.1109/ACCESS.2022.3165809](https://doi.org/10.1109/ACCESS.2022.3165809))
* **Capture Environment**: Realistic Industrial IoT (IIoT) testbed with Modbus, MQTT, OPC UA, HTTP, and CoAP protocols.
* **Scale**: 14 attack types (DDoS, Ransomware, SQL Injection, XSS, MITM, Password attacks, Modbus spoofing).
* **Utility**: Excellent secondary dataset for **cross-dataset generalization tests** to verify whether anomaly detection models trained on CICIoT2023 transfer to industrial protocols.

---

## 4. Comprehensive Dataset Comparison Matrix

| Metric / Attribute | CICIoT2023 | Edge-IIoTset | TON_IoT | N-BAIoT |
| :--- | :--- | :--- | :--- | :--- |
| **Release Year** | 2023 | 2022 | 2020 | 2018 |
| **IoT Device Count** | 105 physical devices | 10 IIoT devices/sensors | 7 IoT devices | 9 commercial devices |
| **Attack Types** | 33 attack types | 14 attack types | 9 attack types | 2 botnet families (Mirai/Bashlite) |
| **Protocols Covered** | TCP, UDP, ICMP, HTTP, DNS, ARP | Modbus, MQTT, OPC-UA, CoAP, HTTP | Telemetry, HTTP, MQTT, DNS | TCP, UDP |
| **Feature Count** | 46 statistical features | 61 features | 43 features | 115 packet features |
| **Temporal Sequence**| Yes (flow duration/IAT) | Yes (time-series flows) | Yes | Yes (time windows) |
| **Class Imbalance** | Heavy attack volume (~95% attack, 5% benign across full set) | Moderate | Moderate | Heavy botnet volume |
| **Primary Selection**| **PRIMARY CHOICE** | **SECONDARY (Cross-eval)**| Reference | Reference |

---

## 5. Dataset Cleaning & Preprocessing Protocol

To ensure strict experimental integrity and prevent data leakage:
1. **Raw Data Immutability**: Raw CSV files downloaded from UNB CIC will be placed in `data/raw/` and set to read-only.
2. **Deterministic Sampling**: Due to the massive size of CICIoT2023 (>10 GB), a stratified temporal subsample (e.g., 200,000 to 500,000 flow records preserving class proportions and session continuity) will be created for local model training and cross-validation.
3. **Training-Only Scalers**: All min-max scalers, standardizers, and imputers will be fit **strictly on training split data** and applied to validation and test splits without recalculating parameters.
4. **Data Cleaning Rules**:
   - Explicitly drop non-numeric / metadata identifiers (`src_ip`, `dst_ip`, `src_port`, `dst_port`) to prevent identity memorization shortcuts.
   - Detect and handle `NaN`, `Inf`, and zero-variance constant columns.
   - Audit and log duplicate rows before and after splitting.
