"""
Contextual Risk Prioritization Engine:
Ranks correlated incidents by operational severity, asset impact, corroboration,
and evidence strength:
    R_i = w_1 * D_i + w_2 * I_i + w_3 * C_i + w_4 * E_i

Where:
    - D_i in [0, 1]: Detection confidence (aggregate hybrid model score)
    - I_i in [0, 1]: Asset and service criticality / impact
    - C_i in [0, 1]: Multi-event corroboration across time and indicators
    - E_i in [0, 1]: Evidence consistency strength
"""

import math
import numpy as np
from typing import List, Dict, Any, Optional
from src.correlation.incident_correlator import CorrelatedIncident


# Asset / Service Criticality Ratings
SERVICE_CRITICALITY = {
    'DNS': 0.95,        # Core resolution infrastructure
    'HTTPS': 0.90,      # Secure web / API endpoints
    'SSH': 0.85,        # Remote administrative access
    'Telnet': 0.90,     # Insecure legacy management port (critical vulnerability)
    'HTTP': 0.75,       # Web application traffic
    'TCP': 0.60,        # Standard transport
    'UDP': 0.55,        # Datagram transport
    'ICMP': 0.40,       # Ping / diagnostics
    'ARP': 0.50,        # Local layer-2 resolution
    'Generic': 0.30     # Secondary traffic
}

# Attack Class Impact Factor
ATTACK_SEVERITY_IMPACT = {
    'DDoS': 0.95,
    'DoS': 0.90,
    'Mirai': 0.95,
    'Web-based': 0.85,
    'BruteForce': 0.70,
    'Spoofing': 0.65,
    'Recon': 0.40,
    'Benign': 0.10
}


class ContextualRiskScorer:
    """
    Contextual Risk Assessment and Incident Prioritization Engine.
    """
    def __init__(
        self,
        w_confidence: float = 0.35,
        w_impact: float = 0.25,
        w_corroboration: float = 0.25,
        w_evidence: float = 0.15,
        corroboration_lambda: float = 0.20
    ):
        # Normalize weights to sum to 1.0
        total_w = w_confidence + w_impact + w_corroboration + w_evidence
        self.w_conf = w_confidence / total_w
        self.w_imp = w_impact / total_w
        self.w_corr = w_corroboration / total_w
        self.w_ev = w_evidence / total_w
        self.corr_lambda = float(corroboration_lambda)

    def compute_risk(self, incident: CorrelatedIncident) -> float:
        """
        Computes the contextual risk score R_i in [0, 1] for a given incident.
        """
        if not incident.events:
            return 0.0

        # 1. Detection Confidence (D_i): combination of mean and peak score
        # 70% mean score + 30% peak score
        d_conf = float(0.70 * incident.mean_score + 0.30 * incident.max_score)
        d_conf = float(np.clip(d_conf, 0.0, 1.0))

        # 2. Asset & Service Impact (I_i)
        # Service criticality: maximum criticality among affected services
        svc_criticalities = [
            SERVICE_CRITICALITY.get(s, 0.40) for s in incident.affected_services
        ] if incident.affected_services else [0.40]
        max_svc_crit = max(svc_criticalities)

        # Attack severity factor
        atk_impact = ATTACK_SEVERITY_IMPACT.get(incident.primary_attack_class, 0.50)
        
        # Combined impact
        i_impact = float(0.50 * max_svc_crit + 0.50 * atk_impact)

        # 3. Multi-Event Corroboration (C_i)
        # Diminishing returns formula: 1 - exp(-lambda * N)
        n_events = incident.event_count
        c_corr = 1.0 - math.exp(-self.corr_lambda * n_events)
        
        # Corroboration bonus for multi-stage attack progression (e.g. Recon -> Exploitation)
        if incident.is_multistage:
            c_corr = min(1.0, c_corr + 0.15)

        # 4. Evidence Strength (E_i)
        # Based on event density and consistency
        # Duration density: events per second (clamped)
        duration = max(incident.duration, 0.1)
        rate = n_events / duration
        e_strength = min(1.0, 0.30 + 0.70 * (1.0 - math.exp(-0.1 * rate)))

        # Composite Risk Formula
        risk_score = (
            self.w_conf * d_conf +
            self.w_imp * i_impact +
            self.w_corr * c_corr +
            self.w_ev * e_strength
        )
        return float(np.clip(risk_score, 0.0, 1.0))

    def prioritize_incidents(
        self,
        incidents: List[CorrelatedIncident]
    ) -> List[CorrelatedIncident]:
        """
        Assigns risk scores and priority tiers to a list of incidents,
        returning them sorted in descending order of operational priority.
        """
        for inc in incidents:
            score = self.compute_risk(inc)
            inc.contextual_risk_score = score

            if score >= 0.75:
                inc.priority_level = "CRITICAL"
            elif score >= 0.55:
                inc.priority_level = "HIGH"
            elif score >= 0.35:
                inc.priority_level = "MEDIUM"
            else:
                inc.priority_level = "LOW"

        # Sort descending by risk score
        return sorted(incidents, key=lambda inc: inc.contextual_risk_score, reverse=True)
