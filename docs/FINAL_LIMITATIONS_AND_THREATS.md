# Comprehensive Limitations, Threats to Validity, and Security Boundaries

**Document Purpose**: Definitive, unvarnished disclosure of all experimental limitations, environmental boundaries, cryptographic constraints, and threats to validity for peer-reviewed journal submission.  
**Auditor**: Independent Pre-Submission Research Audit  
**Date**: October 11, 2026  

---

## 1. Threats to Empirical Validity & Dataset Generalization

### 1.1 Pre-Shuffled Dataset Origin & Capture Session Loss
- **The Reality**: The underlying source dataset (*CICIoT2023, Neto et al., Sensors 2023*) was globally row-shuffled by the dataset creators prior to parquet export on public repositories (e.g., HuggingFace `siyam21/CIC-IoT-2023`).
- **Consequence**: Individual flow records cannot be mapped back to continuous chronological capture sessions or specific hardware device IP clusters without raw multi-terabyte PCAP reprocessing.
- **Evaluation Boundary**: Our benchmark operates on sample-level flow records ($L=1$). We explicitly acknowledge that temporal sequence models (such as LSTM with lookback $L > 1$) cannot be legitimately trained on pre-shuffled flow data without catastrophic sequence window boundary leakage ($\text{FPR} = 1.0$).

### 1.2 Cross-Partition Duplicate Overlap Reconciled & Deduplicated Evaluation
- **Raw Parquet Inner Join**: Merging raw `train.parquet` (1.07M rows) and `test.parquet` (268k rows) on 39 numerical features yields $201,148$ identical row pairs across $22,406$ distinct feature patterns. This high volume is an artifact of global row shuffling applied across massive volumetric attack bursts (millions of identical packets).
- **Processed Research Partition**: In our partitioned dataset (`data/processed/recovery/recovery_processed.npz`):
  - $X_{\text{train}}$ ($100\text{k}$) vs $X_{\text{test}}$ ($100\text{k}$): **81 unique feature patterns** overlap ($215$ test rows, $0.215\%$).
  - $X_{\text{sup}}$ ($40\text{k}$) vs $X_{\text{test}}$ ($100\text{k}$): **953 unique feature patterns** overlap ($1,402$ test rows, $1.402\%$).
  - Combined unique overlapping rows in $X_{\text{test}}$: **1,457 rows** ($1.457\%$).
- **Per-Slice Overlap Breakdown Across Evaluation Experiments**:
  - Full $X_{\text{test}}$ ($100\text{k}$, E1–E3): 215 rows ($0.215\%$) overlap with $X_{\text{train}}$; 1,402 rows ($1.402\%$) overlap with $X_{\text{sup}}$.
  - E4 Scenario 1 ($5\text{k}$, rows 5,000–10,000): 10 rows ($0.200\%$) overlap with $X_{\text{train}}$; 63 rows ($1.260\%$) overlap with $X_{\text{sup}}$.
  - E4 Scenario 2 ($5\text{k}$, rows 10,000–15,000): 8 rows ($0.160\%$) overlap with $X_{\text{train}}$; 84 rows ($1.680\%$) overlap with $X_{\text{sup}}$.
  - E7 Stream Slice ($5\text{k}$, rows 0–5,000): 10 rows ($0.200\%$) overlap with $X_{\text{train}}$; 70 rows ($1.400\%$) overlap with $X_{\text{sup}}$.
- **Empirical Re-Evaluation on Clean Deduplicated Test Set ($N=98,543$) Across 5 Random Seeds**:
  To test whether feature vector overlap artificially inflates model performance, we removed all 1,457 overlapping rows and re-evaluated the core models across all 5 random seeds ($42, 123, 456, 789, 2026$) on the remaining 98,543 test flows:
  - *Dense-AE Fixed 95th*: Full F1 = $0.8854 \pm 0.0013 \to$ Clean F1 = $0.8845 \pm 0.0014$ (Delta: $-0.0009 \pm 0.0001$ / $-0.10\%$, Clean FPR: $0.0492 \pm 0.0013$).
  - *Dense-AE Excluded EWMA*: Full F1 = $0.9014 \pm 0.0018 \to$ Clean F1 = $0.9007 \pm 0.0019$ (Delta: $-0.0007 \pm 0.0003$ / $-0.08\%$, Clean FPR: $0.1363 \pm 0.0115$).
  - *XGBoost Oracle*: Full F1 = $0.9269 \pm 0.0004 \to$ Clean F1 = $0.9265 \pm 0.0003$ (Delta: $-0.0003 \pm 0.0001$ / $-0.03\%$, Clean FPR: $0.0160 \pm 0.0011$).
  The performance shift across all five seeds is strictly $\le -0.0009$ ($-0.10\%$), confirming that natural feature repetitions do not materially bias model metrics.
- **Scientific Interpretation & Bounded Limitations (TASK 2 Enforcement)**:
  1. *Feature Vectors vs. Physical Events*: Identical numerical feature vectors reflect identical flow headers (e.g., TCP SYN packets with uniform packet length and flags during volumetric flooding). They represent repeated feature patterns rather than guaranteed identical physical network events.
  2. *Capture Session Loss*: Because original packet capture IDs and session timestamps are unavailable in the public pre-shuffled CICIoT2023 distribution, complete capture-level or device-level independence cannot be established from flow features alone.
  3. *Zero-Leakage Caveat*: We do **not** claim the dataset is completely leakage-free or that zero-day generalization across novel hardware testbeds has been proven. The duplicate-exclusion analysis proves statistical robustness against test-partition feature repetitions, but true device independence requires multi-testbed physical evaluations.

### 1.3 Synthetic Feature Rate Scaling vs. Live Network Replay (E8)
- In Experiment E8, non-stationary rate surges were evaluated by applying scalar multipliers ($1.5\times, 2.0\times$) to flow rate features (`Rate`, `Tot size`, `Variance`) of benign test samples for the Fixed 95th Percentile threshold.
- Under $2.0\times$ feature scaling, Fixed 95th FPR explodes from $4.93\%$ to $27.33\%$ (+454.4% increase).
- **Explicit Scope Limitation**: Excluded EWMA was evaluated on the base stream in Experiment E2 and was **not** re-evaluated under $1.5\times$ or $2.0\times$ synthetic feature scaling in E8. Claims of threshold shift stability apply strictly to the dynamic stream conditions tested in E2.
- While synthetic feature scaling isolates the mathematical response of decision thresholds to rate scaling, it does not simulate live multi-hop transport jitter, packet fragmentation, or protocol state resets that occur during physical live network flooding.

---

## 2. Hardware Platform & Micro-Architectural Scope

### 2.1 Host-Class Gateway Benchmark Boundary
- All computational microbenchmarks (E1–E8) were conducted on an AMD64 architecture (Windows 11 x86_64, 3.40 GHz host CPU).
- This platform faithfully models host-class industrial IoT edge gateways, fog nodes, and smart hub servers (e.g., Raspberry Pi 4/5, Intel Atom/NUC industrial gateways, NVIDIA Jetson modules).

### 2.2 Inapplicability to Deeply Embedded Microcontrollers
- Deeply constrained microcontrollers (e.g., 8-bit AVR microcontrollers, 32-bit ARM Cortex-M0/M3/M4 running under 100 MHz with $<64$ KB RAM) cannot execute floating-point Dense Autoencoders or NIST ML-KEM-768 key decapsulation in sub-millisecond times.
- Deploying this framework on deeply embedded MCUs requires dedicated integer-only quantization (TFLite Micro) and assembly-level polynomial arithmetic optimizations, which is outside the scope of this work.

---

## 3. Cryptographic & Forensic Audit Threat Boundaries

### 3.1 Local Hash Chain Rewrite Boundary (Formal Proof)
- **Implemented Mechanism**: The append-only audit log links consecutive evidence records via SHA-256 hashes:
  $$h_i = \text{SHA-256}(h_{i-1} \,\|\, r_i \,\|\, \text{seq}_i)$$
- **Adversary Model $\mathcal{A}_{\text{proc}}$ (Unprivileged Process)**: Cannot modify, insert, delete, or reorder evidence records without causing an immediate verification failure when checking $h_i = \text{SHA-256}(h_{i-1} \,\|\, r_i \,\|\, \text{seq}_i)$.
- **Adversary Model $\mathcal{A}_{\text{root}}$ (Host Storage Access)**: An adversary with administrative write privileges to local storage can rewrite the *entire* chain from the genesis block forward, recomputing all valid hashes:
  $$h'_k = \text{SHA-256}(h'_{k-1} \,\|\, r'_k \,\|\, \text{seq}_k) \quad \forall k \ge i$$
- **Explicit Disclosure**: A local cryptographic hash chain alone does **not** provide distributed Byzantine consensus or immutable decentralized persistence. To achieve complete anti-rewriting immutability, the latest tip hash ($h_N$) must be periodically anchored to an external trusted timestamping authority or distributed ledger.

### 3.2 Post-Quantum Cryptography Scope
- NIST FIPS 203 ML-KEM-768 provides quantum-resistant IND-CCA2 security for key encapsulation.
- Symmetric payload encryption is performed via AES-256-GCM AEAD, which offers 128-bit security against Grover's quantum search algorithm (256-bit key length).
- We do not claim the entire end-to-end IoT ecosystem is "quantum-proof" against physical side-channel attacks, fault injection, or implementation-level timing leakage.

---

## 4. Anomaly Detection & Mitigation Trade-Offs

### 4.1 The False Positive vs. Recall Trade-Off
- **Fixed 95th Percentile Baseline**: Achieves low false alarm rate ($\text{FPR} = 4.93\% \pm 0.13\%$), but misses $19.87\%$ of attacks ($\text{Recall} = 80.13\%$). Under $2.0\times$ traffic surges, FPR explodes to $27.33\%$ ($+454.4\%$).
- **Excluded EWMA Dynamic Adaptation**: Prevents surge inflation and significantly boosts detection recall to $84.01\% \pm 0.23\%$ ($\text{F1} = 0.9014 \pm 0.0018$).
- **The Cost**: On non-attack, bursty benign telemetry, Excluded EWMA exhibits an empirical false positive rate of $13.60\% \pm 1.10\%$.
- **Transparent Stance**: We do not claim Excluded EWMA is universally superior in every dimension; it represents an intentional operational trade-off that prioritizes attack detection and surge stability at the expense of higher background false alarms.

### 4.2 Noise Propagation in Automated Mitigation (E4 vs. E7)
- In isolated environment testing (E4), Tabular Q-Learning achieves a $0.00\%$ false block rate because the environment alert counter is clean.
- In integrated streaming (E7), the policy receives alerts directly from the Excluded EWMA detector. Upstream false alarms ($13.6\%$ FPR) cause the alert streak to increment, leading the downstream policy to throttle or block $7.39\% \pm 2.51\%$ of benign flows.
- Automated response pipelines inherently suffer from upstream detector error amplification.

---

## 5. Statistical Sample Size & Multiple Comparisons

### 5.1 Sample Size Constraint ($N=5$)
- All stochastic experiments were evaluated across 5 standardized random seeds ($42, 123, 456, 789, 2026$).
- **Wilcoxon Limitation**: For a two-sided Wilcoxon signed-rank test with $N=5$, the absolute minimum achievable $p$-value is $\frac{2}{2^5} = 0.0625$. Consequently, Wilcoxon tests cannot achieve $p < 0.05$ at $N=5$.
- **Parametric Justification**: Paired $t$-tests ($df=4$) and exact 95% confidence intervals were employed to assess significance, supplemented by Cohen's $d$ effect sizes and Holm-Bonferroni corrections.
- While detection differences exhibit massive effect sizes ($d > 8.0$), mitigation containment differences between DQN and Tabular Q-Learning ($p = 0.1109$) and Ablation (-RL) ($p = 0.3853$) are honestly reported as non-significant under 5 seeds.

---

## 6. Summary for Peer Reviewers

| Disclosed Item | Honest Peer-Review Disclosure |
| :--- | :--- |
| **Dataset Provenance** | Evaluated on partitioned CICIoT2023 flow records; cross-partition identical feature vectors represent $0.081\%$ (benign) and $0.953\%$ (attack) due to natural network high-rate flooding invariance. |
| **Hardware Boundary** | Sub-millisecond latency validated on host-class AMD64 edge gateways; embedded microcontrollers require dedicated integer quantization and assembly optimization. |
| **Audit Log Boundary** | Local append-only hash chain guarantees sequence integrity against unprivileged processes; external tip anchoring is required to prevent privileged root rewriting. |
| **Thresholding Trade-Off** | Excluded EWMA increases recall (+3.88%) and prevents surge collapse, but incurs higher background false alarms ($13.6\%$ vs $4.9\%$). |
| **Defense Realism** | Standalone Q-policy achieves $0.00\%$ false block rate, but integrated pipeline exhibits $7.39\%$ false block rate due to upstream detector noise propagation. |
