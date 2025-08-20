@echo off
echo ========================================
@echo off
echo ==========================================
echo    MARKET CLOSE REPORT GENERATOR
echo    Enhanced with Statistical Analysis
echo    v2.1 - Now with Technical Glossary
echo ==========================================
echo.

echo 📊 Starting comprehensive market analysis...
echo.

:: Configure Python environment and run the enhanced report
call "C:\Users\will7\OneDrive - Sygma Data Analytics\Stock Trading\Scalping Bot System\.venv\Scripts\activate.bat"

echo 🔄 Generating market close report with statistical analysis...
python "C:\Users\will7\OneDrive - Sygma Data Analytics\Stock Trading\Scalping Bot System\market_close_report.py"

echo.
echo ✅ Market close report generation complete!
echo.
echo 📄 New Features in this Report:
echo    - Fixed Day P&L calculation (now shows realized + unrealized)
echo    - Clarified Dollar Volume measurements  
echo    - Added comprehensive Technical Terms Glossary
echo    - Enhanced statistical analysis charts
echo    - Trading performance visualizations
echo.

pause
echo ========================================
echo.
echo Generating comprehensive end-of-day analysis...
echo.

cd /d "%~dp0"
".venv\Scripts\python.exe" market_close_report.py

echo.
echo ========================================
echo       📈 REPORT GENERATION COMPLETE
echo ========================================
echo.
echo Report saved in reports/ directory
echo Opening in browser...
echo.
pause
