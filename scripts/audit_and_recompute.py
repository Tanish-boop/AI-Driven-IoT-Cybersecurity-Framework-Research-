"""
Independent Audit & Recomputed Metrics Script
Recalculates exact metrics from saved predictions/errors in results/metrics/baseline_errors.npz
Saves clean recomputed metrics to results/metrics/recomputed_metrics.csv
"""

import os
import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, precision_recall_curve, auc, roc_auc_score

def recalculate():
    errors_path = 'results/metrics/baseline_errors.npz'
    if not os.path.exists(errors_path):
        raise FileNotFoundError("baseline_errors.npz missing")

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

    recomputed = []

    # Helper function
    def compute_all(y_true, scores, pred_binary, model_name, strat_name):
        tp = int(np.sum((y_true == 1) & (pred_binary == 1)))
        fp = int(np.sum((y_true == 0) & (pred_binary == 1)))
        tn = int(np.sum((y_true == 0) & (pred_binary == 0)))
        fn = int(np.sum((y_true == 1) & (pred_binary == 0)))

        prec = float(precision_score(y_true, pred_binary, zero_division=0))
        rec = float(recall_score(y_true, pred_binary, zero_division=0))
        f1 = float(f1_score(y_true, pred_binary, zero_division=0))
        fpr = float(fp / (fp + tn + 1e-8))

        try:
            prec_curve, rec_curve, _ = precision_recall_curve(y_true, scores)
            pr_auc = float(auc(rec_curve, prec_curve))
            roc_auc = float(roc_auc_score(y_true, scores))
        except Exception:
            pr_auc = np.nan
            roc_auc = np.nan

        return {
            'model': model_name,
            'strategy': strat_name,
            'precision': prec,
            'recall': rec,
            'f1_score': f1,
            'fpr': fpr,
            'pr_auc': pr_auc,
            'roc_auc': roc_auc,
            'tp': tp,
            'fp': fp,
            'tn': tn,
            'fn': fn
        }

    # 1. Dense-AE Fixed 95
    tau_dense_95 = np.percentile(err_val_dense, 95)
    preds_dense_95 = (err_test_dense > tau_dense_95).astype(int)
    recomputed.append(compute_all(y_test_binary, err_test_dense, preds_dense_95, 'Dense-AE', 'Fixed_95'))

    # 2. Dense-AE Fixed 99
    tau_dense_99 = np.percentile(err_val_dense, 99)
    preds_dense_99 = (err_test_dense > tau_dense_99).astype(int)
    recomputed.append(compute_all(y_test_binary, err_test_dense, preds_dense_99, 'Dense-AE', 'Fixed_99'))

    # 3. LSTM-AE Fixed 95
    tau_lstm_95 = np.percentile(err_val_lstm, 95)
    preds_lstm_95 = (err_test_lstm > tau_lstm_95).astype(int)
    recomputed.append(compute_all(y_test_seq, err_test_lstm, preds_lstm_95, 'LSTM-AE', 'Fixed_95'))

    # 4. GRU-AE Fixed 95
    tau_gru_95 = np.percentile(err_val_gru, 95)
    preds_gru_95 = (err_test_gru > tau_gru_95).astype(int)
    recomputed.append(compute_all(y_test_seq, err_test_gru, preds_gru_95, 'GRU-AE', 'Fixed_95'))

    # 5. Isolation Forest Fixed 95
    tau_iforest_95 = np.percentile(err_val_iforest, 95)
    preds_iforest_95 = (err_test_iforest > tau_iforest_95).astype(int)
    recomputed.append(compute_all(y_test_binary, err_test_iforest, preds_iforest_95, 'Isolation_Forest', 'Fixed_95'))

    # 6. XGBoost Oracle Supervised Prob 0.5
    preds_xgb = (probs_test_xgb >= 0.5).astype(int)
    recomputed.append(compute_all(y_test_binary, probs_test_xgb, preds_xgb, 'XGBoost_Oracle', 'Supervised_Prob_0.5'))

    df_out = pd.DataFrame(recomputed)
    out_path = 'results/metrics/recomputed_metrics.csv'
    df_out.to_csv(out_path, index=False)
    print(f"Saved recomputed metrics to {out_path}")
    print(df_out.to_string(index=False))

if __name__ == '__main__':
    recalculate()
