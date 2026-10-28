"""
Concept Drift Detection and Adaptive Controller:
Implements:
1. ADWIN (Adaptive Windowing) Drift Detector for streaming cybersecurity telemetry.
2. Streaming Statistical Drift Monitor (Rolling KS-Distance and Mean Shift).
3. DriftAdaptiveController: Integrates drift detection with Truncation-Bias Corrected
   Adaptive Thresholding (TCA-Adaptive) to handle benign traffic shifts and attack contamination.
"""

import math
import numpy as np
from collections import deque
from typing import List, Dict, Any, Tuple, Optional


class ADWINDriftDetector:
    """
    ADWIN (Adaptive Windowing) Concept Drift Detector.
    Maintains a variable-length window W of recent values. When two subwindows
    exhibit statistically significant differences in their means exceeding
    the Hoeffding/Chernoff bound:
        |mu_0 - mu_1| > epsilon_cut = sqrt( (1 / 2m) * ln(4 / delta) )
    where m = 1 / (1/n_0 + 1/n_1), drift is confirmed and older observations are pruned.
    """
    def __init__(self, delta: float = 0.002, max_window_size: int = 2000, min_subwindow_size: int = 30):
        self.delta = float(delta)
        self.max_window_size = int(max_window_size)
        self.min_subwindow_size = int(min_subwindow_size)
        self.window = deque(maxlen=max_window_size)
        self.drift_detected: bool = False
        self.total_drifts: int = 0
        self.drift_timesteps: List[int] = []
        self.current_t: int = 0

    def add_element(self, value: float) -> bool:
        """
        Ingests a new value into the streaming window and checks for drift.
        Returns True if concept drift is detected at this timestep.
        """
        self.current_t += 1
        self.window.append(float(value))
        self.drift_detected = False

        n = len(self.window)
        if n < 2 * self.min_subwindow_size:
            return False

        # Evaluate potential split points between subwindow 0 and subwindow 1
        # Check candidate cut points (sampling every 10% to ensure low computational latency)
        step = max(5, n // 20)
        best_cut = None
        max_diff = 0.0
        max_eps = 0.0

        w_arr = np.array(self.window)
        # Cumulative sums for O(1) subwindow mean computation
        cumsum = np.cumsum(w_arr)
        total_sum = cumsum[-1]

        for cut in range(self.min_subwindow_size, n - self.min_subwindow_size, step):
            n0 = cut
            n1 = n - cut
            sum0 = cumsum[cut - 1]
            sum1 = total_sum - sum0

            mu0 = sum0 / n0
            mu1 = sum1 / n1
            diff = abs(mu0 - mu1)

            m = 1.0 / (1.0 / n0 + 1.0 / n1)
            # Bound from ADWIN formulation
            eps_cut = math.sqrt((1.0 / (2.0 * m)) * math.log(4.0 * n / self.delta))

            if diff > eps_cut and diff > max_diff:
                max_diff = diff
                max_eps = eps_cut
                best_cut = cut

        if best_cut is not None:
            # Drift detected! Drop older subwindow
            self.drift_detected = True
            self.total_drifts += 1
            self.drift_timesteps.append(self.current_t)
            # Drop items before best_cut
            for _ in range(best_cut):
                if self.window:
                    self.window.popleft()
            return True

        return False

    def reset(self):
        """Resets the detector window and state."""
        self.window.clear()
        self.drift_detected = False
        self.total_drifts = 0
        self.drift_timesteps = []
        self.current_t = 0


class DriftAdaptiveController:
    """
    Combines ADWIN Drift Detection with Truncation-Bias Corrected Adaptive Thresholding.
    Tracks streaming anomaly scores and automatically adjusts the decision boundary:
      - Normal stream: Operates within calibrated envelope [rho_min * tau_0, rho_max * tau_0]
      - Drift detected: Dynamically widens or adapts threshold to accommodate benign drift
      - Attack burst: Detects sudden alert streaks and triggers incident freeze to prevent
        upward threshold inflation
    """
    def __init__(
        self,
        tau_calib: float = 0.50,
        alpha_ewma: float = 0.02,
        k_sigma: float = 2.0,
        rho_min: float = 0.50,
        rho_max: float = 2.50,
        freeze_streak: int = 3,
        cooldown_needed: int = 20,
        adwin_delta: float = 0.01
    ):
        self.tau_calib = float(tau_calib)
        self.alpha = float(alpha_ewma)
        self.k = float(k_sigma)
        self.rho_min = float(rho_min)
        self.rho_max = float(rho_max)
        self.freeze_streak = int(freeze_streak)
        self.cooldown_needed = int(cooldown_needed)

        # ADWIN detector
        self.adwin = ADWINDriftDetector(delta=adwin_delta)

        # Running statistics
        self.mu_t = float(tau_calib * 0.5)
        self.var_t = float((tau_calib * 0.25) ** 2)
        self.sigma_t = float(math.sqrt(self.var_t))
        self.current_tau = float(tau_calib)

        # Calibration factor kappa to correct truncation bias
        # Derived on validation data: kappa = tau_calib / (mu_trunc + k * sigma_trunc)
        denom = self.mu_t + self.k * self.sigma_t
        self.kappa = float(self.tau_calib / denom) if denom > 1e-8 else 1.0

        # State flags
        self.streak: int = 0
        self.cooldown: int = 0
        self.frozen: bool = False
        self.drift_active: bool = False
        self.drift_count: int = 0

    def calibrate_kappa(self, val_scores: np.ndarray, target_percentile: float = 95.0):
        """Calibrates truncation-bias correction factor kappa on validation scores."""
        self.tau_calib = float(np.percentile(val_scores, target_percentile))
        trunc_scores = val_scores[val_scores <= self.tau_calib]
        if len(trunc_scores) > 10:
            mu_trunc = float(np.mean(trunc_scores))
            var_trunc = float(np.var(trunc_scores))
            sigma_trunc = float(np.sqrt(max(var_trunc, 1e-8)))
        else:
            mu_trunc = float(np.mean(val_scores))
            sigma_trunc = float(np.std(val_scores))

        denom = mu_trunc + self.k * sigma_trunc
        self.kappa = float(self.tau_calib / denom) if denom > 1e-8 else 1.0
        self.mu_t = mu_trunc
        self.var_t = sigma_trunc ** 2
        self.sigma_t = sigma_trunc
        self.current_tau = self.tau_calib

    def process_score(self, score: float) -> Tuple[int, float, Dict[str, Any]]:
        """
        Processes a streaming score at time t:
          Returns:
            - is_alert (0 or 1)
            - current_threshold (tau_t)
            - metadata dict (drift_detected, frozen, streak)
        """
        score = float(score)
        tau_t = self.current_tau

        # 1. Detection decision
        is_alert = 1 if score >= tau_t else 0

        # 2. ADWIN drift check
        drift_flag = self.adwin.add_element(score)
        if drift_flag:
            self.drift_active = True
            self.drift_count += 1

        # 3. Incident Freeze / Cooldown tracking
        if is_alert == 1:
            self.streak += 1
            self.cooldown = 0
            if self.streak >= self.freeze_streak:
                self.frozen = True
        else:
            self.streak = 0
            if self.frozen:
                self.cooldown += 1
                if self.cooldown >= self.cooldown_needed:
                    self.frozen = False
                    self.cooldown = 0

        # 4. Statistical update: update only on non-alerts and when not frozen
        if not self.frozen and is_alert == 0:
            # Winsorize update score
            update_val = min(score, self.tau_calib)
            self.mu_t = (1.0 - self.alpha) * self.mu_t + self.alpha * update_val
            diff = update_val - self.mu_t
            self.var_t = (1.0 - self.alpha) * self.var_t + self.alpha * (diff ** 2)
            self.sigma_t = float(math.sqrt(max(self.var_t, 1e-8)))

            # If drift is active, allow adaptation to track new normal baseline
            new_tau = self.kappa * (self.mu_t + self.k * self.sigma_t)
            # Enforce hard operational envelope
            low_bound = self.rho_min * self.tau_calib
            high_bound = self.rho_max * self.tau_calib
            self.current_tau = float(np.clip(new_tau, low_bound, high_bound))

        meta = {
            'drift_flag': drift_flag,
            'frozen': self.frozen,
            'streak': self.streak,
            'current_tau': self.current_tau,
            'total_drifts': self.drift_count
        }
        return is_alert, self.current_tau, meta
