@echo off
REM 📱 Real-time PnL Monitor Launcher (Batch file version)
REM Launches live P&L monitoring in external command prompt

title Real-time P&L Monitor

echo 🚀 Starting Real-time P&L Monitor...
echo 📊 Monitor will show live trading performance
echo ⏹️ Press Ctrl+C to stop monitoring
echo ─────────────────────────────────────────────

REM Get the script directory
set SCRIPT_DIR=%~dp0

REM Check if virtual environment exists
if not exist "%SCRIPT_DIR%.venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found
    echo 💡 Please run setup.py first to create the virtual environment
    pause
    exit /b 1
)

REM Launch the live PnL monitor
"%SCRIPT_DIR%.venv\Scripts\python.exe" -c "from utils.live_pnl import show_live_pnl; show_live_pnl()"

if errorlevel 1 (
    echo ❌ Error starting P&L monitor
    pause
)
