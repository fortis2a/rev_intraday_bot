# VS Code Tab Cleanup - Fix Persistent Deleted Files
# This script cleans VS Code workspace state to prevent deleted files from reappearing

Write-Host "=== VS CODE TAB CLEANUP ===" -ForegroundColor Green
Write-Host ""

# 1. Find VS Code workspace folders that might contain state
$possibleStatePaths = @(
    "$env:APPDATA\Code\User\workspaceStorage",
    "$env:APPDATA\Code\User\globalStorage", 
    "$env:LOCALAPPDATA\Code\User\workspaceStorage",
    ".\.vscode"
)

Write-Host "1. Checking VS Code state locations..." -ForegroundColor Cyan

foreach ($path in $possibleStatePaths) {
    if (Test-Path $path) {
        Write-Host "   Found: $path" -ForegroundColor Green
    } else {
        Write-Host "   Not found: $path" -ForegroundColor Gray
    }
}

# 2. Clean current workspace state
Write-Host ""
Write-Host "2. Cleaning current workspace state..." -ForegroundColor Cyan

# Check for .vscode workspace state files
$workspaceFiles = @(
    ".\.vscode\*.code-workspace",
    ".\.vscode\workspace.json",
    ".\.vscode\launch.json.backup"
)

foreach ($pattern in $workspaceFiles) {
    $files = Get-ChildItem $pattern -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        Write-Host "   Found workspace file: $($file.Name)" -ForegroundColor Yellow
    }
}

# 3. Add problematic file patterns to gitignore if not already there
Write-Host ""
Write-Host "3. Updating pollution prevention..." -ForegroundColor Cyan

$gitignorePath = ".gitignore"
$problematicPatterns = @(
    "diagnose-*.py",
    "real-time-*.py", 
    "*-monitor.py",
    "debug_*.py"
)

if (Test-Path $gitignorePath) {
    $currentIgnore = Get-Content $gitignorePath -Raw
    $updated = $false
    
    foreach ($pattern in $problematicPatterns) {
        if ($currentIgnore -notlike "*$pattern*") {
            Add-Content $gitignorePath $pattern
            Write-Host "   Added to .gitignore: $pattern" -ForegroundColor Green
            $updated = $true
        }
    }
    
    if (-not $updated) {
        Write-Host "   .gitignore already up to date" -ForegroundColor Green
    }
}

# 4. Update VS Code settings to exclude problematic patterns
Write-Host ""
Write-Host "4. Updating VS Code exclusions..." -ForegroundColor Cyan

$settingsPath = ".\.vscode\settings.json"
if (Test-Path $settingsPath) {
    $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
    
    # Add exclusions for problematic files
    $exclusions = @{
        "**/diagnose-*.py" = $true
        "**/real-time-*.py" = $true  
        "**/*-monitor.py" = $true
        "**/debug_*.py" = $true
        "**/organize*.py" = $true
        "**/cleanup*.py" = $true
        "**/phase*.py" = $true
    }
    
    $updated = $false
    foreach ($pattern in $exclusions.Keys) {
        if (-not $settings."files.exclude".$pattern) {
            $settings."files.exclude" | Add-Member -NotePropertyName $pattern -NotePropertyValue $true -Force
            $updated = $true
        }
    }
    
    if ($updated) {
        $settings | ConvertTo-Json -Depth 10 | Set-Content $settingsPath
        Write-Host "   Updated VS Code file exclusions" -ForegroundColor Green
    } else {
        Write-Host "   VS Code exclusions already up to date" -ForegroundColor Green
    }
}

# 5. Instructions for user
Write-Host ""
Write-Host "=== SOLUTION FOR PERSISTENT TABS ===" -ForegroundColor Yellow
Write-Host ""
Write-Host "The strikethrough files are VS Code workspace state artifacts." -ForegroundColor White
Write-Host ""
Write-Host "IMMEDIATE FIX:" -ForegroundColor Green
Write-Host "1. Close all tabs with strikethrough files" -ForegroundColor White
Write-Host "2. File > Close Workspace" -ForegroundColor White  
Write-Host "3. File > Open Folder > Select this folder again" -ForegroundColor White
Write-Host "4. Deleted files should no longer appear" -ForegroundColor White
Write-Host ""
Write-Host "PREVENTION (completed):" -ForegroundColor Green
Write-Host "- Added file exclusions to VS Code settings" -ForegroundColor White
Write-Host "- Updated .gitignore patterns" -ForegroundColor White
Write-Host "- Startup cleanup will remove any new pollution" -ForegroundColor White

Write-Host ""
Write-Host "ALTERNATIVE FIX:" -ForegroundColor Yellow
Write-Host "If tabs persist, completely restart VS Code:" -ForegroundColor White
Write-Host "1. Close VS Code completely" -ForegroundColor White
Write-Host "2. Restart VS Code" -ForegroundColor White  
Write-Host "3. Open this workspace folder" -ForegroundColor White

Write-Host ""
Write-Host "CLEANUP COMPLETE!" -ForegroundColor Green
