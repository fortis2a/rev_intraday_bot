@echo off
REM Live P&L Monitor Launcher
REM Launches live P&L monitoring in external PowerShell window

title Live P&L Monitor Launcher

echo.
echo LIVE P^&L MONITOR LAUNCHER
echo ============================
echo Quantum Watchlist: IONQ, PG, QBTS, RGTI, JNJ
echo Real-time P^&L tracking per stock + summary
echo.
echo Choose your monitor:
echo   1. Complete P^&L Monitor (Total P^&L from Alpaca - RECOMMENDED)
echo   2. Enhanced P^&L Monitor (Per-stock breakdown)
echo   3. Standard P^&L Monitor (Simple)
echo   4. All Monitors (Side by side)
echo.
set /p choice="Enter choice (1-4): "

REM Change to the script directory
cd /d "%~dp0"

if "%choice%"=="1" (
    echo.
    echo Launching Complete P^&L Monitor in external window...
    powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', '& \".\.venv\Scripts\Activate.ps1\"; python complete_live_pnl.py; Read-Host \"Press Enter to close\"' -WindowStyle Normal"
    echo Complete P^&L Monitor launched
) else if "%choice%"=="2" (
    echo.
    echo Launching Enhanced P^&L Monitor in external window...
    powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', '& \".\.venv\Scripts\Activate.ps1\"; python enhanced_live_pnl.py; Read-Host \"Press Enter to close\"' -WindowStyle Normal"
    echo Enhanced P^&L Monitor launched
) else if "%choice%"=="3" (
    echo.
    echo Launching Standard P^&L Monitor in external window...
    powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', '& \".\.venv\Scripts\Activate.ps1\"; python live_pnl_monitor.py; Read-Host \"Press Enter to close\"' -WindowStyle Normal"
    echo Standard P^&L Monitor launched
) else if "%choice%"=="4" (
    echo.
    echo Launching All Monitors in separate windows...
    powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', '& \".\.venv\Scripts\Activate.ps1\"; python complete_live_pnl.py; Read-Host \"Press Enter to close\"' -WindowStyle Normal"
    timeout /t 2 /nobreak >nul
    powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', '& \".\.venv\Scripts\Activate.ps1\"; python enhanced_live_pnl.py; Read-Host \"Press Enter to close\"' -WindowStyle Normal"
    timeout /t 2 /nobreak >nul
    powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', '& \".\.venv\Scripts\Activate.ps1\"; python live_pnl_monitor.py; Read-Host \"Press Enter to close\"' -WindowStyle Normal"
    echo All P^&L Monitors launched
) else (
    echo Invalid choice. Launching Enhanced Monitor by default...
    powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', '& \".\.venv\Scripts\Activate.ps1\"; python enhanced_live_pnl.py; Read-Host \"Press Enter to close\"' -WindowStyle Normal"
    echo Enhanced P^&L Monitor launched
)

echo.
echo You can now run your trading bot in this window
echo P^&L Monitor(s) will update every 5 seconds
echo Press Ctrl+C in monitor window to stop
echo.
pause
