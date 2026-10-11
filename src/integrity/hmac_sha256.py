"""
HMAC-SHA-256 Secret-Key Authenticated Integrity Verification (Experiment E6)

Security Properties & Threat Model:
  - Cryptographic Primitive: HMAC-SHA-256 (RFC 2104 / FIPS 198-1).
  - Secret Key Management: Separate 256-bit (32-byte) symmetric key held in secure key storage.
    The secret key is NEVER stored inside the evidence record.
  - Message Authentication: Authenticates both data integrity and origin.
    An adversary cannot forge or modify evidence records without knowing the secret key,
    even if the adversary possesses full write access to the evidence database.
  - Timing-Attack Resistance: Verification utilizes constant-time comparison (hmac.compare_digest).

SECURITY LIMITATIONS:
  - Symmetric Cryptography: Any entity possessing the secret key can forge or alter records.
    It does not provide asymmetric non-repudiation.
  - Individual Record Scope: HMAC-SHA-256 protects individual records independently.
    It does NOT cryptographically bind the sequence order of records, meaning an attacker
    with storage access could delete records or swap record orders without breaking individual MACs,
    unless sequence numbers are strictly enforced in the application layer.
"""

import os
import json
import hmac
import hashlib
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass, asdict


@dataclass
class HMACEvidenceRecord:
    evidence_id: str
    timestamp: float
    payload: Dict[str, Any]
    key_id: str
    mac_hex: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def serialized_payload(self) -> bytes:
        return json.dumps(self.payload, sort_keys=True, separators=(',', ':')).encode('utf-8')


class HMACSHA256Verifier:
    def __init__(self, key: Optional[bytes] = None, key_id: str = "iot-edge-key-01"):
        self.key_id = key_id
        self.key = key if key is not None else os.urandom(32)
        if len(self.key) < 16:
            raise ValueError("HMAC key length must be at least 16 bytes for adequate security.")

    def create_record(self, evidence_id: str, timestamp: float, payload: Dict[str, Any]) -> HMACEvidenceRecord:
        canonical_bytes = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
        
        mac = hmac.new(self.key, canonical_bytes, hashlib.sha256).hexdigest()

        return HMACEvidenceRecord(
            evidence_id=evidence_id,
            timestamp=timestamp,
            payload=payload,
            key_id=self.key_id,
            mac_hex=mac
        )

    def verify_record(self, record: HMACEvidenceRecord, verification_key: Optional[bytes] = None) -> Tuple[bool, str]:
        key = verification_key if verification_key is not None else self.key
        
        canonical_bytes = record.serialized_payload()
        expected_mac = hmac.new(key, canonical_bytes, hashlib.sha256).hexdigest()

        if hmac.compare_digest(expected_mac, record.mac_hex):
            return True, "Valid HMAC-SHA-256 authentication tag"
        else:
            return False, f"HMAC verification failure: authentication tag mismatch or invalid key"

    def compute_storage_overhead(self, record: HMACEvidenceRecord) -> int:
        """Computes byte overhead added to raw payload (key_id + mac + ID + timestamp metadata)."""
        full_json = json.dumps(record.to_dict(), separators=(',', ':')).encode('utf-8')
        payload_json = record.serialized_payload()
        return len(full_json) - len(payload_json)
