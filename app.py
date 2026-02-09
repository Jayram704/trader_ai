"""
Flask Backend - RL Portfolio Trader
Handles training, inference, and real-time updates
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import numpy as np
import json
import os
from threading import Thread
import time

from trading_env import TradingEnvironment
from ddpg_agent import DDPGAgent

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
current_agent = None
current_env = None
training_active = False
training_stats = {
    'episode_rewards': [],
    'sharpe_ratios': [],
    'max_drawdowns': [],
    'portfolio_values': []
}

@app.route('/')
def index():
    """Serve main dashboard"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get current system status"""
    return jsonify({
        'training_active': training_active,
        'model_loaded': current_agent is not None,
        'episodes_completed': len(training_stats['episode_rewards']),
        'device': 'CUDA' if os.environ.get('CUDA_VISIBLE_DEVICES') else 'CPU'
    })

@app.route('/api/config', methods=['GET', 'POST'])
def config():
    """Get or set training configuration"""
    if request.method == 'POST':
        config_data = request.json
        return jsonify({'status': 'success', 'config': config_data})
    
    # Default config
    return jsonify({
        'tickers': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'JPM', 'BAC', 'JNJ', 'PG', 'BTC-USD', 'ETH-USD'],
        'start_date': '2020-01-01',
        'end_date': '2024-01-01',
        'episodes': 100,
        'initial_balance': 100000
    })

@app.route('/api/start_training', methods=['POST'])
def start_training():
    """Start training process"""
    global training_active, current_env, current_agent
    
    if training_active:
        return jsonify({'error': 'Training already in progress'}), 400
    
    config = request.json
    
    # Create environment
    current_env = TradingEnvironment(
        tickers=config.get('tickers', ['AAPL', 'MSFT', 'GOOGL']),
        start_date=config.get('start_date', '2020-01-01'),
        end_date=config.get('end_date', '2023-01-01'),
        initial_balance=config.get('initial_balance', 100000)
    )
    
    # Create agent
    current_agent = DDPGAgent(
        state_dim=current_env.observation_space.shape[0],
        action_dim=current_env.action_space.shape[0]
    )
    
    # Start training in background
    training_thread = Thread(target=train_agent, args=(config,))
    training_thread.daemon = True
    training_thread.start()
    
    return jsonify({'status': 'Training started'})

def train_agent(config):
    """Training loop with real-time updates"""
    global training_active, training_stats
    
    training_active = True
    episodes = config.get('episodes', 100)
    
    for episode in range(episodes):
        state, _ = current_env.reset()
        episode_reward = 0
        done = False
        step = 0
        
        while not done:
            # Select action
            action = current_agent.select_action(state, add_noise=(episode < 10))
            next_state, reward, terminated, truncated, info = current_env.step(action)
            done = terminated or truncated
            
            # Store transition
            current_agent.replay_buffer.push(state, action, reward, next_state, done)
            
            # Train
            if episode >= 10:
                current_agent.train()
            
            episode_reward += reward
            state = next_state
            step += 1
            
            # Send real-time update every 10 steps
            if step % 10 == 0:
                socketio.emit('training_step', {
                    'episode': episode,
                    'step': step,
                    'reward': float(reward),
                    'portfolio_value': float(info['portfolio_value']),
                    'weights': info['weights']
                })
        
        # Episode complete
        metrics = current_env.get_performance_metrics()
        training_stats['episode_rewards'].append(episode_reward)
        training_stats['sharpe_ratios'].append(metrics['sharpe_ratio'])
        training_stats['max_drawdowns'].append(metrics['max_drawdown'])
        training_stats['portfolio_values'].append(metrics['final_value'])
        
        # Send episode summary
        socketio.emit('episode_complete', {
            'episode': episode + 1,
            'total_episodes': episodes,
            'reward': float(episode_reward),
            'sharpe_ratio': float(metrics['sharpe_ratio']),
            'max_drawdown': float(metrics['max_drawdown']),
            'portfolio_value': float(metrics['final_value']),
            'progress': ((episode + 1) / episodes) * 100
        })
        
        # Save checkpoint every 10 episodes
        if (episode + 1) % 10 == 0:
            current_agent.save(f'../models/checkpoint_ep{episode+1}.pt')
    
    # Training complete
    current_agent.save('../models/final_model.pt')
    training_active = False
    
    socketio.emit('training_complete', {
        'message': 'Training completed successfully!',
        'final_sharpe': float(training_stats['sharpe_ratios'][-1]),
        'final_portfolio_value': float(training_stats['portfolio_values'][-1])
    })

@app.route('/api/stop_training', methods=['POST'])
def stop_training():
    """Stop training process"""
    global training_active
    training_active = False
    return jsonify({'status': 'Training stopped'})

@app.route('/api/training_stats')
def get_training_stats():
    """Get training statistics"""
    return jsonify(training_stats)

@app.route('/api/predict', methods=['POST'])
def predict():
    """Get portfolio allocation prediction"""
    if current_agent is None:
        return jsonify({'error': 'No model loaded'}), 400
    
    data = request.json
    tickers = data.get('tickers', ['AAPL', 'MSFT', 'GOOGL'])
    
    # Create temp environment for current state
    temp_env = TradingEnvironment(
        tickers=tickers,
        start_date=data.get('start_date', '2023-01-01'),
        end_date=data.get('end_date', '2024-01-01')
    )
    
    state, _ = temp_env.reset()
    action = current_agent.select_action(state, add_noise=False)
    weights = temp_env._apply_softmax(action)
    
    return jsonify({
        'tickers': tickers,
        'weights': weights.tolist(),
        'allocations': [
            {'ticker': ticker, 'weight': float(weight)} 
            for ticker, weight in zip(tickers, weights)
        ]
    })

@app.route('/api/backtest', methods=['POST'])
def backtest():
    """Run backtest on historical data"""
    if current_agent is None:
        return jsonify({'error': 'No model loaded'}), 400
    
    data = request.json
    
    # Create environment
    env = TradingEnvironment(
        tickers=data.get('tickers', ['AAPL', 'MSFT', 'GOOGL']),
        start_date=data.get('start_date', '2023-01-01'),
        end_date=data.get('end_date', '2024-01-01')
    )
    
    state, _ = env.reset()
    done = False
    
    portfolio_values = [env.initial_balance]
    weights_history = []
    
    while not done:
        action = current_agent.select_action(state, add_noise=False)
        state, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        
        portfolio_values.append(info['portfolio_value'])
        weights_history.append(info['weights'])
    
    metrics = env.get_performance_metrics()
    
    return jsonify({
        'portfolio_values': portfolio_values,
        'weights_history': weights_history,
        'metrics': metrics
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'message': 'Connected to RL Trader Server'})

@socketio.on('request_status')
def handle_status_request():
    """Send current status to client"""
    emit('status_update', {
        'training_active': training_active,
        'episodes_completed': len(training_stats['episode_rewards'])
    })

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('../models', exist_ok=True)
    os.makedirs('../data', exist_ok=True)
    
    print("="*60)
    print("RL PORTFOLIO TRADER - WEB SERVER")
    print("="*60)
    print("\nServer starting...")
    print("Dashboard: http://localhost:5000")
    print("API: http://localhost:5000/api/")
    print("\nPress Ctrl+C to stop")
    print("="*60)
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
