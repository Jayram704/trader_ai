"""
Test Script - Verify RL Portfolio Trader Installation
Runs basic tests to ensure everything is working correctly
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing imports...")
    try:
        import numpy as np
        import pandas as pd
        import torch
        import gymnasium as gym
        import yfinance as yf
        import matplotlib.pyplot as plt
        import seaborn as sns
        print("✓ All packages imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_environment():
    """Test trading environment creation"""
    print("\nTesting trading environment...")
    try:
        from trading_env import TradingEnvironment
        
        env = TradingEnvironment(
            tickers=['AAPL', 'MSFT', 'GOOGL'],
            start_date='2023-01-01',
            end_date='2023-06-01',
            initial_balance=100000,
            transaction_cost=0.001
        )
        
        state, _ = env.reset()
        action = env.action_space.sample()
        next_state, reward, terminated, truncated, info = env.step(action)
        
        print(f"  State shape: {state.shape}")
        print(f"  Action shape: {action.shape}")
        print(f"  Reward: {reward:.4f}")
        print("✓ Environment working correctly")
        return True
    except Exception as e:
        print(f"✗ Environment error: {e}")
        return False

def test_agent():
    """Test DDPG agent creation"""
    print("\nTesting DDPG agent...")
    try:
        from ddpg_agent import DDPGAgent
        
        agent = DDPGAgent(
            state_dim=100,
            action_dim=10,
            hidden_dims=[64, 64],
            batch_size=32
        )
        
        import numpy as np
        state = np.random.randn(100)
        action = agent.select_action(state, add_noise=False)
        
        print(f"  Action shape: {action.shape}")
        print(f"  Device: {agent.device}")
        print("✓ Agent working correctly")
        return True
    except Exception as e:
        print(f"✗ Agent error: {e}")
        return False

def test_integration():
    """Test full integration"""
    print("\nTesting integration (agent + environment)...")
    try:
        from trading_env import TradingEnvironment
        from ddpg_agent import DDPGAgent
        
        env = TradingEnvironment(
            tickers=['AAPL', 'MSFT'],
            start_date='2023-01-01',
            end_date='2023-03-01',
            initial_balance=100000
        )
        
        agent = DDPGAgent(
            state_dim=env.observation_space.shape[0],
            action_dim=env.action_space.shape[0],
            hidden_dims=[64, 64]
        )
        
        state, _ = env.reset()
        total_reward = 0
        
        for _ in range(10):
            action = agent.select_action(state)
            next_state, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            
            if terminated or truncated:
                break
            
            state = next_state
        
        print(f"  Steps completed: 10")
        print(f"  Total reward: {total_reward:.4f}")
        print("✓ Integration test passed")
        return True
    except Exception as e:
        print(f"✗ Integration error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cuda():
    """Test CUDA availability"""
    print("\nTesting GPU/CUDA...")
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        
        if cuda_available:
            print(f"✓ CUDA available")
            print(f"  Device: {torch.cuda.get_device_name(0)}")
            print(f"  CUDA version: {torch.version.cuda}")
        else:
            print("⚠ CUDA not available (using CPU)")
            print("  Training will be slower but still functional")
        
        return True
    except Exception as e:
        print(f"✗ CUDA test error: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("RL PORTFOLIO TRADER - INSTALLATION TEST")
    print("="*60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Trading Environment", test_environment),
        ("DDPG Agent", test_agent),
        ("Integration", test_integration),
        ("GPU/CUDA", test_cuda)
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n✗ {name} failed with exception: {e}")
            results[name] = False
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:.<40} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("\nYour installation is ready!")
        print("Next steps:")
        print("  1. Train model: python train.py --episodes 10")
        print("  2. Full training: python train.py --episodes 200 --use_her")
        print("  3. Evaluate: jupyter notebook notebooks/evaluation.ipynb")
    else:
        print("✗ SOME TESTS FAILED")
        print("\nPlease check the error messages above.")
        print("Common fixes:")
        print("  1. Reinstall dependencies: pip install -r requirements.txt")
        print("  2. Check Python version: python --version (need 3.8+)")
        print("  3. Install CUDA drivers for GPU support")
    print("="*60)

if __name__ == '__main__':
    main()
