#!/usr/bin/env pwsh
# 📱 Real-time PnL Monitor Launcher
# Launches live P&L monitoring in external PowerShell window

$ErrorActionPreference = "Stop"

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Join-Path $ScriptDir ".venv\Scripts\python.exe"

# Check if virtual environment exists
if (-not (Test-Path $VenvPython)) {
    Write-Host "❌ Virtual environment not found at: $VenvPython" -ForegroundColor Red
    Write-Host "💡 Please run setup.py first to create the virtual environment" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "🚀 Starting Real-time P&L Monitor..." -ForegroundColor Green
Write-Host "📊 Monitor will show live trading performance" -ForegroundColor Cyan
Write-Host "⏹️ Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────" -ForegroundColor Gray

try {
    # Launch the live PnL monitor
    & $VenvPython -c "from utils.live_pnl import show_live_pnl; show_live_pnl()"
}
catch {
    Write-Host "❌ Error starting P&L monitor: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
