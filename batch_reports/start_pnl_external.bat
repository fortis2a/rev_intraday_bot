@echo off
echo Starting Live P&L External Monitor...
cd /d "%~dp0"

REM Activate virtual environment and run external P&L monitor
call .venv\Scripts\activate.bat
python scripts\live_pnl_external.py

pause
