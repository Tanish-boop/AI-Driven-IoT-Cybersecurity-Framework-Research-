"""
Threshold Adaptation Strategies:
1. Fixed Threshold (Percentile on Validation Errors)
2. Un-Guarded Adaptive Threshold (EWMA updated on ALL observations)
3. Guarded Adaptive Threshold (EWMA updated with winsorized/clamped errors on flagged anomalies)
"""

import numpy as np

class FixedThreshold:
    def __init__(self, percentile=95):
        self.percentile = percentile
        self.tau = None

    def fit(self, val_errors):
        self.tau = np.percentile(val_errors, self.percentile)
        return self.tau

    def predict(self, test_errors):
        # 1 for anomaly, 0 for normal
        predictions = (test_errors > self.tau).astype(int)
        taus = np.full_like(test_errors, self.tau)
        return predictions, taus

class UnGuardedAdaptiveThreshold:
    def __init__(self, alpha=0.02, k=2.5, initial_percentile=95):
        self.alpha = alpha
        self.k = k
        self.initial_percentile = initial_percentile

    def evaluate_stream(self, val_errors, test_errors):
        # Initialize mean and std from validation errors
        mu = np.mean(val_errors)
        var = np.var(val_errors)
        std = np.sqrt(var + 1e-8)

        n_test = len(test_errors)
        predictions = np.zeros(n_test, dtype=int)
        taus = np.zeros(n_test, dtype=float)

        for t in range(n_test):
            err = test_errors[t]
            tau_t = mu + self.k * std
            taus[t] = tau_t
            predictions[t] = 1 if err > tau_t else 0

            # Un-guarded update: update on ALL observations, including anomalies
            mu = (1 - self.alpha) * mu + self.alpha * err
            var = (1 - self.alpha) * var + self.alpha * ((err - mu) ** 2)
            std = np.sqrt(max(var, 1e-8))

        return predictions, taus

class ExcludedAdaptiveThreshold:
    def __init__(self, alpha=0.02, k=2.5, initial_percentile=95):
        self.alpha = alpha
        self.k = k
        self.initial_percentile = initial_percentile

    def evaluate_stream(self, val_errors, test_errors):
        mu = np.mean(val_errors)
        var = np.var(val_errors)
        std = np.sqrt(var + 1e-8)

        n_test = len(test_errors)
        predictions = np.zeros(n_test, dtype=int)
        taus = np.zeros(n_test, dtype=float)

        for t in range(n_test):
            err = test_errors[t]
            tau_t = mu + self.k * std
            taus[t] = tau_t

            if err > tau_t:
                predictions[t] = 1
                # Excluded update: skip update when sample is flagged as anomalous
            else:
                predictions[t] = 0
                mu = (1 - self.alpha) * mu + self.alpha * err
                var = (1 - self.alpha) * var + self.alpha * ((err - mu) ** 2)
                std = np.sqrt(max(var, 1e-8))

        return predictions, taus

class GuardedAdaptiveThreshold:
    def __init__(self, alpha=0.02, k=2.5, delta=0.2, initial_percentile=95):
        self.alpha = alpha
        self.k = k
        self.delta = delta
        self.initial_percentile = initial_percentile

    def evaluate_stream(self, val_errors, test_errors):
        mu = np.mean(val_errors)
        var = np.var(val_errors)
        std = np.sqrt(var + 1e-8)

        n_test = len(test_errors)
        predictions = np.zeros(n_test, dtype=int)
        taus = np.zeros(n_test, dtype=float)

        for t in range(n_test):
            err = test_errors[t]
            tau_t = mu + self.k * std
            taus[t] = tau_t

            if err > tau_t:
                predictions[t] = 1
                # Guarded update: clamp error to tau_t + delta * std
                update_err = tau_t + self.delta * std
            else:
                predictions[t] = 0
                update_err = err

            mu = (1 - self.alpha) * mu + self.alpha * update_err
            var = (1 - self.alpha) * var + self.alpha * ((update_err - mu) ** 2)
            std = np.sqrt(max(var, 1e-8))

        return predictions, taus
