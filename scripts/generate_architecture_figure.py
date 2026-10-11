"""
Generate Publication-Quality System Architecture Diagram
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def main():
    os.makedirs('paper/figures', exist_ok=True)
    os.makedirs('results/figures', exist_ok=True)

    fig, ax = plt.subplots(figsize=(14, 5.5), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Color palette (IEEE style)
    c_blue = '#1f77b4'
    c_orange = '#ff7f0e'
    c_green = '#2ca02c'
    c_purple = '#9467bd'
    c_red = '#d62728'
    c_bg = '#f8f9fa'

    stages = [
        ("Stage 1: Telemetry Ingestion\n& Normalization", 
         "• 39 Numerical Flow Features\n• Metadata Dropped (IP/Port)\n• StandardScaler (X_train strictly)\n• Sample-level L=1 (No leakage)", 
         c_blue, 0.4),
        ("Stage 2: Anomaly Detection\n& Boundary Adaptation", 
         "• Dense-AE (39-32-16-32-39)\n• Reconstruction Loss ||x - x̂||²\n• Excluded EWMA Thresholding\n• Prevents Inflation Collapse", 
         c_orange, 3.1),
        ("Stage 3: Automated Mitigation\nPolicy (RL Engine)", 
         "• Un-Contaminated Split (X_sup)\n• Deep Q-Network / Tabular Q\n• Actions: Allow, Limit, Inspect, Block\n• Consecutive Alert Streak Tracking", 
         c_green, 5.8),
        ("Stage 4: Post-Quantum Transit\n(NIST FIPS 203)", 
         "• NIST ML-KEM-768 Key Encaps\n• Sub-millisecond (0.4293 ms)\n• HKDF-SHA256 Key Derivation\n• AES-256-GCM Authenticated AEAD", 
         c_purple, 8.5),
        ("Stage 5: Forensic Audit Log\n(Hash-Chain Sequencing)", 
         "• Append-only Hash Chain Log\n• O(1) Append Latency (0.0409 ms)\n• Provable Tamper Localization\n• Local Rewrite Boundary Disclosed", 
         c_red, 11.2)
    ]

    for title, desc, color, x in stages:
        # Main box
        rect = patches.FancyBboxPatch((x, 0.6), 2.4, 4.8, boxstyle="round,pad=0.1,rounding_size=0.15",
                                      linewidth=1.5, edgecolor=color, facecolor=c_bg)
        ax.add_patch(rect)
        # Header box
        hdr = patches.FancyBboxPatch((x, 4.3), 2.4, 1.1, boxstyle="round,pad=0.08,rounding_size=0.1",
                                     linewidth=1.2, edgecolor=color, facecolor=color)
        ax.add_patch(hdr)
        ax.text(x + 1.2, 4.85, title, ha='center', va='center', color='white', fontweight='bold', fontsize=9.5)
        ax.text(x + 0.15, 2.4, desc, ha='left', va='center', color='#212529', fontsize=8.2, linespacing=1.6)

    # Arrows between stages
    for i in range(len(stages) - 1):
        x_start = stages[i][3] + 2.4
        x_end = stages[i+1][3]
        ax.annotate("", xy=(x_end, 3.0), xytext=(x_start, 3.0),
                    arrowprops=dict(arrowstyle="->", color="#495057", lw=2, mutation_scale=15))

    # Overall pipeline box
    outer = patches.Rectangle((0.1, 0.2), 13.8, 5.6, linewidth=1, edgecolor='#ced4da', facecolor='none', linestyle='--')
    ax.add_patch(outer)
    ax.text(0.3, 5.65, "Five-Stage Integrated AI-Driven IoT Cybersecurity Framework (AMD64 Edge Gateway Pipeline)", 
            fontweight='bold', fontsize=11, color='#343a40')

    plt.tight_layout()
    fig.savefig('paper/figures/figure0_system_architecture.png', dpi=300, bbox_inches='tight')
    fig.savefig('results/figures/figure0_system_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Architecture diagram generated successfully!")

if __name__ == '__main__':
    main()
