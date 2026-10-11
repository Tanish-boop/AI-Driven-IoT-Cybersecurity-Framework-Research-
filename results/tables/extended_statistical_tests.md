| Comparison | Metric | Mean Diff (95% CI) | Paired t-stat | t p-value | Holm-Bonf p-val | Wilcoxon W (p-val) | Cohen's d | Significant ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| Dense-AE Excluded_EWMA vs Dense-AE Fixed_95 | F1-Score | +0.0160 [0.0147, 0.0173] | t=33.805 | p=4.5675e-06 | p=2.7405e-05 | W=0.0 (p=0.0625) | d=15.12 | **YES** |
| Dense-AE Fixed_95 vs Dense-AE Fixed_99 | F1-Score | +0.0195 [0.0183, 0.0207] | t=46.211 | p=1.3116e-06 | p=1.0493e-05 | W=0.0 (p=0.0625) | d=20.67 | **YES** |
| Dense-AE Fixed_95 vs Isolation_Forest Fixed_95 | F1-Score | +0.1089 [0.0978, 0.1201] | t=27.183 | p=1.0891e-05 | p=5.4456e-05 | W=0.0 (p=0.0625) | d=12.16 | **YES** |
| XGBoost_Oracle vs Dense-AE Excluded_EWMA | F1-Score | +0.0254 [0.0235, 0.0274] | t=36.223 | p=3.4676e-06 | p=2.4273e-05 | W=0.0 (p=0.0625) | d=16.20 | **YES** |
| DQN vs Tabular Q-Learning | Scenario 1 Attack Containment | +10.8078 [-3.9017, 25.5173] | t=2.040 | p=1.1094e-01 | p=2.2189e-01 | W=1.0 (p=0.1250) | d=0.91 | No |
| Full Proposed Framework vs Base Paper Architecture | Integrated F1-Score | +0.0131 [0.0113, 0.0149] | t=19.888 | p=3.7712e-05 | p=1.5085e-04 | W=0.0 (p=0.0625) | d=8.89 | **YES** |
| Full Framework vs Ablation | -Adaptive | +0.0131 [0.0113, 0.0149] | t=19.888 | p=3.7712e-05 | p=1.5085e-04 | W=0.0 (p=0.0625) | d=8.89 | **YES** |
| Full Framework vs Ablation | -RL Defense | +1.2338 [-2.2835, 4.7511] | t=0.974 | p=3.8526e-01 | p=3.8526e-01 | W=4.0 (p=0.4375) | d=0.44 | No |
