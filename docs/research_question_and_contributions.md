# Research Question, Evidence-Backed Novelty Assessment, and Contributions

**Document Date**: October 9, 2026 (Revised Iteration 2)  
**Primary Author**: Senior Research Engineer  
**Status**: Revised Protocol Incorporating Pre-Approval Feedback  

---

## 1. Title and Refined Research Question

### Working Title
**Empirical Evaluation of Adaptive Anomaly Thresholding Strategies for IoT Intrusion Detection Under Non-Stationary Traffic Conditions**

### Primary Research Question
> *How do fixed, un-guarded adaptive, and guarded adaptive thresholding strategies compare in balancing attack detection recall against false-alarm adaptation when sequence-based deep reconstruction models (LSTM-AE, GRU-AE, Dense-AE) are evaluated on IoT traffic streams subjected to non-stationary rate shifts and multi-vector attacks?*

---

## 2. Research Hypotheses

* **Hypothesis 1 ($H_1$)**: Fixed percentile thresholding ($\tau_{95}, \tau_{99}$) exhibits high false-positive rates when subjected to benign traffic rate surges because its decision boundary remains static.
* **Hypothesis 2 ($H_2$)**: Un-guarded adaptive thresholding (updating statistics on all observations) successfully adapts to legitimate traffic surges but suffers from threshold inflation during sustained attacks, leading to degraded attack recall over time.
* **Hypothesis 3 ($H_3$)**: Guarded adaptive thresholding (utilizing bounded updates / statistical winsorization) achieves superior trade-offs, limiting threshold inflation during sustained attacks while permitting gradual adaptation to persistent benign baseline shifts.

---

## 3. Evidence-Backed Novelty Assessment & Related Work Comparison

### Context from Recent Literature (2025–2026)
* **Drift-Aware Streaming Anomaly Detection** (ScienceDirect 2025; Bioengineer 2025): Recent studies explore adaptive model updating and two-timescale feedback loops for streaming time-series under concept drift.
* **RL-Based & Drift Monitoring on CICIoT2023** (MDPI 2026; ejournal.abcollab.id 2026): Recent work investigates reinforcement learning for dynamic threshold tuning and feature-level drift monitoring (e.g., FeDrift) on CICIoT2023.

### Refined Contribution Statement (No Broad Priority Claims)
We do **not** claim to be the first study to examine adaptive thresholding or concept drift in IoT. Rather, our contribution is specifically focused and evidence-backed:
> *A controlled empirical evaluation comparing three explicit threshold update mechanisms (Fixed, Un-Guarded Adaptive, and Guarded Adaptive) for unsupervised deep reconstruction models on CICIoT2023, quantifying both false-alarm adaptation under synthetic rate-scaling stress tests and threshold inflation resistance under sustained attacks.*

---

## 4. Focused Scope Boundaries

### Included Components
1. **Unsupervised Deep Reconstruction Models**: LSTM Autoencoder, GRU Autoencoder, Dense Autoencoder, Isolation Forest baseline.
2. **Supervised Oracle Reference**: Separate XGBoost classifier trained on a distinct labeled partition to contextualize the unsupervised detection gap.
3. **Controlled Threshold Update Evaluation**: Comparative analysis of Fixed, Un-Guarded Adaptive, and Guarded Adaptive strategies.
4. **Stress Testing & Multi-Attack Breakdown**: Synthetic rate-scaling stress tests + per-attack family performance across 33 attack types.

### Excluded / Deferred Components
* **PQC Microbenchmarking**: Removed from the primary paper to maintain sharp focus on threshold adaptation. Deferred to a separate study.
* **Q-Learning / Counter-Attacks**: Excluded (operationally unviable for IoT edge nodes).
* **Blockchain Logging**: Excluded (unnecessary latency/storage overhead).
