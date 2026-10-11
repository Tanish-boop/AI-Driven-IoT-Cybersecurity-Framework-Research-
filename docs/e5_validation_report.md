# Experiment E5: Post-Quantum Cryptography Validation Report

## 1. Executive Summary

Experiment E5 validates the post-quantum cryptographic upgrade for IoT telemetry frame protection. We benchmarked NIST FIPS 203 ML-KEM-512, ML-KEM-768, and ML-KEM-1024 paired with HKDF-SHA256 and AES-256-GCM AEAD across payload sizes of 64B, 256B, 1KiB, and 4KiB.

All cryptographic integrity and tamper rejection assertions passed.

## 2. Validation Checklist

- [x] **NIST Standard Compliance**: ML-KEM-512, 768, 1024 implemented according to NIST FIPS 203 specifications.
- [x] **Artifact Size Verification**: Verified exact key and ciphertext byte sizes:
  - ML-KEM-512: $PK = 800\text{B}$, $SK = 1632\text{B}$, $CT = 768\text{B}$, $SS = 32\text{B}$.
  - ML-KEM-768: $PK = 1184\text{B}$, $SK = 2400\text{B}$, $CT = 1088\text{B}$, $SS = 32\text{B}$.
  - ML-KEM-1024: $PK = 1568\text{B}$, $SK = 3168\text{B}$, $CT = 1568\text{B}$, $SS = 32\text{B}$.
- [x] **Shared Secret Equality**: Decapsulation reconstructs the exact shared secret generated during encapsulation across 100/100 trials per parameter set.
- [x] **AEAD Integrity & Tamper Rejection**: 1-byte bit flips in ciphertext or header data reliably raise `cryptography.exceptions.InvalidTag`, preventing unauthenticated ciphertext processing.
- [x] **Latency Bounds**:
  - ML-KEM-512 total setup latency: **0.1802 ms**
  - ML-KEM-768 total setup latency: **0.4293 ms**
  - ML-KEM-1024 total setup latency: **0.4594 ms**
- [x] **Automated Test Coverage**: 7/7 unit tests passing in `tests/test_e5_crypto.py`.

## 3. Discrepancies with Base Paper Claims

| Base Paper Claim (*IEEE Access, 2025*) | Independent Benchmark Findings | Resolution / Scientific Stance |
| :--- | :--- | :--- |
| Unspecified "LWE" post-quantum encryption | Standardized NIST FIPS 203 ML-KEM-768 | Baseline updated to standardized FIPS 203 specification. |
| No latency or artifact size breakdown | Detailed breakdown for KeyGen, Encaps, Decaps, AEAD, PK/SK/CT sizes | Documented exact memory and latency trade-offs transparently. |
| No tamper detection verification | Verified OpenSSL AES-256-GCM tag verification | Added explicit integrity and tamper rejection unit tests. |

## 4. Conclusion & Recommendation

ML-KEM-768 provides the optimal balance of NIST Category 3 security (192-bit classical quantum equivalence) and low computational latency (<0.5 ms setup). It is recommended as the default PQC mechanism for the framework.
