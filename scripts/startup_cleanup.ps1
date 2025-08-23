# VS Code Startup Pollution Prevention
# Run this automatically when VS Code starts to maintain clean workspace

Write-Host "VS Code Startup - Pollution Prevention" -ForegroundColor Green

# Comprehensive pollution patterns including VS Code tab problems
$pollutionFiles = @(
    "pnl_monitor.py",
    "debug_*.py", 
    "*_temp*.py",
    "organize*.py",
    "cleanup*.py",
    "phase*.py",
    "diagnose-*.py",
    "real-time-*.py",
    "*-monitor.py"
)

$cleaned = 0
foreach ($pattern in $pollutionFiles) {
    $files = Get-ChildItem -Filter $pattern -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        Remove-Item $file.FullName -Force -ErrorAction SilentlyContinue
        $cleaned++
    }
}

if ($cleaned -gt 0) {
    Write-Host "Cleaned $cleaned pollution file(s)" -ForegroundColor Yellow
} else {
    Write-Host "Workspace is clean!" -ForegroundColor Green
}

# Show workspace status
$terminalCount = (Get-Process powershell -ErrorAction SilentlyContinue).Count
$pythonCount = (Get-Process python -ErrorAction SilentlyContinue).Count

Write-Host ""
Write-Host "Workspace Status:" -ForegroundColor Cyan
Write-Host "   Terminals: $terminalCount" -ForegroundColor White
Write-Host "   Python processes: $pythonCount" -ForegroundColor White

if ($terminalCount -gt 10) {
    Write-Host "High terminal count - consider cleanup" -ForegroundColor Yellow
}

# Check for VS Code tab pollution (files that don't exist but show in tabs)
$tabPollutionPatterns = @("diagnose-*.py", "real-time-*.py", "organize-*.py", "phase1-*.py")
$foundTabPollution = $false

foreach ($pattern in $tabPollutionPatterns) {
    if (Get-ChildItem $pattern -ErrorAction SilentlyContinue) {
        $foundTabPollution = $true
        break
    }
}

if ($foundTabPollution) {
    Write-Host ""
    Write-Host "VS Code Tab Pollution Detected!" -ForegroundColor Yellow
    Write-Host "If deleted files still show in tabs, restart VS Code workspace." -ForegroundColor Cyan
}

Write-Host "Ready for clean development!" -ForegroundColor Green
