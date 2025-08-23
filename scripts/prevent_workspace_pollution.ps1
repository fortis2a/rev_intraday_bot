# Workspace Pollution Prevention System
# Prevents temporary files from polluting the workspace after VS Code restarts

Write-Host "=== WORKSPACE POLLUTION PREVENTION ===" -ForegroundColor Green

# 1. Check for known pollution sources
$pollutionSources = @(
    "pnl_monitor.py",           # Created by launcher.py
    "*_temp*.py",               # Temporary files
    "*_debug*.py",              # Debug files  
    "*_test*.py",               # Test files
    "organize*.py",             # Organization scripts
    "cleanup*.py",              # Cleanup scripts
    "phase*.py",                # Phase files
    "*_backup*.py",             # Backup files
    "temp_*.py",                # Temp prefixed files
    "debug_*.py"                # Debug prefixed files
)

Write-Host "🔍 Scanning for pollution files..." -ForegroundColor Cyan

$found = @()
foreach ($pattern in $pollutionSources) {
    $files = Get-ChildItem -Filter $pattern -ErrorAction SilentlyContinue
    if ($files) {
        $found += $files
        foreach ($file in $files) {
            Write-Host "⚠️  Found: $($file.Name)" -ForegroundColor Yellow
        }
    }
}

if ($found.Count -eq 0) {
    Write-Host "✅ No pollution files found!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "🧹 Cleaning pollution files..." -ForegroundColor Yellow
    
    foreach ($file in $found) {
        try {
            Remove-Item $file.FullName -Force
            Write-Host "   ✅ Removed: $($file.Name)" -ForegroundColor Green
        } catch {
            Write-Host "   ❌ Failed to remove: $($file.Name) - $_" -ForegroundColor Red
        }
    }
}

# 2. Verify git is clean
Write-Host ""
Write-Host "🔍 Checking git status..." -ForegroundColor Cyan
$gitStatus = git status --porcelain 2>$null
if ($gitStatus) {
    Write-Host "⚠️  Git has unstaged changes:" -ForegroundColor Yellow
    git status --short
} else {
    Write-Host "✅ Git repository is clean!" -ForegroundColor Green
}

# 3. Check running processes that might create files
Write-Host ""
Write-Host "🔍 Checking for file-generating processes..." -ForegroundColor Cyan
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcs) {
    Write-Host "⚠️  Python processes running:" -ForegroundColor Yellow
    foreach ($proc in $pythonProcs) {
        $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($proc.Id)" -ErrorAction SilentlyContinue).CommandLine
        if ($cmdLine -like "*launcher*" -or $cmdLine -like "*pnl*" -or $cmdLine -like "*monitor*") {
            Write-Host "   🚨 Potential file creator: PID $($proc.Id)" -ForegroundColor Red
            Write-Host "      Command: $cmdLine" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "✅ No Python processes running!" -ForegroundColor Green
}

# 4. Terminal count check
$terminalCount = (Get-Process powershell).Count
Write-Host ""
Write-Host "🔍 Terminal count: $terminalCount" -ForegroundColor Cyan
if ($terminalCount -gt 5) {
    Write-Host "⚠️  High terminal count may indicate pollution risk!" -ForegroundColor Yellow
    Write-Host "   Consider running: .\scripts\cleanup_terminals.ps1 -KeepDashboards" -ForegroundColor Gray
} else {
    Write-Host "✅ Terminal count is reasonable!" -ForegroundColor Green
}

# 5. Create prevention measures
Write-Host ""
Write-Host "🛡️  Setting up prevention measures..." -ForegroundColor Cyan

# Update .gitignore to prevent pollution
$gitignoreContent = @"
# Temporary pollution files
pnl_monitor.py
*_temp*.py
*_debug*.py
*_test*.py
temp_*.py
debug_*.py
organize*.py
cleanup*.py
phase*.py
*_backup*.py

# IDE pollution
.vscode/tasks.json.backup
.vscode/settings.json.backup

# Python pollution
*.pyc.temp
*.py.bak
"@

$gitignorePath = ".gitignore"
if (Test-Path $gitignorePath) {
    $existing = Get-Content $gitignorePath -Raw
    if ($existing -notlike "*pnl_monitor.py*") {
        Add-Content $gitignorePath "`n# Auto-added pollution prevention`n$gitignoreContent"
        Write-Host "✅ Updated .gitignore with pollution prevention!" -ForegroundColor Green
    } else {
        Write-Host "✅ .gitignore already has pollution prevention!" -ForegroundColor Green
    }
} else {
    Set-Content $gitignorePath $gitignoreContent
    Write-Host "✅ Created .gitignore with pollution prevention!" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎯 PREVENTION SUMMARY:" -ForegroundColor Green
Write-Host "- Cleaned existing pollution files" -ForegroundColor White
Write-Host "- Updated .gitignore to prevent tracking" -ForegroundColor White
Write-Host "- Identified potential pollution sources" -ForegroundColor White
Write-Host "- Verified git repository cleanliness" -ForegroundColor White

Write-Host ""
Write-Host "🔄 TO MAINTAIN CLEAN WORKSPACE:" -ForegroundColor Yellow
Write-Host "1. Run this script after VS Code restarts" -ForegroundColor White
Write-Host "2. Check for new pollution: Get-ChildItem *temp*, *debug*" -ForegroundColor White
Write-Host "3. Monitor launcher.py for file creation" -ForegroundColor White
Write-Host "4. Use terminal cleanup: .\scripts\cleanup_terminals.ps1" -ForegroundColor White

Write-Host ""
Write-Host "✨ WORKSPACE POLLUTION PREVENTION COMPLETE!" -ForegroundColor Green
