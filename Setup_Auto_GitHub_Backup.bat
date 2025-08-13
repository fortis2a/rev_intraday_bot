@echo off
REM Auto GitHub Backup Setup for Windows Task Scheduler
REM This script sets up automatic daily backup at midnight

echo.
echo ===============================================
echo      AUTO GITHUB BACKUP - TASK SCHEDULER SETUP
echo ===============================================
echo.
echo This will create a Windows Task to automatically backup
echo your trading bot to GitHub at midnight every day.
echo.
echo Repository: https://github.com/fortis2a/rev_intraday_bot
echo.

set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%backup_system.py
set TASK_NAME="TradingBot_GitHub_Backup"

echo [INFO] Script Directory: %SCRIPT_DIR%
echo [INFO] Python Script: %PYTHON_SCRIPT%
echo [INFO] Task Name: %TASK_NAME%
echo.

REM Check if task already exists
schtasks /query /tn %TASK_NAME% >nul 2>&1
if %errorlevel% == 0 (
    echo [FOUND] Task already exists. Removing old task...
    schtasks /delete /tn %TASK_NAME% /f
)

echo [CREATE] Creating new scheduled task...

REM Create the task to run daily at midnight
schtasks /create /tn %TASK_NAME% ^
    /tr "python \"%PYTHON_SCRIPT%\" backup" ^
    /sc daily ^
    /st 00:00 ^
    /ru SYSTEM ^
    /rl HIGHEST ^
    /f

if %errorlevel% == 0 (
    echo.
    echo [SUCCESS] ✅ GitHub Backup task created successfully!
    echo [INFO] Task will run daily at midnight (00:00)
    echo [INFO] Task name: %TASK_NAME%
    echo [INFO] Repository: https://github.com/fortis2a/rev_intraday_bot
    echo.
    echo [NEXT] To view/modify the task:
    echo        1. Open Task Scheduler (taskschd.msc)
    echo        2. Look for: %TASK_NAME%
    echo.
    echo [TEST] To test the task now:
    echo        schtasks /run /tn %TASK_NAME%
    echo.
) else (
    echo.
    echo [ERROR] ❌ Failed to create scheduled task
    echo [INFO] You may need to run this as Administrator
    echo.
)

echo ===============================================
echo          MANUAL ALTERNATIVES
echo ===============================================
echo.
echo If Task Scheduler setup failed, you can:
echo.
echo 1. Run GitHub_Backup.bat manually
echo 2. Use: python backup_system.py schedule
echo 3. Add to Option 11 in launcher.py
echo.

pause
