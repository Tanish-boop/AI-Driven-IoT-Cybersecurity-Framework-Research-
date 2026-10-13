# MANUSCRIPT INCONSISTENCY & AUDIT AUDIT LOG

**Repository**: `C:\Users\hp\OneDrive\Desktop\Research Experiments`  
**Target Submission**: IEEE Access  
**Date**: October 2026  
**Status**: Fully Synchronized with Verified Experimental Sources  

---

## 1. Overview

This document provides a comprehensive audit trail of all scientific, methodological, numerical, and editorial inconsistencies identified across earlier drafts, audit reports, and the final verified manuscript. Every inconsistency is documented with its original formulation, discovered discrepancy, empirical evidence, and final corrected implementation.

---

## 2. Itemized Inconsistency Log

### Inconsistency #1: Baseline Classification Performance of Saeed (2025)
- **Previous Statement**: Earlier drafts cited Saeed (2025) (*IEEE Access*) as reporting an F1-score of ~88% or ~91% for LSTM-based IoT anomaly detection.
- **Discovered Discrepancy**: A forensic line-by-line inspection of the text and tables of Saeed (2025) revealed that the base paper reported **zero global classification metrics** (no Precision, Recall, F1-Score, False Positive Rate, or Confusion Matrix). The only anomaly detection evidence in Saeed (2025) was Table 1, showing a single anomalous timestamp (810: actual 1.25, predicted 0.72) and an illustrative line plot (Figure 2).
- **Corrected Statement**: The manuscript now explicitly clarifies:
  > *"Because Saeed (2025) evaluated on a private simulated IoT data stream and reported only a single-timestamp qualitative deviation (Table 1: actual 1.25 vs. predicted 0.72) without global classification metrics (Precision, Recall, F1, FPR), we established an adapted baseline by implementing Saeed's exact 2-layer LSTM architecture with static 95th percentile MSE thresholding on the standardized CICIoT2023 benchmark."*
- **Evidence / Source**: `scratch/base_paper_text.txt` (pp. 4–5, Table 1); `docs/BASELINE_REPRODUCTION_PLAN.md`.

---

### Inconsistency #2: Fair Model Selection: Dense-AE vs. LSTM-AE (Saeed-Adapted)
- **Previous Statement**: Earlier audits noted that Dense-AE was chosen as the primary detector without a controlled, head-to-head empirical comparison against LSTM-AE on identical partitions, or that LSTM-AE was reported with an unexplained 100% False Positive Rate.
- **Discovered Discrepancy**: 
  1. In `scripts/run_baselines.py`, LSTM-AE was trained using a sliding window of length 10 across pre-shuffled tabular NetFlow rows. Because attacks represent ~85% of CICIoT2023, the probability of 10 consecutive rows being benign was $(0.149)^{10} \approx 5.6 \times 10^{-9}$. In 100,000 test rows, exactly **0 pure benign sequences** existed. Every sequence contained attack flows or cross-session jumps, causing 100% of test sequences to exceed the validation threshold ($\text{FPR} = 100\%$).
  2. When evaluated fairly on individual NetFlow feature vectors ($L=1$), the Saeed-adapted LSTM-AE achieves $87.38\% \pm 0.18\%$ F1 (Fixed 95th) and $89.37\% \pm 0.22\%$ F1 (Excluded EWMA). Dense-AE achieves $88.54\% \pm 0.13\%$ F1 (Fixed 95th) and $90.14\% \pm 0.18\%$ F1 (Excluded EWMA).
  3. However, Dense-AE requires only **10,775 parameters** vs **129,255 parameters** for LSTM-AE ($12.0\times$ smaller) and runs in **$1.50\,\mu\text{s}$ per sample** vs **$5.77\,\mu\text{s}$ per sample** ($3.85\times$ faster).
- **Corrected Statement**: The manuscript now documents both: (a) explains why naïve sequence sliding windows collapse on pre-shuffled tabular NetFlow data, and (b) presents the 5-seed head-to-head comparison demonstrating that Dense-AE achieves comparable/superior F1 with 12x lower memory and 3.85x lower inference latency.
- **Evidence / Source**: `docs/FAIR_COMPARISON_RESULTS.csv`, `scripts/run_fair_head_to_head_comparison.py`.

---

### Inconsistency #3: Framing of Excluded EWMA Adaptive Thresholding
- **Previous Statement**: Earlier text described Excluded EWMA as an unmitigated improvement over fixed thresholding, claiming it was "leak-free and universally superior."
- **Discovered Discrepancy**: While Excluded EWMA successfully prevents threshold inflation collapse during sustained attack floods ($F1 = 90.14\%$ vs UnGuarded EWMA's $0.03\%$), it increases the False Positive Rate from $4.93\%$ (Fixed 95th) to $13.60\%$ (Excluded EWMA).
- **Corrected Statement**: The manuscript frames this as an honest operational trade-off:
  > *"Excluded EWMA provides critical resilience against adversarial threshold poisoning and sustained flood attacks (increasing attack recall from 80.13% to 84.01%), but incurs an operational trade-off of +8.67% additional false alarms per 10,000 benign records. In high-security environments where attack containment is paramount, this trade-off is advantageous; in operational environments where operator alert fatigue dominates, guarded or fixed thresholding remains viable."*
- **Evidence / Source**: `results/metrics/full_benchmark_summary.csv`, Table I of manuscript.

---

### Inconsistency #4: Nature of E3 Synthetic Rate-Scaling Stress Test
- **Previous Statement**: Earlier versions described E3 as a "dynamic traffic burst test" or "arrival rate scaling experiment," implying live packet queue simulation.
- **Discovered Discrepancy**: The actual implementation in `scripts/run_full_benchmark.py` applies synthetic multiplicative scaling factors ($1.5\times$ and $2.0\times$) to rate- and volume-related features (`Rate`, `Tot size`, `Variance`) of benign test samples, rather than altering live packet inter-arrival timestamps or router queue depths.
- **Corrected Statement**: The methodology and evaluation sections explicitly define E3 as a **"feature-level synthetic rate scaling stress test"** and document the limitation that physical packet queue dynamics require hardware testbed validation.
- **Evidence / Source**: `scripts/run_full_benchmark.py` (lines 185–205), `docs/FINAL_LIMITATIONS_AND_THREATS.md`.

---

### Inconsistency #5: Defensive Mitigation RL Split Isolation (E4)
- **Previous Statement**: Historical E4 scripts shared index mappings with unsupervised training splits, creating potential reward-signal leakage.
- **Discovered Discrepancy**: An audit revealed that evaluating RL agents on samples overlapping with unsupervised training could artificially inflate policy evaluation metrics.
- **Corrected Statement**: E4 was completely re-architected with strict split isolation: $X_{\text{sup}}$ (40,000 records) is strictly allocated for policy training and Q-network convergence, while $X_{\text{test}}$ (100,000 records) is strictly held out for final evaluation.
- **Evidence / Source**: `scripts/run_e4_defense_experiment.py`, `tests/test_e4_uncontaminated.py`, `results/metrics/e4_policy_results_corrected.csv`.

---

### Inconsistency #6: Cryptographic and Hash Chain Claims (E5 & E6)
- **Previous Statement**: Manuscripts used phrases like "proving mathematical invariance," "immutable blockchain," and "absolute quantum immunity."
- **Discovered Discrepancy**:
  1. E5 implements NIST FIPS 203 ML-KEM (Kyber) key encapsulation mechanism, which defends against "Harvest Now, Decrypt Later" (HNDL) attacks under the Learning With Errors hardness assumption. It does not provide digital signatures (ML-DSA) or data confidentiality on its own.
  2. E6 implements a centralized append-only SHA-256 hash chain with cryptographic parent hashing. It provides tamper-evident forward integrity and non-repudiation, but lacks Byzantine Fault Tolerant distributed consensus. A compromised centralized server could withhold or truncate log files.
- **Corrected Statement**: Wording replaced with scientifically rigorous, bounded descriptions: "NIST FIPS 203 ML-KEM post-quantum key establishment" and "tamper-evident append-only hash chain audit log."
- **Evidence / Source**: `docs/SECURITY_THREAT_MODEL.md`, `tests/test_e5_crypto.py`, `tests/test_e6_integrity.py`.

---

### Inconsistency #7: Journal Metadata and Author Attribution
- **Previous Statement**: The compiled PDF header contained an unverified IEEE Access special-section banner ("SPECIAL SECTION ON ADVANCES IN MACHINE LEARNING"), an invented DOI ("10.1109/ACCESS.2026.3576506"), and an "Accepted for Publication" notice.
- **Discovered Discrepancy**: The manuscript is a pre-submission research paper and has not yet been accepted or assigned a publisher DOI. Publisher-only banners must not be used on pre-submission drafts.
- **Corrected Statement**: Header cleaned to standard IEEE Access Preprint Draft format (`PREPRINT - UNDER PEER REVIEW`), real author metadata maintained (Tanish Thakare), and verified public GitHub repository URL synchronized across LaTeX source, markdown, and citation files.
- **Evidence / Source**: `paper/IEEE_Access_Final_Manuscript.pdf`, `paper/ieee_access_manuscript.tex`, `CITATION.cff`.

---

## 3. Summary of Synchronization Status

| Document / Component | Synchronization Status | Verification Method |
| :--- | :--- | :--- |
| `paper/ieee_access_manuscript.tex` | Fully Synchronized | Checked against raw CSVs & compiled PDF |
| `paper/IEEE_Access_Final_Manuscript.pdf` | Fully Synchronized | 6 pages, 8 figures, 8 tables, clean header |
| `docs/FIGURE_TO_SOURCE_DATA_MAP.md` | Fully Synchronized | Every figure/table mapped to raw CSV path |
| `docs/FINAL_CLAIM_EVIDENCE_MATRIX.md` | Fully Synchronized | All 10 core claims verified with statistical bounds |
| `docs/FINAL_LIMITATIONS_AND_THREATS.md` | Fully Synchronized | All 7 architectural limitations fully documented |
| `docs/EXPERIMENT_STATUS_MATRIX.csv` | Fully Synchronized | E1–E8 tracked with exact metrics |
| `docs/BASELINE_REPRODUCTION_PLAN.md` | Fully Synchronized | Saeed (2025) audit & adaptation documented |
| `docs/FAIR_COMPARISON_RESULTS.csv` | Fully Synchronized | Head-to-head 5-seed metrics recorded |
