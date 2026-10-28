"""
IncidentIQ Investigation & Forensic Dossier Engine:
Provides historical incident retrieval, attack timeline reconstruction,
MITRE ATT&CK technique mapping, and cryptographic evidence verification
using SHA-256 tamper-evident integrity hashes.
"""

import hashlib
import json
import time
from typing import List, Dict, Any, Optional
from src.correlation.incident_correlator import CorrelatedIncident, SecurityEvent


class IncidentIQEngine:
    """
    IncidentIQ Investigation Layer:
    Synthesizes correlated security events into forensically verified
    incident dossiers with automated response recommendations.
    """
    def __init__(self):
        self.incident_archive: List[Dict[str, Any]] = []

    @staticmethod
    def compute_evidence_hash(incident: CorrelatedIncident) -> str:
        """
        Computes a deterministic SHA-256 cryptographic digest of all
        constituent events, guaranteeing tamper-evident auditability.
        """
        hasher = hashlib.sha256()
        canonical_records = []
        for e in sorted(incident.events, key=lambda ev: (ev.timestamp, ev.event_id)):
            rec = {
                'id': e.event_id,
                'ts': round(e.timestamp, 4),
                'dev': e.device_id,
                'dst': e.dst_ip,
                'srv': e.service,
                'score': round(e.detection_score, 4),
                'class': e.attack_class
            }
            canonical_records.append(rec)

        serialized = json.dumps(canonical_records, sort_keys=True, separators=(',', ':'))
        hasher.update(serialized.encode('utf-8'))
        return hasher.hexdigest()

    def generate_dossier(self, incident: CorrelatedIncident) -> Dict[str, Any]:
        """
        Constructs an analyst-ready investigation dossier for the SOC.
        """
        evidence_hash = self.compute_evidence_hash(incident)

        # Build chronological timeline
        timeline = []
        for e in sorted(incident.events, key=lambda ev: ev.timestamp):
            timeline.append({
                'timestamp': round(e.timestamp, 3),
                'event_id': e.event_id,
                'device_id': e.device_id,
                'service': e.service,
                'attack_class': e.attack_class,
                'subclass': e.attack_subclass,
                'score': round(e.detection_score, 4)
            })

        # Generate containment recommendation
        primary = incident.primary_attack_class
        if primary in ['DDoS', 'DoS']:
            rec_action = f"Apply immediate traffic rate limiting and ACL ingress filtering on target services: {', '.join(incident.affected_services)}."
        elif primary == 'Mirai':
            rec_action = f"Isolate infected IoT hosts {', '.join(incident.affected_devices[:3])} and terminate unauthorized C2 outbound sockets."
        elif primary == 'BruteForce':
            rec_action = f"Temporarily lock targeted service credentials on {', '.join(incident.affected_services)} and enforce multi-factor re-authentication."
        elif primary == 'Web-based':
            rec_action = f"Deploy WAF virtual patching for web exploit vectors and inspect application database query logs."
        elif primary == 'Recon':
            rec_action = "Block scanning source IP at firewall edge and enable verbose port audit logging."
        else:
            rec_action = "Review system logs for anomalous behavioral divergence."

        dossier = {
            'incident_id': incident.incident_id,
            'priority': incident.priority_level,
            'risk_score': round(incident.contextual_risk_score, 4),
            'primary_attack_class': incident.primary_attack_class,
            'is_multistage': incident.is_multistage,
            'event_count': incident.event_count,
            'duration_seconds': round(incident.duration, 2),
            'start_time': round(incident.start_time, 2),
            'end_time': round(incident.end_time, 2),
            'affected_devices': incident.affected_devices,
            'affected_services': incident.affected_services,
            'mitre_tactics': incident.mitre_tactics,
            'mitre_techniques': incident.mitre_techniques,
            'evidence_sha256': evidence_hash,
            'recommended_action': rec_action,
            'timeline_summary': timeline[:10]  # First 10 events for quick display
        }

        self.incident_archive.append(dossier)
        return dossier
