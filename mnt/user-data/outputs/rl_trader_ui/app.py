"""
Flask Backend for RL Portfolio Trader UI
Handles training requests, data streaming, and API endpoints
"""

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import json
import time
import threading
import queue
from datetime import datetime
import numpy as np
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
CORS(app)

# Training state
training_state = {
    'is_running': False,
    'current_episode': 0,
    'total_episodes': 0,
    'metrics': {},
    'config': {}
}

# Event queue for SSE
event_queue = queue.Queue()

# ========================================
# ROUTES
# ========================================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get current training status"""
    return jsonify({
        'is_running': training_state['is_running'],
        'current_episode': training_state['current_episode'],
        'total_episodes': training_state['total_episodes'],
        'metrics': training_state['metrics']
    })

@app.route('/api/train', methods=['POST'])
def start_training():
    """Start training with provided configuration"""
    if training_state['is_running']:
        return jsonify({'error': 'Training already in progress'}), 400
    
    config = request.json
    training_state['config'] = config
    training_state['total_episodes'] = config.get('episodes', 200)
    training_state['current_episode'] = 0
    training_state['is_running'] = True
    
    # Start training in background thread
    thread = threading.Thread(target=run_training, args=(config,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'Training started', 'config': config})

@app.route('/api/train/stop', methods=['POST'])
def stop_training():
    """Stop current training"""
    training_state['is_running'] = False
    return jsonify({'status': 'Training stopped'})

@app.route('/api/train/stream')
def training_stream():
    """Server-Sent Events stream for training updates"""
    def event_stream():
        while True:
            try:
                # Get data from queue
                data = event_queue.get(timeout=1)
                yield f"data: {json.dumps(data)}\n\n"
            except queue.Empty:
                # Send heartbeat
                yield f"data: {json.dumps({'heartbeat': True})}\n\n"
            
            if not training_state['is_running']:
                break
    
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/api/portfolio')
def get_portfolio():
    """Get current portfolio allocation"""
    # Mock data - replace with actual model output
    assets = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'JPM', 'BAC', 'JNJ', 'PG', 'GBTC', 'ETHE']
    weights = np.random.dirichlet(np.ones(10))
    
    return jsonify({
        'assets': assets,
        'weights': weights.tolist(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/performance')
def get_performance():
    """Get performance metrics"""
    return jsonify({
        'sharpe_ratio': 1.64,
        'max_drawdown': -0.132,
        'annual_return': 0.187,
        'volatility': 0.145,
        'total_return': 0.342
    })

@app.route('/api/backtest')
def get_backtest():
    """Get backtest results"""
    days = 500
    dates = [(datetime.now().timestamp() - i * 86400) for i in range(days)][::-1]
    
    portfolio_values = generate_portfolio_data(days, 100000, 0.002)
    benchmark_values = generate_portfolio_data(days, 100000, 0.0015)
    
    return jsonify({
        'dates': dates,
        'portfolio_values': portfolio_values,
        'benchmark_values': benchmark_values
    })

# ========================================
# TRAINING SIMULATION
# ========================================

def run_training(config):
    """Simulate training process"""
    print(f"Starting training with config: {config}")
    
    total_episodes = config.get('episodes', 200)
    learning_rate = config.get('learningRate', 0.0001)
    risk_penalty = config.get('riskPenalty', 0.5)
    
    for episode in range(1, total_episodes + 1):
        if not training_state['is_running']:
            print("Training stopped by user")
            break
        
        # Update state
        training_state['current_episode'] = episode
        
        # Simulate training metrics
        progress = episode / total_episodes
        metrics = {
            'episode': episode,
            'reward': float(np.random.randn() * 0.1),
            'avgReward': float(0.05 * progress + np.random.randn() * 0.02),
            'actorLoss': float(np.random.rand() * 0.5),
            'criticLoss': float(np.random.rand() * 1.0),
            'sharpe': float(0.8 + progress * 1.2 + np.random.randn() * 0.2)
        }
        
        training_state['metrics'] = metrics
        
        # Send update to SSE stream
        try:
            event_queue.put(metrics, timeout=0.1)
        except queue.Full:
            pass
        
        # Simulate episode duration
        time.sleep(0.05)  # Fast simulation
        
        # Log progress
        if episode % 10 == 0:
            print(f"Episode {episode}/{total_episodes} - Reward: {metrics['reward']:.4f}")
    
    training_state['is_running'] = False
    print("Training completed")

def generate_portfolio_data(count, start_value, daily_return):
    """Generate mock portfolio value data"""
    values = [start_value]
    for _ in range(count - 1):
        change = (np.random.randn() - 0.2) * daily_return
        values.append(values[-1] * (1 + change))
    return values

# ========================================
# ERROR HANDLERS
# ========================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ========================================
# MAIN
# ========================================

if __name__ == '__main__':
    print("="*60)
    print("RL PORTFOLIO TRADER - WEB UI")
    print("="*60)
    print("\nStarting Flask server...")
    print("Dashboard: http://localhost:5000")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
