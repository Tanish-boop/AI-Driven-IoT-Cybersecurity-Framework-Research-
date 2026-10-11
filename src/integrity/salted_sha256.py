"""
Salted SHA-256 Integrity Verification (Experiment E6)

Security Properties & Threat Model:
  - Cryptographic Primitive: Unkeyed SHA-256 hash function (FIPS 180-4).
  - Per-Record Salt: Cryptographically secure random 16-byte salt (os.urandom).
    The salt prevents pre-computation / rainbow-table attacks on low-entropy evidence payloads.
  - Deterministic Serialization: Canonical JSON representation (sorted keys, compact separators).

SECURITY LIMITATIONS (CRITICAL):
  - Salted SHA-256 is an UNKEYED cryptographic digest.
  - It does NOT provide message authentication or proof of origin against an active adversary.
  - Any attacker with write access to evidence storage can modify the evidence payload,
    re-calculate SHA-256(salt || tampered_payload), and update the stored digest without detection.
  - It is only effective for detecting accidental data corruption or transmission errors when
    the digest is transmitted or stored via a pre-trusted, out-of-band read-only channel.
"""

import os
import json
import hashlib
from typing import Dict, Any, Tuple
from dataclasses import dataclass, asdict


@dataclass
class SaltedEvidenceRecord:
    evidence_id: str
    timestamp: float
    payload: Dict[str, Any]
    salt_hex: str
    digest_hex: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def serialized_payload(self) -> bytes:
        return json.dumps(self.payload, sort_keys=True, separators=(',', ':')).encode('utf-8')


class SaltedSHA256Verifier:
    def __init__(self, salt_bytes: int = 16):
        self.salt_bytes = salt_bytes

    def create_record(self, evidence_id: str, timestamp: float, payload: Dict[str, Any]) -> SaltedEvidenceRecord:
        salt = os.urandom(self.salt_bytes)
        salt_hex = salt.hex()
        
        canonical_bytes = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
        
        hasher = hashlib.sha256()
        hasher.update(salt)
        hasher.update(canonical_bytes)
        digest_hex = hasher.hexdigest()

        return SaltedEvidenceRecord(
            evidence_id=evidence_id,
            timestamp=timestamp,
            payload=payload,
            salt_hex=salt_hex,
            digest_hex=digest_hex
        )

    def verify_record(self, record: SaltedEvidenceRecord) -> Tuple[bool, str]:
        try:
            salt = bytes.fromhex(record.salt_hex)
        except ValueError:
            return False, "Invalid salt hexadecimal encoding"

        canonical_bytes = record.serialized_payload()
        
        hasher = hashlib.sha256()
        hasher.update(salt)
        hasher.update(canonical_bytes)
        expected_digest = hasher.hexdigest()

        if expected_digest == record.digest_hex:
            return True, "Valid integrity digest"
        else:
            return False, f"Digest mismatch: expected {expected_digest}, found {record.digest_hex}"

    def compute_storage_overhead(self, record: SaltedEvidenceRecord) -> int:
        """Computes byte overhead added to raw payload (salt + digest + ID + timestamp metadata)."""
        full_json = json.dumps(record.to_dict(), separators=(',', ':')).encode('utf-8')
        payload_json = record.serialized_payload()
        return len(full_json) - len(payload_json)
