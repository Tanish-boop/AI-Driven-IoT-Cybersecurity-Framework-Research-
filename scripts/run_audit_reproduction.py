"""
Master Audit Reproduction Script: E1 through E8
Executes all experiment benchmarks, logs environment, runtime, exit codes, and output hashes,
and archives the newly produced artifacts to results/audit_rerun_20261011/
"""

import os
import sys
import time
import json
import hashlib
import platform
import subprocess
import shutil

def get_file_sha256(filepath):
    if not os.path.exists(filepath):
        return "MISSING"
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    audit_dir = 'results/audit_rerun_20261011'
    os.makedirs(audit_dir, exist_ok=True)
    os.makedirs(os.path.join(audit_dir, 'metrics'), exist_ok=True)
    os.makedirs(os.path.join(audit_dir, 'tables'), exist_ok=True)

    experiments = [
        {
            'id': 'E1_E2_E3_E8',
            'name': 'Detection Baselines & Threshold Stress Benchmark',
            'script': 'scripts/run_full_benchmark.py',
            'expected_outputs': [
                'results/metrics/full_benchmark_results.csv',
                'results/metrics/full_benchmark_summary.csv',
                'results/metrics/baseline_errors.npz',
                'results/metrics/statistical_tests.json'
            ]
        },
        {
            'id': 'E4',
            'name': 'Un-Contaminated Defensive RL Response Experiment',
            'script': 'scripts/run_e4_defense_experiment.py',
            'expected_outputs': [
                'results/metrics/e4_policy_results_corrected.csv',
                'results/metrics/e4_policy_summary_corrected.csv',
                'results/metrics/e4_reward_sensitivity.csv'
            ]
        },
        {
            'id': 'E5',
            'name': 'NIST FIPS 203 ML-KEM Post-Quantum Cryptography Benchmark',
            'script': 'scripts/run_e5_crypto_benchmark.py',
            'expected_outputs': [
                'results/metrics/e5_raw_results.csv',
                'results/metrics/e5_summary.csv',
                'results/metrics/e5_crypto_environment.json'
            ]
        },
        {
            'id': 'E6',
            'name': 'Integrity Verification Architecture Benchmark',
            'script': 'scripts/run_e6_integrity_benchmark.py',
            'expected_outputs': [
                'results/metrics/e6_raw_results.csv',
                'results/metrics/e6_summary.csv',
                'results/metrics/e6_scaling_summary.csv',
                'results/metrics/e6_integrity_environment.json'
            ]
        },
        {
            'id': 'E7',
            'name': 'Full Integrated Framework Ablation Benchmark',
            'script': 'scripts/run_e7_ablation_experiment.py',
            'expected_outputs': [
                'results/metrics/e7_ablation_results.csv',
                'results/metrics/e7_ablation_summary.csv',
                'results/tables/table7_ablation_comparison.md'
            ]
        }
    ]

    import torch, sklearn, xgboost, cryptography
    env_metadata = {
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'python_version': sys.version,
        'platform': platform.platform(),
        'cpu_arch': platform.machine(),
        'torch_version': torch.__version__,
        'sklearn_version': sklearn.__version__,
        'xgboost_version': xgboost.__version__,
        'cryptography_version': cryptography.__version__,
    }

    audit_log = {
        'environment': env_metadata,
        'runs': []
    }

    print("============================================================")
    print("STARTING COMPLETE EVIDENCE-FIRST AUDIT REPRODUCTION (E1-E8)")
    print("============================================================")

    total_start = time.time()

    for exp in experiments:
        exp_id = exp['id']
        exp_name = exp['name']
        print(f"\n--- RERUNNING {exp_id}: {exp_name} ---", flush=True)
        
        t0 = time.time()
        res = subprocess.run([sys.executable, exp['script']], capture_output=True, text=True)
        t1 = time.time()
        duration = t1 - t0
        exit_code = res.returncode
        
        file_hashes = {}
        copied_files = []
        for out_f in exp['expected_outputs']:
            sha = get_file_sha256(out_f)
            file_hashes[out_f] = sha
            if sha != "MISSING":
                rel = os.path.relpath(out_f, 'results')
                dest = os.path.join(audit_dir, rel)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(out_f, dest)
                copied_files.append(dest)
                
        status = 'REPRODUCED' if exit_code == 0 and all(h != 'MISSING' for h in file_hashes.values()) else 'NOT REPRODUCED'
        
        entry = {
            'experiment_id': exp_id,
            'name': exp_name,
            'command': f"python {exp['script']}",
            'runtime_seconds': round(duration, 2),
            'exit_code': exit_code,
            'status': status,
            'output_hashes': file_hashes,
            'copied_artifacts': copied_files,
            'stderr_snippet': res.stderr[-300:] if res.stderr else ''
        }
        audit_log['runs'].append(entry)
        print(f"--> Status: {status} | Duration: {duration:.2f}s | Exit: {exit_code}", flush=True)

    total_duration = time.time() - total_start
    audit_log['total_runtime_seconds'] = round(total_duration, 2)

    manifest_path = os.path.join(audit_dir, 'audit_reproduction_manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(audit_log, f, indent=2)

    print("\n============================================================")
    print(f"AUDIT REPRODUCTION COMPLETED IN {total_duration:.2f}s")
    print(f"Manifest saved to {manifest_path}")
    print("============================================================")

if __name__ == '__main__':
    main()
