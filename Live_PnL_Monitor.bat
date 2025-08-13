@echo off
REM Enhanced Live P&L Monitor Launcher - COLORIZED VERSION
REM Opens in new PowerShell window with full color display

title Live P&L Monitor Launcher - COLORIZED

echo.
echo ===============================================
echo   LIVE P&L MONITOR - COLORIZED DISPLAY
echo ===============================================
echo.
echo [START] Initializing Colorized Live P&L Monitor...
echo [INFO] Opening in dedicated PowerShell window
echo [INFO] Window title: "Intraday Trading - Live P&L"
echo [INFO] Full color display with GREEN gains, RED losses
echo [INFO] Updates every 5 seconds with Alpaca data
echo.
echo [READY] Starting monitor now...
echo.

REM Launch PowerShell with custom title and live P&L monitor
start "Intraday Trading - Live P&L" powershell.exe -NoExit -Command "& {$Host.UI.RawUI.WindowTitle='Intraday Trading - Live P&L Monitor'; Set-Location '%~dp0'; Write-Host '[INIT] Starting Live P&L Monitor...' -ForegroundColor Green; python live_pnl_external.py}"

echo [SUCCESS] Live P&L Monitor window opened
echo [INFO] Check the new PowerShell window for live data
echo [INFO] Close that window to stop the monitor
echo.
echo Press any key to close this launcher...
pause >nul
