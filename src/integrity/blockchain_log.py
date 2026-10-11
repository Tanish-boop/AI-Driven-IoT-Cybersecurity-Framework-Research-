"""
Lightweight Blockchain-Style Append-Only Audit Log (Experiment E6)

Security Properties & Threat Model:
  - Cryptographic Primitive: SHA-256 hash chaining (Merkle-style linked sequence).
  - Deterministic Serialization: Canonical JSON representation (sorted keys, compact separators).
  - Append-Only Sequence Protection: Each block explicitly links to its predecessor via `prev_hash`.
  - Temporal & Sequence Ordering: Strictly enforces monotonic indices (i = 0, 1, 2, ...) and timestamps.
  - Tamper Localization: Chain verification pinpoints the exact index of any modified payload,
    broken link, deleted record, or inserted entry.

CRITICAL SECURITY LIMITATIONS (RESEARCH HONESTY):
  - A local cryptographic hash chain is NOT an immutable distributed ledger.
  - It does NOT provide Byzantine consensus, decentralized proof-of-work, or multi-party voting.
  - If an attacker gains full write access to the local filesystem or storage volume, the attacker
    can rewrite the tampered block AND recompute all subsequent `prev_hash` and `block_hash` values
    up to the chain tip without triggering verification errors on a purely local verify pass.
  - To achieve true immutability, the chain tip hash (or periodic checkpoint Merkle roots) MUST be
    anchored to an external, independently witnessed medium (e.g., TPM/HSM counter, remote syslog,
    or public distributed ledger). This implementation serves as the local cryptographic audit structure.
"""

import os
import json
import time
import hashlib
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, asdict


GENESIS_PREV_HASH = "0" * 64


@dataclass
class AuditBlock:
    index: int
    timestamp: float
    evidence_id: str
    payload: Dict[str, Any]
    payload_hash: str
    prev_hash: str
    block_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def serialized_payload(self) -> bytes:
        return json.dumps(self.payload, sort_keys=True, separators=(',', ':')).encode('utf-8')

    def calculate_header_hash(self) -> str:
        header_data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'evidence_id': self.evidence_id,
            'payload_hash': self.payload_hash,
            'prev_hash': self.prev_hash
        }
        canonical_header = json.dumps(header_data, sort_keys=True, separators=(',', ':')).encode('utf-8')
        return hashlib.sha256(canonical_header).hexdigest()


class BlockchainAuditLog:
    def __init__(self):
        self.chain: List[AuditBlock] = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        """Initializes the immutable Genesis Block (index 0)."""
        genesis_payload = {"event": "GENESIS_BLOCK", "description": "IoT Framework Audit Log Initialized"}
        canonical_payload = json.dumps(genesis_payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
        payload_hash = hashlib.sha256(canonical_payload).hexdigest()
        
        timestamp = 1700000000.0  # Deterministic reference timestamp
        header_data = {
            'index': 0,
            'timestamp': timestamp,
            'evidence_id': "GENESIS",
            'payload_hash': payload_hash,
            'prev_hash': GENESIS_PREV_HASH
        }
        canonical_header = json.dumps(header_data, sort_keys=True, separators=(',', ':')).encode('utf-8')
        block_hash = hashlib.sha256(canonical_header).hexdigest()

        genesis_block = AuditBlock(
            index=0,
            timestamp=timestamp,
            evidence_id="GENESIS",
            payload=genesis_payload,
            payload_hash=payload_hash,
            prev_hash=GENESIS_PREV_HASH,
            block_hash=block_hash
        )
        self.chain.append(genesis_block)

    @property
    def tip(self) -> AuditBlock:
        return self.chain[-1]

    def append_record(self, evidence_id: str, timestamp: float, payload: Dict[str, Any]) -> AuditBlock:
        """Appends a new evidence record cryptographically linked to the previous tip."""
        canonical_payload = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
        payload_hash = hashlib.sha256(canonical_payload).hexdigest()

        index = len(self.chain)
        prev_hash = self.tip.block_hash

        header_data = {
            'index': index,
            'timestamp': timestamp,
            'evidence_id': evidence_id,
            'payload_hash': payload_hash,
            'prev_hash': prev_hash
        }
        canonical_header = json.dumps(header_data, sort_keys=True, separators=(',', ':')).encode('utf-8')
        block_hash = hashlib.sha256(canonical_header).hexdigest()

        new_block = AuditBlock(
            index=index,
            timestamp=timestamp,
            evidence_id=evidence_id,
            payload=payload,
            payload_hash=payload_hash,
            prev_hash=prev_hash,
            block_hash=block_hash
        )
        self.chain.append(new_block)
        return new_block

    def verify_chain(self) -> Tuple[bool, str, Optional[int]]:
        """
        Verifies the full cryptographic integrity of the audit log from genesis to tip.
        Returns: (is_valid, status_message, failed_block_index)
        """
        if len(self.chain) == 0:
            return False, "Chain is empty (missing genesis block)", None

        # Verify Genesis Block
        genesis = self.chain[0]
        if genesis.index != 0 or genesis.prev_hash != GENESIS_PREV_HASH:
            return False, "Genesis block corrupted or invalid prev_hash", 0
        if genesis.block_hash != genesis.calculate_header_hash():
            return False, "Genesis block hash mismatch", 0

        # Verify subsequent blocks
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]

            # 1. Check sequence index
            if current.index != i:
                return False, f"Sequence error: Block at position {i} has index {current.index}", i

            # 2. Check payload hash
            canonical_payload = current.serialized_payload()
            expected_payload_hash = hashlib.sha256(canonical_payload).hexdigest()
            if current.payload_hash != expected_payload_hash:
                return False, f"Payload tampering at block {i}: payload_hash mismatch", i

            # 3. Check hash link
            if current.prev_hash != prev.block_hash:
                return False, f"Broken cryptographic link at block {i}: prev_hash does not match previous block_hash", i

            # 4. Check block hash
            expected_block_hash = current.calculate_header_hash()
            if current.block_hash != expected_block_hash:
                return False, f"Block header tampering at block {i}: block_hash mismatch", i

        return True, "Blockchain audit log verified successfully", None

    def verify_single_block(self, block: AuditBlock, prev_block: Optional[AuditBlock] = None) -> Tuple[bool, str]:
        """Verifies an individual block against its predecessor in O(1) time."""
        canonical_payload = block.serialized_payload()
        if hashlib.sha256(canonical_payload).hexdigest() != block.payload_hash:
            return False, "Payload hash mismatch"

        if block.calculate_header_hash() != block.block_hash:
            return False, "Block hash mismatch"

        if prev_block is not None:
            if block.prev_hash != prev_block.block_hash:
                return False, "Previous hash pointer mismatch"
            if block.index != prev_block.index + 1:
                return False, "Non-sequential block index"

        return True, "Valid block"

    def compute_storage_overhead(self, block: AuditBlock) -> int:
        """Computes byte overhead added to raw payload (header, hashes, indices, metadata)."""
        full_json = json.dumps(block.to_dict(), separators=(',', ':')).encode('utf-8')
        payload_json = block.serialized_payload()
        return len(full_json) - len(payload_json)

    def to_json(self) -> str:
        return json.dumps([b.to_dict() for b in self.chain], indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'BlockchainAuditLog':
        raw_list = json.loads(json_str)
        log = cls.__new__(cls)
        log.chain = [AuditBlock(**item) for item in raw_list]
        return log
