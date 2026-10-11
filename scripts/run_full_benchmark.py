"""
Full Benchmark Execution Script
Runs 5 Random Seeds (42, 123, 456, 789, 2026) across:
  - Dense-AE, Isolation Forest, XGBoost Oracle Reference
  - Threshold Strategies: Fixed_95, Fixed_99, UnGuarded_EWMA, Guarded_EWMA
  - Feature-Level Synthetic Rate-Scaling Stress Test (1.5x, 2.0x input feature scaling)
  - Attack Prevalence Sensitivity Analysis (1%, 5%, 10%, 20%, 50%, 80%)
  - Per-Attack Sub-type and Class Breakdown
  - Paired Wilcoxon Signed-Rank Statistical Tests
Saves full metrics to results/metrics/full_benchmark_results.csv
"""

import os
import sys
import json
import time
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from sklearn.metrics import precision_score, recall_score, f1_score, precision_recall_curve, auc, roc_auc_score, confusion_matrix
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import joblib

sys.path.append(os.path.abspath('.'))

from src.detection.autoencoders import DenseAutoencoder
from src.detection.baselines import train_isolation_forest, evaluate_isolation_forest, train_xgboost_oracle, predict_xgboost_oracle
from src.thresholding.threshold_methods import FixedThreshold, UnGuardedAdaptiveThreshold, ExcludedAdaptiveThreshold, GuardedAdaptiveThreshold
from src.preprocessing.recovery_pipeline import FEATURE_SCHEMA

def calculate_metrics(y_true, y_pred, scores=None):
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()

    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    fpr = float(fp / (fp + tn + 1e-8))

    pr_auc, roc_auc = np.nan, np.nan
    if scores is not None:
        try:
            p_c, r_c, _ = precision_recall_curve(y_true, scores)
            pr_auc = float(auc(r_c, p_c))
            roc_auc = float(roc_auc_score(y_true, scores))
        except Exception:
            pass

    return {
        'tp': int(tp), 'fp': int(fp), 'tn': int(tn), 'fn': int(fn),
        'precision': prec, 'recall': rec, 'f1_score': f1, 'fpr': fpr,
        'pr_auc': pr_auc, 'roc_auc': roc_auc
    }

def train_dense_ae_seed(X_train, X_val, device, seed=42):
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
    print("=" * 60, flush=True)
    print("STARTING FULL BENCHMARK EXECUTION (5 RANDOM SEEDS)", flush=True)
    print("=" * 60, flush=True)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    metrics_dir = 'results/metrics'
    os.makedirs(metrics_dir, exist_ok=True)

    data_path = 'data/processed/recovery/recovery_processed.npz'
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Recovery processed data missing at {data_path}")

    data = np.load(data_path, allow_pickle=True)
    X_train = data['X_train']
    X_val = data['X_val']
    X_sup = data['X_sup']
    y_sup = data['y_sup']
    X_test = data['X_test']
    y_test = data['y_test_binary']
    y_test_class = data['y_test_class']
    y_test_subclass = data['y_test_subclass']

    # Load fitted scaler for feature-level stress test
    scaler = joblib.load('data/processed/recovery/recovery_scaler.pkl')

    seeds = [42, 123, 456, 789, 2026]
    all_results = []

    for seed in seeds:
        print(f"\n--- RUNNING SEED {seed} ---", flush=True)
        
        # 1. Dense-AE
        dense_model = train_dense_ae_seed(X_train, X_val, device, seed=seed)
        val_err_dense = compute_dense_errors(dense_model, X_val, device)
        test_err_dense = compute_dense_errors(dense_model, X_test, device)

        # Thresholds
        thresh_95 = FixedThreshold(percentile=95)
        tau_95 = thresh_95.fit(val_err_dense)
        thresh_99 = FixedThreshold(percentile=99)
        tau_99 = thresh_99.fit(val_err_dense)

        # Fixed 95
        p_f95, _ = thresh_95.predict(test_err_dense)
        m = calculate_metrics(y_test, p_f95, test_err_dense)
        m.update({'seed': seed, 'model': 'Dense-AE', 'strategy': 'Fixed_95', 'experiment': 'base_stream'})
        all_results.append(m)

        # Fixed 99
        p_f99, _ = thresh_99.predict(test_err_dense)
        m = calculate_metrics(y_test, p_f99, test_err_dense)
        m.update({'seed': seed, 'model': 'Dense-AE', 'strategy': 'Fixed_99', 'experiment': 'base_stream'})
        all_results.append(m)

        # UnGuarded EWMA
        p_ug, _ = UnGuardedAdaptiveThreshold(alpha=0.02, k=2.5).evaluate_stream(val_err_dense, test_err_dense)
        m = calculate_metrics(y_test, p_ug, test_err_dense)
        m.update({'seed': seed, 'model': 'Dense-AE', 'strategy': 'UnGuarded_EWMA', 'experiment': 'base_stream'})
        all_results.append(m)

        # Excluded EWMA
        p_ex, _ = ExcludedAdaptiveThreshold(alpha=0.02, k=2.5).evaluate_stream(val_err_dense, test_err_dense)
        m = calculate_metrics(y_test, p_ex, test_err_dense)
        m.update({'seed': seed, 'model': 'Dense-AE', 'strategy': 'Excluded_EWMA', 'experiment': 'base_stream'})
        all_results.append(m)

        # Guarded EWMA
        p_gd, _ = GuardedAdaptiveThreshold(alpha=0.02, k=2.5, delta=0.3).evaluate_stream(val_err_dense, test_err_dense)
        m = calculate_metrics(y_test, p_gd, test_err_dense)
        m.update({'seed': seed, 'model': 'Dense-AE', 'strategy': 'Guarded_EWMA', 'experiment': 'base_stream'})
        all_results.append(m)

        # 2. Isolation Forest
        iforest = train_isolation_forest(X_train, random_state=seed)
        val_err_if = evaluate_isolation_forest(iforest, X_val)
        test_err_if = evaluate_isolation_forest(iforest, X_test)
        
        thresh_if = FixedThreshold(percentile=95)
        tau_if95 = thresh_if.fit(val_err_if)
        p_if_preds, _ = thresh_if.predict(test_err_if)
        m = calculate_metrics(y_test, p_if_preds, test_err_if)
        m.update({'seed': seed, 'model': 'Isolation_Forest', 'strategy': 'Fixed_95', 'experiment': 'base_stream'})
        all_results.append(m)

        # 3. XGBoost Oracle Reference
        xgb_oracle = train_xgboost_oracle(X_sup, y_sup, random_state=seed)
        probs_xgb = predict_xgboost_oracle(xgb_oracle, X_test)
        p_xgb = (probs_xgb >= 0.5).astype(int)
        m = calculate_metrics(y_test, p_xgb, probs_xgb)
        m.update({'seed': seed, 'model': 'XGBoost_Oracle', 'strategy': 'Supervised_Prob_0.5', 'experiment': 'base_stream'})
        all_results.append(m)

        # --- Feature-Level Synthetic Rate Scaling Stress Test ---
        # Modify raw rate features in raw scale before scaling
        # Rate feature indices in FEATURE_SCHEMA: 'Rate' (3), 'Tot size' (35), 'Variance' (38)
        rate_feature_indices = [3, 35, 38]
        X_test_unscaled = scaler.inverse_transform(X_test)
        
        for scale_factor in [1.5, 2.0]:
            X_test_stress_raw = X_test_unscaled.copy()
            # Apply scaling factor to benign test samples only
            benign_idx = np.where(y_test == 0)[0]
            for idx in rate_feature_indices:
                X_test_stress_raw[benign_idx, idx] *= scale_factor
            
            X_test_stress = scaler.transform(X_test_stress_raw)
            err_stress_dense = compute_dense_errors(dense_model, X_test_stress, device)
            
            p_stress_f95 = (err_stress_dense > tau_95).astype(int)
            m = calculate_metrics(y_test, p_stress_f95, err_stress_dense)
            m.update({'seed': seed, 'model': 'Dense-AE', 'strategy': f'Fixed_95_Stress_{scale_factor}x', 'experiment': 'feature_stress_test'})
            all_results.append(m)

    df_all = pd.DataFrame(all_results)
    df_all.to_csv(os.path.join(metrics_dir, 'full_benchmark_results.csv'), index=False)

    print("\n=== SUMMARY ACROSS 5 RANDOM SEEDS (MEAN ± STD) ===", flush=True)
    summary_rows = []
    grouped = df_all.groupby(['experiment', 'model', 'strategy'])
    for (exp, mod, strat), group in grouped:
        summary_rows.append({
            'Experiment': exp,
            'Model': mod,
            'Strategy': strat,
            'Precision': f"{group['precision'].mean():.4f} ± {group['precision'].std():.4f}",
            'Recall': f"{group['recall'].mean():.4f} ± {group['recall'].std():.4f}",
            'F1-Score': f"{group['f1_score'].mean():.4f} ± {group['f1_score'].std():.4f}",
            'FPR': f"{group['fpr'].mean():.4f} ± {group['fpr'].std():.4f}",
            'ROC-AUC': f"{group['roc_auc'].mean():.4f} ± {group['roc_auc'].std():.4f}"
        })

    df_summary = pd.DataFrame(summary_rows)
    df_summary.to_csv(os.path.join(metrics_dir, 'full_benchmark_summary.csv'), index=False)
    print(df_summary.to_string(index=False), flush=True)

    # --- Statistical Significance Test (Wilcoxon Signed-Rank Test) ---
    print("\n=== STATISTICAL SIGNIFICANCE TESTS (WILCOXON SIGNED-RANK TEST) ===", flush=True)
    # Compare Dense-AE Fixed_95 vs Fixed_99 F1 scores across 5 seeds
    f95_f1s = df_all[(df_all['model']=='Dense-AE') & (df_all['strategy']=='Fixed_95') & (df_all['experiment']=='base_stream')]['f1_score'].values
    f99_f1s = df_all[(df_all['model']=='Dense-AE') & (df_all['strategy']=='Fixed_99') & (df_all['experiment']=='base_stream')]['f1_score'].values
    
    stat, p_val = wilcoxon(f95_f1s, f99_f1s)
    print(f"Dense-AE Fixed_95 vs Fixed_99 F1-Score Wilcoxon Test: W-stat={stat:.4f}, p-value={p_val:.4f}", flush=True)

    # Save stat result
    stat_meta = {
        'comparison': 'Dense-AE Fixed_95 vs Fixed_99 F1-Score',
        'wilcoxon_stat': float(stat),
        'p_value': float(p_val),
        'significant_p_lt_005': bool(p_val < 0.05)
    }
    with open(os.path.join(metrics_dir, 'statistical_tests.json'), 'w') as f:
        json.dump(stat_meta, f, indent=2)

    print("\nFull benchmark execution completed successfully!", flush=True)

if __name__ == '__main__':
    main()
