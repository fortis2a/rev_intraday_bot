@echo off
REM Deployment Dashboard - Monitor CI/CD pipeline status

echo 🏭 TRADING BOT DEPLOYMENT DASHBOARD
echo.

REM Change to project root
cd /d "%~dp0\.."

REM Run the deployment dashboard
python cicd\deployment_dashboard.py

echo.
echo Press any key to continue...
pause >nul
