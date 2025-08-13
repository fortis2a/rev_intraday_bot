# ========================================
# End-of-Day Report Generator (PowerShell)
# Generates comprehensive daily trading reports
# ========================================

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "📊 INTRADAY TRADING BOT - EOD REPORT GENERATOR" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup.py first to create the virtual environment." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# Check if Python script exists
if (-not (Test-Path "generate_eod_report.py")) {
    Write-Host "❌ generate_eod_report.py not found!" -ForegroundColor Red
    Write-Host "Please ensure the file exists in the current directory." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Get current date for report
$today = Get-Date -Format "yyyy-MM-dd"
Write-Host "📅 Generating EOD report for: $today" -ForegroundColor Green
Write-Host ""

# Run the EOD report generator
Write-Host "🚀 Running EOD report generator..." -ForegroundColor Yellow

try {
    & python generate_eod_report.py --date $today
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ EOD report generated successfully!" -ForegroundColor Green
        Write-Host "📁 Check the reports\ directory for output files." -ForegroundColor Cyan
        Write-Host ""
        
        # Open reports directory if it exists
        if (Test-Path "reports\") {
            Write-Host "📂 Opening reports directory..." -ForegroundColor Cyan
            Invoke-Item "reports\"
        }
        
        # Display recent report files
        if (Test-Path "reports\daily\") {
            Write-Host "📄 Recent report files:" -ForegroundColor Cyan
            Get-ChildItem "reports\daily\" -Filter "*$($today.Replace('-',''))*" | 
                Format-Table Name, Length, LastWriteTime -AutoSize
        }
    } else {
        throw "Report generation failed with exit code $LASTEXITCODE"
    }
} catch {
    Write-Host ""
    Write-Host "❌ EOD report generation failed!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "Please check the logs for error details." -ForegroundColor Yellow
    Write-Host ""
    
    # Show recent log files
    if (Test-Path "logs\") {
        Write-Host "📋 Recent log files:" -ForegroundColor Cyan
        Get-ChildItem "logs\" -Filter "*.log" | 
            Sort-Object LastWriteTime -Descending | 
            Select-Object -First 3 | 
            Format-Table Name, LastWriteTime -AutoSize
    }
}

Write-Host ""
Read-Host "Press Enter to exit"
