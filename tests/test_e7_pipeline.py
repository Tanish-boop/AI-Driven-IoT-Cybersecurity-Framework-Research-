"""
Unit Tests for Experiment E7: Integrated Pipeline and Ablation Framework
Verifies:
  - Framework configuration instantiation
  - End-to-end flow event processing across all component layers
  - PQC session encryption behavior
  - Blockchain audit log chain integrity integration
  - Ablation variant execution correctness
"""

import numpy as np
import torch
import pytest

from src.detection.autoencoders import DenseAutoencoder
from src.pipeline.integrated_framework import FrameworkConfig, IntegratedPipeline, PipelineEventResult


@pytest.fixture
def mock_model():
    model = DenseAutoencoder(input_dim=39, hidden_dims=[64, 32, 16])
    return model


def test_pipeline_baseline_run(mock_model):
    cfg = FrameworkConfig(
        name="Baseline_Variant",
        threshold_type="fixed_95",
        mitigation_type="rule_based",
        pqc_type="none",
        integrity_type="salted_sha256"
    )
    pipeline = IntegratedPipeline(cfg, mock_model)
    
    x = np.random.randn(39).astype(np.float32)
    res = pipeline.process_event(x, y_label=1, timestep=1)

    assert isinstance(res, PipelineEventResult)
    assert res.timestep == 1
    assert res.action_taken in [0, 1, 2, 3]
    assert res.latency_ms > 0
    assert res.integrity_overhead_bytes > 0


def test_pipeline_full_proposed_run(mock_model):
    cfg = FrameworkConfig(
        name="Full_Proposed_Framework",
        threshold_type="excluded_ewma",
        mitigation_type="rule_based",
        pqc_type="ml_kem_768",
        integrity_type="blockchain_log"
    )
    pipeline = IntegratedPipeline(cfg, mock_model)
    
    assert pipeline.session_key is not None
    assert len(pipeline.session_key) == 32
    assert len(pipeline.blockchain_log.chain) == 1 # Genesis

    x = np.random.randn(39).astype(np.float32)
    for t in range(1, 5):
        res = pipeline.process_event(x, y_label=0, timestep=t)
        assert res.integrity_overhead_bytes > 0

    assert len(pipeline.blockchain_log.chain) == 5
    is_valid, msg, _ = pipeline.blockchain_log.verify_chain()
    assert is_valid is True, f"Integrated blockchain audit log verification failed: {msg}"


def test_all_ablation_variants_functional(mock_model):
    variants = [
        FrameworkConfig("Base_Paper_Baseline", "fixed_95", "rule_based", "none", "salted_sha256"),
        FrameworkConfig("Ablation_NoAdaptive", "fixed_95", "rule_based", "ml_kem_768", "blockchain_log"),
        FrameworkConfig("Ablation_NoPQC", "excluded_ewma", "rule_based", "none", "blockchain_log"),
        FrameworkConfig("Ablation_NoBlockchain", "excluded_ewma", "rule_based", "ml_kem_768", "hmac_sha256"),
        FrameworkConfig("Full_Proposed_Framework", "excluded_ewma", "rule_based", "ml_kem_768", "blockchain_log")
    ]

    x = np.random.randn(39).astype(np.float32)

    for cfg in variants:
        pipe = IntegratedPipeline(cfg, mock_model)
        res = pipe.process_event(x, y_label=1, timestep=1)
        assert res.latency_ms > 0
        assert res.action_taken in [0, 1, 2, 3]
