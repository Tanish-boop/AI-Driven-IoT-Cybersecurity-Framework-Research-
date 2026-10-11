"""
Unit Tests for Experiment E6: Integrity Verification Architecture
Verifies:
  - Salted SHA-256 correctness, payload tamper detection, and unkeyed limitation
  - HMAC-SHA-256 correctness, payload tamper detection, and secret key mismatch rejection
  - Blockchain-Style Audit Log:
    * Genesis block initialization
    * Append-only cryptographic hash linking
    * Payload modification detection at exact index
    * Broken hash link detection
    * Intermediate block deletion detection
    * Unauthorized block insertion detection
    * Block reordering detection
    * Local chain rewrite limitation demonstration
"""

import os
import copy
import pytest
from src.integrity.salted_sha256 import SaltedSHA256Verifier, SaltedEvidenceRecord
from src.integrity.hmac_sha256 import HMACSHA256Verifier, HMACEvidenceRecord
from src.integrity.blockchain_log import BlockchainAuditLog, AuditBlock, GENESIS_PREV_HASH


# ============================================================================
# 1. Salted SHA-256 Tests
# ============================================================================

def test_salted_sha256_validity():
    verifier = SaltedSHA256Verifier()
    payload = {"device_id": "iot-sensor-01", "event": "RATE_EXCEEDED", "rate": 142.5}
    record = verifier.create_record("EVID-001", 1700000100.0, payload)

    is_valid, msg = verifier.verify_record(record)
    assert is_valid is True, f"Valid Salted SHA-256 record failed verification: {msg}"
    assert len(record.salt_hex) == 32  # 16 bytes = 32 hex chars
    assert len(record.digest_hex) == 64  # SHA-256 hex


def test_salted_sha256_payload_tamper():
    verifier = SaltedSHA256Verifier()
    payload = {"device_id": "iot-sensor-01", "status": "BENIGN"}
    record = verifier.create_record("EVID-002", 1700000100.0, payload)

    # Tamper payload
    tampered_record = SaltedEvidenceRecord(
        evidence_id=record.evidence_id,
        timestamp=record.timestamp,
        payload={"device_id": "iot-sensor-01", "status": "ATTACK"},
        salt_hex=record.salt_hex,
        digest_hex=record.digest_hex
    )
    is_valid, msg = verifier.verify_record(tampered_record)
    assert is_valid is False, "Tampered payload should have failed verification"
    assert "Digest mismatch" in msg


def test_salted_sha256_unkeyed_limitation():
    """Demonstrates that an attacker with write access can forge both payload and digest."""
    verifier = SaltedSHA256Verifier()
    original_payload = {"device_id": "iot-sensor-01", "action": "BLOCK"}
    original_record = verifier.create_record("EVID-003", 1700000100.0, original_payload)

    # Attacker replaces payload AND re-calculates hash with same salt
    tampered_payload = {"device_id": "iot-sensor-01", "action": "ALLOW"}
    forged_record = verifier.create_record("EVID-003", 1700000100.0, tampered_payload)

    # Verifier cannot detect forgery because it is unkeyed
    is_valid, _ = verifier.verify_record(forged_record)
    assert is_valid is True, "Expected unkeyed hash limitation: attacker can forge valid digest"


# ============================================================================
# 2. HMAC-SHA-256 Tests
# ============================================================================

def test_hmac_sha256_validity():
    verifier = HMACSHA256Verifier()
    payload = {"device_id": "iot-gateway-01", "decision": "ISOLATE", "confidence": 0.98}
    record = verifier.create_record("EVID-HMAC-01", 1700000200.0, payload)

    is_valid, msg = verifier.verify_record(record)
    assert is_valid is True, f"Valid HMAC record failed verification: {msg}"
    assert len(record.mac_hex) == 64


def test_hmac_sha256_payload_tamper():
    verifier = HMACSHA256Verifier()
    payload = {"device_id": "iot-gateway-01", "anomaly_score": 0.85}
    record = verifier.create_record("EVID-HMAC-02", 1700000200.0, payload)

    tampered_record = HMACEvidenceRecord(
        evidence_id=record.evidence_id,
        timestamp=record.timestamp,
        payload={"device_id": "iot-gateway-01", "anomaly_score": 0.05},
        key_id=record.key_id,
        mac_hex=record.mac_hex
    )
    is_valid, msg = verifier.verify_record(tampered_record)
    assert is_valid is False, "Tampered HMAC payload should have failed verification"
    assert "HMAC verification failure" in msg


def test_hmac_sha256_wrong_key_rejection():
    """Verifies that an incorrect verification key fails verification strictly."""
    key_alice = os.urandom(32)
    key_bob = os.urandom(32)

    verifier_alice = HMACSHA256Verifier(key=key_alice)
    payload = {"event": "THRESHOLD_EXCEEDED", "threshold": 0.075}
    record = verifier_alice.create_record("EVID-HMAC-03", 1700000300.0, payload)

    # Verification with Alice's key succeeds
    assert verifier_alice.verify_record(record)[0] is True

    # Verification with Bob's key MUST fail
    is_valid, msg = verifier_alice.verify_record(record, verification_key=key_bob)
    assert is_valid is False
    assert "HMAC verification failure" in msg


# ============================================================================
# 3. Blockchain Audit Log Tests
# ============================================================================

def test_blockchain_validity():
    log = BlockchainAuditLog()
    assert len(log.chain) == 1
    assert log.chain[0].index == 0
    assert log.chain[0].prev_hash == GENESIS_PREV_HASH

    # Append 3 records
    for i in range(1, 4):
        log.append_record(f"EVID-BC-{i}", 1700000000.0 + i * 10, {"event_index": i, "status": "SECURE"})

    assert len(log.chain) == 4
    is_valid, msg, err_idx = log.verify_chain()
    assert is_valid is True, f"Valid chain failed verification: {msg}"
    assert err_idx is None


def test_blockchain_payload_tamper_detected():
    log = BlockchainAuditLog()
    for i in range(1, 6):
        log.append_record(f"EVID-BC-{i}", 1700000000.0 + i, {"reading": i * 10})

    # Tamper payload of block index 3
    log.chain[3].payload["reading"] = 99999

    is_valid, msg, err_idx = log.verify_chain()
    assert is_valid is False
    assert err_idx == 3
    assert "Payload tampering at block 3" in msg


def test_blockchain_broken_link_detected():
    log = BlockchainAuditLog()
    for i in range(1, 5):
        log.append_record(f"EVID-BC-{i}", 1700000000.0 + i, {"step": i})

    # Break hash link at block 2
    log.chain[2].prev_hash = "f" * 64

    is_valid, msg, err_idx = log.verify_chain()
    assert is_valid is False
    assert err_idx == 2
    assert "Broken cryptographic link at block 2" in msg


def test_blockchain_deletion_detected():
    log = BlockchainAuditLog()
    for i in range(1, 6):
        log.append_record(f"EVID-BC-{i}", 1700000000.0 + i, {"val": i})

    # Delete block at index 2
    del log.chain[2]

    is_valid, msg, err_idx = log.verify_chain()
    assert is_valid is False
    # Sequence error or broken link detected at index 2
    assert err_idx == 2


def test_blockchain_insertion_detected():
    log = BlockchainAuditLog()
    for i in range(1, 5):
        log.append_record(f"EVID-BC-{i}", 1700000000.0 + i, {"val": i})

    # Insert an illicit block at index 2
    fake_block = copy.deepcopy(log.chain[2])
    fake_block.evidence_id = "ILLICIT_INJECTION"
    log.chain.insert(2, fake_block)

    is_valid, msg, err_idx = log.verify_chain()
    assert is_valid is False
    assert err_idx is not None


def test_blockchain_reordering_detected():
    log = BlockchainAuditLog()
    for i in range(1, 5):
        log.append_record(f"EVID-BC-{i}", 1700000000.0 + i, {"val": i})

    # Swap block 2 and block 3
    log.chain[2], log.chain[3] = log.chain[3], log.chain[2]

    is_valid, msg, err_idx = log.verify_chain()
    assert is_valid is False
    assert err_idx == 2


def test_blockchain_rewrite_limitation_demonstrated():
    """
    Demonstrates the fundamental limitation: If an attacker has write access
    to local storage and recomputes all block hashes from the point of tamper to the tip,
    a local hash chain without external anchoring will verify as valid.
    """
    log = BlockchainAuditLog()
    for i in range(1, 5):
        log.append_record(f"EVID-BC-{i}", 1700000000.0 + i, {"action": "BLOCK"})

    # Attacker rewrites block 2 payload
    log.chain[2].payload["action"] = "ALLOW"
    canonical = log.chain[2].serialized_payload()
    import hashlib
    log.chain[2].payload_hash = hashlib.sha256(canonical).hexdigest()
    log.chain[2].block_hash = log.chain[2].calculate_header_hash()

    # Attacker ripples the hash recalculation forward to block 3 and block 4
    for j in range(3, len(log.chain)):
        log.chain[j].prev_hash = log.chain[j - 1].block_hash
        log.chain[j].block_hash = log.chain[j].calculate_header_hash()

    # The rewritten chain now passes local-only verification!
    is_valid, _, _ = log.verify_chain()
    assert is_valid is True, "Limitation verified: local hash chain without external anchor can be rewritten"
