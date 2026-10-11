# Pre-Registered Experiment Protocol (Revised Iteration 2)

**Document Date**: October 9, 2026  
**Primary Author**: Senior Research Engineer  
**Status**: Final Revised Experimental Protocol  

---

## 1. Dataset Protocol & Capture-Aware Splits

### Dataset Specification
* **Dataset**: CICIoT2023 (Canadian Institute for Cybersecurity, UNB).
* **Composition**: 105 physical IoT devices, 33 attack types in 7 categories + Benign.

### Feature Selection & Preprocessing
* **Included Features (40 numerical flow metrics)**: Header lengths, protocol type, flow duration, packet rates (`Rate`, `Srate`, `Drate`), TCP flags, Inter-Arrival Time (`IAT`) statistics, packet size aggregates (`Min`, `Max`, `AVG`, `Std`, `Tot size`, `Variance`, `Weight`).
* **Excluded Features**: Identifiers (`src_ip`, `dst_ip`, `src_port`, `dst_port`, `Timestamp` string) are dropped to prevent identity shortcut memorization.
* **Leakage-Resistant Preprocessing**:
  - `StandardScaler` fit **strictly on Training set**. Applied to Validation and Test sets without recalculating parameters.
  - Missing values imputed using training feature medians; infinite values clamped.

### Capture-Aware Split Protocols

#### A. Unsupervised Training Protocol (For Deep Autoencoders & iForest)
* **Training Partition (60%)**: Sequential capture files consisting **exclusively of Benign traffic** (~200,000 flow records).
* **Validation Partition (20%)**: Sequential Benign capture files (~60,000 flow records) for convergence check and initial threshold parameter selection ($\alpha, k, W$).
* **Test Partition (20%)**: Sequential held-out capture files (~60,000 flow records) containing Benign traffic and all 33 Attack families.

#### B. Supervised Reference Protocol (For XGBoost Oracle Reference ONLY)
* **Supervised Training Partition**: A distinct 50/50 Benign + Attack labeled sample (~50,000 flow records) drawn from the training capture files.
* *Purpose*: Serves as an **oracle baseline reference** to quantify the performance gap between unsupervised anomaly detection and full supervised classification with known labels.

---

## 2. Fair Baseline Specifications

| Model Class | Model Identifier | Objective Function | Input Shape | Training Data Partition | Threshold Tuning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Sequence Autoencoder** | **LSTM Autoencoder (LSTM-AE)** | MSE Loss | Sequence $(L=10, D=40)$ | Unsupervised Benign Train | Validation Split Errors |
| **Sequence Autoencoder** | **GRU Autoencoder (GRU-AE)** | MSE Loss | Sequence $(L=10, D=40)$ | Unsupervised Benign Train | Validation Split Errors |
| **Dense Autoencoder** | **Dense Autoencoder (Dense-AE)**| MSE Loss | Single Flow Vector $(D=40)$ | Unsupervised Benign Train | Validation Split Errors |
| **Non-Parametric Unsupervised**| **Isolation Forest (iForest)** | Anomaly Isolation Score | Single Flow Vector $(D=40)$ | Unsupervised Benign Train | Contamination Rate on Val |
| **Supervised Reference** | **XGBoost Classifier** | Binary Cross-Entropy | Single Flow Vector $(D=40)$ | Labeled Supervised Train | Probability Cutoff $p \ge 0.5$ |

---

## 3. Threshold Update Strategies

Let $E_t = |X_t - \hat{X}_t|^2$ denote the reconstruction error at timestep $t$.

### Strategy 1: Fixed Threshold ($\tau_{\text{fixed}}$)
* Static threshold $\tau = \text{Percentile}(E_{\text{val}}, 95)$ or $\text{Percentile}(E_{\text{val}}, 99)$ computed once on validation errors. Does not update during testing.

### Strategy 2: Un-Guarded Adaptive Threshold ($\tau_{\text{unguarded}}$)
* Updates running mean $\mu_t$ and variance $\sigma_t^2$ using **all incoming observations**, including flagged anomalies:
  $$\mu_t = (1-\alpha)\mu_{t-1} + \alpha E_t$$
  $$\sigma_t^2 = (1-\alpha)\sigma_{t-1}^2 + \alpha (E_t - \mu_t)^2$$
  $$\tau_t = \mu_t + k \cdot \sigma_t$$
* *Evaluated Property*: Ability to adapt to persistent traffic shifts, and susceptibility to threshold inflation during sustained attack floods.

### Strategy 3: Guarded Adaptive Threshold ($\tau_{\text{guarded}}$)
* Uses a bounded update / winsorized buffer rule:
  - If $E_t \le \tau_t$: Update $\mu_t, \sigma_t^2$ normally with $E_t$.
  - If $E_t > \tau_t$ (flagged anomaly): Update $\mu_t, \sigma_t^2$ using a **clamped error** $E_t^{\text{clamp}} = \tau_t + \delta \cdot \sigma_t$ (where $\delta \in [0.1, 0.5]$).
* *Evaluated Property*: Prevents severe threshold inflation during sustained attacks while permitting gradual adaptation if a benign traffic level shift persists over time.

---

## 4. Controlled Traffic-Shift & Attack Evaluation

1. **Synthetic Rate-Scaling Stress Test**:
   - Apply controlled inter-arrival time and packet rate scaling ($1.5\times, 2.0\times, 4.0\times$) to benign test streams to simulate legitimate traffic volume surges.
   - *Explicit Classification*: Labeled explicitly as a **synthetic stress test**, not proof of real-world concept drift.
2. **Sustained Attack Inflation Test**:
   - Inject continuous, high-volume DDoS/DoS attack streams to measure whether un-guarded thresholds inflate and cause attack leakages over time.
3. **Per-Attack Sub-type Evaluation**:
   - Evaluate detection recall across all 33 attack sub-types (DDoS-ICMP, DoS-UDP, PortScan, ARP Spoofing, SQL Injection, Mirai, etc.).

---

## 5. Metrics & Statistical Design

### Metrics Recorded
* **Detection Quality**: Precision, Recall, F1-Score, False Positive Rate (FPR), Precision-Recall AUC (PR-AUC).
* **Adaptation Dynamics**: False Positive Rate decay time (timesteps) during rate surges; Recall decay during sustained attacks.
* **Efficiency**: Microseconds per sample inference latency ($\mu s/\text{sample}$) and RAM footprint (MB).

### Paired Statistical Verification
* **Initial Stability Check**: 5 random seeds ($42, 123, 456, 789, 2026$) for model initialization.
* **Paired Statistical Test**: Primary statistical inferences will be drawn using two-tailed **paired Wilcoxon signed-rank tests** ($p < 0.05$) across the 33 attack sub-types and 10 capture segments to rigorously compare threshold strategies.
