"""
Extended Statistical Evidence & Hypothesis Testing Script
Computes:
  - Exact 95% Confidence Intervals (t-distribution, df=4)
  - Paired t-tests & Wilcoxon signed-rank tests
  - Holm-Bonferroni multiple testing corrections
  - Effect size (Cohen's d for paired samples)
"""

import json
import numpy as np
import pandas as pd
from scipy import stats

def compute_paired_stats(x, y, name_x, name_y, metric_name):
    diffs = np.array(x) - np.array(y)
    n = len(diffs)
    mean_diff = float(np.mean(diffs))
    std_diff = float(np.std(diffs, ddof=1))
    
    # Paired t-test
    t_stat, t_pval = stats.ttest_rel(x, y)
    
    # Wilcoxon signed-rank test (two-sided)
    try:
        w_stat, w_pval = stats.wilcoxon(x, y, alternative='two-sided')
    except Exception:
        w_stat, w_pval = np.nan, np.nan
        
    # Cohen's d for paired samples
    cohen_d = float(mean_diff / std_diff) if std_diff > 1e-8 else np.nan
    
    # 95% CI for difference: t(0.975, 4) = 2.7764
    t_crit = stats.t.ppf(0.975, df=n-1)
    se_diff = std_diff / np.sqrt(n)
    ci_lower = mean_diff - t_crit * se_diff
    ci_upper = mean_diff + t_crit * se_diff
    
    return {
        'comparison': f"{name_x} vs {name_y} ({metric_name})",
        'n_seeds': n,
        'mean_x': float(np.mean(x)),
        'mean_y': float(np.mean(y)),
        'mean_difference': mean_diff,
        'std_difference': std_diff,
        'ci_95_lower': float(ci_lower),
        'ci_95_upper': float(ci_upper),
        't_statistic': float(t_stat),
        't_p_value': float(t_pval),
        'wilcoxon_statistic': float(w_stat),
        'wilcoxon_p_value': float(w_pval),
        'cohen_d': cohen_d
    }

def main():
    results = []

    # 1. Detection Benchmarks (E1, E2, E3)
    df_det = pd.read_csv('results/metrics/full_benchmark_results.csv')
    df_base = df_det[df_det['experiment'] == 'base_stream']
    
    # Excluded EWMA vs Fixed 95th F1
    f1_ex = df_base[(df_base['model'] == 'Dense-AE') & (df_base['strategy'] == 'Excluded_EWMA')]['f1_score'].values
    f1_f95 = df_base[(df_base['model'] == 'Dense-AE') & (df_base['strategy'] == 'Fixed_95')]['f1_score'].values
    results.append(compute_paired_stats(f1_ex, f1_f95, 'Dense-AE Excluded_EWMA', 'Dense-AE Fixed_95', 'F1-Score'))

    # Fixed 95th vs Fixed 99th F1
    f1_f99 = df_base[(df_base['model'] == 'Dense-AE') & (df_base['strategy'] == 'Fixed_99')]['f1_score'].values
    results.append(compute_paired_stats(f1_f95, f1_f99, 'Dense-AE Fixed_95', 'Dense-AE Fixed_99', 'F1-Score'))

    # Dense-AE Fixed 95 vs Isolation Forest F1
    f1_if = df_base[(df_base['model'] == 'Isolation_Forest') & (df_base['strategy'] == 'Fixed_95')]['f1_score'].values
    results.append(compute_paired_stats(f1_f95, f1_if, 'Dense-AE Fixed_95', 'Isolation_Forest Fixed_95', 'F1-Score'))

    # XGBoost Oracle vs Dense-AE Excluded EWMA F1
    f1_xgb = df_base[df_base['model'] == 'XGBoost_Oracle']['f1_score'].values
    results.append(compute_paired_stats(f1_xgb, f1_ex, 'XGBoost_Oracle', 'Dense-AE Excluded_EWMA', 'F1-Score'))

    # 2. Defensive Mitigation (E4)
    df_e4 = pd.read_csv('results/metrics/e4_policy_results_corrected.csv')
    df_s1 = df_e4[df_e4['scenario'] == 'Scenario_1_Heavy_Attack']
    
    cont_dqn = df_s1[df_s1['policy'] == 'DQN']['containment_rate'].values
    cont_q = df_s1[df_s1['policy'] == 'Q_Learning']['containment_rate'].values
    results.append(compute_paired_stats(cont_dqn, cont_q, 'DQN', 'Tabular Q-Learning', 'Scenario 1 Attack Containment'))

    # 3. Integrated Ablation (E7)
    df_e7 = pd.read_csv('results/metrics/e7_ablation_results.csv')
    
    f1_full = df_e7[df_e7['variant_id'] == 'Full_Proposed_Framework']['f1_score'].values
    f1_base_arch = df_e7[df_e7['variant_id'] == 'Base_Paper_Baseline']['f1_score'].values
    results.append(compute_paired_stats(f1_full, f1_base_arch, 'Full Proposed Framework', 'Base Paper Architecture', 'Integrated F1-Score'))

    f1_no_adapt = df_e7[df_e7['variant_id'] == 'Ablation_NoAdaptive']['f1_score'].values
    results.append(compute_paired_stats(f1_full, f1_no_adapt, 'Full Framework', 'Ablation (-Adaptive)', 'Integrated F1-Score'))

    cont_full = df_e7[df_e7['variant_id'] == 'Full_Proposed_Framework']['containment_rate_pct'].values
    cont_no_rl = df_e7[df_e7['variant_id'] == 'Ablation_NoRL']['containment_rate_pct'].values
    results.append(compute_paired_stats(cont_full, cont_no_rl, 'Full Framework', 'Ablation (-RL Defense)', 'Attack Containment Rate'))

    # Holm-Bonferroni correction
    p_vals = [r['t_p_value'] for r in results]
    m = len(p_vals)
    sorted_indices = np.argsort(p_vals)
    adj_p_vals = np.zeros(m)
    for rank, idx in enumerate(sorted_indices):
        adj_p = min(1.0, p_vals[idx] * (m - rank))
        adj_p_vals[idx] = adj_p
    # Ensure monotonicity
    for i in range(1, m):
        if adj_p_vals[sorted_indices[i]] < adj_p_vals[sorted_indices[i-1]]:
            adj_p_vals[sorted_indices[i]] = adj_p_vals[sorted_indices[i-1]]

    for i, r in enumerate(results):
        r['holm_bonferroni_t_p_value'] = float(adj_p_vals[i])
        r['statistically_significant_alpha_005'] = bool(adj_p_vals[i] < 0.05)

    # Save to JSON
    with open('results/metrics/extended_statistical_tests.json', 'w') as f:
        json.dump(results, f, indent=2)

    # Save formatted Markdown
    md_rows = [
        "| Comparison | Metric | Mean Diff (95% CI) | Paired t-stat | t p-value | Holm-Bonf p-val | Wilcoxon W (p-val) | Cohen's d | Significant ($\\alpha=0.05$) |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |"
    ]
    for r in results:
        ci_str = f"+{r['mean_difference']:.4f} [{r['ci_95_lower']:.4f}, {r['ci_95_upper']:.4f}]" if r['mean_difference'] >= 0 else f"{r['mean_difference']:.4f} [{r['ci_95_lower']:.4f}, {r['ci_95_upper']:.4f}]"
        sig_str = "**YES**" if r['statistically_significant_alpha_005'] else "No"
        md_rows.append(
            f"| {r['comparison'].split('(')[0].strip()} | {r['comparison'].split('(')[1].replace(')', '').strip()} | {ci_str} | t={r['t_statistic']:.3f} | p={r['t_p_value']:.4e} | p={r['holm_bonferroni_t_p_value']:.4e} | W={r['wilcoxon_statistic']:.1f} (p={r['wilcoxon_p_value']:.4f}) | d={r['cohen_d']:.2f} | {sig_str} |"
        )
    
    with open('results/tables/extended_statistical_tests.md', 'w') as f:
        f.write("\n".join(md_rows) + "\n")

    print("Extended statistical tests generated successfully!")

if __name__ == '__main__':
    main()
