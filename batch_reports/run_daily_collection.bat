@echo off
REM Daily Trading Data Collection - Scheduled for 4:15 PM
REM Activates virtual environment and runs data collector

echo ==========================================
echo Daily Trading Data Collection
echo Time: %date% %time%
echo ==========================================

cd /d "C:\Users\will7\OneDrive - Sygma Data Analytics\Stock Trading\Scalping Bot System"

REM Activate virtual environment
call ".venv\Scripts\activate.bat"

REM Run data collector
echo Collecting today's trading data...
python "scripts\daily_data_collector.py"

if %ERRORLEVEL% EQU 0 (
    echo ✅ Data collection completed successfully
) else (
    echo ❌ Data collection failed with error code %ERRORLEVEL%
)

echo.
echo ==========================================
echo Collection finished at %time%
echo ==========================================

pause
