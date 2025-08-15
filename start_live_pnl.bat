@echo off
echo Starting Alpaca-Synced Live P&L Monitor in External Window...
cd /d "%~dp0"

REM Activate virtual environment and run live P&L monitor
call .venv\Scripts\activate.bat
python scripts\live_pnl_external.py

pause
