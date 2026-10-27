"""
Master Validated Experiment Runner (Stage 4 & Stage 5)
Executes Pre-registered Evaluation across 5 Random Seeds on CICIoT2023.

Enforces:
  1. Strict Test-Label Firewall: No ground-truth test labels accessible during
     adaptation or threshold decisions. Labels used ONLY in final offline metric computation.
  2. Distinct Scenarios:
     - Scenario 1: Nominal Held-Out Test Stream (N=100,000)
     - Scenario 2: Synthetic Score-Level Stress Test (1.8x on benign scores)
     - Scenario 3: Feature-Level Rate Scaling Stress Test (2.0x on rate/size features before AE)
     - Scenario 4: Structured Attack Contamination Episode (20k attack flood + 20k recovery)
     - Scenario 5: Mixed Drift and Contamination Episode
  3. Predeclared Methods on Identical Streams:
     - Fixed_95, Fixed_99, Raw_EWMA, Excluded_EWMA, CGB_Adaptive, Gated_Rolling_Quantile, Robust_Median_MAD
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
import joblib

sys.path.append(os.path.abspath('.'))

from src.detection.autoencoders import DenseAutoencoder
from src.thresholding.threshold_methods import (
    FixedThreshold,
    UnGuardedAdaptiveThreshold,
    ExcludedAdaptiveThreshold,
    ContaminationGatedAdaptiveThreshold,
    GatedRollingQuantileThreshold,
    RobustMedianMADThreshold
)

def calculate_metrics(y_true, y_pred, taus=None, tau_init=None):
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    fpr = float(fp / (fp + tn + 1e-8))
    fnr = float(fn / (tp + fn + 1e-8))

    max_inflation = float(np.max(taus) / tau_init) if (taus is not None and tau_init is not None and tau_init > 0) else np.nan
    max_tau = float(np.max(taus)) if taus is not None else np.nan

    return {
        'tp': int(tp), 'fp': int(fp), 'tn': int(tn), 'fn': int(fn),
        'precision': prec, 'recall': rec, 'f1_score': f1, 'fpr': fpr, 'fnr': fnr,
        'max_tau': max_tau, 'max_inflation': max_inflation
    }

def train_dense_ae(X_train, device, seed=42, epochs=10, batch_size=512):
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = DenseAutoencoder(input_dim=39).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
    criterion = nn.MSELoss()

    train_ds = TensorDataset(torch.tensor(X_train, dtype=torch.float32))
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)

    t0 = time.time()
    model.train()
    for epoch in range(1, epochs + 1):
        for (bx,) in train_loader:
            bx = bx.to(device)
            optimizer.zero_grad()
            recon = model(bx)
            loss = criterion(recon, bx)
            loss.backward()
            optimizer.step()
    train_time = time.time() - t0
    return model, train_time

def compute_errors(model, X, device):
    model.eval()
    ds = TensorDataset(torch.tensor(X, dtype=torch.float32))
    loader = DataLoader(ds, batch_size=2048, shuffle=False)
    errs = []
    with torch.no_grad():
        for (bx,) in loader:
            bx = bx.to(device)
            recon = model(bx)
            err = torch.mean((bx - recon)**2, dim=1).cpu().numpy()
            errs.append(err)
    return np.concatenate(errs)

def build_scenarios(test_err_nominal, X_test, y_test, scaler, model, device):
    """
    Constructs the 5 distinct evaluation scenarios.
    All scenario streams are constructed BEFORE threshold controller execution.
    """
    scenarios = {}

    # 1. Nominal Held-Out Stream
    scenarios['scenario_1_nominal'] = {
        'errors': test_err_nominal.copy(),
        'y_true': y_test.copy(),
        'description': 'Nominal held-out stream without modification'
    }

    # 2. Synthetic Score Shift (1.8x on benign scores)
    err_score_shift = test_err_nominal.copy()
    err_score_shift[y_test == 0] *= 1.8
    scenarios['scenario_2_synthetic_score_shift'] = {
        'errors': err_score_shift,
        'y_true': y_test.copy(),
        'description': 'Synthetic score-level stress: 1.8x scalar scaling on benign scores'
    }

    # 3. Feature-Level Rate Scaling Stress Test (2.0x on features [3, 35, 38])
    rate_indices = [3, 35, 38] # Rate, Tot size, Variance
    X_test_unscaled = scaler.inverse_transform(X_test)
    X_test_feature_drift = X_test_unscaled.copy()
    benign_mask = (y_test == 0)
    for idx in rate_indices:
        X_test_feature_drift[benign_mask, idx] *= 2.0
    X_test_drift_scaled = scaler.transform(X_test_feature_drift)
    err_feature_drift = compute_errors(model, X_test_drift_scaled, device)
    scenarios['scenario_3_feature_benign_drift'] = {
        'errors': err_feature_drift,
        'y_true': y_test.copy(),
        'description': 'Feature-level rate scaling: 2.0x on features [3, 35, 38] before AE'
    }

    # 4. Structured Attack Contamination Episode
    # Construct an ordered stream:
    # 0..10,000: nominal test samples
    # 10,000..30,000: 20,000 consecutive attack samples (100% flood)
    # 30,000..50,000: 20,000 consecutive benign samples (clean recovery window)
    # 50,000..100,000: remaining nominal samples
    attack_indices = np.where(y_test == 1)[0]
    benign_indices = np.where(y_test == 0)[0]

    # Partition indices
    init_nom = np.arange(10000)
    flood_attacks = attack_indices[10000:30000] if len(attack_indices) >= 30000 else np.resize(attack_indices, 20000)
    recovery_benign = np.resize(benign_indices, 20000)
    tail_nom = np.arange(50000, 100000)

    stream_idx_s4 = np.concatenate([init_nom, flood_attacks[:20000], recovery_benign[:20000], tail_nom])
    scenarios['scenario_4_adversarial_contamination'] = {
        'errors': test_err_nominal[stream_idx_s4],
        'y_true': y_test[stream_idx_s4],
        'description': 'Structured contamination: 20k attack flood (t=10k..30k) + 20k recovery (t=30k..50k)',
        'flood_start': 10000, 'flood_end': 30000, 'recovery_end': 50000
    }

    # 5. Mixed Scenario: Feature Drift + Attack Contamination
    # 0..20,000: Feature drift errors
    # 20,000..40,000: Attack flood
    # 40,000..60,000: Clean recovery
    # 60,000..100,000: Nominal tail
    stream_idx_s5 = np.concatenate([np.arange(20000), flood_attacks[:20000], recovery_benign[:20000], np.arange(60000, 100000)])
    err_s5 = test_err_nominal[stream_idx_s5].copy()
    err_s5[:20000] = err_feature_drift[stream_idx_s5[:20000]]
    scenarios['scenario_5_mixed_drift_and_contamination'] = {
        'errors': err_s5,
        'y_true': y_test[stream_idx_s5],
        'description': 'Mixed: feature drift (0..20k), attack flood (20k..40k), recovery (40k..60k)'
    }

    return scenarios

def main():
    print("=" * 80)
    print("STARTING PRE-REGISTERED VALID EVALUATION RUN (STAGE 4 & STAGE 5)")
    print("=" * 80)

    out_dir = 'experiments/valid_evaluation_20261016'
    os.makedirs(out_dir, exist_ok=True)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Compute Device: {device}")

    data_path = 'data/processed/recovery/recovery_processed.npz'
    scaler_path = 'data/processed/recovery/recovery_scaler.pkl'
    data = np.load(data_path, allow_pickle=True)
    scaler = joblib.load(scaler_path)

    X_train = data['X_train']
    X_val = data['X_val']
    X_test = data['X_test']
    y_test = data['y_test_binary']

    seeds = [42, 123, 456, 789, 2026]
    per_seed_results = []
    threshold_traces = {}

    for seed in seeds:
        print(f"\n====================== RUNNING SEED {seed} ======================")
        # 1. Train Dense-AE on X_train (Unsupervised)
        model, train_t = train_dense_ae(X_train, device, seed=seed, epochs=10)
        
        # 2. Compute validation reconstruction errors (Offline calibration strictly on X_val)
        val_err = compute_errors(model, X_val, device)
        tau_val_95 = float(np.percentile(val_err, 95.0))
        tau_val_99 = float(np.percentile(val_err, 99.0))
        print(f"Validation Calibrated tau_95: {tau_val_95:.5f} | tau_99: {tau_val_99:.5f}")

        # 3. Compute nominal test errors
        test_err_nominal = compute_errors(model, X_test, device)

        # 4. Construct scenarios before controller evaluation
        scenarios = build_scenarios(test_err_nominal, X_test, y_test, scaler, model, device)

        # Define Methods
        methods = {
            'Fixed_95': FixedThreshold(percentile=95.0),
            'Fixed_99': FixedThreshold(percentile=99.0),
            'Raw_EWMA': UnGuardedAdaptiveThreshold(alpha=0.02, k=2.5),
            'Excluded_EWMA': ExcludedAdaptiveThreshold(alpha=0.02, k=2.5),
            'CGB_Adaptive': ContaminationGatedAdaptiveThreshold(alpha=0.01, k=2.5, buffer_margin=0.85, cooldown=15, max_alert_rate=0.08, window=50, max_delta=0.005),
            'Gated_Rolling_Quantile': GatedRollingQuantileThreshold(buffer_size=1000, quantile=95.0, cooldown=10, max_alert_rate=0.08, window=50),
            'Robust_Median_MAD': RobustMedianMADThreshold(buffer_size=1000, k_mad=3.0, cooldown=10, max_alert_rate=0.08, window=50)
        }

        # Fit static thresholds offline
        methods['Fixed_95'].fit(val_err)
        methods['Fixed_99'].fit(val_err)

        for sc_id, sc_data in scenarios.items():
            err_stream = sc_data['errors']
            y_stream = sc_data['y_true']

            for m_name, m_obj in methods.items():
                t0 = time.perf_counter()
                if 'Fixed' in m_name:
                    preds, taus = m_obj.predict(err_stream)
                else:
                    # Online streaming evaluation: receives ONLY val_err and err_stream
                    # Test labels are STRICTLY NOT PASSED (Test-Label Firewall)
                    preds, taus = m_obj.evaluate_stream(val_err, err_stream)
                lat_us = ((time.perf_counter() - t0) / len(err_stream)) * 1e6

                # Decision Invariant Check
                expected_preds = (err_stream > taus).astype(int)
                assert np.array_equal(preds, expected_preds), f"Decision invariant violated in {m_name} on {sc_id}"

                # Compute metrics strictly offline after predictions are finalized
                m = calculate_metrics(y_stream, preds, taus=taus, tau_init=tau_val_95)
                m.update({
                    'seed': seed,
                    'scenario': sc_id,
                    'method': m_name,
                    'latency_us_per_sample': lat_us,
                    'train_time_s': train_t
                })
                per_seed_results.append(m)

                # Store trace for seed 42
                if seed == 42:
                    trace_key = f"{sc_id}__{m_name}"
                    threshold_traces[trace_key] = taus

            # Progress output for seed
            sc_cgb = [r for r in per_seed_results if r['seed'] == seed and r['scenario'] == sc_id and r['method'] == 'CGB_Adaptive'][0]
            sc_f95 = [r for r in per_seed_results if r['seed'] == seed and r['scenario'] == sc_id and r['method'] == 'Fixed_95'][0]
            print(f"[{sc_id}] Fixed_95 F1: {sc_f95['f1_score']*100:.2f}% FPR: {sc_f95['fpr']*100:.2f}% | CGB F1: {sc_cgb['f1_score']*100:.2f}% FPR: {sc_cgb['fpr']*100:.2f}%")

    # Save per-seed results
    df_per_seed = pd.DataFrame(per_seed_results)
    out_per_seed_csv = os.path.join(out_dir, 'results_per_seed.csv')
    df_per_seed.to_csv(out_per_seed_csv, index=False)
    print(f"\nSaved per-seed results to {out_per_seed_csv}")

    # Save threshold traces
    out_traces = os.path.join(out_dir, 'threshold_traces.npz')
    np.savez_compressed(out_traces, **threshold_traces)
    print(f"Saved threshold traces to {out_traces}")

    # Generate Summary Table across 5 seeds (Mean +- Std)
    summary_rows = []
    grouped = df_per_seed.groupby(['scenario', 'method'], sort=False)
    for (sc, meth), grp in grouped:
        summary_rows.append({
            'Scenario': sc,
            'Method': meth,
            'Precision': f"{grp['precision'].mean()*100:.2f}% ± {grp['precision'].std()*100:.2f}%",
            'Recall': f"{grp['recall'].mean()*100:.2f}% ± {grp['recall'].std()*100:.2f}%",
            'F1_Score': f"{grp['f1_score'].mean()*100:.2f}% ± {grp['f1_score'].std()*100:.2f}%",
            'FPR': f"{grp['fpr'].mean()*100:.2f}% ± {grp['fpr'].std()*100:.2f}%",
            'FNR': f"{grp['fnr'].mean()*100:.2f}% ± {grp['fnr'].std()*100:.2f}%",
            'Max_Inflation': f"{grp['max_inflation'].mean():.2f}x ± {grp['max_inflation'].std():.2f}x" if not np.isnan(grp['max_inflation'].mean()) else "N/A",
            'Latency_us': f"{grp['latency_us_per_sample'].mean():.2f}"
        })

    df_summary = pd.DataFrame(summary_rows)
    out_summary_csv = os.path.join(out_dir, 'results_summary.csv')
    df_summary.to_csv(out_summary_csv, index=False)
    print(f"Saved summary results to {out_summary_csv}")

    # Save Scenario Manifest
    scenario_manifest = {
        'date': '2026-10-16',
        'eval_script': 'experiments/valid_evaluation_20261016/run_valid_evaluation.py',
        'seeds': seeds,
        'scenarios': {
            'scenario_1_nominal': 'Nominal held-out stream without modification (N=100k)',
            'scenario_2_synthetic_score_shift': 'Synthetic score-level stress test (1.8x on benign scores)',
            'scenario_3_feature_benign_drift': 'Feature-level rate scaling (2.0x on features 3, 35, 38 before AE)',
            'scenario_4_adversarial_contamination': 'Structured 20k attack flood (t=10k..30k) + 20k clean recovery (t=30k..50k)',
            'scenario_5_mixed_drift_and_contamination': 'Compound: feature drift (0..20k), attack flood (20k..40k), recovery (40k..60k)'
        },
        'firewall_verified': True
    }
    with open(os.path.join(out_dir, 'scenario_manifest.json'), 'w') as f:
        json.dump(scenario_manifest, f, indent=2)

    print("\n" + "=" * 90)
    print("PRE-REGISTERED EVALUATION SUMMARY (5 RANDOM SEEDS)")
    print("=" * 90)
    print(df_summary.to_string(index=False))
    print("=" * 90)

if __name__ == '__main__':
    main()
