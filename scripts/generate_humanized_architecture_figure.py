"""
Upgraded Publication-Tier System Architecture Diagram for DACC-ID
Modeled after Saeed (IEEE Access 2025, Figure 1) and elevated to comprehensive 6-stage architecture.
"""
import os
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_module_card(ax, x, y, w, h, badge, title, subtitle, items, header_color, bg_color='#ffffff'):
    # Subtle drop shadow
    shadow = patches.FancyBboxPatch((x + 0.08, y - 0.08), w, h,
                                   boxstyle="round,pad=0.1,rounding_size=0.16",
                                   linewidth=0, facecolor='#cbd5e1', alpha=0.55)
    ax.add_patch(shadow)

    # Main card container
    card = patches.FancyBboxPatch((x, y), w, h,
                                  boxstyle="round,pad=0.1,rounding_size=0.16",
                                  linewidth=1.6, edgecolor=header_color, facecolor=bg_color)
    ax.add_patch(card)

    # Header banner
    hdr_h = 1.05
    hdr = patches.FancyBboxPatch((x, y + h - hdr_h), w, hdr_h,
                                 boxstyle="round,pad=0.08,rounding_size=0.12",
                                 linewidth=1.2, edgecolor=header_color, facecolor=header_color)
    ax.add_patch(hdr)

    # Stage Badge & Title
    ax.text(x + 0.25, y + h - 0.35, badge, ha='left', va='center',
            color='#fef08a', fontweight='bold', fontsize=7.8)
    ax.text(x + 0.25, y + h - 0.65, title, ha='left', va='center',
            color='white', fontweight='bold', fontsize=9.8)
    ax.text(x + 0.25, y + h - 0.88, subtitle, ha='left', va='center',
            color='#e2e8f0', style='italic', fontsize=7.6)

    # Card body items
    text_y = y + h - hdr_h - 0.38
    for label, formula, note in items:
        # Step label
        ax.text(x + 0.22, text_y, label, ha='left', va='center',
                color='#0f172a', fontweight='bold', fontsize=8.2)
        text_y -= 0.32

        # Formula / equation box
        box_w = w - 0.44
        f_box = patches.FancyBboxPatch((x + 0.22, text_y - 0.22), box_w, 0.46,
                                       boxstyle="round,pad=0.04,rounding_size=0.06",
                                       linewidth=0.75, edgecolor='#cbd5e1', facecolor='#f8fafc')
        ax.add_patch(f_box)
        ax.text(x + 0.32, text_y, formula, ha='left', va='center',
                color='#1e293b', fontfamily='monospace', fontsize=7.4, fontweight='semibold')
        text_y -= 0.32

        # Metric / Note
        ax.text(x + 0.25, text_y, note, ha='left', va='center',
                color='#475569', fontsize=7.2, style='italic')
        text_y -= 0.42

def main():
    os.makedirs('paper/figures', exist_ok=True)
    output_path = 'paper/figures/figure0_system_architecture.png'

    fig, ax = plt.subplots(figsize=(16.8, 11.4), dpi=300)
    ax.set_xlim(0, 16.8)
    ax.set_ylim(0, 11.4)
    ax.axis('off')

    # Palette
    c_navy = '#1e3a8a'    # Stage 1: Ingestion
    c_blue = '#1d4ed8'    # Stage 2: Detection
    c_amber = '#b45309'   # Stage 3: Drift & Threshold
    c_teal = '#0f766e'    # Stage 4: Incident Correlation
    c_green = '#15803d'   # Stage 5: RL Mitigation
    c_purple = '#6b21a8'  # Stage 6: NIST PQC & Audit

    # Title Banner
    ax.text(8.4, 11.0, "DACC-ID: End-to-End System Architecture & Threat Lifecycle Pipeline",
            ha='center', va='center', fontsize=15.5, fontweight='bold', color='#0f172a')
    ax.text(8.4, 10.65, "An Integrated Edge Architecture for Drift-Aware Anomaly Detection, Streaming Graph Incident Correlation, Reinforcement Learning Mitigation, and Post-Quantum Security",
            ha='center', va='center', fontsize=8.8, style='italic', color='#334155')

    # Card geometry
    cw = 4.8
    ch = 4.25
    y_top = 5.95
    y_bot = 0.95
    x1 = 0.6
    x2 = 6.0
    x3 = 11.4

    # -------------------------------------------------------------
    # STAGE 1: IOT EDGE TELEMETRY & PREPROCESSING (Top Left)
    # -------------------------------------------------------------
    s1_items = [
        ("1. Multi-Protocol Edge Ingestion", "Protocols: MQTT, CoAP, DNS, HTTP, TCP, UDP", "Ingests streaming network telemetry across distributed IoT sensor nodes"),
        ("2. Feature Extraction & Normalization", "x_t in R^39,  x_t_norm = (x_t - mu_train) / sigma_train", "39 statistical flow features normalized strictly on pure benign D_train"),
        ("3. Strict Test-Label Firewall", "Y_test completely isolated; zero test contamination", "Guarantees unbiased online evaluation without label leakage")
    ]
    draw_module_card(ax, x1, y_top, cw, ch,
                     "STAGE 1: EDGE TELEMETRY",
                     "IoT Ingestion & Feature Engineering",
                     "Distributed Sensor Streams & Unbiased Sanitization",
                     s1_items, c_navy)

    # -------------------------------------------------------------
    # STAGE 2: AI-DRIVEN CALIBRATED DETECTION ENGINE (Top Center)
    # -------------------------------------------------------------
    s2_items = [
        ("1. Supervised Random Forest (Known Signatures)", "p_t = Pr(y=1 | x_t; theta_RF),  Trees=100, Depth=12", "Detects recognized attack patterns with high confidence"),
        ("2. Dense Autoencoder Reconstruction (Zero-Day)", "a_t = ||x_t - g(f(x_t))||_2^2,  L=1, 10,775 params", "Reconstruction error flags novel zero-day anomalies in 1.35 us"),
        ("3. Calibrated Probabilistic Score Fusion", "S_t = 0.65 * p_t + 0.35 * a_t,  S_t in [0, 1]", "F1 = 92.53% +/- 0.08%, FPR = 4.77% across 100,000 test flows")
    ]
    draw_module_card(ax, x2, y_top, cw, ch,
                     "STAGE 2: HYBRID DETECTION",
                     "AI-Driven Calibrated Detection Engine",
                     "Supervised & Unsupervised Dual-Stream Score Fusion",
                     s2_items, c_blue)

    # -------------------------------------------------------------
    # STAGE 3: DRIFT MONITORING & TCA-ADAPTIVE CONTROLLER (Top Right)
    # -------------------------------------------------------------
    s3_items = [
        ("1. Streaming ADWIN Drift Detection", "|mu_W0 - mu_W1| > eps_cut = sqrt(1/(2m) * ln(4n/delta))", "Dynamically detects rate shifts and concept drift without ground truth"),
        ("2. Truncation-Bias Calibration Factor", "kappa = tau_calib / (mu_trunc + k * sigma_trunc)", "Mathematically counteracts false alarm inflation under non-stationary traffic"),
        ("3. TCA-Adaptive Decision Rule & Streak Freeze", "tau_t = kappa * (mu_t + k*sigma_t),  y_t = 1[S_t >= tau_t]", "Streak-based freeze (s_burst >= 50) halts drift adaptation during attacks")
    ]
    draw_module_card(ax, x3, y_top, cw, ch,
                     "STAGE 3: DYNAMIC THRESHOLD",
                     "Drift Monitoring & TCA-Adaptive Controller",
                     "Non-Stationary Adaptation with Contamination Guard",
                     s3_items, c_amber)

    # -------------------------------------------------------------
    # STAGE 4: STREAMING TEMPORAL INCIDENT CORRELATION (Bottom Right)
    # -------------------------------------------------------------
    s4_items = [
        ("1. Sliding-Window Session Graph Clustering", "Edge(i, j) if |t_i - t_j| <= 45.0s and EntityAffinity", "Groups fragmented flow alerts into coherent multi-step attack campaigns"),
        ("2. MITRE ATT&CK Kill-Chain Progression", "Recon (TA0043) -> BruteForce (TA0006) -> DoS (TA0040)", "Identifies 90 multi-stage attack campaigns across 74,453 alerts"),
        ("3. 4-Factor Contextual Risk Prioritization", "R_k = 0.35*D_k + 0.25*I_k + 0.25*C_k + 0.15*E_k", "99.88% Alert Reduction Rate (74,453 alerts -> 91 incidents: 67 Crit, 24 High)")
    ]
    draw_module_card(ax, x3, y_bot, cw, ch,
                     "STAGE 4: GRAPH CORRELATION",
                     "Streaming Temporal Incident Correlation",
                     "Alert Fatigue Elimination & MITRE ATT&CK Synthesis",
                     s4_items, c_teal)

    # -------------------------------------------------------------
    # STAGE 5: REINFORCEMENT LEARNING MITIGATION (Bottom Center)
    # -------------------------------------------------------------
    s5_items = [
        ("1. Un-Contaminated Deep Q-Network (DQN)", "Q*(s, a) = r + gamma * max_a' Q(s', a'; theta^-)", "Trained strictly on clean state transitions to eliminate feedback poisoning"),
        ("2. Multi-Tier Autonomous Mitigation Actions", "Actions: {ALLOW (0), ALERT (1), RATE_LIMIT (2), BLOCK (3)}", "Dynamic action space balances security containment against service disruption"),
        ("3. Empirical Containment & Low Disruption", "Containment = 71.26% +/- 0.85%,  False Block Rate = 0.63%", "Outperforms tabular Q-learning while eliminating 99.37% false drops")
    ]
    draw_module_card(ax, x2, y_bot, cw, ch,
                     "STAGE 5: RL DEFENSE RESPONSE",
                     "Deep Q-Network Mitigation Engine",
                     "Autonomous Dynamic Containment & False-Block Minimization",
                     s5_items, c_green)

    # -------------------------------------------------------------
    # STAGE 6: POST-QUANTUM CRYPTOGRAPHY & FORENSICS (Bottom Left)
    # -------------------------------------------------------------
    s6_items = [
        ("1. NIST FIPS 203 ML-KEM-768 Transit Security", "(pk, sk) <- KeyGen(),  (c, K) <- Encaps(pk)", "Quantum-resistant key encapsulation: 0.429 ms total setup, 1,088B ciphertext"),
        ("2. Authenticated Symmetric Telemetry Channel", "Ciphertext = AES-256-GCM_Enc(K, Incident_Record)", "High-throughput transit encryption: 0.018 ms execution, 100% tamper reject"),
        ("3. Tamper-Evident SHA-256 Hash Chain", "h_i = SHA-256(h_{i-1} || rec_i || seq_i),  19,379 rec/s", "Append-only forensic audit trail (0.0516 ms/append) with zero blockchain lag")
    ]
    draw_module_card(ax, x1, y_bot, cw, ch,
                     "STAGE 6: POST-QUANTUM & FORENSICS",
                     "NIST PQC Transit & Hash-Chain Audit",
                     "Quantum-Resistant Key Exchange & Immutable Logging",
                     s6_items, c_purple)

    # -------------------------------------------------------------
    # PIPELINE CONNECTING ARROWS & DATA LABELS
    # -------------------------------------------------------------
    # Forward Arrow 1 -> 2 (Top Left to Top Mid)
    ax.annotate("", xy=(x2 - 0.05, y_top + ch/2), xytext=(x1 + cw + 0.05, y_top + ch/2),
                arrowprops=dict(arrowstyle="-|>", color="#1e3a8a", lw=2.4, mutation_scale=18))
    # Badge on Arrow 1->2
    b1 = patches.FancyBboxPatch(((x1 + cw + x2)/2 - 0.45, y_top + ch/2 + 0.12), 0.9, 0.45,
                                boxstyle="round,pad=0.04,rounding_size=0.08",
                                linewidth=0.8, edgecolor='#93c5fd', facecolor='#eff6ff')
    ax.add_patch(b1)
    ax.text((x1 + cw + x2)/2, y_top + ch/2 + 0.34, "x_t in R^39\nNormalized", ha='center', va='center',
            fontsize=7.2, fontweight='bold', color='#1e3a8a')

    # Forward Arrow 2 -> 3 (Top Mid to Top Right)
    ax.annotate("", xy=(x3 - 0.05, y_top + ch/2), xytext=(x2 + cw + 0.05, y_top + ch/2),
                arrowprops=dict(arrowstyle="-|>", color="#1d4ed8", lw=2.4, mutation_scale=18))
    # Badge on Arrow 2->3
    b2 = patches.FancyBboxPatch(((x2 + cw + x3)/2 - 0.45, y_top + ch/2 + 0.12), 0.9, 0.45,
                                boxstyle="round,pad=0.04,rounding_size=0.08",
                                linewidth=0.8, edgecolor='#bfdbfe', facecolor='#eff6ff')
    ax.add_patch(b2)
    ax.text((x2 + cw + x3)/2, y_top + ch/2 + 0.34, "S_t in [0, 1]\nFused Score", ha='center', va='center',
            fontsize=7.2, fontweight='bold', color='#1d4ed8')

    # Downward Arrow 3 -> 4 (Top Right down to Bottom Right)
    ax.annotate("", xy=(x3 + cw/2, y_bot + ch + 0.05), xytext=(x3 + cw/2, y_top - 0.05),
                arrowprops=dict(arrowstyle="-|>", color="#b45309", lw=2.4, mutation_scale=18))
    # Badge on Arrow 3->4
    b3 = patches.FancyBboxPatch((x3 + cw/2 - 0.85, (y_top + y_bot + ch)/2 - 0.28), 1.7, 0.56,
                                boxstyle="round,pad=0.04,rounding_size=0.08",
                                linewidth=0.8, edgecolor='#fde68a', facecolor='#fffbeb')
    ax.add_patch(b3)
    ax.text(x3 + cw/2, (y_top + y_bot + ch)/2, "Raw Flow Alerts: y_t = 1\n(74,453 Stream Alerts)",
            ha='center', va='center', fontsize=7.2, fontweight='bold', color='#b45309')

    # Forward Arrow 4 -> 5 (Bottom Right to Bottom Mid)
    ax.annotate("", xy=(x2 + cw + 0.05, y_bot + ch/2), xytext=(x3 - 0.05, y_bot + ch/2),
                arrowprops=dict(arrowstyle="-|>", color="#0f766e", lw=2.4, mutation_scale=18))
    # Badge on Arrow 4->5
    b4 = patches.FancyBboxPatch(((x2 + cw + x3)/2 - 0.65, y_bot + ch/2 + 0.12), 1.3, 0.45,
                                boxstyle="round,pad=0.04,rounding_size=0.08",
                                linewidth=0.8, edgecolor='#99f6e4', facecolor='#f0fdf4')
    ax.add_patch(b4)
    ax.text((x2 + cw + x3)/2, y_bot + ch/2 + 0.34, "91 Correlated Incidents\n(67 Crit, 24 High)",
            ha='center', va='center', fontsize=7.2, fontweight='bold', color='#0f766e')

    # Forward Arrow 5 -> 6 (Bottom Mid to Bottom Left)
    ax.annotate("", xy=(x1 + cw + 0.05, y_bot + ch/2), xytext=(x2 - 0.05, y_bot + ch/2),
                arrowprops=dict(arrowstyle="-|>", color="#15803d", lw=2.4, mutation_scale=18))
    # Badge on Arrow 5->6
    b5 = patches.FancyBboxPatch(((x1 + cw + x2)/2 - 0.60, y_bot + ch/2 + 0.12), 1.2, 0.45,
                                boxstyle="round,pad=0.04,rounding_size=0.08",
                                linewidth=0.8, edgecolor='#bbf7d0', facecolor='#f0fdf4')
    ax.add_patch(b5)
    ax.text((x1 + cw + x2)/2, y_bot + ch/2 + 0.34, "Mitigation Decisions\n& Verified State",
            ha='center', va='center', fontsize=7.2, fontweight='bold', color='#15803d')

    # -------------------------------------------------------------
    # CLOSED-LOOP FEEDBACK ARCS
    # -------------------------------------------------------------
    # Loop 1: RL Action (Stage 5) -> Edge Gateway Firewall (Stage 1)
    fb1 = patches.FancyArrowPatch((x2 + 0.8, y_bot + ch + 0.05), (x1 + cw - 0.8, y_top - 0.05),
                                  connectionstyle="arc3,rad=-0.22",
                                  color="#dc2626", lw=2.0, linestyle="--",
                                  arrowstyle="-|>", mutation_scale=16)
    ax.add_patch(fb1)
    # Badge for Feedback 1
    fb1_box = patches.FancyBboxPatch((3.8, 5.25), 1.6, 0.48, boxstyle="round,pad=0.04,rounding_size=0.08",
                                    linewidth=0.8, edgecolor='#fca5a5', facecolor='#fef2f2')
    ax.add_patch(fb1_box)
    ax.text(4.6, 5.49, "Mitigation Feedback Loop:\nDynamic IP/Port Rules", ha='center', va='center',
            fontsize=6.8, fontweight='bold', color='#b91c1c')

    # Loop 2: Temporal Correlation (Stage 4) -> Dynamic Threshold Controller (Stage 3)
    fb2 = patches.FancyArrowPatch((x3 + 0.8, y_bot + ch + 0.05), (x3 + 0.8, y_top - 0.05),
                                  connectionstyle="arc3,rad=0.30",
                                  color="#6366f1", lw=2.0, linestyle="--",
                                  arrowstyle="-|>", mutation_scale=16)
    ax.add_patch(fb2)
    # Badge for Feedback 2
    fb2_box = patches.FancyBboxPatch((10.3, 5.25), 1.6, 0.48, boxstyle="round,pad=0.04,rounding_size=0.08",
                                    linewidth=0.8, edgecolor='#c7d2fe', facecolor='#eef2ff')
    ax.add_patch(fb2_box)
    ax.text(11.1, 5.49, "Recalibration Signal:\nBurst Cooldown Control", ha='center', va='center',
            fontsize=6.8, fontweight='bold', color='#4338ca')

    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated upgraded architecture diagram: {output_path}")

if __name__ == '__main__':
    main()
