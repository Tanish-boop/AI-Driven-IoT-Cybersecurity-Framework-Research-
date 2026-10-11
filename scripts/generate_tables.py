"""
Generate LaTeX and Markdown Tables from Full 5-Seed Benchmark Results
"""

import os
import pandas as pd

def main():
    metrics_dir = 'results/metrics'
    results_file = os.path.join(metrics_dir, 'full_benchmark_results.csv')
    summary_file = os.path.join(metrics_dir, 'full_benchmark_summary.csv')
    tables_dir = 'results/tables'
    paper_tables_dir = 'paper/tables'

    os.makedirs(tables_dir, exist_ok=True)
    os.makedirs(paper_tables_dir, exist_ok=True)

    if not os.path.exists(results_file):
        print(f"Results file not found: {results_file}")
        return

    df_res = pd.read_csv(results_file)

    # 1. Main Performance Comparison Table Across 5 Seeds (Base Stream)
    base_res = df_res[df_res['experiment'] == 'base_stream'].copy()
    
    # Compute mean and std across seeds
    grouped = base_res.groupby(['model', 'strategy']).agg(
        prec_mean=('precision', 'mean'), prec_std=('precision', 'std'),
        rec_mean=('recall', 'mean'), rec_std=('recall', 'std'),
        f1_mean=('f1_score', 'mean'), f1_std=('f1_score', 'std'),
        fpr_mean=('fpr', 'mean'), fpr_std=('fpr', 'std'),
        pr_auc_mean=('pr_auc', 'mean'), pr_auc_std=('pr_auc', 'std'),
        roc_auc_mean=('roc_auc', 'mean'), roc_auc_std=('roc_auc', 'std')
    ).reset_index()

    table1 = pd.DataFrame()
    table1['Model'] = grouped['model']
    table1['Threshold Strategy'] = grouped['strategy']
    table1['Precision'] = grouped.apply(lambda r: f"{r['prec_mean']:.4f} ± {r['prec_std']:.4f}", axis=1)
    table1['Recall'] = grouped.apply(lambda r: f"{r['rec_mean']:.4f} ± {r['rec_std']:.4f}", axis=1)
    table1['F1-Score'] = grouped.apply(lambda r: f"{r['f1_mean']:.4f} ± {r['f1_std']:.4f}", axis=1)
    table1['FPR'] = grouped.apply(lambda r: f"{r['fpr_mean']:.4f} ± {r['fpr_std']:.4f}", axis=1)
    table1['PR-AUC'] = grouped.apply(lambda r: f"{r['pr_auc_mean']:.4f} ± {r['pr_auc_std']:.4f}", axis=1)
    table1['ROC-AUC'] = grouped.apply(lambda r: f"{r['roc_auc_mean']:.4f} ± {r['roc_auc_std']:.4f}", axis=1)

    table1.to_csv(os.path.join(tables_dir, 'table1_base_performance.csv'), index=False)
    with open(os.path.join(tables_dir, 'table1_base_performance.md'), 'w') as f:
        f.write(table1.to_markdown(index=False))
    with open(os.path.join(paper_tables_dir, 'table1_base_performance.tex'), 'w') as f:
        f.write(table1.to_latex(index=False))

    # 2. Rate-Shift Stress Test Table
    stress_res = df_res[df_res['experiment'] == 'feature_stress_test'].copy()
    if not stress_res.empty:
        grouped_stress = stress_res.groupby(['model', 'strategy']).agg(
            prec_mean=('precision', 'mean'), prec_std=('precision', 'std'),
            rec_mean=('recall', 'mean'), rec_std=('recall', 'std'),
            f1_mean=('f1_score', 'mean'), f1_std=('f1_score', 'std'),
            fpr_mean=('fpr', 'mean'), fpr_std=('fpr', 'std'),
            pr_auc_mean=('pr_auc', 'mean'), pr_auc_std=('pr_auc', 'std'),
            roc_auc_mean=('roc_auc', 'mean'), roc_auc_std=('roc_auc', 'std')
        ).reset_index()

        table2 = pd.DataFrame()
        table2['Model'] = grouped_stress['model']
        table2['Strategy'] = grouped_stress['strategy']
        table2['Precision'] = grouped_stress.apply(lambda r: f"{r['prec_mean']:.4f} ± {r['prec_std']:.4f}", axis=1)
        table2['Recall'] = grouped_stress.apply(lambda r: f"{r['rec_mean']:.4f} ± {r['rec_std']:.4f}", axis=1)
        table2['F1-Score'] = grouped_stress.apply(lambda r: f"{r['f1_mean']:.4f} ± {r['f1_std']:.4f}", axis=1)
        table2['FPR'] = grouped_stress.apply(lambda r: f"{r['fpr_mean']:.4f} ± {r['fpr_std']:.4f}", axis=1)

        table2.to_csv(os.path.join(tables_dir, 'table2_stress_test_performance.csv'), index=False)
        with open(os.path.join(tables_dir, 'table2_stress_test_performance.md'), 'w') as f:
            f.write(table2.to_markdown(index=False))
        with open(os.path.join(paper_tables_dir, 'table2_stress_test_performance.tex'), 'w') as f:
            f.write(table2.to_latex(index=False))

    print("Tables generated successfully in results/tables and paper/tables!")

if __name__ == '__main__':
    main()
