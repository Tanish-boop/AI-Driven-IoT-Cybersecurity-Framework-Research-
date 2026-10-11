# Experiment E6: Integrity Verification Architecture Methodology

## 1. Overview and Scope

Experiment E6 evaluates the computational performance, verification overhead, storage footprint, scaling behavior, and tamper detection capabilities of three integrity verification mechanisms for IoT security event records:
1. **Salted SHA-256** (Unkeyed digest with per-record random salt)
2. **HMAC-SHA-256** (Symmetric-key authenticated message integrity, RFC 2104)
3. **Lightweight Blockchain-Style Audit Log** (Append-only cryptographic hash chain with deterministic canonical JSON serialization)

The base paper (*IEEE Access, 2025*) claimed "blockchain-based data integrity" and "salted SHA-256 verification" in vague prose without formalizing threat models, key management, sequence binding, or computational overhead. In E6, we establish a controlled, reproducible benchmark comparing these three distinct cryptographic mechanisms under identical test conditions and synthetic evidence payloads.

---

## 2. Cryptographic Architectures & Threat Models

### 2.1 Salted SHA-256
* **Formulation**:
  $$\text{Digest} = \text{SHA-256}(salt \parallel \text{CanonicalJSON}(payload))$$
* **Parameters**: 16-byte cryptographically secure random salt generated per record via `os.urandom(16)`.
* **Security Properties**: Pre-image and second pre-image resistance. The per-record unique salt prevents rainbow-table pre-computation attacks on low-entropy telemetry.
* **Threat Model Limitations**:
  - Salted SHA-256 is an **unkeyed** hash function.
  - It does NOT provide message authentication or proof of origin against an active adversary.
  - An adversary with write access to storage can modify the evidence record, recompute $\text{SHA-256}(salt \parallel payload')$, and replace the stored digest without triggering verification errors.
  - Useful only for detecting accidental transmission errors when the digest is distributed out-of-band.

### 2.2 HMAC-SHA-256
* **Formulation**:
  $$\text{MAC} = \text{HMAC-SHA256}(K, \text{CanonicalJSON}(payload))$$
* **Parameters**: 256-bit (32-byte) secret symmetric key $K$, managed in isolated key storage and strictly excluded from evidence records. Constant-time verification via `hmac.compare_digest`.
* **Security Properties**: RFC 2104 compliant message authentication code. Protects authenticity and data integrity against forgery: an adversary without $K$ cannot construct a valid MAC for modified evidence, even with full write access to the record store.
* **Threat Model Limitations**:
  - Symmetric key: any entity holding $K$ can create valid MACs (no asymmetric non-repudiation).
  - Scope: protects individual records independently. Does not intrinsically bind record order or prevent record deletion without higher-layer sequence indexing.

### 2.3 Blockchain-Style Append-Only Audit Log
* **Formulation**:
  $$\text{Block}_i = \langle i, t_i, \text{ID}_i, \text{Payload}_i, H_{\text{payload}}, H_{\text{prev}}, H_{\text{block}} \rangle$$
  $$H_{\text{payload}} = \text{SHA-256}(\text{CanonicalJSON}(\text{Payload}_i))$$
  $$H_{\text{block}} = \text{SHA-256}(\text{CanonicalJSON}(\langle i, t_i, \text{ID}_i, H_{\text{payload}}, H_{\text{prev}} \rangle))$$
  with Genesis Block $H_{\text{prev}} = 0^{64}$.
* **Security Properties**:
  - Append-only cryptographic link: tampering with block $k$ breaks $H_{\text{prev}}$ for block $k+1$.
  - Sequence integrity: detects record deletion, insertion, truncation, and reordering.
* **Threat Model Limitations**:
  - A local hash chain is NOT a decentralized consensus network.
  - If an adversary gains root write access to the host storage, the adversary can modify block $k$ and rewrite all subsequent block hashes $k+1 \dots \text{tip}$ without triggering local verification errors.
  - Complete immutability requires anchoring chain tips to an external medium (e.g., TPM/HSM, remote syslog witness, or public blockchain).

---

## 3. Benchmarking Design & Protocol

### 3.1 Synthetic Evidence Payloads
Evidence records represent IoT security events (anomaly alerts, mitigation decisions, telemetry readings), with fixed sizes matching E5:
- **64 B**: Small sensor telemetry alert
- **256 B**: Status report with anomaly scores
- **1 KiB (1024 B)**: Aggregated flow telemetry record
- **4 KiB (4096 B)**: Detailed forensic log batch

### 3.2 Evaluation Protocol
1. **Cryptographic Microbenchmarks**: 100 repeated trials measuring in-memory record creation/anchoring and verification latency.
2. **I/O Overhead Isolation**: Disk persistence measured separately to isolate filesystem append cost from pure cryptographic computation.
3. **Chain Scaling Analysis**: $N \in \{100, 500, 1000, 2000\}$ records to measure $O(1)$ block append vs $O(N)$ full chain verification scaling.
4. **Tamper Detection Battery**: 6 adversarial attack vectors evaluated:
   - Modified payload
   - Wrong verification key
   - Block deletion
   - Block insertion
   - Block reordering
   - Broken hash pointer
