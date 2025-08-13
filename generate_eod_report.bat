@echo off
REM ========================================
REM End-of-Day Report Generator (Windows)
REM Generates comprehensive daily trading reports
REM ========================================

echo.
echo ================================================
echo 📊 INTRADAY TRADING BOT - EOD REPORT GENERATOR
echo ================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Please run setup.py first to create the virtual environment.
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if Python script exists
if not exist "generate_eod_report.py" (
    echo ❌ generate_eod_report.py not found!
    echo Please ensure the file exists in the current directory.
    pause
    exit /b 1
)

REM Get current date for report
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "today=%YYYY%-%MM%-%DD%"

echo 📅 Generating EOD report for: %today%
echo.

REM Run the EOD report generator
echo 🚀 Running EOD report generator...
python generate_eod_report.py --date %today%

if %errorlevel% equ 0 (
    echo.
    echo ✅ EOD report generated successfully!
    echo 📁 Check the reports\ directory for output files.
    echo.
    
    REM Open reports directory if it exists
    if exist "reports\" (
        echo 📂 Opening reports directory...
        start "" "reports\"
    )
) else (
    echo.
    echo ❌ EOD report generation failed!
    echo Please check the logs for error details.
    echo.
)

echo.
echo Press any key to exit...
pause > nul
