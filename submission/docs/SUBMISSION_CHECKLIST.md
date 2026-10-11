# Pre-Submission Readiness Checklist for IEEE Access

**Manuscript Title**: *An AI-Driven Adaptive Cybersecurity Framework for IoT: Anomaly Detection, Dynamic Thresholding, Un-Contaminated Reinforcement Learning Defense, Post-Quantum Cryptography, and Tamper-Evident Audit Logging*  
**Target Journal**: *IEEE Access*  
**Date Sealed**: October 12, 2026  

---

## 1. IEEE Access Formatting & Compliance Checklist

- [x] **Official Document Class**: `ieeeaccess.cls` used with standard double-column, single-spaced formatting.
- [x] **Header Assets Included**: `Logo.png`, `notaglineLogo.png`, and `bullet.png` bundled in `paper/`.
- [x] **Section Structure**: Introduction, Related Work, Research Gap & Contributions, System Architecture & Threat Model, Dataset & Methodology, Proposed Methods, Experimental Results (E1–E6), Ablation & Stress Testing (E7–E8), Statistical Analysis, Discussion, Limitations, Reproducibility Statement, Conclusion.
- [x] **Keywords**: 8 IEEE-compliant index terms specified (within the 3–10 requirement).
- [x] **Bibliographic Standards**: IEEE-style numbered citations using verified `references.bib` with complete author names, journal venues, years, and DOIs.
- [x] **AI-Use Disclosure**: Mandatory IEEE policy disclosure included in Acknowledgments section.
- [x] **Author Biographies**: Biography blocks included at the end of the manuscript.
- [ ] **ACTION REQUIRED (Author Metadata)**: Replace `Author One`, `Author Two`, `Author Three` placeholders and placeholder email addresses in `submission/paper/ieee_access_manuscript.tex` with your real names and affiliations.
- [ ] **ACTION REQUIRED (Visual PDF Layout Inspection)**: Compile `submission/paper/ieee_access_manuscript.tex` on Overleaf or local TeX Live to visually confirm margins, column balance for wide tables (Tables I, VI, VII, IX), and typography.

---

## 2. Scientific & Empirical Integrity Checklist

- [x] **Experiment Inventory Sealed**: Strictly eight experiments (E1–E8). No fictitious E9.
- [x] **Zero Data-Leakage Protocol**: Feature normalizer strictly fitted on benign training flows ($X_{\text{train}}$, $n=100,000$). No test samples exposed during training.
- [x] **Sample-Level Granularity ($L=1$)**: Temporal window sliding ($L > 1$) eliminated to prevent boundary leakage across pre-shuffled flow records.
- [x] **Deduplication Sensitivity Validated**: Evaluated on clean test set ($N=98,543$, all 1,457 duplicates purged); F1 shifts by only $-0.0009$ ($-0.10\%$), proving natural packet header repetitions do not bias results.
- [x] **Accurate Attribution**: Baseline labeled as our study-defined adaptation of Saeed (2025) on CICIoT2023. No claims that Saeed published 0.8837.
- [x] **Bounded Cryptographic Claims**: Described as a ``tamper-evident append-only hash-chain audit log'' with local root storage rewrite boundary disclosed. No claims of distributed blockchain immutability.
- [x] **Bounded Hardware Scope**: Timings explicitly stated as host AMD64 CPU measurements (3.40 GHz). Microcontrollers disclosed as modeled targets requiring fixed-point quantization.
- [x] **Statistical Significance Disclosed**: Paired $t$-tests, exact 95% CIs, Holm-Bonferroni corrections, and Cohen's $d$ effect sizes reported. Non-significant mitigation differences honestly stated under $N=5$.
- [x] **Automated Regression Test Suite**: 30 / 30 tests passing in 50.02s (`results/final_submission_audit/test_report.xml`).

---

## 3. Submission Bundle Contents (`submission/`)

1. `submission/paper/ieee_access_manuscript.tex`: Complete IEEE Access LaTeX source.
2. `submission/paper/references.bib`: Complete verified BibTeX database.
3. `submission/paper/ieeeaccess.cls` & `IEEEtran.cls`: Official template classes.
4. `submission/paper/figures/`: Figures 0 through 7 in high-resolution 300 DPI PNG format.
5. `submission/README.md`: Complete reproduction instructions.
6. `submission/CITATION.cff`: Citation metadata.
7. `submission/requirements.txt`: Python package dependencies.
8. `submission/LICENSE`: MIT Open Source License.
9. `submission/docs/EXPERIMENT_TO_ARTIFACT_MAP.md`: Metric-to-file traceability matrix.
10. `submission/docs/EVIDENCE_MANIFEST.json`: Machine-readable SHA-256 artifact manifest.
