# 🚀 QUICK START GUIDE

## Get Running in 60 Seconds!

### Windows Users

1. **Double-click** `start.bat`
2. **Wait** for installation (first time only)
3. **Open browser** to `http://localhost:5000`
4. **Done!** 🎉

### Alternative (Windows Command Prompt)

```cmd
start.bat
```

---

### Linux/Mac Users

```bash
chmod +x start.sh
./start.sh
```

Or manually:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

---

## What You'll See

### 1. **Dashboard Loads** ⚡
- Animated cyberpunk interface
- Glowing neon effects
- Real-time metrics

### 2. **Configure Training** ⚙️
Navigate to "Training" section:
- Episodes: `200` (recommended)
- Learning Rate: `0.0001`
- Risk Penalty: `0.5`
- ✅ Enable HER
- ✅ Enable Twin Critics

### 3. **Click "START TRAINING"** 🎮
Watch the magic happen:
- Live progress bar
- Real-time metrics
- Training logs
- Chart updates

### 4. **View Results** 📊
- Portfolio allocation
- Performance charts
- Benchmark comparison
- Efficient frontier

---

## Quick Tips

### First Time Running?
- Initial setup takes ~30 seconds
- Dependencies auto-install
- Browser opens to dashboard

### Training Speed
- **Quick Test**: 10 episodes (~1 min)
- **Full Training**: 200 episodes (~30 min)
- **Production**: 500+ episodes (1+ hour)

### Best Performance
- Close other apps
- Use Chrome/Firefox
- Enable GPU if available

---

## Keyboard Shortcuts

- `Ctrl+C` - Stop Flask server
- `F5` - Refresh dashboard
- `Ctrl+Shift+I` - Open DevTools

---

## Common Issues

**Port 5000 in use?**
```python
# Edit app.py, change:
app.run(port=8000)  # Use port 8000 instead
```

**Slow loading?**
- Check internet connection (downloads fonts/CDN)
- Clear browser cache

**Charts not showing?**
- Verify JavaScript enabled
- Check browser console for errors

---

## Next Steps

1. ✅ Start the server
2. ✅ Run quick test (10 episodes)
3. ✅ Explore visualizations
4. ✅ Try full training (200 episodes)
5. ✅ Experiment with config

---

## Need Help?

1. Check `README.md` for detailed docs
2. Review troubleshooting section
3. Check Flask console for errors
4. Verify all dependencies installed

---

**Enjoy your cyberpunk trading dashboard! 🌃📈**
