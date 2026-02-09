"""
Trading Environment for RL Portfolio Allocation
Implements Gymnasium interface with continuous action space for portfolio weights
"""

import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces
from typing import Dict, Tuple, Optional
import yfinance as yf
from datetime import datetime, timedelta


class TradingEnvironment(gym.Env):
    """
    Custom Trading Environment for Portfolio Allocation
    
    State: 30-day returns, volatility, VIX (20-day)
    Action: Portfolio weights (continuous, simplex constraint via softmax)
    Reward: Portfolio return - 0.5 * risk
    """
    
    metadata = {'render_modes': ['human']}
    
    def __init__(
        self,
        tickers: list,
        start_date: str,
        end_date: str,
        initial_balance: float = 100000,
        transaction_cost: float = 0.001,
        lookback_window: int = 30,
        vix_window: int = 20,
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
        self.vix_window = vix_window
        self.risk_penalty = risk_penalty
        
        # Download market data
        self.data = self._download_data()
        self.vix_data = self._download_vix()
        
        # State space: returns (n_assets * lookback) + volatility (n_assets) + VIX (vix_window)
        state_dim = (self.n_assets * lookback_window) + self.n_assets + vix_window
        self.observation_space = spaces.Box(
            low=-np.inf, 
            high=np.inf, 
            shape=(state_dim,), 
            dtype=np.float32
        )
        
        # Action space: continuous weights for each asset (will apply softmax)
        self.action_space = spaces.Box(
            low=-10, 
            high=10, 
            shape=(self.n_assets,), 
            dtype=np.float32
        )
        
        # Episode tracking
        self.current_step = 0
        self.max_steps = len(self.data) - lookback_window - 1
        self.balance = initial_balance
        self.portfolio_value = initial_balance
        self.positions = np.zeros(self.n_assets)
        self.portfolio_history = []
        self.weights_history = []
        
    def _download_data(self) -> pd.DataFrame:
        """Download OHLCV data for all tickers"""
        print(f"Downloading data for {self.tickers}...")
        data = yf.download(
            self.tickers,
            start=self.start_date,
            end=self.end_date,
            progress=False
        )
        
        # Handle single vs multiple tickers
        if len(self.tickers) == 1:
            data = pd.DataFrame(data['Adj Close'])
            data.columns = self.tickers
        else:
            data = data['Adj Close']
        
        # Forward fill missing values
        data = data.fillna(method='ffill').fillna(method='bfill')
        
        print(f"Data shape: {data.shape}")
        return data
    
    def _download_vix(self) -> pd.Series:
        """Download VIX (volatility index) data"""
        try:
            vix = yf.download('^VIX', start=self.start_date, end=self.end_date, progress=False)
            vix_series = vix['Adj Close'].fillna(method='ffill').fillna(method='bfill')
            
            # Align VIX with main data index
            vix_aligned = vix_series.reindex(self.data.index, method='ffill').fillna(method='bfill')
            return vix_aligned
        except Exception as e:
            print(f"Warning: Could not download VIX data: {e}")
            # Return synthetic VIX based on market volatility
            returns = self.data.pct_change().dropna()
            synthetic_vix = returns.std(axis=1).rolling(20).std() * 100
            return synthetic_vix.fillna(15)  # Fill with typical VIX value
    
    def _get_state(self) -> np.ndarray:
        """
        Construct state vector:
        - 30-day returns for each asset (flattened)
        - Volatility for each asset (30-day std)
        - VIX 20-day history
        """
        idx = self.lookback_window + self.current_step
        
        # Get price data for lookback window
        prices = self.data.iloc[idx - self.lookback_window:idx].values
        
        # Calculate returns (30-day window for each asset)
        returns = np.diff(prices, axis=0) / prices[:-1]
        returns_flat = returns.flatten()
        
        # Calculate volatility (std of returns for each asset)
        volatility = np.std(returns, axis=0)
        
        # Get VIX data (20-day window)
        vix_history = self.vix_data.iloc[idx - self.vix_window:idx].values
        
        # Normalize VIX to 0-1 range (typical range 10-80)
        vix_normalized = (vix_history - 10) / 70
        vix_normalized = np.clip(vix_normalized, 0, 1)
        
        # Concatenate all features
        state = np.concatenate([returns_flat, volatility, vix_normalized])
        
        return state.astype(np.float32)
    
    def _apply_softmax(self, raw_actions: np.ndarray) -> np.ndarray:
        """Apply softmax to ensure weights sum to 1 (simplex constraint)"""
        exp_actions = np.exp(raw_actions - np.max(raw_actions))  # Numerical stability
        weights = exp_actions / np.sum(exp_actions)
        return weights
    
    def _calculate_portfolio_value(self, weights: np.ndarray) -> float:
        """Calculate portfolio value given current weights"""
        idx = self.lookback_window + self.current_step
        current_prices = self.data.iloc[idx].values
        
        # Calculate number of shares for each asset
        shares = (self.portfolio_value * weights) / current_prices
        
        return np.sum(shares * current_prices)
    
    def _calculate_transaction_costs(self, new_weights: np.ndarray, old_weights: np.ndarray) -> float:
        """Calculate transaction costs based on portfolio rebalancing"""
        weight_change = np.abs(new_weights - old_weights)
        total_turnover = np.sum(weight_change)
        cost = total_turnover * self.transaction_cost * self.portfolio_value
        return cost
    
    def reset(self, seed: Optional[int] = None) -> Tuple[np.ndarray, Dict]:
        """Reset environment to initial state"""
        super().reset(seed=seed)
        
        self.current_step = 0
        self.balance = self.initial_balance
        self.portfolio_value = self.initial_balance
        self.positions = np.zeros(self.n_assets)
        self.portfolio_history = [self.initial_balance]
        self.weights_history = []
        
        # Initialize with equal weights
        self.current_weights = np.ones(self.n_assets) / self.n_assets
        
        state = self._get_state()
        info = {}
        
        return state, info
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        Execute one step in the environment
        
        Returns:
            observation, reward, terminated, truncated, info
        """
        # Convert raw actions to portfolio weights using softmax
        new_weights = self._apply_softmax(action)
        
        # Calculate transaction costs
        transaction_cost = self._calculate_transaction_costs(new_weights, self.current_weights)
        
        # Get current and next prices
        idx = self.lookback_window + self.current_step
        current_prices = self.data.iloc[idx].values
        next_prices = self.data.iloc[idx + 1].values
        
        # Calculate returns for each asset
        asset_returns = (next_prices - current_prices) / current_prices
        
        # Calculate portfolio return (weighted average)
        portfolio_return = np.dot(new_weights, asset_returns)
        
        # Calculate portfolio risk (volatility)
        returns_window = self.data.iloc[idx - self.lookback_window:idx].pct_change().dropna()
        cov_matrix = returns_window.cov().values
        portfolio_variance = new_weights.T @ cov_matrix @ new_weights
        portfolio_risk = np.sqrt(portfolio_variance)
        
        # Update portfolio value
        self.portfolio_value = self.portfolio_value * (1 + portfolio_return) - transaction_cost
        
        # Calculate reward: return - risk_penalty * risk
        reward = portfolio_return - self.risk_penalty * portfolio_risk
        
        # Update state
        self.current_weights = new_weights
        self.weights_history.append(new_weights)
        self.portfolio_history.append(self.portfolio_value)
        self.current_step += 1
        
        # Check if episode is done
        terminated = False
        truncated = self.current_step >= self.max_steps
        
        # Get next state
        if not truncated:
            next_state = self._get_state()
        else:
            next_state = np.zeros_like(self._get_state())
        
        # Info dictionary
        info = {
            'portfolio_value': self.portfolio_value,
            'weights': new_weights,
            'portfolio_return': portfolio_return,
            'portfolio_risk': portfolio_risk,
            'transaction_cost': transaction_cost,
            'reward': reward
        }
        
        return next_state, reward, terminated, truncated, info
    
    def render(self):
        """Render current state"""
        print(f"Step: {self.current_step}, Portfolio Value: ${self.portfolio_value:.2f}")
        print(f"Weights: {self.current_weights}")
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Calculate performance metrics for the episode"""
        returns = pd.Series(self.portfolio_history).pct_change().dropna()
        
        # Total return
        total_return = (self.portfolio_value - self.initial_balance) / self.initial_balance
        
        # Annualized return
        n_days = len(returns)
        annualized_return = (1 + total_return) ** (252 / n_days) - 1
        
        # Volatility (annualized)
        volatility = returns.std() * np.sqrt(252)
        
        # Sharpe ratio (assuming 0% risk-free rate)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # Maximum drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'final_value': self.portfolio_value
        }
