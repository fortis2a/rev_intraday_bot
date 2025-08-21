@echo off
REM Generate Enhanced Market Close Report - Scheduled for 4:30 PM
REM Uses database cache for fast report generation

echo ==========================================
echo Enhanced Market Close Report Generation
echo Time: %date% %time%
echo ==========================================

cd /d "C:\Users\will7\OneDrive - Sygma Data Analytics\Stock Trading\Scalping Bot System"

REM Activate virtual environment
call ".venv\Scripts\activate.bat"

REM Generate report
echo Generating market close report...
python "scripts\enhanced_report_generator.py"

if %ERRORLEVEL% EQU 0 (
    echo ✅ Report generation completed successfully
    echo Opening report in browser...
    
    REM Find today's report file
    for /f "delims=" %%i in ('powershell -command "Get-Date -Format 'yyyyMMdd'"') do set TODAY=%%i
    set REPORT_FILE=reports\market_close_report_%TODAY%.html
    
    if exist "%REPORT_FILE%" (
        start "" "%REPORT_FILE%"
    ) else (
        echo Report file not found: %REPORT_FILE%
    )
) else (
    echo ❌ Report generation failed with error code %ERRORLEVEL%
)

echo.
echo ==========================================
echo Report generation finished at %time%
echo ==========================================

pause
