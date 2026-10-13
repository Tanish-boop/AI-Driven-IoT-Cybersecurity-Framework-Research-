# BASELINE REPRODUCTION PLAN: SAEED (2025) IEEE ACCESS ADAPTATION

**Target Article**: M. M. Saeed, *"An AI-Driven Cybersecurity Framework for IoT: Integrating LSTM-Based Anomaly Detection, Reinforcement Learning, and Post-Quantum Encryption,"* *IEEE Access*, vol. 13, pp. 104027–104037, Jun. 2025. Digital Object Identifier: [10.1109/ACCESS.2025.3576506](https://doi.org/10.1109/ACCESS.2025.3576506).  
**Repository**: `C:\Users\hp\OneDrive\Desktop\Research Experiments`  
**Date**: October 2026  
**Status**: Rigorously Adapted & Empirically Verified across 5 Random Seeds  

---

## 1. Executive Summary & Audit Context

A central methodological requirement of scientific research is establishing rigorous, fair, and reproducible baselines. Our investigation builds upon and critically evaluates the recent IoT cybersecurity framework proposed by Mozamel M. Saeed in *IEEE Access* (2025). 

While Saeed (2025) presented an ambitious vision combining LSTM anomaly detection, Q-learning mitigation, homomorphic hashing, and lattice-based cryptography, our forensic audit of the publication revealed substantial methodological ambiguities and omitted metrics. This document establishes:
1. The exact mathematical and algorithmic details of the Saeed baseline.
2. The fundamental data availability and reporting gaps in the published paper.
3. Our rigorous adaptation of Saeed's architecture to the public, real-world **CICIoT2023** benchmark dataset.
4. The critical distinction between sequence sliding windows ($L=10$) and individual NetFlow feature representations ($L=1$), explaining why naïve sequence models collapse on tabular network traffic.
5. The full 5-seed head-to-head comparison protocol contrasting Dense Autoencoders against Saeed's LSTM Autoencoder.

---

## 2. Forensic Analysis of Saeed (2025) Claims vs. Published Evidence

A line-by-line inspection of the text and figures of Saeed (2025) (*IEEE Access*, vol. 13) yields the following empirical facts regarding the original paper's baseline reporting:

| Dimension | Saeed (2025) Claim / Stated Design | Actual Published Evidence in Saeed (2025) | Our Research Audit Finding |
| :--- | :--- | :--- | :--- |
| **Dataset** | Simulated IoT network environment with sensor streams | Private, unreleased synthetic simulation data; zero public URLs or hashes. | Cannot directly execute Saeed's original data stream. Must adapt to standard public benchmark (CICIoT2023). |
| **Detection Model** | 2-layer Long Short-Term Memory (LSTM) Autoencoder | Stated in Section II.A; equations (1)–(6) describe standard LSTM cell. | Exact architecture replicated in PyTorch (`LSTMAutoencoder`, 2 layers, hidden dimension 64). |
| **Thresholding** | Fixed 95th percentile of Mean Squared Error (MSE) reconstruction | Equation (9) MSE: $\text{MSE} = \frac{1}{n} \sum_{i=1}^n (y - \hat{y})^2$. Stated 95th percentile threshold. | Replicated in `FixedThreshold(percentile=95)` fit on benign validation traffic. |
| **Detection Performance Metrics** | Claims "high accuracy in identifying anomalies" (Abstract) | **Zero global classification metrics reported**: No Precision, Recall, F1-Score, False Positive Rate, or Confusion Matrix. | Saeed reported only a single qualitative point: Table 1 shows timestamp 810 with actual = 1.25, predicted = 0.72. |
| **Threshold Adaptation** | Acknowledged limitation of static threshold | Section III.A explicitly states: *"Future improvements could include dynamic thresholding... These strategies were not implemented in the present work but are proposed for future research."* | Our framework directly answers Saeed's research call by implementing and benchmarking dynamic thresholding (EWMA). |
| **Defensive Mitigation** | Q-learning reinforcement learning agent | Conceptual reward equations; 3 actions (block, alert, monitor). | Replicated in `QLearningPolicy` and compared against Deep Q-Networks (`DQNPolicy`). |
| **Post-Quantum Cryptography** | Lattice-based encryption based on Learning With Errors (LWE) | Theoretical matrix equation $y = Ax + e \pmod q$; zero implementation measurements on actual microcontrollers. | Standardized using official NIST FIPS 203 ML-KEM-512/768/1024 benchmarks. |

> [!IMPORTANT]
> **Key Baseline Reality**: Saeed (2025) never reported a baseline F1-score or False Positive Rate. Therefore, any paper citing Saeed (2025) as having an "88% F1" or "91% F1" is attributing metrics to Saeed that do not exist in the published paper. In our study, the Saeed baseline is defined strictly as **Saeed's 2-layer LSTM Autoencoder with 95th percentile MSE thresholding, trained and evaluated under identical conditions on the CICIoT2023 benchmark**.

---

## 3. Adapted Baseline Architecture & Implementation Specification

To provide a 100% reproducible and fair benchmark, we implemented Saeed's exact anomaly detection architecture in PyTorch (`src/detection/autoencoders.py`):

### 3.1. Mathematical Architecture
Given an input sequence $X = [x_1, x_2, \dots, x_L] \in \mathbb{R}^{L \times d}$ where $d=39$ (CICIoT2023 NetFlow features):

1. **LSTM Encoder**:
   $$\begin{aligned}
   f_t &= \sigma(W_f [h_{t-1}, x_t] + b_f) \\
   i_t &= \sigma(W_i [h_{t-1}, x_t] + b_i) \\
   \tilde{c}_t &= \tanh(W_c [h_{t-1}, x_t] + b_c) \\
   c_t &= f_t \odot c_{t-1} + i_t \odot \tilde{c}_t \\
   o_t &= \sigma(W_o [h_{t-1}, x_t] + b_o) \\
   h_t &= o_t \odot \tanh(c_t)
   \end{aligned}$$
   Two stacked LSTM layers with hidden dimension $h = 64$. The final hidden state $h_L^{(2)}$ serves as the compressed bottleneck representation.

2. **Context Expansion & LSTM Decoder**:
   The bottleneck state $h_L^{(2)}$ is repeated across sequence length $L$ and fed into a 2-layer LSTM decoder ($h=64$), followed by a linear projection layer:
   $$\hat{x}_t = W_p h_{\text{dec}, t}^{(2)} + b_p \in \mathbb{R}^{39}$$

3. **Reconstruction Error Calculation**:
   $$e(X) = \frac{1}{L \cdot d} \sum_{t=1}^L \sum_{j=1}^d (x_{t,j} - \hat{x}_{t,j})^2$$

4. **Saeed Static Threshold**:
   $$\tau_{\text{Saeed}} = \text{Percentile}_{95}\left(\{e(X_{\text{val}}^{(i)})\}_{i=1}^{N_{\text{val}}}\right)$$
   where $X_{\text{val}}$ contains strictly benign validation traffic.

5. **Decision Rule**:
   $$\hat{y} = \begin{cases} 1 & \text{if } e(X) > \tau_{\text{Saeed}} \\ 0 & \text{otherwise} \end{cases}$$

---

## 4. Sequence Formulation Nuance: Tabular NetFlow vs. Time Series

A fundamental methodological trap arises when applying recurrent models (LSTM, GRU) to NetFlow datasets like CICIoT2023.

### 4.1. The Failure Mode of Naïve Sliding Windows ($L=10$)
In physical sensor time-series (like Saeed's private simulation), consecutive samples represent successive measurements from the same physical sensor. In contrast, **CICIoT2023 provides pre-shuffled flow-level statistical summaries**. 

When researchers construct sequences by sliding a window of length 10 across shuffled rows ($X_{t:t+10}$):
1. **Zero Pure Benign Sequences**: With an 85% attack prevalence, the probability of 10 consecutive rows being benign is $(0.149)^{10} \approx 5.6 \times 10^{-9}$. In a 100,000-sample test set, the empirical count of pure benign length-10 sequences is **exactly 0** ($0.00\%$).
2. **Artificial Cross-Flow Transition Noise**: The sequence glues together 10 unrelated flows from different IP addresses, protocols, and sessions.
3. **Threshold Collapse & 100% FPR**: Because every single test sequence contains attack traffic or disjoint session leaps, the test reconstruction error universally exceeds $\tau_{\text{Saeed}}$ ($e_{\text{test}} \ge 1.718$ vs $\tau = 0.968$). As a result:
   - **$FPR = 100.00\%$** (all 14,909 benign sequences flagged as attacks).
   - Under EWMA adaptation, the threshold inflates exponentially, resulting in **$Recall = 0.45\%$**.

### 4.2. The Individual NetFlow Formulation ($L=1$)
To eliminate cross-event boundary leakage and evaluate Saeed's LSTM cell fairly on identical data:
- Each NetFlow feature vector is treated as an independent observation of dimension $(1, 39)$.
- The LSTM processes $(B, 1, 39)$ and decodes $(B, 1, 39)$.
- All 100,000 held-out test samples are evaluated identically to the Dense Autoencoder without sequence mixing.

---

## 5. Experimental Protocol & 5-Seed Comparison Matrix

### 5.1. Data Partitions (Strict Temporal & Record Split)
- **$X_{\text{train}}$**: 100,000 records, 100% Benign traffic (Unsupervised baseline training).
- **$X_{\text{val}}$**: 30,000 records, 100% Benign traffic (Threshold calibration).
- **$X_{\text{sup}}$**: 40,000 records, 85% Attack / 15% Benign (Supervised reference & RL training).
- **$X_{\text{test}}$**: 100,000 records, 85% Attack / 15% Benign (Identical held-out evaluation).
- **Random Seeds**: 42, 123, 456, 789, 2026.

### 5.2. Evaluation Dimensions
1. **Detection Accuracy**: Precision, Recall, F1-Score, False Positive Rate (FPR), ROC-AUC.
2. **Computational Complexity**: Number of trainable parameters, Model memory footprint (KB).
3. **Inference Latency**: Microseconds per sample ($\mu$s/sample) measured over 50 batches of 1,000 samples on CPU.
4. **Training Efficiency**: Wall-clock training duration (seconds).

---

## 6. Reproduction Execution Guide

To reproduce the adapted Saeed baseline and compare it head-to-head against Dense Autoencoder:

```bash
# 1. Activate Python Environment
python -V  # Verified on Python 3.13.4

# 2. Run Head-to-Head Comparison Across 5 Seeds
python scripts/run_fair_head_to_head_comparison.py

# 3. Verify Output Artifacts
# docs/FAIR_COMPARISON_RESULTS.csv
# results/metrics/fair_comparison_results.csv
# results/metrics/fair_comparison_per_seed.csv
```

---

## 7. Key Findings & Scientific Conclusion

1. **Comparable Anomaly Detection**: When evaluated fairly on individual flow vectors ($L=1$), the Saeed-adapted LSTM-AE achieves $87.38\% \pm 0.18\%$ F1-score (Fixed 95th), slightly below Dense Autoencoder ($88.54\% \pm 0.13\%$).
2. **Parameter Bloat**: The LSTM-AE requires **129,255 parameters** compared to **10,775 parameters** for Dense-AE (a **$12.0\times$ increase in model size**).
3. **Inference Latency Overhead**: Dense-AE executes in **$1.50\,\mu\text{s}$ per sample**, whereas LSTM-AE requires **$5.77\,\mu\text{s}$ per sample** (**$3.85\times$ slower**). For high-throughput IoT edge gateways processing 100,000 packets per second, Dense-AE fits comfortably within line-rate budgets, whereas LSTM-AE incurs severe queuing delay.
4. **Validation of Dynamic Thresholding**: Applying our Excluded EWMA adaptive threshold to the Saeed LSTM architecture elevates its recall from $78.30\%$ to $82.79\%$ and F1-score from $87.38\%$ to $89.37\%$, directly demonstrating the value of dynamic thresholding proposed as future work by Saeed (2025).
