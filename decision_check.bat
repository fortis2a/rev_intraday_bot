@echo off
echo ========================================
echo    TRADING BOT DECISION CHECK TEST
echo ========================================
echo.
echo Testing the updated decision check with LONG/SHORT direction display...
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo Testing BUY signal (should show LONG):
python -c "from stock_specific_config import should_execute_trade; should_execute_trade('SOXL', 'BUY')"

echo.
echo Testing SELL signal (should show SHORT):
python -c "from stock_specific_config import should_execute_trade; should_execute_trade('SOXL', 'SELL')"

echo.
echo Testing default entry signal (should show ENTRY):
python -c "from stock_specific_config import should_execute_trade; should_execute_trade('SOXL')"

echo.
echo ========================================
echo    DECISION CHECK TEST COMPLETE
echo ========================================
echo.
pause
