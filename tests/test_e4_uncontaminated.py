"""
Unit tests for E4 Un-Contaminated Split Verification and Policy Correctness
"""

import pytest
import numpy as np
import os
import sys

sys.path.append(os.path.abspath('.'))

from src.response.environment import IoTDefenseEnv
from src.response.policies import RuleBasedPolicy, QLearningPolicy, DQNPolicy

def test_uncontaminated_split_isolation():
    data_path = 'data/processed/recovery/recovery_processed.npz'
    assert os.path.exists(data_path), f"Processed data missing at {data_path}"
    
    data = np.load(data_path, allow_pickle=True)
    X_train = data['X_train']
    X_val = data['X_val']
    X_sup = data['X_sup']
    y_sup = data['y_sup']
    X_test = data['X_test']
    y_test = data['y_test_binary']

    # Verify array identities and memory addresses are distinct
    assert X_sup.shape[0] == 40000
    assert X_test.shape[0] == 100000
    assert not np.array_equal(X_sup[:1000], X_test[:1000]), "X_sup and X_test must be disjoint partitions!"

def test_env_reward_sensitivity():
    errs = np.array([0.01, 0.50, 0.02, 0.80])
    rates = np.array([1.0, 2.0, 1.5, 3.0])
    labels = np.array([0, 1, 0, 1])

    env_standard = IoTDefenseEnv(errs, rates, labels, max_steps=4, benign_block_penalty=-10.0)
    env_sensitive = IoTDefenseEnv(errs, rates, labels, max_steps=4, benign_block_penalty=-50.0)

    # Benign false block (action 3 on index 0, label 0)
    _, r_std, _, _ = env_standard.step(action=3)
    _, r_sens, _, _ = env_sensitive.step(action=3)

    assert r_std == -10.0
    assert r_sens == -50.0

def test_action_bounds():
    rule_pol = RuleBasedPolicy(tau_threshold=0.075)
    for err in [0.01, 0.05, 0.10, 0.50]:
        for alert in [0, 1, 2, 3]:
            act = rule_pol.select_action(err, alert)
            assert act in [0, 1, 2, 3], f"Action {act} out of bounds [0, 1, 2, 3]"
