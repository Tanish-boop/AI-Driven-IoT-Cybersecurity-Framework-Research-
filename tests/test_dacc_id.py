"""
Unit and Integration Tests for DACC-ID:
Drift-Aware Contextual Cybersecurity Incident Detection & Correlation Framework.

Validates:
1. HybridDetector: Supervised + Unsupervised score fusion and component bounds.
2. ADWINDriftDetector: Drift detection under synthetic distribution shift.
3. DriftAdaptiveController: Truncation-bias corrected adaptive thresholding and streak freeze.
4. TemporalIncidentCorrelator: NetworkX graph correlation and Alert Reduction Rate (ARR).
5. ContextualRiskScorer: 4-factor risk score calculation and priority tier sorting.
6. IncidentIQEngine: MITRE ATT&CK mapping and deterministic SHA-256 evidence integrity hashing.
"""

import math
import numpy as np
import pytest

from src.detection.hybrid_detector import HybridDetector
from src.drift.drift_detector import ADWINDriftDetector, DriftAdaptiveController
from src.correlation.incident_correlator import (
    SecurityEvent,
    CorrelatedIncident,
    TemporalIncidentCorrelator,
    MITRE_ATTACK_MAPPING
)
from src.correlation.contextual_risk import ContextualRiskScorer, SERVICE_CRITICALITY, ATTACK_SEVERITY_IMPACT
from src.correlation.incident_iq import IncidentIQEngine


class TestHybridDetector:
    def test_hybrid_detector_fit_and_predict(self):
        np.random.seed(42)
        # Synthetic data: 500 samples, 10 features
        X_sup = np.random.randn(200, 10)
        y_sup = (X_sup[:, 0] > 0).astype(int)
        X_unsup = np.random.randn(200, 10)
        X_val = np.random.randn(100, 10)
        y_val = (X_val[:, 0] > 0).astype(int)

        detector = HybridDetector(n_estimators_rf=20, max_depth_rf=5, n_estimators_if=20, random_state=42)
        detector.fit(X_sup, y_sup, X_unsup, X_val, y_val)

        assert detector.is_fitted
        assert 0.0 <= detector.alpha <= 1.0

        X_test = np.random.randn(50, 10)
        comps = detector.predict_components(X_test)
        assert 'p_sup' in comps and 'a_unsup' in comps and 's_fused' in comps
        assert comps['p_sup'].shape == (50,)
        assert np.all((comps['p_sup'] >= 0.0) & (comps['p_sup'] <= 1.0))
        assert np.all((comps['a_unsup'] >= 0.0) & (comps['a_unsup'] <= 1.0))
        assert np.all((comps['s_fused'] >= 0.0) & (comps['s_fused'] <= 1.0))

        preds = detector.predict(X_test)
        assert preds.shape == (50,)
        assert set(preds).issubset({0, 1})


class TestDriftDetector:
    def test_adwin_detects_distribution_shift(self):
        detector = ADWINDriftDetector(delta=0.01, min_subwindow_size=20)
        np.random.seed(42)
        # Stationary stream
        stat_stream = np.random.normal(loc=0.1, scale=0.02, size=300)
        # Shifted stream
        shift_stream = np.random.normal(loc=0.9, scale=0.02, size=300)

        drifts = []
        for t, x in enumerate(np.concatenate([stat_stream, shift_stream])):
            if detector.add_element(x):
                drifts.append(t)

        # Drift must be detected after step 300
        assert len(drifts) > 0
        assert any(t >= 300 for t in drifts)

    def test_drift_adaptive_controller_streak_freeze(self):
        controller = DriftAdaptiveController(tau_calib=0.50, freeze_streak=3, cooldown_needed=5)
        # Simulate attack flood with 10 high-score samples
        attack_scores = [0.95] * 10
        frozen_states = []
        for s in attack_scores:
            _, _, meta = controller.process_score(s)
            frozen_states.append(meta['frozen'])

        # Controller must freeze after streak >= 3
        assert frozen_states[0] is False
        assert frozen_states[1] is False
        assert frozen_states[2] is True
        assert all(frozen_states[3:])

        # Simulate recovery
        recovery_scores = [0.10] * 6
        for s in recovery_scores:
            _, _, meta = controller.process_score(s)

        # After cooldown_needed benign samples, freeze is lifted
        assert controller.frozen is False


class TestIncidentCorrelation:
    def test_temporal_incident_correlator_grouping_and_arr(self):
        correlator = TemporalIncidentCorrelator(window_seconds=30.0, enable_causal_chains=True)

        events = [
            SecurityEvent(event_id='E1', timestamp=5.0, device_id='Dev-A', dst_ip='10.0.0.1', service='HTTP', detection_score=0.8, attack_class='Recon', attack_subclass='PortScan'),
            SecurityEvent(event_id='E2', timestamp=10.0, device_id='Dev-A', dst_ip='10.0.0.1', service='HTTP', detection_score=0.9, attack_class='BruteForce', attack_subclass='Dict'),
            SecurityEvent(event_id='E3', timestamp=15.0, device_id='Dev-A', dst_ip='10.0.0.1', service='HTTP', detection_score=0.95, attack_class='DoS', attack_subclass='SYNFlood'),
            SecurityEvent(event_id='E4', timestamp=200.0, device_id='Dev-B', dst_ip='10.0.0.2', service='DNS', detection_score=0.7, attack_class='Benign', attack_subclass='Normal')
        ]

        incidents = correlator.correlate_alerts(events)
        assert len(incidents) == 2

        # Incident 1 groups E1, E2, E3
        inc1 = incidents[0]
        assert inc1.event_count == 3
        assert inc1.is_multistage is True
        assert 'Recon' in inc1.attack_classes and 'DoS' in inc1.attack_classes

        # Alert reduction rate: (4 - 2) / 4 = 50%
        arr = correlator.compute_alert_reduction_rate(4, 2)
        assert math.isclose(arr, 50.0)


class TestContextualRiskAndIncidentIQ:
    def test_contextual_risk_prioritization(self):
        scorer = ContextualRiskScorer()
        e_crit = [
            SecurityEvent(event_id='E1', timestamp=1.0, device_id='Core-GW', dst_ip='10.0.0.1', service='DNS', detection_score=0.95, attack_class='DDoS', attack_subclass='DNSFlood'),
            SecurityEvent(event_id='E2', timestamp=2.0, device_id='Core-GW', dst_ip='10.0.0.1', service='DNS', detection_score=0.98, attack_class='DDoS', attack_subclass='DNSFlood')
        ]
        inc_crit = CorrelatedIncident(incident_id='INC-01', events=e_crit)
        inc_crit.compile_summary()

        e_low = [
            SecurityEvent(event_id='E3', timestamp=1.0, device_id='IoT-Sensor', dst_ip='10.0.0.99', service='Generic', detection_score=0.45, attack_class='Benign', attack_subclass='Normal')
        ]
        inc_low = CorrelatedIncident(incident_id='INC-02', events=e_low)
        inc_low.compile_summary()

        prioritized = scorer.prioritize_incidents([inc_low, inc_crit])
        # Higher risk incident must be sorted first
        assert prioritized[0].incident_id == 'INC-01'
        assert prioritized[0].contextual_risk_score > prioritized[1].contextual_risk_score

    def test_incident_iq_sha256_evidence_integrity(self):
        iq = IncidentIQEngine()
        events = [
            SecurityEvent(event_id='E1', timestamp=1.0, device_id='D1', dst_ip='10.0.0.1', service='SSH', detection_score=0.9, attack_class='BruteForce', attack_subclass='SSH-BF')
        ]
        inc = CorrelatedIncident(incident_id='INC-TEST', events=events)
        inc.compile_summary()

        dossier1 = iq.generate_dossier(inc)
        h1 = dossier1['evidence_sha256']
        assert len(h1) == 64  # Valid SHA-256 hex string

        # Deterministic check
        h2 = iq.compute_evidence_hash(inc)
        assert h1 == h2
        assert 'mitre_tactics' in dossier1
        assert 'recommended_action' in dossier1
