@echo off
REM Today's Trading Analysis Report
echo.
echo ========================================
echo       📊 TODAY'S TRADING ANALYSIS
echo ========================================
echo.

cd /d "%~dp0"
".venv\Scripts\python.exe" today_analysis.py

echo.
echo ========================================
echo       📈 ANALYSIS COMPLETE
echo ========================================
echo.
pause
