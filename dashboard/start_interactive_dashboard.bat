@echo off
echo ===========================================
echo   Interactive Trading Dashboard Launcher
echo ===========================================
echo.
echo Starting dashboard server...
echo Dashboard will be available at: http://localhost:8050
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
call ".venv\Scripts\activate.bat"
python interactive_dashboard.py

pause
