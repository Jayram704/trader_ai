"""
Deep Deterministic Policy Gradient (DDPG) Agent with Twin Critics
Implements actor-critic architecture for continuous portfolio allocation
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from collections import deque
import random
from typing import Tuple, List


class ReplayBuffer:
    """Experience replay buffer for off-policy learning"""
    
    def __init__(self, capacity: int):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        """Add experience to buffer"""
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size: int):
        """Sample random batch from buffer"""
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        return (
            np.array(states),
            np.array(actions),
            np.array(rewards),
            np.array(next_states),
            np.array(dones)
        )
    
    def __len__(self):
        return len(self.buffer)


class Actor(nn.Module):
    """
    Actor network: maps states to actions (portfolio weights)
    Output uses tanh to bound actions, which will be processed via softmax in env
    """
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dims: List[int] = [256, 256]):
        super(Actor, self).__init__()
        
        layers = []
        input_dim = state_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.LayerNorm(hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.1))
            input_dim = hidden_dim
        
        self.network = nn.Sequential(*layers)
        self.output_layer = nn.Linear(input_dim, action_dim)
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize network weights using He initialization"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
        
        # Small initialization for output layer
        nn.init.uniform_(self.output_layer.weight, -3e-3, 3e-3)
        nn.init.uniform_(self.output_layer.bias, -3e-3, 3e-3)
    
    def forward(self, state):
        """Forward pass through actor network"""
        x = self.network(state)
        # Output raw logits (will be converted to weights via softmax in environment)
        action = self.output_layer(x)
        return action


class Critic(nn.Module):
    """
    Critic network: estimates Q-value for state-action pairs
    Uses twin critics to reduce overestimation bias
    """
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dims: List[int] = [256, 256]):
        super(Critic, self).__init__()
        
        # First critic
        layers1 = []
        input_dim = state_dim + action_dim
        
        for hidden_dim in hidden_dims:
            layers1.append(nn.Linear(input_dim, hidden_dim))
            layers1.append(nn.LayerNorm(hidden_dim))
            layers1.append(nn.ReLU())
            layers1.append(nn.Dropout(0.1))
            input_dim = hidden_dim
        
        self.network1 = nn.Sequential(*layers1)
        self.output1 = nn.Linear(input_dim, 1)
        
        # Second critic (twin)
        layers2 = []
        input_dim = state_dim + action_dim
        
        for hidden_dim in hidden_dims:
            layers2.append(nn.Linear(input_dim, hidden_dim))
            layers2.append(nn.LayerNorm(hidden_dim))
            layers2.append(nn.ReLU())
            layers2.append(nn.Dropout(0.1))
            input_dim = hidden_dim
        
        self.network2 = nn.Sequential(*layers2)
        self.output2 = nn.Linear(input_dim, 1)
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize network weights"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
        
        # Small initialization for output layers
        for output in [self.output1, self.output2]:
            nn.init.uniform_(output.weight, -3e-3, 3e-3)
            nn.init.uniform_(output.bias, -3e-3, 3e-3)
    
    def forward(self, state, action):
        """Forward pass through both critics"""
        x = torch.cat([state, action], dim=1)
        
        q1 = self.output1(self.network1(x))
        q2 = self.output2(self.network2(x))
        
        return q1, q2
    
    def Q1(self, state, action):
        """Get Q-value from first critic only"""
        x = torch.cat([state, action], dim=1)
        return self.output1(self.network1(x))


class OUNoise:
    """Ornstein-Uhlenbeck process for exploration"""
    
    def __init__(self, size: int, mu: float = 0., theta: float = 0.15, sigma: float = 0.2):
        self.mu = mu * np.ones(size)
        self.theta = theta
        self.sigma = sigma
        self.state = None
        self.reset()
    
    def reset(self):
        """Reset internal state"""
        self.state = np.copy(self.mu)
    
    def sample(self):
        """Generate noise sample"""
        dx = self.theta * (self.mu - self.state) + self.sigma * np.random.randn(len(self.state))
        self.state += dx
        return self.state


class DDPGAgent:
    """
    DDPG Agent with Twin Critics for Portfolio Allocation
    """
    
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden_dims: List[int] = [256, 256],
        lr_actor: float = 1e-4,
        lr_critic: float = 3e-4,
        gamma: float = 0.99,
        tau: float = 0.005,
        buffer_capacity: int = 1000000,
        batch_size: int = 256,
        device: str = 'cuda' if torch.cuda.is_available() else 'cpu'
    ):
        self.device = device
        self.gamma = gamma
        self.tau = tau
        self.batch_size = batch_size
        self.action_dim = action_dim
        
        # Actor networks
        self.actor = Actor(state_dim, action_dim, hidden_dims).to(device)
        self.actor_target = Actor(state_dim, action_dim, hidden_dims).to(device)
        self.actor_target.load_state_dict(self.actor.state_dict())
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=lr_actor)
        
        # Critic networks (twin critics)
        self.critic = Critic(state_dim, action_dim, hidden_dims).to(device)
        self.critic_target = Critic(state_dim, action_dim, hidden_dims).to(device)
        self.critic_target.load_state_dict(self.critic.state_dict())
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=lr_critic)
        
        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_capacity)
        
        # Exploration noise
        self.noise = OUNoise(action_dim)
        
        # Training statistics
        self.actor_losses = []
        self.critic_losses = []
    
    def select_action(self, state: np.ndarray, add_noise: bool = True) -> np.ndarray:
        """Select action using current policy with optional exploration noise"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        self.actor.eval()
        with torch.no_grad():
            action = self.actor(state_tensor).cpu().numpy()[0]
        self.actor.train()
        
        if add_noise:
            noise = self.noise.sample()
            action = action + noise
        
        return action
    
    def train(self):
        """Train agent using batch from replay buffer"""
        if len(self.replay_buffer) < self.batch_size:
            return
        
        # Sample batch
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(self.batch_size)
        
        # Convert to tensors
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.FloatTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).unsqueeze(1).to(self.device)
        
        # Update Critic
        with torch.no_grad():
            # Get next actions from target actor
            next_actions = self.actor_target(next_states)
            
            # Compute target Q-values using twin critics (take minimum)
            target_q1, target_q2 = self.critic_target(next_states, next_actions)
            target_q = torch.min(target_q1, target_q2)
            target_q = rewards + (1 - dones) * self.gamma * target_q
        
        # Current Q-values
        current_q1, current_q2 = self.critic(states, actions)
        
        # Critic loss (MSE for both critics)
        critic_loss = F.mse_loss(current_q1, target_q) + F.mse_loss(current_q2, target_q)
        
        # Optimize critic
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.critic.parameters(), 1.0)
        self.critic_optimizer.step()
        
        # Update Actor
        actor_actions = self.actor(states)
        actor_loss = -self.critic.Q1(states, actor_actions).mean()
        
        # Optimize actor
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.actor.parameters(), 1.0)
        self.actor_optimizer.step()
        
        # Soft update target networks
        self._soft_update(self.actor, self.actor_target)
        self._soft_update(self.critic, self.critic_target)
        
        # Track losses
        self.actor_losses.append(actor_loss.item())
        self.critic_losses.append(critic_loss.item())
    
    def _soft_update(self, source: nn.Module, target: nn.Module):
        """Soft update target network parameters"""
        for target_param, param in zip(target.parameters(), source.parameters()):
            target_param.data.copy_(
                target_param.data * (1.0 - self.tau) + param.data * self.tau
            )
    
    def save(self, filepath: str):
        """Save agent parameters"""
        torch.save({
            'actor': self.actor.state_dict(),
            'critic': self.critic.state_dict(),
            'actor_target': self.actor_target.state_dict(),
            'critic_target': self.critic_target.state_dict(),
            'actor_optimizer': self.actor_optimizer.state_dict(),
            'critic_optimizer': self.critic_optimizer.state_dict(),
        }, filepath)
    
    def load(self, filepath: str):
        """Load agent parameters"""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.actor.load_state_dict(checkpoint['actor'])
        self.critic.load_state_dict(checkpoint['critic'])
        self.actor_target.load_state_dict(checkpoint['actor_target'])
        self.critic_target.load_state_dict(checkpoint['critic_target'])
        self.actor_optimizer.load_state_dict(checkpoint['actor_optimizer'])
        self.critic_optimizer.load_state_dict(checkpoint['critic_optimizer'])
