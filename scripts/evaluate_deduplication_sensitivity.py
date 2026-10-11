"""
Deduplication Sensitivity Evaluation Script across 5 Random Seeds (42, 123, 456, 789, 2026).
Evaluates Dense-AE (Fixed 95th and Excluded EWMA) and XGBoost Oracle on:
1. Full Held-Out Test Set (N=100,000)
2. Clean Deduplicated Test Set (N=98,543) - removing all 1,457 cross-partition duplicate feature rows.
"""

import os
import sys
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score

sys.path.append(os.path.abspath('.'))
from src.detection.autoencoders import DenseAutoencoder
from src.thresholding.threshold_methods import FixedThreshold, ExcludedAdaptiveThreshold
from src.detection.baselines import train_xgboost_oracle, predict_xgboost_oracle

def calculate_metrics(y_true, y_pred, scores=None):
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    fpr = float(fp / (fp + tn + 1e-8))
    roc_auc = float(roc_auc_score(y_true, scores)) if scores is not None else np.nan
    return {
        'tp': int(tp), 'fp': int(fp), 'tn': int(tn), 'fn': int(fn),
        'precision': prec, 'recall': rec, 'f1_score': f1, 'fpr': fpr, 'roc_auc': roc_auc
    }

def train_dense_ae_seed(X_train, device, seed=42):
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = DenseAutoencoder(input_dim=39).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
    criterion = nn.MSELoss()

    train_ds = TensorDataset(torch.tensor(X_train, dtype=torch.float32))
    train_loader = DataLoader(train_ds, batch_size=512, shuffle=True)

    model.train()
    for epoch in range(1, 11):
        for (bx,) in train_loader:
            bx = bx.to(device)
            optimizer.zero_grad()
            recon = model(bx)
            loss = criterion(recon, bx)
            loss.backward()
            optimizer.step()
    return model

def compute_dense_errors(model, X, device):
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

def main():
    print("=" * 70)
    print("RUNNING 5-SEED DEDUPLICATION SENSITIVITY EVALUATION")
    print("=" * 70)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    data = np.load('data/processed/recovery/recovery_processed.npz', allow_pickle=True)
    X_train = data['X_train']
    X_val = data['X_val']
    X_sup = data['X_sup']
    y_sup = data['y_sup']
    X_test = data['X_test']
    y_test = data['y_test_binary']

    set_train = set(map(tuple, X_train))
    set_sup = set(map(tuple, X_sup))
    set_leak = set_train | set_sup
    mask_clean = np.array([tuple(r) not in set_leak for r in X_test])
    X_test_clean = X_test[mask_clean]
    y_test_clean = y_test[mask_clean]

    print(f"Full Test Set: N={len(X_test)}, Clean Test Set: N={len(X_test_clean)}, Excluded Overlap: {(~mask_clean).sum()}")

    seeds = [42, 123, 456, 789, 2026]
    records = []

    for seed in seeds:
        print(f"\n--- Seed {seed} ---")
        
        # Train Dense-AE exactly as in run_full_benchmark.py
        model = train_dense_ae_seed(X_train, device, seed=seed)
        val_err = compute_dense_errors(model, X_val, device)
        test_err_full = compute_dense_errors(model, X_test, device)
        test_err_clean = compute_dense_errors(model, X_test_clean, device)

        # 1. Fixed 95th Percentile
        thresh_95 = FixedThreshold(percentile=95)
        thresh_95.fit(val_err)
        p_f95_full, _ = thresh_95.predict(test_err_full)
        p_f95_clean, _ = thresh_95.predict(test_err_clean)

        m_f95_full = calculate_metrics(y_test, p_f95_full, test_err_full)
        m_f95_clean = calculate_metrics(y_test_clean, p_f95_clean, test_err_clean)

        records.append({
            'seed': seed, 'model': 'Dense-AE', 'strategy': 'Fixed_95',
            'full_f1': m_f95_full['f1_score'], 'clean_f1': m_f95_clean['f1_score'],
            'delta_f1': m_f95_clean['f1_score'] - m_f95_full['f1_score'],
            'full_fpr': m_f95_full['fpr'], 'clean_fpr': m_f95_clean['fpr'],
            'full_prec': m_f95_full['precision'], 'clean_prec': m_f95_clean['precision'],
            'full_rec': m_f95_full['recall'], 'clean_rec': m_f95_clean['recall'],
            'full_auc': m_f95_full['roc_auc'], 'clean_auc': m_f95_clean['roc_auc']
        })

        # 2. Excluded EWMA
        p_ex_full, _ = ExcludedAdaptiveThreshold(alpha=0.02, k=2.5).evaluate_stream(val_err, test_err_full)
        p_ex_clean, _ = ExcludedAdaptiveThreshold(alpha=0.02, k=2.5).evaluate_stream(val_err, test_err_clean)

        m_ex_full = calculate_metrics(y_test, p_ex_full, test_err_full)
        m_ex_clean = calculate_metrics(y_test_clean, p_ex_clean, test_err_clean)

        records.append({
            'seed': seed, 'model': 'Dense-AE', 'strategy': 'Excluded_EWMA',
            'full_f1': m_ex_full['f1_score'], 'clean_f1': m_ex_clean['f1_score'],
            'delta_f1': m_ex_clean['f1_score'] - m_ex_full['f1_score'],
            'full_fpr': m_ex_full['fpr'], 'clean_fpr': m_ex_clean['fpr'],
            'full_prec': m_ex_full['precision'], 'clean_prec': m_ex_clean['precision'],
            'full_rec': m_ex_full['recall'], 'clean_rec': m_ex_clean['recall'],
            'full_auc': m_ex_full['roc_auc'], 'clean_auc': m_ex_clean['roc_auc']
        })

        # 3. XGBoost Oracle Reference
        xgb_oracle = train_xgboost_oracle(X_sup, y_sup, random_state=seed)
        probs_xgb_full = predict_xgboost_oracle(xgb_oracle, X_test)
        p_xgb_full = (probs_xgb_full >= 0.5).astype(int)
        probs_xgb_clean = predict_xgboost_oracle(xgb_oracle, X_test_clean)
        p_xgb_clean = (probs_xgb_clean >= 0.5).astype(int)

        m_xgb_full = calculate_metrics(y_test, p_xgb_full, probs_xgb_full)
        m_xgb_clean = calculate_metrics(y_test_clean, p_xgb_clean, probs_xgb_clean)

        records.append({
            'seed': seed, 'model': 'XGBoost_Oracle', 'strategy': 'Supervised_Prob_0.5',
            'full_f1': m_xgb_full['f1_score'], 'clean_f1': m_xgb_clean['f1_score'],
            'delta_f1': m_xgb_clean['f1_score'] - m_xgb_full['f1_score'],
            'full_fpr': m_xgb_full['fpr'], 'clean_fpr': m_xgb_clean['fpr'],
            'full_prec': m_xgb_full['precision'], 'clean_prec': m_xgb_clean['precision'],
            'full_rec': m_xgb_full['recall'], 'clean_rec': m_xgb_clean['recall'],
            'full_auc': m_xgb_full['roc_auc'], 'clean_auc': m_xgb_clean['roc_auc']
        })

    df_records = pd.DataFrame(records)
    out_per_seed = 'results/metrics/deduplication_sensitivity_per_seed.csv'
    df_records.to_csv(out_per_seed, index=False)
    print(f"\nSaved per-seed results to {out_per_seed}")

    # Summary table across 5 seeds
    summary = []
    for (model, strategy), group in df_records.groupby(['model', 'strategy']):
        summary.append({
            'model': model,
            'strategy': strategy,
            'full_f1_mean': group['full_f1'].mean(),
            'full_f1_std': group['full_f1'].std(),
            'clean_f1_mean': group['clean_f1'].mean(),
            'clean_f1_std': group['clean_f1'].std(),
            'delta_f1_mean': group['delta_f1'].mean(),
            'full_fpr_mean': group['full_fpr'].mean(),
            'full_fpr_std': group['full_fpr'].std(),
            'clean_fpr_mean': group['clean_fpr'].mean(),
            'clean_fpr_std': group['clean_fpr'].std()
        })
    
    df_summary = pd.DataFrame(summary)
    out_summary = 'results/metrics/deduplication_sensitivity_summary.csv'
    df_summary.to_csv(out_summary, index=False)
    print(f"Saved summary to {out_summary}")

    print("\n=== 5-SEED DEDUPLICATION SENSITIVITY SUMMARY ===")
    for row in summary:
        print(f"{row['model']} ({row['strategy']}): Full F1 = {row['full_f1_mean']:.4f} ± {row['full_f1_std']:.4f} --> Clean F1 = {row['clean_f1_mean']:.4f} ± {row['clean_f1_std']:.4f} | Delta = {row['delta_f1_mean']:+.4f} | Clean FPR = {row['clean_fpr_mean']:.4f}")

if __name__ == '__main__':
    main()
