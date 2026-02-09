@echo off
REM RL Portfolio Trader - Windows Setup Script

echo ==================================
echo RL Portfolio Trader - Setup
echo ==================================
echo.

REM Check Python
echo Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    echo Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip -q
echo pip upgraded
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt -q
echo Dependencies installed
echo.

REM Create directories
echo Creating project directories...
if not exist data mkdir data
if not exist results mkdir results
if not exist tests mkdir tests
echo Directories created
echo.

REM Verify installation
echo Verifying installation...
python -c "import torch; import numpy; import pandas; import gymnasium; print('All core packages imported successfully')"
echo.

REM Check GPU
echo Checking GPU availability...
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')"
echo.

echo ==================================
echo Setup Complete!
echo ==================================
echo.
echo Next steps:
echo 1. Activate environment: venv\Scripts\activate.bat
echo 2. Train model: python train.py --episodes 200 --use_her
echo 3. Evaluate: jupyter notebook notebooks\evaluation.ipynb
echo.
echo See QUICKSTART.md for detailed instructions.
echo.
pause
