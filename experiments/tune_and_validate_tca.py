"""
experiments/tune_and_validate_tca.py

Strict Validation Calibration & Held-Out Testing of TCA-Adaptive Threshold:
1. Enforces Test-Label Firewall: Hyperparameters (percentile, k, alpha, rho_min)
   are selected exclusively on X_val / X_sup.
2. The chosen parameter configuration is then evaluated on the held-out test set (N=100,000)
   across all 5 scenarios.
"""

import os
import sys
import numpy as np
import torch
import joblib

sys.path.append(os.path.abspath('.'))

from src.detection.autoencoders import DenseAutoencoder
from experiments.valid_evaluation_20261016.run_valid_evaluation import train_dense_ae, compute_errors, build_scenarios, calculate_metrics

class TruncationCorrectedAdaptiveThreshold:
    def __init__(self, target_percentile=93.0, alpha=0.015, k=2.0, rho_min=0.85, rho_max=2.5, max_delta=0.008, freeze_streak=3, cooldown=10):
        self.target_percentile = target_percentile
        self.alpha = alpha
        self.k = k
        self.rho_min = rho_min
        self.rho_max = rho_max
        self.max_delta = max_delta
        self.freeze_streak = freeze_streak
        self.cooldown = cooldown

    def evaluate_stream(self, val_errors, test_errors):
        tau_calib = float(np.percentile(val_errors, self.target_percentile))
        
        # Estimate truncation bias on validation set
        val_below = val_errors[val_errors <= tau_calib]
        mu_val_trunc = np.mean(val_below)
        var_val_trunc = np.var(val_below)
        std_val_trunc = np.sqrt(var_val_trunc + 1e-8)
        
        denom = mu_val_trunc + self.k * std_val_trunc
        kappa = tau_calib / max(denom, 1e-8)
        
        mu = mu_val_trunc
        var = var_val_trunc
        std = std_val_trunc
        current_tau = tau_calib
        
        n = len(test_errors)
        predictions = np.zeros(n, dtype=int)
        taus = np.zeros(n, dtype=float)
        
        streak = 0
        cooldown_timer = 0
        
        for t in range(n):
            e = test_errors[t]
            taus[t] = current_tau
            
            is_alert = 1 if e > current_tau else 0
            predictions[t] = is_alert
            
            if is_alert:
                streak += 1
                if streak >= self.freeze_streak:
                    cooldown_timer = self.cooldown
            else:
                streak = 0
                if cooldown_timer > 0:
                    cooldown_timer -= 1
            
            # Gated update: update only on non-alert samples outside attack bursts
            if is_alert == 0 and cooldown_timer == 0:
                capped_e = min(e, current_tau)
                mu = (1 - self.alpha) * mu + self.alpha * capped_e
                var = (1 - self.alpha) * var + self.alpha * ((capped_e - mu) ** 2)
                std = np.sqrt(max(var, 1e-8))
                
                raw_target = kappa * (mu + self.k * std)
                bounded_target = np.clip(raw_target, self.rho_min * tau_calib, self.rho_max * tau_calib)
                
                delta = np.clip(bounded_target - current_tau, -self.max_delta, self.max_delta)
                current_tau = current_tau + delta

        return predictions, taus

def run_calibration_and_test():
    print("Loading data...")
    data = np.load('data/processed/recovery/recovery_processed.npz', allow_pickle=True)
    scaler = joblib.load('data/processed/recovery/recovery_scaler.pkl')
    
    device = torch.device('cpu')
    print("Training Dense-AE on seed 42...")
    model, _ = train_dense_ae(data['X_train'], device, seed=42, epochs=5)
    
    val_err = compute_errors(model, data['X_val'], device)
    sup_err = compute_errors(model, data['X_sup'], device)
    y_sup = data['y_sup']
    
    test_err_nominal = compute_errors(model, data['X_test'], device)
    y_test = data['y_test_binary']
    
    print("\n--- STAGE 1: CALIBRATION ON SUPERVISORY PARTITION (X_sup, y_sup) ---")
    print("Selecting optimal target_percentile and k on X_sup (Test set strictly NOT touched)...")
    
    best_sup_f1 = 0
    best_config = None
    
    for p in [90.0, 92.0, 93.0, 94.0, 95.0]:
        for k_val in [1.5, 1.8, 2.0, 2.2, 2.5]:
            for a in [0.01, 0.015, 0.02]:
                tca = TruncationCorrectedAdaptiveThreshold(target_percentile=p, k=k_val, alpha=a)
                preds, _ = tca.evaluate_stream(val_err, sup_err)
                m = calculate_metrics(y_sup, preds)
                # Select configuration that keeps FPR <= 7% while maximizing F1
                if m['fpr'] <= 0.07 and m['f1_score'] > best_sup_f1:
                    best_sup_f1 = m['f1_score']
                    best_config = (p, k_val, a)
                    print(f"  New Best on X_sup: p={p}, k={k_val}, alpha={a} => F1={m['f1_score']*100:.2f}%, FPR={m['fpr']*100:.2f}%, Rec={m['recall']*100:.2f}%")
    
    print(f"\nFinal Selected Config from Supervisory Optimization: p={best_config[0]}, k={best_config[1]}, alpha={best_config[2]} (F1 on X_sup: {best_sup_f1*100:.2f}%)")
    
    print("\n--- STAGE 2: HELD-OUT EVALUATION ACROSS ALL 5 SCENARIOS (X_test, N=100,000) ---")
    scenarios = build_scenarios(test_err_nominal, data['X_test'], y_test, scaler, model, device)
    
    from src.thresholding.threshold_methods import FixedThreshold, ExcludedAdaptiveThreshold, ContaminationGatedAdaptiveThreshold
    
    tau_val_95 = float(np.percentile(val_err, 95.0))
    methods = {
        'Fixed_95': FixedThreshold(percentile=95.0),
        'Excluded_EWMA': ExcludedAdaptiveThreshold(alpha=0.02, k=2.5),
        'Old_CGB': ContaminationGatedAdaptiveThreshold(alpha=0.01, k=2.5, buffer_margin=0.85, cooldown=15, max_alert_rate=0.08, window=50, max_delta=0.005),
        'TCA_Calibrated': TruncationCorrectedAdaptiveThreshold(target_percentile=best_config[0], k=best_config[1], alpha=best_config[2], rho_min=0.85, rho_max=2.5, max_delta=0.008)
    }
    methods['Fixed_95'].fit(val_err)
    
    for sc_name, sc_data in scenarios.items():
        err_stream = sc_data['errors']
        y_stream = sc_data['y_true']
        print(f"\nScenario: {sc_name}")
        for m_name, m_obj in methods.items():
            if 'Fixed' in m_name:
                preds, taus = m_obj.predict(err_stream)
            else:
                preds, taus = m_obj.evaluate_stream(val_err, err_stream)
            
            m = calculate_metrics(y_stream, preds, taus=taus, tau_init=tau_val_95)
            print(f"  {m_name:20s} | F1: {m['f1_score']*100:6.2f}% | Rec: {m['recall']*100:6.2f}% | Prec: {m['precision']*100:6.2f}% | FPR: {m['fpr']*100:6.2f}% | Tau: [{np.min(taus):.4f}, {np.max(taus):.4f}]")

if __name__ == '__main__':
    run_calibration_and_test()
