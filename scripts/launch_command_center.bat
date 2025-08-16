@echo off
echo.
echo ==========================================
echo   🚀 SCALPING COMMAND CENTER LAUNCHER
echo ==========================================
echo.

:: Change to project directory
cd /d "c:\Users\will7\OneDrive - Sygma Data Analytics\Stock Trading\Scalping Bot System"

:: Activate virtual environment
echo 📦 Activating virtual environment...
call .venv\Scripts\activate.bat

:: Check if activation was successful
if %errorlevel% neq 0 (
    echo ❌ Failed to activate virtual environment
    echo Creating new virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
)

:: Install dependencies if needed
echo 📋 Checking dependencies...
python -c "import psutil" 2>nul || (
    echo Installing psutil...
    pip install psutil
)

:: Launch Command Center
echo.
echo 🚀 Launching Scalping Command Center...
echo ==========================================
echo.
python scripts\scalping_command_center.py

:: Keep window open if there's an error
if %errorlevel% neq 0 (
    echo.
    echo ❌ Command Center exited with error
    pause
)
