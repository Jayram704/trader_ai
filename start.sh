#!/bin/bash

echo "========================================"
echo "RL PORTFOLIO TRADER - WEB UI"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "Checking dependencies..."
pip install -q -r requirements.txt
echo ""

# Start Flask server
echo "Starting Flask server..."
echo "Dashboard will open at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
python app.py
