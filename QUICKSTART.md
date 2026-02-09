# 🚀 Quick Start Guide - RL Portfolio Trader Web

Get up and running in **5 minutes**!

---

## ⚡ Super Quick Start (Windows)

### **Option 1: Double-Click Setup (Easiest)**

1. **Download** and extract the project folder
2. **Double-click** `setup_windows.bat` → Wait for completion
3. **Double-click** `run.bat` → Opens server
4. **Open browser** → Go to `http://localhost:5000`
5. **Start trading!** 🎉

### **Option 2: VS Code** (Recommended for developers)

1. **Open folder** in VS Code (`code .`)
2. **Open terminal** (`Ctrl+``)
3. **Run setup**:
   ```cmd
   setup_windows.bat
   ```
4. **Press F5** to start server
5. **Open** `http://localhost:5000`

---

## 📋 Step-by-Step First Use

### **1. Initial Setup (One Time Only)**

```cmd
# Open Command Prompt in project folder
cd rl_trader_web

# Run setup script
setup_windows.bat

# This will:
# ✓ Create virtual environment
# ✓ Install all dependencies
# ✓ Create necessary folders
# ✓ Test installation
```

**⏱️ Time: 3-5 minutes**

### **2. Start the Server**

```cmd
# Activate virtual environment
venv\Scripts\activate

# Run Flask server
python backend\app.py
```

**OR** simply double-click `run.bat`

**Expected Output:**
```
============================================
RL PORTFOLIO TRADER - WEB SERVER
============================================

Server starting...
Dashboard: http://localhost:5000
API: http://localhost:5000/api/

Press Ctrl+C to stop
============================================
```

### **3. Open Dashboard**

- Open your browser
- Go to: `http://localhost:5000`
- You'll see the beautiful dashboard! ✨

---

## 🎯 Your First Training Session

### **Step 1: Configure Assets**

In the **Training Configuration** panel:
- Select 3-5 stocks (e.g., AAPL, MSFT, GOOGL)
- Tip: Start with well-known stocks for first test

### **Step 2: Set Parameters**

- **Episodes**: `20` (for quick test)
- **Start Date**: `2022-01-01`
- **End Date**: `2023-01-01`
- **Initial Balance**: `100000`

### **Step 3: Start Training**

- Click **"Start Training"** button
- Watch the magic happen! 🪄
  - Progress bar fills up
  - Charts update in real-time
  - Activity log shows progress
  - Stats update live

### **Step 4: Monitor Results**

Watch these metrics:
- **Sharpe Ratio** → Target: >1.5
- **Max Drawdown** → Target: <15%
- **Portfolio Value** → Should increase!

**⏱️ Training Time:**
- 20 episodes: ~2-5 minutes (CPU)
- 100 episodes: ~10-30 minutes (CPU)

---

## 📊 What You'll See

### **Dashboard Components**

1. **Control Panel** (Top)
   - Asset selection
   - Training parameters
   - Action buttons

2. **Progress Section**
   - Real-time progress bar
   - Live statistics cards
   - Current episode/metrics

3. **Charts** (Middle)
   - Episode Rewards (line chart)
   - Sharpe Ratio Evolution (line chart)
   - Both update live during training!

4. **Portfolio Allocation**
   - Colorful doughnut chart
   - Percentage breakdown
   - Updates after backtest

5. **Activity Log** (Bottom)
   - Timestamped events
   - Training progress
   - Success/error messages

---

## 🎨 Cool Features to Try

### **Real-Time Updates**
- Watch charts update as training progresses
- See live portfolio value changes
- Monitor risk metrics in real-time

### **Interactive Charts**
- Hover over points for details
- Zoom in/out on timeline
- Beautiful animations

### **Run Backtest**
- After training, click "Run Backtest"
- See historical performance
- View optimal portfolio allocation

### **Toast Notifications**
- Success messages slide in from right
- Beautiful glassmorphism design
- Auto-dismiss after 3 seconds

---

## 🔧 Customization Tips

### **Change Colors**

Edit `frontend/static/css/style.css`:
```css
:root {
    --primary: #667eea;    /* Change this! */
    --secondary: #764ba2;  /* And this! */
    --accent: #f093fb;     /* And this! */
}
```

### **Add More Assets**

Edit `frontend/templates/index.html`:
```html
<select id="assetSelect" multiple>
    <option value="TSLA">Tesla</option>
    <option value="NVDA">NVIDIA</option>
    <!-- Add more here! -->
</select>
```

### **Adjust Training Speed**

Edit `backend/app.py` - change update frequency:
```python
if step % 10 == 0:  # Change 10 to higher number
    socketio.emit('training_step', {...})
```

---

## 🐛 Common Issues & Fixes

### **Issue: "Python not found"**
**Fix:**
1. Install Python 3.8+ from python.org
2. Check "Add to PATH" during installation
3. Restart Command Prompt

### **Issue: "Port 5000 already in use"**
**Fix:**
Edit `backend/app.py`, last line:
```python
socketio.run(app, port=5001)  # Changed from 5000
```

### **Issue: "Module not found"**
**Fix:**
```cmd
venv\Scripts\activate
pip install -r requirements.txt --upgrade
```

### **Issue: Charts not showing**
**Fix:**
1. Hard refresh browser (Ctrl+F5)
2. Clear cache
3. Check browser console (F12) for errors

### **Issue: Training very slow**
**Tips:**
- Reduce episodes (try 10-20 first)
- Use fewer assets (3-4 optimal)
- Shorter date range
- Consider GPU if available

---

## 💡 Pro Tips

### **For Faster Training:**
```cmd
# If you have NVIDIA GPU:
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### **For Better Results:**
- Use 4-6 diverse assets
- Train for 100+ episodes
- Check Sharpe ratio trends
- Monitor drawdown closely

### **For Development:**
- Use VS Code for best experience
- Install Python extension
- Use F5 to debug
- Check Output panel for logs

---

## 📱 Next Steps

After your first successful training:

1. **Experiment with assets** - Try different combinations
2. **Increase episodes** - Train for 100-200 episodes
3. **Compare periods** - Test different date ranges
4. **Run backtests** - Analyze performance
5. **Customize UI** - Make it your own!

---

## 🎓 Learning Resources

### **Understanding the Metrics**

- **Sharpe Ratio**: Higher = better risk-adjusted returns
  - <1: Poor
  - 1-2: Good
  - >2: Excellent

- **Max Drawdown**: Maximum portfolio decline
  - Lower = better
  - Target: <15%

- **Portfolio Value**: Total value over time
  - Should trend upward
  - Compare to initial balance

---

## ✅ Success Checklist

- [ ] Setup completed without errors
- [ ] Server starts successfully
- [ ] Dashboard loads in browser
- [ ] Can select assets
- [ ] Training starts and runs
- [ ] Charts update in real-time
- [ ] Training completes successfully
- [ ] Backtest runs and shows results

**All checked? You're ready to trade! 🎉**

---

## 🆘 Need Help?

1. Check error messages in:
   - Browser console (F12)
   - Terminal/Command Prompt
   - Activity Log in dashboard

2. Common solutions:
   - Restart server
   - Refresh browser
   - Reinstall dependencies
   - Check internet connection

3. Still stuck?
   - Read the full README.md
   - Check code comments
   - Review error logs

---

**Happy Trading! 📈🚀**

*Remember: This is for educational purposes. Always do your own research for real trading!*
