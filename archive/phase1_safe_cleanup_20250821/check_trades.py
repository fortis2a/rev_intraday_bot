#!/usr/bin/env python3
"""Check Recent Trading Activity"""

from alpaca.trading.client import TradingClient
from config import ALPACA_API_KEY, ALPACA_SECRET_KEY
from datetime import datetime

# Connect to Alpaca
client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)

# Get current positions
positions = client.get_all_positions()
print('=== CURRENT POSITIONS ===')
for p in positions:
    print(f'{p.symbol}: {p.qty} shares @ ${p.avg_entry_price} (Current Value: ${p.market_value})')
    print(f'  Unrealized P&L: ${p.unrealized_pl}')

# Get recent orders
orders = client.get_orders()
print(f'\n=== RECENT ORDERS (Last 10) ===')
recent_orders = sorted(orders, key=lambda x: x.created_at, reverse=True)[:10]

for o in recent_orders:
    created_time = o.created_at.strftime('%H:%M:%S')
    filled_price = f"${o.filled_avg_price}" if o.filled_avg_price else "PENDING"
    print(f'{created_time}: {o.side} {o.qty} {o.symbol} @ {filled_price} - Status: {o.status}')

print(f'\n=== ANALYSIS ===')
print(f'Current Time: {datetime.now().strftime("%H:%M:%S")}')
print(f'Total Open Positions: {len(positions)}')
print(f'Total Recent Orders: {len(recent_orders)}')

# Check if any orders were placed before 10:00 AM today
today_early_orders = []
for o in recent_orders:
    if o.created_at.date() == datetime.now().date():
        order_time = o.created_at.time()
        if order_time < datetime.strptime("10:00", "%H:%M").time():
            today_early_orders.append(o)

if today_early_orders:
    print(f'\n🚨 VIOLATION DETECTED: {len(today_early_orders)} orders placed before 10:00 AM today!')
    for o in today_early_orders:
        print(f'   {o.created_at.strftime("%H:%M:%S")}: {o.side} {o.qty} {o.symbol} - SHOULD NOT HAVE EXECUTED')
else:
    print(f'\n✅ No early trading violations detected')
