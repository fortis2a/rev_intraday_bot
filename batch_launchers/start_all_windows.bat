@echo off
echo Starting All Trading System Components...
cd /d "%~dp0"

REM Start main trading engine in new window
start "Trading Engine" cmd /k "call .venv\Scripts\activate.bat && python core\intraday_engine.py"

REM Wait a moment for engine to start
timeout /t 3

REM Start live P&L monitor in new window
start "Alpaca-Synced P&L Monitor" cmd /k "call .venv\Scripts\activate.bat && python scripts\live_pnl_external.py"

REM Start dashboard/status monitor in new window  
start "Trading Dashboard" cmd /k "call .venv\Scripts\activate.bat && python launcher.py"

echo All components started in separate windows!
pause
