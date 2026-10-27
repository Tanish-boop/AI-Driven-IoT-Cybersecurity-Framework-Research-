"""
experiments/test_feature_error_pooling.py

Tests whether feature-level error pooling (Top-k or variance-weighted)
solves the Reconstruction Error Dilution problem for stealthy attacks
(Reconnaissance, BruteForce, Spoofing, Web-based) on CICIoT2023.
"""

import os
import sys
sys.path.append(os.path.abspath('.'))

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
import joblib

from src.detection.autoencoders import DenseAutoencoder
from experiments.valid_evaluation_20261016.run_valid_evaluation import train_dense_ae

data = np.load('data/processed/recovery/recovery_processed.npz', allow_pickle=True)
device = torch.device('cpu')

print("Training baseline Dense-AE...")
model, _ = train_dense_ae(data['X_train'], device, seed=42, epochs=5)
model.eval()

# Compute feature-wise errors for validation and test
def compute_featurewise_errors(model, X):
    loader = DataLoader(TensorDataset(torch.tensor(X, dtype=torch.float32)), batch_size=2048, shuffle=False)
    diffs = []
    with torch.no_grad():
        for (bx,) in loader:
            recon = model(bx)
            sq_err = (bx - recon)**2 # shape (batch, 39)
            diffs.append(sq_err.cpu().numpy())
    return np.vstack(diffs)

val_sq_err = compute_featurewise_errors(model, data['X_val'])
test_sq_err = compute_featurewise_errors(model, data['X_test'])
y_test = data['y_test_binary']

# 1. Standard Mean MSE
val_mse = np.mean(val_sq_err, axis=1)
test_mse = np.mean(test_sq_err, axis=1)
tau_mse_95 = np.percentile(val_mse, 95)
preds_mse = (test_mse > tau_mse_95).astype(int)

# 2. Top-k feature pooling: average of top-k largest feature squared errors
print("\n--- Testing Top-k Feature Error Pooling ---")
for k in [1, 2, 3, 5, 8, 12, 20, 39]:
    val_topk = np.mean(np.sort(val_sq_err, axis=1)[:, -k:], axis=1)
    test_topk = np.mean(np.sort(test_sq_err, axis=1)[:, -k:], axis=1)
    tau_topk_95 = np.percentile(val_topk, 95)
    
    preds_topk = (test_topk > tau_topk_95).astype(int)
    f1 = f1_score(y_test, preds_topk, zero_division=0) * 100
    rec = recall_score(y_test, preds_topk, zero_division=0) * 100
    prec = precision_score(y_test, preds_topk, zero_division=0) * 100
    tn, fp, fn, tp = confusion_matrix(y_test, preds_topk).ravel()
    fpr = fp / (fp + tn) * 100
    print(f"Top-{k:2d} Error Pooling: F1={f1:5.2f}% | Rec={rec:5.2f}% | Prec={prec:5.2f}% | FPR={fpr:5.2f}%")

# 3. Normalized / Standardized Error per Feature:
# Scale each feature's error by its 95th percentile in benign validation data
print("\n--- Testing Normalized Feature Error Pooling ---")
feat_p95 = np.percentile(val_sq_err, 95, axis=0) + 1e-6
val_norm_err = np.mean(val_sq_err / feat_p95, axis=1)
test_norm_err = np.mean(test_sq_err / feat_p95, axis=1)
tau_norm_95 = np.percentile(val_norm_err, 95)

preds_norm = (test_norm_err > tau_norm_95).astype(int)
f1 = f1_score(y_test, preds_norm, zero_division=0) * 100
rec = recall_score(y_test, preds_norm, zero_division=0) * 100
prec = precision_score(y_test, preds_norm, zero_division=0) * 100
tn, fp, fn, tp = confusion_matrix(y_test, preds_norm).ravel()
fpr = fp / (fp + tn) * 100
print(f"Feature-Normalized MSE:  F1={f1:5.2f}% | Rec={rec:5.2f}% | Prec={prec:5.2f}% | FPR={fpr:5.2f}%")

# Check class breakdown for top-5 vs standard
if 'y_test_class' in data.files:
    y_class = data['y_test_class']
    classes = np.unique(y_class)
    print("\n--- Per-Class Recall Comparison: Standard MSE vs Top-5 Pooling ---")
    val_top5 = np.mean(np.sort(val_sq_err, axis=1)[:, -5:], axis=1)
    test_top5 = np.mean(np.sort(test_sq_err, axis=1)[:, -5:], axis=1)
    tau_top5_95 = np.percentile(val_top5, 95)
    preds_top5 = (test_top5 > tau_top5_95).astype(int)
    
    for c in classes:
        mask = (y_class == c)
        n_c = np.sum(mask)
        if c == 'Benign':
            rec_mse = (1.0 - np.mean(preds_mse[mask])) * 100 # specificity
            rec_top5 = (1.0 - np.mean(preds_top5[mask])) * 100
            print(f"  {c:20s} (N={n_c:5d}) Specificity: Standard={rec_mse:5.2f}% | Top-5={rec_top5:5.2f}%")
        else:
            rec_mse = np.mean(preds_mse[mask]) * 100
            rec_top5 = np.mean(preds_top5[mask]) * 100
            print(f"  {c:20s} (N={n_c:5d}) Recall:      Standard={rec_mse:5.2f}% | Top-5={rec_top5:5.2f}% | Diff={rec_top5 - rec_mse:+5.2f}%")
