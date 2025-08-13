@echo off
REM Live P&L Monitor - External PowerShell Window
REM Launches the live P&L monitor in a separate window

echo [START] Starting Live P&L Monitor in external window...
echo [INFO] Monitor will open in new PowerShell window
echo [INFO] Close this window or press Ctrl+C in the monitor to stop

REM Start PowerShell with the live P&L monitor
powershell.exe -NoExit -Command "& {Set-Location '%~dp0'; python live_pnl_external.py}"

echo [STOP] Live P&L Monitor closed
pause
