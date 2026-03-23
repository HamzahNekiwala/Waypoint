@echo off
echo ==========================================
echo         WAYPOINT - Travel Hub
echo ==========================================
echo.
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit
)
echo.
echo Checking Flask installation...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Flask not found. Installing Flask...
    pip install flask
) else (
    echo Flask is already installed.
)
echo.
echo Starting Waypoint server...
echo Open your browser and go to: http://127.0.0.1:5000
echo Press CTRL+C to stop the server.
echo.
start "" "http://127.0.0.1:5000"
timeout /t 2 >nul
python app.py
pause