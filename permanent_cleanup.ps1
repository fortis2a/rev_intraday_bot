# Permanent Workspace Cleanup for Windows
# This script prevents VS Code from auto-restoring deleted files

Write-Host "🧹 PERMANENT WORKSPACE CLEANUP" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Get current directory
$rootPath = Get-Location

# Files to remove (patterns)
$filesToRemove = @(
    "test_*.py",
    "demo_*.py", 
    "*_demo.py",
    "debug_*.py",
    "analyze_*.py",
    "check_*.py",
    "fix_*.py",
    "diagnose_*.py",
    "investigate_*.py",
    "verify_*.py",
    "validate_*.py",
    "cleanup_*.py",
    "clear_*.py",
    "emergency_*.py",
    "force_*.py",
    "reset_*.py",
    "restart_*.py",
    "move_*.py",
    "legacy_*.py",
    "scalping_bot.py",
    "intraday_trading_bot.py",
    "main_simple.py",
    "minimal_main.py",
    "dashboard.py",
    "dashboard_enhanced.py",
    "live_dashboard.py",
    "pnl_monitor.py",
    "live_pnl_monitor.py",
    "rgti_*.py",
    "manual_closer.py",
    "adopt_positions.py",
    "*.bat",
    "*.ps1",
    "*_SUMMARY.md",
    "*_GUIDE.md", 
    "*_ANALYSIS.md",
    "*_COMPLETE.md",
    "*_FIX*.md"
)

# Directories to remove
$dirsToRemove = @(
    "analysis",
    "batch", 
    "archive",
    "demo_reports",
    "Futures Scalping Bot"
)

# Protected files (never remove these)
$protectedFiles = @(
    "launcher.py",
    "main.py", 
    "config.py",
    "requirements.txt",
    "README.md",
    ".gitignore",
    "CLEANUP_SUMMARY.md",
    "permanent_cleanup.py"
)

Write-Host "🔍 Scanning for files to remove..." -ForegroundColor Yellow

# Find files to remove
$foundFiles = @()
foreach ($pattern in $filesToRemove) {
    $matchedFiles = Get-ChildItem -Path $rootPath -Name $pattern -ErrorAction SilentlyContinue
    foreach ($match in $matchedFiles) {
        if ($match -notin $protectedFiles) {
            $foundFiles += $match
        }
    }
}

# Find directories to remove  
$foundDirs = @()
foreach ($dirName in $dirsToRemove) {
    $dirPath = Join-Path $rootPath $dirName
    if (Test-Path $dirPath) {
        $foundDirs += $dirName
    }
}

Write-Host "📄 Found $($foundFiles.Count) files to remove" -ForegroundColor Green
Write-Host "📁 Found $($foundDirs.Count) directories to remove" -ForegroundColor Green

if ($foundFiles.Count -eq 0 -and $foundDirs.Count -eq 0) {
    Write-Host "✅ Workspace is already clean!" -ForegroundColor Green
    exit 0
}

# Show what will be removed
Write-Host "`n📋 Items to be removed:" -ForegroundColor Cyan
foreach ($file in $foundFiles[0..9]) {  # Show first 10
    Write-Host "  - $file" -ForegroundColor Red
}
if ($foundFiles.Count -gt 10) {
    Write-Host "  ... and $($foundFiles.Count - 10) more files" -ForegroundColor Red
}
foreach ($dir in $foundDirs) {
    Write-Host "  - $dir/" -ForegroundColor Red
}

# Confirm removal
$response = Read-Host "`n🤔 Proceed with cleanup? (y/N)"
if ($response.ToLower() -ne "y") {
    Write-Host "❌ Cleanup cancelled" -ForegroundColor Red
    exit 0
}

Write-Host "`n🚀 Starting cleanup..." -ForegroundColor Green

# Remove from git tracking first (if git is available)
Write-Host "🔧 Removing files from git tracking..." -ForegroundColor Yellow
foreach ($file in $foundFiles) {
    try {
        git rm --cached $file 2>$null
    } catch {
        # Ignore git errors - file might not be tracked
    }
}

foreach ($dir in $foundDirs) {
    try {
        git rm -r --cached $dir 2>$null  
    } catch {
        # Ignore git errors - directory might not be tracked
    }
}

# Physical removal
Write-Host "🗑️ Removing files..." -ForegroundColor Yellow
$removedCount = 0

foreach ($file in $foundFiles) {
    $filePath = Join-Path $rootPath $file
    if (Test-Path $filePath) {
        try {
            Remove-Item $filePath -Force
            Write-Host "  ❌ $file" -ForegroundColor Red
            $removedCount++
        } catch {
            Write-Host "  ⚠️ Could not remove $file" -ForegroundColor Yellow
        }
    }
}

foreach ($dir in $foundDirs) {
    $dirPath = Join-Path $rootPath $dir
    if (Test-Path $dirPath) {
        try {
            Remove-Item $dirPath -Recurse -Force
            Write-Host "  ❌ $dir/" -ForegroundColor Red
            $removedCount++
        } catch {
            Write-Host "  ⚠️ Could not remove $dir/" -ForegroundColor Yellow
        }
    }
}

# Clean Python cache
Write-Host "🧹 Cleaning Python cache..." -ForegroundColor Yellow
Get-ChildItem -Path $rootPath -Recurse -Name "__pycache__" -Directory | ForEach-Object {
    $cachePath = Join-Path $rootPath $_
    try {
        Remove-Item $cachePath -Recurse -Force
        Write-Host "  ❌ $_" -ForegroundColor Red
    } catch {
        Write-Host "  ⚠️ Could not remove cache: $_" -ForegroundColor Yellow
    }
}

Write-Host "`n✅ Removed $removedCount items" -ForegroundColor Green

# Update .gitignore
Write-Host "📝 Updating .gitignore..." -ForegroundColor Yellow
$gitignoreAdditions = @"

# === WORKSPACE CLEANUP PROTECTION ===
# Prevent VS Code auto-restore of unwanted files

# Development and testing files (root level only)
/test_*.py
/demo_*.py
/*_demo.py
/debug_*.py
/temp_*.py
/tmp_*.py

# Analysis and diagnostic files
/analyze_*.py
/check_*.py
/fix_*.py
/diagnose_*.py
/investigate_*.py
/verify_*.py
/validate_*.py

# Cleanup and maintenance files
/cleanup_*.py
/clear_*.py
/emergency_*.py
/force_*.py
/reset_*.py
/restart_*.py
/move_*.py

# Legacy and outdated files
/legacy_*.py
/scalping_bot.py
/intraday_trading_bot.py
/main_simple.py
/minimal_main.py

# Duplicate dashboards
/dashboard.py
/dashboard_enhanced.py
/live_dashboard.py

# Batch and script files
*.bat
*.ps1
*.sh

# Analysis summaries and guides (excessive)
/*_SUMMARY.md
/*_GUIDE.md
/*_ANALYSIS.md
/*_COMPLETE.md
/*_FIX*.md

# Temporary directories
/analysis/
/batch/
/archive/
/demo_reports/

# Backup files
cleanup_backup_list.json

# Exclude legitimate files in subdirectories
!scripts/test_*.py
!tests/test_*.py
!docs/*_GUIDE.md
!docs/*_SUMMARY.md
"@

Add-Content -Path ".gitignore" -Value $gitignoreAdditions -Encoding UTF8
Write-Host "✅ Updated .gitignore" -ForegroundColor Green

# Create VS Code settings
Write-Host "⚙️ Configuring VS Code..." -ForegroundColor Yellow
$vscodeDir = ".vscode"
if (!(Test-Path $vscodeDir)) {
    New-Item -ItemType Directory -Path $vscodeDir
}

$vscodeSettings = @{
    "files.watcherExclude" = @{
        "**/test_*.py" = $true
        "**/demo_*.py" = $true
        "**/*_demo.py" = $true
        "**/debug_*.py" = $true
        "**/analyze_*.py" = $true
        "**/cleanup_*.py" = $true
        "**/*.bat" = $true
        "**/*.ps1" = $true
        "**/analysis/**" = $true
        "**/batch/**" = $true
        "**/archive/**" = $true
    }
    "files.exclude" = @{
        "**/test_*.py" = $true
        "**/demo_*.py" = $true
        "**/*_demo.py" = $true
        "**/debug_*.py" = $true
    }
    "search.exclude" = @{
        "**/test_*.py" = $true
        "**/demo_*.py" = $true
        "**/*_demo.py" = $true
        "**/debug_*.py" = $true
        "**/analyze_*.py" = $true
        "**/cleanup_*.py" = $true
    }
} | ConvertTo-Json -Depth 3

$settingsPath = Join-Path $vscodeDir "settings.json"
Set-Content -Path $settingsPath -Value $vscodeSettings -Encoding UTF8
Write-Host "✅ VS Code configured" -ForegroundColor Green

Write-Host "`n" -NoNewline
Write-Host "="*60 -ForegroundColor Cyan
Write-Host "✅ WORKSPACE CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "✅ VS Code protection configured" -ForegroundColor Green  
Write-Host "✅ Git tracking updated" -ForegroundColor Green
Write-Host "✅ .gitignore enhanced" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Cyan

Write-Host "`n📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Restart VS Code to apply settings" -ForegroundColor White
Write-Host "2. Run: git add . && git commit -m 'Clean workspace'" -ForegroundColor White
Write-Host "3. If files reappear, re-run this script" -ForegroundColor White

# Optionally commit changes
$commitResponse = Read-Host "`n🤔 Commit changes to git now? (y/N)"
if ($commitResponse.ToLower() -eq "y") {
    Write-Host "📝 Committing changes..." -ForegroundColor Yellow
    git add .
    git commit -m "Clean workspace and prevent auto-restore"
    Write-Host "✅ Changes committed" -ForegroundColor Green
}

Write-Host "`n🎉 Cleanup complete! Workspace is now clean and protected." -ForegroundColor Green
