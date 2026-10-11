# Pre-Submission Blockers and Integrity Corrections

**Audit Date**: October 11, 2026  
**Auditor**: Independent Pre-Submission Research Audit  
**Purpose**: Rigorous identification and remediation of all empirical discrepancies, overclaimed language, attribution errors, and presentation blockers prior to journal submission.

---

## 1. Executive Summary & Audit Recommendation

### Verdict: **GO (ALL BLOCKERS RESOLVED)**
All 5 identified pre-submission blockers have been completely remediated across `paper/manuscript.md`, `paper/manuscript.tex`, `docs/FINAL_REPRODUCIBILITY_REPORT.md`, and the audit documentation. The repository, experiments, metrics, and manuscript are now fully aligned with academic integrity and empirical standards.

---

## 2. Identified Pre-Submission Blockers & Completed Remediations

### Blocker 1: Reconciling the E4 vs. E7 False Block Rate Discrepancy
- **Status**: **RESOLVED**
- **Action Taken**: Formally explained the difference between isolated policy capability (E4: $0.00\%$ false block rate on idealized test streams) and integrated pipeline behavior (E7: $7.39\%$ false block rate under upstream Excluded EWMA detector noise) in Section 3.3 and Section 3.6 of `paper/manuscript.md` and Section 3.2 of `paper/manuscript.tex`.

### Blocker 2: Attribution of Base Paper Baseline Metrics
- **Status**: **RESOLVED**
- **Action Taken**: Explicitly footnoted in Table 7 and described in Section 3.6 that the "Base Paper Architecture" row represents our standardized benchmark re-implementation of the architectural design proposed by Saeed (2025) on CICIoT2023 under identical test splits, as Saeed (2025) did not report global test F1/Recall metrics.

### Blocker 3: Removal of Unprofessional, Promotional, and Invented Metadata
- **Status**: **RESOLVED**
- **Action Taken**: Removed all promotional claims ("100% verified", "guaranteed superiority", "reviewer-proof") and replaced fictitious author titles with standard peer-review placeholders (`Anonymous Authors / Author One et al.`) in both `paper/manuscript.md` and `paper/manuscript.tex`.

### Blocker 4: Hardware Platform & Deployment Qualification
- **Status**: **RESOLVED**
- **Action Taken**: Formally qualified deployment hardware in Section 2.3 of `paper/manuscript.md` and Section 2-A of `paper/manuscript.tex`. Explicitly documented that benchmarks represent host-class IoT edge gateways (AMD64 / ARM64, e.g. Raspberry Pi 4/5, Intel Atom), and that deeply embedded microcontrollers (<100 MHz) require dedicated integer-only quantization and assembly optimizations.

### Blocker 5: Multi-Dimensional Ablation Orthogonality
- **Status**: **RESOLVED**
- **Action Taken**: Added explicit discussions in Section 3.6 of `paper/manuscript.md` and Section 3.1 of `paper/manuscript.tex` explaining why removing PQC or Blockchain logging leaves detection F1 exactly invariant ($0.8968$): they execute downstream of anomaly inference and secure payload transit and audit sequence immutability without altering upstream reconstruction errors.

---

## 3. Pre-Submission Remediation Checklist

| Blocker ID | Description | Status | Verification Target |
| :---: | :--- | :---: | :--- |
| **B1** | Reconcile E4 vs E7 False Block Rate in text | **RESOLVED** | `paper/manuscript.md`, `paper/manuscript.tex` |
| **B2** | Clarify Base Paper Architecture attribution | **RESOLVED** | Table 7 caption & Section 3.6 text |
| **B3** | Remove promotional language & fake author credentials | **RESOLVED** | Title/Author block & Abstract in `manuscript.tex` |
| **B4** | Qualify host CPU vs embedded microcontroller deployment | **RESOLVED** | Section 2 & Discussion in `manuscript.tex` |
| **B5** | Explain multi-dimensional ablation orthogonality | **RESOLVED** | Section 3.6 in `manuscript.md` & `manuscript.tex` |

**Final Recommendation**: **GO FOR PUBLICATION / PEER REVIEW SUBMISSION**.
