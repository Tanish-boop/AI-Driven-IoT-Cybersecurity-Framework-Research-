"""
Integrated Framework Package (Experiment E7)
Provides end-to-end integration and ablation modeling combining:
  - Dense Autoencoder Anomaly Detection
  - Adaptive vs Fixed Thresholding (E1, E2)
  - Defensive Reinforcement Learning Policies (E4)
  - Post-Quantum Cryptographic Key Encapsulation (E5)
  - Authenticated Integrity & Blockchain Audit Logging (E6)
"""

from .integrated_framework import IntegratedPipeline, FrameworkConfig

__all__ = ['IntegratedPipeline', 'FrameworkConfig']
