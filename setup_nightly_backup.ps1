# PowerShell script for setting up automatic nightly backup
# Run this as Administrator for best results

Write-Host "🔧 Setting up automatic nightly backup to GitHub..." -ForegroundColor Yellow
Write-Host ""

$TaskName = "TradingBotNightlyBackup"
$ScriptPath = "C:\Users\will7\OneDrive - Sygma Data Analytics\Stock Trading\Scalping Bot System\backup_to_github.py"
$PythonPath = "python"

# Check if task already exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($ExistingTask) {
    Write-Host "⚠️ Task already exists. Removing old task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create new scheduled task
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument "`"$ScriptPath`"" -WorkingDirectory "C:\Users\will7\OneDrive - Sygma Data Analytics\Stock Trading\Scalping Bot System"
$Trigger = New-ScheduledTaskTrigger -Daily -At "23:30"
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Automatic nightly backup of Intraday Trading Bot to GitHub"
    
    Write-Host "✅ Nightly backup scheduled successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📅 Schedule: Every day at 11:30 PM" -ForegroundColor Cyan
    Write-Host "💾 Action: Automatic backup to GitHub" -ForegroundColor Cyan
    Write-Host "🔄 Working Directory: C:\Users\will7\OneDrive - Sygma Data Analytics\Stock Trading\Scalping Bot System" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor White
    Write-Host "  View task: Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host "  Delete task: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false" -ForegroundColor Gray
    Write-Host "  Test backup now: python backup_to_github.py" -ForegroundColor Gray
    
} catch {
    Write-Host "❌ Failed to create scheduled task: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Try running PowerShell as Administrator" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
