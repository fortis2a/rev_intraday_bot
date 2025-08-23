# Terminal Cleanup Script for Trading System
# Use with caution - this will close processes

param(
    [switch]$KeepDashboards,
    [switch]$Force
)

Write-Host "=== TRADING SYSTEM TERMINAL CLEANUP ===" -ForegroundColor Yellow

# Check for critical processes
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
$dashboardProcesses = $pythonProcesses | Where-Object {
    (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine -like "*dashboard*"
}

Write-Host "`nCurrent Status:" -ForegroundColor Cyan
Write-Host "- Python processes: $($pythonProcesses.Count)" -ForegroundColor White
Write-Host "- Dashboard processes: $($dashboardProcesses.Count)" -ForegroundColor Green
Write-Host "- PowerShell processes: $((Get-Process powershell).Count)" -ForegroundColor Red

if ($dashboardProcesses.Count -gt 0 -and -not $KeepDashboards -and -not $Force) {
    Write-Host "`n⚠️  WARNING: Dashboard processes detected!" -ForegroundColor Yellow
    Write-Host "These may be monitoring your trading activity." -ForegroundColor Yellow
    Write-Host "Use -KeepDashboards to preserve them or -Force to close everything." -ForegroundColor Yellow
    Write-Host "`nDashboard processes:" -ForegroundColor White
    foreach ($proc in $dashboardProcesses) {
        $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
        Write-Host "  PID $($proc.Id): $cmdLine" -ForegroundColor Gray
    }
    return
}

# Close excess PowerShell processes (keep current one)
$currentPID = $PID
$powershellProcesses = Get-Process powershell | Where-Object {$_.Id -ne $currentPID}

Write-Host "`n🧹 Cleanup Actions:" -ForegroundColor Cyan

if (-not $KeepDashboards -and $dashboardProcesses.Count -gt 0) {
    Write-Host "- Stopping dashboard processes..." -ForegroundColor Yellow
    $dashboardProcesses | Stop-Process -Force
    Write-Host "  ✅ Stopped $($dashboardProcesses.Count) dashboard process(es)" -ForegroundColor Green
}

if ($powershellProcesses.Count -gt 0) {
    Write-Host "- Closing excess PowerShell terminals..." -ForegroundColor Yellow
    $powershellProcesses | Stop-Process -Force
    Write-Host "  ✅ Closed $($powershellProcesses.Count) PowerShell terminal(s)" -ForegroundColor Green
}

Write-Host "`n✨ Cleanup Complete!" -ForegroundColor Green
Write-Host "Recommendation: Restart VS Code for cleanest environment" -ForegroundColor Cyan

# Final status
Write-Host "`nFinal Status:" -ForegroundColor Cyan
Write-Host "- Python processes: $((Get-Process python -ErrorAction SilentlyContinue).Count)" -ForegroundColor White
Write-Host "- PowerShell processes: $((Get-Process powershell).Count)" -ForegroundColor Green
