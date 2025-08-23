# VS Code Startup Pollution Prevention - AGGRESSIVE MODE
# Run this automatically when VS Code starts to maintain clean workspace

Write-Host "VS Code Startup - AGGRESSIVE Pollution Prevention" -ForegroundColor Red

# IMMEDIATE NUCLEAR CLEANUP - Remove all known pollution patterns
Write-Host "🧹 NUCLEAR CLEANUP MODE ACTIVATED..." -ForegroundColor Yellow

# Use git clean to remove ALL untracked files immediately
try {
    $beforeClean = (git status --porcelain | Where-Object {$_ -like "??*"}).Count
    if ($beforeClean -gt 0) {
        git clean -f 2>$null
        $afterClean = (git status --porcelain | Where-Object {$_ -like "??*"}).Count
        Write-Host "🚀 Cleaned $beforeClean untracked files with git clean" -ForegroundColor Green
    } else {
        Write-Host "✅ No untracked files to clean!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Git clean failed: $_" -ForegroundColor Yellow
}

# Additional targeted cleanup for specific patterns
$pollutionPatterns = @(
    "*_pnl_summary.py",
    "calculate_*.py",
    "diagnose_*.py", 
    "real_time_*.py",
    "explore_*.py",
    "query_*.py",
    "fix_*.py",
    "test_*.py",
    "explain_*.py",
    "concrete_*.py",
    "confidence_*.py",
    "permanent_*.py",
    "hybrid_*.py",
    "*_monitor.py",
    "*_summary.py",
    "*_fix*.py"
)

$cleaned = 0
foreach ($pattern in $pollutionPatterns) {
    $files = Get-ChildItem -Filter $pattern -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        Remove-Item $file.FullName -Force -ErrorAction SilentlyContinue
        $cleaned++
    }
}

if ($cleaned -gt 0) {
    Write-Host "🔥 Additional pattern cleanup: $cleaned files" -ForegroundColor Yellow
}

# Show workspace status
$terminalCount = (Get-Process powershell -ErrorAction SilentlyContinue).Count
$pythonCount = (Get-Process python -ErrorAction SilentlyContinue).Count

Write-Host ""
Write-Host "📊 Workspace Status:" -ForegroundColor Cyan
Write-Host "   Terminals: $terminalCount" -ForegroundColor White
Write-Host "   Python processes: $pythonCount" -ForegroundColor White
Write-Host "   Untracked files: $((git status --porcelain | Where-Object {$_ -like '??*'}).Count)" -ForegroundColor White

if ($terminalCount -gt 10) {
    Write-Host "⚠️  High terminal count - consider cleanup" -ForegroundColor Yellow
}

# Final verification
$stillUntracked = git status --porcelain | Where-Object {$_ -like "??*"}
if ($stillUntracked) {
    Write-Host ""
    Write-Host "🚨 WARNING: Files still untracked after cleanup!" -ForegroundColor Red
    $stillUntracked | ForEach-Object { Write-Host "   $($_.Substring(3))" -ForegroundColor Yellow }
    Write-Host "   This suggests active file generation - investigate immediately!" -ForegroundColor Red
} else {
    Write-Host ""
    Write-Host "✅ WORKSPACE IS COMPLETELY CLEAN!" -ForegroundColor Green
}

Write-Host "🛡️  AGGRESSIVE CLEANUP COMPLETE!" -ForegroundColor Green
