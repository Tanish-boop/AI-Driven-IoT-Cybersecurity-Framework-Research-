"""
Post-Quantum Cryptography Benchmark Module (E5)
Standardized NIST FIPS 203 ML-KEM Parameter Sets:
  - ML-KEM-512
  - ML-KEM-768
  - ML-KEM-1024
Paired with HKDF-SHA256 Key Derivation and AES-256-GCM Authenticated Encryption.
"""

import os
import time
import numpy as np
import pqcrypto.kem.ml_kem_512 as mlkem512
import pqcrypto.kem.ml_kem_768 as mlkem768
import pqcrypto.kem.ml_kem_1024 as mlkem1024

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

KEM_MAP = {
    'ML-KEM-512': mlkem512,
    'ML-KEM-768': mlkem768,
    'ML-KEM-1024': mlkem1024
}

PAYLOAD_SIZES = {
    '64B': 64,
    '256B': 256,
    '1KiB': 1024,
    '4KiB': 4096
}

def benchmark_kem_variant(variant_name='ML-KEM-768', trials=100, payload_bytes=1024):
    kem = KEM_MAP[variant_name]
    
    # Warm-up run
    for _ in range(5):
        pk_w, sk_w = kem.keygen()
        ct_w, ss1_w = kem.encaps(pk_w)
        ss2_w = kem.decaps(sk_w, ct_w)
        assert ss1_w == ss2_w

    keygen_times = []
    encaps_times = []
    decaps_times = []
    total_kem_times = []
    aead_enc_times = []
    aead_dec_times = []
    first_msg_times = []
    repeated_msg_times = []

    payload = os.urandom(payload_bytes)
    aad = b'IoT-Telemetry-Header'

    for t in range(trials):
        # 1. KeyGen
        t0 = time.perf_counter()
        pk, sk = kem.keygen()
        t1 = time.perf_counter()
        
        # 2. Encaps
        ct, ss1 = kem.encaps(pk)
        t2 = time.perf_counter()
        
        # 3. Decaps
        ss2 = kem.decaps(sk, ct)
        t3 = time.perf_counter()
        
        assert ss1 == ss2, f"Shared secret mismatch on trial {t}"
        
        # 4. KDF (HKDF-SHA256)
        t_kdf_start = time.perf_counter()
        hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=b'IoT-PQC-Salt', info=b'IoT-PQC-AEAD')
        aes_key = hkdf.derive(ss1)
        
        # 5. AEAD Encryption (AES-256-GCM)
        aesgcm = AESGCM(aes_key)
        nonce = os.urandom(12)
        aead_ct = aesgcm.encrypt(nonce, payload, associated_data=aad)
        t_enc = time.perf_counter()
        
        # 6. AEAD Decryption
        decrypted = aesgcm.decrypt(nonce, aead_ct, associated_data=aad)
        t_dec = time.perf_counter()
        assert decrypted == payload, f"Decrypted payload mismatch on trial {t}"

        # Timing metrics in milliseconds
        keygen_ms = (t1 - t0) * 1000.0
        encaps_ms = (t2 - t1) * 1000.0
        decaps_ms = (t3 - t2) * 1000.0
        total_kem_ms = (t3 - t0) * 1000.0
        aead_enc_ms = (t_enc - t_kdf_start) * 1000.0
        aead_dec_ms = (t_dec - t_enc) * 1000.0
        first_msg_ms = (t_dec - t0) * 1000.0
        repeated_msg_ms = (t_dec - t_kdf_start) * 1000.0

        keygen_times.append(keygen_ms)
        encaps_times.append(encaps_ms)
        decaps_times.append(decaps_ms)
        total_kem_times.append(total_kem_ms)
        aead_enc_times.append(aead_enc_ms)
        aead_dec_times.append(aead_dec_ms)
        first_msg_times.append(first_msg_ms)
        repeated_msg_times.append(repeated_msg_ms)

    # Communication Overhead Calculation
    # Public Key + KEM Ciphertext + AES-GCM Nonce (12B) + AEAD Tag (16B)
    comm_overhead_first_msg = len(pk) + len(ct) + 12 + 16 + payload_bytes
    comm_overhead_repeated = 12 + 16 + payload_bytes

    return {
        'variant': variant_name,
        'payload_size_name': f"{payload_bytes}B",
        'payload_bytes': payload_bytes,
        'pk_size_bytes': len(pk),
        'sk_size_bytes': len(sk),
        'ct_size_bytes': len(ct),
        'ss_size_bytes': len(ss1),
        'comm_overhead_first_msg_bytes': comm_overhead_first_msg,
        'comm_overhead_repeated_bytes': comm_overhead_repeated,
        'keygen_mean_ms': float(np.mean(keygen_times)),
        'keygen_std_ms': float(np.std(keygen_times)),
        'keygen_median_ms': float(np.median(keygen_times)),
        'keygen_p95_ms': float(np.percentile(keygen_times, 95)),
        'encaps_mean_ms': float(np.mean(encaps_times)),
        'encaps_std_ms': float(np.std(encaps_times)),
        'encaps_median_ms': float(np.median(encaps_times)),
        'encaps_p95_ms': float(np.percentile(encaps_times, 95)),
        'decaps_mean_ms': float(np.mean(decaps_times)),
        'decaps_std_ms': float(np.std(decaps_times)),
        'decaps_median_ms': float(np.median(decaps_times)),
        'decaps_p95_ms': float(np.percentile(decaps_times, 95)),
        'total_kem_mean_ms': float(np.mean(total_kem_times)),
        'total_kem_std_ms': float(np.std(total_kem_times)),
        'aead_enc_mean_ms': float(np.mean(aead_enc_times)),
        'aead_dec_mean_ms': float(np.mean(aead_dec_times)),
        'first_msg_mean_ms': float(np.mean(first_msg_times)),
        'first_msg_std_ms': float(np.std(first_msg_times)),
        'repeated_msg_mean_ms': float(np.mean(repeated_msg_times)),
        'repeated_msg_std_ms': float(np.std(repeated_msg_times)),
        'throughput_mb_s': float((payload_bytes / (1024 * 1024)) / (np.mean(first_msg_times) / 1000.0))
    }

def verify_tamper_rejection(variant_name='ML-KEM-768'):
    kem = KEM_MAP[variant_name]
    pk, sk = kem.keygen()
    ct, ss1 = kem.encaps(pk)
    
    hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=b'IoT-PQC-Salt', info=b'IoT-PQC-AEAD')
    aes_key = hkdf.derive(ss1)
    aesgcm = AESGCM(aes_key)
    
    nonce = os.urandom(12)
    payload = b'Sensitive Telemetry'
    aead_ct = bytearray(aesgcm.encrypt(nonce, payload, associated_data=b'Header'))
    
    # Corrupt 1 byte of ciphertext
    aead_ct[0] ^= 0xFF
    
    try:
        aesgcm.decrypt(nonce, bytes(aead_ct), associated_data=b'Header')
        return False # Failed to reject tampering!
    except InvalidTag:
        return True # Successfully rejected tampering!
