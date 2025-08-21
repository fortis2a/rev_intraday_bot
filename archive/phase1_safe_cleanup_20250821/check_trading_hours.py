#!/usr/bin/env python3
"""Check Trading Hours Status"""

from datetime import datetime
import sys
sys.path.append('.')
from config import TRADING_START, TRADING_END

now = datetime.now()
current_time = now.strftime('%H:%M')

print('=== TRADING HOURS RESTRICTIONS ===')
print(f'Current Time: {current_time}')
print(f'Market Opens: 09:30 (Real market open)')
print(f'Trading Starts: {TRADING_START} (30 min buffer)')
print(f'Trading Ends: {TRADING_END} (30 min before close)')
print(f'Market Closes: 16:00 (Real market close)')
print('')

is_trading_hours = TRADING_START <= current_time <= TRADING_END
print(f'✅ Trading Allowed: {is_trading_hours}')

if is_trading_hours:
    print('📊 Status: Trading is ACTIVE')
else:
    if current_time < TRADING_START:
        minutes_left = (int(TRADING_START.split(':')[0]) * 60 + int(TRADING_START.split(':')[1])) - (now.hour * 60 + now.minute)
        print(f'⏸️ Status: Trading PAUSED (starts in {minutes_left} minutes at {TRADING_START})')
    else:
        print('⏸️ Status: Trading CLOSED for the day')

print('')
print('🛡️ SAFETY RESTRICTIONS:')
print('   • NO trading first 30 minutes (9:30-10:00 AM)')
print('   • NO trading last 30 minutes (3:30-4:00 PM)')
print('   • Avoids high volatility periods')
print('   • Prevents opening/closing auction interference')
