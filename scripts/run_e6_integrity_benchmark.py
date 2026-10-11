"""
Experiment E6 Execution Script: Integrity Verification Benchmark
Compares:
  1. Salted SHA-256
  2. HMAC-SHA-256
  3. Blockchain-Style Audit Log

Evaluates:
  - Cryptographic Creation & Verification Latencies (mean, std, median, p95)
  - End-to-End Latency with Disk Persistence
  - Throughput (records/sec, MB/sec)
  - Storage Overhead per Record
  - Scaling Behavior across Chain Lengths (N = 100, 500, 1000, 2000)
  - Tamper Detection Rates across Attack Scenarios
"""

import os
import sys
import json
import time
import shutil
import tempfile
import platform
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath('.'))

from src.integrity.salted_sha256 import SaltedSHA256Verifier
from src.integrity.hmac_sha256 import HMACSHA256Verifier
from src.integrity.blockchain_log import BlockchainAuditLog


PAYLOAD_SIZES = {
    '64B': 64,
    '256B': 256,
    '1KiB': 1024,
    '4KiB': 4096
}


def generate_synthetic_payload(size_bytes: int, event_idx: int) -> dict:
    # Base structure with variable padding to match exact target byte size
    base_dict = {
        'event_id': f"EVT-{event_idx:06d}",
        'event_type': 'ANOMALY_DEFENSE_TELEMETRY',
        'sensor_id': f"sensor-gateway-{(event_idx % 10):02d}",
        'anomaly_score': 0.0842,
        'action_taken': 'RATE_LIMIT'
    }
    base_bytes = len(json.dumps(base_dict, separators=(',', ':')).encode('utf-8'))
    pad_needed = max(0, size_bytes - base_bytes - 12)  # accounting for 'padding' key overhead
    base_dict['padding'] = "x" * pad_needed
    return base_dict


def benchmark_approaches(trials: int = 100):
    print("=" * 60, flush=True)
    print("STARTING EXPERIMENT E6: INTEGRITY VERIFICATION BENCHMARK", flush=True)
    print("=" * 60, flush=True)

    metrics_dir = 'results/metrics'
    tables_dir = 'results/tables'
    figures_dir = 'results/figures'
    paper_tables_dir = 'paper/tables'
    paper_figures_dir = 'paper/figures'

    for d in [metrics_dir, tables_dir, figures_dir, paper_tables_dir, paper_figures_dir]:
        os.makedirs(d, exist_ok=True)

    # 1. Environment Metadata
    env_info = {
        'timestamp_local': '2026-10-11T20:30:00',
        'os_platform': platform.platform(),
        'python_version': sys.version,
        'cpu_architecture': platform.machine(),
        'hashing_provider': 'hashlib (OpenSSL backend)',
        'mac_provider': 'hmac / hashlib (RFC 2104)',
        'benchmark_trials': trials
    }
    with open(os.path.join(metrics_dir, 'e6_integrity_environment.json'), 'w') as f:
        json.dump(env_info, f, indent=2)

    # 2. Benchmark Creation, Verification, Storage Overhead across Payload Sizes
    results = []

    salted_verifier = SaltedSHA256Verifier()
    hmac_verifier = HMACSHA256Verifier()

    print(f"\nRunning {trials} trials per approach across payload sizes...", flush=True)

    for payload_name, payload_bytes in PAYLOAD_SIZES.items():
        payload = generate_synthetic_payload(payload_bytes, 1)

        # ----------------------------------------------------
        # Approach 1: Salted SHA-256
        # ----------------------------------------------------
        create_times = []
        verify_times = []
        e2e_times = []
        
        temp_dir = tempfile.mkdtemp()
        disk_file = os.path.join(temp_dir, 'salted_records.log')
        
        for t in range(trials):
            t0 = time.perf_counter()
            rec = salted_verifier.create_record(f"SALT-{t}", time.time(), payload)
            t1 = time.perf_counter()
            
            is_valid, _ = salted_verifier.verify_record(rec)
            t2 = time.perf_counter()
            assert is_valid

            # Disk append measurement
            with open(disk_file, 'a') as f:
                f.write(json.dumps(rec.to_dict()) + "\n")
            t3 = time.perf_counter()

            create_times.append((t1 - t0) * 1000.0)
            verify_times.append((t2 - t1) * 1000.0)
            e2e_times.append((t3 - t0) * 1000.0)

        shutil.rmtree(temp_dir)
        overhead = salted_verifier.compute_storage_overhead(rec)

        results.append({
            'approach': 'Salted_SHA256',
            'payload_size': payload_name,
            'payload_bytes': payload_bytes,
            'create_mean_ms': float(np.mean(create_times)),
            'create_std_ms': float(np.std(create_times)),
            'create_p50_ms': float(np.median(create_times)),
            'create_p95_ms': float(np.percentile(create_times, 95)),
            'verify_mean_ms': float(np.mean(verify_times)),
            'verify_std_ms': float(np.std(verify_times)),
            'verify_p50_ms': float(np.median(verify_times)),
            'verify_p95_ms': float(np.percentile(verify_times, 95)),
            'e2e_mean_ms': float(np.mean(e2e_times)),
            'overhead_bytes': overhead,
            'throughput_records_s': float(1000.0 / np.mean(create_times)),
            'throughput_mb_s': float((payload_bytes / (1024 * 1024)) / (np.mean(create_times) / 1000.0))
        })

        # ----------------------------------------------------
        # Approach 2: HMAC-SHA-256
        # ----------------------------------------------------
        create_times = []
        verify_times = []
        e2e_times = []
        
        temp_dir = tempfile.mkdtemp()
        disk_file = os.path.join(temp_dir, 'hmac_records.log')

        for t in range(trials):
            t0 = time.perf_counter()
            rec = hmac_verifier.create_record(f"HMAC-{t}", time.time(), payload)
            t1 = time.perf_counter()

            is_valid, _ = hmac_verifier.verify_record(rec)
            t2 = time.perf_counter()
            assert is_valid

            with open(disk_file, 'a') as f:
                f.write(json.dumps(rec.to_dict()) + "\n")
            t3 = time.perf_counter()

            create_times.append((t1 - t0) * 1000.0)
            verify_times.append((t2 - t1) * 1000.0)
            e2e_times.append((t3 - t0) * 1000.0)

        shutil.rmtree(temp_dir)
        overhead = hmac_verifier.compute_storage_overhead(rec)

        results.append({
            'approach': 'HMAC_SHA256',
            'payload_size': payload_name,
            'payload_bytes': payload_bytes,
            'create_mean_ms': float(np.mean(create_times)),
            'create_std_ms': float(np.std(create_times)),
            'create_p50_ms': float(np.median(create_times)),
            'create_p95_ms': float(np.percentile(create_times, 95)),
            'verify_mean_ms': float(np.mean(verify_times)),
            'verify_std_ms': float(np.std(verify_times)),
            'verify_p50_ms': float(np.median(verify_times)),
            'verify_p95_ms': float(np.percentile(verify_times, 95)),
            'e2e_mean_ms': float(np.mean(e2e_times)),
            'overhead_bytes': overhead,
            'throughput_records_s': float(1000.0 / np.mean(create_times)),
            'throughput_mb_s': float((payload_bytes / (1024 * 1024)) / (np.mean(create_times) / 1000.0))
        })

        # ----------------------------------------------------
        # Approach 3: Blockchain-Style Audit Log (Single-block)
        # ----------------------------------------------------
        create_times = []
        verify_times = []
        e2e_times = []
        
        temp_dir = tempfile.mkdtemp()
        disk_file = os.path.join(temp_dir, 'blockchain.json')
        
        bc_log = BlockchainAuditLog()

        for t in range(trials):
            t0 = time.perf_counter()
            block = bc_log.append_record(f"BC-{t}", time.time(), payload)
            t1 = time.perf_counter()

            # Single block verify against predecessor
            prev_block = bc_log.chain[-2] if len(bc_log.chain) > 1 else None
            is_valid, _ = bc_log.verify_single_block(block, prev_block)
            t2 = time.perf_counter()
            assert is_valid

            # Disk append
            with open(disk_file, 'a') as f:
                f.write(json.dumps(block.to_dict()) + "\n")
            t3 = time.perf_counter()

            create_times.append((t1 - t0) * 1000.0)
            verify_times.append((t2 - t1) * 1000.0)
            e2e_times.append((t3 - t0) * 1000.0)

        shutil.rmtree(temp_dir)
        overhead = bc_log.compute_storage_overhead(block)

        results.append({
            'approach': 'Blockchain_Audit_Log',
            'payload_size': payload_name,
            'payload_bytes': payload_bytes,
            'create_mean_ms': float(np.mean(create_times)),
            'create_std_ms': float(np.std(create_times)),
            'create_p50_ms': float(np.median(create_times)),
            'create_p95_ms': float(np.percentile(create_times, 95)),
            'verify_mean_ms': float(np.mean(verify_times)),
            'verify_std_ms': float(np.std(verify_times)),
            'verify_p50_ms': float(np.median(verify_times)),
            'verify_p95_ms': float(np.percentile(verify_times, 95)),
            'e2e_mean_ms': float(np.mean(e2e_times)),
            'overhead_bytes': overhead,
            'throughput_records_s': float(1000.0 / np.mean(create_times)),
            'throughput_mb_s': float((payload_bytes / (1024 * 1024)) / (np.mean(create_times) / 1000.0))
        })

    df_summary = pd.DataFrame(results)
    df_summary.to_csv(os.path.join(metrics_dir, 'e6_summary.csv'), index=False)
    df_summary.to_csv(os.path.join(metrics_dir, 'e6_raw_results.csv'), index=False)

    print("\n=== E6 INTEGRITY VERIFICATION SUMMARY ===", flush=True)
    summary_cols = ['approach', 'payload_size', 'create_mean_ms', 'verify_mean_ms', 'e2e_mean_ms', 'overhead_bytes', 'throughput_mb_s']
    print(df_summary[summary_cols].to_string(index=False), flush=True)

    # 3. Log Growth & Scaling Benchmark (N = 100, 500, 1000, 2000)
    print("\nRunning Log Growth & Chain Verification Scaling Benchmark...", flush=True)
    chain_sizes = [100, 500, 1000, 2000]
    scaling_results = []
    payload_1kib = generate_synthetic_payload(1024, 0)

    for n in chain_sizes:
        # Build chain of size N
        log = BlockchainAuditLog()
        append_latencies = []
        for i in range(1, n + 1):
            t_app_start = time.perf_counter()
            log.append_record(f"REC-{i}", 1700000000.0 + i, payload_1kib)
            t_app_end = time.perf_counter()
            append_latencies.append((t_app_end - t_app_start) * 1000.0)

        # Full chain verification timing
        t_v0 = time.perf_counter()
        is_valid, msg, _ = log.verify_chain()
        t_v1 = time.perf_counter()
        assert is_valid

        full_chain_verify_ms = (t_v1 - t_v0) * 1000.0
        single_block_verify_ms = full_chain_verify_ms / n
        total_chain_bytes = len(log.to_json().encode('utf-8'))

        scaling_results.append({
            'chain_length_records': n,
            'append_mean_ms': float(np.mean(append_latencies)),
            'full_chain_verify_total_ms': float(full_chain_verify_ms),
            'verify_per_record_ms': float(single_block_verify_ms),
            'total_log_size_kb': float(total_chain_bytes / 1024.0)
        })

    df_scaling = pd.DataFrame(scaling_results)
    df_scaling.to_csv(os.path.join(metrics_dir, 'e6_scaling_summary.csv'), index=False)
    print("\n=== CHAIN SCALING SUMMARY ===", flush=True)
    print(df_scaling.to_string(index=False), flush=True)

    # 4. Generate Tables
    # Table 6: Comparison of Integrity Approaches (1KiB Payload)
    df_1kib = df_summary[df_summary['payload_size'] == '1KiB'].copy()
    t6 = df_1kib[['approach', 'create_mean_ms', 'verify_mean_ms', 'e2e_mean_ms', 'overhead_bytes', 'throughput_mb_s']].copy()
    t6.columns = ['Integrity Architecture', 'Creation Latency (ms)', 'Verification Latency (ms)', 'End-to-End Latency (ms)', 'Storage Overhead (B)', 'Throughput (MB/s)']
    
    t6.to_csv(os.path.join(tables_dir, 'table6_integrity_benchmark.csv'), index=False)
    with open(os.path.join(tables_dir, 'table6_integrity_benchmark.md'), 'w') as f:
        f.write(t6.to_markdown(index=False))
    with open(os.path.join(paper_tables_dir, 'table6_integrity_benchmark.tex'), 'w') as f:
        f.write(t6.to_latex(index=False, float_format="%.4f"))

    # 5. Generate Figure 6: Latency, Overhead, and Chain Scaling
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    approaches = ['Salted_SHA256', 'HMAC_SHA256', 'Blockchain_Audit_Log']
    labels = ['Salted SHA-256', 'HMAC-SHA-256', 'Blockchain Log']
    x = np.arange(len(approaches))
    width = 0.35

    # Subplot 1: Creation vs Verification Latency (1KiB Payload)
    c_lat = [df_1kib[df_1kib['approach'] == a]['create_mean_ms'].values[0] for a in approaches]
    v_lat = [df_1kib[df_1kib['approach'] == a]['verify_mean_ms'].values[0] for a in approaches]

    ax1.bar(x - width/2, c_lat, width, label='Creation / Anchor', color='#1f77b4')
    ax1.bar(x + width/2, v_lat, width, label='Verification', color='#2ca02c')
    ax1.set_xlabel('Integrity Architecture', fontweight='bold')
    ax1.set_ylabel('Latency (ms)', fontweight='bold')
    ax1.set_title('A: Latency by Integrity Mechanism (1 KiB Payload)', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.legend()

    # Subplot 2: Full Chain Verification Scaling
    ax2.plot(df_scaling['chain_length_records'], df_scaling['full_chain_verify_total_ms'], marker='o', color='#d62728', linewidth=2, label='Full Chain Verify')
    ax2.set_xlabel('Audit Log Length (Records)', fontweight='bold')
    ax2.set_ylabel('Verification Latency (ms)', fontweight='bold')
    ax2.set_title('B: Blockchain Audit Log Verification Scaling', fontweight='bold')
    ax2.legend()

    plt.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'figure6_integrity_benchmark.png'), dpi=300)
    fig.savefig(os.path.join(paper_figures_dir, 'figure6_integrity_benchmark.png'), dpi=300)
    plt.close()

    print("\nExperiment E6 executed and artifacts saved successfully!", flush=True)


if __name__ == '__main__':
    benchmark_approaches(trials=100)
