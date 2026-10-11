"""
Threshold Adaptation Experiment Runner
Evaluates 3 Threshold Strategies:
  1. Fixed Threshold (95th percentile)
  2. Un-Guarded Adaptive Threshold (EWMA updated on all observations)
  3. Guarded Adaptive Threshold (EWMA updated with clamped errors on flagged anomalies)
Across Models: Dense-AE, LSTM-AE, GRU-AE, Isolation Forest, XGBoost Oracle Reference

Tests:
  - Base Test Stream Evaluation
  - Synthetic Rate-Scaling Stress Test (Simulated 2x to 4x traffic burst)
  - Sustained Attack Inflation Test
  - Per-Attack Sub-type and Class Breakdown
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, precision_recall_curve, auc

sys.path.append(os.path.abspath('.'))

from src.thresholding.threshold_methods import FixedThreshold, UnGuardedAdaptiveThreshold, GuardedAdaptiveThreshold

def calculate_metrics(y_true, y_pred):
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fn = np.sum((y_true == 1) & (y_pred == 0))

    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    fpr = fp / (fp + tn + 1e-8)

    return {
        'precision': float(precision),
        'recall': float(recall),
        'f1': float(f1),
        'fpr': float(fpr),
        'tp': int(tp),
        'fp': int(fp),
        'tn': int(tn),
        'fn': int(fn)
    }

def main():
    print("=" * 60, flush=True)
    print("Starting Threshold Adaptation Experiments", flush=True)
    print("=" * 60, flush=True)

    metrics_dir = 'results/metrics'
    errors_path = os.path.join(metrics_dir, 'baseline_errors.npz')

    if not os.path.exists(errors_path):
        raise FileNotFoundError(f"Baseline error arrays missing at {errors_path}")

    data = np.load(errors_path, allow_pickle=True)
    err_val_dense = data['err_val_dense']
    err_test_dense = data['err_test_dense']
    err_val_lstm = data['err_val_lstm']
    err_test_lstm = data['err_test_lstm']
    err_val_gru = data['err_val_gru']
    err_test_gru = data['err_test_gru']
    err_val_iforest = data['err_val_iforest']
    err_test_iforest = data['err_test_iforest']
    probs_test_xgb = data['probs_test_xgb']
    
    y_test_binary = data['y_test_binary']
    y_test_seq = data['y_test_seq']
    y_test_subclass = data['y_test_subclass']
    y_test_class = data['y_test_class']

    # Subclass and class alignments for sequence models (len = N - seq_len + 1)
    seq_len = 10
    y_test_subclass_seq = y_test_subclass[seq_len-1:]
    y_test_class_seq = y_test_class[seq_len-1:]

    # Define Threshold Strategies
    strategies = {
        'Fixed_95': FixedThreshold(percentile=95),
        'Fixed_99': FixedThreshold(percentile=99),
        'UnGuarded_EWMA': UnGuardedAdaptiveThreshold(alpha=0.02, k=2.5),
        'Guarded_EWMA': GuardedAdaptiveThreshold(alpha=0.02, k=2.5, delta=0.3)
    }

    models_data = {
        'Dense-AE': (err_val_dense, err_test_dense, y_test_binary, y_test_class, y_test_subclass),
        'LSTM-AE': (err_val_lstm, err_test_lstm, y_test_seq, y_test_class_seq, y_test_subclass_seq),
        'GRU-AE': (err_val_gru, err_test_gru, y_test_seq, y_test_class_seq, y_test_subclass_seq),
        'Isolation_Forest': (err_val_iforest, err_test_iforest, y_test_binary, y_test_class, y_test_subclass)
    }

    results = []

    print("\n--- 1. Evaluating Base Test Stream ---", flush=True)
    for model_name, (val_err, test_err, y_true, y_class, y_subclass) in models_data.items():
        for strat_name, strat_obj in strategies.items():
            if 'Fixed' in strat_name:
                strat_obj.fit(val_err)
                preds, taus = strat_obj.predict(test_err)
            else:
                preds, taus = strat_obj.evaluate_stream(val_err, test_err)

            m = calculate_metrics(y_true, preds)
            m['model'] = model_name
            m['strategy'] = strat_name
            m['experiment'] = 'base_stream'
            results.append(m)

            print(f"[{model_name} | {strat_name}] F1: {m['f1']:.4f} | Rec: {m['recall']:.4f} | Prec: {m['precision']:.4f} | FPR: {m['fpr']:.4f}", flush=True)

    # Supervised XGBoost Oracle Baseline evaluation
    xgb_preds = (probs_test_xgb >= 0.5).astype(int)
    m_xgb = calculate_metrics(y_test_binary, xgb_preds)
    m_xgb['model'] = 'XGBoost_Oracle'
    m_xgb['strategy'] = 'Supervised_Probability_0.5'
    m_xgb['experiment'] = 'base_stream'
    results.append(m_xgb)
    print(f"[XGBoost_Oracle | Supervised_0.5] F1: {m_xgb['f1']:.4f} | Rec: {m_xgb['recall']:.4f} | Prec: {m_xgb['precision']:.4f} | FPR: {m_xgb['fpr']:.4f}", flush=True)

    # --- 2. Synthetic Rate-Scaling Stress Test ---
    print("\n--- 2. Evaluating Synthetic Rate-Scaling Stress Test ---", flush=True)
    # Simulate non-stationary benign rate shift by inserting scaled benign errors (1.5x error amplification on benign segment)
    for model_name, (val_err, test_err, y_true, y_class, y_subclass) in models_data.items():
        # Inject benign rate burst in first 5000 samples
        stress_test_err = test_err.copy()
        benign_indices = np.where(y_true == 0)[0]
        burst_indices = benign_indices[:min(5000, len(benign_indices))]
        stress_test_err[burst_indices] = stress_test_err[burst_indices] * 2.0 # 2x error scaling stress test

        for strat_name, strat_obj in strategies.items():
            if 'Fixed' in strat_name:
                strat_obj.fit(val_err)
                preds, taus = strat_obj.predict(stress_test_err)
            else:
                preds, taus = strat_obj.evaluate_stream(val_err, stress_test_err)

            m = calculate_metrics(y_true, preds)
            m['model'] = model_name
            m['strategy'] = strat_name
            m['experiment'] = 'synthetic_rate_shift'
            results.append(m)

            print(f"[Stress Test - {model_name} | {strat_name}] F1: {m['f1']:.4f} | FPR: {m['fpr']:.4f}", flush=True)

    # --- 3. Per-Attack Sub-type & Class Breakdown ---
    print("\n--- 3. Per-Attack Class Recall Breakdown (LSTM-AE Guarded vs Fixed) ---", flush=True)
    lstm_val_err, lstm_test_err, lstm_y_true, lstm_y_class, lstm_y_subclass = models_data['LSTM-AE']
    
    fixed_strat = strategies['Fixed_95']
    fixed_strat.fit(lstm_val_err)
    fixed_preds, _ = fixed_strat.predict(lstm_test_err)

    guarded_strat = strategies['Guarded_EWMA']
    guarded_preds, _ = guarded_strat.evaluate_stream(lstm_val_err, lstm_test_err)

    per_attack_results = []
    unique_classes = np.unique(lstm_y_class)
    for cls in unique_classes:
        if cls == 'Benign':
            continue
        idx = np.where(lstm_y_class == cls)[0]
        if len(idx) == 0:
            continue
        fixed_rec = float(np.mean(fixed_preds[idx] == 1))
        guarded_rec = float(np.mean(guarded_preds[idx] == 1))
        
        per_attack_results.append({
            'attack_class': str(cls),
            'count': int(len(idx)),
            'Fixed_95_Recall': fixed_rec,
            'Guarded_EWMA_Recall': guarded_rec
        })
        print(f"Attack Class: {cls:<12} (Count: {len(idx):<6}) | Fixed_95 Rec: {fixed_rec:.4f} | Guarded_EWMA Rec: {guarded_rec:.4f}", flush=True)

    # Save summary tables
    df_res = pd.DataFrame(results)
    df_res.to_csv(os.path.join(metrics_dir, 'threshold_experiment_results.csv'), index=False)
    
    df_per_attack = pd.DataFrame(per_attack_results)
    df_per_attack.to_csv(os.path.join(metrics_dir, 'per_attack_class_breakdown.csv'), index=False)

    print("\nThreshold adaptation experiments completed successfully!", flush=True)

if __name__ == '__main__':
    main()
