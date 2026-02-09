@echo off
echo ========================================
echo RL PORTFOLIO TRADER - WEB UI
echo ========================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies if needed
echo Checking dependencies...
pip install -q -r requirements.txt
echo.

REM Start Flask server
echo Starting Flask server...
echo Dashboard will open at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
python app.py

pause
