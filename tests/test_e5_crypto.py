"""
Unit Tests for Experiment E5: Post-Quantum Cryptography (ML-KEM) Implementation
Verifies:
  - NIST FIPS 203 compliant artifact sizes (Public Key, Secret Key, Ciphertext, Shared Secret)
  - Key encapsulation/decapsulation shared secret equality
  - AES-256-GCM AEAD encryption and decryption correctness
  - Tamper rejection (InvalidTag exception on payload/ciphertext corruption)
  - Benchmark metric structure
"""

import os
import pytest
from cryptography.exceptions import InvalidTag
from src.crypto.ml_kem_benchmark import (
    KEM_MAP,
    PAYLOAD_SIZES,
    benchmark_kem_variant,
    verify_tamper_rejection
)


@pytest.mark.parametrize("variant, expected_pk, expected_sk, expected_ct", [
    ("ML-KEM-512", 800, 1632, 768),
    ("ML-KEM-768", 1184, 2400, 1088),
    ("ML-KEM-1024", 1568, 3168, 1568),
])
def test_ml_kem_artifact_sizes(variant, expected_pk, expected_sk, expected_ct):
    kem = KEM_MAP[variant]
    pk, sk = kem.keygen()
    ct, ss1 = kem.encaps(pk)
    ss2 = kem.decaps(sk, ct)

    assert len(pk) == expected_pk, f"{variant} PK size mismatch"
    assert len(sk) == expected_sk, f"{variant} SK size mismatch"
    assert len(ct) == expected_ct, f"{variant} CT size mismatch"
    assert len(ss1) == 32, f"{variant} Shared Secret size mismatch"
    assert len(ss2) == 32, f"{variant} Shared Secret size mismatch"
    assert ss1 == ss2, f"{variant} Shared secret mismatch between encaps and decaps"


@pytest.mark.parametrize("variant", ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"])
def test_tamper_rejection(variant):
    assert verify_tamper_rejection(variant) is True, f"Tamper rejection failed for {variant}"


def test_benchmark_kem_variant_structure():
    res = benchmark_kem_variant(variant_name="ML-KEM-768", trials=5, payload_bytes=256)
    
    expected_keys = [
        'variant', 'payload_size_name', 'payload_bytes',
        'pk_size_bytes', 'sk_size_bytes', 'ct_size_bytes', 'ss_size_bytes',
        'comm_overhead_first_msg_bytes', 'comm_overhead_repeated_bytes',
        'keygen_mean_ms', 'encaps_mean_ms', 'decaps_mean_ms', 'total_kem_mean_ms',
        'first_msg_mean_ms', 'repeated_msg_mean_ms', 'throughput_mb_s'
    ]
    for key in expected_keys:
        assert key in res, f"Missing key '{key}' in benchmark results"
    
    assert res['variant'] == "ML-KEM-768"
    assert res['payload_bytes'] == 256
    assert res['pk_size_bytes'] == 1184
    assert res['ct_size_bytes'] == 1088
    assert res['keygen_mean_ms'] > 0
    assert res['encaps_mean_ms'] > 0
    assert res['decaps_mean_ms'] > 0
