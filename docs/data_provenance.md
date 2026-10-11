# Data Provenance, Split Protocol, and Limitations

**Dataset**: CICIoT2023  
**Source Repository**: `siyam21/CIC-IoT-2023` (Hugging Face / UNB Canadian Institute for Cybersecurity)  
**Processed File**: `data/processed/recovery/recovery_processed.npz`  
**Fitted Scaler**: `data/processed/recovery/recovery_scaler.pkl`  

---

## 1. Raw Dataset Properties

- **Physical Environment**: 105 physical IoT devices (smart home, industrial sensors, IP cameras).
- **Attack Sub-Types**: 33 attack categories (DDoS-ICMP, DDoS-UDP, DoS-TCP, Mirai-greeth_flood, Recon-PortScan, Web-XSS, BruteForce-Dictionary, etc.).
- **7 Primary Classes**: DDoS, DoS, Reconnaissance, Mirai Botnet, Spoofing, Web-based, BruteForce.
- **Raw Feature Set**: 46 raw CSV columns per record.

---

## 2. Feature Selection & Frozen Schema

To prevent shortcut identity memorization, all IP addresses, MAC addresses, port numbers, and timestamps were dropped.

**Frozen 39-Feature Schema (`FEATURE_SCHEMA`)**:
- `flow_duration`, `Header_Length`, `Protocol_Type`, `Duration`, `Rate`, `Srate`, `Drate`
- `fin_flag_number`, `syn_flag_number`, `rst_flag_number`, `psh_flag_number`, `ack_flag_number`, `ece_flag_number`, `cwr_flag_number`
- `ack_count`, `active_Max`, `active_Min`, `active_Mean`, `active_Std`
- `idle_Max`, `idle_Min`, `idle_Mean`, `idle_Std`
- `fwd_pkts_s`, `bwd_pkts_s`
- `Min`, `Max`, `AVG`, `Std`, `Tot size`
- `IAT`, `Number`, `Magnitue`, `Radius`, `Covariance`, `Variance`, `Weight`
- `fl_tot_pkts`, `fl_tot_bytes`

---

## 3. Leak-Free Split Protocol

All scaling (`StandardScaler.fit()`) is fit **strictly on `X_train`**. Validation and test partitions are transformed without parameter recalculation (`scaler.transform()`).

| Partition | Sample Count | Benign Count | Attack Count | Attack % | Primary Usage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `X_train` | 100,000 | 100,000 | 0 | 0.0% | Scaler fitting & Unsupervised model training |
| `X_val` | 30,000 | 30,000 | 0 | 0.0% | Threshold parameter selection ($\tau_{95}, \tau_{99}, \alpha, k, \delta$) |
| `X_sup` | 40,000 | 20,000 | 20,000 | 50.0% | Supervised XGBoost Oracle training |
| `X_test` | 100,000 | 14,911 | 85,089 | 85.09% | Final leakage-free evaluation |

---

## 4. Critical Data Limitations & Disclosures

1. **Pre-Shuffled Raw Parquet Files**:
   - The Hugging Face raw Parquet split (`siyam21/CIC-IoT-2023/random/`) consists of sample-level randomly pre-shuffled flow records.
   - **Consequence**: Raw capture temporal ordering is lost across files. Constructing sliding sequence windows ($L > 1$) on pre-shuffled rows merges non-contiguous flows, causing sequence models (LSTM/GRU) to suffer sequence window boundary contamination ($\text{FPR}=1.0$).
   - **Resolution**: Evaluation is strictly performed on **sample-level flow vectors ($L=1$)**.
2. **High Test Attack Prevalence**:
   - Test attack prevalence is 85.09%, which inflates naive F1-Scores for all-1 predictors.
   - **Resolution**: All benchmark tables explicitly report False Positive Rate (FPR), Precision, Recall, PR-AUC, and ROC-AUC alongside F1-Score.
