"""
Temporal Event Correlation Engine:
Constructs a Temporal Incident Correlation Graph using NetworkX to connect
individual intrusion alerts into coherent, multi-stage cybersecurity incidents.

Transforms isolated high-volume alerts:
    e_i = (t_i, u_i, d_i, ip_i, s_i, r_i)
Into structured incidents:
    I_k = {e_1, e_2, ..., e_m}
"""

import time
import numpy as np
import networkx as nx
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional, Set


# MITRE ATT&CK Mapping Dictionary for IoT/Network Attack Classes
MITRE_ATTACK_MAPPING = {
    'Recon': {
        'tactic': 'TA0043: Reconnaissance',
        'techniques': ['T1595: Active Scanning', 'T1046: Network Service Discovery'],
        'stage_order': 1
    },
    'BruteForce': {
        'tactic': 'TA0006: Credential Access',
        'techniques': ['T1110: Brute Force', 'T1110.001: Password Guessing'],
        'stage_order': 2
    },
    'Web-based': {
        'tactic': 'TA0001: Initial Access',
        'techniques': ['T1190: Exploit Public-Facing Application', 'T1059: Command and Scripting Interpreter'],
        'stage_order': 3
    },
    'Spoofing': {
        'tactic': 'TA0005: Defense Evasion / TA0006: Credential Access',
        'techniques': ['T1557: Adversary-in-the-Middle', 'T1557.002: ARP Spoofing'],
        'stage_order': 3
    },
    'Mirai': {
        'tactic': 'TA0011: Command and Control / TA0040: Impact',
        'techniques': ['T1584.005: Botnet', 'T1498: Network Denial of Service'],
        'stage_order': 4
    },
    'DoS': {
        'tactic': 'TA0040: Impact',
        'techniques': ['T1498: Network Denial of Service', 'T1498.001: Direct Network Flood'],
        'stage_order': 5
    },
    'DDoS': {
        'tactic': 'TA0040: Impact',
        'techniques': ['T1498.001: Direct Network Flood', 'T1499: Endpoint Denial of Service'],
        'stage_order': 5
    },
    'Benign': {
        'tactic': 'None: Normal Traffic',
        'techniques': [],
        'stage_order': 0
    }
}


@dataclass
class SecurityEvent:
    event_id: str
    timestamp: float
    device_id: str
    dst_ip: str
    service: str
    detection_score: float
    attack_class: str
    attack_subclass: str
    src_ip: str = ""
    is_anomaly: int = 1
    ground_truth: int = 1
    ground_truth_incident: Optional[str] = None


@dataclass
class CorrelatedIncident:
    incident_id: str
    events: List[SecurityEvent] = field(default_factory=list)
    start_time: float = 0.0
    end_time: float = 0.0
    duration: float = 0.0
    primary_attack_class: str = "Unknown"
    attack_classes: List[str] = field(default_factory=list)
    attack_subclasses: List[str] = field(default_factory=list)
    affected_devices: List[str] = field(default_factory=list)
    affected_services: List[str] = field(default_factory=list)
    max_score: float = 0.0
    mean_score: float = 0.0
    event_count: int = 0
    mitre_tactics: List[str] = field(default_factory=list)
    mitre_techniques: List[str] = field(default_factory=list)
    is_multistage: bool = False
    contextual_risk_score: float = 0.0
    priority_level: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL

    def compile_summary(self):
        """Compiles aggregates from constituent events."""
        if not self.events:
            return
        self.event_count = len(self.events)
        self.start_time = min(e.timestamp for e in self.events)
        self.end_time = max(e.timestamp for e in self.events)
        self.duration = max(0.0, self.end_time - self.start_time)

        scores = [e.detection_score for e in self.events]
        self.max_score = float(max(scores))
        self.mean_score = float(np.mean(scores))

        self.affected_devices = sorted(list(set(e.device_id for e in self.events)))
        self.affected_services = sorted(list(set(e.service for e in self.events)))

        classes = [e.attack_class for e in self.events if e.attack_class != 'Benign']
        if classes:
            # Primary class is most frequent attack class
            self.primary_attack_class = max(set(classes), key=classes.count)
            self.attack_classes = sorted(list(set(classes)))
        else:
            self.primary_attack_class = "Benign_Anomaly"
            self.attack_classes = ["Benign"]

        self.attack_subclasses = sorted(list(set(e.attack_subclass for e in self.events)))

        # MITRE ATT&CK compilation
        tactics = []
        techniques = []
        for c in self.attack_classes:
            mapping = MITRE_ATTACK_MAPPING.get(c, None)
            if mapping:
                if mapping['tactic'] != 'None: Normal Traffic':
                    tactics.append(mapping['tactic'])
                techniques.extend(mapping['techniques'])
        self.mitre_tactics = sorted(list(set(tactics)))
        self.mitre_techniques = sorted(list(set(techniques)))

        # Multi-stage if contains more than 1 distinct non-benign attack class
        self.is_multistage = len(self.attack_classes) > 1


class TemporalIncidentCorrelator:
    """
    Graph-based alert correlation engine using NetworkX.
    Links alerts based on:
      1. Temporal Proximity: |t_i - t_j| <= window_seconds
      2. Entity Affinity: Same Device, Target IP, or Target Service
      3. Causal Attack Chains: e.g. Recon -> BruteForce -> DoS
    """
    def __init__(
        self,
        window_seconds: float = 30.0,
        enable_causal_chains: bool = True
    ):
        self.window_seconds = float(window_seconds)
        self.enable_causal_chains = enable_causal_chains

    def correlate_alerts(self, alerts: List[SecurityEvent]) -> List[CorrelatedIncident]:
        """
        Groups a list of incoming security alerts into coherent incidents using
        streaming session correlation with temporal sliding windows and entity affinity.
        """
        if not alerts:
            return []

        # Sort alerts chronologically
        sorted_alerts = sorted(alerts, key=lambda a: a.timestamp)

        # Active incident sessions: key -> session dict
        # Key: (device_id, service_group)
        open_sessions: Dict[str, Dict[str, Any]] = {}
        completed_sessions: List[Dict[str, Any]] = []

        # Inactivity timeout (seconds) and maximum incident duration (seconds)
        inactivity_timeout = self.window_seconds
        max_duration = max(300.0, self.window_seconds * 5.0)

        for alert in sorted_alerts:
            # Service grouping
            srv_grp = alert.service if alert.service in ['DNS', 'HTTPS', 'SSH', 'Telnet', 'HTTP'] else 'Network'
            session_key = f"{alert.device_id}_{srv_grp}"

            # Check if an open session exists and is still active
            matched_key = None
            if session_key in open_sessions:
                sess = open_sessions[session_key]
                if alert.timestamp - sess['last_ts'] <= inactivity_timeout and alert.timestamp - sess['start_ts'] <= max_duration:
                    matched_key = session_key

            # If not matched to exact key, check for causal progression on same device
            if matched_key is None and self.enable_causal_chains:
                for k, sess in list(open_sessions.items()):
                    if sess['device_id'] == alert.device_id:
                        if alert.timestamp - sess['last_ts'] <= inactivity_timeout and alert.timestamp - sess['start_ts'] <= max_duration:
                            # Causal check: e.g. Recon -> Exploit/DoS
                            prev_cls = sess['events'][-1].attack_class
                            order_prev = MITRE_ATTACK_MAPPING.get(prev_cls, {}).get('stage_order', 0)
                            order_curr = MITRE_ATTACK_MAPPING.get(alert.attack_class, {}).get('stage_order', 0)
                            if 0 < order_prev <= order_curr:
                                matched_key = k
                                break

            # Flush expired sessions
            expired_keys = []
            for k, sess in open_sessions.items():
                if alert.timestamp - sess['last_ts'] > inactivity_timeout or alert.timestamp - sess['start_ts'] > max_duration:
                    expired_keys.append(k)
            for k in expired_keys:
                completed_sessions.append(open_sessions.pop(k))

            if matched_key is not None:
                sess = open_sessions[matched_key]
                sess['events'].append(alert)
                sess['last_ts'] = alert.timestamp
            else:
                open_sessions[session_key] = {
                    'device_id': alert.device_id,
                    'dst_ip': alert.dst_ip,
                    'service': alert.service,
                    'start_ts': alert.timestamp,
                    'last_ts': alert.timestamp,
                    'events': [alert]
                }

        # Flush remaining open sessions
        completed_sessions.extend(open_sessions.values())

        # Build CorrelatedIncident objects
        incidents: List[CorrelatedIncident] = []
        for inc_idx, sess in enumerate(completed_sessions):
            inc_events = sorted(sess['events'], key=lambda a: a.timestamp)
            incident = CorrelatedIncident(
                incident_id=f"INC-{inc_idx + 1:04d}",
                events=inc_events
            )
            incident.compile_summary()
            incidents.append(incident)

        # Sort incidents chronologically by start time
        incidents.sort(key=lambda inc: inc.start_time)
        return incidents

    @staticmethod
    def compute_alert_reduction_rate(total_alerts: int, total_incidents: int) -> float:
        """Computes percentage reduction in alert volume."""
        if total_alerts <= 0:
            return 0.0
        reduction = (total_alerts - total_incidents) / total_alerts * 100.0
        return float(max(0.0, reduction))
