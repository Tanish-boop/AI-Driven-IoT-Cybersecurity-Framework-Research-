"""
Dataset Preparation and Preprocessing Script for CICIoT2023
Enforces strict capture-aware and leakage-resistant dataset splits.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib

def main():
    print("=" * 60)
    print("Starting CICIoT2023 Dataset Preparation & Preprocessing")
    print("=" * 60)

    raw_train_path = 'data/raw/train.parquet'
    raw_test_path = 'data/raw/test.parquet'
    processed_dir = 'data/processed'
    os.makedirs(processed_dir, exist_ok=True)

    if not os.path.exists(raw_train_path) or not os.path.exists(raw_test_path):
        raise FileNotFoundError("Raw parquet files missing in data/raw/")

    print("Loading raw train and test parquet files...")
    df_train = pd.read_parquet(raw_train_path)
    df_test = pd.read_parquet(raw_test_path)

    print(f"Loaded df_train: {df_train.shape}, df_test: {df_test.shape}")

    # Exclude metadata and label columns from features
    target_cols = ['Label', 'attack_class', 'label']
    feature_cols = [c for c in df_train.columns if c not in target_cols]
    print(f"Total feature columns count: {len(feature_cols)}")

    # 1. Separate Benign and Attack samples in df_train
    df_benign_train = df_train[df_train['Label'] == 'BenignTraffic'].copy()
    df_attack_train = df_train[df_train['Label'] != 'BenignTraffic'].copy()

    print(f"Benign samples in df_train: {len(df_benign_train)}")
    print(f"Attack samples in df_train: {len(df_attack_train)}")

    # Shuffle deterministically
    rng = np.random.RandomState(42)
    benign_shuffled = df_benign_train.sample(frac=1.0, random_state=rng).reset_index(drop=True)
    attack_shuffled = df_attack_train.sample(frac=1.0, random_state=rng).reset_index(drop=True)

    # Split Benign into Unsupervised Train (100k) and Validation (30k)
    n_train_benign = 100000
    n_val_benign = 30000

    train_benign_df = benign_shuffled.iloc[:n_train_benign]
    val_benign_df = benign_shuffled.iloc[n_train_benign:n_train_benign + n_val_benign]
    remaining_benign_train = benign_shuffled.iloc[n_train_benign + n_val_benign:]

    # Create separate Supervised Oracle Training set (20k benign + 20k attack)
    sup_benign = remaining_benign_train.iloc[:20000]
    sup_attack = attack_shuffled.iloc[:20000]
    df_supervised = pd.concat([sup_benign, sup_attack]).sample(frac=1.0, random_state=rng).reset_index(drop=True)

    # 2. Extract feature matrices
    X_train_unsup_raw = train_benign_df[feature_cols].values
    X_val_unsup_raw = val_benign_df[feature_cols].values
    X_sup_train_raw = df_supervised[feature_cols].values
    y_sup_train = (df_supervised['Label'] != 'BenignTraffic').astype(int).values

    # Test set from df_test (subsample 100k preserving class proportions if larger)
    df_test_sampled = df_test.sample(n=min(100000, len(df_test)), random_state=rng).reset_index(drop=True)
    X_test_raw = df_test_sampled[feature_cols].values
    y_test_binary = (df_test_sampled['Label'] != 'BenignTraffic').astype(int).values
    y_test_subclass = df_test_sampled['Label'].values
    y_test_class = df_test_sampled['attack_class'].values

    # Clean infinite/NaN values
    def clean_matrix(mat, reference_medians=None):
        mat = np.nan_to_num(mat, nan=0.0, posinf=1e6, neginf=-1e6)
        return mat

    X_train_unsup_raw = clean_matrix(X_train_unsup_raw)
    X_val_unsup_raw = clean_matrix(X_val_unsup_raw)
    X_sup_train_raw = clean_matrix(X_sup_train_raw)
    X_test_raw = clean_matrix(X_test_raw)

    # 3. Fit Scaler STRICTLY on Unsupervised Train Data
    print("Fitting StandardScaler strictly on Unsupervised Benign Training Data...")
    scaler = StandardScaler()
    X_train_unsup = scaler.fit_transform(X_train_unsup_raw)

    # Apply fitted scaler to all other partitions
    X_val_unsup = scaler.transform(X_val_unsup_raw)
    X_sup_train = scaler.transform(X_sup_train_raw)
    X_test = scaler.transform(X_test_raw)

    print(f"X_train_unsup shape: {X_train_unsup.shape}")
    print(f"X_val_unsup shape: {X_val_unsup.shape}")
    print(f"X_sup_train shape: {X_sup_train.shape}")
    print(f"X_test shape: {X_test.shape}")
    print(f"Test benign count: {(y_test_binary == 0).sum()}, attack count: {(y_test_binary == 1).sum()}")

    # 4. Save processed datasets
    output_npz = os.path.join(processed_dir, 'ciciot2023_processed.npz')
    np.savez_compressed(
        output_npz,
        X_train_unsup=X_train_unsup.astype(np.float32),
        X_val_unsup=X_val_unsup.astype(np.float32),
        X_sup_train=X_sup_train.astype(np.float32),
        y_sup_train=y_sup_train.astype(np.int64),
        X_test=X_test.astype(np.float32),
        y_test_binary=y_test_binary.astype(np.int64),
        y_test_subclass=y_test_subclass,
        y_test_class=y_test_class
    )
    print(f"Saved processed datasets to {output_npz}")

    # Save fitted scaler
    joblib.dump(scaler, os.path.join(processed_dir, 'scaler.pkl'))
    
    # Save dataset metadata summary
    meta = {
        'num_features': len(feature_cols),
        'feature_names': feature_cols,
        'X_train_unsup_rows': X_train_unsup.shape[0],
        'X_val_unsup_rows': X_val_unsup.shape[0],
        'X_sup_train_rows': X_sup_train.shape[0],
        'X_test_rows': X_test.shape[0],
        'test_benign_count': int((y_test_binary == 0).sum()),
        'test_attack_count': int((y_test_binary == 1).sum()),
        'unique_test_attack_classes': list(np.unique(y_test_class)),
        'unique_test_subclasses': list(np.unique(y_test_subclass))
    }
    with open(os.path.join(processed_dir, 'dataset_metadata.json'), 'w') as f:
        json.dump(meta, f, indent=2)

    print("Dataset Preparation Completed Successfully!")

if __name__ == '__main__':
    main()
