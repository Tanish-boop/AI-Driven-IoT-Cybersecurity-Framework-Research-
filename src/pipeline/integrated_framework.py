"""
Integrated Cybersecurity Framework Pipeline (Experiment E7)
End-to-End Orchestrator connecting:
  1. Deep Anomaly Detection (Dense Autoencoder)
  2. Threshold Adaptation (Fixed 95th vs Excluded EWMA)
  3. Reactive Mitigation Policy (Rule-Based vs Q-Learning vs DQN)
  4. Post-Quantum Encryption (Classical/None vs NIST FIPS 203 ML-KEM-768 + AES-256-GCM)
  5. Cryptographic Evidence Integrity (Salted SHA-256 vs HMAC-SHA-256 vs Blockchain Audit Log)
"""

import os
import time
import json
import numpy as np
import torch
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Tuple, Optional

from src.detection.autoencoders import DenseAutoencoder
from src.thresholding.threshold_methods import FixedThreshold, ExcludedAdaptiveThreshold
from src.response.policies import RuleBasedPolicy, QLearningPolicy, DQNPolicy
from src.crypto.ml_kem_benchmark import KEM_MAP
from src.integrity.salted_sha256 import SaltedSHA256Verifier
from src.integrity.hmac_sha256 import HMACSHA256Verifier
from src.integrity.blockchain_log import BlockchainAuditLog

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


@dataclass
class FrameworkConfig:
    name: str
    threshold_type: str        # 'fixed_95' | 'excluded_ewma'
    mitigation_type: str       # 'rule_based' | 'q_learning' | 'dqn'
    pqc_type: str              # 'none' | 'classical_aes' | 'ml_kem_768'
    integrity_type: str        # 'salted_sha256' | 'hmac_sha256' | 'blockchain_log'
    tau_fixed: float = 0.075   # Baseline fixed threshold
    ewma_alpha: float = 0.02
    ewma_k: float = 2.5
    val_mu: float = 0.898
    val_var: float = 3.097
    val_std: float = 1.760
    err_quantiles: list = None
    rate_quantiles: list = None


@dataclass
class PipelineEventResult:
    timestep: int
    reconstruction_error: float
    threshold: float
    is_anomaly: int
    action_taken: int          # 0: ALLOW, 1: ALERT, 2: RATE_LIMIT, 3: BLOCK
    latency_ms: float          # End-to-end event processing latency
    encrypted_bytes: int
    integrity_overhead_bytes: int
    is_attack_ground_truth: int
    was_attack_contained: bool
    was_benign_falsely_blocked: bool


class IntegratedPipeline:
    def __init__(self, config: FrameworkConfig, model: DenseAutoencoder, q_policy=None, dqn_policy=None):
        self.config = config
        self.model = model
        self.model.eval()

        # Policies
        self.rule_policy = RuleBasedPolicy(tau_threshold=config.tau_fixed)
        self.q_policy = q_policy
        self.dqn_policy = dqn_policy

        # Integrity Engines
        self.salted_verifier = SaltedSHA256Verifier()
        self.hmac_verifier = HMACSHA256Verifier()
        self.blockchain_log = BlockchainAuditLog()

        # PQC Session Setup (if enabled, establish shared session key)
        self.session_key = None
        if config.pqc_type == 'ml_kem_768':
            kem = KEM_MAP['ML-KEM-768']
            pk, sk = kem.keygen()
            ct, ss1 = kem.encaps(pk)
            ss2 = kem.decaps(sk, ct)
            hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=b'IoT-E7-Salt', info=b'IoT-E7-AEAD')
            self.session_key = hkdf.derive(ss1)
            self.aesgcm = AESGCM(self.session_key)
        elif config.pqc_type == 'classical_aes':
            self.session_key = os.urandom(32)
            self.aesgcm = AESGCM(self.session_key)
        else:
            self.session_key = None
            self.aesgcm = None

        # State tracking for EWMA
        self.ewma_mu = float(config.val_mu)
        self.ewma_var = float(config.val_var)
        self.ewma_std = float(config.val_std)
        self.alert_streak = 0

    def process_event(self, x_vec: np.ndarray, y_label: int, timestep: int) -> PipelineEventResult:
        """Processes a single telemetry/flow event through the full pipeline."""
        t0 = time.perf_counter()

        # 1. Anomaly Reconstruction Inference
        with torch.no_grad():
            x_tensor = torch.tensor(x_vec, dtype=torch.float32).unsqueeze(0)
            x_hat = self.model(x_tensor).squeeze(0).numpy()
            err_val = float(np.mean((x_vec - x_hat) ** 2))

        # 2. Threshold Evaluation
        if self.config.threshold_type == 'fixed_95':
            tau_t = self.config.tau_fixed
            is_anomaly = 1 if err_val > tau_t else 0
        elif self.config.threshold_type == 'excluded_ewma':
            tau_t = self.ewma_mu + self.config.ewma_k * self.ewma_std
            is_anomaly = 1 if err_val > tau_t else 0

            # Excluded EWMA: update ONLY if not an anomaly
            if is_anomaly == 0:
                self.ewma_mu = (1 - self.config.ewma_alpha) * self.ewma_mu + self.config.ewma_alpha * err_val
                self.ewma_var = (1 - self.config.ewma_alpha) * self.ewma_var + self.config.ewma_alpha * ((err_val - self.ewma_mu) ** 2)
                self.ewma_std = float(np.sqrt(max(self.ewma_var, 1e-8)))
        else:
            tau_t = self.config.tau_fixed
            is_anomaly = 1 if err_val > tau_t else 0

        # Update alert streak
        if is_anomaly == 1:
            self.alert_streak = min(self.alert_streak + 1, 3)
        else:
            self.alert_streak = 0

        # 3. Mitigation Decision
        rate_val = float(x_vec[3]) if len(x_vec) > 3 else 1.0
        
        if self.config.mitigation_type == 'rule_based':
            action = self.rule_policy.select_action(err_val, self.alert_streak)
        elif self.config.mitigation_type == 'q_learning' and self.q_policy is not None:
            if self.config.err_quantiles is not None and self.config.rate_quantiles is not None:
                err_bin = int(np.digitize(err_val, self.config.err_quantiles))
                rate_bin = int(np.digitize(rate_val, self.config.rate_quantiles))
            else:
                err_bin = min(int(err_val / 0.05), 3)
                rate_bin = min(int(max(0, rate_val) / 2.0), 3)
            alert_bin = min(self.alert_streak, 3)
            state_id = err_bin * 16 + rate_bin * 4 + alert_bin
            action = self.q_policy.select_action(state_id, evaluate=True)
        elif self.config.mitigation_type == 'dqn' and self.dqn_policy is not None:
            max_err = self.config.err_quantiles[-1] if self.config.err_quantiles is not None else 1.0
            max_rate = self.config.rate_quantiles[-1] if self.config.rate_quantiles is not None else 10.0
            continuous_vector = np.array([
                min(err_val / (max_err + 1e-5), 5.0),
                min(rate_val / (max_rate + 1e-5), 5.0),
                min(self.alert_streak, 3) / 3.0
            ], dtype=np.float32)
            action = self.dqn_policy.select_action(continuous_vector, evaluate=True)
        else:
            action = self.rule_policy.select_action(err_val, self.alert_streak)

        # 4. Cryptographic Encryption of Event Log/Packet
        evidence_payload = {
            'ts': timestep,
            'err': round(err_val, 4),
            'action': action,
            'anomaly': is_anomaly
        }
        canonical_bytes = json.dumps(evidence_payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
        
        if self.aesgcm is not None:
            nonce = os.urandom(12)
            ciphertext = self.aesgcm.encrypt(nonce, canonical_bytes, associated_data=b'IoT-E7-Header')
            encrypted_bytes = len(ciphertext) + 12
        else:
            encrypted_bytes = len(canonical_bytes)

        # 5. Integrity Verification / Audit Logging
        if self.config.integrity_type == 'salted_sha256':
            rec = self.salted_verifier.create_record(f"EVT-{timestep}", time.time(), evidence_payload)
            integrity_overhead = self.salted_verifier.compute_storage_overhead(rec)
        elif self.config.integrity_type == 'hmac_sha256':
            rec = self.hmac_verifier.create_record(f"EVT-{timestep}", time.time(), evidence_payload)
            integrity_overhead = self.hmac_verifier.compute_storage_overhead(rec)
        elif self.config.integrity_type == 'blockchain_log':
            block = self.blockchain_log.append_record(f"EVT-{timestep}", time.time(), evidence_payload)
            integrity_overhead = self.blockchain_log.compute_storage_overhead(block)
        else:
            integrity_overhead = 0

        t1 = time.perf_counter()
        total_latency_ms = (t1 - t0) * 1000.0

        # Outcome assessment
        # Attack contained if y_label == 1 and action in [2 (RATE_LIMIT), 3 (BLOCK)]
        was_attack_contained = (y_label == 1) and (action in [2, 3])
        # Benign falsely blocked if y_label == 0 and action == 3 (BLOCK)
        was_benign_falsely_blocked = (y_label == 0) and (action == 3)

        return PipelineEventResult(
            timestep=timestep,
            reconstruction_error=err_val,
            threshold=tau_t,
            is_anomaly=is_anomaly,
            action_taken=action,
            latency_ms=total_latency_ms,
            encrypted_bytes=encrypted_bytes,
            integrity_overhead_bytes=integrity_overhead,
            is_attack_ground_truth=y_label,
            was_attack_contained=was_attack_contained,
            was_benign_falsely_blocked=was_benign_falsely_blocked
        )
