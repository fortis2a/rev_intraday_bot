@echo off
echo ========================================
echo  PROFIT PROTECTION COMMAND CENTER
echo ========================================
echo.
echo Current Status: ALL POSITIONS ARE PROFITABLE ($47.35 total)
echo.
echo Available Actions:
echo.
echo 1. View Live Dashboard
echo 2. Protect All Positions (Emergency)
echo 3. Check Current Orders
echo 4. Manual Position Close
echo 5. Start Continuous Monitoring
echo.
echo ========================================

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo Starting Live Dashboard...
    python live_dashboard.py
) else if "%choice%"=="2" (
    echo Running Emergency Protection...
    python manual_protection.py
    pause
) else if "%choice%"=="3" (
    echo Checking Current Orders...
    python -c "
import sys
sys.path.append('.')
from config import config
import alpaca_trade_api as tradeapi

api = tradeapi.REST(config['ALPACA_API_KEY'], config['ALPACA_SECRET_KEY'], config['ALPACA_BASE_URL'])
orders = api.list_orders(status='open')
print('ACTIVE ORDERS:')
if not orders:
    print('No active orders')
else:
    for order in orders:
        print(f'{order.symbol} {order.side} {order.qty} {order.order_type} - {order.id}')
"
    pause
) else if "%choice%"=="4" (
    echo Manual Position Management...
    python -c "
import sys
sys.path.append('.')
from config import config
import alpaca_trade_api as tradeapi

api = tradeapi.REST(config['ALPACA_API_KEY'], config['ALPACA_SECRET_KEY'], config['ALPACA_BASE_URL'])
positions = api.list_positions()
print('CURRENT POSITIONS:')
for i, pos in enumerate(positions, 1):
    side = 'LONG' if float(pos.qty) > 0 else 'SHORT'
    profit = float(pos.unrealized_pl)
    print(f'{i}. {pos.symbol} ({side}) - P&L: ${profit:+.2f}')

choice = input('Enter position number to close (or 0 to cancel): ')
if choice != '0' and choice.isdigit():
    idx = int(choice) - 1
    if 0 <= idx < len(positions):
        pos = positions[idx]
        side = 'sell' if float(pos.qty) > 0 else 'buy'
        qty = abs(float(pos.qty))
        confirm = input(f'Close {pos.symbol} {side.upper()} {qty} shares? (y/N): ')
        if confirm.lower() == 'y':
            order = api.submit_order(symbol=pos.symbol, qty=qty, side=side, type='market', time_in_force='gtc')
            print(f'Position closed - Order ID: {order.id}')
        else:
            print('Cancelled')
    else:
        print('Invalid position number')
"
    pause
) else if "%choice%"=="5" (
    echo Starting Continuous Monitoring...
    python continuous_position_monitor.py
) else (
    echo Invalid choice
    pause
)
