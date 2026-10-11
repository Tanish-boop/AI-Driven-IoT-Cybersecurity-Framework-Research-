"""
Integrity Verification Package (Experiment E6)
Provides:
  - Salted SHA-256 unkeyed integrity verification
  - HMAC-SHA-256 secret-key authenticated integrity verification
  - Lightweight blockchain-style append-only cryptographic audit log
"""

from .salted_sha256 import SaltedSHA256Verifier, SaltedEvidenceRecord
from .hmac_sha256 import HMACSHA256Verifier, HMACEvidenceRecord
from .blockchain_log import BlockchainAuditLog, AuditBlock

__all__ = [
    'SaltedSHA256Verifier',
    'SaltedEvidenceRecord',
    'HMACSHA256Verifier',
    'HMACEvidenceRecord',
    'BlockchainAuditLog',
    'AuditBlock'
]
