# Master Research Plan: Fixed Experimental Scope (E1–E8)

**Target Paper Title**: Adaptive Anomaly Thresholding for IoT Intrusion Detection Under Non-Stationary Traffic Conditions: An Empirical Benchmark on CICIoT2023  
**Base Paper Under Improvement**: *M. M. Saeed, "An AI-Driven Cybersecurity Framework for IoT: Integrating LSTM-Based Anomaly Detection, Reinforcement Learning, and Post-Quantum Encryption," IEEE Access, 2025.*  
**Status**: Scope Frozen. Strictly restricted to Experiments E1 through E8.

---

## 1. Experimental Mapping Matrix (E1–E8)

| Experiment ID | Focus Area | Objective | Baseline / Comparison | Evaluation Metric | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **E1** | **Reconstructed LSTM Baseline** | Reconstruct the base paper's LSTM anomaly detector under explicit independent reimplementation disclosures. | Original reported numbers vs. Reimplemented LSTM ($L=1$). | Precision, Recall, F1, FPR, Loss | **Completed** |
| **E2** | **Fixed vs. Adaptive Thresholds** | Compare static percentile thresholds against online EWMA threshold adaptation rules under stream processing. | Fixed 95th, Fixed 99th vs. UnGuarded, Excluded, and Guarded EWMA. | Precision, Recall, F1, FPR, PR-AUC, ROC-AUC | **Completed** |
| **E3** | **Detector Architecture Comparison** | Compare unsupervised reconstruction models against non-temporal baselines and a supervised reference. | Dense-AE vs. Isolation Forest vs. XGBoost Supervised Oracle. | Precision, Recall, F1, FPR, PR-AUC, ROC-AUC, Latency | **Completed** |
| **E4** | **Defensive-Response Policies** | Compare reactive mitigation policies under simulated network attack streams and operational constraints. | Static Rule-Based vs. Q-Learning vs. Deep Q-Network (DQN). | Mitigation Success, False Isolation Rate, Cumulative Reward, Cost | **Planned Next** |
| **E5** | **Post-Quantum Cryptography** | Measure standardized NIST PQC key encapsulation overhead for secure IoT key establishment. | ML-KEM-512 vs. ML-KEM-768 vs. ML-KEM-1024 (paired with AES-256-GCM). | KeyGen/Encap/Decap Latency, Key/Ciphertext Size, Memory | **Planned Next** |
| **E6** | **Integrity & Authentication** | Compare message authentication and tamper-evident audit logging for telemetry verification. | Salted SHA-256 vs. HMAC-SHA-256 vs. Blockchain Audit Log. | Verification Latency, Storage Overhead, Tamper Detection Rate | **Planned Next** |
| **E7** | **Integrated Framework & Ablation** | Benchmark the end-to-end framework with validated component upgrades against the base architecture. | Full Baseline Framework vs. Ablated Framework (No Adaptive Threshold / No PQC). | System Throughput, End-to-End Latency, Overall F1, Cost | **Pending E4-E6** |
| **E8** | **Non-Stationary Traffic & Robustness** | Evaluate model resilience under input feature-level rate perturbations and unseen attack categories. | Baseline Traffic vs. $1.5\times$ and $2.0\times$ Input Rate-Scaled Telemetry. | False Positive Rate Explosion (FPR Increase %), Recall Delta | **Completed** |

---

## 2. Detailed Experiment Protocols

### E1: Reconstructed LSTM Baseline
- **Research Question**: Can the base paper's LSTM anomaly detection performance be independently reproduced on sample-level IoT flow features without temporal sequence window boundary contamination?
- **Protocol**: Train single-sample ($L=1$) LSTM and Dense Autoencoders on pure benign training telemetry (`X_train`). Evaluate on `X_test`.

### E2: Fixed versus Adaptive Anomaly Thresholds
- **Research Question**: Does adaptive thresholding prevent false-alarm spikes under non-stationary traffic without causing threshold inflation during continuous attack floods?
- **Protocol**: Tune initial $\mu, \sigma$ on `X_val`. Evaluate 4 adaptation rules (`Fixed_95`, `Fixed_99`, `UnGuarded_EWMA`, `Excluded_EWMA`, `Guarded_EWMA`) on streaming test errors.

### E3: LSTM versus Alternative Detectors
- **Research Question**: How does an unsupervised Dense Autoencoder compare against tree-based anomaly detectors (Isolation Forest) and a fully supervised reference (XGBoost)?
- **Protocol**: Benchmark on identical leak-free test partitions (`X_test`). Report PR-AUC and ROC-AUC alongside F1 to account for attack prevalence.

### E4: Defensive-Response Policies
- **Research Question**: Does reinforcement learning (Q-Learning / DQN) provide superior cost-weighted mitigation compared to static rule-based policies?
- **Protocol**: Simulate an IoT gateway environment with 4 actions (Allow, Alert, Rate-Limit, Block) and cost penalties for false isolations.

### E5: Post-Quantum Cryptography (ML-KEM)
- **Research Question**: What is the computational and latency overhead of NIST-standardized ML-KEM key exchange on IoT edge devices?
- **Protocol**: Implement ML-KEM-512, ML-KEM-768, ML-KEM-1024 using standardized PyCryptodome / OQS primitives; measure microbenchmarks (CPU time, memory, throughput).

### E6: Integrity and Authentication
- **Research Question**: What is the performance trade-off between HMAC-SHA-256 packet authentication and blockchain tamper-evident audit logging?
- **Protocol**: Measure per-packet HMAC generation/verification latency vs. block commitment latency and payload size overhead.

### E7: Integrated Framework and Ablation
- **Research Question**: What is the net performance gain of combining Excluded EWMA thresholding, ML-KEM key exchange, and DQN mitigation?
- **Protocol**: Run controlled ablation experiments dropping one component at a time from the full framework.

### E8: Changing Traffic and Unseen Attacks
- **Research Question**: How severely do static thresholds degrade when benign packet rates increase by $1.5\times$ and $2.0\times$?
- **Protocol**: Apply feature-level scaling to raw rate attributes (`Rate`, `Srate`, `Drate`, `Tot size`) prior to standard scaling and measure FPR increase.

---

## 3. Scope Protection Guarantee
No additional datasets, model families, or unvetted cryptographic algorithms will be added beyond the 8 predefined experiments.
