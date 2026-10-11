# Final Journal Submission Decision & Evidence Validation Audit

**Audit Date**: October 12, 2026  
**Auditor**: Independent Pre-Submission Research Auditor  
**Target Repository**: `C:\Users\hp\OneDrive\Desktop\Research Experiments`  
**GitHub Repository**: `https://github.com/Tanish-boop/AI-Driven-IoT-Cybersecurity-Framework-Research-`  
**Scope**: Experiments E1–E8, Figures 1–8, Tables I–IX, Data Provenance, Deduplication Sensitivity, Manuscript Sources, and Compiled PDF Artifacts.

---

## 1. Issue Resolution and Audit Verification Matrix

| Audit Item | Prior Status | Audit Finding | Corrective Action Implemented | Final Verification |
| :--- | :--- | :--- | :--- | :---: |
| **1. Publisher Metadata** | Misleading banners present | Previous PDF included fake IEEE Access special section banner, fake DOI (`10.1109/ACCESS.2026.3526148`), and "Accepted for Publication" statements. | Removed all unverified publisher metadata, cleared DOI, labeled document as Preprint Working Draft for Peer Review. | **PASSED** |
| **2. Author Credentials** | Generic placeholders | Manuscript and citation files contained `Author One`, `Author Two`, `Author Three`. | Updated manuscript, `CITATION.cff`, and PDF to verified researcher metadata: Tanish Thakare, Independent Researcher. | **PASSED** |
| **3. Figure 2 (Threshold Strategies)** | Discrepant models plotted | Legacy plot contained LSTM-AE and GRU-AE models not evaluated in the audited 5-seed benchmark. | Regenerated `figure1_threshold_comparison.png` strictly plotting the 5-seed Dense-AE models from `full_benchmark_results.csv`. | **PASSED** |
| **4. Figure 3 (E8 Rate Scaling)** | Overclaimed conditions | Legend previously included Excluded EWMA under rate scaling, which was never evaluated in E8. | Regenerated `figure2_rate_stress_test.png` exclusively plotting Dense-AE Fixed 95th across 1.0×, 1.5×, and 2.0× scaling. | **PASSED** |
| **5. Figure 4 & Table IV (Attack Recall)** | Unsupported text claims | Manuscript cited Reconnaissance (73.12%) and Web (58.41%) recall unbacked by CSV evidence. | Recomputed exact per-class recall from test set inferences: DDoS: 100%, DoS: 100%, Mirai: 100%, BruteForce: 42.80% vs 55.54%, Recon: 38.18% vs 49.19%, Spoofing: 23.38% vs 39.15%, Web: 20.42% vs 37.88%. Saved to `per_attack_class_breakdown.csv`. | **PASSED** |
| **6. Figure 8 & Table VIII (E7 Latency)** | Severe numerical mismatch | Table VIII reported 0.3781 ms while Figure 8 plotted 0.81–1.21 ms from conflicting runs. | Harmonized Table VIII and Figure 8 to the official 5-seed summary `e7_ablation_summary.csv`: Baseline: 0.81 ms, -Adaptive: 0.86 ms, -RL: 0.97 ms, -PQC: 0.91 ms, -Hash Log: 1.21 ms, Full: 0.96 ms. | **PASSED** |
| **7. E4 Mitigation Numbers** | Preliminary numbers | Manuscript text cited preliminary DQN reward (27,092) and latency (0.4412 ms). | Harmonized to official 5-seed summary `e4_policy_summary_corrected.csv`: Reward $28,513.20 \pm 122.92$, Containment $71.26\% \pm 0.09\%$, False Block $0.63\% \pm 0.46\%$, Latency $0.1160 \pm 0.0052$ ms. | **PASSED** |
| **8. E5 & E6 Cryptographic Timings** | Preliminary exploratory run | Tables VI & VII previously cited unanchored preliminary numbers. | Synchronized with official summaries `e5_summary.csv` (ML-KEM-768 total KEM: 0.2758 ms, first msg: 0.2905 ms) and `e6_summary.csv` (Hash Chain append: 0.0605 ms, verify: 0.0328 ms). | **PASSED** |
| **9. Scientific Terminology** | Promotional / Unbounded | Phrase "leak-free" and "proving mathematical invariance" masked underlying nuances. | Reworded to "strictly partitioned across isolated training, validation, supervised, and held-out evaluation splits", "tamper-evident append-only hash-chain audit log", and explicit disclosures on synthetic feature scaling. | **PASSED** |
| **10. Visual PDF Verification** | Unverified locally | Windows host lacked native `pdflatex`. | Compiled 6-page double-column PDF via headless Microsoft Edge; visually audited all pages with zero overflows or broken figures. | **PASSED** |

---

## 2. Final Submission Verdict

### Verdict: **CONDITIONAL GO**

**Verdict Justification**:
1. **Empirical Evidence Integrity**: All experimental data in Tables I–IX and Figures 1–8 are 100% synchronized with underlying CSV summaries and scripts. Zero numerical discrepancies remain.
2. **Methodological Rigor**: Partition isolation, deduplication sensitivity analysis (shift $\le -0.10\%$), and hardware boundaries are explicitly disclosed.
3. **No External Premature Submission**: The paper is ready for submission to *IEEE Access*, but must not be submitted externally until the author completes the final non-technical check below.

### Mandatory Pre-Submission Checklist for the Author:
1. **Co-Authors and Institutional Affiliation**: Confirm whether any co-authors, department affiliations, or funding grant numbers should be added alongside Tanish Thakare.
2. **Cover Letter**: Prepare a standard journal cover letter highlighting the leak-resistant protocol, 5-seed deduplication sensitivity check, and NIST FIPS 203 standardization.
3. **Journal Selection**: Confirm *IEEE Access* as the primary target journal.
