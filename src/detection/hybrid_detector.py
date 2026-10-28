"""
Hybrid Detection Engine:
Combines Supervised Classification (Random Forest) and Unsupervised Anomaly Detection
(Isolation Forest or Autoencoder) via calibrated score fusion:
    S_t = alpha * p_t + (1 - alpha) * a_t

Where:
    - p_t in [0, 1]: Supervised probability of attack from Random Forest
    - a_t in [0, 1]: Normalized anomaly score from Isolation Forest or Autoencoder
    - alpha in [0, 1]: Fusion weight calibrated on validation split
"""

import os
import time
import numpy as np
import joblib
from typing import Dict, Any, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import roc_auc_score, precision_recall_curve, f1_score


class HybridDetector:
    """
    Hybrid Intrusion Detector fusing Supervised Attack Classification
    with Unsupervised Anomaly Detection.
    """
    def __init__(
        self,
        n_estimators_rf: int = 100,
        max_depth_rf: int = 12,
        n_estimators_if: int = 100,
        alpha: float = 0.65,
        random_state: int = 42
    ):
        self.alpha = float(alpha)
        self.random_state = random_state
        
        # Models
        self.rf = RandomForestClassifier(
            n_estimators=n_estimators_rf,
            max_depth=max_depth_rf,
            random_state=random_state,
            n_jobs=-1
        )
        self.iforest = IsolationForest(
            n_estimators=n_estimators_if,
            contamination='auto',
            random_state=random_state,
            n_jobs=-1
        )
        
        # Calibration bounds for unsupervised anomaly score
        self.a_min: float = 0.0
        self.a_max: float = 1.0
        self.calibrated_threshold: float = 0.50
        self.is_fitted: bool = False

    def fit(
        self,
        X_sup_train: np.ndarray,
        y_sup_train: np.ndarray,
        X_unsup_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None
    ) -> "HybridDetector":
        """
        Trains the Supervised and Unsupervised components and calibrates
        score normalization and fusion weights on the validation split.
        """
        # 1. Fit Random Forest on labeled subset
        t0 = time.time()
        self.rf.fit(X_sup_train, y_sup_train)
        rf_time = time.time() - t0

        # 2. Fit Isolation Forest on benign/unsupervised subset
        t0 = time.time()
        self.iforest.fit(X_unsup_train)
        if_time = time.time() - t0

        # 3. Calibrate anomaly score min/max on training/validation normal data
        if X_val is not None:
            raw_val_if = -self.iforest.decision_function(X_val)
            self.a_min = float(np.percentile(raw_val_if, 1))
            self.a_max = float(np.percentile(raw_val_if, 99))
            if self.a_max <= self.a_min:
                self.a_max = self.a_min + 1.0

            # If validation labels provided, calibrate optimal alpha and threshold
            if y_val is not None:
                self._calibrate_fusion(X_val, y_val)
        else:
            raw_train_if = -self.iforest.decision_function(X_unsup_train[:10000])
            self.a_min = float(np.percentile(raw_train_if, 1))
            self.a_max = float(np.percentile(raw_train_if, 99))
            if self.a_max <= self.a_min:
                self.a_max = self.a_min + 1.0

        self.is_fitted = True
        return self

    def _calibrate_fusion(self, X_val: np.ndarray, y_val: np.ndarray):
        """Calibrates alpha and decision threshold on validation set."""
        p_val = self.rf.predict_proba(X_val)[:, 1]
        raw_a_val = -self.iforest.decision_function(X_val)
        a_val = np.clip((raw_a_val - self.a_min) / (self.a_max - self.a_min + 1e-8), 0.0, 1.0)

        best_f1 = -1.0
        best_alpha = self.alpha
        best_tau = 0.50

        # Grid search over alpha values on validation split
        for candidate_alpha in [0.3, 0.5, 0.65, 0.75, 0.85]:
            fused_val = candidate_alpha * p_val + (1.0 - candidate_alpha) * a_val
            # Evaluate across thresholds
            for candidate_tau in np.linspace(0.30, 0.70, 9):
                preds = (fused_val >= candidate_tau).astype(int)
                f1 = f1_score(y_val, preds, zero_division=0)
                if f1 > best_f1:
                    best_f1 = f1
                    best_alpha = candidate_alpha
                    best_tau = candidate_tau

        self.alpha = float(best_alpha)
        self.calibrated_threshold = float(best_tau)

    def normalize_anomaly_score(self, raw_scores: np.ndarray) -> np.ndarray:
        """Normalizes raw decision function scores to [0, 1]."""
        norm = (raw_scores - self.a_min) / (self.a_max - self.a_min + 1e-8)
        return np.clip(norm, 0.0, 1.0)

    def predict_components(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Returns individual component scores and fused score:
          - 'p_sup': Random Forest attack probability in [0, 1]
          - 'a_unsup': Normalized Isolation Forest anomaly score in [0, 1]
          - 's_fused': Fused hybrid score in [0, 1]
        """
        p_sup = self.rf.predict_proba(X)[:, 1]
        raw_a = -self.iforest.decision_function(X)
        a_unsup = self.normalize_anomaly_score(raw_a)
        s_fused = self.alpha * p_sup + (1.0 - self.alpha) * a_unsup
        return {
            'p_sup': p_sup,
            'a_unsup': a_unsup,
            's_fused': s_fused
        }

    def predict(self, X: np.ndarray, threshold: Optional[float] = None) -> np.ndarray:
        """Binary predictions using calibrated threshold."""
        tau = threshold if threshold is not None else self.calibrated_threshold
        scores = self.predict_components(X)['s_fused']
        return (scores >= tau).astype(int)

    def save(self, filepath: str):
        """Saves detector state."""
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> "HybridDetector":
        """Loads saved detector."""
        return joblib.load(filepath)
