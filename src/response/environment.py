"""
Defensive-Response Environment for IoT Intrusion Mitigation (E4)
Simulates an IoT Edge Gateway processing flow reconstruction errors and packet rates.

Actions (Purely Defensive):
  0: ALLOW      (Pass flow; 0 service disruption)
  1: ALERT      (Log SOC alert; low overhead)
  2: RATE_LIMIT (Throttle flow by 50%; medium service disruption)
  3: BLOCK      (Isolate/drop flow; high service disruption if false positive)
"""

import numpy as np

class IoTDefenseEnv:
    def __init__(self, error_stream, rate_stream, label_stream, max_steps=5000, benign_block_penalty=-10.0):
        self.error_stream = np.array(error_stream, dtype=float)
        self.rate_stream = np.array(rate_stream, dtype=float)
        self.label_stream = np.array(label_stream, dtype=int)
        self.max_steps = min(max_steps, len(error_stream))
        self.benign_block_penalty = float(benign_block_penalty)
        
        self.current_step = 0
        self.consecutive_alerts = 0
        
        # Quantile bins derived from baseline distribution
        self.err_quantiles = np.percentile(self.error_stream, [50, 90, 98])
        self.rate_quantiles = np.percentile(self.rate_stream, [50, 90, 98])

    def reset(self):
        self.current_step = 0
        self.consecutive_alerts = 0
        return self._get_state()

    def _discretize(self, val, quantiles):
        return int(np.digitize(val, quantiles))

    def _get_state(self):
        err_val = self.error_stream[self.current_step]
        rate_val = self.rate_stream[self.current_step]
        
        err_bin = self._discretize(err_val, self.err_quantiles)
        rate_bin = self._discretize(rate_val, self.rate_quantiles)
        alert_bin = min(self.consecutive_alerts, 3)
        
        # Discrete state ID: 4 x 4 x 4 = 64 states
        state_id = err_bin * 16 + rate_bin * 4 + alert_bin
        
        # Continuous normalized vector for DQN: [err_norm, rate_norm, alert_norm]
        continuous_vector = np.array([
            min(err_val / (self.err_quantiles[-1] + 1e-5), 5.0),
            min(rate_val / (self.rate_quantiles[-1] + 1e-5), 5.0),
            alert_bin / 3.0
        ], dtype=np.float32)
        
        return state_id, continuous_vector

    def step(self, action):
        is_attack = self.label_stream[self.current_step]
        
        # Reward Matrix
        if is_attack == 1:
            if action == 3: # BLOCK
                reward = 10.0
                self.consecutive_alerts += 1
            elif action == 2: # RATE_LIMIT
                reward = 4.0
                self.consecutive_alerts += 1
            elif action == 1: # ALERT
                reward = -2.0
                self.consecutive_alerts += 1
            else: # ALLOW (Missed Attack)
                reward = -10.0
                self.consecutive_alerts = 0
        else: # Benign Flow
            if action == 0: # ALLOW
                reward = 2.0
                self.consecutive_alerts = 0
            elif action == 1: # ALERT
                reward = 1.0
                self.consecutive_alerts += 1
            elif action == 2: # RATE_LIMIT (Unnecessary throttling)
                reward = -3.0
                self.consecutive_alerts += 1
            else: # BLOCK (False Positive Blocking)
                reward = self.benign_block_penalty
                self.consecutive_alerts += 1

        self.current_step += 1
        done = (self.current_step >= self.max_steps)
        
        next_state_id, next_vector = (0, np.zeros(3, dtype=np.float32)) if done else self._get_state()
        info = {
            'is_attack': is_attack,
            'action': action,
            'reward': reward
        }
        
        return (next_state_id, next_vector), reward, done, info
