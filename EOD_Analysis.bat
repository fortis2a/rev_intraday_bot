@echo off
REM EOD Analysis Launcher - Comprehensive End-of-Day Reports
REM Creates detailed trading reports with charts and analysis

title EOD Analysis System

echo.
echo ===============================================
echo       EOD ANALYSIS - COMPREHENSIVE REPORTS
echo ===============================================
echo.
echo [INFO] End-of-Day Trading Analysis System
echo [INFO] Generates detailed P&L reports with:
echo        - Stock-by-stock performance analysis
echo        - Long vs Short profitability breakdown  
echo        - Hourly trading patterns and timing
echo        - Interactive charts and visualizations
echo        - Win/loss distribution analysis
echo        - Comprehensive summary statistics
echo.
echo ===============================================
echo   SELECT ANALYSIS MODE
echo ===============================================
echo.
echo 1. RUN EOD ANALYSIS NOW (Manual)
echo 2. START AUTO SCHEDULER (Runs at 4:30 PM daily)
echo 3. VIEW LATEST REPORTS (Opens dashboard)
echo 4. QUICK STATS ONLY (Fast summary)
echo 5. EXIT
echo.
echo ===============================================

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto manual
if "%choice%"=="2" goto scheduler
if "%choice%"=="3" goto reports
if "%choice%"=="4" goto quick
if "%choice%"=="5" goto exit

echo Invalid choice. Please select 1-5.
pause
goto start

:manual
echo.
echo [RUNNING] Manual EOD Analysis...
echo [INFO] This will analyze today's trades and generate:
echo        - PNG charts for all analysis
echo        - Interactive HTML dashboard  
echo        - Detailed text report
echo        - CSV data exports
echo.
python eod_analysis.py
echo.
echo [COMPLETE] Check the reports/ folder for results
pause
goto exit

:scheduler
echo.
echo [STARTING] Auto EOD Scheduler...
echo [INFO] Will automatically run analysis at 4:30 PM on trading days
echo [INFO] Press Ctrl+C to stop the scheduler
echo.
python eod_scheduler.py start
goto exit

:reports
echo.
echo [OPENING] Latest EOD Reports...
for /f "delims=" %%i in ('powershell -command "Get-Date -Format 'yyyy-MM-dd'"') do set today=%%i
set report_path=reports\%today%\eod_dashboard.html
if exist "%report_path%" (
    echo [FOUND] Opening dashboard: %report_path%
    start "" "%report_path%"
) else (
    echo [ERROR] No reports found for today (%today%)
    echo [INFO] Run analysis first (option 1)
)
pause
goto exit

:quick
echo.
echo [RUNNING] Quick Stats Summary...
python -c "from eod_analysis import EODAnalyzer; analyzer = EODAnalyzer(); trades = analyzer.get_todays_trades(); pairs = analyzer.calculate_trade_pairs(trades); stats = analyzer.generate_summary_stats(trades, pairs); print(f'Total P&L: ${stats.get(\"total_pnl\", 0):.2f}'); print(f'Win Rate: {stats.get(\"win_rate\", 0):.1f}%'); print(f'Total Trades: {stats.get(\"completed_trades\", 0)}'); print(f'Symbols: {stats.get(\"symbols_traded\", 0)}')"
echo.
pause
goto exit

:exit
echo.
echo [EXIT] EOD Analysis System closed
echo.
exit
