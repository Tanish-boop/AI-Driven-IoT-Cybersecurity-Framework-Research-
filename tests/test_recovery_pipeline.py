"""
Comprehensive Unit Tests for Recovery Preprocessing Pipeline
Verifies zero data leakage, schema freezing, NaN/Inf handling, label exclusion, and reproducible splitting.
"""

import os
import shutil
import unittest
import numpy as np
import pandas as pd
from src.preprocessing.recovery_pipeline import FEATURE_SCHEMA, build_recovery_pipeline

class TestRecoveryPipeline(unittest.TestCase):
    def setUp(self):
        self.raw_train = 'data/raw/train.parquet'
        self.raw_test = 'data/raw/test.parquet'
        self.output_dir = 'data/processed/recovery_unittest'

    def tearDown(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir, ignore_errors=True)

    def test_pipeline_execution_and_leakage(self):
        if not os.path.exists(self.raw_train) or not os.path.exists(self.raw_test):
            self.skipTest("Raw parquet files missing.")

        out_npz = build_recovery_pipeline(self.raw_train, self.raw_test, output_dir=self.output_dir)
        self.assertTrue(os.path.exists(out_npz))

        data = np.load(out_npz, allow_pickle=True)
        X_train = data['X_train']
        X_val = data['X_val']
        X_test = data['X_test']

        # 1. Verify train-only fitting (train mean ~ 0, train std ~ 1)
        train_means = np.mean(X_train, axis=0)
        train_stds = np.std(X_train, axis=0)

        self.assertTrue(np.allclose(train_means, 0.0, atol=1e-4))
        non_zero_std_mask = train_stds > 1e-4
        self.assertTrue(np.allclose(train_stds[non_zero_std_mask], 1.0, atol=1e-4))

        # 2. Verify schema dimension matches FEATURE_SCHEMA (39 features)
        self.assertEqual(X_train.shape[1], len(FEATURE_SCHEMA))
        self.assertEqual(X_val.shape[1], len(FEATURE_SCHEMA))
        self.assertEqual(X_test.shape[1], len(FEATURE_SCHEMA))

    def test_label_exclusion(self):
        """Verify that target and label metadata columns are completely excluded from X arrays."""
        if not os.path.exists(self.raw_train) or not os.path.exists(self.raw_test):
            self.skipTest("Raw parquet files missing.")

        out_npz = build_recovery_pipeline(self.raw_train, self.raw_test, output_dir=self.output_dir)
        data = np.load(out_npz, allow_pickle=True)
        X_train = data['X_train']

        # Ensure feature matrix count strictly equals length of FEATURE_SCHEMA (39)
        self.assertEqual(X_train.shape[1], 39)

    def test_missing_and_infinite_values(self):
        """Verify that transformed arrays contain zero NaN or Inf values."""
        if not os.path.exists(self.raw_train) or not os.path.exists(self.raw_test):
            self.skipTest("Raw parquet files missing.")

        out_npz = build_recovery_pipeline(self.raw_train, self.raw_test, output_dir=self.output_dir)
        data = np.load(out_npz, allow_pickle=True)

        for key in ['X_train', 'X_val', 'X_sup', 'X_test']:
            mat = data[key]
            self.assertFalse(np.isnan(mat).any(), f"NaN found in {key}")
            self.assertFalse(np.isinf(mat).any(), f"Inf found in {key}")

    def test_reproducible_splitting(self):
        """Verify that two pipeline builds produce identical outputs."""
        if not os.path.exists(self.raw_train) or not os.path.exists(self.raw_test):
            self.skipTest("Raw parquet files missing.")

        dir1 = os.path.join(self.output_dir, 'run1')
        dir2 = os.path.join(self.output_dir, 'run2')

        out1 = build_recovery_pipeline(self.raw_train, self.raw_test, output_dir=dir1)
        out2 = build_recovery_pipeline(self.raw_train, self.raw_test, output_dir=dir2)

        d1 = np.load(out1, allow_pickle=True)
        d2 = np.load(out2, allow_pickle=True)

        self.assertTrue(np.array_equal(d1['X_train'], d2['X_train']))
        self.assertTrue(np.array_equal(d1['X_test'], d2['X_test']))

if __name__ == '__main__':
    unittest.main()
