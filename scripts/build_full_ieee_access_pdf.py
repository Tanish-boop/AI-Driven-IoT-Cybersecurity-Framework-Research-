"""
scripts/build_full_ieee_access_pdf.py

Compiles the complete, audited IEEE Access research paper into a
publication-grade double-column PDF with verified 300-DPI figures, exact
5-seed experimental tables, correct author metadata, and no unverified publisher claims.
"""

import os
import sys
import base64
import subprocess

def encode_image(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/png;base64,{encoded}"
    return ""

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fig_dir = os.path.join(repo_root, "paper", "figures")
    output_pdf = os.path.join(repo_root, "paper", "IEEE_Access_Final_Manuscript.pdf")
    submission_pdf = os.path.join(repo_root, "submission", "paper", "IEEE_Access_Final_Manuscript.pdf")
    html_out = os.path.join(repo_root, "paper", "manuscript_formatted.html")

    # Load verified images as Base64 for headless rendering
    f0 = encode_image(os.path.join(fig_dir, "figure0_system_architecture.png"))
    f1 = encode_image(os.path.join(fig_dir, "figure1_threshold_comparison.png"))
    f2 = encode_image(os.path.join(fig_dir, "figure2_rate_stress_test.png"))
    f3 = encode_image(os.path.join(fig_dir, "figure3_per_attack_recall.png"))
    f4 = encode_image(os.path.join(fig_dir, "figure4_defense_rewards.png"))
    f5 = encode_image(os.path.join(fig_dir, "figure5_pqc_latency.png"))
    f6 = encode_image(os.path.join(fig_dir, "figure6_integrity_benchmark.png"))
    f7 = encode_image(os.path.join(fig_dir, "figure7_ablation_comparison.png"))

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>An AI-Driven Adaptive Cybersecurity Framework for IoT</title>
<style>
@page {{
    size: letter;
    margin: 18mm 14mm 18mm 14mm;
    @bottom-right {{
        content: counter(page);
    }}
}}

body {{
    font-family: 'Times New Roman', Times, serif;
    font-size: 10pt;
    line-height: 1.25;
    color: #111;
    margin: 0;
    padding: 0;
}}

/* Clean IEEE Access Draft Header Banner */
.ieee-banner {{
    border-bottom: 2px solid #002855;
    padding-bottom: 4px;
    margin-bottom: 14px;
    display: flex;
    justify-content: space-between;
    font-size: 7.5pt;
    font-weight: bold;
    color: #002855;
    letter-spacing: 0.5px;
}}

.title-block {{
    text-align: center;
    margin-bottom: 16px;
}}

h1.paper-title {{
    font-size: 18.5pt;
    font-weight: bold;
    line-height: 1.2;
    margin: 0 0 10px 0;
    color: #000;
}}

.authors {{
    font-size: 11pt;
    font-variant: small-caps;
    margin-bottom: 4px;
}}

.affiliations {{
    font-size: 8.5pt;
    font-style: italic;
    color: #444;
    margin-bottom: 8px;
    line-height: 1.3;
}}

.pub-meta {{
    font-size: 8pt;
    color: #555;
    margin-bottom: 14px;
}}

/* Abstract Box */
.abstract-box {{
    background: #fbfbfb;
    border: 1px solid #ddd;
    border-left: 3px solid #002855;
    padding: 10px 14px;
    margin-bottom: 16px;
    font-size: 9pt;
    text-align: justify;
    line-height: 1.35;
}}

.abstract-box strong {{
    color: #002855;
    font-variant: small-caps;
}}

.keywords {{
    margin-top: 6px;
    font-size: 8.5pt;
    font-weight: normal;
}}

/* Two Column Layout */
.columns {{
    column-count: 2;
    column-gap: 18px;
    column-rule: 0.5px solid #eaeaea;
    text-align: justify;
    text-justify: inter-word;
}}

h2.section-heading {{
    column-span: none;
    font-size: 10.5pt;
    font-weight: bold;
    font-variant: small-caps;
    color: #002855;
    border-bottom: 1px solid #002855;
    margin-top: 14px;
    margin-bottom: 6px;
    padding-bottom: 2px;
}}

h3.subheading {{
    font-size: 9.5pt;
    font-weight: bold;
    font-style: italic;
    color: #222;
    margin-top: 10px;
    margin-bottom: 4px;
}}

p {{
    margin: 0 0 8px 0;
    text-indent: 14px;
}}

p.no-indent {{
    text-indent: 0;
}}

/* Figures and Tables */
.figure-container {{
    break-inside: avoid;
    margin: 10px 0;
    text-align: center;
}}

.figure-container.full-width {{
    column-span: all;
    margin: 14px 0;
}}

.figure-container img {{
    max-width: 100%;
    height: auto;
    border: 1px solid #e0e0e0;
    border-radius: 2px;
}}

.caption {{
    font-size: 8pt;
    font-style: italic;
    margin-top: 4px;
    color: #333;
    text-align: center;
}}

.table-container {{
    break-inside: avoid;
    margin: 10px 0;
}}

.table-container.full-width {{
    column-span: all;
    margin: 14px 0;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 7.5pt;
    line-height: 1.25;
    margin-top: 4px;
}}

th, td {{
    border-top: 0.5px solid #ccc;
    border-bottom: 0.5px solid #ccc;
    padding: 3px 4px;
    text-align: left;
}}

th {{
    background-color: #f2f5f9;
    font-weight: bold;
    color: #002855;
    border-top: 1.5px solid #002855;
    border-bottom: 1.5px solid #002855;
}}

.table-caption {{
    font-size: 8pt;
    font-weight: bold;
    text-align: center;
    color: #002855;
    font-variant: small-caps;
    margin-bottom: 3px;
}}

/* Equation formatting */
.equation {{
    text-align: center;
    margin: 6px 0;
    font-family: 'Cambria Math', 'Times New Roman', serif;
    font-style: italic;
    font-size: 9.5pt;
}}

.eq-num {{
    float: right;
    font-style: normal;
}}

/* Callout Box */
.disclosure-box {{
    background-color: #f8f9fa;
    border: 1px dashed #002855;
    padding: 6px 8px;
    font-size: 8pt;
    margin: 8px 0;
    line-height: 1.3;
    break-inside: avoid;
}}

/* References */
.references ol {{
    padding-left: 16px;
    margin: 0;
    font-size: 7.8pt;
    line-height: 1.3;
}}

.references li {{
    margin-bottom: 4px;
    text-align: left;
}}
</style>
</head>
<body>

<div class="ieee-banner">
    <span>IEEE ACCESS MANUSCRIPT TEMPLATE &bull; RESEARCH PREPRINT</span>
    <span>DATE OF DRAFT: OCTOBER 12, 2026 &bull; PREPARED FOR JOURNAL PEER REVIEW</span>
</div>

<div class="title-block">
    <h1 class="paper-title">An AI-Driven Adaptive Cybersecurity Framework for IoT: Anomaly Detection, Dynamic Thresholding, Un-Contaminated Reinforcement Learning Defense, Post-Quantum Cryptography, and Tamper-Evident Audit Logging</h1>
    <div class="authors">Tanish Thakare</div>
    <div class="affiliations">
        Department of Computer Science and Engineering, Independent Research<br>
        Corresponding Author Email: tanish.thakare2005@gmail.com
    </div>
    <div class="pub-meta">
        Manuscript Working Draft &bull; October 12, 2026.<br>
        Verified Open-Access Code Repository: <a href="https://github.com/Tanish-boop/AI-Driven-IoT-Cybersecurity-Framework-Research-">https://github.com/Tanish-boop/AI-Driven-IoT-Cybersecurity-Framework-Research-</a>
    </div>
</div>

<div class="abstract-box">
    <strong>Abstract</strong>&mdash;In Internet of Things (IoT) edge cybersecurity, deep reconstruction-based autoencoders provide effective detection of zero-day network intrusions without requiring labeled attack samples during training. However, translating continuous reconstruction errors into operational mitigation decisions faces critical vulnerabilities: static decision thresholds explode in false alarms under non-stationary traffic surges, un-guarded adaptive thresholds suffer severe threshold inflation collapse during attack floods, defensive reinforcement learning policies risk evaluation split contamination, and existing literature relies on abstract non-standardized cryptographic assumptions. This paper presents an empirically rigorous benchmark evaluating an integrated five-stage cybersecurity framework on CICIoT2023 across 5 random seeds (42, 123, 456, 789, 2026) under strictly isolated training, validation, supervised, and held-out test splits. Our empirical results establish that: (1) Sample-level Dense Autoencoders (<em>L</em>=1) eliminate sequence window boundary contamination, achieving an unsupervised baseline F1-Score of <strong>0.8854 &plusmn; 0.0013</strong> (Precision: 0.9893, Recall: 0.8013, FPR: 0.0493 &plusmn; 0.0013); (2) Excluded EWMA thresholding prevents inflation collapse, reaching F1 = <strong>0.9014 &plusmn; 0.0018</strong> and coming within 2.55% of a supervised XGBoost oracle (F1 = 0.9269 &plusmn; 0.0004), albeit with an elevated false positive rate (13.60 &plusmn; 1.10%); (3) Static 95th percentile thresholds suffer a +454.4% explosion in false positive rates under 2.0&times; synthetic rate feature scaling; (4) Under strictly un-contaminated evaluation (<em>X</em><sub>sup</sub> training, held-out <em>X</em><sub>test</sub> evaluation), Deep Q-Networks achieve <strong>71.26 &plusmn; 0.09%</strong> attack containment with <strong>0.63 &plusmn; 0.46%</strong> false block rate (decision latency: 0.1160 &plusmn; 0.0052 ms), while Tabular Q-Learning achieves a 0.00% false block rate in isolated testing; (5) Standardized NIST FIPS 203 ML-KEM-768 key encapsulation paired with AES-256-GCM achieves sub-millisecond key establishment (<strong>0.2758 ms</strong> KEM, 0.2905 ms first-message setup) and 100% tamper rejection; (6) HMAC-SHA-256 (0.0470 ms creation) and Tamper-Evident Hash-Chain Audit Logging (0.0605 ms append, <em>O</em>(1) scaling) provide verifiable sequence integrity and tamper localization; (7) In sensitivity testing, evaluating on a deduplicated test set (<em>N</em>=98,543) purging all 1,457 cross-partition duplicates shifts F1 by at most &minus;0.0009 (&minus;0.10%), confirming that repeated feature patterns do not materially inflate evaluation metrics; and (8) The full integrated framework achieves an end-to-end F1-Score of <strong>0.8968 &plusmn; 0.0013</strong> and <strong>81.01% &plusmn; 2.83%</strong> attack containment with edge processing latency of <strong>0.9626 &plusmn; 0.6304 ms</strong> (1,436.2 &plusmn; 759.5 events/s throughput).
    <div class="keywords">
        <strong>Index Terms</strong>&mdash;Internet of Things (IoT), Anomaly Detection, Adaptive Thresholding, Reinforcement Learning, Post-Quantum Cryptography, NIST FIPS 203, ML-KEM-768, Tamper-Evident Hash Chain, CICIoT2023.
    </div>
</div>

<div class="columns">

<h2 class="section-heading">I. Introduction</h2>
<p class="no-indent">The exponential expansion of Internet of Things (IoT) deployments across critical infrastructure, industrial automation, and consumer environments has widened the network attack surface. Edge devices and gateways regularly encounter automated botnets, distributed denial-of-service (DDoS) floods, stealthy reconnaissance scans, and weaponized firmware exploits. Traditional signature-based Intrusion Detection Systems (IDS) fail against polymorphic variants and zero-day attack vectors.</p>

<p>Deep learning approaches&mdash;specifically unsupervised reconstruction-based autoencoders&mdash;have emerged as an effective paradigm for IoT anomaly detection. By training exclusively on benign telemetry flows, the model learns the normal representation manifold. During operational inference, flows generating high reconstruction errors:</p>

<div class="equation">
    <i>E<sub>t</sub></i> = ||<b>x</b><sub><i>t</i></sub> &minus; <b>x̂</b><sub><i>t</i></sub>||<sup>2</sup> = &sum;<sub><i>j</i>=1</sub><sup><i>D</i></sup> (<i>x<sub>t,j</sub></i> &minus; <i>x̂<sub>t,j</sub></i>)<sup>2</sup>
    <span class="eq-num">(1)</span>
</div>

<p class="no-indent">are flagged as anomalies whenever <i>E<sub>t</sub></i> exceeds a decision boundary &tau;<sub><i>t</i></sub>. However, practical deployment in operational IoT edge environments is hindered by four critical challenges:</p>

<p><strong>1. Threshold Brittleness and Inflation:</strong> Literature predominantly relies on static percentile thresholds (&tau;<sub>95</sub>, &tau;<sub>99</sub>) calibrated during offline validation. Under non-stationary traffic bursts or benign rate increases, fixed thresholds trigger severe false-alarm storms. Conversely, conventional adaptive algorithms like Exponentially Weighted Moving Average (EWMA) dynamically incorporate hostile attack traffic into background statistics, causing <em>threshold inflation</em> and complete detection failure during sustained floods.</p>

<p><strong>2. Evaluation Contamination in Mitigation Policies:</strong> Reinforcement learning (RL) policies for automated mitigation are frequently trained and evaluated on overlapping data partitions, obscuring generalization failure and overfitting.</p>

<p><strong>3. Abstract vs. Standardized Cryptography:</strong> Existing literature frequently claims "post-quantum encryption" without evaluating concrete standardized primitives. NIST FIPS 203 (ML-KEM) requires rigorous empirical benchmarking under IoT edge latency and memory constraints.</p>

<p><strong>4. Forensic Audit Logging Boundaries:</strong> Edge gateways require verifiable audit trails to guarantee incident provenance. However, the local storage trust boundary against privileged host adversaries must be clearly formulated rather than asserting unqualified blockchain immutability.</p>

<h2 class="section-heading">II. System Architecture</h2>
<p class="no-indent">The proposed architecture integrates five synchronized defensive stages within a lightweight edge pipeline, illustrated in Figure 1:</p>

<div class="figure-container">
    <img src="{f0}" alt="System Architecture">
    <div class="caption"><strong>FIGURE 1.</strong> Five-Stage Integrated IoT Edge Cybersecurity Framework Architecture.</div>
</div>

<p><strong>Stage 1 (Feature Normalization):</strong> 39 numerical flow features are extracted from incoming packets. Non-numeric metadata identifiers (<code>src_ip</code>, <code>dst_ip</code>, <code>src_port</code>, <code>dst_port</code>, <code>Timestamp</code>, <code>flow_id</code>) are purged to eliminate shortcut memorization. Features are normalized via StandardScaler fitted exclusively on <em>X</em><sub>train</sub>.</p>

<p><strong>Stage 2 (Reconstruction Inference & Excluded EWMA):</strong> The normalized vector is passed through a 4-layer symmetrical Dense Autoencoder (39 &rarr; 24 &rarr; 12 &rarr; 24 &rarr; 39). Reconstruction error <i>E<sub>t</sub></i> is compared against an adaptive threshold &tau;<sub><i>t</i></sub>. When <i>E<sub>t</sub></i> &le; &tau;<sub><i>t</i></sub>, the flow is classified as benign and background statistics are updated. When <i>E<sub>t</sub></i> &gt; &tau;<sub><i>t</i></sub>, the flow is flagged as an anomaly and the sample is strictly <strong>excluded</strong> from statistical updating, preventing threshold inflation.</p>

<p><strong>Stage 3 (Un-Contaminated RL Response):</strong> Flagged alerts are routed to a Deep Q-Network (DQN) mitigation agent maintaining an internal state (flow rate, anomaly score, consecutive alert streak). The policy selects actions: <em>Pass</em>, <em>Rate-Limit</em>, or <em>Isolate/Block</em>, balancing attack containment against false disruption.</p>

<p><strong>Stage 4 (Post-Quantum Transport Encryption):</strong> High-priority incident telemetry is encapsulated using NIST FIPS 203 ML-KEM-768, deriving a 256-bit symmetric session key via HKDF-SHA256, and encrypted via AES-256-GCM AEAD.</p>

<p><strong>Stage 5 (Tamper-Evident Hash-Chain Logging):</strong> Forensic incident records are appended to an immutable cryptographic hash chain where block <i>k</i> encapsulates the SHA-256 digest of block <i>k</i>&minus;1.</p>

<h2 class="section-heading">III. Dataset & Strict Split Protocol</h2>
<p class="no-indent">Experiments are conducted on <strong>CICIoT2023</strong> (Neto et al., <em>Sensors</em>, 2023). To guarantee absolute data isolation, the benchmark implements four strict partitions:</p>
<p>&bull; <strong><i>X</i><sub>train</sub>:</strong> 100,000 pure benign flows (scaler fitting and unsupervised autoencoder training).<br>
&bull; <strong><i>X</i><sub>val</sub>:</strong> 30,000 pure benign flows (offline threshold calibration &tau;<sub>95</sub>, &tau;<sub>99</sub>).<br>
&bull; <strong><i>X</i><sub>sup</sub>:</strong> 40,000 50/50 benign/attack flows (supervised XGBoost and RL training).<br>
&bull; <strong><i>X</i><sub>test</sub>:</strong> 100,000 held-out flows (14,911 benign, 85,089 attack) for all evaluations.</p>

<div class="disclosure-box">
    <strong>Data Integrity & Deduplication Disclosure:</strong><br>
    Identical feature vectors occur naturally during high-rate attack bursts (e.g. uniform SYN flood packet sizes). We evaluated the entire benchmark on both the full test set (<em>N</em>=100k) and a strictly deduplicated test set (<em>N</em>=98.5k) where all 1,457 cross-partition duplicates were purged. F1-scores shifted by at most &minus;0.10%, confirming that repeated vectors do not inflate reported performance.
</div>

<h2 class="section-heading">IV. Experimental Results (E1–E8)</h2>

<h3 class="subheading">A. Detection Baselines & Threshold Strategies (E1, E2)</h3>
<p class="no-indent">Table I summarizes the anomaly detection benchmark across 5 standardized random seeds (42, 123, 456, 789, 2026):</p>

<div class="table-container">
    <div class="table-caption">TABLE I. Base Test Stream Performance (5 Random Seeds)</div>
    <table>
        <thead>
            <tr>
                <th>Model</th>
                <th>Threshold Strategy</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1-Score</th>
                <th>FPR</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Dense-AE</strong></td>
                <td><strong>Excluded EWMA</strong></td>
                <td>0.9724 &plusmn; 0.0022</td>
                <td><strong>0.8401 &plusmn; 0.0023</strong></td>
                <td><strong>0.9014 &plusmn; 0.0018</strong></td>
                <td>0.1360 &plusmn; 0.0110</td>
            </tr>
            <tr>
                <td>Dense-AE</td>
                <td>Fixed 95th Percentile</td>
                <td>0.9893 &plusmn; 0.0003</td>
                <td>0.8013 &plusmn; 0.0022</td>
                <td>0.8854 &plusmn; 0.0013</td>
                <td>0.0493 &plusmn; 0.0013</td>
            </tr>
            <tr>
                <td>Dense-AE</td>
                <td>Fixed 99th Percentile</td>
                <td>0.9975 &plusmn; 0.0001</td>
                <td>0.7650 &plusmn; 0.0017</td>
                <td>0.8659 &plusmn; 0.0011</td>
                <td>0.0108 &plusmn; 0.0004</td>
            </tr>
            <tr>
                <td>Dense-AE</td>
                <td>Guarded EWMA</td>
                <td>1.0000 &plusmn; 0.0000</td>
                <td>0.0022 &plusmn; 0.0000</td>
                <td>0.0045 &plusmn; 0.0001</td>
                <td>0.0000 &plusmn; 0.0000</td>
            </tr>
            <tr>
                <td>Dense-AE</td>
                <td>Un-Guarded EWMA</td>
                <td>1.0000 &plusmn; 0.0000</td>
                <td>0.0001 &plusmn; 0.0000</td>
                <td>0.0003 &plusmn; 0.0001</td>
                <td>0.0000 &plusmn; 0.0000</td>
            </tr>
            <tr>
                <td>Isolation Forest</td>
                <td>Fixed 95th Percentile</td>
                <td>0.9866 &plusmn; 0.0003</td>
                <td>0.6402 &plusmn; 0.0114</td>
                <td>0.7765 &plusmn; 0.0084</td>
                <td>0.0495 &plusmn; 0.0009</td>
            </tr>
            <tr>
                <td><strong>XGBoost Oracle</strong></td>
                <td>Supervised (p=0.5)</td>
                <td>0.9967 &plusmn; 0.0002</td>
                <td><strong>0.8662 &plusmn; 0.0009</strong></td>
                <td><strong>0.9269 &plusmn; 0.0004</strong></td>
                <td>0.0162 &plusmn; 0.0012</td>
            </tr>
        </tbody>
    </table>
</div>

<div class="figure-container">
    <img src="{f1}" alt="F1 Comparison">
    <div class="caption"><strong>FIGURE 2.</strong> Dense-AE Performance and False Positive Rates Across Threshold Adaptation Strategies (5 Seeds, Mean &plusmn; Std).</div>
</div>

<p>As evident in Table I, Un-Guarded EWMA experiences complete threshold inflation collapse: as attack records enter the evaluation window, the mean reconstruction error expands exponentially, raising &tau;<sub><i>t</i></sub> above attack error levels and driving recall to 0.01% (F1 = 0.0003). In contrast, <strong>Excluded EWMA</strong> prevents hostile sample pollution, achieving F1 = <strong>0.9014 &plusmn; 0.0018</strong>, outperforming Fixed 95th (0.8854) and Fixed 99th (0.8659). However, Excluded EWMA incurs an elevated FPR (13.60% vs 4.93%), representing an operational trade-off.</p>

<h3 class="subheading">B. Deduplication Sensitivity Evaluation</h3>
<p class="no-indent">Table II establishes metric stability when removing identical feature vectors across partitions:</p>

<div class="table-container">
    <div class="table-caption">TABLE II. Deduplication Sensitivity Analysis (5 Seeds)</div>
    <table>
        <thead>
            <tr>
                <th>Model / Strategy</th>
                <th>Full Test F1</th>
                <th>Clean Test F1</th>
                <th>F1 Delta</th>
                <th>Clean FPR</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Dense-AE Fixed 95th</td>
                <td>0.8854 &plusmn; 0.0013</td>
                <td>0.8845 &plusmn; 0.0014</td>
                <td>&minus;0.0009 (&minus;0.10%)</td>
                <td>0.0492 &plusmn; 0.0013</td>
            </tr>
            <tr>
                <td>Dense-AE Excluded EWMA</td>
                <td>0.9014 &plusmn; 0.0018</td>
                <td>0.9007 &plusmn; 0.0019</td>
                <td>&minus;0.0007 (&minus;0.08%)</td>
                <td>0.1363 &plusmn; 0.0115</td>
            </tr>
            <tr>
                <td>XGBoost Oracle</td>
                <td>0.9269 &plusmn; 0.0004</td>
                <td>0.9265 &plusmn; 0.0003</td>
                <td>&minus;0.0003 (&minus;0.03%)</td>
                <td>0.0160 &plusmn; 0.0011</td>
            </tr>
        </tbody>
    </table>
</div>

<h3 class="subheading">C. Rate Feature Stress Testing (E3, E8)</h3>
<p class="no-indent">Table III and Figure 3 quantify the vulnerability of static thresholds under synthetic rate feature value scaling (1.0&times;, 1.5&times;, 2.0&times;):</p>

<div class="table-container">
    <div class="table-caption">TABLE III. Rate Feature Stress Test Performance (E8)</div>
    <table>
        <thead>
            <tr>
                <th>Scaling</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1-Score</th>
                <th>FPR</th>
                <th>FPR Shift</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>1.0&times; (Base)</td>
                <td>0.9893 &plusmn; 0.0003</td>
                <td>0.8013 &plusmn; 0.0022</td>
                <td>0.8854 &plusmn; 0.0013</td>
                <td>0.0493 &plusmn; 0.0013</td>
                <td>Baseline</td>
            </tr>
            <tr>
                <td>1.5&times;</td>
                <td>0.9796 &plusmn; 0.0019</td>
                <td>0.8013 &plusmn; 0.0022</td>
                <td>0.8815 &plusmn; 0.0017</td>
                <td>0.0953 &plusmn; 0.0092</td>
                <td>+93.3%</td>
            </tr>
            <tr>
                <td>2.0&times;</td>
                <td>0.9436 &plusmn; 0.0030</td>
                <td>0.8013 &plusmn; 0.0022</td>
                <td>0.8666 &plusmn; 0.0021</td>
                <td><strong>0.2733 &plusmn; 0.0152</strong></td>
                <td><strong>+454.4%</strong></td>
            </tr>
        </tbody>
    </table>
</div>

<div class="figure-container">
    <img src="{f2}" alt="FPR Stress Test">
    <div class="caption"><strong>FIGURE 3.</strong> False Positive Rate Explosion Under Synthetic Rate Feature Scaling on Dense-AE Fixed 95th (E8).</div>
</div>

<p><em>Operational Scope Disclosure</em>: In Experiment E8, synthetic scaling was applied strictly to rate features (`Rate`, `Tot size`, `Variance`) of benign test samples for Fixed 95th Percentile thresholding to evaluate sensitivity to burst telemetry. Excluded EWMA was evaluated on the base stream in Experiment E2 and was not re-evaluated under synthetic feature scaling in E8; threshold stability claims are strictly confined to the dynamic stream conditions tested in E2.</p>

<h3 class="subheading">D. Granular Attack-Class Breakdown</h3>
<p class="no-indent">Table IV and Figure 4 depict recall breakdown across 7 attack classes on the held-out test stream:</p>

<div class="table-container">
    <div class="table-caption">TABLE IV. Dense-AE Detection Recall Across 7 Attack Categories (Held-Out Test Set)</div>
    <table>
        <thead>
            <tr>
                <th>Attack Category</th>
                <th>Sample Count</th>
                <th>Fixed 95th Recall</th>
                <th>Excluded EWMA Recall</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>DDoS</td>
                <td>33,483</td>
                <td>100.0%</td>
                <td>100.0%</td>
            </tr>
            <tr>
                <td>DoS</td>
                <td>15,107</td>
                <td>100.0%</td>
                <td>100.0%</td>
            </tr>
            <tr>
                <td>Mirai</td>
                <td>11,160</td>
                <td>100.0%</td>
                <td>100.0%</td>
            </tr>
            <tr>
                <td>BruteForce</td>
                <td>965</td>
                <td>42.80%</td>
                <td><strong>55.54%</strong></td>
            </tr>
            <tr>
                <td>Reconnaissance</td>
                <td>15,038</td>
                <td>38.18%</td>
                <td><strong>49.19%</strong></td>
            </tr>
            <tr>
                <td>Spoofing</td>
                <td>7,451</td>
                <td>23.38%</td>
                <td><strong>39.15%</strong></td>
            </tr>
            <tr>
                <td>Web-based</td>
                <td>1,885</td>
                <td>20.42%</td>
                <td><strong>37.88%</strong></td>
            </tr>
            <tr>
                <td><strong>Total Attack Stream</strong></td>
                <td><strong>85,089</strong></td>
                <td><strong>79.95%</strong></td>
                <td><strong>83.81%</strong></td>
            </tr>
        </tbody>
    </table>
</div>

<div class="figure-container">
    <img src="{f3}" alt="Attack Recall">
    <div class="caption"><strong>FIGURE 4.</strong> Dense-AE Detection Recall Breakdown Across 7 Attack Categories on Held-Out Test Set.</div>
</div>

<h3 class="subheading">E. Un-Contaminated RL Defense Mitigation (E4)</h3>
<p class="no-indent">Table V compares Static Rule, Tabular Q-Learning, and Deep Q-Network (DQN) mitigation policies under strict held-out evaluation on <em>X</em><sub>test</sub>:</p>

<div class="table-container">
    <div class="table-caption">TABLE V. Defensive Mitigation Policy Performance under Held-Out Evaluation (5 Seeds)</div>
    <table>
        <thead>
            <tr>
                <th>Scenario / Policy</th>
                <th>Cumulative Reward</th>
                <th>Attack Containment</th>
                <th>False Block Rate</th>
                <th>Latency (ms)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Scenario 1 (Heavy)</strong></td>
                <td colspan="4"></td>
            </tr>
            <tr>
                <td>&bull; Static Rule</td>
                <td>35,402.00 &plusmn; 0.00</td>
                <td>99.98% &plusmn; 0.00%</td>
                <td>100.00% &plusmn; 0.00%</td>
                <td>0.0123 &plusmn; 0.0033</td>
            </tr>
            <tr>
                <td>&bull; Tabular Q</td>
                <td>17,199.00 &plusmn; 3,799.62</td>
                <td>60.45% &plusmn; 11.91%</td>
                <td><strong>0.00% &plusmn; 0.00%</strong></td>
                <td><strong>0.0122 &plusmn; 0.0003</strong></td>
            </tr>
            <tr>
                <td>&bull; <strong>DQN</strong></td>
                <td><strong>28,513.20 &plusmn; 122.92</strong></td>
                <td><strong>71.26% &plusmn; 0.09%</strong></td>
                <td><strong>0.63% &plusmn; 0.46%</strong></td>
                <td>0.1160 &plusmn; 0.0052</td>
            </tr>
            <tr>
                <td><strong>Scenario 2 (Stealth)</strong></td>
                <td colspan="4"></td>
            </tr>
            <tr>
                <td>&bull; Static Rule</td>
                <td>35,762.00 &plusmn; 0.00</td>
                <td>99.98% &plusmn; 0.00%</td>
                <td>100.00% &plusmn; 0.00%</td>
                <td>0.0115 &plusmn; 0.0015</td>
            </tr>
            <tr>
                <td>&bull; Tabular Q</td>
                <td>16,661.60 &plusmn; 4,096.27</td>
                <td>59.27% &plusmn; 11.50%</td>
                <td><strong>0.00% &plusmn; 0.00%</strong></td>
                <td><strong>0.0122 &plusmn; 0.0002</strong></td>
            </tr>
            <tr>
                <td>&bull; <strong>DQN</strong></td>
                <td><strong>29,506.00 &plusmn; 156.37</strong></td>
                <td><strong>73.06% &plusmn; 0.09%</strong></td>
                <td><strong>0.48% &plusmn; 0.39%</strong></td>
                <td>0.1226 &plusmn; 0.0120</td>
            </tr>
        </tbody>
    </table>
</div>

<div class="figure-container">
    <img src="{f4}" alt="Defense Policy Rewards">
    <div class="caption"><strong>FIGURE 5.</strong> Cumulative Reward and Containment vs. Disruption Trade-off Across RL Policies (E4).</div>
</div>

<p>While Static Rule achieves 99.98% containment, it indiscriminately blocks 100% of benign traffic during attack periods, resulting in total denial of legitimate service. In contrast, <strong>DQN</strong> balances containment (71.26% to 73.06%) with ultra-low false blocking (0.48% to 0.63%).</p>

<h3 class="subheading">F. Post-Quantum Cryptography Microbenchmark (E5)</h3>
<p class="no-indent">Table VI and Figure 6 report key encapsulation latency and transmission overhead for NIST FIPS 203 ML-KEM paired with AES-256-GCM AEAD over 100 trials for 1024-byte telemetry payloads:</p>

<div class="table-container">
    <div class="table-caption">TABLE VI. NIST FIPS 203 PQC Microbenchmark (1024-Byte Payload, AMD64)</div>
    <table>
        <thead>
            <tr>
                <th>Variant</th>
                <th>Public Key</th>
                <th>Ciphertext</th>
                <th>Total KEM (ms)</th>
                <th>First Msg (ms)</th>
                <th>Tamper Rej</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>ML-KEM-512</strong></td>
                <td>800 B</td>
                <td>768 B</td>
                <td>0.1757 ms</td>
                <td>0.1895 ms</td>
                <td>100.0%</td>
            </tr>
            <tr>
                <td><strong>ML-KEM-768</strong></td>
                <td>1,184 B</td>
                <td>1,088 B</td>
                <td><strong>0.2758 ms</strong></td>
                <td><strong>0.2905 ms</strong></td>
                <td><strong>100.0%</strong></td>
            </tr>
            <tr>
                <td><strong>ML-KEM-1024</strong></td>
                <td>1,568 B</td>
                <td>1,568 B</td>
                <td>0.4363 ms</td>
                <td>0.4538 ms</td>
                <td>100.0%</td>
            </tr>
        </tbody>
    </table>
</div>

<div class="figure-container">
    <img src="{f5}" alt="PQC Latency">
    <div class="caption"><strong>FIGURE 6.</strong> Post-Quantum Key Encapsulation Latency and Artifact Transmission Footprints (E5).</div>
</div>

<h3 class="subheading">G. Cryptographic Integrity Benchmark (E6)</h3>
<p class="no-indent">Table VII and Figure 7 compare three integrity mechanisms on 1 KiB event records over 100 trials:</p>

<div class="table-container">
    <div class="table-caption">TABLE VII. Cryptographic Integrity Verification Microbenchmarks (1 KiB Records)</div>
    <table>
        <thead>
            <tr>
                <th>Mechanism</th>
                <th>Create (ms)</th>
                <th>Verify (ms)</th>
                <th>Overhead</th>
                <th>Throughput</th>
                <th>Security Guarantee</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Salted SHA-256</td>
                <td>0.0468 &plusmn; 0.0240</td>
                <td>0.0207 &plusmn; 0.0134</td>
                <td>193 B</td>
                <td>20.85 MB/s</td>
                <td>Accidental errors (Unkeyed)</td>
            </tr>
            <tr>
                <td>HMAC-SHA-256</td>
                <td>0.0470 &plusmn; 0.0209</td>
                <td>0.0214 &plusmn; 0.0097</td>
                <td>170 B</td>
                <td>20.79 MB/s</td>
                <td>Authenticity (Keyed)</td>
            </tr>
            <tr>
                <td><strong>Hash Chain Log</strong></td>
                <td><strong>0.0605 &plusmn; 0.0248</strong></td>
                <td><strong>0.0328 &plusmn; 0.0310</strong></td>
                <td>318 B</td>
                <td>16.15 MB/s</td>
                <td><strong>Sequence & Tamper Localized</strong></td>
            </tr>
        </tbody>
    </table>
</div>

<div class="figure-container">
    <img src="{f6}" alt="Integrity Benchmark">
    <div class="caption"><strong>FIGURE 7.</strong> Processing Latency and Throughput of Integrity Architectures (E6).</div>
</div>

<h2 class="section-heading">V. Integrated Framework Ablation (E7)</h2>
<p class="no-indent">Table VIII and Figure 8 provide the holistic multi-dimensional ablation evaluation across 5 random seeds (42, 123, 456, 789, 2026) directly matching verified raw experimental summaries:</p>

<div class="table-container full-width">
    <div class="table-caption">TABLE VIII. End-to-End Integrated Framework and Modular Ablation Study Across 5 Standardized Seeds (E7)</div>
    <table>
        <thead>
            <tr>
                <th>System Configuration</th>
                <th>F1-Score</th>
                <th>Recall (%)</th>
                <th>Containment (%)</th>
                <th>False Block (%)</th>
                <th>Availability (%)</th>
                <th>Latency (ms)</th>
                <th>Throughput (ev/s)</th>
                <th>Overhead</th>
                <th>Quantum-Safe</th>
                <th>Audit Integrity</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Study-Defined Baseline (Adapted Saeed)</strong></td>
                <td>0.8837 &plusmn; 0.0004</td>
                <td>79.88% &plusmn; 0.06%</td>
                <td>79.88% &plusmn; 0.06%</td>
                <td>3.20% &plusmn; 0.07%</td>
                <td>96.80% &plusmn; 0.07%</td>
                <td>0.8103 &plusmn; 0.5338</td>
                <td>1,676.4 &plusmn; 866.9</td>
                <td>194 B</td>
                <td>No (Vulnerable)</td>
                <td>No (Unkeyed)</td>
            </tr>
            <tr>
                <td><strong>Ablation (&minus;Adaptive Threshold)</strong></td>
                <td>0.8837 &plusmn; 0.0004</td>
                <td>79.88% &plusmn; 0.06%</td>
                <td>80.58% &plusmn; 3.12%</td>
                <td>5.46% &plusmn; 2.55%</td>
                <td>94.54% &plusmn; 2.55%</td>
                <td>0.8579 &plusmn; 0.5443</td>
                <td>1,496.5 &plusmn; 676.6</td>
                <td>321 B</td>
                <td>Yes (NIST ML-KEM)</td>
                <td>Yes (Hash Chain)</td>
            </tr>
            <tr>
                <td><strong>Ablation (&minus;RL Defense)</strong></td>
                <td>0.8968 &plusmn; 0.0013</td>
                <td>82.68% &plusmn; 0.24%</td>
                <td>79.78% &plusmn; 0.06%</td>
                <td>3.22% &plusmn; 0.06%</td>
                <td>96.78% &plusmn; 0.06%</td>
                <td>0.9737 &plusmn; 0.7128</td>
                <td>1,534.4 &plusmn; 873.1</td>
                <td>321 B</td>
                <td>Yes (NIST ML-KEM)</td>
                <td>Yes (Hash Chain)</td>
            </tr>
            <tr>
                <td><strong>Ablation (&minus;PQC)</strong></td>
                <td>0.8968 &plusmn; 0.0013</td>
                <td>82.68% &plusmn; 0.24%</td>
                <td>81.01% &plusmn; 2.83%</td>
                <td>6.01% &plusmn; 1.52%</td>
                <td>93.99% &plusmn; 1.52%</td>
                <td>0.9103 &plusmn; 0.5070</td>
                <td>1,402.5 &plusmn; 717.6</td>
                <td>321 B</td>
                <td>No (Vulnerable)</td>
                <td>Yes (Hash Chain)</td>
            </tr>
            <tr>
                <td><strong>Ablation (&minus;Hash Chain Log)</strong></td>
                <td>0.8968 &plusmn; 0.0013</td>
                <td>82.68% &plusmn; 0.24%</td>
                <td>81.01% &plusmn; 2.83%</td>
                <td>6.01% &plusmn; 1.52%</td>
                <td>93.99% &plusmn; 1.52%</td>
                <td>1.2107 &plusmn; 0.7004</td>
                <td>1,196.6 &plusmn; 819.5</td>
                <td>194 B</td>
                <td>Yes (NIST ML-KEM)</td>
                <td>No (Unkeyed)</td>
            </tr>
            <tr>
                <td><strong>Full Proposed Framework</strong></td>
                <td><strong>0.8968 &plusmn; 0.0013</strong></td>
                <td><strong>82.68% &plusmn; 0.24%</strong></td>
                <td><strong>81.01% &plusmn; 2.83%</strong></td>
                <td>6.01% &plusmn; 1.52%</td>
                <td>93.99% &plusmn; 1.52%</td>
                <td><strong>0.9626 &plusmn; 0.6304</strong></td>
                <td><strong>1,436.2 &plusmn; 759.5</strong></td>
                <td>321 B</td>
                <td><strong>Yes (NIST ML-KEM)</strong></td>
                <td><strong>Yes (Hash Chain)</strong></td>
            </tr>
        </tbody>
    </table>
</div>

<div class="figure-container full-width">
    <img src="{f7}" alt="Ablation Comparison" style="max-height: 270px;">
    <div class="caption"><strong>FIGURE 8.</strong> Multi-Metric Ablation Comparison Across All 6 Architectural Configurations (E7, Verified from Table VII Data).</div>
</div>

<p><em>Attribution Note</em>: The "Study-Defined Baseline (Adapted Saeed)" row represents our empirical benchmark implementation adapting the general concepts proposed by Saeed (2025) (fixed percentile threshold + static rule escalation + salted SHA-256) using a sample-level Dense Autoencoder on CICIoT2023 under identical test conditions, as Saeed (2025) used an LSTM Autoencoder with a 30s lookback on a private unreleased dataset and reported zero global test stream F1/Recall metrics. We do not claim this was Saeed's published score or that the original LSTM was exactly reproduced.</p>

<h2 class="section-heading">VI. Statistical Significance Analysis</h2>
<p class="no-indent">Table IX presents paired <i>t</i>-tests, exact 95% confidence intervals, Holm-Bonferroni adjusted <i>p</i>-values, and Cohen's <i>d</i> effect sizes across all 5 evaluation seeds:</p>

<div class="table-container">
    <div class="table-caption">TABLE IX. Hypothesis Testing and Effect Size (5 Seeds)</div>
    <table>
        <thead>
            <tr>
                <th>Hypothesis Comparison</th>
                <th>Mean Diff (95% CI)</th>
                <th>Paired <i>t</i></th>
                <th>Adjusted <i>p</i></th>
                <th>Cohen's <i>d</i></th>
                <th>Sig.</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Excluded EWMA vs Fixed 95th</td>
                <td>+0.0160 [0.0147, 0.0173]</td>
                <td><i>t</i>=33.81</td>
                <td><i>p</i>=2.74e-5</td>
                <td><i>d</i>=15.12</td>
                <td><strong>YES</strong></td>
            </tr>
            <tr>
                <td>Fixed 95th vs Fixed 99th</td>
                <td>+0.0195 [0.0183, 0.0207]</td>
                <td><i>t</i>=46.21</td>
                <td><i>p</i>=1.05e-5</td>
                <td><i>d</i>=20.67</td>
                <td><strong>YES</strong></td>
            </tr>
            <tr>
                <td>Dense-AE vs Isolation Forest</td>
                <td>+0.1089 [0.0978, 0.1201]</td>
                <td><i>t</i>=27.18</td>
                <td><i>p</i>=5.45e-5</td>
                <td><i>d</i>=12.16</td>
                <td><strong>YES</strong></td>
            </tr>
            <tr>
                <td>Proposed vs Baseline (Adapted)</td>
                <td>+0.0131 [0.0113, 0.0149]</td>
                <td><i>t</i>=19.89</td>
                <td><i>p</i>=1.51e-4</td>
                <td><i>d</i>=8.89</td>
                <td><strong>YES</strong></td>
            </tr>
            <tr>
                <td>Proposed vs Ablation (&minus;Adapt)</td>
                <td>+0.0131 [0.0113, 0.0149]</td>
                <td><i>t</i>=19.89</td>
                <td><i>p</i>=1.51e-4</td>
                <td><i>d</i>=8.89</td>
                <td><strong>YES</strong></td>
            </tr>
            <tr>
                <td>DQN vs Tabular Q Containment</td>
                <td>+10.81% [&minus;3.9%, 25.5%]</td>
                <td><i>t</i>=2.04</td>
                <td><i>p</i>=0.2219</td>
                <td><i>d</i>=0.91</td>
                <td>No</td>
            </tr>
            <tr>
                <td>Proposed vs Ablation (&minus;RL)</td>
                <td>+1.23% [&minus;2.28%, 4.75%]</td>
                <td><i>t</i>=0.97</td>
                <td><i>p</i>=0.3853</td>
                <td><i>d</i>=0.44</td>
                <td>No</td>
            </tr>
        </tbody>
    </table>
</div>

<h2 class="section-heading">VII. Limitations & Scope</h2>
<p class="no-indent">To uphold rigorous scientific integrity, we explicitly delimit the operational and empirical boundaries of this study:</p>
<p><strong>1. Pre-Shuffled Dataset Origin:</strong> Public CICIoT2023 records are pre-shuffled across captures. While our 5-seed duplicate-exclusion sensitivity test confirms that repeated feature vectors do not materially shift metrics (&Delta;F1 &le; 0.10%), device-level and capture-level independence cannot be proven without raw physical network PCAP captures.</p>
<p><strong>2. Local Storage Trust Boundary:</strong> The append-only hash chain guarantees sequence integrity against unprivileged processes (<i>A</i><sub>proc</sub>), but cannot prevent a root host adversary (<i>A</i><sub>root</sub>) from rewriting the local filesystem without external tip anchoring.</p>
<p><strong>3. Host Hardware Scope:</strong> Benchmarks were executed on an AMD64 host edge gateway (3.40 GHz). Highly constrained microcontrollers (&lt;100 MHz) require dedicated integer quantization and assembly optimizations.</p>
<p><strong>4. Synthetic Feature Scaling:</strong> Experiment E8 applied analytical scaling to benign numerical rate columns rather than live network packet arrivals.</p>

<h2 class="section-heading">VIII. Reproducibility & Open-Source Code</h2>
<p class="no-indent">The complete experimental code, deterministic partition generation scripts, trained model checkpoints, and raw verification manifests are publicly available under the open-source MIT License at:</p>
<p style="text-align: center; margin: 8px 0;">
    <strong><a href="https://github.com/Tanish-boop/AI-Driven-IoT-Cybersecurity-Framework-Research-">https://github.com/Tanish-boop/AI-Driven-IoT-Cybersecurity-Framework-Research-</a></strong>
</p>
<p>The complete 30-item regression unit test suite passes 100% in 26.91s (<code>results/final_submission_audit/test_report.xml</code>).</p>

<h2 class="section-heading">IX. Conclusion</h2>
<p class="no-indent">This study presented an empirical evaluation of adaptive anomaly thresholding, un-contaminated reinforcement learning mitigation, standardized post-quantum cryptography, and tamper-evident audit logging for IoT networks. Excluded EWMA prevents threshold inflation collapse (F1 = 0.9014), DQN achieves 71.26% attack containment with 0.63% false blocking, ML-KEM-768 provides sub-millisecond post-quantum transport security (0.2758 ms), and the full integrated framework achieves an end-to-end F1-Score of 0.8968 &plusmn; 0.0013 and 81.01% attack containment at 0.9626 ms edge latency.</p>

<h2 class="section-heading">References</h2>
<div class="references">
<ol>
    <li>M. M. Saeed, &ldquo;An AI-Driven Cybersecurity Framework for IoT: Integrating LSTM-Based Anomaly Detection, Reinforcement Learning, and Post-Quantum Encryption,&rdquo; <em>IEEE Access</em>, vol. 13, pp. 104027&ndash;104036, 2025.</li>
    <li>J. Neto et al., &ldquo;CICIoT2023: A Real-Time Dataset and Benchmark for Large-Scale Attacks in IoT Environment,&rdquo; <em>Sensors</em>, vol. 23, no. 13, p. 5941, 2023.</li>
    <li>A. Siffer, P.-A. Fouque, A. Termier, and C. Largouet, &ldquo;Anomaly Detection in Streams with Extreme Value Theory,&rdquo; in <em>Proc. ACM SIGKDD Int. Conf. Knowl. Discov. Data Min.</em>, 2017, pp. 1067&ndash;1075.</li>
    <li>J. Arjunan and A. S. Babu, &ldquo;Deep Learning Techniques for IoT Intrusion Detection: A Comprehensive Review,&rdquo; <em>IEEE Internet of Things Journal</em>, vol. 11, no. 4, pp. 5890&ndash;5912, 2024.</li>
    <li>National Institute of Standards and Technology, &ldquo;Module-Lattice-Based Key-Encapsulation Mechanism Standard,&rdquo; <em>NIST FIPS 203</em>, Aug. 2024.</li>
    <li>C. Alcaraz and S. Zeadally, &ldquo;Critical Infrastructure Protection in IoT: A Survey,&rdquo; <em>IEEE Internet of Things Journal</em>, vol. 10, no. 12, pp. 10450&ndash;10468, 2023.</li>
    <li>R. S. Sutton and A. G. Barto, <em>Reinforcement Learning: An Introduction</em>, 2nd ed. Cambridge, MA, USA: MIT Press, 2018.</li>
    <li>M. Roesch, &ldquo;Snort: Lightweight Intrusion Detection for Networks,&rdquo; in <em>Proc. 13th USENIX Conf. Syst. Adm.</em>, 1999, pp. 229&ndash;238.</li>
    <li>F. T. Liu, K. M. Ting, and Z.-H. Zhou, &ldquo;Isolation Forest,&rdquo; in <em>Proc. 8th IEEE Int. Conf. Data Min.</em>, 2008, pp. 413&ndash;422.</li>
    <li>T. Chen and C. Guestrin, &ldquo;XGBoost: A Scalable Tree Boosting System,&rdquo; in <em>Proc. 22nd ACM SIGKDD Int. Conf. Knowl. Discov. Data Min.</em>, 2016, pp. 785&ndash;794.</li>
</ol>
</div>

</div>
</body>
</html>
"""

    with open(html_out, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated formatted HTML manuscript: {html_out} ({len(html_content)} bytes)")

    # Call Headless Edge to print to PDF
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    edge_bin = None
    for p in edge_paths:
        if os.path.exists(p):
            edge_bin = p
            break

    if not edge_bin:
        print("ERROR: Microsoft Edge not found.")
        sys.exit(1)

    print(f"Compiling PDF via {edge_bin}...")
    cmd = [
        edge_bin,
        "--headless=new",
        "--disable-gpu",
        "--allow-file-access-from-files",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={output_pdf}",
        html_out
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if res.returncode == 0 and os.path.exists(output_pdf):
        size_kb = os.path.getsize(output_pdf) / 1024
        print(f"SUCCESS: Generated {output_pdf} ({size_kb:.2f} KB)")
        import shutil
        shutil.copy2(output_pdf, submission_pdf)
        print(f"Copied to {submission_pdf}")
    else:
        print(f"Compilation failed with exit code {res.returncode}: {res.stderr}")
        sys.exit(res.returncode)

if __name__ == "__main__":
    main()
