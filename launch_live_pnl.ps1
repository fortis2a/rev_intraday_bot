# Live P&L Monitor Launcher PowerShell Script
# Launches live P&L monitoring in external window

Write-Host ""
Write-Host "📊 LIVE P&L MONITOR LAUNCHER" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host "🎯 Quantum Watchlist: IONQ, PG, QBTS, RGTI, JNJ" -ForegroundColor Yellow
Write-Host "💰 Real-time P&L tracking per stock + summary" -ForegroundColor Green
Write-Host ""
Write-Host "Choose your monitor:"
Write-Host "  1. 📊 Complete P&L Monitor (Realized + Unrealized from Alpaca)" -ForegroundColor Green
Write-Host "  2. 📈 Enhanced P&L Monitor (Per-stock breakdown)" -ForegroundColor Blue
Write-Host "  3. 💰 Standard P&L Monitor (Simple)" -ForegroundColor Cyan
Write-Host "  4. 🚀 All Monitors (Side by side)" -ForegroundColor Magenta
Write-Host ""

$choice = Read-Host "Enter choice (1-4)"

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🖥️ Launching Complete P&L Monitor (Alpaca Total P&L)..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '.\\.venv\\Scripts\\Activate.ps1'; python complete_live_pnl.py; Read-Host 'Press Enter to close'" -WindowStyle Normal
        Write-Host "✅ Complete P&L Monitor launched" -ForegroundColor Green
    }
    "2" {
        Write-Host ""
        Write-Host "🖥️ Launching Enhanced P&L Monitor..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '.\\.venv\\Scripts\\Activate.ps1'; python enhanced_live_pnl.py; Read-Host 'Press Enter to close'" -WindowStyle Normal
        Write-Host "✅ Enhanced P&L Monitor launched" -ForegroundColor Green
    }
    "3" {
        Write-Host ""
        Write-Host "🖥️ Launching Standard P&L Monitor..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '.\\.venv\\Scripts\\Activate.ps1'; python live_pnl_monitor.py; Read-Host 'Press Enter to close'" -WindowStyle Normal
        Write-Host "✅ Standard P&L Monitor launched" -ForegroundColor Green
    }
    "4" {
        Write-Host ""
        Write-Host "🖥️ Launching All Monitors in separate windows..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '.\\.venv\\Scripts\\Activate.ps1'; python complete_live_pnl.py; Read-Host 'Press Enter to close'" -WindowStyle Normal
        Start-Sleep -Seconds 2
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '.\\.venv\\Scripts\\Activate.ps1'; python enhanced_live_pnl.py; Read-Host 'Press Enter to close'" -WindowStyle Normal
        Start-Sleep -Seconds 2
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '.\\.venv\\Scripts\\Activate.ps1'; python live_pnl_monitor.py; Read-Host 'Press Enter to close'" -WindowStyle Normal
        Write-Host "✅ All P&L Monitors launched" -ForegroundColor Green
    }
    default {
        Write-Host ""
        Write-Host "❌ Invalid choice. Launching Complete Monitor by default..." -ForegroundColor Red
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '.\\.venv\\Scripts\\Activate.ps1'; python complete_live_pnl.py; Read-Host 'Press Enter to close'" -WindowStyle Normal
        Write-Host "✅ Complete P&L Monitor launched" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "💡 You can now run your trading bot in this window" -ForegroundColor Blue
Write-Host "🔄 P&L Monitor(s) will update every 5 seconds" -ForegroundColor Blue
Write-Host "🛑 Press Ctrl+C in monitor window to stop" -ForegroundColor Blue
Write-Host ""
Read-Host "Press Enter to continue"
