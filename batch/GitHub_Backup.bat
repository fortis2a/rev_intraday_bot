@echo off
REM GitHub Backup System Launcher
REM Backs up entire trading bot to GitHub repository

title GitHub Backup System

echo.
echo ===============================================
echo       GITHUB BACKUP SYSTEM
echo ===============================================
echo.
echo Repository: https://github.com/fortis2a/rev_intraday_bot
echo.
echo [INFO] This system will backup your complete trading bot:
echo        - All Python code and configurations
echo        - Trading strategies and core components  
echo        - Launchers and utility scripts
echo        - Documentation and setup files
echo.
echo [EXCLUDED] For security and efficiency:
echo        - Environment variables (.env file)
echo        - Log files and reports (generated data)
echo        - Python cache files
echo.
echo ===============================================
echo   SELECT BACKUP OPTION
echo ===============================================
echo.
echo 1. BACKUP NOW (Manual backup to GitHub)
echo 2. START AUTO SCHEDULER (Daily at midnight)
echo 3. TEST GIT CONNECTION (Verify setup)
echo 4. VIEW BACKUP STATUS (Check last backup)
echo 5. EXIT
echo.
echo ===============================================

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto manual
if "%choice%"=="2" goto scheduler
if "%choice%"=="3" goto test
if "%choice%"=="4" goto status
if "%choice%"=="5" goto exit

echo Invalid choice. Please select 1-5.
pause
goto start

:manual
echo.
echo [RUNNING] Manual GitHub Backup...
echo [INFO] This will commit and push all changes to GitHub
echo [INFO] Repository: https://github.com/fortis2a/rev_intraday_bot
echo.
python backup_system.py backup
echo.
pause
goto exit

:scheduler
echo.
echo [STARTING] Auto Backup Scheduler...
echo [INFO] Will backup to GitHub daily at midnight
echo [INFO] Press Ctrl+C to stop the scheduler
echo.
python backup_system.py schedule
goto exit

:test
echo.
echo [TESTING] Git Connection...
echo [INFO] Checking Git installation and connectivity
echo.
git --version
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in PATH
    echo [INFO] Please install Git from: https://git-scm.com/
) else (
    echo [SUCCESS] Git is installed
    echo.
    echo [TEST] Checking repository access...
    git ls-remote https://github.com/fortis2a/rev_intraday_bot.git
    if %errorlevel% neq 0 (
        echo [ERROR] Cannot access repository
        echo [INFO] Check repository URL and permissions
    ) else (
        echo [SUCCESS] Repository accessible
    )
)
echo.
pause
goto exit

:status
echo.
echo [STATUS] Backup System Status...
echo.
if exist .git (
    echo [FOUND] Git repository initialized
    echo.
    echo [RECENT COMMITS]
    git log --oneline -5
    echo.
    echo [LAST BACKUP INFO]
    git log -1 --format="Last backup: %%ad (%%ar)" --date=short
) else (
    echo [INFO] No Git repository found - run backup to initialize
)
echo.
pause
goto exit

:exit
echo.
echo [EXIT] GitHub Backup System closed
echo.
exit
