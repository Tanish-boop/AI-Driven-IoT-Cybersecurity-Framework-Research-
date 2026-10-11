"""
Corrected Experiment E4: Defensive-Response Policy Evaluation
Strictly enforces:
  - Training RL policies on X_sup / y_sup ONLY (dedicated training partition).
  - Reserving X_test EXCLUSIVELY for held-out evaluation scenarios.
  - Reward sensitivity analysis across benign block penalties (-10, -25, -50, -100).
  - Preserving historical contaminated results in e4_policy_results_historical.csv.
  - Saving corrected outputs to e4_policy_results_corrected.csv.
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch

sys.path.append(os.path.abspath('.'))

from src.detection.autoencoders import DenseAutoencoder
from src.response.environment import IoTDefenseEnv
from src.response.policies import RuleBasedPolicy, QLearningPolicy, DQNPolicy

def evaluate_policy_on_env(policy, env, policy_type='rule_based'):
    (state_id, state_vec) = env.reset()
    done = False
    
    total_reward = 0.0
    attack_total = 0
    attack_contained = 0
    benign_total = 0
    benign_falsely_blocked = 0
    disruption_penalty = 0.0
    
    start_t = time.time()
    steps = 0
    
    while not done:
        steps += 1
        if policy_type == 'rule_based':
            err_val = env.error_stream[env.current_step]
            alert_count = min(env.consecutive_alerts, 3)
            action = policy.select_action(err_val, alert_count)
        elif policy_type == 'q_learning':
            action = policy.select_action(state_id, evaluate=True)
        elif policy_type == 'dqn':
            action = policy.select_action(state_vec, evaluate=True)

        (next_state_id, next_state_vec), reward, done, info = env.step(action)
        state_id, state_vec = next_state_id, next_state_vec
        
        total_reward += reward
        is_att = info['is_attack']
        act = info['action']
        
        if is_att == 1:
            attack_total += 1
            if act in [2, 3]: # RATE_LIMIT or BLOCK
                attack_contained += 1
        else:
            benign_total += 1
            if act == 3: # BLOCK
                benign_falsely_blocked += 1
            if act in [2, 3]:
                disruption_penalty += (3.0 if act == 2 else 10.0)

    elapsed_ms = ((time.time() - start_t) / max(steps, 1)) * 1000.0
    
    containment_rate = (attack_contained / max(attack_total, 1)) * 100.0
    false_block_rate = (benign_falsely_blocked / max(benign_total, 1)) * 100.0

    return {
        'total_reward': float(total_reward),
        'containment_rate': float(containment_rate),
        'false_block_rate': float(false_block_rate),
        'disruption_penalty': float(disruption_penalty),
        'latency_ms': float(elapsed_ms),
        'attack_total': int(attack_total),
        'attack_contained': int(attack_contained),
        'benign_total': int(benign_total),
        'benign_falsely_blocked': int(benign_falsely_blocked)
    }

def main():
    print("=" * 60, flush=True)
    print("STARTING CORRECTED EXPERIMENT E4: DEFENSIVE-RESPONSE POLICY EVALUATION", flush=True)
    print("=" * 60, flush=True)

    metrics_dir = 'results/metrics'
    tables_dir = 'results/tables'
    figures_dir = 'results/figures'
    paper_tables_dir = 'paper/tables'
    paper_figures_dir = 'paper/figures'

    for d in [metrics_dir, tables_dir, figures_dir, paper_tables_dir, paper_figures_dir]:
        os.makedirs(d, exist_ok=True)

    # Preserve historical contaminated results if not already backed up
    hist_file = os.path.join(metrics_dir, 'e4_policy_results_historical.csv')
    orig_file = os.path.join(metrics_dir, 'e4_policy_results.csv')
    if os.path.exists(orig_file) and not os.path.exists(hist_file):
        df_old = pd.read_csv(orig_file)
        df_old.to_csv(hist_file, index=False)
        print(f"Preserved historical contaminated E4 results to {hist_file}", flush=True)

    data_path = 'data/processed/recovery/recovery_processed.npz'
    data = np.load(data_path, allow_pickle=True)
    X_train = data['X_train']
    X_sup = data['X_sup']
    y_sup = data['y_sup']
    X_test = data['X_test']
    y_test = data['y_test_binary']

    device = torch.device('cpu')
    dense_model = DenseAutoencoder(input_dim=39).to(device)
    
    # Train Dense-AE for 5 epochs on X_train to get errors
    torch.manual_seed(42)
    optimizer = torch.optim.Adam(dense_model.parameters(), lr=0.001)
    criterion = torch.nn.MSELoss()
    train_t = torch.tensor(X_train[:10000], dtype=torch.float32)
    for epoch in range(5):
        optimizer.zero_grad()
        recon = dense_model(train_t)
        loss = criterion(recon, train_t)
        loss.backward()
        optimizer.step()

    dense_model.eval()
    with torch.no_grad():
        sup_t = torch.tensor(X_sup, dtype=torch.float32)
        sup_errs = torch.mean((sup_t - dense_model(sup_t))**2, dim=1).numpy()
        
        test_t = torch.tensor(X_test, dtype=torch.float32)
        test_errs = torch.mean((test_t - dense_model(test_t))**2, dim=1).numpy()

    sup_rates = X_sup[:, 3]
    test_rates = X_test[:, 3]

    # Training Environment: Built STRICTLY from X_sup / y_sup (40,000 samples)
    # X_test is NEVER touched during RL policy training!
    err_train_sc, rate_train_sc, label_train_sc = sup_errs[:2000], sup_rates[:2000], y_sup[:2000]
    
    # Eval Scenario 1 (Heavy Attack Stream): 5,000 to 10,000 of X_test (5,000 steps)
    err_eval1, rate_eval1, label_eval1 = test_errs[5000:10000], test_rates[5000:10000], y_test[5000:10000]

    # Eval Scenario 2 (Stealth Attack Stream): 15,000 to 20,000 of X_test (5,000 steps)
    err_eval2, rate_eval2, label_eval2 = test_errs[15000:20000], test_rates[15000:20000], y_test[15000:20000]

    seeds = [42, 123, 456, 789, 2026]
    e4_corrected_results = []
    sensitivity_results = []

    # 1. Main Corrected Run (benign_block_penalty = -10.0)
    for seed in seeds:
        print(f"\n--- RUNNING CORRECTED SEED {seed} ---", flush=True)
        np.random.seed(seed)
        torch.manual_seed(seed)

        # Rule-Based
        rule_pol = RuleBasedPolicy(tau_threshold=0.075)
        
        env_eval1 = IoTDefenseEnv(err_eval1, rate_eval1, label_eval1, max_steps=5000)
        res_rule_s1 = evaluate_policy_on_env(rule_pol, env_eval1, policy_type='rule_based')
        res_rule_s1.update({'seed': seed, 'policy': 'Rule_Based', 'scenario': 'Scenario_1_Heavy_Attack', 'benign_block_penalty': -10.0})
        e4_corrected_results.append(res_rule_s1)

        env_eval2 = IoTDefenseEnv(err_eval2, rate_eval2, label_eval2, max_steps=5000)
        res_rule_s2 = evaluate_policy_on_env(rule_pol, env_eval2, policy_type='rule_based')
        res_rule_s2.update({'seed': seed, 'policy': 'Rule_Based', 'scenario': 'Scenario_2_Stealth_Attack', 'benign_block_penalty': -10.0})
        e4_corrected_results.append(res_rule_s2)

        # Q-Learning (Trained strictly on X_sup)
        q_pol = QLearningPolicy()
        train_env = IoTDefenseEnv(err_train_sc, rate_train_sc, label_train_sc, max_steps=2000, benign_block_penalty=-10.0)
        for ep in range(15):
            (state_id, _) = train_env.reset()
            done = False
            while not done:
                act = q_pol.select_action(state_id)
                (next_sid, _), r, done, _ = train_env.step(act)
                q_pol.update(state_id, act, r, next_sid, done)
                state_id = next_sid

        env_eval1 = IoTDefenseEnv(err_eval1, rate_eval1, label_eval1, max_steps=5000)
        res_q_s1 = evaluate_policy_on_env(q_pol, env_eval1, policy_type='q_learning')
        res_q_s1.update({'seed': seed, 'policy': 'Q_Learning', 'scenario': 'Scenario_1_Heavy_Attack', 'benign_block_penalty': -10.0})
        e4_corrected_results.append(res_q_s1)

        env_eval2 = IoTDefenseEnv(err_eval2, rate_eval2, label_eval2, max_steps=5000)
        res_q_s2 = evaluate_policy_on_env(q_pol, env_eval2, policy_type='q_learning')
        res_q_s2.update({'seed': seed, 'policy': 'Q_Learning', 'scenario': 'Scenario_2_Stealth_Attack', 'benign_block_penalty': -10.0})
        e4_corrected_results.append(res_q_s2)

        # DQN (Trained strictly on X_sup)
        dqn_pol = DQNPolicy()
        train_env = IoTDefenseEnv(err_train_sc, rate_train_sc, label_train_sc, max_steps=2000, benign_block_penalty=-10.0)
        for ep in range(15):
            (state_id, state_vec) = train_env.reset()
            done = False
            while not done:
                act = dqn_pol.select_action(state_vec)
                (next_sid, next_vec), r, done, _ = train_env.step(act)
                dqn_pol.update(state_vec, act, r, next_vec, done)
                state_vec = next_vec

        env_eval1 = IoTDefenseEnv(err_eval1, rate_eval1, label_eval1, max_steps=5000)
        res_dqn_s1 = evaluate_policy_on_env(dqn_pol, env_eval1, policy_type='dqn')
        res_dqn_s1.update({'seed': seed, 'policy': 'DQN', 'scenario': 'Scenario_1_Heavy_Attack', 'benign_block_penalty': -10.0})
        e4_corrected_results.append(res_dqn_s1)

        env_eval2 = IoTDefenseEnv(err_eval2, rate_eval2, label_eval2, max_steps=5000)
        res_dqn_s2 = evaluate_policy_on_env(dqn_pol, env_eval2, policy_type='dqn')
        res_dqn_s2.update({'seed': seed, 'policy': 'DQN', 'scenario': 'Scenario_2_Stealth_Attack', 'benign_block_penalty': -10.0})
        e4_corrected_results.append(res_dqn_s2)

    # 2. Reward Sensitivity Analysis (benign_block_penalty in [-10, -25, -50, -100])
    print("\n--- RUNNING REWARD SENSITIVITY ANALYSIS ---", flush=True)
    for penalty in [-10.0, -25.0, -50.0, -100.0]:
        seed = 42
        np.random.seed(seed)
        torch.manual_seed(seed)

        # Q-Learning trained with penalty
        q_pol = QLearningPolicy()
        train_env = IoTDefenseEnv(err_train_sc, rate_train_sc, label_train_sc, max_steps=2000, benign_block_penalty=penalty)
        for ep in range(15):
            (state_id, _) = train_env.reset()
            done = False
            while not done:
                act = q_pol.select_action(state_id)
                (next_sid, _), r, done, _ = train_env.step(act)
                q_pol.update(state_id, act, r, next_sid, done)
                state_id = next_sid

        env_eval1 = IoTDefenseEnv(err_eval1, rate_eval1, label_eval1, max_steps=5000, benign_block_penalty=penalty)
        res_sens = evaluate_policy_on_env(q_pol, env_eval1, policy_type='q_learning')
        res_sens.update({'policy': 'Q_Learning', 'benign_block_penalty': penalty, 'scenario': 'Scenario_1_Heavy_Attack'})
        sensitivity_results.append(res_sens)

    df_corrected = pd.DataFrame(e4_corrected_results)
    df_corrected.to_csv(os.path.join(metrics_dir, 'e4_policy_results_corrected.csv'), index=False)
    # Also update main e4_policy_results.csv with corrected results
    df_corrected.to_csv(os.path.join(metrics_dir, 'e4_policy_results.csv'), index=False)

    df_sens = pd.DataFrame(sensitivity_results)
    df_sens.to_csv(os.path.join(metrics_dir, 'e4_reward_sensitivity.csv'), index=False)

    print("\n=== E4 CORRECTED DEFENSIVE POLICY RESULTS SUMMARY (MEAN ± STD) ===", flush=True)
    summary_rows = []
    grouped = df_corrected.groupby(['scenario', 'policy'])
    for (scen, pol), group in grouped:
        summary_rows.append({
            'Scenario': scen,
            'Policy': pol,
            'Cumulative Reward': f"{group['total_reward'].mean():.2f} ± {group['total_reward'].std():.2f}",
            'Attack Containment (%)': f"{group['containment_rate'].mean():.2f}% ± {group['containment_rate'].std():.2f}%",
            'False Block Rate (%)': f"{group['false_block_rate'].mean():.2f}% ± {group['false_block_rate'].std():.2f}%",
            'Disruption Penalty': f"{group['disruption_penalty'].mean():.2f} ± {group['disruption_penalty'].std():.2f}",
            'Latency (ms)': f"{group['latency_ms'].mean():.4f} ± {group['latency_ms'].std():.4f}"
        })

    df_summary = pd.DataFrame(summary_rows)
    df_summary.to_csv(os.path.join(metrics_dir, 'e4_policy_summary_corrected.csv'), index=False)
    df_summary.to_csv(os.path.join(metrics_dir, 'e4_policy_summary.csv'), index=False)
    print(df_summary.to_string(index=False), flush=True)

    # Save Tables
    df_summary.to_csv(os.path.join(tables_dir, 'table4_defense_policy.csv'), index=False)
    with open(os.path.join(tables_dir, 'table4_defense_policy.md'), 'w') as f:
        f.write(df_summary.to_markdown(index=False))
    with open(os.path.join(paper_tables_dir, 'table4_defense_policy.tex'), 'w') as f:
        f.write(df_summary.to_latex(index=False))

    # Generate Figure 4: Cumulative Reward Comparison
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, ax = plt.subplots(figsize=(9, 4.5))

    policies = ['Rule_Based', 'Q_Learning', 'DQN']
    rew_means = [df_corrected[(df_corrected['scenario']=='Scenario_1_Heavy_Attack') & (df_corrected['policy']==p)]['total_reward'].mean() for p in policies]
    rew_stds = [df_corrected[(df_corrected['scenario']=='Scenario_1_Heavy_Attack') & (df_corrected['policy']==p)]['total_reward'].std() for p in policies]

    x = np.arange(len(policies))
    ax.bar(x, rew_means, yerr=rew_stds, capsize=5, color=['#1f77b4', '#ff7f0e', '#2ca02c'], width=0.4)
    ax.set_xlabel('Defensive-Response Policy', fontweight='bold')
    ax.set_ylabel('Cumulative Reward', fontweight='bold')
    ax.set_title('E4 Corrected: Cumulative Reward Comparison Across Defensive Policies', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(policies)

    plt.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'figure4_defense_rewards.png'), dpi=300)
    fig.savefig(os.path.join(paper_figures_dir, 'figure4_defense_rewards.png'), dpi=300)
    plt.close()

    print("\nCorrected Experiment E4 completed successfully!", flush=True)

if __name__ == '__main__':
    main()
