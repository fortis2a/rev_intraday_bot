@echo off
REM Quick Trade Closer Script
echo.
echo ========================================
echo         QUICK TRADE CLOSER
echo ========================================
echo.
echo This script will help you close trades
echo.

cd /d "%~dp0"
".venv\Scripts\python.exe" close_trade.py --interactive

pause
