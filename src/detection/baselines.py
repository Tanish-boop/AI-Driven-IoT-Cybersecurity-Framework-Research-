"""
Baselines: Isolation Forest (Unsupervised) and XGBoost Classifier (Supervised Oracle Reference)
"""

import numpy as np
from sklearn.ensemble import IsolationForest
import xgboost as xgb

def train_isolation_forest(X_train, random_state=42):
    print("Training Isolation Forest baseline...")
    clf = IsolationForest(
        n_estimators=100,
        contamination='auto',
        random_state=random_state,
        n_jobs=-1
    )
    clf.fit(X_train)
    return clf

def evaluate_isolation_forest(clf, X):
    # Isolation forest outputs negative scores for anomalies
    scores = -clf.decision_function(X)
    return scores

def train_xgboost_oracle(X_sup_train, y_sup_train, random_state=42):
    print("Training XGBoost Supervised Oracle Reference...")
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=random_state,
        n_jobs=-1,
        eval_metric='logloss'
    )
    model.fit(X_sup_train, y_sup_train)
    return model

def predict_xgboost_oracle(model, X):
    probs = model.predict_proba(X)[:, 1]
    return probs
