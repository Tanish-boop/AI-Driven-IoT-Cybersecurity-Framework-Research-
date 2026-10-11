# Literature Review: AI-Driven IoT Cybersecurity & Post-Quantum Resilience

**Review Date**: October 9, 2026  
**Authors**: Senior Research Team  
**Scope**: Comprehensive survey of recent (2022–2026) and foundational literature in IoT anomaly detection, adaptive thresholding, defensive incident response, post-quantum key establishment, and integrity logging.

---

## 1. Deep Learning & LSTM-Based IoT Intrusion Detection

Deep learning models, particularly Long Short-Term Memory (LSTM) networks, Gated Recurrent Units (GRUs), and Autoencoders, have been widely adopted for intrusion detection in IoT networks due to their capacity to capture temporal dependencies in network flow streams.

* **Arjunan et al. (2023)** evaluated LSTM networks on IoT flow data, demonstrating superior temporal feature extraction over static feed-forward networks. However, their model relied on static thresholding and evaluated only on stationary traffic.
* **Chiranjeevi et al. (2024)** explored hybrid CNN-LSTM architectures for multi-class attack classification, reporting high accuracy on benchmark datasets. Their study assumed supervised learning with full attack labels during training, making it unsuitable for detecting novel zero-day attacks.
* **Xiang et al. (2024)** investigated autoencoder-based reconstruction models for unsupervised anomaly detection, highlighting that reconstruction error metrics effectively flag unseen anomalies without requiring labeled attack samples during training.

---

## 2. Thresholding Mechanisms: Static vs. Adaptive

Setting an anomaly detection threshold ($\tau$) is a critical challenge in real-world IoT deployments.

* **Wiessner et al. (2023)** analyzed fixed percentile thresholding (e.g., 95th or 99th percentile of reconstruction errors on benign training data). They showed that while fixed thresholds perform well under stationary traffic, they suffer from high false positive rates (FPR) when traffic rates spike or legitimate protocol shifts occur.
* **Siffer et al. (2017) & Dynamic Adaptation Studies**: Streaming Peak-Over-Threshold (SPOT) based on Extreme Value Theory (EVT) and Dynamic Exponentially Weighted Moving Average (EWMA) thresholding have been proposed to adaptively adjust $\tau$ based on rolling error distributions.
* **Research Gap in Base Paper**: Saeed (IEEE Access 2025) claimed adaptive thresholding in prose but implemented only a static fixed threshold in practice, leaving the actual empirical performance of adaptive vs. fixed thresholding under IoT traffic rate shifts unevaluated in their framework.

---

## 3. Reinforcement Learning for Defensive Incident Response

Automating security countermeasures using Reinforcement Learning (RL) allows defense agents to choose actions based on threat state feedback.

* **Ren et al. (2023) & Almehdhar et al. (2024)** formulated network defense as a Markov Decision Process (MDP), applying Q-learning and Deep Q-Networks (DQN) to select rate-limiting, IP blocking, or device isolation actions.
* **Limitations in Existing Literature**: Many studies (including Saeed 2025) use trivial $3 \times 2$ state-action lookup tables with arbitrary hardcoded rewards ($0, 10, 15$) without modeling realistic network state transitions, false alarm penalties, or legitimate service disruption costs. Furthermore, proposals for autonomous "counter-attacking" in IoT environments violate standard operational and legal defense guidelines.

---

## 4. Post-Quantum Cryptography (PQC) in Resource-Constrained IoT

With the standardization of NIST Post-Quantum Cryptography standards (FIPS 203 ML-KEM, FIPS 204 ML-DSA) in August 2024, integrating PQC into IoT security architectures has become a priority.

* **Bashminova et al. (2024) & Dhahir et al. (2024)** examined lattice-based cryptography, noting that classical RSA and ECC are vulnerable to Shor's algorithm on quantum hardware.
* **NIST FIPS 203 (ML-KEM / Kyber)**: Standardized as a Module-LWE Key Encapsulation Mechanism. ML-KEM-512, ML-KEM-768, and ML-KEM-1024 provide post-quantum key establishment.
* **AEAD Integration**: ML-KEM must be paired with an Authenticated Encryption with Associated Data (AEAD) scheme (such as AES-256-GCM or ChaCha20-Poly1305) for symmetric bulk encryption.
* **Research Gap in Base Paper**: Saeed (IEEE Access 2025) presented generic LWE equations ($y = Ax + e \bmod q$) without parameters, code, key size analysis, or latency benchmarks. Standardized ML-KEM empirical performance on IoT hardware remains to be rigorously measured within integrated frameworks.

---

## 5. Integrity Protection: Salted Hashes vs. HMAC vs. Blockchain

Data integrity logging ensures tamper-evident audit trails for security events.

* **Karemallaiah et al. (2023) & Wu et al. (2024)** evaluated cryptographic hashes for data integrity in distributed networks.
* **Base Paper Flaw**: Saeed (2025) mislabeled standard salted SHA-256 ($H = \text{SHA-256}(m \oplus s)$) as "homomorphic hashing".
* **Blockchain vs. Hash Chains**: While permissioned blockchains (e.g., Hyperledger Fabric) offer decentralized tamper-resistance, their storage growth, consensus latency, and compute overhead are prohibitive for resource-constrained IoT nodes. Keyed HMAC-SHA256 hash chains provide tamper-evident logging with minimal computational overhead.

---

## 6. Key References

1. M. M. Saeed, "An AI-Driven Cybersecurity Framework for IoT: Integrating LSTM-Based Anomaly Detection, Reinforcement Learning, and Post-Quantum Encryption," *IEEE Access*, vol. 13, pp. 104027–104036, 2025.
2. J. Neto et al., "CICIoT2023: A Real-Time Dataset and Benchmark for Large-Scale Attacks in IoT Environment," *Sensors*, vol. 23, no. 13, p. 5941, 2023.
3. M. Al-Hawawreh et al., "Edge-IIoTset: A New Comprehensive Realistic Cyber Security Dataset of IoT and IIoT Applications," *IEEE Access*, vol. 10, pp. 31658–31671, 2022.
4. NIST FIPS 203, "Module-Lattice-Based Key-Encapsulation Mechanism Standard," National Institute of Standards and Technology, Aug. 2024.
5. A. Siffer et al., "Anomaly Detection in Streams with Extreme Value Theory," *KDD*, pp. 1067–1075, 2017.
