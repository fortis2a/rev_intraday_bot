# Setup Clean Terminal Environment for Trading System

Write-Host "=== SETTING UP CLEAN TRADING ENVIRONMENT ===" -ForegroundColor Green

# Navigate to trading system directory
$tradingDir = "C:\Users\will7\OneDrive - Sygma Data Analytics\Stock Trading\Scalping Bot System"
Set-Location $tradingDir

Write-Host "`n📁 Working Directory: $tradingDir" -ForegroundColor Cyan

# Activate Python virtual environment
Write-Host "`n🐍 Activating Python Virtual Environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Show environment status
Write-Host "`n✅ Environment Status:" -ForegroundColor Green
Write-Host "- Python: $((Get-Command python).Source)" -ForegroundColor White
Write-Host "- Pip: $((Get-Command pip).Source)" -ForegroundColor White
Write-Host "- Working Directory: $(Get-Location)" -ForegroundColor White

# Show key commands
Write-Host "`n🚀 Available Commands:" -ForegroundColor Cyan
Write-Host "Trading Operations:" -ForegroundColor Yellow
Write-Host "  python main.py                    # Start main trading bot" -ForegroundColor White
Write-Host "  python launcher.py                # Start launcher interface" -ForegroundColor White
Write-Host "  python dashboard/interactive_dashboard.py  # Start monitoring dashboard" -ForegroundColor White

Write-Host "`nAnalysis & Reports:" -ForegroundColor Yellow
Write-Host "  python today_analysis.py          # Run today's analysis" -ForegroundColor White
Write-Host "  python enhanced_daily_analysis.py # Enhanced analysis" -ForegroundColor White

Write-Host "`nDatabase Operations:" -ForegroundColor Yellow
Write-Host "  sqlite3 data/trading.db           # Access database directly" -ForegroundColor White
Write-Host "  # Use SQL queries from database/SQL_QUERIES_REFERENCE.md" -ForegroundColor Gray

Write-Host "`nGit Operations:" -ForegroundColor Yellow
Write-Host "  git status                        # Check repository status" -ForegroundColor White
Write-Host "  git add . && git commit -m 'msg'  # Commit changes" -ForegroundColor White
Write-Host "  git push origin main              # Push to GitHub" -ForegroundColor White

Write-Host "`n🎯 Recommended Terminal Setup:" -ForegroundColor Green
Write-Host "1. Main Terminal: General commands, git operations" -ForegroundColor White
Write-Host "2. Trading Terminal: Run trading bots and analysis" -ForegroundColor White
Write-Host "3. Monitoring Terminal: Dashboard and logging (optional)" -ForegroundColor White

Write-Host "`n🔧 System Status:" -ForegroundColor Cyan
Write-Host "- Current Terminals: Keep this one + max 2 more" -ForegroundColor White
Write-Host "- Memory Usage: Monitor with Task Manager" -ForegroundColor White
Write-Host "- Background Processes: Check with 'Get-Process python'" -ForegroundColor White

Write-Host "`nReady for Trading Operations!" -ForegroundColor Green
