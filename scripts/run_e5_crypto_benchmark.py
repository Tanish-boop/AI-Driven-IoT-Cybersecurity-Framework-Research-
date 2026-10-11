"""
Experiment E5 Execution Script: Standardized NIST ML-KEM Post-Quantum Cryptography Benchmark
Runs 100 repeated trials across:
  - ML-KEM-512, ML-KEM-768, ML-KEM-1024
  - Payload Sizes: 64B, 256B, 1KiB, 4KiB
  - HKDF-SHA256 Key Derivation + AES-256-GCM AEAD
Measures KEM latency (KeyGen, Encaps, Decaps), AEAD latency, artifact sizes, and communication overhead.
"""

import os
import sys
import json
import time
import platform
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath('.'))

from src.crypto.ml_kem_benchmark import benchmark_kem_variant, verify_tamper_rejection, KEM_MAP, PAYLOAD_SIZES

def main():
    print("=" * 60, flush=True)
    print("STARTING EXPERIMENT E5: POST-QUANTUM CRYPTOGRAPHY BENCHMARK (ML-KEM)", flush=True)
    print("=" * 60, flush=True)

    metrics_dir = 'results/metrics'
    tables_dir = 'results/tables'
    figures_dir = 'results/figures'
    paper_tables_dir = 'paper/tables'
    paper_figures_dir = 'paper/figures'

    for d in [metrics_dir, tables_dir, figures_dir, paper_tables_dir, paper_figures_dir]:
        os.makedirs(d, exist_ok=True)

    # 1. Environment & Cryptographic Provider Metadata
    crypto_env_info = {
        'timestamp_local': '2026-10-09T15:55:00',
        'os_platform': platform.platform(),
        'python_version': sys.version,
        'provider_library': 'pqcrypto (1.0.0, C-optimized NIST FIPS 203 implementation)',
        'aead_algorithm': 'AES-256-GCM (cryptography 46.0.1 OpenSSL provider)',
        'kdf_algorithm': 'HKDF-SHA256'
    }
    with open(os.path.join(metrics_dir, 'e5_crypto_environment.json'), 'w') as f:
        json.dump(crypto_env_info, f, indent=2)

    # 2. Tamper Detection Integrity Checks
    print("\nExecuting Cryptographic Correctness & Tamper Rejection Checks...", flush=True)
    for variant in ['ML-KEM-512', 'ML-KEM-768', 'ML-KEM-1024']:
        tamper_pass = verify_tamper_rejection(variant)
        assert tamper_pass, f"Tamper rejection check FAILED for {variant}!"
        print(f"  [{variant}] Tamper Rejection Check: PASSED (InvalidTag raised on corrupted ciphertext)", flush=True)

    # 3. Comprehensive Benchmarking across Variants and Payload Sizes
    e5_results = []
    trials = 100

    print(f"\nRunning {trials} repeated trials for each parameter set...", flush=True)
    for variant in ['ML-KEM-512', 'ML-KEM-768', 'ML-KEM-1024']:
        for payload_name, payload_bytes in PAYLOAD_SIZES.items():
            print(f"  Benchmarking {variant} | Payload: {payload_name} ({payload_bytes} bytes)...", flush=True)
            res = benchmark_kem_variant(variant_name=variant, trials=trials, payload_bytes=payload_bytes)
            e5_results.append(res)

    df_e5 = pd.DataFrame(e5_results)
    df_e5.to_csv(os.path.join(metrics_dir, 'e5_raw_results.csv'), index=False)
    df_e5.to_csv(os.path.join(metrics_dir, 'e5_summary.csv'), index=False)

    print("\n=== E5 POST-QUANTUM CRYPTOGRAPHY BENCHMARK SUMMARY ===", flush=True)
    summary_cols = ['variant', 'payload_size_name', 'pk_size_bytes', 'ct_size_bytes', 
                    'keygen_mean_ms', 'encaps_mean_ms', 'decaps_mean_ms', 'total_kem_mean_ms', 
                    'first_msg_mean_ms', 'repeated_msg_mean_ms']
    print(df_e5[summary_cols].to_string(index=False), flush=True)

    # 4. Generate Tables
    # Table 5A: Key Establishment Artifact Sizes & KEM Timing (1KiB Payload)
    df_1kib = df_e5[df_e5['payload_size_name'] == '1024B'].copy()
    t5a = df_1kib[['variant', 'pk_size_bytes', 'sk_size_bytes', 'ct_size_bytes', 'ss_size_bytes',
                    'keygen_mean_ms', 'encaps_mean_ms', 'decaps_mean_ms', 'total_kem_mean_ms']].copy()
    t5a.columns = ['ML-KEM Variant', 'Public Key (B)', 'Secret Key (B)', 'Ciphertext (B)', 'Shared Secret (B)',
                   'KeyGen (ms)', 'Encaps (ms)', 'Decaps (ms)', 'Total KEM Latency (ms)']
    
    t5a.to_csv(os.path.join(tables_dir, 'table5_pqc_benchmark.csv'), index=False)
    with open(os.path.join(tables_dir, 'table5_pqc_benchmark.md'), 'w') as f:
        f.write(t5a.to_markdown(index=False))
    with open(os.path.join(paper_tables_dir, 'table5_pqc_benchmark.tex'), 'w') as f:
        f.write(t5a.to_latex(index=False, float_format="%.4f"))

    # Table 5B: Communication Overhead & End-to-End AEAD Latency Across Payload Sizes
    t5b = df_e5[['variant', 'payload_size_name', 'comm_overhead_first_msg_bytes', 'first_msg_mean_ms', 'repeated_msg_mean_ms', 'throughput_mb_s']].copy()
    t5b.columns = ['Variant', 'Payload', 'Total Overhead (B)', 'First-Msg Setup Latency (ms)', 'Repeated-Msg Latency (ms)', 'Throughput (MB/s)']
    t5b.to_csv(os.path.join(tables_dir, 'table5b_pqc_payload_latency.csv'), index=False)
    with open(os.path.join(tables_dir, 'table5b_pqc_payload_latency.md'), 'w') as f:
        f.write(t5b.to_markdown(index=False))

    # 5. Generate Figure 5: Key Establishment Latency & Artifact Size Comparison
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    variants = ['ML-KEM-512', 'ML-KEM-768', 'ML-KEM-1024']
    x = np.arange(len(variants))
    width = 0.25

    # Subplot 1: Latency Breakdown (KeyGen, Encaps, Decaps)
    kg_means = [df_1kib[df_1kib['variant']==v]['keygen_mean_ms'].values[0] for v in variants]
    enc_means = [df_1kib[df_1kib['variant']==v]['encaps_mean_ms'].values[0] for v in variants]
    dec_means = [df_1kib[df_1kib['variant']==v]['decaps_mean_ms'].values[0] for v in variants]

    ax1.bar(x - width, kg_means, width, label='KeyGen', color='#1f77b4')
    ax1.bar(x, enc_means, width, label='Encaps', color='#ff7f0e')
    ax1.bar(x + width, dec_means, width, label='Decaps', color='#2ca02c')
    ax1.set_xlabel('ML-KEM Parameter Set', fontweight='bold')
    ax1.set_ylabel('Latency (ms)', fontweight='bold')
    ax1.set_title('A: ML-KEM Key Establishment Latency', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(variants)
    ax1.legend()

    # Subplot 2: Artifact Sizes (Public Key & Ciphertext)
    pk_sizes = [df_1kib[df_1kib['variant']==v]['pk_size_bytes'].values[0] for v in variants]
    ct_sizes = [df_1kib[df_1kib['variant']==v]['ct_size_bytes'].values[0] for v in variants]

    ax2.bar(x - width/2, pk_sizes, width, label='Public Key', color='#9467bd')
    ax2.bar(x + width/2, ct_sizes, width, label='Ciphertext', color='#8c564b')
    ax2.set_xlabel('ML-KEM Parameter Set', fontweight='bold')
    ax2.set_ylabel('Size (Bytes)', fontweight='bold')
    ax2.set_title('B: ML-KEM Cryptographic Artifact Sizes', fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(variants)
    ax2.legend()

    plt.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'figure5_pqc_latency.png'), dpi=300)
    fig.savefig(os.path.join(paper_figures_dir, 'figure5_pqc_latency.png'), dpi=300)
    plt.close()

    print("\nExperiment E5 completed successfully!", flush=True)

if __name__ == '__main__':
    main()
