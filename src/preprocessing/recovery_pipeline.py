"""
Recovery Preprocessing Pipeline & Leakage-Free Data Partitioning
Provides strict train-only fitting, reproducible index manifests, and schema freezing.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib

FEATURE_SCHEMA = [
    'Header_Length', 'Protocol Type', 'Time_To_Live', 'Rate',
    'fin_flag_number', 'syn_flag_number', 'rst_flag_number', 'psh_flag_number',
    'ack_flag_number', 'ece_flag_number', 'cwr_flag_number', 'ack_count',
    'syn_count', 'fin_count', 'rst_count', 'HTTP', 'HTTPS', 'DNS', 'Telnet',
    'SMTP', 'SSH', 'IRC', 'TCP', 'UDP', 'DHCP', 'ARP', 'ICMP', 'IGMP', 'IPv',
    'LLC', 'Tot sum', 'Min', 'Max', 'AVG', 'Std', 'Tot size', 'IAT', 'Number', 'Variance'
]

def build_recovery_pipeline(raw_train_path, raw_test_path, output_dir='data/processed/recovery'):
    os.makedirs(output_dir, exist_ok=True)

    df_train = pd.read_parquet(raw_train_path)
    df_test = pd.read_parquet(raw_test_path)

    # Verify frozen schema alignment
    missing_cols = [c for c in FEATURE_SCHEMA if c not in df_train.columns]
    if missing_cols:
        raise ValueError(f"Missing schema features in training data: {missing_cols}")

    # Separate Benign and Attack samples in df_train
    df_benign_train = df_train[df_train['Label'] == 'BenignTraffic'].copy()
    df_attack_train = df_train[df_train['Label'] != 'BenignTraffic'].copy()

    # Deterministic shuffling
    rng = np.random.RandomState(42)
    benign_shuffled = df_benign_train.sample(frac=1.0, random_state=rng).reset_index(drop=True)
    attack_shuffled = df_attack_train.sample(frac=1.0, random_state=rng).reset_index(drop=True)

    # 1. Unsupervised Training Split (100,000 pure Benign samples)
    train_benign_df = benign_shuffled.iloc[:100000].copy()
    val_benign_df = benign_shuffled.iloc[100000:130000].copy()
    remaining_benign = benign_shuffled.iloc[130000:].copy()

    # 2. Supervised Oracle Training Split (20k Benign + 20k Attack)
    sup_benign = remaining_benign.iloc[:20000]
    sup_attack = attack_shuffled.iloc[:20000]
    df_supervised = pd.concat([sup_benign, sup_attack]).sample(frac=1.0, random_state=rng).reset_index(drop=True)

    # 3. Test Partition (100,000 samples from df_test)
    df_test_sampled = df_test.sample(n=min(100000, len(df_test)), random_state=rng).reset_index(drop=True)

    # Extract feature matrices
    X_train_raw = train_benign_df[FEATURE_SCHEMA].values
    X_val_raw = val_benign_df[FEATURE_SCHEMA].values
    X_sup_raw = df_supervised[FEATURE_SCHEMA].values
    y_sup_train = (df_supervised['Label'] != 'BenignTraffic').astype(int).values

    X_test_raw = df_test_sampled[FEATURE_SCHEMA].values
    y_test_binary = (df_test_sampled['Label'] != 'BenignTraffic').astype(int).values
    y_test_subclass = df_test_sampled['Label'].values
    y_test_class = df_test_sampled['attack_class'].values

    # Clean NaNs and Infs
    def clean_matrix(mat):
        return np.nan_to_num(mat, nan=0.0, posinf=1e6, neginf=-1e6)

    X_train_raw = clean_matrix(X_train_raw)
    X_val_raw = clean_matrix(X_val_raw)
    X_sup_raw = clean_matrix(X_sup_raw)
    X_test_raw = clean_matrix(X_test_raw)

    # Fit scaler STRICTLY on Unsupervised Benign Training Data
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train_raw)

    # Transform other partitions
    X_val = scaler.transform(X_val_raw)
    X_sup = scaler.transform(X_sup_raw)
    X_test = scaler.transform(X_test_raw)

    # Save output artifacts and manifest
    out_npz = os.path.join(output_dir, 'recovery_processed.npz')
    np.savez_compressed(
        out_npz,
        X_train=X_train.astype(np.float32),
        X_val=X_val.astype(np.float32),
        X_sup=X_sup.astype(np.float32),
        y_sup=y_sup_train.astype(np.int64),
        X_test=X_test.astype(np.float32),
        y_test_binary=y_test_binary.astype(np.int64),
        y_test_subclass=y_test_subclass,
        y_test_class=y_test_class
    )

    joblib.dump(scaler, os.path.join(output_dir, 'recovery_scaler.pkl'))

    manifest = {
        'schema_feature_count': len(FEATURE_SCHEMA),
        'feature_schema': FEATURE_SCHEMA,
        'X_train_shape': list(X_train.shape),
        'X_val_shape': list(X_val.shape),
        'X_sup_shape': list(X_sup.shape),
        'X_test_shape': list(X_test.shape),
        'scaler_mean': scaler.mean_.tolist(),
        'scaler_scale': scaler.scale_.tolist()
    }
    with open(os.path.join(output_dir, 'recovery_manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)

    return out_npz
