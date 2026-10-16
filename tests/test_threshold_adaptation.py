"""
Unit Tests for Adaptive Thresholding Strategies:
FixedThreshold, UnGuardedAdaptiveThreshold, ExcludedAdaptiveThreshold, GuardedAdaptiveThreshold,
and ContaminationGatedAdaptiveThreshold (CGB-Adaptive).
"""

import unittest
import numpy as np
from src.thresholding.threshold_methods import (
    FixedThreshold,
    UnGuardedAdaptiveThreshold,
    ExcludedAdaptiveThreshold,
    GuardedAdaptiveThreshold,
    ContaminationGatedAdaptiveThreshold
)

class TestThresholdMethods(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        # 1000 normal validation errors (mean 0.05, std 0.02)
        self.val_errors = np.abs(np.random.normal(0.05, 0.02, 1000))
        # 2000 test errors: 1000 benign + 1000 attack flood (errors ~ 10.0)
        benign_test = np.abs(np.random.normal(0.05, 0.02, 1000))
        attack_test = np.random.normal(10.0, 1.0, 1000)
        self.test_errors = np.concatenate([benign_test, attack_test])
        self.y_true = np.concatenate([np.zeros(1000, dtype=int), np.ones(1000, dtype=int)])

    def test_fixed_threshold(self):
        ft = FixedThreshold(percentile=95)
        tau = ft.fit(self.val_errors)
        self.assertGreater(tau, 0.0)
        preds, taus = ft.predict(self.test_errors)
        self.assertEqual(len(preds), len(self.test_errors))
        # Should detect almost all attack samples
        attack_detected = np.sum(preds[1000:] == 1)
        self.assertGreaterEqual(attack_detected, 950)

    def test_unguarded_collapse(self):
        """UnGuarded EWMA should absorb attack errors and suffer severe recall drop."""
        ug = UnGuardedAdaptiveThreshold(alpha=0.05, k=2.5)
        preds, taus = ug.evaluate_stream(self.val_errors, self.test_errors)
        # Because attacks are high, threshold inflates rapidly and later attacks are missed
        late_attacks_detected = np.sum(preds[1800:] == 1)
        self.assertLess(late_attacks_detected, 100) # collapsed

    def test_contamination_gated_threshold(self):
        """CGB-Adaptive controller must resist attack flood and detect attacks without collapse."""
        cgb = ContaminationGatedAdaptiveThreshold(alpha=0.01, k=2.5, buffer_margin=0.85, cooldown=10, max_alert_rate=0.08)
        preds, taus = cgb.evaluate_stream(self.val_errors, self.test_errors)
        self.assertEqual(len(preds), len(self.test_errors))

        # Check attack detection rate
        attack_detected = np.sum(preds[1000:] == 1)
        self.assertGreaterEqual(attack_detected, 950, "CGB controller must not collapse under attack flood")

        # Check false positive rate on benign samples
        false_positives = np.sum(preds[:1000] == 1)
        fpr = false_positives / 1000.0
        self.assertLess(fpr, 0.12, "CGB controller must keep false positive rate bounded")

    def test_cgb_bounded_step_movement(self):
        """Verify that per-step movement is bounded by max_delta."""
        max_delta = 0.005
        cgb = ContaminationGatedAdaptiveThreshold(max_delta=max_delta)
        preds, taus = cgb.evaluate_stream(self.val_errors, self.test_errors[:500])
        step_diffs = np.abs(np.diff(taus))
        # Allow tiny epsilon for numerical precision
        self.assertTrue(np.all(step_diffs <= max_delta + 1e-6))

if __name__ == '__main__':
    unittest.main()
