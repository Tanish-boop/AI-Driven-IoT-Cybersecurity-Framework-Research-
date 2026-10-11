# Research Gap and Novelty Analysis

**Date**: October 9, 2026  
**Authors**: Senior Research Team  
**Scope**: Literature-based identification and rigorous analysis of defensible research gaps for an experimentally validated IoT cybersecurity study.

---

## Executive Summary

Following a comprehensive audit of the base paper (Saeed, *IEEE Access* 2025) and survey of 2022–2026 literature, we reject the notion that simply "combining LSTM, RL, salted hashes, and LWE" constitutes a novel research contribution. Instead, we identify **three specific, testable, and defensible research gaps** grounded in empirical limitations of existing literature.

---

## Research Gap 1: Detection Reliability Under Traffic Rate Shifts (Adaptive vs. Fixed Thresholding)

### 1. Evidence that the Problem Exists
Current IoT anomaly detection models (including Saeed 2025 and Arjunan et al. 2023) set anomaly decision thresholds ($\tau$) using static percentiles (e.g. 95th or 99th percentile of reconstruction errors on benign training data). In real IoT networks, legitimate traffic rate changes, bursty device telemetry, and non-stationary load cause reconstruction errors to drift, resulting in unacceptable False Positive Rates (FPR > 15-25%) or missed low-and-slow zero-day attacks. While Saeed (2025) claimed adaptive thresholding in prose, their implementation actually used a static fixed threshold.

### 2. Closely Related Work
* Siffer et al. (KDD 2017) - SPOT (Streaming Peak-Over-Threshold based on Extreme Value Theory).
* Wiessner et al. (2023) - Static vs. dynamic thresholding in time-series anomaly detection.
* Saeed (IEEE Access 2025) - Claimed adaptive thresholding, but evaluated only fixed 95th percentile.

### 3. What Previous Studies Accomplished
Established that unsupervised deep reconstruction models (LSTM, Autoencoders) can detect traffic anomalies without attack labels, and proved theoretically that streaming threshold updates reduce false alarms.

### 4. What Remains Insufficiently Evaluated
No study has systematically evaluated **Dynamic EWMA vs. Rolling Quantile vs. SPOT EVT thresholding** on standard modern IoT traffic datasets (CICIoT2023) under controlled, non-stationary traffic rate shifts and multi-vector attacks, measuring both detection latency and false alarm rate decay over time.

### 5. Why the Gap Matters
Static thresholds cause alert fatigue in security operations centers (SOCs) or result in catastrophic false alarms during legitimate IoT network traffic surges.

### 6. Testable Research Question
> *Does statistical adaptive thresholding (Dynamic EWMA / Rolling Quantile) significantly reduce false alarm rates while maintaining high detection recall ($\ge 95\%$) compared to fixed percentile thresholding when LSTM/Autoencoder detection models are deployed under non-stationary IoT traffic rate shifts?*

### 7. Feasible Experimental Design
* **Dataset**: CICIoT2023 flow records.
* **Baselines**: Fixed 95th percentile, Fixed 99th percentile thresholding.
* **Proposed Adaptations**: Dynamic EWMA thresholding, Rolling 1000-window Quantile thresholding, SPOT EVT thresholding.
* **Test Conditions**: Introduce controlled legitimate rate scaling (1.5x to 4x traffic burst) vs. genuine attack flows (DDoS, Recon, Spoofing).
* **Metrics**: F1-score, False Positive Rate (FPR), Detection Latency, Threshold Stability index.

### 8. Required Evidence to Support Claim
Empirical proof showing a statistically significant reduction in FPR ($p < 0.05$ via Wilcoxon signed-rank test) without sacrificing recall under rate-shifted test streams.

### 9. Potential Risks / Reasons Gap Might Not Be Novel
Adaptive thresholding algorithms exist in generic time-series literature. Novelty comes from rigorous empirical evaluation in an end-to-end IoT cybersecurity framework with reproducible benchmarks.

---

## Research Gap 2: Empirical Cost-Benefit Evaluation of Standardized NIST ML-KEM PQC on IoT Edge Gateways

### 1. Evidence that the Problem Exists
Existing framework papers (such as Saeed 2025) cite generic Learning With Errors (LWE) equations ($y = Ax + e \bmod q$) as a theoretical post-quantum shield. However, they report zero concrete benchmarks regarding key encapsulation latency, ciphertext expansion, or CPU/memory overhead. Furthermore, NIST finalized FIPS 203 (ML-KEM) in August 2024, but empirical studies integrating ML-KEM with AEAD (AES-256-GCM / ChaCha20-Poly1305) in resource-constrained IoT gateway pipelines are scarce.

### 2. Closely Related Work
* NIST FIPS 203 (Aug 2024) - Module-Lattice-Based Key-Encapsulation Mechanism.
* Bashminova et al. (2024) - Microbenchmarks of Ring-LWE on cloud servers.
* Saeed (IEEE Access 2025) - High-level prose on LWE without parameters or empirical metrics.

### 3. What Previous Studies Accomplished
Proved cryptographic security bounds of Module-LWE and provided microbenchmarks of isolated ML-KEM primitives on x86/ARM hardware.

### 4. What Remains Insufficiently Evaluated
Quantifying the exact **end-to-end latency, memory footprint, and message payload expansion** of replacing classical key exchange (ECDH P-256) with standardized NIST ML-KEM-512 / 768 / 1024 paired with AEAD symmetric encryption in an active IoT packet processing pipeline.

### 5. Why the Gap Matters
IoT developers need concrete empirical data to decide whether ML-KEM-512 or ML-KEM-768 is computationally viable for edge gateways without bottlenecking real-time packet inspection.

### 6. Testable Research Question
> *What is the exact computational overhead (handshake latency, memory footprint, packet expansion, and encryption throughput) of deploying standardized NIST ML-KEM (FIPS 203) key encapsulation with AEAD symmetric encryption on IoT edge gateway hardware compared to classical ECDH/AES baselines?*

### 7. Feasible Experimental Design
* **Cryptographic Schemes**: Classical Baseline (ECDH P-256 + AES-128-GCM), ML-KEM-512 + AES-256-GCM, ML-KEM-768 + AES-256-GCM, ML-KEM-1024 + ChaCha20-Poly1305.
* **Measurements**: 1,000 repeated trial handshakes per parameter set.
* **Metrics**: KeyGen time (ms), Encapsulation time (ms), Decapsulation time (ms), Public Key size (bytes), Ciphertext size (bytes), Peak RAM usage (MB), Throughput (MB/s).

### 8. Required Evidence to Support Claim
Rigorous distributions (mean, std dev, 95th percentile latency) proving the operational feasibility and exact cost of ML-KEM on IoT gateway nodes.

---

## Research Gap 3: Realistic Cost-Sensitive Defensive Response Simulation vs. Static Lookup Tables

### 1. Evidence that the Problem Exists
Literature often presents RL response agents using trivial $3 \times 2$ static lookup tables with arbitrary rewards or ungrounded "counter-attack" actions (Saeed 2025). There is a lack of reproducible, cost-sensitive MDP simulation environments that evaluate defensive actions (rate-limiting, quarantine, connection drop) against realistic false positive costs and service availability trade-offs.

### 2. Closely Related Work
* Ren et al. (2023) - Cost-sensitive RL for network defense.
* Saeed (IEEE Access 2025) - Trivial 3-state Q-table with static reward preferences.

### 3. What Previous Studies Accomplished
Demonstrated that RL can learn defensive policies in simulated discrete environments.

### 4. What Remains Insufficiently Evaluated
Evaluating whether a learned Tabular Q-learning / DQN policy outperforms a deterministic risk-based rule policy when defensive actions incur explicit operational penalties (e.g., blocking legitimate IoT telemetry vs. containing genuine attacks).

### 5. Why the Gap Matters
In operational IoT networks, blocking benign traffic halts critical sensors. A defense agent must balance security risk against service availability.

---

## Recommended Primary Research Direction

We recommend focusing the paper on **Research Gap 1 and Research Gap 2**, titled provisionally:

> **"Resource-Aware IoT Cybersecurity Under Distribution Shift: An Empirical Evaluation of Adaptive Anomaly Detection, Defensive Response, and Post-Quantum Key Establishment"**

This combines:
1. Benchmark of unsupervised anomaly detectors (LSTM, Autoencoder, XGBoost, GRU) on **CICIoT2023**.
2. Controlled evaluation of **Dynamic EWMA Adaptive Thresholding** vs. Fixed Thresholding under non-stationary traffic shifts.
3. Micro-benchmarking of standardized **NIST ML-KEM (FIPS 203)** key encapsulation + AEAD symmetric encryption.
4. Lightweight **HMAC-SHA256 tamper-evident audit logging**.
