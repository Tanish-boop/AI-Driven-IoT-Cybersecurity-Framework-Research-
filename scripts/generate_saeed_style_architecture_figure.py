"""
scripts/generate_saeed_style_architecture_figure.py

Generates the exact methodology flowchart matching Saeed (IEEE Access 2025, Figure 1)
elevated with DACC-ID's validated empirical components.
"""
import os
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_flow_box(ax, x, y, w, h, text, is_header=False, bg_color='#ffffff', edge_color='#1e293b', font_size=8.5, is_bold=False):
    # Standard crisp box with clean borders exactly like Saeed Figure 1
    face = '#f1f5f9' if is_header else bg_color
    lw = 1.6 if is_header else 1.1
    box = patches.Rectangle((x, y), w, h, linewidth=lw, edgecolor=edge_color, facecolor=face, zorder=3)
    ax.add_patch(box)
    
    font_weight = 'bold' if (is_header or is_bold) else 'normal'
    ax.text(x + w / 2.0, y + h / 2.0, text, ha='center', va='center',
            fontsize=font_size, fontweight=font_weight, color='#0f172a', zorder=4)

def draw_oval(ax, x, y, w, h, text, edge_color='#1e293b'):
    oval = patches.Ellipse((x, y), w, h, linewidth=1.4, edgecolor=edge_color, facecolor='#ffffff', zorder=3)
    ax.add_patch(oval)
    ax.text(x, y, text, ha='center', va='center', fontsize=9.0, fontweight='bold', color='#0f172a', zorder=4)

def draw_thin_down_arrow(ax, x, y_start, y_end):
    ax.annotate("", xy=(x, y_end), xytext=(x, y_start),
                arrowprops=dict(arrowstyle="-|>", color="#1e293b", lw=1.3, mutation_scale=12),
                zorder=5)

def draw_thick_block_arrow(ax, x1, y1, x2, y2, color="#2563eb", width=0.28, head_len=0.45, head_width=0.55):
    # Draw solid block arrow matching Saeed Figure 1
    dx = x2 - x1
    dy = y2 - y1
    if dx > 0: # pointing right
        tail_x = x1
        tail_y = y1 - width/2
        tail_w = dx - head_len
        tail_h = width
        ax.add_patch(patches.Rectangle((tail_x, tail_y), tail_w, tail_h, facecolor=color, edgecolor=color, zorder=5))
        # Arrowhead triangle
        tri = patches.Polygon([[x2 - head_len, y1 - head_width/2],
                               [x2, y1],
                               [x2 - head_len, y1 + head_width/2]],
                              closed=True, facecolor=color, edgecolor=color, zorder=5)
        ax.add_patch(tri)
    elif dx < 0: # pointing left
        tail_x = x1
        tail_y = y1 - width/2
        tail_w = dx + head_len
        tail_h = width
        ax.add_patch(patches.Rectangle((tail_x, tail_y), tail_w, tail_h, facecolor=color, edgecolor=color, zorder=5))
        # Arrowhead triangle
        tri = patches.Polygon([[x2 + head_len, y1 - head_width/2],
                               [x2, y1],
                               [x2 + head_len, y1 + head_width/2]],
                              closed=True, facecolor=color, edgecolor=color, zorder=5)
        ax.add_patch(tri)

def draw_thick_curved_arrow(ax, x_start, y_start, x_end, y_end, color="#2563eb"):
    # Curved arrow looping from Top Right down to Bottom Right
    arc = patches.FancyArrowPatch((x_start, y_start), (x_end, y_end),
                                  connectionstyle="arc3,rad=-0.8",
                                  color=color, lw=0,
                                  arrowstyle="Simple,tail_width=9,head_width=22,head_length=18",
                                  zorder=5)
    ax.add_patch(arc)

def main():
    os.makedirs('paper/figures', exist_ok=True)
    output_path = 'paper/figures/figure0_system_architecture.png'

    fig, ax = plt.subplots(figsize=(15.0, 11.2), dpi=300)
    ax.set_xlim(0, 15.0)
    ax.set_ylim(0, 11.2)
    ax.axis('off')

    # Coordinates layout: Left Column and Right Column
    col_w = 5.2
    x_left = 2.4
    x_right = 8.8
    bw = 4.8
    bx_left = x_left + (col_w - bw) / 2.0
    bx_right = x_right + (col_w - bw) / 2.0

    # -------------------------------------------------------------
    # 1. TOP LEFT BLOCK: AI DRIVEN ANOMALY DETECTION (DACC-ID Hybrid)
    # -------------------------------------------------------------
    y_hdr1 = 10.1
    draw_flow_box(ax, bx_left, y_hdr1, bw, 0.65,
                  "AI driven anomaly detection\n(using Calibrated Dense-AE & Random Forest)",
                  is_header=True, font_size=9.2)

    # Sub-box 1
    y_b1_1 = 8.95
    h_b1_1 = 0.85
    draw_flow_box(ax, bx_left + 0.2, y_b1_1, bw - 0.4, h_b1_1,
                  "Problem Formulation & Feature Normalization:\nModel NetFlow traffic as feature vector x_t in R^39\nEnforce strict Test-Label Firewall (Y_test isolated)",
                  font_size=8.0)
    draw_thin_down_arrow(ax, bx_left + bw/2.0, y_hdr1, y_b1_1 + h_b1_1)

    # Sub-box 2
    y_b1_2 = 7.75
    h_b1_2 = 0.85
    draw_flow_box(ax, bx_left + 0.2, y_b1_2, bw - 0.4, h_b1_2,
                  "Model Training & Architecture Selection:\nTrain sample-level Dense Autoencoder (L=1, 10,775 params)\nTrain Supervised Random Forest (Trees=100, Depth=12) on D_sup",
                  font_size=8.0)
    draw_thin_down_arrow(ax, bx_left + bw/2.0, y_b1_1, y_b1_2 + h_b1_2)

    # Sub-box 3
    y_b1_3 = 6.45
    h_b1_3 = 0.95
    draw_flow_box(ax, bx_left + 0.2, y_b1_3, bw - 0.4, h_b1_3,
                  "Calibrated Anomaly Detection & Fusion:\nCompute error E_t = ||x_t - g(f(x_t))||^2, a_t = min(1, E_t / tau_calib)\nProbabilistic Fusion: S_t = 0.65 * p_t + 0.35 * a_t in [0, 1]\nDetect anomaly alert if S_t >= tau_t  [F1 = 92.53%]",
                  font_size=8.0)
    draw_thin_down_arrow(ax, bx_left + bw/2.0, y_b1_2, y_b1_3 + h_b1_3)

    # START Oval
    draw_oval(ax, 1.1, y_hdr1 + 0.32, 1.5, 0.70, "START")
    # Arrow START -> Top Left Header
    ax.annotate("", xy=(bx_left, y_hdr1 + 0.32), xytext=(1.85, y_hdr1 + 0.32),
                arrowprops=dict(arrowstyle="-|>", color="#1e293b", lw=1.5, mutation_scale=14),
                zorder=5)

    # -------------------------------------------------------------
    # THICK BLOCK ARROW (Top Left -> Top Right)
    # -------------------------------------------------------------
    draw_thick_block_arrow(ax, bx_left + bw + 0.15, 8.4, bx_right - 0.15, 8.4, color="#2563eb", width=0.35, head_len=0.55, head_width=0.70)
    ax.text((bx_left + bw + bx_right)/2.0, 8.85, "Fused Score\nS_t in [0, 1]", ha='center', va='center',
            fontsize=7.8, fontweight='bold', color='#1d4ed8', zorder=6)

    # -------------------------------------------------------------
    # 2. TOP RIGHT BLOCK: DRIFT MONITORING & ADAPTIVE THRESHOLDING
    # -------------------------------------------------------------
    y_hdr2 = 10.1
    draw_flow_box(ax, bx_right, y_hdr2, bw, 0.65,
                  "Drift Monitoring & Adaptive Thresholding\n(using ADWIN & TCA-Adaptive Controller)",
                  is_header=True, font_size=9.2)

    # Sub-box 1
    y_b2_1 = 8.95
    h_b2_1 = 0.85
    draw_flow_box(ax, bx_right + 0.2, y_b2_1, bw - 0.4, h_b2_1,
                  "Streaming Concept Drift Detection:\nMonitor score statistics via ADWIN cut-rule:\n|mu_W0 - mu_W1| > eps_cut = sqrt( (1/(2m)) * ln(4n / delta) )",
                  font_size=8.0)
    draw_thin_down_arrow(ax, bx_right + bw/2.0, y_hdr2, y_b2_1 + h_b2_1)

    # Sub-box 2
    y_b2_2 = 7.75
    h_b2_2 = 0.85
    draw_flow_box(ax, bx_right + 0.2, y_b2_2, bw - 0.4, h_b2_2,
                  "Truncation-Bias Calibration & Guard:\nCompute factor kappa = tau_calib / (mu_trunc + k * sigma_trunc)\nPrevents downward censoring collapse on nominal streams",
                  font_size=8.0)
    draw_thin_down_arrow(ax, bx_right + bw/2.0, y_b2_1, y_b2_2 + h_b2_2)

    # Sub-box 3
    y_b2_3 = 6.45
    h_b2_3 = 0.95
    draw_flow_box(ax, bx_right + 0.2, y_b2_3, bw - 0.4, h_b2_3,
                  "Operational Decision Rule & Streak Freeze:\ntau_t = kappa * (mu_t + k * sigma_t),  y_t = 1[S_t >= tau_t]\nFreeze threshold updates if burst streak s_burst >= 50\nSlashes false alarms by 77% under non-stationary drift",
                  font_size=8.0)
    draw_thin_down_arrow(ax, bx_right + bw/2.0, y_b2_2, y_b2_3 + h_b2_3)

    # -------------------------------------------------------------
    # THICK CURVED ARROW (Top Right -> Bottom Right)
    # -------------------------------------------------------------
    draw_thick_curved_arrow(ax, bx_right + bw + 0.15, 6.8, bx_right + bw + 0.15, 4.4, color="#2563eb")
    ax.text(bx_right + bw + 0.95, 5.6, "Raw Alerts\ny_t = 1\n(74,453 Flows)", ha='center', va='center',
            fontsize=7.8, fontweight='bold', color='#1d4ed8', zorder=6)

    # -------------------------------------------------------------
    # 3. MIDDLE/BOTTOM RIGHT BLOCK: TEMPORAL INCIDENT CORRELATION & RL RESPONSE
    # -------------------------------------------------------------
    y_hdr3 = 5.25
    draw_flow_box(ax, bx_right, y_hdr3, bw, 0.65,
                  "Automated Incident Response & Correlation\n(Temporal Graph Engine & Deep Reinforcement Learning)",
                  is_header=True, font_size=9.2)

    # Sub-box 1
    y_b3_1 = 4.10
    h_b3_1 = 0.85
    draw_flow_box(ax, bx_right + 0.2, y_b3_1, bw - 0.4, h_b3_1,
                  "Temporal Incident Correlation Graph:\nCluster alerts: Edge(i,j) if |t_i - t_j| <= 45.0s & same IP/Device\nGroup 74,453 flow alerts into 91 multi-stage incidents\nAlert Fatigue Reduction: ARR = 99.88% (67 Crit, 24 High)",
                  font_size=8.0)
    draw_thin_down_arrow(ax, bx_right + bw/2.0, y_hdr3, y_b3_1 + h_b3_1)

    # Sub-box 2
    y_b3_2 = 2.90
    h_b3_2 = 0.85
    draw_flow_box(ax, bx_right + 0.2, y_b3_2, bw - 0.4, h_b3_2,
                  "MDP Incident Response Formulation:\nStates s = (S_t, tau_t, Delta S_t, rate_t),  Reward R(s, a, y)\nAction Space A: {ALLOW (0), ALERT (1), RATE_LIMIT (2), BLOCK (3)}",
                  font_size=8.0)
    draw_thin_down_arrow(ax, bx_right + bw/2.0, y_b3_1, y_b3_2 + h_b3_2)

    # Sub-box 3
    y_b3_3 = 1.60
    h_b3_3 = 0.95
    draw_flow_box(ax, bx_right + 0.2, y_b3_3, bw - 0.4, h_b3_3,
                  "Un-Contaminated DQN Bellman Update Rule:\nQ*(s, a) = r + gamma * max_a' Q(s', a'; theta^-)\nTrained strictly on X_sup; evaluated on held-out X_test\nAttack Containment: 71.26% +/- 0.85%,  False Block: 0.63%",
                  font_size=8.0)
    draw_thin_down_arrow(ax, bx_right + bw/2.0, y_b3_2, y_b3_3 + h_b3_3)

    # -------------------------------------------------------------
    # THICK BLOCK ARROW (Bottom Right -> Bottom Left)
    # -------------------------------------------------------------
    draw_thick_block_arrow(ax, bx_right - 0.15, 3.4, bx_left + bw + 0.15, 3.4, color="#2563eb", width=0.35, head_len=0.55, head_width=0.70)
    ax.text((bx_left + bw + bx_right)/2.0, 3.85, "Prioritized Incidents\n& Enforced Actions", ha='center', va='center',
            fontsize=7.8, fontweight='bold', color='#1d4ed8', zorder=6)

    # -------------------------------------------------------------
    # 4. BOTTOM LEFT BLOCK: POST-QUANTUM CRYPTOGRAPHY & FORENSIC INTEGRITY
    # -------------------------------------------------------------
    y_hdr4 = 5.25
    draw_flow_box(ax, bx_left, y_hdr4, bw, 0.65,
                  "Post-Quantum Cryptography & Forensic Integrity\n(NIST FIPS 203 ML-KEM-768 & Hash-Chain Audit Logging)",
                  is_header=True, font_size=9.2)

    # Sub-box 1
    y_b4_1 = 3.90
    h_b4_1 = 1.05
    draw_flow_box(ax, bx_left + 0.2, y_b4_1, bw - 0.4, h_b4_1,
                  "Standardized NIST ML-KEM-768 Key Encapsulation:\n(pk, sk) <- KeyGen(),  (c, K) <- Encaps(pk),  K <- Decaps(sk, c)\nLattice parameters: k=3, q=3329, eta1=eta2=2\nPayload Encryption: Ciphertext = AES-256-GCM_K(Incident_Record)\nSetup Latency: 0.429 ms, 100% Tamper Rejection",
                  font_size=8.0)
    draw_thin_down_arrow(ax, bx_left + bw/2.0, y_hdr4, y_b4_1 + h_b4_1)

    # Sub-box 2
    y_b4_2 = 2.45
    h_b4_2 = 1.10
    draw_flow_box(ax, bx_left + 0.2, y_b4_2, bw - 0.4, h_b4_2,
                  "Tamper-Evident SHA-256 Hash-Chain Audit Trail:\nh_i = SHA-256( h_{i-1} || rec_i || seq_i )\nVerify Integrity: Recompute and check h'_i == h_i\nAppend throughput: 19,379 records/s (0.0516 ms/append)\nGuarantees immutable sequence integrity & tamper localization",
                  font_size=8.0)
    draw_thin_down_arrow(ax, bx_left + bw/2.0, y_b4_1, y_b4_2 + h_b4_2)

    # STOP Oval
    draw_oval(ax, 1.1, y_b4_2 + h_b4_2 / 2.0, 1.5, 0.70, "STOP")
    # Arrow Bottom Left -> STOP
    ax.annotate("", xy=(1.85, y_b4_2 + h_b4_2 / 2.0), xytext=(bx_left, y_b4_2 + h_b4_2 / 2.0),
                arrowprops=dict(arrowstyle="-|>", color="#1e293b", lw=1.5, mutation_scale=14),
                zorder=5)

    # Caption at bottom
    ax.text(7.5, 0.45, "FIGURE 1. Methodology illustrated: The proposed DACC-ID end-to-end operational lifecycle.",
            ha='center', va='center', fontsize=10.5, fontweight='bold', color='#0f172a')

    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated Saeed-style methodology architecture diagram: {output_path}")

if __name__ == '__main__':
    main()
