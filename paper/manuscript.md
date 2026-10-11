# Adaptive Anomaly Thresholding, Un-Contaminated Reinforcement Learning Defense, and Standardized Post-Quantum Encryption for IoT Cybersecurity

**Authors**: Anonymous Authors (Under Academic Peer Review)  
**Target Venue**: *IEEE Access* / *Sensors*  
**Artifact Repository**: https://github.com/Tanish-boop/AI-Driven-IoT-Cybersecurity-Framework-Research-  

---

## Abstract
In Internet of Things (IoT) cybersecurity, deep reconstruction-based anomaly detection models (such as Dense Autoencoders) offer promising capabilities for flagging zero-day network intrusions without requiring labeled attack samples during training. However, translating reconstruction error scores into operational binary decisions relies heavily on thresholding mechanisms ($\tau$). While static percentile thresholds ($\tau_{95}, \tau_{99}$) set during offline training are standard in literature, they are highly sensitive to non-stationary network traffic shifts and benign telemetry rate surges, leading to false-alarm explosions. Conversely, un-guarded adaptive thresholding mechanisms (such as standard Exponentially Weighted Moving Average - EWMA) dynamically update background error statistics on incoming telemetry, making them vulnerable to severe **threshold inflation** during sustained attack floods.

This paper presents an empirically rigorous, leakage-resistant benchmark evaluating four explicit threshold adaptation strategies (**Fixed 95th Percentile**, **Fixed 99th Percentile**, **Un-Guarded EWMA**, **Excluded EWMA**, and **Guarded Winsorized EWMA**) across unsupervised anomaly detection models (Dense Autoencoder and Isolation Forest) alongside a supervised XGBoost oracle reference over 5 random seeds ($42, 123, 456, 789, 2026$). Furthermore, we evaluate three defensive-response mitigation policies (**Static Rule-Based**, **Tabular Q-Learning**, and **Deep Q-Network - DQN**) trained strictly on supervised training partitions (`X_sup`) and evaluated on held-out test data (`X_test`), and microbenchmark standardized NIST FIPS 203 Post-Quantum Cryptography (**ML-KEM-512**, **ML-KEM-768**, and **ML-KEM-1024**) paired with HKDF-SHA256 and AES-256-GCM AEAD alongside a tamper-evident append-only hash-chain audit log.

Our empirical results demonstrate that while Dense Autoencoders with a Fixed 95th Percentile threshold achieve a baseline F1-Score of **0.8854 ± 0.0013** (Precision: $0.9893 \pm 0.0003$, Recall: $0.8013 \pm 0.0022$, FPR: $0.0493 \pm 0.0013$), synthetic benign rate feature scaling causes a **+454.4% explosion in false positive rates** under $2.0\times$ scaling (jumping from 4.93% to 27.33%). On the base test stream, Excluded EWMA adaptation achieves the highest unsupervised F1-Score of **0.9014 ± 0.0018** (Recall: $0.8401 \pm 0.0023$, FPR: $0.1360 \pm 0.0110$), coming within 2.55% of the Supervised XGBoost Oracle (F1: $0.9269 \pm 0.0004$). For defensive mitigation under held-out evaluation, **DQN** achieves **71.20% attack containment** with a **0.77% false block rate** (latency: 0.4412 ms), while **Tabular Q-Learning** achieves a **0.00% false block rate** in isolated testing with ultra-low decision latency (**0.0757 ms**). For post-quantum encryption, **ML-KEM-768** achieves sub-millisecond key establishment (**0.4293 ms**) and **100% tamper rejection**. In full integrated pipeline evaluation, the proposed framework achieves an end-to-end F1-Score of **0.8968 ± 0.0013** and **80.65% ± 3.16%** attack containment at **0.3781 ms** per event. We provide open-source code, deterministic data splitting protocols, and statistical verification scripts to ensure independent reproducibility.

---

## 1. Introduction

The proliferation of Internet of Things (IoT) devices in critical infrastructure, smart healthcare, industrial automation, and consumer environments has drastically expanded the cyber-attack surface. Traditional rule-based Intrusion Detection Systems (IDS) rely on signature databases that fail against novel zero-day attacks and stealthy multi-vector traffic anomalies.

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

### 2.2 Leak-Free Split Protocol
- **Unsupervised Benign Train Split (`X_train`)**: 100,000 Benign flow records.
- **Unsupervised Benign Validation Split (`X_val`)**: 30,000 Benign flow records.
- **Supervised Policy Split (`X_sup`)**: 40,000 50/50 Benign+Attack records (used for RL training).
- **Held-Out Test Split (`X_test`)**: 100,000 flow records (14,911 Benign, 85,089 Attack) strictly reserved for held-out evaluation.

### 2.3 Deployment Hardware Scope & Environmental Boundaries
All benchmarks reported in this study were executed on an AMD64 host architecture (Windows 11 x86_64, 3.40 GHz). No physical measurements were performed on ARM64 or Raspberry Pi hardware; embedded edge gateway and microcontroller porting represent modeled targets for future hardware-in-the-loop validation. Deeply embedded microcontrollers (such as 8-bit AVR or 32-bit ARM Cortex-M0/M4 devices running under 100 MHz clock frequencies) possess stringent cycle and memory constraints; executing neural network inferences and lattice-based ML-KEM-768 on such microcontrollers would require dedicated integer-only quantization (e.g., TFLite Micro) and optimized assembly implementations, which represents a separate research trajectory.

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

*Methodological & Integrity Disclosures*:
1. *Feature Vectors vs. Physical Events*: Identical numerical feature vectors reflect identical network packet header fields (such as uniform packet length and TCP flag states during high-rate SYN flood bursts or periodic keepalives). They represent repeated traffic patterns rather than guaranteed identical physical network events.
2. *Independence Boundaries*: Because original packet capture IDs and session timestamps are unavailable in the pre-shuffled public CICIoT2023 distribution, complete capture-level or device-level independence cannot be established from flow features alone.
3. *Scope of Sensitivity Check*: While this sensitivity analysis demonstrates that repeated feature vectors do not materially inflate evaluation metrics, it does not prove broad zero-day generalization to novel physical hardware testbeds. Evaluation across independent physical testbeds remains necessary for cross-environment validation.

---

### 3.3 Synthetic Feature Rate Stress Test Results (E8)

Table 3 evaluates the sensitivity of the static 95th percentile threshold under synthetic rate feature value scaling:

| Model | Strategy | Precision | Recall | F1-Score | False Positive Rate (FPR) | FPR Increase |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dense-AE** | **Fixed 95th Base (1.0x)** | $0.9893 \pm 0.0003$ | $0.8013 \pm 0.0022$ | $0.8854 \pm 0.0013$ | $0.0493 \pm 0.0013$ | Baseline |
| Dense-AE | Fixed 95th Stress (1.5x) | $0.9796 \pm 0.0019$ | $0.8013 \pm 0.0022$ | $0.8815 \pm 0.0017$ | $0.0953 \pm 0.0092$ | +93.3% |
| **Dense-AE** | **Fixed 95th Stress (2.0x)** | $0.9436 \pm 0.0030$ | $0.8013 \pm 0.0022$ | $0.8666 \pm 0.0021$ | **$0.2733 \pm 0.0152$** | **+454.4%** |

*Operational Scope & Methodological Disclosure*: In Experiment E8, synthetic feature scaling was applied strictly to rate-related numerical feature columns (`Rate`, `Tot size`, `Variance`) of benign test samples to evaluate threshold sensitivity to sudden telemetry bursts. This represents an analytical simulation of feature value inflation rather than a physical live network packet arrival rate increase or hardware replay. Furthermore, Excluded EWMA was evaluated on the base test stream in Experiment E2 and was not re-evaluated under synthetic feature scaling in E8; claims of threshold shift stability are strictly confined to the dynamic stream conditions tested in E2.

---

### 3.4 Un-Contaminated Defensive-Response Policy Evaluation (E4 Rerun)

Table 4 presents the empirical performance of static Rule-Based, Tabular Q-Learning, and Deep Q-Network (DQN) mitigation policies across 5 random seeds under strict un-contaminated data split isolation (policies trained strictly on `X_sup` and evaluated on held-out `X_test`):

| Evaluation Scenario | Mitigation Policy | Cumulative Reward | Attack Containment (%) | False Block Rate (%) | Disruption Penalty | Decision Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Scenario 1 (Heavy)** | Static Rule-Based | $35,402.00 \pm 0.00$ | $99.98\% \pm 0.00\%$ | $100.00\% \pm 0.00\%$ | $7,290.00 \pm 0.00$ | $0.0413 \pm 0.0233$ |
| Scenario 1 (Heavy) | **Tabular Q-Learning** | $17,692.00 \pm 3,324.37$ | $55.94\% \pm 7.26\%$ | **$0.00\% \pm 0.00\%$** | **$12.60 \pm 28.17$** | **$0.0757 \pm 0.0146$** |
| Scenario 1 (Heavy) | **DQN** | $27,092.00 \pm 3,289.35$ | **$71.20\% \pm 0.05\%$** | **$0.77\% \pm 0.43\%$** | **$60.20 \pm 21.91$** | $0.4412 \pm 0.1315$ |
| **Scenario 2 (Stealth)**| Static Rule-Based | $35,762.00 \pm 0.00$ | $99.98\% \pm 0.00\%$ | $100.00\% \pm 0.00\%$ | $7,110.00 \pm 0.00$ | $0.0398 \pm 0.0221$ |
| Scenario 2 (Stealth)| **Tabular Q-Learning** | $17,446.80 \pm 3,648.61$ | $56.21\% \pm 7.81\%$ | **$0.00\% \pm 0.00\%$** | **$18.00 \pm 40.25$** | **$0.0718 \pm 0.0036$** |
| Scenario 2 (Stealth)| **DQN** | $28,219.60 \pm 3,109.63$ | **$73.01\% \pm 0.05\%$** | **$0.53\% \pm 0.32\%$** | **$44.60 \pm 15.96$** | $0.3071 \pm 0.1332$ |

*Contextual Note on False Block Rate*: In isolated environment evaluation (Table 4), Tabular Q-Learning achieves a $0.00\% \pm 0.00\%$ False Block Rate because benign evaluation flows present low reconstruction errors, and the consecutive alert counter tracks environment attack transitions cleanly without upstream false alarms. In Section 3.6 (Table 7), we examine how this policy performs when integrated downstream of an actual statistical detector (Excluded EWMA Autoencoder), where upstream detector false alarms elevate the alert streak and induce an empirical $7.39\%$ false block rate.

---

### 3.5 Post-Quantum Cryptography Microbenchmark (E5)

Table 5 presents the key establishment latency, artifact memory footprints, and AEAD encryption times for NIST FIPS 203 ML-KEM parameter sets paired with HKDF-SHA256 and AES-256-GCM across 100 repeated trials on AMD64 host CPU:

| ML-KEM Variant | Public Key (B) | Secret Key (B) | Ciphertext (B) | KeyGen (ms) | Encaps (ms) | Decaps (ms) | Total KEM (ms) | First-Msg Setup (ms) | Repeated-Msg (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ML-KEM-512** | 800 | 1,632 | 768 | 0.0469 | 0.0560 | 0.0774 | 0.1802 | 0.1972 | 0.0168 |
| **ML-KEM-768** | 1,184 | 2,400 | 1,088 | 0.1114 | 0.1353 | 0.1826 | **0.4293** | **0.4754** | **0.0456** |
| **ML-KEM-1024** | 1,568 | 3,168 | 1,568 | 0.1294 | 0.1485 | 0.1815 | 0.4594 | 0.4963 | 0.0365 |

All variants achieved 100% tamper rejection when tested against bit-flip modifications of ciphertext or header data (raising `cryptography.exceptions.InvalidTag`).

---

### 3.6 Integrity Verification Architecture Benchmark (E6)

Table 6 evaluates three candidate integrity verification mechanisms across 100 trials with 1 KiB evidence records:

| Integrity Mechanism | Creation Latency (ms) | Verification Latency (ms) | End-to-End Latency w/ Disk (ms) | Storage Overhead (Bytes) | Throughput (MB/s) | Core Security Guarantee |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Salted SHA-256** | $0.0279 \pm 0.0112$ | $0.0133 \pm 0.0035$ | $0.3374$ | 193 B | 34.94 MB/s | Accidental error detection (Unkeyed) |
| **HMAC-SHA-256** | $0.0332 \pm 0.0128$ | $0.0158 \pm 0.0048$ | $0.3553$ | **171 B** | 29.45 MB/s | Authenticity & anti-forgery (Keyed) |
| **Tamper-Evident Hash Chain Log** | $0.0409 \pm 0.0186$ | $0.0198 \pm 0.0060$ | $0.4031$ | 317 B | 23.88 MB/s | Append-only sequence & tamper localization |

While Salted SHA-256 has the lowest creation latency ($0.0279$ ms), it cannot prevent forgery by adversaries with storage write access. HMAC-SHA-256 provides authentic message integrity against unauthorized forgery at minimal overhead ($171$ B, $0.0332$ ms). For forensic auditability, the Tamper-Evident Hash Chain Log strictly enforces sequence integrity and localizes tampered blocks with $\mathcal{O}(1)$ append latency ($0.0409$ ms) and $\mathcal{O}(N)$ full chain verification ($29.85$ ms for 2,000 blocks).

*Trust Boundary Disclosure*: The local append-only hash chain guarantees sequence integrity against unprivileged processes ($\mathcal{A}_{\text{proc}}$), but cannot prevent a privileged local storage adversary ($\mathcal{A}_{\text{root}}$) from rewriting the entire local chain. External root tip anchoring is required to resist full local rewrite.

---

### 3.7 Integrated Framework Ablation Study (E7)

Table 7 evaluates the holistic empirical performance of the full end-to-end framework alongside its five component-level ablation variants across 5 random seeds ($42, 123, 456, 789, 2026$):

*Attribution Note*: The "Study-Defined Baseline (Adapted from Saeed 2025)" row represents our empirical benchmark implementation adapting the general concepts proposed by Saeed (2025) (fixed percentile threshold + static rule escalation + salted SHA-256) using a sample-level Dense Autoencoder on CICIoT2023 under identical test conditions, as Saeed (2025) used an LSTM Autoencoder with a 30s lookback on a private unreleased dataset and reported zero global test stream F1/Recall metrics. We do not claim this was Saeed's published score or that the original LSTM was exactly reproduced.

| Variant | F1-Score | Recall (%) | Containment (%) | False Block (%) | Availability (%) | Latency (ms) | Throughput (ev/s) | Overhead (B) | Quantum Safe | Audit Immutability |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Study-Defined Baseline (Adapted from Saeed 2025)** | $0.8837 \pm 0.0004$ | $79.88\% \pm 0.06\%$ | $79.88\% \pm 0.06\%$ | $3.20\% \pm 0.07\%$ | $96.80\% \pm 0.07\%$ | $0.3319 \pm 0.0440$ | $3050.9 \pm 356.1$ | 194 B | No (Vulnerable) | No (Unkeyed Hash) |
| **Ablation (-Adaptive Threshold)** | $0.8837 \pm 0.0004$ | $79.88\% \pm 0.06\%$ | $81.67\% \pm 2.51\%$ | $8.24\% \pm 3.44\%$ | $91.76\% \pm 3.44\%$ | $0.3815 \pm 0.0415$ | $2644.8 \pm 272.9$ | 321 B | Yes (NIST ML-KEM) | Yes (Hash Chain) |
| **Ablation (-RL Defense)** | $0.8968 \pm 0.0013$ | $82.68\% \pm 0.24\%$ | $79.78\% \pm 0.06\%$ | $3.22\% \pm 0.06\%$ | $96.78\% \pm 0.06\%$ | $0.4791 \pm 0.3193$ | $2576.8 \pm 926.7$ | 321 B | Yes (NIST ML-KEM) | Yes (Hash Chain) |
| **Ablation (-PQC)** | $0.8968 \pm 0.0013$ | $82.68\% \pm 0.24\%$ | $80.65\% \pm 3.16\%$ | $7.39\% \pm 2.51\%$ | $92.61\% \pm 2.51\%$ | $0.4484 \pm 0.2165$ | $2522.0 \pm 763.1$ | 321 B | No (Vulnerable) | Yes (Hash Chain) |
| **Ablation (-Hash Chain Log)** | $0.8968 \pm 0.0013$ | $82.68\% \pm 0.24\%$ | $80.65\% \pm 3.16\%$ | $7.39\% \pm 2.51\%$ | $92.61\% \pm 2.51\%$ | $0.5523 \pm 0.4207$ | $2353.8 \pm 895.4$ | 194 B | Yes (NIST ML-KEM) | No (Unkeyed Hash) |
| **Full Proposed Framework** | $\mathbf{0.8968 \pm 0.0013}$ | $\mathbf{82.68\% \pm 0.24\%}$ | $\mathbf{80.65\% \pm 3.16\%}$ | $7.39\% \pm 2.51\%$ | $92.61\% \pm 2.51\%$ | $\mathbf{0.3781 \pm 0.0225}$ | $\mathbf{2652.4 \pm 154.8}$ | 321 B | **Yes (NIST ML-KEM)** | **Yes (Hash Chain)** |

#### Multi-Dimensional Ablation Orthogonality
A critical structural finding in Table 7 is the exact invariance of detection F1-score ($0.8968 \pm 0.0013$) when removing Post-Quantum Cryptography (`Ablation -PQC`) or the Hash Chain Log (`Ablation -Hash Chain Log`). This invariance is mathematically expected due to the pipelined modular architecture: the Autoencoder anomaly detector executes first on network flow features to generate reconstruction errors and binary decisions. Post-quantum AEAD encryption and hash-chain logging execute downstream to secure payload transit and preserve forensic event records. Because downstream cryptographic operations do not feed back into input feature transformations or detector threshold adaptation, ablating cryptographic modules alters payload security and auditability without affecting detection metrics.

#### Reconciliation of False Block Rates (E4 Standalone vs. E7 Integrated)
The difference between the false block rate in standalone policy testing (Table 4: $0.00\%$ for Tabular Q-Learning) and integrated streaming (Table 7: $7.39\%$) highlights the reality of detector noise propagation. In isolated environment testing (E4), the RL agent operates on clean test streams where alert streak transitions directly correspond to simulated attack phases. In the integrated pipeline (E7), the Q-policy operates directly downstream of the Excluded EWMA Autoencoder detector. Because Excluded EWMA exhibits an empirical $13.6\%$ false positive rate on bursty benign traffic, occasional false alarms increment the consecutive alert streak counter. When benign flows follow closely after false alerts with elevated flow rates, the Q-learning policy escalates to rate-limiting and blocking ($7.39\%$ false block rate). This realistic propagation emphasizes why end-to-end integration benchmarks are essential.

#### Extended Hypothesis Testing & Statistical Significance
To ensure that all observed advantages are statistically robust, Table 8 details paired $t$-tests, exact 95% confidence intervals, Holm-Bonferroni corrected $p$-values, and Cohen's $d$ effect sizes across 5 random seeds:

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

This study presented a leak-free empirical evaluation of adaptive anomaly thresholding, un-contaminated reinforcement learning defensive response, post-quantum encryption, cryptographic integrity verification, and integrated end-to-end pipeline ablation on **CICIoT2023**. Excluded EWMA thresholding achieves strong anomaly detection (F1: 0.9014), DQN achieves 71.20% attack containment with a 0.77% false block rate, ML-KEM-768 provides sub-millisecond post-quantum security (0.4293 ms setup), HMAC-SHA-256 and Tamper-Evident Hash Chain Logging provide verifiable event integrity at sub-millisecond overhead, and the full integrated framework achieves an end-to-end F1-Score of 0.8968 with 80.65% attack containment at 0.3781 ms per event.

All code, scripts, weights, and results are available for independent verification at:  
`https://github.com/Tanish-boop/AI-Driven-IoT-Cybersecurity-Framework-Research-`

---

## References

1. M. M. Saeed, "An AI-Driven Cybersecurity Framework for IoT: Integrating LSTM-Based Anomaly Detection, Reinforcement Learning, and Post-Quantum Encryption," *IEEE Access*, vol. 13, pp. 104027–104036, 2025.
2. J. Neto et al., "CICIoT2023: A Real-Time Dataset and Benchmark for Large-Scale Attacks in IoT Environment," *Sensors*, vol. 23, no. 13, p. 5941, 2023.
3. A. Siffer et al., "Anomaly Detection in Streams with Extreme Value Theory," *KDD*, pp. 1067–1075, 2017.
4. J. Arjunan et al., "Deep Learning Techniques for IoT Intrusion Detection," *IEEE Internet of Things Journal*, 2024.
5. National Institute of Standards and Technology, "Module-Lattice-Based Key-Encapsulation Mechanism Standard," *NIST FIPS 203*, 2024.
