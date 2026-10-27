"""
experiments/test_improved_thresholding.py

Tests improved contamination-resistant and drift-aware adaptive thresholding
designed following the Review Paper blueprint:
1. Truncation-bias corrected EWMA (calibrated kappa factor)
2. Envelope-bounded adaptive controller
3. Quantile tracking with contamination freeze
4. Compares against Fixed 95th, Excluded EWMA, and Raw EWMA across all 5 scenarios.
"""

import os
import sys
import numpy as np
import pandas as pd
import torch
import joblib

sys.path.append(os.path.abspath('.'))

from src.detection.autoencoders import DenseAutoencoder
from experiments.valid_evaluation_20261016.run_valid_evaluation import train_dense_ae, compute_errors, build_scenarios, calculate_metrics

class TruncationCorrectedAdaptiveThreshold:
    """
    Truncation-Bias Corrected Adaptive Threshold (TCA-Threshold)
    
    Addresses the core flaw of Excluded EWMA (downward drift):
    - On validation data, estimates the truncation bias factor kappa:
      kappa = tau_val_95 / (mu_trunc + k * std_trunc)
    - During streaming, updates mu and var only on non-alert samples (e <= tau_t).
    - Multiplies the candidate threshold by kappa, preventing downward drift.
    - Applies a bounded envelope [rho_min * tau_calib, rho_max * tau_calib].
    - Applies step-size clamping |tau_{t+1} - tau_t| <= max_delta.
    """
    def __init__(self, alpha=0.01, k=2.5, rho_min=0.85, rho_max=2.5, max_delta=0.005, freeze_streak=3, cooldown=10):
        self.alpha = alpha
        self.k = k
        self.rho_min = rho_min
        self.rho_max = rho_max
        self.max_delta = max_delta
        self.freeze_streak = freeze_streak
        self.cooldown = cooldown

    def evaluate_stream(self, val_errors, test_errors):
        tau_calib = float(np.percentile(val_errors, 95.0))
        
        # Estimate truncation bias on validation set
        val_below = val_errors[val_errors <= tau_calib]
        mu_val_trunc = np.mean(val_below)
        var_val_trunc = np.var(val_below)
        std_val_trunc = np.sqrt(var_val_trunc + 1e-8)
        
        denom = mu_val_trunc + self.k * std_val_trunc
        kappa = tau_calib / max(denom, 1e-8)
        
        # State variables
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
            
            # Update only when:
            # 1. Non-alert (e <= current_tau)
            # 2. Not in attack flood cooldown
            if is_alert == 0 and cooldown_timer == 0:
                # Winsorized error update
                capped_e = min(e, current_tau)
                mu = (1 - self.alpha) * mu + self.alpha * capped_e
                var = (1 - self.alpha) * var + self.alpha * ((capped_e - mu) ** 2)
                std = np.sqrt(max(var, 1e-8))
                
                raw_target = kappa * (mu + self.k * std)
                # Envelope bounding
                bounded_target = np.clip(raw_target, self.rho_min * tau_calib, self.rho_max * tau_calib)
                
                # Slew-rate / step-size clamping
                delta = np.clip(bounded_target - current_tau, -self.max_delta, self.max_delta)
                current_tau = current_tau + delta

        return predictions, taus

def run_test():
    print("Loading data...")
    data = np.load('data/processed/recovery/recovery_processed.npz', allow_pickle=True)
    scaler = joblib.load('data/processed/recovery/recovery_scaler.pkl')
    
    device = torch.device('cpu')
    print("Training Dense-AE on seed 42...")
    model, _ = train_dense_ae(data['X_train'], device, seed=42, epochs=5)
    
    val_err = compute_errors(model, data['X_val'], device)
    test_err_nominal = compute_errors(model, data['X_test'], device)
    y_test = data['y_test_binary']
    
    tau_val_95 = float(np.percentile(val_err, 95.0))
    print(f"Validation Calibrated tau_95: {tau_val_95:.5f}")
    
    scenarios = build_scenarios(test_err_nominal, data['X_test'], y_test, scaler, model, device)
    
    # Test methods:
    # 1. Fixed 95th
    # 2. Excluded EWMA
    # 3. Old CGB Adaptive
    # 4. New TCA Adaptive (Truncation-Corrected Adaptive)
    from src.thresholding.threshold_methods import FixedThreshold, ExcludedAdaptiveThreshold, ContaminationGatedAdaptiveThreshold
    
    methods = {
        'Fixed_95': FixedThreshold(percentile=95.0),
        'Excluded_EWMA': ExcludedAdaptiveThreshold(alpha=0.02, k=2.5),
        'Old_CGB': ContaminationGatedAdaptiveThreshold(alpha=0.01, k=2.5, buffer_margin=0.85, cooldown=15, max_alert_rate=0.08, window=50, max_delta=0.005),
        'TCA_Adaptive_k2.5': TruncationCorrectedAdaptiveThreshold(alpha=0.01, k=2.5, rho_min=0.90, rho_max=2.5, max_delta=0.005),
        'TCA_Adaptive_k2.0': TruncationCorrectedAdaptiveThreshold(alpha=0.01, k=2.0, rho_min=0.90, rho_max=2.5, max_delta=0.005),
        'TCA_Adaptive_Fast': TruncationCorrectedAdaptiveThreshold(alpha=0.02, k=2.5, rho_min=0.90, rho_max=3.0, max_delta=0.01)
    }
    methods['Fixed_95'].fit(val_err)
    
    records = []
    print("\n--- EVALUATION ACROSS SCENARIOS ---")
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
            print(f"  {m_name:20s} | F1: {m['f1_score']*100:6.2f}% | Rec: {m['recall']*100:6.2f}% | Prec: {m['precision']*100:6.2f}% | FPR: {m['fpr']*100:6.2f}% | Tau_Range: [{np.min(taus):.4f}, {np.max(taus):.4f}]")
            records.append({
                'scenario': sc_name,
                'method': m_name,
                'f1': m['f1_score'],
                'rec': m['recall'],
                'prec': m['precision'],
                'fpr': m['fpr'],
                'min_tau': np.min(taus),
                'max_tau': np.max(taus)
            })

if __name__ == '__main__':
    run_test()
