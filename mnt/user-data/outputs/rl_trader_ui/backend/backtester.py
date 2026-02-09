"""
Backtesting and Evaluation Module
Compares RL agent performance against benchmarks and visualizes results
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.optimize import minimize


class Backtester:
    """Backtest RL agent and compare with benchmarks"""
    
    def __init__(self, env, agent):
        self.env = env
        self.agent = agent
        self.results = {}
    
    def run_backtest(self, name: str = "RL Agent") -> Dict:
        """Run backtest on the environment"""
        print(f"Running backtest for {name}...")
        
        state, _ = self.env.reset()
        done = False
        
        portfolio_values = [self.env.initial_balance]
        weights_history = []
        daily_returns = []
        
        while not done:
            # Get action from agent
            action = self.agent.select_action(state, add_noise=False)
            next_state, reward, terminated, truncated, info = self.env.step(action)
            done = terminated or truncated
            
            portfolio_values.append(info['portfolio_value'])
            weights_history.append(info['weights'])
            daily_returns.append(info['portfolio_return'])
            
            state = next_state
        
        # Store results
        result = {
            'name': name,
            'portfolio_values': portfolio_values,
            'weights_history': weights_history,
            'daily_returns': daily_returns,
            'metrics': self.env.get_performance_metrics()
        }
        
        self.results[name] = result
        return result
    
    def run_equal_weight_benchmark(self) -> Dict:
        """Run equal-weight portfolio benchmark"""
        print("Running equal-weight benchmark...")
        
        # Create equal weights
        n_assets = self.env.n_assets
        equal_weights = np.ones(n_assets) / n_assets
        
        state, _ = self.env.reset()
        done = False
        
        portfolio_values = [self.env.initial_balance]
        weights_history = []
        daily_returns = []
        
        while not done:
            # Use equal weights (convert to logits for environment)
            action = np.log(equal_weights + 1e-8)
            next_state, reward, terminated, truncated, info = self.env.step(action)
            done = terminated or truncated
            
            portfolio_values.append(info['portfolio_value'])
            weights_history.append(info['weights'])
            daily_returns.append(info['portfolio_return'])
            
            state = next_state
        
        result = {
            'name': 'Equal Weight',
            'portfolio_values': portfolio_values,
            'weights_history': weights_history,
            'daily_returns': daily_returns,
            'metrics': self.env.get_performance_metrics()
        }
        
        self.results['Equal Weight'] = result
        return result
    
    def run_markowitz_benchmark(self) -> Dict:
        """Run Markowitz mean-variance optimized portfolio"""
        print("Running Markowitz optimization benchmark...")
        
        # Get historical returns for optimization
        returns_data = self.env.data.pct_change().dropna()
        mean_returns = returns_data.mean().values
        cov_matrix = returns_data.cov().values
        
        # Optimize for maximum Sharpe ratio
        n_assets = len(mean_returns)
        
        def neg_sharpe(weights):
            portfolio_return = np.dot(weights, mean_returns) * 252
            portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
            return -portfolio_return / portfolio_std if portfolio_std > 0 else 0
        
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_weights = np.ones(n_assets) / n_assets
        
        result = minimize(
            neg_sharpe,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        optimal_weights = result.x
        
        # Run backtest with optimal weights
        state, _ = self.env.reset()
        done = False
        
        portfolio_values = [self.env.initial_balance]
        weights_history = []
        daily_returns = []
        
        while not done:
            # Use optimal weights
            action = np.log(optimal_weights + 1e-8)
            next_state, reward, terminated, truncated, info = self.env.step(action)
            done = terminated or truncated
            
            portfolio_values.append(info['portfolio_value'])
            weights_history.append(info['weights'])
            daily_returns.append(info['portfolio_return'])
            
            state = next_state
        
        result = {
            'name': 'Markowitz Optimal',
            'portfolio_values': portfolio_values,
            'weights_history': weights_history,
            'daily_returns': daily_returns,
            'metrics': self.env.get_performance_metrics(),
            'optimal_weights': optimal_weights
        }
        
        self.results['Markowitz Optimal'] = result
        return result
    
    def plot_performance_comparison(self, save_path: str = None):
        """Plot performance comparison across strategies"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Portfolio Value Over Time', 'Cumulative Returns',
                          'Drawdown Analysis', 'Performance Metrics'),
            specs=[[{'type': 'scatter'}, {'type': 'scatter'}],
                   [{'type': 'scatter'}, {'type': 'bar'}]]
        )
        
        colors = ['blue', 'green', 'red', 'orange']
        
        # Plot 1: Portfolio Values
        for idx, (name, result) in enumerate(self.results.items()):
            fig.add_trace(
                go.Scatter(
                    y=result['portfolio_values'],
                    name=name,
                    line=dict(color=colors[idx % len(colors)], width=2),
                    legendgroup=name
                ),
                row=1, col=1
            )
        
        # Plot 2: Cumulative Returns
        for idx, (name, result) in enumerate(self.results.items()):
            returns = pd.Series(result['daily_returns'])
            cumulative = (1 + returns).cumprod() - 1
            fig.add_trace(
                go.Scatter(
                    y=cumulative.values,
                    name=name,
                    line=dict(color=colors[idx % len(colors)], width=2),
                    showlegend=False,
                    legendgroup=name
                ),
                row=1, col=2
            )
        
        # Plot 3: Drawdown
        for idx, (name, result) in enumerate(self.results.items()):
            values = pd.Series(result['portfolio_values'])
            cumulative = values / values.iloc[0]
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            
            fig.add_trace(
                go.Scatter(
                    y=drawdown.values,
                    name=name,
                    line=dict(color=colors[idx % len(colors)], width=2),
                    showlegend=False,
                    legendgroup=name
                ),
                row=2, col=1
            )
        
        # Plot 4: Metrics Comparison
        metrics_names = ['Sharpe Ratio', 'Max Drawdown', 'Annual Return']
        for metric_idx, metric in enumerate(['sharpe_ratio', 'max_drawdown', 'annualized_return']):
            y_values = [result['metrics'][metric] for result in self.results.values()]
            fig.add_trace(
                go.Bar(
                    x=list(self.results.keys()),
                    y=y_values,
                    name=metrics_names[metric_idx],
                    showlegend=False
                ),
                row=2, col=2
            )
        
        # Update layout
        fig.update_xaxes(title_text="Days", row=1, col=1)
        fig.update_xaxes(title_text="Days", row=1, col=2)
        fig.update_xaxes(title_text="Days", row=2, col=1)
        fig.update_xaxes(title_text="Strategy", row=2, col=2)
        
        fig.update_yaxes(title_text="Value ($)", row=1, col=1)
        fig.update_yaxes(title_text="Cumulative Return", row=1, col=2)
        fig.update_yaxes(title_text="Drawdown", row=2, col=1)
        fig.update_yaxes(title_text="Value", row=2, col=2)
        
        fig.update_layout(
            height=800,
            title_text="Portfolio Performance Comparison",
            showlegend=True
        )
        
        if save_path:
            fig.write_html(save_path)
        
        fig.show()
    
    def plot_efficient_frontier(self, n_portfolios: int = 5000, save_path: str = None):
        """Plot efficient frontier and mark strategy positions"""
        print("Generating efficient frontier...")
        
        # Get historical data
        returns_data = self.env.data.pct_change().dropna()
        mean_returns = returns_data.mean().values * 252
        cov_matrix = returns_data.cov().values * 252
        n_assets = len(mean_returns)
        
        # Generate random portfolios
        portfolio_returns = []
        portfolio_volatilities = []
        
        for _ in range(n_portfolios):
            weights = np.random.random(n_assets)
            weights /= np.sum(weights)
            
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            portfolio_returns.append(portfolio_return)
            portfolio_volatilities.append(portfolio_vol)
        
        # Create plot
        fig = go.Figure()
        
        # Plot random portfolios (efficient frontier cloud)
        fig.add_trace(go.Scatter(
            x=portfolio_volatilities,
            y=portfolio_returns,
            mode='markers',
            marker=dict(
                size=3,
                color=np.array(portfolio_returns) / np.array(portfolio_volatilities),
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Sharpe Ratio")
            ),
            name='Random Portfolios',
            showlegend=True
        ))
        
        # Plot strategy positions
        colors_map = {'RL Agent': 'red', 'Equal Weight': 'blue', 
                     'Markowitz Optimal': 'green'}
        
        for name, result in self.results.items():
            metrics = result['metrics']
            fig.add_trace(go.Scatter(
                x=[metrics['volatility']],
                y=[metrics['annualized_return']],
                mode='markers+text',
                marker=dict(size=15, color=colors_map.get(name, 'orange'), 
                           symbol='star', line=dict(width=2, color='white')),
                text=[name],
                textposition="top center",
                name=name,
                showlegend=True
            ))
        
        fig.update_layout(
            title="Efficient Frontier with Strategy Positions",
            xaxis_title="Volatility (Annual)",
            yaxis_title="Expected Return (Annual)",
            hovermode='closest',
            height=600
        )
        
        if save_path:
            fig.write_html(save_path)
        
        fig.show()
    
    def plot_weights_evolution(self, save_path: str = None):
        """Plot how portfolio weights evolve over time"""
        fig, axes = plt.subplots(len(self.results), 1, 
                                figsize=(15, 4 * len(self.results)))
        
        if len(self.results) == 1:
            axes = [axes]
        
        for idx, (name, result) in enumerate(self.results.items()):
            weights_df = pd.DataFrame(result['weights_history'], 
                                     columns=self.env.tickers)
            
            axes[idx].stackplot(range(len(weights_df)), 
                               *[weights_df[col] for col in weights_df.columns],
                               labels=weights_df.columns,
                               alpha=0.8)
            axes[idx].set_title(f'{name} - Portfolio Weights Over Time')
            axes[idx].set_xlabel('Days')
            axes[idx].set_ylabel('Weight')
            axes[idx].legend(loc='upper left', bbox_to_anchor=(1, 1))
            axes[idx].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def generate_performance_report(self) -> pd.DataFrame:
        """Generate comprehensive performance report"""
        report_data = []
        
        for name, result in self.results.items():
            metrics = result['metrics']
            report_data.append({
                'Strategy': name,
                'Total Return (%)': metrics['total_return'] * 100,
                'Annual Return (%)': metrics['annualized_return'] * 100,
                'Volatility (%)': metrics['volatility'] * 100,
                'Sharpe Ratio': metrics['sharpe_ratio'],
                'Max Drawdown (%)': metrics['max_drawdown'] * 100,
                'Final Value ($)': metrics['final_value']
            })
        
        df = pd.DataFrame(report_data)
        df = df.set_index('Strategy')
        
        return df
