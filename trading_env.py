"""
Trading Environment - Web Optimized Version
"""

import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces
import yfinance as yf
from typing import Dict, Tuple, Optional


class TradingEnvironment(gym.Env):
    """Trading Environment for Portfolio Allocation"""
    
    def __init__(
        self,
        tickers: list,
        start_date: str,
        end_date: str,
        initial_balance: float = 100000,
        transaction_cost: float = 0.001,
        lookback_window: int = 30,
        risk_penalty: float = 0.5
    ):
        super().__init__()
        
        self.tickers = tickers
        self.n_assets = len(tickers)
        self.start_date = start_date
        self.end_date = end_date
        self.initial_balance = initial_balance
        self.transaction_cost = transaction_cost
        self.lookback_window = lookback_window
        self.risk_penalty = risk_penalty
        
        # Download data
        self.data = self._download_data()
        
        # Simplified state: returns + volatility
        state_dim = (self.n_assets * lookback_window) + self.n_assets
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(state_dim,), dtype=np.float32
        )
        
        self.action_space = spaces.Box(
            low=-10, high=10, shape=(self.n_assets,), dtype=np.float32
        )
        
        # Tracking
        self.current_step = 0
        self.max_steps = len(self.data) - lookback_window - 1
        self.balance = initial_balance
        self.portfolio_value = initial_balance
        self.current_weights = np.ones(self.n_assets) / self.n_assets
        self.portfolio_history = []
        self.weights_history = []
        
    def _download_data(self) -> pd.DataFrame:
        """Download price data"""
        print(f"Downloading data for {self.tickers}...")
        data = yf.download(self.tickers, start=self.start_date, end=self.end_date, progress=False)
        
        if len(self.tickers) == 1:
            data = pd.DataFrame(data['Adj Close'])
            data.columns = self.tickers
        else:
            data = data['Adj Close']
        
        data = data.fillna(method='ffill').fillna(method='bfill')
        return data
    
    def _get_state(self) -> np.ndarray:
        """Get current state"""
        idx = self.lookback_window + self.current_step
        prices = self.data.iloc[idx - self.lookback_window:idx].values
        
        returns = np.diff(prices, axis=0) / prices[:-1]
        returns_flat = returns.flatten()
        volatility = np.std(returns, axis=0)
        
        state = np.concatenate([returns_flat, volatility])
        return state.astype(np.float32)
    
    def _apply_softmax(self, raw_actions: np.ndarray) -> np.ndarray:
        """Apply softmax for valid weights"""
        exp_actions = np.exp(raw_actions - np.max(raw_actions))
        weights = exp_actions / np.sum(exp_actions)
        return weights
    
    def reset(self, seed: Optional[int] = None) -> Tuple[np.ndarray, Dict]:
        """Reset environment"""
        super().reset(seed=seed)
        
        self.current_step = 0
        self.balance = self.initial_balance
        self.portfolio_value = self.initial_balance
        self.current_weights = np.ones(self.n_assets) / self.n_assets
        self.portfolio_history = [self.initial_balance]
        self.weights_history = []
        
        state = self._get_state()
        return state, {}
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """Execute one step"""
        new_weights = self._apply_softmax(action)
        
        # Transaction cost
        weight_change = np.abs(new_weights - self.current_weights)
        transaction_cost = np.sum(weight_change) * self.transaction_cost * self.portfolio_value
        
        # Get prices
        idx = self.lookback_window + self.current_step
        current_prices = self.data.iloc[idx].values
        next_prices = self.data.iloc[idx + 1].values
        
        # Calculate returns
        asset_returns = (next_prices - current_prices) / current_prices
        portfolio_return = np.dot(new_weights, asset_returns)
        
        # Calculate risk
        returns_window = self.data.iloc[idx - self.lookback_window:idx].pct_change().dropna()
        cov_matrix = returns_window.cov().values
        portfolio_variance = new_weights.T @ cov_matrix @ new_weights
        portfolio_risk = np.sqrt(portfolio_variance)
        
        # Update portfolio
        self.portfolio_value = self.portfolio_value * (1 + portfolio_return) - transaction_cost
        
        # Reward
        reward = portfolio_return - self.risk_penalty * portfolio_risk
        
        # Update state
        self.current_weights = new_weights
        self.weights_history.append(new_weights.tolist())
        self.portfolio_history.append(self.portfolio_value)
        self.current_step += 1
        
        # Done
        truncated = self.current_step >= self.max_steps
        terminated = False
        
        next_state = self._get_state() if not truncated else np.zeros_like(self._get_state())
        
        info = {
            'portfolio_value': self.portfolio_value,
            'weights': new_weights.tolist(),
            'portfolio_return': portfolio_return,
            'portfolio_risk': portfolio_risk,
            'reward': reward
        }
        
        return next_state, reward, terminated, truncated, info
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Calculate performance metrics"""
        returns = pd.Series(self.portfolio_history).pct_change().dropna()
        
        total_return = (self.portfolio_value - self.initial_balance) / self.initial_balance
        n_days = len(returns)
        annualized_return = (1 + total_return) ** (252 / n_days) - 1
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        return {
            'total_return': float(total_return),
            'annualized_return': float(annualized_return),
            'volatility': float(volatility),
            'sharpe_ratio': float(sharpe_ratio),
            'max_drawdown': float(max_drawdown),
            'final_value': float(self.portfolio_value)
        }
