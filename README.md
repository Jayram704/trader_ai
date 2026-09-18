# 🚀 RL Portfolio Trader 

**AI-Powered Portfolio Management with Beautiful Real-Time Dashboard**

A production-ready web application featuring Deep Reinforcement Learning for automated portfolio allocation with live training visualization, interactive charts, and modern glassmorphism UI.

![Dashboard Preview](https://via.placeholder.com/1200x600/667eea/ffffff?text=Beautiful+Dashboard+UI)

---

## ✨ Features

### 🎨 **Modern UI/UX**
- **Glassmorphism Design** - Beautiful frosted glass effects
- **Smooth Animations** - Fluid transitions and micro-interactions
- **Real-Time Updates** - Live training progress via WebSockets
- **Responsive Layout** - Works on desktop, tablet, and mobile
- **Dark Theme** - Eye-friendly gradient backgrounds

### 🤖 **AI/ML Capabilities**
- **DDPG Algorithm** - Twin critics for stable learning
- **Portfolio Optimization** - Maximizes Sharpe ratio (>1.5 target)
- **Risk Management** - Constrains max drawdown (<15%)
- **Multi-Asset Support** - Stocks + Crypto (up to 10 assets)
- **Adaptive Learning** - No price predictions required

### 📊 **Interactive Visualizations**
- **Real-Time Charts** - Episode rewards, Sharpe ratio evolution
- **Portfolio Allocation** - Dynamic doughnut chart
- **Performance Metrics** - Live updates during training
- **Activity Log** - Detailed training progress
- **Backtest Results** - Historical performance analysis

### 🔧 **Technical Stack**
- **Backend**: Flask + SocketIO (Python 3.8+)
- **Frontend**: HTML5 + CSS3 + Vanilla JS
- **ML Framework**: PyTorch
- **Charts**: Chart.js
- **Data**: Yahoo Finance API

---

## 📁 Project Structure

```
rl_trader_web/
├── backend/
│   ├── app.py              # Flask server + WebSocket
│   ├── trading_env.py      # Gymnasium environment
│   └── ddpg_agent.py       # DDPG implementation
├── frontend/
│   ├── templates/
│   │   └── index.html      # Main dashboard
│   └── static/
│       ├── css/
│       │   └── style.css   # Glassmorphism styles
│       └── js/
│           └── app.js      # Interactive functionality
├── models/                 # Saved models (created on training)
├── data/                   # Market data cache
├── requirements.txt        # Python dependencies
├── setup_windows.bat       # Windows setup script
└── README.md              # This file
```

---

## 🚀 Quick Start (Windows)

### **Method 1: Automated Setup (Recommended)**

1. **Download and Extract** the project folder
2. **Double-click** `setup_windows.bat`
3. **Wait** for setup to complete
4. **Run** the application:
   ```cmd
   venv\Scripts\activate
   python backend\app.py
   ```
5. **Open** your browser to `http://localhost:5000`

### **Method 2: Manual Setup**

```cmd
# 1. Open Command Prompt in project folder
cd rl_trader_web

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the server
python backend\app.py
```

Then open: `http://localhost:5000`

---

## 💻 VS Code Setup

### **Recommended Extensions**
1. Python (Microsoft)
2. Pylance
3. Live Server (for frontend dev)
4. Better Comments

### **Open in VS Code**
```cmd
code .
```

### **VS Code Tasks**
Create `.vscode/tasks.json`:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run Flask Server",
            "type": "shell",
            "command": "venv\\Scripts\\activate && python backend\\app.py",
            "problemMatcher": []
        }
    ]
}
```

Run with: `Ctrl+Shift+B`

---

## 🎯 How to Use

### **1. Configure Training**
- Select **Assets** (stocks/crypto)
- Set **Episodes** (10-500)
- Choose **Date Range**
- Set **Initial Balance**

### **2. Start Training**
- Click **"Start Training"** button
- Watch **real-time progress** in dashboard
- Monitor **Sharpe ratio** and **drawdown**
- View **live charts** updating

### **3. Monitor Performance**
- **Episode Rewards** - Training progress
- **Sharpe Ratio** - Risk-adjusted returns
- **Max Drawdown** - Risk control
- **Portfolio Value** - Total value

### **4. Run Backtest**
- Click **"Run Backtest"** after training
- View **historical performance**
- See **portfolio allocation**
- Analyze **metrics**

---

## 📊 Dashboard Overview

### **Control Panel**
Configure training parameters and start/stop training

### **Training Progress**
- Progress bar with percentage
- Real-time statistics cards
- Current episode tracking

### **Charts Section**
- **Episode Rewards**: Training convergence
- **Sharpe Ratio**: Performance evolution

### **Portfolio Allocation**
- Doughnut chart visualization
- Detailed weight breakdown

### **Activity Log**
- Timestamped events
- Training milestones
- Error messages

---

## 🎨 UI Customization

### **Colors** (in `style.css`)
```css
:root {
    --primary: #667eea;      /* Main color */
    --secondary: #764ba2;    /* Accent */
    --accent: #f093fb;       /* Highlights */
}
```

### **Animations**
All animations use CSS3 for smooth 60fps performance:
- Fade in/out
- Slide transitions
- Floating shapes
- Progress animations

---

## 🔍 API Endpoints

### **Status**
```
GET /api/status
Returns: Server status, device info
```

### **Start Training**
```
POST /api/start_training
Body: { tickers, episodes, start_date, end_date, initial_balance }
Returns: Training status
```

### **Stop Training**
```
POST /api/stop_training
Returns: Stop confirmation
```

### **Get Training Stats**
```
GET /api/training_stats
Returns: Complete training statistics
```

### **Run Backtest**
```
POST /api/backtest
Body: { tickers, start_date, end_date }
Returns: Portfolio performance, metrics
```

### **Predict Allocation**
```
POST /api/predict
Body: { tickers, start_date, end_date }
Returns: Optimal portfolio weights
```

---

## 🛡️ WebSocket Events

### **Client → Server**
- `connect`: Establish connection
- `request_status`: Get current status

### **Server → Client**
- `connected`: Connection confirmed
- `training_step`: Real-time step update
- `episode_complete`: Episode finished
- `training_complete`: Training done
- `status_update`: Status changed

---

## 🎓 Training Tips

### **For Best Results:**
1. **Start Small**: Test with 10-20 episodes first
2. **GPU Recommended**: 5-10x faster training
3. **Diversify Assets**: Use 4-8 different assets
4. **Monitor Sharpe**: Target >1.5 for good performance
5. **Control Risk**: Ensure drawdown <15%

### **Typical Training Times:**
- **CPU**: 30-60 minutes (100 episodes)
- **GPU**: 5-10 minutes (100 episodes)

---

## 🐛 Troubleshooting

### **Server won't start**
```cmd
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### **Charts not loading**
- Clear browser cache
- Check browser console (F12)
- Ensure Chart.js loaded

### **WebSocket disconnects**
- Check firewall settings
- Try different port in `app.py`
- Restart server

### **Training errors**
- Verify internet connection (for data download)
- Check date range validity
- Ensure sufficient assets selected

---

## 🚀 Performance Optimization

### **Backend**
- Enable GPU: Set `CUDA_VISIBLE_DEVICES=0`
- Increase batch size (if GPU memory allows)
- Use data caching

### **Frontend**
- Chart update throttling (already implemented)
- Lazy load large datasets
- WebWorker for heavy computations

---

## 📈 Advanced Usage

### **Custom Assets**
Edit asset selection in frontend or backend:
```python
tickers = ['AAPL', 'TSLA', 'NVDA', 'AMD', 'BTC-USD']
```

### **Hyperparameter Tuning**
Modify in `ddpg_agent.py`:
```python
lr_actor=1e-4,      # Actor learning rate
lr_critic=3e-4,     # Critic learning rate
gamma=0.99,         # Discount factor
tau=0.005           # Soft update rate
```

### **Risk Penalty**
Adjust in `trading_env.py`:
```python
risk_penalty=0.5    # Higher = more conservative
```

---

## 📝 License

MIT License - Free to use, modify, and distribute

---

## 🙏 Acknowledgments

- **PyTorch** - Deep learning framework
- **Flask** - Web framework
- **Chart.js** - Beautiful charts
- **Socket.IO** - Real-time communication
- **Yahoo Finance** - Market data

---

## 📞 Support

Issues or questions? Check the code comments or create a GitHub issue.

---

**Built with ❤️ for Windows + VS Code**

*Happy Trading! 📈🚀*
