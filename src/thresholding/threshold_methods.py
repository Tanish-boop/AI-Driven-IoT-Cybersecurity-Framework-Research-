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

class ContaminationGatedAdaptiveThreshold:
    """
    Contamination-Gated Bounded Adaptive Threshold Controller (CGB-Adaptive)
    Implements the blueprint from Section 7.4 of the Review Paper:
      1. Eligibility Gate g_t: Updates baseline only when stream is clean benign,
         alert rate is not elevated, and no incident cooldown is active.
      2. Winsorization & Clipping: Caps acceptable score contributions and bounds
         maximum per-step threshold movement (|tau_{t+1} - tau_t| <= max_delta).
      3. Incident Freeze: Freezes baseline during sustained attacks, completely
         preventing threshold poisoning collapse.
    """
    def __init__(self, alpha=0.01, k=2.5, buffer_margin=0.85, cooldown=15, max_alert_rate=0.08, window=50, max_delta=0.005):
        self.alpha = alpha
        self.k = k
        self.buffer_margin = buffer_margin
        self.cooldown = cooldown
        self.max_alert_rate = max_alert_rate
        self.window = window
        self.max_delta = max_delta

    def evaluate_stream(self, val_errors, test_errors):
        tau_init = np.percentile(val_errors, 95)
        # Initialize running statistics from validation errors safely below tau_init
        calib_subset = val_errors[val_errors <= tau_init]
        mu = np.mean(calib_subset)
        var = np.var(calib_subset)
        std = np.sqrt(var + 1e-8)

        n = len(test_errors)
        predictions = np.zeros(n, dtype=int)
        taus = np.zeros(n, dtype=float)

        recent_alerts = np.zeros(self.window, dtype=int)
        cooldown_timer = 0

        for t in range(n):
            e = test_errors[t]
            tau_t = mu + self.k * std
            taus[t] = tau_t

            # Alert decision
            is_alert = 1 if e > tau_t else 0
            predictions[t] = is_alert

            recent_alerts[t % self.window] = is_alert
            alert_rate = np.mean(recent_alerts)

            if is_alert:
                cooldown_timer = self.cooldown
            elif cooldown_timer > 0:
                cooldown_timer -= 1

            # Eligibility gate g_t:
            # 1. Sample is not an alert (is_alert == 0)
            # 2. Score is safely below the alarm boundary (e <= buffer_margin * tau_t)
            # 3. Not in incident cooldown (cooldown_timer == 0)
            # 4. Local alert rate is not elevated (alert_rate <= max_alert_rate)
            eligible = (is_alert == 0) and (e <= self.buffer_margin * tau_t) and (cooldown_timer == 0) and (alert_rate <= self.max_alert_rate)

            if eligible:
                # Winsorize score contribution
                capped_e = min(e, self.buffer_margin * tau_t)
                new_mu = (1 - self.alpha) * mu + self.alpha * capped_e
                new_var = (1 - self.alpha) * var + self.alpha * ((capped_e - new_mu) ** 2)
                new_std = np.sqrt(max(new_var, 1e-8))

                target_tau = new_mu + self.k * new_std
                delta = np.clip(target_tau - tau_t, -self.max_delta, self.max_delta)
                scale = (tau_t + delta) / max(target_tau, 1e-8)
                mu = new_mu * scale
                std = new_std * scale

        return predictions, taus

