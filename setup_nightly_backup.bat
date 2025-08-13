@echo off
REM Windows Task Scheduler XML for Nightly Trading Bot Backup
REM This creates a scheduled task to backup your trading bot to GitHub every night

echo 🔧 Setting up automatic nightly backup to GitHub...
echo.

REM Create the scheduled task
schtasks /create /tn "TradingBotNightlyBackup" /tr "python \"C:\Users\will7\OneDrive - Sygma Data Analytics\Stock Trading\Scalping Bot System\backup_to_github.py\"" /sc daily /st 23:30 /f

if %ERRORLEVEL% equ 0 (
    echo ✅ Nightly backup scheduled successfully!
    echo.
    echo 📅 Schedule: Every day at 11:30 PM
    echo 💾 Action: Automatic backup to GitHub
    echo.
    echo To view the task: schtasks /query /tn "TradingBotNightlyBackup"
    echo To delete the task: schtasks /delete /tn "TradingBotNightlyBackup" /f
) else (
    echo ❌ Failed to create scheduled task
    echo Run this script as Administrator
)

pause
