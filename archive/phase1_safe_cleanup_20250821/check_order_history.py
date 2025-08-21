#!/usr/bin/env python3
"""Check Complete Order History"""

from alpaca.trading.client import TradingClient
from config import ALPACA_API_KEY, ALPACA_SECRET_KEY
from datetime import datetime, timedelta

# Connect to Alpaca
client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)

# Get all recent orders
orders = client.get_orders()
print('=== ALL RECENT ORDERS (Last 50) ===')

for i, o in enumerate(orders[:50]):
    created_time = o.created_at.strftime('%Y-%m-%d %H:%M:%S')
    filled_price = f"${o.filled_avg_price}" if o.filled_avg_price else "PENDING"
    print(f'{i+1:2d}. {created_time}: {o.side} {o.qty} {o.symbol} @ {filled_price} - {o.status}')

# Check specifically for SOFI orders today
print(f'\n=== SOFI ORDERS TODAY ===')
today = datetime.now().date()
sofi_today = [o for o in orders if o.symbol == 'SOFI' and o.created_at.date() == today]

for o in sofi_today:
    created_time = o.created_at.strftime('%H:%M:%S')
    filled_price = f"${o.filled_avg_price}" if o.filled_avg_price else "PENDING"
    print(f'{created_time}: {o.side} {o.qty} SOFI @ {filled_price} - {o.status}')
    
    # Check if this violates trading hours
    order_time = o.created_at.time()
    if order_time < datetime.strptime("10:00", "%H:%M").time():
        print(f'   🚨 VIOLATION: Order placed at {created_time} (before 10:00 AM)')
    else:
        print(f'   ✅ OK: Order placed during allowed hours')

if not sofi_today:
    print('No SOFI orders found today - position may be from previous day')
    
    # Check recent SOFI orders
    sofi_recent = [o for o in orders if o.symbol == 'SOFI'][:5]
    print(f'\n=== RECENT SOFI ORDERS (Last 5) ===')
    for o in sofi_recent:
        created_time = o.created_at.strftime('%Y-%m-%d %H:%M:%S')
        filled_price = f"${o.filled_avg_price}" if o.filled_avg_price else "PENDING"
        print(f'{created_time}: {o.side} {o.qty} SOFI @ {filled_price} - {o.status}')
