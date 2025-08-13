@echo off
REM Auto EOD Analysis Setup for Windows Task Scheduler
REM This script sets up automatic daily execution at market close

echo.
echo ===============================================
echo      AUTO EOD ANALYSIS - TASK SCHEDULER SETUP
echo ===============================================
echo.
echo This will create a Windows Task to automatically run
echo EOD Analysis at 4:30 PM every trading day.
echo.

set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%eod_analysis.py
set TASK_NAME="TradingBot_EOD_Analysis"

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

REM Create the task to run Monday-Friday at 4:30 PM
schtasks /create /tn %TASK_NAME% ^
    /tr "python \"%PYTHON_SCRIPT%\"" ^
    /sc weekly ^
    /d MON,TUE,WED,THU,FRI ^
    /st 16:30 ^
    /ru SYSTEM ^
    /rl HIGHEST ^
    /f

if %errorlevel% == 0 (
    echo.
    echo [SUCCESS] ✅ EOD Analysis task created successfully!
    echo [INFO] Task will run Monday-Friday at 4:30 PM
    echo [INFO] Task name: %TASK_NAME%
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
echo 1. Run EOD_Analysis.bat manually each day
echo 2. Use: python eod_scheduler.py start
echo 3. Add to Option 10 in launcher.py
echo.

pause
