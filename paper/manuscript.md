# Adaptive Anomaly Thresholding, Un-Contaminated Reinforcement Learning Defense, and Standardized Post-Quantum Encryption for IoT Cybersecurity

**Author**: Tanish Thakare  
**Affiliation**: Department of Computer Science and Engineering, Independent Research  
**Target Venue**: IEEE Access (Manuscript Draft Prepared for Peer Review)  
**Artifact Repository**: https://github.com/Tanish-boop/AI-Driven-IoT-Cybersecurity-Framework-Research-  

---

## Abstract
In Internet of Things (IoT) edge cybersecurity, deep reconstruction-based autoencoders provide effective detection of zero-day network intrusions without requiring labeled attack samples during training. However, translating continuous reconstruction errors into operational mitigation decisions faces critical vulnerabilities: static decision thresholds explode in false alarms under non-stationary traffic surges, un-guarded adaptive thresholds suffer severe threshold inflation collapse during attack floods, defensive reinforcement learning policies risk evaluation split contamination, and existing literature relies on abstract non-standardized cryptographic assumptions. This paper presents an empirically rigorous benchmark evaluating an integrated five-stage cybersecurity framework on CICIoT2023 across 5 random seeds ($42, 123, 456, 789, 2026$) under strictly isolated training, validation, supervised, and held-out test splits.

Our empirical results establish that:
1. Sample-level Dense Autoencoders ($L=1$) eliminate sequence window boundary contamination, achieving an unsupervised baseline F1-Score of **0.8854 ± 0.0013** (Precision: $0.9893 \pm 0.0003$, Recall: $0.8013 \pm 0.0022$, FPR: $0.0493 \pm 0.0013$).
2. Excluded EWMA thresholding prevents inflation collapse, reaching F1 = **0.9014 ± 0.0018** (Recall: $0.8401 \pm 0.0023$, FPR: $0.1360 \pm 0.0110$), coming within 2.55% of the Supervised XGBoost Oracle (F1: $0.9269 \pm 0.0004$).
3. Static 95th percentile thresholds suffer a **+454.4% explosion in false positive rates** under $2.0\times$ synthetic rate feature scaling (jumping from 4.93% to 27.33%).
4. Under strictly un-contaminated evaluation (`X_sup` training, held-out `X_test` evaluation), **Deep Q-Networks (DQN)** achieve **71.26% ± 0.09% attack containment** with a **0.63% ± 0.46% false block rate** (decision latency: $0.1160 \pm 0.0052$ ms), while **Tabular Q-Learning** achieves a **0.00% false block rate** in isolated testing with ultra-low decision latency (**0.0122 ± 0.0003 ms**).
5. Standardized NIST FIPS 203 **ML-KEM-768** key encapsulation paired with AES-256-GCM achieves sub-millisecond key establishment (**0.2758 ms** KEM, **0.2905 ms** first-message setup) and 100% tamper rejection.
6. HMAC-SHA-256 ($0.0470$ ms creation) and **Tamper-Evident Hash-Chain Audit Logging** ($0.0605$ ms append, $\mathcal{O}(1)$ scaling) provide verifiable sequence integrity and tamper localization.
7. Evaluating on a deduplicated test set ($N=98,543$) purging all 1,457 cross-partition duplicates shifts F1 by at most $-0.0009$ ($-0.10\%$), confirming that repeated feature patterns do not materially inflate evaluation metrics.
8. The full integrated framework achieves an end-to-end F1-Score of **0.8968 ± 0.0013** and **81.01% ± 2.83%** attack containment with edge processing latency of **0.9626 ± 0.6304 ms** ($1,436.2 \pm 759.5$ events/s throughput).

---

## 1. Introduction

The proliferation of Internet of Things (IoT) devices in critical infrastructure, industrial automation, and consumer environments has drastically expanded the cyber-attack surface. Traditional rule-based Intrusion Detection Systems (IDS) rely on signature databases that fail against novel zero-day attacks and stealthy multi-vector traffic anomalies.

Deep learning models—specifically unsupervised autoencoders—have emerged as a primary defensive paradigm. By training models exclusively on normal (benign) network telemetry, the model learns the underlying statistical structure of legitimate traffic. During operational deployment, network flows with high reconstruction errors $E_t = \|X_t - \hat{X}_t\|^2$ are flagged as anomalies.

However, four fundamental operational bottlenecks remain:
1. **Anomaly Boundary Adaptation**: Current literature predominantly sets decision thresholds ($\tau$) at fixed percentiles (e.g., 95th percentile). Under non-stationary traffic shifts, fixed thresholds cause severe false positive explosions. Adaptive mechanisms like standard EWMA suffer from threshold inflation during continuous attack floods.
2. **Un-Contaminated Defensive Mitigation**: Reinforcement learning policies for defensive response must be trained strictly on dedicated training partitions without exposing reserved test partitions, preventing evaluation split contamination.
3. **Standardized Post-Quantum Encryption**: IoT telemetry requires quantum-resistant key encapsulation paired with authenticated symmetric encryption, replacing abstract unstandardized claims with concrete NIST FIPS 203 primitives.
4. **Verifiable Audit Logging**: Local evidence logging requires tamper-evident cryptographic sequencing with explicit threat modeling regarding local storage rewrite capabilities.

---

## 2. Pre-Registered Experimental Methodology

### 2.1 Dataset & Feature Selection
We evaluate our protocol on **CICIoT2023**, extracting 39 numerical flow features. Non-numeric metadata identifiers (`src_ip`, `dst_ip`, `src_port`, `dst_port`, `Timestamp`, `flow_id`) are explicitly dropped to eliminate shortcut identity memorization. Evaluation is strictly conducted on sample-level flow features ($L=1$).

### 2.2 Strict Split Protocol
- **Unsupervised Benign Train Split (`X_train`)**: 100,000 Benign flow records.
- **Unsupervised Benign Validation Split (`X_val`)**: 30,000 Benign flow records.
- **Supervised Policy Split (`X_sup`)**: 40,000 50/50 Benign+Attack records (used for RL training).
- **Held-Out Test Split (`X_test`)**: 100,000 flow records (14,911 Benign, 85,089 Attack) strictly reserved for held-out evaluation.

### 2.3 Deployment Hardware Scope & Environmental Boundaries
All benchmarks reported in this study were executed on an AMD64 host architecture (Windows 11 x86_64, 3.40 GHz). No physical measurements were performed on ARM64 or Raspberry Pi hardware; embedded edge gateway and microcontroller porting represent modeled targets for future hardware-in-the-loop validation. Deeply embedded microcontrollers (<100 MHz clock frequencies) possess stringent cycle and memory constraints; executing neural network inferences and lattice-based ML-KEM-768 on such microcontrollers would require dedicated integer-only quantization (e.g., TFLite Micro) and optimized assembly implementations, which represents a separate research trajectory.

---

## 3. Experimental Results & Analysis

### 3.1 Base Test Stream Performance (5 Random Seeds)

| Model | Threshold Strategy | Precision | Recall | F1-Score | False Positive Rate (FPR) | PR-AUC | ROC-AUC |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dense-AE** | **Excluded EWMA** | $0.9724 \pm 0.0022$ | **$0.8401 \pm 0.0023$** | **$0.9014 \pm 0.0018$** | $0.1360 \pm 0.0110$ | $0.9867 \pm 0.0005$ | $0.9225 \pm 0.0027$ |
| Dense-AE | Fixed 95th Percentile | $0.9893 \pm 0.0003$ | $0.8013 \pm 0.0022$ | $0.8854 \pm 0.0013$ | $0.0493 \pm 0.0013$ | $0.9867 \pm 0.0005$ | $0.9225 \pm 0.0027$ |
| Dense-AE | Fixed 99th Percentile | $0.9975 \pm 0.0001$ | $0.7650 \pm 0.0017$ | $0.8659 \pm 0.0011$ | $0.0108 \pm 0.0004$ | $0.9867 \pm 0.0005$ | $0.9225 \pm 0.0027$ |
| Dense-AE | Guarded EWMA | $1.0000 \pm 0.0000$ | $0.0022 \pm 0.0000$ | $0.0045 \pm 0.0001$ | $0.0000 \pm 0.0000$ | $0.9867 \pm 0.0005$ | $0.9225 \pm 0.0027$ |
| Dense-AE | Un-Guarded EWMA | $1.0000 \pm 0.0000$ | $0.0001 \pm 0.0000$ | $0.0003 \pm 0.0001$ | $0.0000 \pm 0.0000$ | $0.9867 \pm 0.0005$ | $0.9225 \pm 0.0027$ |
| Isolation Forest | Fixed 95th Percentile | $0.9866 \pm 0.0003$ | $0.6402 \pm 0.0114$ | $0.7765 \pm 0.0084$ | $0.0495 \pm 0.0009$ | $0.9754 \pm 0.0035$ | $0.8828 \pm 0.0095$ |
| **XGBoost Oracle** | **Supervised Prob 0.5** | $0.9967 \pm 0.0002$ | **$0.8662 \pm 0.0009$** | **$0.9269 \pm 0.0004$** | $0.0162 \pm 0.0012$ | $0.9946 \pm 0.0000$ | $0.9682 \pm 0.0001$ |

### 3.2 Evaluation on Deduplicated Test Sets (Impact of Feature Overlap across 5 Random Seeds)
To investigate the empirical impact of repeated flow feature patterns, we evaluated the core models across all 5 random seeds ($42, 123, 456, 789, 2026$) on both the full held-out test set ($N=100,000$) and a strictly deduplicated test set ($N=98,543$) from which all 1,457 rows sharing identical numerical feature vectors with `X_train` or `X_sup` were purged:

| Model & Strategy | Full Test Set ($N=100\text{k}$) F1 | Deduplicated Test Set ($N=98.5\text{k}$) F1 | F1 Delta ($\Delta$) | Full Test FPR | Deduplicated FPR |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Dense-AE Fixed 95th** | $0.8854 \pm 0.0013$ | $0.8845 \pm 0.0014$ | $-0.0009 \pm 0.0001$ ($-0.10\%$) | $0.0493 \pm 0.0013$ | $0.0492 \pm 0.0013$ |
| **Dense-AE Excluded EWMA** | $0.9014 \pm 0.0018$ | $0.9007 \pm 0.0019$ | $-0.0007 \pm 0.0003$ ($-0.08\%$) | $0.1360 \pm 0.0110$ | $0.1363 \pm 0.0115$ |
| **XGBoost Oracle** | $0.9269 \pm 0.0004$ | $0.9265 \pm 0.0003$ | $-0.0003 \pm 0.0001$ ($-0.03\%$) | $0.0162 \pm 0.0012$ | $0.0160 \pm 0.0011$ |

Across all five seeds, purging cross-partition identical feature vectors shifts F1-scores by less than $0.0010$ (at most $-0.10\%$), and FPR shifts by less than $0.0003$.

### 3.3 Synthetic Feature Rate Stress Test Results (E8)

| Model | Strategy | Precision | Recall | F1-Score | False Positive Rate (FPR) | FPR Increase |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dense-AE** | **Fixed 95th Base (1.0x)** | $0.9893 \pm 0.0003$ | $0.8013 \pm 0.0022$ | $0.8854 \pm 0.0013$ | $0.0493 \pm 0.0013$ | Baseline |
| Dense-AE | Fixed 95th Stress (1.5x) | $0.9796 \pm 0.0019$ | $0.8013 \pm 0.0022$ | $0.8815 \pm 0.0017$ | $0.0953 \pm 0.0092$ | +93.3% |
| **Dense-AE** | **Fixed 95th Stress (2.0x)** | $0.9436 \pm 0.0030$ | $0.8013 \pm 0.0022$ | $0.8666 \pm 0.0021$ | **$0.2733 \pm 0.0152$** | **+454.4%** |

*Operational Scope Disclosure*: In Experiment E8, synthetic scaling was applied strictly to rate features (`Rate`, `Tot size`, `Variance`) of benign test samples for Fixed 95th Percentile thresholding to evaluate sensitivity to burst telemetry. Excluded EWMA was evaluated on the base stream in Experiment E2 and was not re-evaluated under synthetic feature scaling in E8; threshold stability claims are strictly confined to the dynamic stream conditions tested in E2.

### 3.4 Granular Per-Attack Category Recall Breakdown

| Attack Category | Sample Count | Fixed 95th Recall | Excluded EWMA Recall |
| :--- | :---: | :---: | :---: |
| DDoS | 33,483 | $100.0\%$ | $100.0\%$ |
| DoS | 15,107 | $100.0\%$ | $100.0\%$ |
| Mirai | 11,160 | $100.0\%$ | $100.0\%$ |
| BruteForce | 965 | $42.80\%$ | $\mathbf{55.54\%}$ |
| Reconnaissance | 15,038 | $38.18\%$ | $\mathbf{49.19\%}$ |
| Spoofing | 7,451 | $23.38\%$ | $\mathbf{39.15\%}$ |
| Web-based | 1,885 | $20.42\%$ | $\mathbf{37.88\%}$ |
| **Total Attack Stream** | **85,089** | **$79.95\%$** | **$83.81\%$** |

### 3.5 Un-Contaminated Defensive-Response Policy Evaluation (E4 Rerun)

| Evaluation Scenario | Mitigation Policy | Cumulative Reward | Attack Containment (%) | False Block Rate (%) | Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Scenario 1 (Heavy)** | Static Rule-Based | $35,402.00 \pm 0.00$ | $99.98\% \pm 0.00\%$ | $100.00\% \pm 0.00\%$ | $0.0123 \pm 0.0033$ |
| Scenario 1 (Heavy) | **Tabular Q-Learning** | $17,199.00 \pm 3,799.62$ | $60.45\% \pm 11.91\%$ | **$0.00\% \pm 0.00\%$** | **$0.0122 \pm 0.0003$** |
| Scenario 1 (Heavy) | **DQN** | $28,513.20 \pm 122.92$ | **$71.26\% \pm 0.09\%$** | **$0.63\% \pm 0.46\%$** | $0.1160 \pm 0.0052$ |
| **Scenario 2 (Stealth)**| Static Rule-Based | $35,762.00 \pm 0.00$ | $99.98\% \pm 0.00\%$ | $100.00\% \pm 0.00\%$ | $0.0115 \pm 0.0015$ |
| Scenario 2 (Stealth)| **Tabular Q-Learning** | $16,661.60 \pm 4,096.27$ | $59.27\% \pm 11.50\%$ | **$0.00\% \pm 0.00\%$** | **$0.0122 \pm 0.0002$** |
| Scenario 2 (Stealth)| **DQN** | $29,506.00 \pm 156.37$ | **$73.06\% \pm 0.09\%$** | **$0.48\% \pm 0.39\%$** | $0.1226 \pm 0.0120$ |

### 3.6 Post-Quantum Cryptography Microbenchmark (E5)
Evaluated for 1024-byte telemetry payloads across 100 trials on AMD64 host CPU:

| ML-KEM Variant | Public Key (B) | Secret Key (B) | Ciphertext (B) | Total KEM (ms) | First-Msg Setup (ms) | Tamper Rejection |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **ML-KEM-512** | 800 | 1,632 | 768 | 0.1757 | 0.1895 | 100.0% |
| **ML-KEM-768** | 1,184 | 2,400 | 1,088 | **0.2758** | **0.2905** | **100.0%** |
| **ML-KEM-1024** | 1,568 | 3,168 | 1,568 | 0.4363 | 0.4538 | 100.0% |

### 3.7 Integrity Verification Architecture Benchmark (E6)
Evaluated across 100 trials with 1 KiB evidence records:

| Integrity Mechanism | Create (ms) | Verify (ms) | Overhead (Bytes) | Throughput (MB/s) | Core Security Guarantee |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Salted SHA-256** | $0.0468 \pm 0.0240$ | $0.0207 \pm 0.0134$ | 193 B | 20.85 MB/s | Accidental error detection (Unkeyed) |
| **HMAC-SHA-256** | $0.0470 \pm 0.0209$ | $0.0214 \pm 0.0097$ | 170 B | 20.79 MB/s | Authenticity & anti-forgery (Keyed) |
| **Tamper-Evident Hash Chain Log** | $0.0605 \pm 0.0248$ | $0.0328 \pm 0.0310$ | 318 B | 16.15 MB/s | Append-only sequence & tamper localization |

### 3.8 Integrated Framework Ablation Study (E7)

| Variant | F1-Score | Recall (%) | Containment (%) | False Block (%) | Availability (%) | Latency (ms) | Throughput (ev/s) | Overhead (B) | Quantum Safe | Audit Integrity |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Study-Defined Baseline (Adapted Saeed)** | $0.8837 \pm 0.0004$ | $79.88\% \pm 0.06\%$ | $79.88\% \pm 0.06\%$ | $3.20\% \pm 0.07\%$ | $96.80\% \pm 0.07\%$ | $0.8103 \pm 0.5338$ | $1676.4 \pm 866.9$ | 194 B | No (Vulnerable) | No (Unkeyed) |
| **Ablation (-Adaptive Threshold)** | $0.8837 \pm 0.0004$ | $79.88\% \pm 0.06\%$ | $80.58\% \pm 3.12\%$ | $5.46\% \pm 2.55\%$ | $94.54\% \pm 2.55\%$ | $0.8579 \pm 0.5443$ | $1496.5 \pm 676.6$ | 321 B | Yes (NIST ML-KEM) | Yes (Hash Chain) |
| **Ablation (-RL Defense)** | $0.8968 \pm 0.0013$ | $82.68\% \pm 0.24\%$ | $79.78\% \pm 0.06\%$ | $3.22\% \pm 0.06\%$ | $96.78\% \pm 0.06\%$ | $0.9737 \pm 0.7128$ | $1534.4 \pm 873.1$ | 321 B | Yes (NIST ML-KEM) | Yes (Hash Chain) |
| **Ablation (-PQC)** | $0.8968 \pm 0.0013$ | $82.68\% \pm 0.24\%$ | $81.01\% \pm 2.83\%$ | $6.01\% \pm 1.52\%$ | $93.99\% \pm 1.52\%$ | $0.9103 \pm 0.5070$ | $1402.5 \pm 717.6$ | 321 B | No (Vulnerable) | Yes (Hash Chain) |
| **Ablation (-Hash Chain Log)** | $0.8968 \pm 0.0013$ | $82.68\% \pm 0.24\%$ | $81.01\% \pm 2.83\%$ | $6.01\% \pm 1.52\%$ | $93.99\% \pm 1.52\%$ | $1.2107 \pm 0.7004$ | $1196.6 \pm 819.5$ | 194 B | Yes (NIST ML-KEM) | No (Unkeyed) |
| **Full Proposed Framework** | $\mathbf{0.8968 \pm 0.0013}$ | $\mathbf{82.68\% \pm 0.24\%}$ | $\mathbf{81.01\% \pm 2.83\%}$ | $6.01\% \pm 1.52\%$ | $93.99\% \pm 1.52\%$ | $\mathbf{0.9626 \pm 0.6304}$ | $\mathbf{1436.2 \pm 759.5}$ | 321 B | **Yes (NIST ML-KEM)** | **Yes (Hash Chain)** |

*Attribution Note*: The "Study-Defined Baseline (Adapted Saeed)" row represents our empirical benchmark implementation adapting the general concepts proposed by Saeed (2025) (fixed percentile threshold + static rule escalation + salted SHA-256) using a sample-level Dense Autoencoder on CICIoT2023 under identical test conditions, as Saeed (2025) used an LSTM Autoencoder with a 30s lookback on a private unreleased dataset and reported zero global test stream F1/Recall metrics. We do not claim this was Saeed's published score or that the original LSTM was exactly reproduced.

### 3.9 Extended Hypothesis Testing & Statistical Significance

| Comparison | Metric | Mean Diff (95% CI) | Paired t-stat | t p-value | Holm-Bonf p-val | Cohen's d | Significant ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| Dense-AE Excluded_EWMA vs Fixed_95 | F1-Score | +0.0160 [0.0147, 0.0173] | t=33.805 | p=4.57e-06 | p=2.74e-05 | d=15.12 | **YES** |
| Dense-AE Fixed_95 vs Fixed_99 | F1-Score | +0.0195 [0.0183, 0.0207] | t=46.211 | p=1.31e-06 | p=1.05e-05 | d=20.67 | **YES** |
| Dense-AE Fixed_95 vs Isolation Forest | F1-Score | +0.1089 [0.0978, 0.1201] | t=27.183 | p=1.09e-05 | p=5.45e-05 | d=12.16 | **YES** |
| Full Framework vs Baseline (Adapted Saeed) | Integrated F1 | +0.0131 [0.0113, 0.0149] | t=19.888 | p=3.77e-05 | p=1.51e-04 | d=8.89 | **YES** |
| Full Framework vs Ablation (-Adaptive) | Integrated F1 | +0.0131 [0.0113, 0.0149] | t=19.888 | p=3.77e-05 | p=1.51e-04 | d=8.89 | **YES** |
| DQN vs Tabular Q-Learning | S1 Attack Containment | +10.81% [-3.90%, 25.52%] | t=2.040 | p=0.1109 | p=0.2219 | d=0.91 | No |
| Full Framework vs Ablation (-RL Defense) | Attack Containment | +1.23% [-2.28%, 4.75%] | t=0.974 | p=0.3853 | p=0.3853 | d=0.44 | No |

---

## 4. Conclusion & Reproducibility Statement

This study presented a benchmark of adaptive anomaly thresholding, un-contaminated reinforcement learning defensive response, post-quantum encryption, cryptographic integrity verification, and integrated end-to-end pipeline ablation on **CICIoT2023**. Excluded EWMA thresholding achieves strong anomaly detection (F1: 0.9014), DQN achieves 71.26% attack containment with a 0.63% false block rate, ML-KEM-768 provides sub-millisecond post-quantum security (0.2758 ms KEM), HMAC-SHA-256 and Tamper-Evident Hash Chain Logging provide verifiable event integrity at sub-millisecond overhead, and the full integrated framework achieves an end-to-end F1-Score of 0.8968 with 81.01% attack containment at 0.9626 ms per event.

All code, scripts, weights, and results are available for independent verification at:  
`https://github.com/Tanish-boop/AI-Driven-IoT-Cybersecurity-Framework-Research-`

---

## References

1. M. M. Saeed, "An AI-Driven Cybersecurity Framework for IoT: Integrating LSTM-Based Anomaly Detection, Reinforcement Learning, and Post-Quantum Encryption," *IEEE Access*, vol. 13, pp. 104027–104036, 2025.
2. J. Neto et al., "CICIoT2023: A Real-Time Dataset and Benchmark for Large-Scale Attacks in IoT Environment," *Sensors*, vol. 23, no. 13, p. 5941, 2023.
3. A. Siffer et al., "Anomaly Detection in Streams with Extreme Value Theory," *KDD*, pp. 1067–1075, 2017.
4. J. Arjunan et al., "Deep Learning Techniques for IoT Intrusion Detection," *IEEE Internet of Things Journal*, 2024.
5. National Institute of Standards and Technology, "Module-Lattice-Based Key-Encapsulation Mechanism Standard," *NIST FIPS 203*, 2024.
