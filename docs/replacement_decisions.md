# Mandatory Replacement Mapping and Evidence-Based Decisions

**Reference Section**: Section 11 of Master Research Execution Prompt  
**Status**: Active Decision Log  

---

## Component Replacement Decision Log

| Original Component (Base Paper) | Candidate Replacement / Improvement | Reason for Change | Evidence Supporting Decision | Expected Benefit vs Disadvantage | Experiment ID | Decision Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **LSTM Anomaly Detector** | Dense Autoencoder (Sample-Level $L=1$) | Pre-shuffled raw Parquet rows cause sequence window boundary contamination ($\text{FPR}=1.0$). | 5-seed benchmark ($F1=0.9014$, ROC-AUC=$0.9225$). | **Benefit**: Eliminates boundary leakage. Lower latency.<br>**Disadvantage**: Cannot model non-shuffled long-range temporal dependencies. | E1, E3 | **REPLACE** |
| **Fixed Anomaly Threshold** | Excluded EWMA Adaptive Threshold | Static percentiles ($\tau_{95}$) experience false positive explosions (+454.4%) under rate shifts. UnGuarded EWMA inflates. | 5-seed stress test ($F1=0.9014 \pm 0.0018$). | **Benefit**: Adapts to rate shifts while preventing attack inflation.<br>**Disadvantage**: Higher FPR (13.60%) during continuous attack streams. | E2, E8 | **IMPROVE** |
| **Basic 3x2 Q-Learning Policy** | Tabular Q-Learning & DQN (4 Defensive Actions, Un-Contaminated Split) | Base paper uses a tiny 3x2 Q-table with unethical "counter-attack" actions. Requires realistic defensive mitigation (Alert, Rate-Limit, Block) trained strictly on `X_sup`. | Un-contaminated 5-seed rerun ($71.20\%$ containment, $0.77\%$ false block rate, $0.44$ ms latency for DQN; $55.94\%$ containment, $0.00\%$ false block rate, $0.076$ ms latency for Q-Learning). | **Benefit**: Ethical, un-contaminated defensive policy with zero false blocks (Q-Learning) or balanced containment (DQN).<br>**Disadvantage**: Q-Learning has lower total attack containment. | E4 | **IMPROVE (VERIFIED)** |
| **Salted SHA-256 Integrity Check** | HMAC-SHA-256 & Blockchain Audit Log | Salted SHA-256 is an unkeyed hash function that cannot prevent forgery by adversaries with storage access. | E6 benchmark across 4 payload sizes and 2,000 blocks: HMAC-SHA-256 provides anti-forgery at 171B overhead and 0.033ms latency; blockchain audit log provides sequence protection with O(1) append latency (0.041ms). | **Benefit**: Genuine message authentication and sequence-tamper localization.<br>**Disadvantage**: Symmetric key management for HMAC; chain scaling for audit log. | E6 | **IMPROVE (VERIFIED)** |

