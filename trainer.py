"""
Training Script for RL Portfolio Trader
Implements training loop with Hindsight Experience Replay (HER) and performance tracking
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import torch
from typing import Dict, List
import json
import os

from trading_env import TradingEnvironment
from ddpg_agent import DDPGAgent


class HindsightExperienceReplay:
    """
    Hindsight Experience Replay (HER) for sparse reward scenarios
    Generates additional training samples by relabeling goals/rewards
    """
    
    def __init__(self, agent: DDPGAgent, strategy: str = 'future', k: int = 4):
        self.agent = agent
        self.strategy = strategy
        self.k = k  # Number of additional goals to sample
    
    def augment_experience(self, episode_buffer: List):
        """
        Augment episode with hindsight goals
        For portfolio allocation, we relabel rewards based on achieved outcomes
        """
        # Store original experiences
        for transition in episode_buffer:
            state, action, reward, next_state, done = transition
            self.agent.replay_buffer.push(state, action, reward, next_state, done)
        
        # Generate hindsight experiences
        if self.strategy == 'future':
            for i, transition in enumerate(episode_buffer[:-1]):
                state, action, original_reward, next_state, done = transition
                
                # Sample k future states as alternative goals
                future_indices = np.random.choice(
                    range(i + 1, len(episode_buffer)),
                    size=min(self.k, len(episode_buffer) - i - 1),
                    replace=False
                )
                
                for future_idx in future_indices:
                    # Relabel reward based on achieved future state
                    future_transition = episode_buffer[future_idx]
                    hindsight_reward = self._compute_hindsight_reward(
                        state, action, future_transition[0]
                    )
                    
                    # Add augmented experience
                    self.agent.replay_buffer.push(
                        state, action, hindsight_reward, next_state, done
                    )
    
    def _compute_hindsight_reward(self, state, action, achieved_state):
        """
        Compute reward based on achieved outcome
        Reward = -distance to achieved outcome (encourages reaching various states)
        """
        # Simple distance metric in state space
        distance = np.linalg.norm(state - achieved_state)
        return -distance * 0.1  # Scale down to match original reward magnitude


class Trainer:
    """Main training class for RL portfolio trader"""
    
    def __init__(
        self,
        env: TradingEnvironment,
        agent: DDPGAgent,
        use_her: bool = True,
        save_dir: str = './results'
    ):
        self.env = env
        self.agent = agent
        self.use_her = use_her
        self.save_dir = save_dir
        
        if use_her:
            self.her = HindsightExperienceReplay(agent)
        
        os.makedirs(save_dir, exist_ok=True)
        
        # Training metrics
        self.episode_rewards = []
        self.episode_metrics = []
        self.training_stats = {
            'sharpe_ratios': [],
            'max_drawdowns': [],
            'returns': [],
            'volatilities': []
        }
    
    def train(
        self,
        n_episodes: int,
        warmup_episodes: int = 10,
        train_frequency: int = 1,
        verbose: bool = True
    ):
        """
        Train the agent
        
        Args:
            n_episodes: Number of training episodes
            warmup_episodes: Episodes to fill replay buffer before training
            train_frequency: Train every N steps
            verbose: Print progress
        """
        print(f"Starting training for {n_episodes} episodes...")
        print(f"Device: {self.agent.device}")
        
        for episode in tqdm(range(n_episodes), desc="Training"):
            state, _ = self.env.reset()
            episode_reward = 0
            episode_buffer = []
            done = False
            step = 0
            
            while not done:
                # Select action
                add_noise = episode < warmup_episodes  # Exploration in early episodes
                action = self.agent.select_action(state, add_noise=add_noise)
                
                # Take step
                next_state, reward, terminated, truncated, info = self.env.step(action)
                done = terminated or truncated
                
                episode_reward += reward
                
                # Store transition
                episode_buffer.append((state, action, reward, next_state, done))
                
                # Training
                if episode >= warmup_episodes and step % train_frequency == 0:
                    self.agent.train()
                
                state = next_state
                step += 1
            
            # Process episode with HER
            if self.use_her:
                self.her.augment_experience(episode_buffer)
            else:
                for transition in episode_buffer:
                    self.agent.replay_buffer.push(*transition)
            
            # Track metrics
            self.episode_rewards.append(episode_reward)
            metrics = self.env.get_performance_metrics()
            self.episode_metrics.append(metrics)
            
            self.training_stats['sharpe_ratios'].append(metrics['sharpe_ratio'])
            self.training_stats['max_drawdowns'].append(metrics['max_drawdown'])
            self.training_stats['returns'].append(metrics['annualized_return'])
            self.training_stats['volatilities'].append(metrics['volatility'])
            
            # Logging
            if verbose and (episode + 1) % 10 == 0:
                avg_reward = np.mean(self.episode_rewards[-10:])
                avg_sharpe = np.mean(self.training_stats['sharpe_ratios'][-10:])
                avg_drawdown = np.mean(self.training_stats['max_drawdowns'][-10:])
                
                print(f"\nEpisode {episode + 1}/{n_episodes}")
                print(f"  Avg Reward (10 eps): {avg_reward:.4f}")
                print(f"  Avg Sharpe Ratio: {avg_sharpe:.4f}")
                print(f"  Avg Max Drawdown: {avg_drawdown:.4f}")
                print(f"  Buffer Size: {len(self.agent.replay_buffer)}")
            
            # Save checkpoint
            if (episode + 1) % 50 == 0:
                self.save_checkpoint(episode + 1)
        
        print("\nTraining completed!")
        self.save_final_results()
    
    def evaluate(self, n_episodes: int = 5) -> Dict:
        """Evaluate trained agent"""
        print(f"\nEvaluating agent for {n_episodes} episodes...")
        
        eval_metrics = {
            'sharpe_ratios': [],
            'max_drawdowns': [],
            'returns': [],
            'volatilities': [],
            'final_values': []
        }
        
        for episode in range(n_episodes):
            state, _ = self.env.reset()
            done = False
            
            while not done:
                action = self.agent.select_action(state, add_noise=False)
                next_state, reward, terminated, truncated, info = self.env.step(action)
                done = terminated or truncated
                state = next_state
            
            metrics = self.env.get_performance_metrics()
            for key in eval_metrics:
                eval_metrics[key].append(metrics[key.rstrip('s')])
        
        # Compute statistics
        results = {}
        for key, values in eval_metrics.items():
            results[f'{key}_mean'] = np.mean(values)
            results[f'{key}_std'] = np.std(values)
        
        print("\nEvaluation Results:")
        print(f"  Sharpe Ratio: {results['sharpe_ratios_mean']:.4f} ± {results['sharpe_ratios_std']:.4f}")
        print(f"  Max Drawdown: {results['max_drawdowns_mean']:.4f} ± {results['max_drawdowns_std']:.4f}")
        print(f"  Annual Return: {results['returns_mean']:.4f} ± {results['returns_std']:.4f}")
        
        return results
    
    def save_checkpoint(self, episode: int):
        """Save training checkpoint"""
        checkpoint_path = os.path.join(self.save_dir, f'checkpoint_ep{episode}.pt')
        self.agent.save(checkpoint_path)
        
        # Save metrics
        metrics_path = os.path.join(self.save_dir, f'metrics_ep{episode}.json')
        with open(metrics_path, 'w') as f:
            json.dump({
                'episode': episode,
                'training_stats': {k: v[-100:] for k, v in self.training_stats.items()},
                'recent_metrics': self.episode_metrics[-10:]
            }, f, indent=2)
    
    def save_final_results(self):
        """Save final training results and plots"""
        # Save agent
        final_path = os.path.join(self.save_dir, 'final_model.pt')
        self.agent.save(final_path)
        
        # Save all metrics
        metrics_path = os.path.join(self.save_dir, 'training_metrics.json')
        with open(metrics_path, 'w') as f:
            json.dump({
                'training_stats': self.training_stats,
                'episode_rewards': self.episode_rewards,
                'final_metrics': self.episode_metrics[-1]
            }, f, indent=2)
        
        # Create visualizations
        self.plot_training_progress()
    
    def plot_training_progress(self):
        """Plot training metrics"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Sharpe Ratio
        axes[0, 0].plot(self.training_stats['sharpe_ratios'], alpha=0.6)
        axes[0, 0].plot(pd.Series(self.training_stats['sharpe_ratios']).rolling(20).mean(), 
                        linewidth=2, label='20-episode MA')
        axes[0, 0].axhline(y=1.5, color='r', linestyle='--', label='Target (1.5)')
        axes[0, 0].set_title('Sharpe Ratio over Episodes')
        axes[0, 0].set_xlabel('Episode')
        axes[0, 0].set_ylabel('Sharpe Ratio')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Max Drawdown
        axes[0, 1].plot(self.training_stats['max_drawdowns'], alpha=0.6)
        axes[0, 1].plot(pd.Series(self.training_stats['max_drawdowns']).rolling(20).mean(),
                        linewidth=2, label='20-episode MA')
        axes[0, 1].axhline(y=-0.15, color='r', linestyle='--', label='Constraint (-15%)')
        axes[0, 1].set_title('Maximum Drawdown over Episodes')
        axes[0, 1].set_xlabel('Episode')
        axes[0, 1].set_ylabel('Max Drawdown')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Returns
        axes[1, 0].plot(self.training_stats['returns'], alpha=0.6)
        axes[1, 0].plot(pd.Series(self.training_stats['returns']).rolling(20).mean(),
                        linewidth=2, label='20-episode MA')
        axes[1, 0].set_title('Annualized Returns over Episodes')
        axes[1, 0].set_xlabel('Episode')
        axes[1, 0].set_ylabel('Return')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Episode Rewards
        axes[1, 1].plot(self.episode_rewards, alpha=0.6)
        axes[1, 1].plot(pd.Series(self.episode_rewards).rolling(20).mean(),
                        linewidth=2, label='20-episode MA')
        axes[1, 1].set_title('Episode Rewards')
        axes[1, 1].set_xlabel('Episode')
        axes[1, 1].set_ylabel('Cumulative Reward')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.save_dir, 'training_progress.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Training plots saved to {self.save_dir}/training_progress.png")
