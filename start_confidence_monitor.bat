@echo off
title Real-Time Confidence Monitor
echo 🎯 Starting Real-Time Confidence Monitor...
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo 📊 Monitoring confidence signals for all watchlist stocks
echo 🎯 Shows which stocks exceed 75%% trading threshold with LONG/SHORT directions
echo ⏰ Updates every 10 seconds
echo 📈 Displays best direction (LONG/SHORT) and alternative confidence
echo.

python scripts\confidence_monitor.py

echo.
echo Monitor stopped. Press any key to close window.
pause >nul
