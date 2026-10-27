import os
import sys
sys.path.append(os.path.abspath('.'))

import numpy as np
import torch
import joblib
from experiments.tune_and_validate_tca import TruncationCorrectedAdaptiveThreshold
from experiments.valid_evaluation_20261016.run_valid_evaluation import train_dense_ae, compute_errors, build_scenarios, calculate_metrics

data = np.load('data/processed/recovery/recovery_processed.npz', allow_pickle=True)
scaler = joblib.load('data/processed/recovery/recovery_scaler.pkl')
device = torch.device('cpu')

model, _ = train_dense_ae(data['X_train'], device, seed=42, epochs=5)
val_err = compute_errors(model, data['X_val'], device)
test_err_nominal = compute_errors(model, data['X_test'], device)
y_test = data['y_test_binary']
tau_val_95 = float(np.percentile(val_err, 95.0))

print('Testing TCA target_percentile from 86 to 94 on Scenario 1 (Nominal):')
for p in [86.0, 88.0, 90.0, 91.0, 92.0, 93.0, 94.0]:
    tca = TruncationCorrectedAdaptiveThreshold(target_percentile=p, k=1.8, alpha=0.015, rho_min=0.85, rho_max=2.5, max_delta=0.008)
    preds, taus = tca.evaluate_stream(val_err, test_err_nominal)
    m = calculate_metrics(y_test, preds, taus=taus, tau_init=tau_val_95)
    f1 = m['f1_score'] * 100
    rec = m['recall'] * 100
    prec = m['precision'] * 100
    fpr = m['fpr'] * 100
    t_min, t_max = np.min(taus), np.max(taus)
    print(f"p={p:4.1f}% => F1={f1:5.2f}% | Rec={rec:5.2f}% | Prec={prec:5.2f}% | FPR={fpr:5.2f}% | Tau=[{t_min:.4f}, {t_max:.4f}]")
