# Experiment E5: Post-Quantum Cryptography (PQC) Benchmark Methodology

## 1. Overview and Scope

Experiment E5 evaluates the performance, computational latency, artifact memory footprints, and communication overhead of standardized NIST FIPS 203 (ML-KEM) post-quantum Key Encapsulation Mechanisms integrated into an IoT hybrid encryption pipeline.

The base paper (*IEEE Access, 2025*) claimed post-quantum encryption integration using vague "Learning With Errors (LWE)" references without specifying concrete parameter sets, implementation standards, or payload benchmark protocols. In E5, we replace unverified prose claims with an independently reproducible, standardized NIST FIPS 203 implementation.

## 2. Cryptographic Architecture

The E5 hybrid cryptographic pipeline operates in two distinct phases:

### Phase 1: Post-Quantum Key Encapsulation (NIST FIPS 203 ML-KEM)
1. **Key Generation (`keygen`)**: The receiver generates an ML-KEM public key ($pk$) and secret key ($sk$).
2. **Encapsulation (`encaps`)**: The sender uses $pk$ to encapsulate a 32-byte symmetric shared secret ($ss$) into ciphertext ($ct$).
3. **Decapsulation (`decaps`)**: The receiver uses $sk$ and $ct$ to decapsulate the identical 32-byte shared secret ($ss$).

### Phase 2: Key Derivation & Authenticated Encryption (AES-256-GCM)
1. **Key Derivation Function (KDF)**: The shared secret $ss$ is passed through HKDF-SHA256 (`salt=b'IoT-PQC-Salt'`, `info=b'IoT-PQC-AEAD'`) to derive a 256-bit symmetric key ($K_{\text{AES}}$).
2. **Authenticated Encryption with Associated Data (AEAD)**: Payload data is encrypted using AES-256-GCM with a fresh 12-byte initialization vector (nonce) and associated authenticated data (`aad=b'IoT-Telemetry-Header'`).
3. **Tamper Verification**: Any byte modification in ciphertext or AAD produces an `InvalidTag` exception from the OpenSSL cryptographic provider, rejecting corrupted or tampered frames before decryption.

## 3. Parameter Sets and Experimental Setup

### ML-KEM Parameter Sets Evaluated
- **ML-KEM-512** (NIST Security Category 1, equivalent to AES-128)
- **ML-KEM-768** (NIST Security Category 3, equivalent to AES-192, recommended standard baseline)
- **ML-KEM-1024** (NIST Security Category 5, equivalent to AES-256)

### Payload Sizes Evaluated
- **64 B**: Small IoT sensor readings / telemetry frames
- **256 B**: Aggregated IoT status reports
- **1 KiB (1024 B)**: Medium data packets / log batches
- **4 KiB (4096 B)**: Large telemetry files / firmware update fragments

### Benchmark Execution Protocol
- **Repeated Trials**: 100 independent trials per parameter set and payload size.
- **Warm-up**: 5 un-timed executions per variant to eliminate JIT and cold-start caching artifacts.
- **Provider Environment**: `pqcrypto` 1.0.0 (C-optimized NIST FIPS 203) & `cryptography` 46.0.1 (OpenSSL backend) on Windows 11 x86_64, Python 3.13.4.

## 4. Benchmark Results Summary (1 KiB Payload)

| ML-KEM Variant | Public Key (B) | Secret Key (B) | Ciphertext (B) | KeyGen (ms) | Encaps (ms) | Decaps (ms) | Total KEM (ms) | First-Msg Setup (ms) | Repeated-Msg (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ML-KEM-512** | 800 | 1,632 | 768 | 0.0469 | 0.0560 | 0.0774 | 0.1802 | 0.1972 | 0.0168 |
| **ML-KEM-768** | 1,184 | 2,400 | 1,088 | 0.1114 | 0.1353 | 0.1826 | 0.4293 | 0.4754 | 0.0456 |
| **ML-KEM-1024** | 1,568 | 3,168 | 1,568 | 0.1294 | 0.1485 | 0.1815 | 0.4594 | 0.4963 | 0.0365 |

## 5. Security vs Performance Tradeoffs

1. **Sub-millisecond Latency**: Total KEM setup for ML-KEM-768 is **0.4293 ms**, making it extremely practical for resource-constrained IoT gateways and edge nodes.
2. **Session Key Reuse Advantage**: Once the ML-KEM key exchange establishes the symmetric key, subsequent message transmissions (`Repeated-Msg`) require only **0.0456 ms** for ML-KEM-768 (AES-GCM encryption/decryption), achieving over **20 MB/s** cryptographic throughput.
3. **Artifact Size Impact**: Public keys (1,184 B for ML-KEM-768) and ciphertexts (1,088 B) are significantly larger than classical ECDH (64 B), but remain well within standard Ethernet MTU (1500 B) when transmitted across IP networks.
