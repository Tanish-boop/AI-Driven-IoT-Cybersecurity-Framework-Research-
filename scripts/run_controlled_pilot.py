"""
Controlled Pilot Execution Script
Strictly enforces:
  - Fixed random seed = 42
  - Dense-AE trained on pure Benign train (X_train) ONLY
  - Fixed threshold tuned on pure Benign validation (X_val) ONLY
  - Isolation Forest trained on X_train ONLY
  - XGBoost Oracle trained on X_sup ONLY (explicit supervised reference)
  - Saves full metrics, confusion matrices, score distributions, and environment metadata to results/pilot/
"""

import os
import sys
import json
import time
import platform
import numpy as np
import pandas as pd
import sklearn
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import joblib
from sklearn.metrics import precision_score, recall_score, f1_score, precision_recall_curve, auc, roc_auc_score, confusion_matrix

sys.path.append(os.path.abspath('.'))

from src.detection.autoencoders import DenseAutoencoder
from src.detection.baselines import train_isolation_forest, evaluate_isolation_forest, train_xgboost_oracle, predict_xgboost_oracle

def main():
    print("=" * 60)
    print("STARTING CONTROLLED PILOT EXPERIMENT (SEED = 42)")
    print("=" * 60)

    pilot_dir = 'results/pilot'
    os.makedirs(pilot_dir, exist_ok=True)

    # 1. Environment & Package Metadata
    env_info = {
        'timestamp_local': '2026-10-09T13:07:30',
        'os_platform': platform.platform(),
        'python_version': sys.version,
        'torch_version': torch.__version__,
        'sklearn_version': sklearn.__version__,
        'pandas_version': pd.__version__,
        'numpy_version': np.__version__,
        'random_seed': 42
    }
    with open(os.path.join(pilot_dir, 'pilot_environment.json'), 'w') as f:
        json.dump(env_info, f, indent=2)

    # 2. Load Processed Data
    data_path = 'data/processed/recovery/recovery_processed.npz'
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Processed recovery dataset missing at {data_path}")

    data = np.load(data_path, allow_pickle=True)
    X_train = data['X_train']
    X_val = data['X_val']
    X_sup = data['X_sup']
    y_sup = data['y_sup']
    X_test = data['X_test']
    y_test = data['y_test_binary']
    y_test_class = data['y_test_class']

    # 3. Train Dense Autoencoder on Pure Benign X_train ONLY
    seed = 42
    torch.manual_seed(seed)
    np.random.seed(seed)
    device = torch.device('cpu')

    dense_model = DenseAutoencoder(input_dim=39).to(device)
    optimizer = torch.optim.Adam(dense_model.parameters(), lr=0.001, weight_decay=1e-5)
    criterion = nn.MSELoss()

    train_ds = TensorDataset(torch.tensor(X_train, dtype=torch.float32))
    val_ds = TensorDataset(torch.tensor(X_val, dtype=torch.float32))
    train_loader = DataLoader(train_ds, batch_size=512, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=512, shuffle=False)

    print("Training Pilot Dense-AE (10 Epochs)...")
    start_t = time.time()
    for epoch in range(1, 11):
        dense_model.train()
        t_loss = 0.0
        for (bx,) in train_loader:
            bx = bx.to(device)
            optimizer.zero_grad()
            recon = dense_model(bx)
            loss = criterion(recon, bx)
            loss.backward()
            optimizer.step()
            t_loss += loss.item() * len(bx)
        t_loss /= len(X_train)

        dense_model.eval()
        v_loss = 0.0
        with torch.no_grad():
            for (bx,) in val_loader:
                bx = bx.to(device)
                recon = dense_model(bx)
                loss = criterion(recon, bx)
                v_loss += loss.item() * len(bx)
        v_loss /= len(X_val)

        if epoch % 2 == 0 or epoch == 10:
            print(f"Dense-AE Epoch {epoch:02d}/10 | Train Loss: {t_loss:.6f} | Val Loss: {v_loss:.6f}")

    dense_time = time.time() - start_t

    # Compute Reconstruction Errors on X_val and X_test
    def compute_errors(model, X):
        model.eval()
        ds = TensorDataset(torch.tensor(X, dtype=torch.float32))
        loader = DataLoader(ds, batch_size=1024, shuffle=False)
        errs = []
        with torch.no_grad():
            for (bx,) in loader:
                bx = bx.to(device)
                recon = model(bx)
                err = torch.mean((bx - recon)**2, dim=1).cpu().numpy()
                errs.append(err)
        return np.concatenate(errs)

    val_errors_dense = compute_errors(dense_model, X_val)
    test_errors_dense = compute_errors(dense_model, X_test)

    # Threshold selection on X_val ONLY
    tau_95_dense = float(np.percentile(val_errors_dense, 95))
    tau_99_dense = float(np.percentile(val_errors_dense, 99))

    # 4. Train Isolation Forest on Pure Benign X_train ONLY
    iforest = train_isolation_forest(X_train, random_state=seed)
    val_errors_if = evaluate_isolation_forest(iforest, X_val)
    test_errors_if = evaluate_isolation_forest(iforest, X_test)
    tau_95_if = float(np.percentile(val_errors_if, 95))

    # 5. Train XGBoost Oracle Reference on Separate X_sup Partition ONLY
    xgb_model = train_xgboost_oracle(X_sup, y_sup, random_state=seed)
    test_probs_xgb = predict_xgboost_oracle(xgb_model, X_test)

    # 6. Comprehensive Metric Evaluation Function
    def evaluate_model(y_true, scores, pred_binary, model_name, strat_name):
        cm = confusion_matrix(y_true, pred_binary)
        tn, fp, fn, tp = cm.ravel()

        prec = float(precision_score(y_true, pred_binary, zero_division=0))
        rec = float(recall_score(y_true, pred_binary, zero_division=0))
        f1 = float(f1_score(y_true, pred_binary, zero_division=0))
        fpr = float(fp / (fp + tn + 1e-8))

        prec_c, rec_c, _ = precision_recall_curve(y_true, scores)
        pr_auc = float(auc(rec_c, prec_c))
        roc_auc = float(roc_auc_score(y_true, scores))

        return {
            'model': model_name,
            'strategy': strat_name,
            'tp': int(tp),
            'fp': int(fp),
            'tn': int(tn),
            'fn': int(fn),
            'precision': prec,
            'recall': rec,
            'f1_score': f1,
            'fpr': fpr,
            'pr_auc': pr_auc,
            'roc_auc': roc_auc
        }

    pilot_results = []

    # Dense-AE Fixed_95
    p_dense_95 = (test_errors_dense > tau_95_dense).astype(int)
    pilot_results.append(evaluate_model(y_test, test_errors_dense, p_dense_95, 'Dense-AE', 'Fixed_95_Percentile'))

    # Dense-AE Fixed_99
    p_dense_99 = (test_errors_dense > tau_99_dense).astype(int)
    pilot_results.append(evaluate_model(y_test, test_errors_dense, p_dense_99, 'Dense-AE', 'Fixed_99_Percentile'))

    # Isolation Forest Fixed_95
    p_if_95 = (test_errors_if > tau_95_if).astype(int)
    pilot_results.append(evaluate_model(y_test, test_errors_if, p_if_95, 'Isolation_Forest', 'Fixed_95_Percentile'))

    # XGBoost Supervised Oracle Reference
    p_xgb = (test_probs_xgb >= 0.5).astype(int)
    pilot_results.append(evaluate_model(y_test, test_probs_xgb, p_xgb, 'XGBoost_Oracle', 'Supervised_Prob_0.5'))

    df_results = pd.DataFrame(pilot_results)
    df_results.to_csv(os.path.join(pilot_dir, 'pilot_metrics.csv'), index=False)

    # Save Score Distributions Summary
    score_distrib = {
        'Dense-AE_Val_Errors': {
            'mean': float(val_errors_dense.mean()),
            'median': float(np.median(val_errors_dense)),
            'std': float(val_errors_dense.std()),
            'tau_95': tau_95_dense,
            'tau_99': tau_99_dense
        },
        'Dense-AE_Test_Benign_Errors': {
            'mean': float(test_errors_dense[y_test == 0].mean()),
            'median': float(np.median(test_errors_dense[y_test == 0])),
            'std': float(test_errors_dense[y_test == 0].std())
        },
        'Dense-AE_Test_Attack_Errors': {
            'mean': float(test_errors_dense[y_test == 1].mean()),
            'median': float(np.median(test_errors_dense[y_test == 1])),
            'std': float(test_errors_dense[y_test == 1].std())
        }
    }
    with open(os.path.join(pilot_dir, 'pilot_score_distributions.json'), 'w') as f:
        json.dump(score_distrib, f, indent=2)

    print("\n=== CONTROLLED PILOT RESULTS ===")
    print(df_results[['model', 'strategy', 'precision', 'recall', 'f1_score', 'fpr', 'pr_auc', 'roc_auc']].to_string(index=False))
    print("\nPilot execution completed successfully!")

if __name__ == '__main__':
    main()
