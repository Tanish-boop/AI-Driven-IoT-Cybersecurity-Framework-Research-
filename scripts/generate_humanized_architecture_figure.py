"""
Generate Enhanced, Humanized System Architecture Diagram
Modeled after Saeed (IEEE Access 2025, Figure 1) and elevated with DACC-ID components.
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_card(ax, x, y, w, h, title, subtitle, items, color, bg_color='#fbfcfd'):
    # Outer container with rounded corners and drop shadow
    shadow = patches.FancyBboxPatch((x + 0.08, y - 0.08), w, h,
                                   boxstyle="round,pad=0.1,rounding_size=0.18",
                                   linewidth=0, facecolor='#d0d7de', alpha=0.5)
    ax.add_patch(shadow)

    card = patches.FancyBboxPatch((x, y), w, h,
                                  boxstyle="round,pad=0.1,rounding_size=0.18",
                                  linewidth=1.8, edgecolor=color, facecolor=bg_color)
    ax.add_patch(card)

    # Header banner
    hdr_h = 1.05
    hdr = patches.FancyBboxPatch((x, y + h - hdr_h), w, hdr_h,
                                 boxstyle="round,pad=0.08,rounding_size=0.12",
                                 linewidth=1.2, edgecolor=color, facecolor=color)
    ax.add_patch(hdr)

    # Title & subtitle
    ax.text(x + w / 2, y + h - 0.40, title, ha='center', va='center',
            color='white', fontweight='bold', fontsize=10.5)
    ax.text(x + w / 2, y + h - 0.78, subtitle, ha='center', va='center',
            color='#f1f5f9', style='italic', fontsize=8.2)

    # Card body items
    text_y = y + h - hdr_h - 0.40
    for label, formula in items:
        # Step label
        ax.text(x + 0.25, text_y, label, ha='left', va='center',
                color='#1e293b', fontweight='bold', fontsize=8.5)
        text_y -= 0.35
        # Formula / description box
        box_w = w - 0.50
        f_box = patches.FancyBboxPatch((x + 0.25, text_y - 0.25), box_w, 0.50,
                                       boxstyle="round,pad=0.04,rounding_size=0.06",
                                       linewidth=0.8, edgecolor='#cbd5e1', facecolor='#f1f5f9')
        ax.add_patch(f_box)
        ax.text(x + 0.35, text_y, formula, ha='left', va='center',
                color='#0f172a', fontfamily='monospace', fontsize=7.6)
        text_y -= 0.55

def main():
    os.makedirs('paper/figures', exist_ok=True)
    output_path = 'paper/figures/figure0_system_architecture.png'

    fig, ax = plt.subplots(figsize=(15, 10.5), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 10.5)
    ax.axis('off')

    # Color Scheme
    c_blue = '#1d4ed8'    # Anomaly Detection
    c_amber = '#d97706'   # Threshold & Drift
    c_teal = '#0f766e'    # Incident Correlation
    c_green = '#15803d'   # RL Response
    c_purple = '#6b21a8'  # NIST ML-KEM PQC
    c_red = '#b91c1c'     # Tamper-Evident Forensics

    # Canvas Title & Subtitle
    ax.text(7.5, 10.15, "DACC-ID: System Architecture & Operational Pipeline",
            ha='center', va='center', fontsize=15, fontweight='bold', color='#0f172a')
    ax.text(7.5, 9.80, "Integrated Edge Architecture for Drift-Aware Anomaly Detection, Incident Correlation, Mitigation, and Post-Quantum Security",
            ha='center', va='center', fontsize=9.5, style='italic', color='#475569')

    # START Pill
    start_box = patches.FancyBboxPatch((0.5, 8.65), 1.6, 0.65, boxstyle="round,pad=0.08,rounding_size=0.3",
                                       linewidth=1.5, edgecolor='#0284c7', facecolor='#0284c7')
    ax.add_patch(start_box)
    ax.text(1.3, 8.97, "START\nIoT Telemetry", ha='center', va='center', color='white', fontweight='bold', fontsize=8.2)

    # -------------------------------------------------------------
    # CARD 1: TOP LEFT - AI Anomaly Detection & Hybrid Fusion
    # -------------------------------------------------------------
    card1_items = [
        ("1. Feature Preprocessing (39 NetFlow Features)", "xt in R^39, scaled strictly via benign X_train"),
        ("2. Dense Autoencoder Reconstruction (L=1)", "x_hat = g(f(xt)),  Et = (1/D) * sum(xt - x_hat)^2"),
        ("3. Calibrated Supervised / Anomaly Fusion", "St = 0.65 * p_sup(xt) + 0.35 * a_unsup(xt)")
    ]
    draw_card(ax, 2.5, 5.8, 5.6, 3.7,
              "AI-Driven Anomaly Detection Engine",
              "Supervised & Unsupervised Calibrated Score Fusion",
              card1_items, c_blue)

    # -------------------------------------------------------------
    # CARD 2: TOP RIGHT - Drift Monitoring & Dynamic Thresholding
    # -------------------------------------------------------------
    card2_items = [
        ("1. Streaming ADWIN Concept Drift Monitor", "|mu_W0 - mu_W1| > eps_cut = sqrt(1/(2m)*ln(4n/delta))"),
        ("2. Truncation-Bias Calibration Factor", "kappa = tau_calib / (mu_trunc + k * sigma_trunc)"),
        ("3. TCA-Adaptive Operational Decision Rule", "tau_t = kappa * (mu_t + k*sigma_t),  yt = 1[St >= tau_t]")
    ]
    draw_card(ax, 8.8, 5.8, 5.6, 3.7,
              "Drift Monitoring & TCA-Adaptive Controller",
              "Guarded Dynamic Boundary with Streak-Based Incident Freeze",
              card2_items, c_amber)

    # -------------------------------------------------------------
    # CARD 3: MIDDLE CONNECTOR - Temporal Graph Alert Correlation
    # -------------------------------------------------------------
    card3_items = [
        ("1. Streaming Session Clustering & Affinity", "Link alerts: |ti - tj| <= 45s, same Device/IP/Port"),
        ("2. MITRE ATT&CK Causal Campaign Chains", "Recon (TA0043) -> BruteForce (TA0006) -> DoS (TA0040)"),
        ("3. 4-Factor Contextual Incident Risk Scoring", "R_k = 0.35*D + 0.25*I + 0.25*C + 0.15*E  [ARR = 99.88%]")
    ]
    draw_card(ax, 8.8, 1.2, 5.6, 3.7,
              "Temporal Graph Incident Correlation Engine",
              "Alert Fatigue Reduction & Contextual Risk Prioritization",
              card3_items, c_teal)

    # -------------------------------------------------------------
    # CARD 4: BOTTOM LEFT - Automated Mitigation & PQC Cryptography
    # -------------------------------------------------------------
    card4_items = [
        ("1. Un-Contaminated RL Defense Policy (DQN)", "Actions: {ALLOW, ALERT, RATE_LIMIT, BLOCK} (71.3% cont.)"),
        ("2. NIST FIPS 203 ML-KEM-768 Transit Security", "(pk, sk) <- KeyGen, (c, K) <- Encaps(pk)  [0.429 ms setup]"),
        ("3. Tamper-Evident Hash-Chain Audit Logging", "h_i = SHA-256(h_{i-1} || rec_i || seq_i)  [19,379 rec/s]")
    ]
    draw_card(ax, 2.5, 1.2, 5.6, 3.7,
              "Automated Response & Cryptographic Layer",
              "Deep Reinforcement Learning & Post-Quantum Security",
              card4_items, c_purple)

    # STOP Pill
    stop_box = patches.FancyBboxPatch((0.5, 2.5), 1.6, 0.65, boxstyle="round,pad=0.08,rounding_size=0.3",
                                      linewidth=1.5, edgecolor='#15803d', facecolor='#15803d')
    ax.add_patch(stop_box)
    ax.text(1.3, 2.82, "STOP\nSecured Node", ha='center', va='center', color='white', fontweight='bold', fontsize=8.2)

    # -------------------------------------------------------------
    # CONNECTING ARROWS & DATAFLOW PIPELINE
    # -------------------------------------------------------------
    arrow_style = dict(arrowstyle="-|>", color="#334155", lw=2.2, mutation_scale=18)
    
    # Start -> Card 1
    ax.annotate("", xy=(2.45, 7.8), xytext=(2.15, 8.9),
                arrowprops=dict(arrowstyle="-|>", color="#0284c7", lw=2.4, mutation_scale=18,
                                connectionstyle="arc3,rad=-0.15"))
    ax.text(1.9, 8.4, "Raw Flow\nTelemetry", fontsize=7.5, fontweight='bold', color='#0369a1')

    # Card 1 -> Card 2 (Top Left to Top Right)
    ax.annotate("", xy=(8.75, 7.65), xytext=(8.15, 7.65), arrowprops=arrow_style)
    ax.text(8.45, 7.95, "Fused Score\nSt in [0, 1]", ha='center', fontsize=7.8, fontweight='bold', color='#1e293b')

    # Card 2 -> Card 3 (Top Right down to Middle Right)
    ax.annotate("", xy=(11.6, 4.95), xytext=(11.6, 5.75), arrowprops=arrow_style)
    ax.text(12.35, 5.35, "Raw Alerts\nyt = 1\n(74,453 flows)", ha='center', fontsize=7.8, fontweight='bold', color='#b45309')

    # Card 3 -> Card 4 (Middle Right over to Bottom Left)
    ax.annotate("", xy=(8.15, 3.0), xytext=(8.75, 3.0), arrowprops=arrow_style)
    ax.text(8.45, 3.35, "Prioritized\nIncidents\n(91 incidents)", ha='center', fontsize=7.8, fontweight='bold', color='#0f766e')

    # Card 4 -> Stop Pill
    ax.annotate("", xy=(2.15, 2.82), xytext=(2.45, 2.82),
                arrowprops=dict(arrowstyle="-|>", color="#15803d", lw=2.4, mutation_scale=18))
    ax.text(2.3, 2.45, "Verified &\nContained", ha='center', fontsize=7.5, fontweight='bold', color='#15803d')

    # Central Feedback / Continuous Loop Arc (like Saeed Figure 1)
    arc_arrow = patches.FancyArrowPatch((5.3, 4.95), (5.3, 5.75),
                                         connectionstyle="arc3,rad=-0.35",
                                         color="#64748b", lw=1.8, linestyle="--",
                                         arrowstyle="-|>", mutation_scale=15)
    ax.add_patch(arc_arrow)
    ax.text(4.4, 5.35, "Feedback &\nThreshold Cooldown", ha='center', fontsize=7.2, style='italic', color='#64748b')

    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated humanized architecture diagram: {output_path}")

if __name__ == '__main__':
    main()
