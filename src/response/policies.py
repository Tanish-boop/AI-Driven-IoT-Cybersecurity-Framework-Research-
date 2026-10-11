"""
Defensive-Response Policies for IoT Intrusion Mitigation (E4)
1. Static Rule-Based Policy
2. Tabular Q-Learning Policy
3. Deep Q-Network (DQN) Policy
"""

import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

class RuleBasedPolicy:
    def __init__(self, tau_threshold=0.075):
        self.tau_threshold = tau_threshold

    def select_action(self, err_val, alert_count):
        if err_val <= self.tau_threshold:
            return 0 # ALLOW
        else:
            if alert_count == 0:
                return 1 # ALERT
            elif alert_count == 1:
                return 2 # RATE_LIMIT
            else:
                return 3 # BLOCK

class QLearningPolicy:
    def __init__(self, n_states=64, n_actions=4, lr=0.1, gamma=0.95, epsilon=1.0, epsilon_decay=0.995, min_epsilon=0.01):
        self.n_states = n_states
        self.n_actions = n_actions
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        
        self.q_table = np.zeros((n_states, n_actions))

    def select_action(self, state_id, evaluate=False):
        if not evaluate and random.random() < self.epsilon:
            return random.randint(0, self.n_actions - 1)
        return int(np.argmax(self.q_table[state_id]))

    def update(self, state, action, reward, next_state, done):
        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + (0 if done else self.gamma * self.q_table[next_state, best_next_action])
        td_error = td_target - self.q_table[state, action]
        self.q_table[state, action] += self.lr * td_error
        
        if done:
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

class QNetwork(nn.Module):
    def __init__(self, state_dim=3, action_dim=4):
        super(QNetwork, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, action_dim)
        )

    def forward(self, x):
        return self.net(x)

class ReplayBuffer:
    def __init__(self, capacity=10000):
        self.capacity = capacity
        self.buffer = []

    def push(self, state, action, reward, next_state, done):
        if len(self.buffer) >= self.capacity:
            self.buffer.pop(0)
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = zip(*batch)
        return (np.array(state), np.array(action), np.array(reward, dtype=np.float32),
                np.array(next_state), np.array(done, dtype=np.float32))

    def __len__(self):
        return len(self.buffer)

class DQNPolicy:
    def __init__(self, state_dim=3, action_dim=4, lr=0.001, gamma=0.95, epsilon=1.0, epsilon_decay=0.995, min_epsilon=0.01):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon

        self.policy_net = QNetwork(state_dim, action_dim)
        self.target_net = QNetwork(state_dim, action_dim)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.memory = ReplayBuffer(capacity=10000)
        self.batch_size = 64
        self.update_step = 0

    def select_action(self, state_vector, evaluate=False):
        if not evaluate and random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)
        with torch.no_grad():
            state_t = torch.tensor(state_vector, dtype=torch.float32).unsqueeze(0)
            q_values = self.policy_net(state_t)
            return int(torch.argmax(q_values, dim=1).item())

    def update(self, state, action, reward, next_state, done):
        self.memory.push(state, action, reward, next_state, done)
        if len(self.memory) < self.batch_size:
            return

        states, actions, rewards, next_states, dones = self.memory.sample(self.batch_size)

        states_t = torch.tensor(states, dtype=torch.float32)
        actions_t = torch.tensor(actions, dtype=torch.int64).unsqueeze(1)
        rewards_t = torch.tensor(rewards, dtype=torch.float32).unsqueeze(1)
        next_states_t = torch.tensor(next_states, dtype=torch.float32)
        dones_t = torch.tensor(dones, dtype=torch.float32).unsqueeze(1)

        current_q = self.policy_net(states_t).gather(1, actions_t)
        with torch.no_grad():
            max_next_q = self.target_net(next_states_t).max(1)[0].unsqueeze(1)
            target_q = rewards_t + (1 - dones_t) * self.gamma * max_next_q

        loss = nn.MSELoss()(current_q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.update_step += 1
        if self.update_step % 100 == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())

        if done:
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
