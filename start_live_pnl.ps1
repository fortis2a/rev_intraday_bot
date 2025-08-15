# Alpaca-Synced Live P&L Monitor PowerShell Launcher
# Launches live P&L monitoring in a new PowerShell window synced with Alpaca

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptPath

Write-Host "Starting Alpaca-Synced Live P&L Monitor in External PowerShell Window..." -ForegroundColor Green

# Activate virtual environment and start monitor
$venvPath = ".\.venv\Scripts\Activate.ps1"
$pythonScript = "scripts\live_pnl_external.py"

if (Test-Path $venvPath) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & $venvPath
    
    Write-Host "Starting Alpaca-Synced P&L Monitor..." -ForegroundColor Yellow
    & python $pythonScript
} else {
    Write-Host "Virtual environment not found at $venvPath" -ForegroundColor Red
    Write-Host "Running with system Python..." -ForegroundColor Yellow
    & python $pythonScript
}

Write-Host "Alpaca-Synced P&L Monitor stopped." -ForegroundColor Red
Read-Host "Press Enter to close window"
