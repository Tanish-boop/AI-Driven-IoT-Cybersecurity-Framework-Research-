# Final Remaining Actions Prior to Journal Submission

**Audit Status**: CONDITIONAL GO  
**Date**: October 11, 2026  
**Repository**: `C:\Users\hp\OneDrive\Desktop\Research Experiments`  

This document lists the strictly procedural and external actions required before clicking "Submit" on the journal submission portal. All internal scientific, methodological, and data-leakage blockers have been resolved.

---

## 1. Action Inventory

### Action 1: Replace Author & Affiliation Placeholders in LaTeX Manuscript
- **Target File**: [`paper/manuscript.tex`](file:///C:/Users/hp/OneDrive/Desktop/Research%20Experiments/paper/manuscript.tex#L14-L18)
- **Current State**: Lines 14–18 use placeholder identities (`Author~One`, `Author~Two`, `Author~Three`, `authors@institution.edu`).
- **Unresolved Issue**: Actual author names, institutional departments, university affiliations, and funding grant numbers must be inserted unless submitting to a double-blind peer-review track.
- **Exact Evidence Needed to Close**:
  1. Replace `Author~One`, `Author~Two`, etc., with verified researcher names.
  2. Update the `\thanks{...}` block with actual institutional affiliations and funding numbers.

---

### Action 2: Compile and Visually Inspect Rendered LaTeX PDF
- **Target File**: [`paper/manuscript.tex`](file:///C:/Users/hp/OneDrive/Desktop/Research%20Experiments/paper/manuscript.tex)
- **Current State**: LaTeX source file has been updated with complete methodologies, tables, and references. However, the host Windows environment does not have `pdflatex` or `latexmk` installed in the system PATH.
- **Unresolved Issue**: Two-column IEEE format rendering, table column balancing (especially wide `table*` environments for Table II and Table VII), and line breaks have not been visually checked.
- **Exact Evidence Needed to Close**:
  1. Upload `paper/manuscript.tex` and any referenced style files to [Overleaf](https://www.overleaf.com) or compile locally via TeX Live / MiKTeX:
     ```bash
     pdflatex manuscript.tex
     bibtex manuscript
     pdflatex manuscript.tex
     pdflatex manuscript.tex
     ```
  2. Visually confirm:
     - No text overruns into page margins.
     - Table I–VII column alignments render cleanly.
     - Mathematical expressions ($\tau_{95}$, $\mathcal{O}(1)$, $\mathcal{A}_{\text{proc}}$) render correctly.
     - Bibliography entries [1]–[5] link and format properly.

---

### Action 3: Review Cover Letter & Highlight Methodological Corrections
- **Target Venue**: *IEEE Access* (Primary) or *Sensors* (Alternative)
- **Current State**: Complete empirical evidence base is frozen and reproduced in `results/audit_rerun_20261011/audit_reproduction_manifest.json`.
- **Unresolved Issue**: Journal submission requires a cover letter to the Editor-in-Chief.
- **Exact Evidence Needed to Close**:
  Draft a cover letter summarizing the key methodological distinctions:
  1. Direct benchmark and correction of the architecture proposed by Saeed (2025) on CICIoT2023.
  2. Proof of zero data leakage: pure benign feature scaler calibration (`n_samples_seen_ = 100000`), sample-level flow evaluation ($L=1$), and empirical re-evaluation on a deduplicated clean test set ($N=98,543$) confirming $\Delta \text{F1} \le -0.0010$.
  3. Real-world threshold adaptation: Excluded EWMA prevents threshold inflation collapse.
  4. NIST FIPS 203 ML-KEM-768 post-quantum key encapsulation with AES-256-GCM AEAD and tamper-evident hash-chain audit logging.

---

## 2. Summary Status

| Action Item | Responsible Party | Complexity | Status |
| :--- | :---: | :---: | :---: |
| 1. Author Metadata | Researcher | 5 minutes | **Pending User Input** |
| 2. Visual PDF Inspection | Researcher | 10 minutes | **Pending Compilation** |
| 3. Cover Letter Preparation | Researcher | 15 minutes | **Pending Final Submission** |

*All scientific, statistical, and empirical experiments (E1–E8) are complete, passing, and fully reproduced.*
