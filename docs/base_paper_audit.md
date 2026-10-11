# Comprehensive Base Paper Audit

**Paper Title**: An AI-Driven Cybersecurity Framework for IoT: Integrating LSTM-Based Anomaly Detection, Reinforcement Learning, and Post-Quantum Encryption  
**Primary Auditor**: Senior Research Engineer & Cybersecurity AI Specialist  
**Target Paper File**: `An_AI-Driven_Cybersecurity_Framework_for_IoT_Integ.pdf`  
**Audit Date**: October 2026  

---

## 4.1 Bibliographic Information

* **Exact Title**: An AI-Driven Cybersecurity Framework for IoT: Integrating LSTM-Based Anomaly Detection, Reinforcement Learning, and Post-Quantum Encryption
* **Author**: Mozamel M. Saeed (Department of Computer Science, Prince Sattam Bin Abdulaziz University, Al Kharj 16278, Saudi Arabia; Email: `m.musa@psau.edu.sa`)
* **Publication Venue**: *IEEE Access* (Volume 13, Pages 104027–104036)
* **Publication Year**: Received May 10, 2025; Accepted May 27, 2025; Published June 4, 2025; Current Version June 23, 2025.
* **Digital Object Identifier (DOI)**: [10.1109/ACCESS.2025.3576506](https://doi.org/10.1109/ACCESS.2025.3576506)
* **Official Publisher URL**: https://ieeexplore.ieee.org/document/10547055 (DOI Link: https://doi.org/10.1109/ACCESS.2025.3576506)
* **Grant Support**: Deanship of Scientific Research at Prince Sattam Bin Abdulaziz University under Research Project #2020/01/16826.

---

## 4.2 Research Objective

* **Stated Problem**: Traditional rule-based defense systems and static security mechanisms are increasingly inadequate against dynamic, sophisticated, and high-frequency cybersecurity threats in resource-constrained IoT infrastructures.
* **Proposed Solution**: An integrated 4-component AI-driven cybersecurity framework combining:
  1. Deep Learning (LSTM) for time-series network traffic anomaly detection.
  2. Cryptographic Hashing ("Homomorphic Hashing" using salted SHA-256) for real-time packet data integrity verification.
  3. Reinforcement Learning (Q-learning) for dynamic, automated incident response.
  4. Post-Quantum Cryptography (Lattice-based encryption grounded in Learning With Errors - LWE) for forward-resilient communication security against quantum adversaries.
* **Intended Deployment Environment**: Heterogeneous IoT networks, smart cities, healthcare systems, critical infrastructure, and Cloud-IoT edge gateways.
* **Threat Model**: Network-level intrusion attacks (Denial of Service - DoS, data injection, spoofing, packet mimicry, time-delayed injections, data poisoning) along with transit data tampering and potential future quantum-era decryption attacks.

---

## 4.3 Original Architecture

The base paper proposes an end-to-end operational pipeline connecting four main components:

```
                  +-----------------------------------+
                  |  IoT Traffic / Network Events     |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |  1. LSTM Anomaly Detector         |
                  |  (30s lookback, Predicts X_t+1)   |
                  +-----------------------------------+
                                    |
                    Anomaly Score E_t = |X_t - X_hat_t| > Tau
                                    |
                   +----------------+----------------+
                   |                                 |
                   v                                 v
    +-----------------------------+   +-----------------------------+
    | 2. Salted SHA-256 Integrity |   | 3. Q-Learning Response Agent|
    | H(m, s) = SHA-256(m XOR s)  |   | States: No/Mild/Severe      |
    | Flag tampered packets       |   | Actions: Block / Counter    |
    +-----------------------------+   +-----------------------------+
                   |                                 |
                   +----------------+----------------+
                                    |
                                    v
                  +-----------------------------------+
                  | 4. Post-Quantum Encryption        |
                  | LWE: y = A*x + e mod q           |
                  +-----------------------------------+
```

### Component Breakdown:
1. **LSTM Anomaly Detector**: Takes preprocessed time-series network traffic with a 30-second lookback window. Predicts the next step vector $\hat{x}_{t+1}$. Computes reconstruction/prediction error $E_t = |x_t - \hat{x}_t|$. Flags anomalies if $E_t > \tau$.
2. **Data Integrity Verifier**: Calculates salted SHA-256 hash $H(m, s) = \text{SHA-256}(m \oplus s)$ or $\text{SHA-256}(\text{SALT} + \text{data})$ on received packet payloads. Verifies integrity by matching received digest with reference digest.
3. **Q-Learning Incident Response**: Maps threat state $s \in \{\text{No Attack}, \text{Mild Attack}, \text{Severe Attack}\}$ to optimal defensive action $a \in \{\text{Block}, \text{Counter-attack}\}$ using learned Q-values.
4. **LWE Post-Quantum Encryption**: Encrypts inter-device IoT messages using lattice-based LWE formulation $y = Ax + e \pmod q$.

---

## 4.4 Dataset Audit

The table below lists every dataset parameter reported or missing in the base paper:

| Dataset Parameter | Paper Description | Status / Audit Classification |
| :--- | :--- | :--- |
| **Dataset Origin** | Simulated IoT environment (smart sensors, actuators, edge devices connected to central gateway). | **CONFIRMED FROM PAPER** (Section II-A1) |
| **Public Download Link** | None provided in paper or metadata. | **NOT REPORTED** |
| **Number of Records** | Approximately 150,000 labeled network events. | **CONFIRMED FROM PAPER** |
| **Class Distribution** | 60% normal traffic, 40% diverse attack types. | **CONFIRMED FROM PAPER** |
| **Attack Categories** | Denial of Service (DoS), data injection, spoofing, packet mimicry, time-delayed injection. | **CONFIRMED FROM PAPER** |
| **Input Features** | Timestamp, packet size, inter-arrival time, protocol used, source ID, destination ID. | **PARTIALLY DESCRIBED** (Exact schema/column count unstated) |
| **Feature Types** | Numerical and categorical. | **PARTIALLY DESCRIBED** |
| **Preprocessing** | Min-Max/Standard normalization for numerical, One-Hot Encoding for categorical. | **PARTIALLY DESCRIBED** |
| **Train/Val/Test Splits** | Not stated (e.g. 70/15/15 or 80/20 unmentioned). | **NOT REPORTED** |
| **Sequence Window** | 30-second lookback window. | **CONFIRMED FROM PAPER** |
| **Data Generation Script** | Not provided. | **NOT REPORTED** |
| **Random Seeds** | Not stated. | **NOT REPORTED** |
| **Missing Values / Handling** | Not reported. | **NOT REPORTED** |
| **Duplicate Handling** | Not reported. | **NOT REPORTED** |
| **Temporal Train/Test Split**| Unclear if chronological or random row split. | **NOT REPORTED** |

---

## 4.5 LSTM Model Audit

| Hyperparameter / Setting | Value in Base Paper | Audit Status |
| :--- | :--- | :--- |
| **Architecture Type** | Basic LSTM time-series predictor. | **CONFIRMED FROM PAPER** (Section II-A2) |
| **Number of Layers** | Unstated (1, 2, or more layers?). | **NOT REPORTED** |
| **Hidden Layer Dimensions**| Unstated (e.g., 64, 128, 256 units?). | **NOT REPORTED** |
| **Dropout / Regularization**| Unstated. | **NOT REPORTED** |
| **Input Sequence Length** | 30-second lookback window (number of timesteps unstated). | **PARTIALLY DESCRIBED** |
| **Loss Function** | Mean Squared Error (MSE): $L = \frac{1}{N} \sum (x_i - \hat{x}_i)^2$. | **CONFIRMED FROM PAPER** (Eq. 3) |
| **Optimizer** | Unstated (Adam, SGD, RMSprop?). | **NOT REPORTED** |
| **Learning Rate** | Unstated (e.g., 0.001?). | **NOT REPORTED** |
| **Batch Size** | Unstated. | **NOT REPORTED** |
| **Epochs / Early Stopping** | Unstated. | **NOT REPORTED** |
| **Threshold ($\tau$) Selection**| Fixed threshold at 95th percentile of reconstruction errors (Section III-A). | **CONFIRMED FROM PAPER** |
| **Evaluation Metrics** | Accuracy (reported high), single timestamp prediction error table (Table 1: 5 sample rows). | **PARTIALLY DESCRIBED** (Lacks Precision, Recall, F1, ROC-AUC) |

---

## 4.6 Threshold Audit: Fixed vs. Adaptive

* **Paper Claim in Abstract & Discussion**: Claims an "adaptive thresholding mechanism, which dynamically adjusts based on the statistical distribution of reconstruction errors" (Section IV).
* **Paper Text in Methodology & Results**:
  - Section II-A2b: Defines $E_t = |x_t - \hat{x}_t|$, and if $E_t > \tau$ where $\tau$ is a "predefined threshold", an anomaly is flagged.
  - Section III-A: States explicitly: *"In this study, a basic LSTM architecture with a fixed threshold-setting approach was implemented for identifying anomalies. While this setup effectively detected deviations in most cases, it exhibited limitations in capturing abrupt or rare events."*
  - Section III-A: Refers to setting $\tau$ at the 95th percentile of errors on normal training data.
* **Audit Finding**: There is a **direct contradiction** in the text between the Abstract/Discussion (which claims adaptive thresholding was incorporated) and Section III-A (which explicitly admits that only a static fixed threshold was implemented). This proves that dynamic threshold adaptation was **NOT actually evaluated empirically** in the base paper.

---

## 4.7 Reinforcement Learning (Q-Learning) Audit

| RL Component | Base Paper Specification | Audit Evaluation |
| :--- | :--- | :--- |
| **State Space ($S$)** | 3 discrete states: $S = \{\text{No Attack}, \text{Mild Attack}, \text{Severe Attack}\}$. | **CONFIRMED FROM PAPER** |
| **Action Space ($A$)** | 2 discrete actions: $A = \{\text{Block}, \text{Counter-attack}\}$. | **CONFIRMED FROM PAPER** |
| **Reward Function ($R$)** | Static learned preferences: No Attack $\rightarrow (0, 0)$; Mild Attack $\rightarrow \text{Block: } 10.0, \text{Counter: } 5.0$; Severe Attack $\rightarrow \text{Block: } 5.0, \text{Counter: } 15.0$. | **CONFIRMED FROM PAPER** (Table 3) |
| **Transition Function ($P$)**| Not defined or modeled. | **NOT REPORTED** |
| **Discount Factor ($\gamma$)** | Formula states $\gamma$, value unstated. | **NOT REPORTED** |
| **Learning Rate ($\alpha$)** | Formula states $\alpha$, value unstated. | **NOT REPORTED** |
| **Exploration Policy** | Unstated ($\epsilon$-greedy parameter unmentioned). | **NOT REPORTED** |
| **Interactive Testbed** | None. The paper does not run a dynamic environment simulation; it presents a static $3 \times 2$ lookup table. | **NOT REPORTED / TRIVIAL** |

---

## 4.8 Data Integrity & "Homomorphic Hashing" Audit

* **Stated Equation**: $H(m, s) = \text{SHA-256}(m \oplus s)$ (Eq. 5) or $H = \text{SHA-256}(\text{SALT} + \text{data})$ (Eq. 10).
* **Mathematical Property Audit**:
  - Homomorphic hashing requires additive or multiplicative homomorphism (e.g., $H(m_1 + m_2) = H(m_1) \otimes H(m_2)$ or $H(m_1 \oplus m_2) = H(m_1) \odot H(m_2)$).
  - SHA-256 is an iterated cryptographic hash based on the Merkle–Damgård construction with complete avalanche effects. It is explicitly designed to be **non-homomorphic**.
* **Audit Conclusion**: The construction in the base paper is a standard **salted hash digest / keyed hash message verification**, NOT homomorphic hashing. Describing standard SHA-256 as homomorphic is a severe cryptographic misnomer.

---

## 4.9 Post-Quantum Cryptography (LWE) Audit

* **Stated Equation**: $y = Ax + e \pmod q$ (Eq. 8), where $A$ is a random matrix, $x$ is the secret key, $e$ is noise, and $q$ is modulus.
* **Missing Experimental & Implementation Details**:
  - Scheme specification: Generic LWE vs. RLWE vs. Module-LWE (NIST ML-KEM).
  - Parameter set: Modulus $q$, dimension $n$, noise distribution $\chi$ unstated.
  - Security level: NIST Category 1 (128-bit), Category 3 (192-bit), or Category 5 (256-bit) unstated.
  - Implementation Library: Unstated (no code, no library like liboqs or PyCryptodome cited).
  - Key and Ciphertext Sizes: Unstated.
  - Performance Measurement: Zero empirical timing measurements (ms), throughput (Mbps), or CPU/memory overhead benchmarks reported in the results.
* **Audit Conclusion**: The PQC section in the base paper is purely high-level theoretical prose. It lacks an actual parameterised cryptographic protocol implementation.

---

## 4.10 Claims and Evidence Assessment

| Base Paper Claim | Evidence Supplied | Reproducibility Status | Audit Limitations / Flaws | Independent Test Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **1. LSTM achieves high anomaly detection accuracy.** | 5 timestamp sample rows in Table 1 showing prediction vs. ground truth. | **UNREPRODUCIBLE** | No public dataset, no hyperparameter specs, no overall test metrics (F1, Precision, Recall, ROC-AUC). | Train LSTM & baselines on CICIoT2023 with 5-fold CV & report standard metrics. |
| **2. Dynamic adaptive thresholding improves reliability.** | Text claim in Abstract/Discussion; contradicted by Section III-A which states a fixed threshold was used. | **NOT IMPLEMENTED IN BASE PAPER** | Contradictory text. No adaptive algorithm presented or tested. | Implement & benchmark Dynamic EWMA vs. Rolling Quantile vs. Fixed threshold under rate shift. |
| **3. Q-learning dynamically optimizes incident response.** | Static $3 \times 2$ Q-table (Table 3) with arbitrary reward values (0, 5, 10, 15). | **TRIVIAL LOOKUP TABLE** | No interactive environment, no network dynamics, unethical "counter-attack" action. | Build explicit, constrained MDP simulation with cost-benefit metrics & defensive actions only. |
| **4. Homomorphic hashing verifies real-time integrity.** | SHA-256 digest comparison (Table 2). | **MISLABELED METHOD** | SHA-256 is non-homomorphic. Standard salted hashdigest verification. | Implement HMAC-SHA256 & hash-chained audit logging; benchmark throughput & storage overhead. |
| **5. LWE post-quantum encryption protects IoT communications.** | Text formula $y = Ax + e \pmod q$. | **THEORETICAL TEXT ONLY** | No parameter set, no implementation code, zero benchmark results. | Benchmark NIST ML-KEM-512/768/1024 (FIPS 203) key encapsulation with AES-256-GCM AEAD. |

---

## 4.11 Base Paper Limitations Summary

### A. Author-Stated Limitations (Section IV-A)
1. Tested only in a simulated environment with controlled datasets, which may not capture live network heterogeneity, varying bandwidths, and unpredicted behaviors.
2. Potential scalability issues in large-scale or resource-constrained deployments without optimization.
3. Does not evaluate robustness against adversarial machine learning attacks.

### B. Discovered Audit Limitations & Methodological Flaws
1. **Unreleased Data & Code**: Complete lack of public repository, dataset artifacts, or hyperparameter specifications.
2. **Internal Contradictions**: Abstract and Discussion claim adaptive thresholding was incorporated, whereas Section III-A explicitly admits using a fixed threshold.
3. **Cryptographic Misnomer**: Mislabels standard salted SHA-256 as "homomorphic hashing".
4. **Trivial RL Model**: Hardcoded $3 \times 2$ Q-table with static preference rewards instead of an interactive network MDP.
5. **Non-Benchmarked PQC**: LWE described purely in mathematical abstract terms with zero runtime, latency, key size, or memory measurements.
6. **Inadequate Baselines**: Zero comparison with standard ML/DL baselines (Autoencoders, Isolation Forest, XGBoost, GRU) or statistical significance testing.
