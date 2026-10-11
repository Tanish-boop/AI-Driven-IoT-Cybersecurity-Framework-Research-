# Experiment E7: Integrated Framework Ablation Study Methodology

## 1. Overview and Scope

Experiment E7 evaluates the integrated end-to-end IoT cybersecurity pipeline and conducts a rigorous component-level ablation study. The pipeline combines four complementary security and response tiers:
1. **Unsupervised Anomaly Detection & Boundary Adaptation**: Dense Autoencoder ($L=1$) with Excluded EWMA dynamic threshold adaptation.
2. **Autonomous Defensive Response**: Un-contaminated Reinforcement Learning policy (Tabular Q-Learning / DQN) selecting among four actions: ALLOW, ALERT, RATE_LIMIT, and BLOCK.
3. **Post-Quantum Cryptographic Key Encapsulation & AEAD**: Standardized NIST FIPS 203 ML-KEM-768 session establishment paired with HKDF-SHA256 key derivation and AES-256-GCM authenticated encryption.
4. **Cryptographic Event Integrity & Forensic Auditability**: Lightweight Blockchain-style append-only cryptographic hash chain with deterministic canonical JSON serialization and tamper localization.

The objective of E7 is to empirically quantify the isolated contribution and systemic interaction of each component tier against the base paper (*Saeed, IEEE Access, 2025*) architecture and systematically ablated sub-variants.

---

## 2. Framework Pipeline Architecture

For each incoming telemetry flow event $x_t \in \mathbb{R}^{39}$ at timestep $t$, the integrated pipeline executes a synchronous five-stage processing pipeline:

```
[Incoming Flow Event x_t]
         │
         ▼
[1. Reconstruction Inference] ──► E_t = ||x_t - x_hat_t||^2
         │
         ▼
[2. Threshold Adaptation]     ──► tau_t = mu_{t-1} + k * sigma_{t-1} (Excluded EWMA)
         │                         Flag: is_anomaly in {0, 1}
         ▼
[3. Defensive RL Mitigation]  ──► State s_t = <E_bin, Rate_bin, Alert_bin>
         │                         Action a_t in {ALLOW, ALERT, RATE_LIMIT, BLOCK}
         ▼
[4. Post-Quantum Encryption]  ──► AES-256-GCM(K_ML-KEM, Canonical(Payload))
         │
         ▼
[5. Blockchain Audit Log]     ──► Block_t = <t, ID_t, Hash_prev, Hash_payload, Hash_block>
```

---

## 3. Evaluated Ablation Variants

To establish scientific causality for each architectural innovation, E7 benchmarks six explicit variants under identical execution streams:

| Variant ID | Variant Name | Threshold Strategy | Mitigation Policy | Cryptographic Layer | Integrity Layer |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **V0** | **Base Paper Architecture** | Static Fixed 95th Percentile | Static Rule-Based Escalation | Classical None (Plaintext) | Salted SHA-256 (Unkeyed) |
| **V1** | **Ablation (-Adaptive Threshold)**| Static Fixed 95th Percentile | Tabular Q-Learning Defense | NIST ML-KEM-768 + AES-GCM | Blockchain Audit Log |
| **V2** | **Ablation (-RL Defense)** | Excluded EWMA Adaptation | Static Rule-Based Escalation | NIST ML-KEM-768 + AES-GCM | Blockchain Audit Log |
| **V3** | **Ablation (-PQC)** | Excluded EWMA Adaptation | Tabular Q-Learning Defense | Classical / None | Blockchain Audit Log |
| **V4** | **Ablation (-Blockchain Log)** | Excluded EWMA Adaptation | Tabular Q-Learning Defense | NIST ML-KEM-768 + AES-GCM | Salted SHA-256 (Unkeyed) |
| **V5** | **Full Proposed Framework** | Excluded EWMA Adaptation | Tabular Q-Learning Defense | NIST ML-KEM-768 + AES-GCM | Blockchain Audit Log |

---

## 4. Evaluation Metrics & Protocol

### 4.1 Evaluation Dataset Split
- Evaluation is executed over 5 random seeds ($42, 123, 456, 789, 2026$).
- Models are trained strictly on benign partition `X_train` (15,000 samples) and supervisory partition `X_sup` (2,000 samples).
- Evaluation is performed on the first 5,000 samples of the held-out `X_test` partition (`y_test_binary`), strictly isolated from training.

### 4.2 Evaluated Metrics
1. **Intrusion Detection Performance**:
   - Precision: $\frac{TP}{TP + FP}$
   - Recall: $\frac{TP}{TP + FN}$
   - F1-Score: $\frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$
   - False Positive Rate (FPR): $\frac{FP}{FP + TN}$
2. **Defensive Response & Service Availability**:
   - Attack Containment Rate (%): Percentage of attack events contained via RATE_LIMIT or BLOCK actions.
   - Benign False Block Rate (%): Percentage of benign flow events falsely blocked (Action = 3).
   - Service Availability (%): $100\% - \text{False Block Rate}$.
3. **Operational Overhead**:
   - End-to-End Latency per Event ($\text{ms}$): Combined execution time across all 5 pipeline stages.
   - System Throughput ($\text{events/sec}$): Inverse mean per-event latency.
   - Storage Overhead ($\text{Bytes}$): Additional cryptographic metadata (nonces, authentication tags, block headers, hash links).
4. **Security Assurance Properties**:
   - Post-Quantum Security: Resistance to quantum cryptanalytic attacks (Shor's algorithm).
   - Forensic Immutability: Resistance to unauthorized post-hoc audit record modification and sequence tampering.
