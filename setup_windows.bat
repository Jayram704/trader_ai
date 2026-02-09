@echo off
REM RL Portfolio Trader Web - Windows Setup

echo =========================================
echo RL Portfolio Trader - Web Version Setup
echo =========================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)
echo Python found!
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists.
) else (
    python -m venv venv
    echo Virtual environment created!
)
echo.

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt
echo.

REM Create directories
echo Creating project directories...
if not exist models mkdir models
if not exist data mkdir data
echo.

REM Test installation
echo Testing installation...
python -c "import torch; import flask; import flask_socketio; print('All packages imported successfully!')"
echo.

echo =========================================
echo Setup Complete!
echo =========================================
echo.
echo To start the application:
echo   1. Activate environment: venv\Scripts\activate
echo   2. Run server: python backend\app.py
echo   3. Open browser: http://localhost:5000
echo.
pause
