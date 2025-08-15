# Real-Time Confidence Monitor Launcher
$Host.UI.RawUI.WindowTitle = "Real-Time Confidence Monitor"

Write-Host "🎯 Starting Real-Time Confidence Monitor..." -ForegroundColor Green
Write-Host ""

# Navigate to the script directory
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Activate virtual environment
& ".\.venv\Scripts\Activate.ps1"

Write-Host "📊 Monitoring confidence signals for all watchlist stocks" -ForegroundColor Cyan
Write-Host "🎯 Shows which stocks exceed 75% trading threshold" -ForegroundColor Cyan
Write-Host "⏰ Updates every 10 seconds" -ForegroundColor Cyan
Write-Host "💡 Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
Write-Host ""

# Run the confidence monitor
python scripts\confidence_monitor.py

Write-Host ""
Write-Host "Monitor stopped. Press any key to close window." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
