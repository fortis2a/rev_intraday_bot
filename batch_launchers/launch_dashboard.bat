@echo off
REM Interactive Trading Dashboard Launcher
REM =====================================
REM
REM Quick launcher for the Interactive Trading Dashboard
REM This batch file starts the dashboard with proper environment setup

echo.
echo ========================================
echo   Interactive Trading Dashboard
echo ========================================
echo.
echo Starting dashboard...
echo Dashboard will be available at: http://localhost:8050
echo.
echo Press Ctrl+C to stop the dashboard
echo.

REM Launch the dashboard using the Python launcher
python launch_dashboard.py

echo.
echo Dashboard stopped.
pause
