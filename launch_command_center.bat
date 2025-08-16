@echo off
REM Scalping Bot Command Center Launcher
REM Professional desktop GUI for real-time monitoring

echo.
echo ===============================================
echo  🚀 SCALPING BOT COMMAND CENTER v2.0
echo ===============================================
echo.
echo Starting professional desktop monitoring GUI...
echo.

cd /d "c:\Users\will7\OneDrive - Sygma Data Analytics\Stock Trading\Scalping Bot System"

REM Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found, using system Python
)

echo.
echo Launching Command Center...
echo - Professional multi-panel interface
echo - Real-time monitoring (2-second refresh)
echo - Account & P&L tracking
echo - Confidence monitoring
echo - Trade execution alerts
echo - Strategy performance
echo - Market status & bot health
echo.

python scripts\scalping_command_center.py

echo.
echo Command Center has been closed.
echo.
pause
