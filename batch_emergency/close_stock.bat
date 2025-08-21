@echo off
REM Close Single Stock Position
echo.
echo ========================================
echo       CLOSE SINGLE STOCK POSITION
echo ========================================
echo.

cd /d "%~dp0"

if "%1"=="" (
    echo Usage: close_stock.bat SYMBOL
    echo Example: close_stock.bat AAPL
    echo.
    echo Or run without arguments for interactive mode:
    ".venv\Scripts\python.exe" close_trade.py --interactive
) else (
    echo Closing position for %1...
    ".venv\Scripts\python.exe" close_trade.py --symbol %1
)

echo.
pause
