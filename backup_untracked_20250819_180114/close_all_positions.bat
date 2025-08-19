@echo off
REM Close All Positions - Emergency Script
echo.
echo ========================================
echo       🚨 EMERGENCY CLOSE ALL 🚨
echo ========================================
echo.
echo This will close ALL open positions!
echo.

cd /d "%~dp0"
".venv\Scripts\python.exe" emergency_close_all.py

echo.
pause
