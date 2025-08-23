@echo off
REM CI/CD Quick Test - Run all checks locally before pushing to GitHub

echo 🚀 Running CI/CD checks locally...
echo This will run the same checks that GitHub Actions will run
echo.

REM Change to project root
cd /d "%~dp0\.."

REM Run the Python CI checks script
python cicd\run_ci_checks.py

echo.
echo Press any key to continue...
pause >nul
