# Original Data and Code Investigation

**Target Paper**: "An AI-Driven Cybersecurity Framework for IoT: Integrating LSTM-Based Anomaly Detection, Reinforcement Learning, and Post-Quantum Encryption" (IEEE Access, 2025, DOI: 10.1109/ACCESS.2025.3576506)  
**Investigation Date**: October 9, 2026  
**Investigator**: Senior Research Engineer  

---

## 1. Executive Summary

A comprehensive investigation was conducted across academic indexers, official publisher metadata, public code repositories, and author profiles to determine whether the original dataset, source code, data generation scripts, or experimental configuration files for the target paper are publicly available. 

**Result**: **NO public code repository, dataset artifact, or supplementary code package exists** for this publication. The dataset described in the paper is synthetic/simulated, and the source code has not been released by the author or institution.

---

## 2. Search Strategy & Official Links Inspected

### A. Publisher & DOI Records
* **IEEE Xplore Article Page**: [https://ieeexplore.ieee.org/document/10547055](https://ieeexplore.ieee.org/document/10547055)
  - *Inspection*: Evaluated PDF text, Media tab, and Supplementary Materials tab. No supplementary source code zip files, dataset CSV files, or GitHub repository links are attached.
* **DOI Record**: [https://doi.org/10.1109/ACCESS.2025.3576506](https://doi.org/10.1109/ACCESS.2025.3576506)
  - *Inspection*: Redirects to IEEE Xplore. No external data DOI or Zenodo repository linked.

### B. Author Institutional & Academic Profiles
* **Author Name**: Mozamel M. Saeed
* **Affiliation**: Department of Computer Science, Prince Sattam Bin Abdulaziz University (PSAU), Al Kharj, Saudi Arabia
* **Author Email**: `m.musa@psau.edu.sa`
* **ORCID Profile**: [https://orcid.org/0000-0002-3114-1188](https://orcid.org/0000-0002-3114-1188)
  - *Inspection*: Lists publications including the IEEE Access 2025 paper. No repository links provided.
* **ResearchGate Profile**: [https://www.researchgate.net/profile/Mozamel-Saeed](https://www.researchgate.net/profile/Mozamel-Saeed)
  - *Inspection*: Paper abstract and PDF uploaded. No linked GitHub repository or attached data files.

### C. Public Repository Searches (GitHub, GitLab, Kaggle, HuggingFace, Zenodo)
* **Search Queries Executed**:
  1. `"Mozamel M. Saeed" github`
  2. `"An AI-Driven Cybersecurity Framework for IoT" dataset code`
  3. `10.1109/ACCESS.2025.3576506 github`
  4. `site:github.com "Mozamel" "IEEE Access" "LSTM" "LWE"`
  5. `site:zenodo.org "An AI-Driven Cybersecurity Framework for IoT"`
* **Results**: Zero matching code repositories or dataset packages found.

---

## 3. Search Results Verification Table

| Resource Target | Inspected URLs / Query | Found? | Verification Status & Notes |
| :--- | :--- | :--- | :--- |
| **Source Code Repository** | GitHub / IEEE Xplore | **NO** | No repository created or linked in paper. |
| **Simulated IoT Dataset** | IEEE Xplore / Zenodo / Kaggle | **NO** | Private synthetic dataset (~150k events) unreleased. |
| **Data Generation Scripts**| IEEE Xplore | **NO** | Traffic simulation script not provided. |
| **Model Configs / Weights**| IEEE Xplore | **NO** | No saved model PyTorch/TensorFlow checkpoints. |
| **Q-Learning MDP Specs** | Base paper PDF | **NO** | Only static $3 \times 2$ Q-table presented. |
| **PQC Implementation Code**| Base paper PDF | **NO** | Only theoretical LWE formula ($y = Ax + e \bmod q$). |

---

## 4. Professional Draft Email for Author Inquiry

*Note: As per project guidelines, this email draft is prepared for documentation purposes and will **NOT** be sent without the researcher's explicit written permission.*

```text
Subject: Data and Implementation Clarification Request for IEEE Access Article (DOI: 10.1109/ACCESS.2025.3576506)

Dear Dr. Mozamel M. Saeed,

I hope this message finds you well. 

I am currently conducting an academic research study on AI-driven IoT cybersecurity, focusing on anomaly detection, reinforcement learning, and post-quantum encryption. We have read your paper, "An AI-Driven Cybersecurity Framework for IoT: Integrating LSTM-Based Anomaly Detection, Reinforcement Learning, and Post-Quantum Encryption" (IEEE Access, 2025, DOI: 10.1109/ACCESS.2025.3576506), with great interest.

To ensure our baseline comparisons are scientifically accurate and fully reproducible, we are attempting to align our experimental setup with your original study. We would be extremely grateful if you could share any available details or artifacts regarding:

1. The simulated network traffic dataset (or the data-generation scripts used to create the 150,000 network events).
2. The exact preprocessing, feature schema, lookback window discretization, and train/validation/test splits.
3. The source code or hyperparameter configurations for the LSTM model architecture.
4. The exact Markov Decision Process (MDP) parameters, state-transition dynamics, and reward formulation used for the Q-learning model.
5. The specific lattice parameter set (or library) used for the LWE post-quantum encryption evaluation.

Any source code, scripts, or documentation you could share would be immensely helpful for our benchmarking effort. Full credit and formal citations will be given in our paper.

Thank you very much for your time and contribution to IoT cybersecurity research.

Sincerely,

[Researcher Name]  
Department of Computer Engineering  
[University / Institution]  
```

---

## 5. Methodological Strategy in the Absence of Original Code & Data

Since the original dataset and code are unreleased:
1. We will **not** attempt to fabricate a synthetic dataset and claim it is the original paper's dataset.
2. We will use established, real-world public IoT cybersecurity datasets—specifically **CICIoT2023** (and Edge-IIoTset where applicable)—as transparent, open-source benchmarks.
3. We will explicitly state in our research paper that the base paper's data and source code are unreleased, justifying our use of standard public benchmark datasets for reproducible evaluation.
