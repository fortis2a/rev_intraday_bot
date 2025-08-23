# VS Code Startup Pollution Prevention
# Run this automatically when VS Code starts to maintain clean workspace

Write-Host "VS Code Startup - Pollution Prevention" -ForegroundColor Green

# Quick pollution check and cleanup
$pollutionFiles = @(
    "pnl_monitor.py",
    "debug_*.py", 
    "*_temp*.py",
    "organize*.py",
    "cleanup*.py",
    "phase*.py"
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

Write-Host "Ready for clean development!" -ForegroundColor Green
