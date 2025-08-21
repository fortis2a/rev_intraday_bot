# Interactive Trading Dashboard Launcher (PowerShell)
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "  Interactive Trading Dashboard Launcher" -ForegroundColor Cyan  
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting dashboard server..." -ForegroundColor Green
Write-Host "Dashboard will be available at: http://localhost:8050" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Activate virtual environment and run dashboard
& ".\.venv\Scripts\Activate.ps1"
& ".\.venv\Scripts\python.exe" "interactive_dashboard.py"

Write-Host "Dashboard stopped." -ForegroundColor Red
Read-Host "Press Enter to exit"
