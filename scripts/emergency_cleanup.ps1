# EMERGENCY POLLUTION CLEANUP
# These files keep coming back - we need to identify the source and stop it

Write-Host "=== EMERGENCY POLLUTION CLEANUP ===" -ForegroundColor Red
Write-Host ""

# EMERGENCY POLLUTION CLEANUP & DIAGNOSIS
# Manual tool for when automatic cleanup fails or investigation is needed

Write-Host "=== EMERGENCY POLLUTION CLEANUP ===" -ForegroundColor Red
Write-Host ""

# Quick nuclear cleanup using git clean
Write-Host "🚨 EXECUTING EMERGENCY CLEANUP..." -ForegroundColor Red
$beforeCount = (git status --porcelain | Where-Object {$_ -like "??*"}).Count

if ($beforeCount -gt 0) {
    Write-Host "Found $beforeCount untracked files - executing git clean..." -ForegroundColor Yellow
    git clean -f
    $afterCount = (git status --porcelain | Where-Object {$_ -like "??*"}).Count
    Write-Host "✅ Cleaned $($beforeCount - $afterCount) files" -ForegroundColor Green
} else {
    Write-Host "✅ No untracked files found" -ForegroundColor Green
}

Write-Host ""
Write-Host "📊 CLEANUP RESULTS:" -ForegroundColor Yellow
Write-Host "   Files before: $beforeCount" -ForegroundColor White
Write-Host "   Files after: $((git status --porcelain | Where-Object {$_ -like "??*"}).Count)" -ForegroundColor White

# Check for any remaining untracked files
Write-Host ""
Write-Host "🔍 CHECKING FOR REMAINING POLLUTION..." -ForegroundColor Cyan
$remaining = git status --porcelain | Where-Object {$_ -like "??*"}
if ($remaining) {
    Write-Host "⚠️  Still have untracked files:" -ForegroundColor Yellow
    $remaining | ForEach-Object { Write-Host "   $($_.Substring(3))" -ForegroundColor White }
} else {
    Write-Host "✅ No remaining untracked files!" -ForegroundColor Green
}

# Investigate potential sources
Write-Host ""
Write-Host "🔍 INVESTIGATING POLLUTION SOURCES..." -ForegroundColor Cyan

# Check if any processes are creating files
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcs) {
    Write-Host "⚠️  Python processes detected:" -ForegroundColor Yellow
    foreach ($proc in $pythonProcs) {
        $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($proc.Id)" -ErrorAction SilentlyContinue).CommandLine
        Write-Host "   PID $($proc.Id): $cmdLine" -ForegroundColor White
    }
} else {
    Write-Host "✅ No Python processes running" -ForegroundColor Green
}

# Check for VSCode extensions or tasks that might be creating files
Write-Host ""
Write-Host "💡 POLLUTION PREVENTION RECOMMENDATIONS:" -ForegroundColor Yellow
Write-Host "1. Check if any VSCode extensions are creating files" -ForegroundColor White
Write-Host "2. Review VSCode tasks.json for auto-running scripts" -ForegroundColor White  
Write-Host "3. Check for hidden Python processes or services" -ForegroundColor White
Write-Host "4. Investigate if files are being restored from backup" -ForegroundColor White

Write-Host ""
Write-Host "🛡️  EMERGENCY CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "Use this script when automatic startup cleanup fails." -ForegroundColor Cyan
