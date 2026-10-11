# Experimental Methodology & Protocols

---

## 1. Unsupervised Anomaly Detection Formulations

Let $X_t \in \mathbb{R}^{39}$ represent an un-sequenced flow feature vector at timestep $t$.

### Dense Autoencoder (Dense-AE)
- **Architecture**:
  - Encoder: Linear(39 -> 24) -> BatchNorm -> LeakyReLU(0.1) -> Linear(24 -> 12) -> LeakyReLU(0.1)
  - Bottleneck: 12 units
  - Decoder: Linear(12 -> 24) -> LeakyReLU(0.1) -> Linear(24 -> 39)
- **Loss Function**: Mean Squared Error (MSE)
  $$E_t = \frac{1}{39} \sum_{i=1}^{39} (x_{t,i} - \hat{x}_{t,i})^2$$
- **Training**: Adam optimizer (lr=0.001, weight_decay=1e-5), batch size=512, 10 epochs.

### Isolation Forest Baseline
- **Parameters**: `n_estimators=100`, `contamination='auto'`, `random_state=seed`.

### XGBoost Supervised Oracle Reference
- **Parameters**: `n_estimators=100`, `max_depth=6`, `learning_rate=0.1`, `random_state=seed`.

---

## 2. Threshold Adaptation Formulations (E2)

### Fixed Percentile ($\tau_{\text{fixed}}$)
$$\tau = \text{Percentile}(E_{\text{val}}, 95) \quad \text{or} \quad \text{Percentile}(E_{\text{val}}, 99)$$

### Un-Guarded EWMA ($\tau_{\text{unguarded}}$)
$$\mu_t = (1-\alpha)\mu_{t-1} + \alpha E_t, \quad \sigma_t^2 = (1-\alpha)\sigma_{t-1}^2 + \alpha (E_t - \mu_t)^2, \quad \tau_t = \mu_t + k \cdot \sqrt{\sigma_t^2}$$

### Excluded EWMA ($\tau_{\text{excluded}}$)
$$\text{If } E_t \le \tau_t: \quad \mu_t = (1-\alpha)\mu_{t-1} + \alpha E_t, \quad \sigma_t^2 = (1-\alpha)\sigma_{t-1}^2 + \alpha (E_t - \mu_t)^2$$

### Guarded Winsorized EWMA ($\tau_{\text{guarded}}$)
$$E_t^{\text{clamp}} = \begin{cases} E_t & \text{if } E_t \le \tau_t \\ \tau_t + \delta \cdot \sqrt{\sigma_t^2} & \text{if } E_t > \tau_t \end{cases}$$

---

## 3. Un-Contaminated Defensive-Response Policy Evaluation (E4)

### Data Partitioning Protocol
- **Policy Training Partition (`X_sup`)**: 40,000 samples (50/50 Benign/Attack balance).
- **Held-Out Evaluation Partition (`X_test`)**: 100,000 samples strictly reserved for held-out evaluation (`Scenario_1_Heavy_Attack` and `Scenario_2_Stealth_Attack`).
- **Data Isolation Guarantee**: `X_test` is NEVER used during policy training, hyperparameter selection, or Q-table initialization.

### Environment Formulation (`IoTDefenseEnv`)
- **State Representation**: $S_t = [\text{ErrBin}, \text{RateBin}, \text{AlertBin}]$ (64 discrete states for Q-learning; 3-dim normalized vector for DQN).
- **Actions** (Purely Defensive):
  - `0: ALLOW` (Pass flow; 0 disruption)
  - `1: ALERT` (Log SOC alert)
  - `2: RATE_LIMIT` (Throttle packet rate by 50%)
  - `3: BLOCK` (Isolate/drop IP flow)
- **Reward Function**:
  $$R_t = \begin{cases} +10.0 & \text{if Attack and Action = BLOCK} \\ +4.0 & \text{if Attack and Action = RATE\_LIMIT} \\ -2.0 & \text{if Attack and Action = ALERT} \\ -10.0 & \text{if Attack and Action = ALLOW} \\ +2.0 & \text{if Benign and Action = ALLOW} \\ +1.0 & \text{if Benign and Action = ALERT} \\ -3.0 & \text{if Benign and Action = RATE\_LIMIT} \\ C_{\text{benign\_block}} & \text{if Benign and Action = BLOCK} \end{cases}$$
  where $C_{\text{benign\_block}} \in [-10.0, -25.0, -50.0, -100.0]$ is evaluated for reward sensitivity.

---

## 4. Post-Quantum Cryptography Microbenchmark (E5)

### Cryptographic Primitives (NIST FIPS 203)
- **Parameter Sets**: ML-KEM-512, ML-KEM-768, ML-KEM-1024.
- **Key Derivation Function**: HKDF-SHA256 (`salt=b'IoT-PQC-Salt'`, `info=b'IoT-PQC-AEAD'`).
- **Symmetric AEAD Cipher**: AES-256-GCM with fresh 12-byte initialization vectors (`nonce`).
- **Payload Sizes**: 64B, 256B, 1KiB, 4KiB.
- **Tamper Detection**: OpenSSL `InvalidTag` exception raised on ciphertext or header modifications.
- **Provider Environment**: `pqcrypto` 1.0.0 (C backend) & `cryptography` 46.0.1.
