# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Installation (2 min)
```bash
# Clone and setup
git clone <your-repo>
cd rl_trader
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Train Model (1 min setup + runtime)
```bash
# Quick training (10 episodes for testing)
python train.py --episodes 10 --use_her

# Full training (200 episodes, ~30-60 min depending on hardware)
python train.py --episodes 200 --use_her --warmup 10
```

### 3. Evaluate Results (2 min)
```bash
# Open evaluation notebook
jupyter notebook notebooks/evaluation.ipynb

# Run all cells to see:
# - Backtest results (2018-2025)
# - Performance vs benchmarks
# - Efficient frontier
# - Portfolio weights evolution
```

---

## 📊 Expected Outputs

### During Training
```
Episode 10/200
  Avg Reward (10 eps): 0.0189
  Avg Sharpe Ratio: 1.34
  Avg Max Drawdown: -0.18
  Buffer Size: 12450
```

### After Training
Files in `results/`:
- `final_model.pt` - Trained agent weights
- `training_metrics.json` - Performance history
- `training_progress.png` - Training curves

### After Evaluation
Additional files:
- `performance_comparison.html` - Interactive comparison
- `efficient_frontier.html` - Risk-return visualization
- `weights_evolution.png` - Portfolio allocation over time
- `evaluation_summary.txt` - Text report

---

## 🎯 Key Metrics to Watch

| Metric | Target | Good | Excellent |
|--------|--------|------|-----------|
| Sharpe Ratio | >1.5 | 1.5-2.0 | >2.0 |
| Max Drawdown | <15% | 12-15% | <12% |
| Annual Return | >10% | 10-20% | >20% |
| Volatility | <20% | 15-20% | <15% |

---

## 🔧 Troubleshooting

### GPU Not Detected
```python
# Check CUDA availability
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
```

### Out of Memory
Reduce batch size in `src/ddpg_agent.py`:
```python
# Change from 256 to 128
batch_size=128
```

### Poor Performance
- Increase training episodes: `--episodes 500`
- Enable HER: `--use_her`
- Adjust learning rates in `DDPGAgent` initialization
- Increase warmup period: `--warmup 20`

### Data Download Issues
```python
# Test data download manually
import yfinance as yf
data = yf.download(['AAPL', 'MSFT'], start='2023-01-01', end='2024-01-01')
print(data.head())
```

---

## 💡 Tips for Best Results

1. **Start Small**: Test with 10 episodes first to verify setup
2. **Use GPU**: Training is 10-20x faster with CUDA
3. **Monitor Training**: Watch Sharpe ratio - should increase over episodes
4. **Patience**: Full training takes 30-60 minutes
5. **Compare Benchmarks**: RL should outperform equal-weight baseline

---

## 📚 Next Steps

After successful training:

1. **Experiment with Assets**
   - Modify ticker list in `train.py`
   - Try different asset combinations
   - Test sector-specific portfolios

2. **Tune Hyperparameters**
   - Learning rates (actor/critic)
   - Risk penalty coefficient
   - Network architecture

3. **Advanced Features**
   - Implement transaction cost optimization
   - Add constraint handling (sector limits)
   - Multi-period optimization

4. **Production Deployment**
   - Real-time data integration
   - Automated retraining
   - Risk monitoring system

---

## 🆘 Getting Help

1. Check `README.md` for detailed documentation
2. Review `notebooks/evaluation.ipynb` for usage examples
3. Examine training logs in `results/training_metrics.json`
4. Open GitHub issue with error logs

---

**You're all set! Happy training! 🎉**
