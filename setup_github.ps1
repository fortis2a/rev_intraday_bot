#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Setup GitHub Repository for Intraday Trading Bot
.DESCRIPTION
    Helps set up the GitHub repository and configure automatic backups
#>

Write-Host "🚀 GitHub Repository Setup for Intraday Trading Bot" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

Write-Host "`n📋 SETUP INSTRUCTIONS:" -ForegroundColor Yellow
Write-Host "1. Go to GitHub.com and sign in to your ZEUS7916 account"
Write-Host "2. Click the '+' button in the top right corner"
Write-Host "3. Select 'New repository'"
Write-Host "4. Repository settings:"
Write-Host "   - Repository name: intraday-trading-bot"
Write-Host "   - Description: Professional intraday trading system with intelligent orchestrator"
Write-Host "   - Set to Private (recommended for trading systems)"
Write-Host "   - DO NOT initialize with README, .gitignore, or license (we already have these)"
Write-Host "5. Click 'Create repository'"

Write-Host "`n⏳ Waiting for you to create the repository..." -ForegroundColor Yellow
$confirm = Read-Host "Press Enter when you've created the repository on GitHub"

Write-Host "`n🔗 Testing connection to GitHub..." -ForegroundColor Yellow

# Test if repository exists
$testResult = git ls-remote origin 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Repository connection successful!" -ForegroundColor Green
    
    Write-Host "`n🚀 Pushing initial code to GitHub..." -ForegroundColor Yellow
    git push -u origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
        Write-Host "📊 Your repository: https://github.com/ZEUS7916/intraday-trading-bot" -ForegroundColor Cyan
        
        Write-Host "`n🔄 Setting up automatic daily backups..." -ForegroundColor Yellow
        
        # Create Windows Task Scheduler entry for daily backup
        $taskName = "IntradayBot-GitHubBackup"
        $scriptPath = Join-Path $PWD "backup_to_github.ps1"
        $workingDir = $PWD
        
        # Create task to run daily at 6 PM
        $action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File `"$scriptPath`"" -WorkingDirectory $workingDir
        $trigger = New-ScheduledTaskTrigger -Daily -At 6PM
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
        $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
        
        try {
            Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force
            Write-Host "✅ Daily backup scheduled for 6:00 PM" -ForegroundColor Green
        } catch {
            Write-Host "⚠️ Could not create scheduled task. You can run backup_to_github.ps1 manually" -ForegroundColor Yellow
        }
        
        Write-Host "`n🎯 SETUP COMPLETE!" -ForegroundColor Green
        Write-Host "Your trading system is now backed up to GitHub automatically." -ForegroundColor White
        Write-Host "`nManual backup command: .\backup_to_github.ps1" -ForegroundColor Gray
        
    } else {
        Write-Host "❌ Failed to push to GitHub. Check your authentication." -ForegroundColor Red
        Write-Host "You may need to set up a Personal Access Token:" -ForegroundColor Yellow
        Write-Host "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token" -ForegroundColor Cyan
    }
} else {
    Write-Host "❌ Could not connect to repository. Please check:" -ForegroundColor Red
    Write-Host "1. Repository was created successfully"
    Write-Host "2. Repository name is exactly: intraday-trading-bot"
    Write-Host "3. Your GitHub authentication is working"
}

Write-Host "`nPress Enter to continue..."
Read-Host
