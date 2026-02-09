#!/bin/bash

# RL Portfolio Trader - Setup Script
# Automates environment setup and dependency installation

set -e  # Exit on error

echo "=================================="
echo "RL Portfolio Trader - Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip -q
echo "✓ pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt -q
echo "✓ Dependencies installed"

# Create necessary directories
echo ""
echo "Creating project directories..."
mkdir -p data
mkdir -p results
mkdir -p tests
echo "✓ Directories created"

# Verify installation
echo ""
echo "Verifying installation..."
python3 -c "import torch; import numpy; import pandas; import gymnasium; print('✓ All core packages imported successfully')"

# Check GPU availability
echo ""
echo "Checking GPU availability..."
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')"

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Activate environment: source venv/bin/activate"
echo "2. Train model: python train.py --episodes 200 --use_her"
echo "3. Evaluate: jupyter notebook notebooks/evaluation.ipynb"
echo ""
echo "See QUICKSTART.md for detailed instructions."
echo ""
