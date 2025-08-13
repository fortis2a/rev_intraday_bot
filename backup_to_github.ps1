#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Automated GitHub Backup Script for Intraday Trading Bot
.DESCRIPTION
    Daily backup script that commits and pushes all changes to GitHub
#>

# Set location to script directory
Set-Location $PSScriptRoot

# Activate virtual environment if it exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
}

Write-Host "🔄 Starting automated GitHub backup..." -ForegroundColor Cyan

# Check if git repository exists
if (-not (Test-Path ".git")) {
    Write-Host "❌ No git repository found. Run setup first." -ForegroundColor Red
    exit 1
}

# Get current date and time
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$date = Get-Date -Format "yyyy-MM-dd"

# Add all changes
Write-Host "📁 Adding files to staging..." -ForegroundColor Yellow
git add .

# Check if there are changes to commit
$changes = git diff --cached --name-only
if (-not $changes) {
    Write-Host "✅ No changes to backup." -ForegroundColor Green
    exit 0
}

Write-Host "📝 Found changes in files:" -ForegroundColor Yellow
$changes | ForEach-Object { Write-Host "   - $_" -ForegroundColor Gray }

# Create commit message
$commitMessage = "Daily backup [$date]

Auto-backup of intraday trading system:
- Configuration updates
- Trading logs and data
- Performance reports
- System improvements

Timestamp: $timestamp"

# Commit changes
Write-Host "💾 Committing changes..." -ForegroundColor Yellow
git commit -m $commitMessage

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to commit changes." -ForegroundColor Red
    exit 1
}

# Push to GitHub
Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Successfully backed up to GitHub!" -ForegroundColor Green
    Write-Host "📊 Repository: https://github.com/ZEUS7916/intraday-trading-bot" -ForegroundColor Cyan
} else {
    Write-Host "❌ Failed to push to GitHub. Check authentication." -ForegroundColor Red
    exit 1
}

Write-Host "🎯 Backup completed at $timestamp" -ForegroundColor Green
