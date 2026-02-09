"""
Main Training Script
Configure and run the RL portfolio trader training
"""

import os
import sys
import argparse
import torch
import numpy as np
import random

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from trading_env import TradingEnvironment
from ddpg_agent import DDPGAgent
from trainer import Trainer


def set_seed(seed: int = 42):
    """Set random seeds for reproducibility"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True


def main():
    parser = argparse.ArgumentParser(description='Train RL Portfolio Trader')
    parser.add_argument('--episodes', type=int, default=200, help='Number of training episodes')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--save_dir', type=str, default='../results', help='Directory to save results')
    parser.add_argument('--use_her', action='store_true', help='Use Hindsight Experience Replay')
    parser.add_argument('--warmup', type=int, default=10, help='Warmup episodes before training')
    
    args = parser.parse_args()
    
    # Set seed
    set_seed(args.seed)
    
    # Define assets (10 stocks + crypto)
    tickers = [
        # Tech stocks
        'AAPL', 'MSFT', 'GOOGL', 'AMZN',
        # Financial
        'JPM', 'BAC',
        # Other sectors
        'JNJ', 'PG',
        # Crypto (using crypto ETFs as proxies)
        'GBTC',  # Bitcoin
        'ETHE'   # Ethereum
    ]
    
    print("=" * 80)
    print("RL PORTFOLIO TRADER - TRAINING")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  Assets: {tickers}")
    print(f"  Training Period: 2018-2023 (5 years)")
    print(f"  Episodes: {args.episodes}")
    print(f"  Use HER: {args.use_her}")
    print(f"  Random Seed: {args.seed}")
    print(f"  Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
    print()
    
    # Create environment
    env = TradingEnvironment(
        tickers=tickers,
        start_date='2018-01-01',
        end_date='2023-01-01',
        initial_balance=100000,
        transaction_cost=0.001,  # 0.1%
        lookback_window=30,
        vix_window=20,
        risk_penalty=0.5
    )
    
    # Create agent
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.shape[0]
    
    agent = DDPGAgent(
        state_dim=state_dim,
        action_dim=action_dim,
        hidden_dims=[256, 256],
        lr_actor=1e-4,
        lr_critic=3e-4,
        gamma=0.99,
        tau=0.005,
        buffer_capacity=1000000,
        batch_size=256
    )
    
    print(f"Environment created:")
    print(f"  State dimension: {state_dim}")
    print(f"  Action dimension: {action_dim}")
    print(f"  Max steps per episode: {env.max_steps}")
    print()
    
    # Create trainer
    save_dir = os.path.join(os.path.dirname(__file__), args.save_dir)
    trainer = Trainer(
        env=env,
        agent=agent,
        use_her=args.use_her,
        save_dir=save_dir
    )
    
    # Train
    trainer.train(
        n_episodes=args.episodes,
        warmup_episodes=args.warmup,
        train_frequency=1,
        verbose=True
    )
    
    # Evaluate
    print("\n" + "=" * 80)
    print("FINAL EVALUATION")
    print("=" * 80)
    eval_results = trainer.evaluate(n_episodes=5)
    
    print("\n" + "=" * 80)
    print("TRAINING COMPLETE")
    print("=" * 80)
    print(f"\nResults saved to: {save_dir}")
    print(f"  - Model: final_model.pt")
    print(f"  - Metrics: training_metrics.json")
    print(f"  - Plots: training_progress.png")
    
    # Check if targets achieved
    sharpe_achieved = eval_results['sharpe_ratios_mean'] > 1.5
    drawdown_achieved = abs(eval_results['max_drawdowns_mean']) < 0.15
    
    print(f"\nTarget Achievement:")
    print(f"  Sharpe Ratio > 1.5: {'✓' if sharpe_achieved else '✗'} ({eval_results['sharpe_ratios_mean']:.4f})")
    print(f"  Max Drawdown < 15%: {'✓' if drawdown_achieved else '✗'} ({abs(eval_results['max_drawdowns_mean'])*100:.2f}%)")


if __name__ == '__main__':
    main()
