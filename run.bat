@echo off
REM Quick launcher for RL Portfolio Trader

echo =========================================
echo Starting RL Portfolio Trader...
echo =========================================
echo.

REM Check if venv exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup_windows.bat first
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Start server
echo Starting Flask server...
echo.
echo Dashboard will be available at:
echo   http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python backend\app.py

pause
