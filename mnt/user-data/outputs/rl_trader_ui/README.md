# 🚀 RL Portfolio Trader - Web UI

**Beautiful, Interactive Dashboard for Deep Reinforcement Learning Trading**

A cyberpunk-themed web interface for monitoring and controlling your RL trading agent in real-time. Features live training visualization, portfolio analytics, and performance tracking with stunning animations.

![Dashboard Preview](https://via.placeholder.com/1200x600/0a0a0f/00f3ff?text=RL+Portfolio+Trader+Dashboard)

---

## ✨ Features

### 🎨 **Stunning Cyberpunk UI**
- Neon color scheme with cyan/magenta accents
- Animated grid background with parallax scrolling
- Glitch effects on text
- Smooth hover states and micro-interactions
- Responsive design for all screen sizes

### 📊 **Real-Time Training Monitoring**
- Live episode progress tracking
- Real-time metrics updates (rewards, losses)
- Interactive training logs
- Progress bar with completion percentage
- Start/stop training controls

### 📈 **Advanced Visualizations**
- **Portfolio Value Chart**: Compare RL agent vs benchmarks
- **Sharpe Ratio Progression**: Track performance over episodes
- **Drawdown Analysis**: Monitor risk metrics
- **Efficient Frontier**: Visualize risk-return tradeoff
- All charts powered by Chart.js with custom cyberpunk styling

### 💼 **Portfolio Management**
- Real-time weight allocation bars
- Asset performance table
- Contribution analysis
- 10 assets (stocks + crypto)

### ⚡ **High Performance**
- Server-Sent Events (SSE) for live updates
- Efficient data streaming
- Minimal latency
- Smooth 60fps animations

---

## 🛠️ Tech Stack

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Custom cyberpunk design system
- **Vanilla JavaScript** - No framework bloat
- **Chart.js** - Beautiful charts
- **Google Fonts** - Orbitron & JetBrains Mono

### Backend
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin requests
- **Server-Sent Events** - Real-time streaming
- **NumPy/Pandas** - Data processing
- **PyTorch** - RL model backend

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip
- Modern web browser (Chrome, Firefox, Edge)

### Quick Start

```bash
# 1. Clone/navigate to project
cd rl_trader_ui

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
python app.py

# 4. Open browser
# Navigate to: http://localhost:5000
```

### Full Setup (Windows)

```cmd
# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Install
pip install -r requirements.txt

# Run
python app.py
```

### Full Setup (Linux/Mac)

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install
pip install -r requirements.txt

# Run
python app.py
```

---

## 🎮 Usage

### 1. **Access Dashboard**
Open your browser to `http://localhost:5000`

### 2. **Configure Training**
- Set number of episodes (10-1000)
- Adjust learning rate
- Set risk penalty (0-1)
- Enable/disable features:
  - ✅ Hindsight Experience Replay (HER)
  - ✅ Twin Critics (TD3)

### 3. **Start Training**
Click **"START TRAINING"** button
- Watch real-time progress
- Monitor metrics live
- View training logs
- Stop anytime

### 4. **Analyze Performance**
Navigate through sections:
- **Dashboard**: Key metrics at a glance
- **Training**: Live monitoring and control
- **Backtest**: Historical performance
- **Portfolio**: Current allocation

---

## 🎨 Design System

### Color Palette
```css
--neon-cyan:     #00f3ff   /* Primary accent */
--neon-magenta:  #ff006e   /* Secondary accent */
--neon-yellow:   #ffbe0b   /* Warning/highlight */
--electric-blue: #3a86ff   /* Links/interactive */
--deep-purple:   #8338ec   /* Gradients */
--success:       #00ff88   /* Positive metrics */
--error:         #ff3864   /* Negative metrics */
```

### Typography
- **Display**: Orbitron (headings, numbers)
- **Body**: JetBrains Mono (text, code)

### Components
- **Cards**: Glass-morphism with blur
- **Buttons**: Gradient with glow effects
- **Inputs**: Neon borders with focus glow
- **Charts**: Custom theme with gradients

---

## 🔧 Configuration

### Backend API Endpoints

```python
GET  /                    # Dashboard page
GET  /api/status          # Training status
POST /api/train           # Start training
POST /api/train/stop      # Stop training
GET  /api/train/stream    # SSE stream
GET  /api/portfolio       # Portfolio data
GET  /api/performance     # Performance metrics
GET  /api/backtest        # Backtest results
```

### Training Config

```javascript
{
  episodes: 200,          // Number of episodes
  learningRate: 0.0001,   // Actor learning rate
  riskPenalty: 0.5,       // Risk penalty coefficient
  useHER: true,           // Use HER
  twinCritics: true       // Use twin critics
}
```

---

## 📊 Metrics Explained

### **Sharpe Ratio**
- Measures risk-adjusted returns
- Target: **>1.5**
- Formula: (Return - Risk-Free Rate) / Volatility
- Higher is better

### **Max Drawdown**
- Largest peak-to-trough decline
- Target: **<15%**
- Measures downside risk
- Lower absolute value is better

### **Annual Return**
- Annualized portfolio return
- Target: **>10%**
- Higher is better

### **Volatility**
- Standard deviation of returns
- Measures risk
- Lower is generally better (for same return)

---

## 🎯 Key Features Explained

### **Real-Time Training**
The UI connects to Flask backend via Server-Sent Events (SSE):
1. User starts training
2. Backend begins RL training loop
3. Every episode completion sends update
4. Frontend updates charts/metrics instantly

### **Chart Animations**
All charts use Chart.js with custom config:
- Smooth line transitions
- Hover tooltips
- Responsive sizing
- Cyberpunk color scheme

### **Portfolio Weights**
Dynamic visualization of asset allocation:
- Animated progress bars
- Real-time updates
- Color-coded by performance
- Sortable table view

---

## 🚀 Performance Tips

### Frontend Optimization
- Charts use `update('none')` for instant updates
- Debounced scroll events
- CSS transforms for smooth animations
- Minimal DOM manipulation

### Backend Optimization
- Threaded training execution
- Queue-based event streaming
- Efficient numpy operations
- Cached data where possible

---

## 🎨 Customization

### Change Theme Colors

Edit `static/css/main.css`:

```css
:root {
    --neon-cyan: #YOUR_COLOR;
    --neon-magenta: #YOUR_COLOR;
    /* ... */
}
```

### Add New Charts

1. Add canvas to `templates/index.html`
2. Create chart in `static/js/charts.js`
3. Update data stream handler

### Modify Layout

Edit grid layouts in CSS:

```css
.panel-grid {
    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
}
```

---

## 🐛 Troubleshooting

### **Server won't start**
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000   # Windows
lsof -i :5000                  # Linux/Mac

# Use different port
python app.py --port 8000
```

### **Charts not showing**
- Check browser console for errors
- Verify Chart.js CDN is loaded
- Clear browser cache

### **Training not connecting**
- Verify Flask server is running
- Check browser console for SSE errors
- Firewall may block SSE connection

### **Slow performance**
- Reduce training visualization frequency
- Lower chart data points
- Check CPU/memory usage

---

## 📁 Project Structure

```
rl_trader_ui/
├── app.py                      # Flask backend
├── requirements.txt            # Dependencies
├── backend/                    # RL training code
│   ├── trading_env.py         # Gymnasium environment
│   ├── ddpg_agent.py          # DDPG implementation
│   ├── trainer.py             # Training loop
│   └── backtester.py          # Backtesting
├── templates/
│   └── index.html             # Main dashboard
├── static/
│   ├── css/
│   │   └── main.css           # Cyberpunk theme
│   └── js/
│       ├── main.js            # Core functionality
│       ├── charts.js          # Chart.js config
│       ├── training.js        # API integration
│       └── animations.js      # UI effects
└── README.md                  # This file
```

---

## 🎓 Learning Resources

### Understanding the Code
- **Flask SSE**: Real-time browser updates
- **Chart.js**: Interactive visualizations
- **CSS Grid**: Modern layouts
- **Vanilla JS**: No framework needed

### RL Trading Concepts
- DDPG algorithm
- Portfolio optimization
- Risk metrics (Sharpe, Drawdown)
- Efficient frontier

---

## 🤝 Contributing

Ideas for improvements:
- [ ] Add dark/light theme toggle
- [ ] Export charts as images
- [ ] Save/load training configs
- [ ] Historical comparison view
- [ ] Mobile app version
- [ ] 3D visualizations

---

## 📝 License

MIT License - see LICENSE file

---

## 🙏 Acknowledgments

- Chart.js for beautiful charts
- Flask for simple backend
- Google Fonts for typography
- Inspired by cyberpunk aesthetics

---

## 📞 Support

Having issues?
1. Check troubleshooting section
2. Review console errors
3. Verify dependencies installed
4. Check Flask server logs

---

**Built with 💙 for the future of algorithmic trading**

*Enjoy trading in the cyber future! 🚀📈*
