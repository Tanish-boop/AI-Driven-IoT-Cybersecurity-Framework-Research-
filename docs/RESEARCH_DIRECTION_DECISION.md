# RESEARCH DIRECTION & NOVELTY DECISION

**Target Submission**: IEEE Access / Empirical Track  
**Repository**: `C:\Users\hp\OneDrive\Desktop\Research Experiments`  
**Branch**: `research/valid-evaluation`  
**Date**: October 2026  
**Status**: Decided & Grounded in Literature Audit  

---

## 1. Analysis of Novelty Gate (Stage 3 Findings)

Following a systematic audit of the seven closest related works (`docs/NEAREST_PRIOR_WORK.csv`), including Sun et al. (*ICML 2024*), ADTCD (2023), CDDIA (2024), ASOC (2025), and Springer (2026), we conclude:

1. **CGB is Not a Fundamental Theoretical Invention**:
   - The Contamination-Gated Bounded (CGB) adaptive controller combines established control-theoretic mechanisms:
     - Eligibility gating based on local anomaly rate,
     - Alert-state freeze and post-incident clean cooldown,
     - Score winsorization and per-step clipping bounds.
   - It does not introduce a novel statistical theorem (such as the anytime-valid empirical Bernstein confidence sequences of Sun et al., ICML 2024), nor does it perform streaming model weight fine-tuning (like ADTCD or CDDIA).

2. **CGB Exhibits Real Operational Trade-Offs (Not an Absolute Win)**:
   - On the nominal clean test stream: CGB achieves $\text{F1} = 88.96\%$ and $\text{FPR} = 7.75\%$, compared to $\text{F1} = 88.44\%$ and $\text{FPR} = 4.86\%$ for the Fixed 95th Percentile threshold. This represents an operational trade-off ($+0.52\%$ F1 in exchange for $+2.89\%$ higher false alarm rate).
   - Under synthetic benign score drift: CGB produced an $\text{FPR} = 18.54\%$ (higher than Fixed 95th's $11.09\%$), demonstrating that score-level gating without feature-level feedback struggles when the entire benign error distribution shifts upward.
   - Under sustained attack contamination: CGB successfully eliminates the catastrophic threshold collapse suffered by conventional un-guarded EWMA (where Recall collapsed to $0.02\%$), maintaining attack recall at $81.20\%$.

---

## 2. Selection of Primary Research Contribution: Direction B (Rigorous Benchmark & Operational Characterization)

Rather than overclaiming CGB as a revolutionary algorithm, we select **Research Direction B: A Rigorous Cross-Layer Evaluation Protocol and Contamination-Resistant Thresholding Benchmark for IoT Anomaly Detection**:

### Core Defensible Contributions
1. **Direct Answer to the Saeed (2025) Research Gap**:
   - Saeed (*IEEE Access 2025*) proposed combining LSTM, Q-learning, PQC, and hashing, but reported zero global classification metrics and explicitly highlighted static thresholding as a key limitation, calling for dynamic thresholding in future work.
   - Our paper provides the exact, rigorous empirical evaluation missing in Saeed (2025), implementing Saeed's architecture on the public **CICIoT2023** benchmark.

2. **Validation of Hardware-Aware Architectural Selection**:
   - Building on Mazinani et al. (*Future Internet, 2026*), we show that for tabular NetFlow data, recurrent sequence models (LSTM-AE, GRU-AE) suffer from sequence boundary leakage when applied to shuffled flows ($100\%$ FPR under sliding windows), and provide zero accuracy advantage over Dense Autoencoders when evaluated independently ($88.54\%$ vs $88.18\%$ F1), while Dense-AE executes in $1.35\,\mu\text{s}$ ($3.67\times$ faster) with $12.0\times$ fewer parameters.

3. **Empirical Characterization of Score-to-Decision Dynamics**:
   - We establish a benchmark protocol separating clean streams, benign drift, and malicious attack contamination.
   - We demonstrate why raw EWMA fails (threshold inflation collapse), why naive Excluded EWMA suffers severe false alarms ($15.41\%$), and how contamination gating halves false alarms ($7.75\%$) while preserving flood immunity.

4. **Modular Cross-Layer Scoping**:
   - As recommended by the Critical Review Paper (*"Beyond Component Stacking"*), the primary paper focuses tightly on the **score-to-decision boundary (detector and threshold controller)**, treating RL mitigation, NIST FIPS 203 ML-KEM key exchange, and tamper-evident audit logging as separately measured integration layers.

---

## 3. Predeclared Success & Failure Criteria

In accordance with open science practices, our benchmark evaluation will pre-register the following criteria:
- **Criterion 1 (Contamination Resilience)**: Under a sustained attack flood, the controller must maintain attack recall $\ge 80.0\%$, avoiding the collapse of un-guarded EWMA ($\text{Recall} < 1.0\%$).
- **Criterion 2 (False Alarm Boundedness)**: On nominal traffic, the controller must keep $\text{FPR} \le 8.5\%$, improving upon naive Excluded EWMA ($\text{FPR} > 13.5\%$).
- **Criterion 3 (Honest Trade-off Reporting)**: The paper will explicitly report that under pure benign score drift, static thresholds or feature-aware recalibration remain necessary if false alarm containment is paramount.
