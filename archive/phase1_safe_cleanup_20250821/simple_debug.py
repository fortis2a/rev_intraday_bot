#!/usr/bin/env python3
"""Simple debug to see what Alpaca returns for today only"""

import os
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

# Load environment variables
load_dotenv()

def main():
    # Initialize Alpaca API
    api = tradeapi.REST(
        os.getenv('ALPACA_API_KEY'),
        os.getenv('ALPACA_SECRET_KEY'),
        os.getenv('ALPACA_BASE_URL'),
        api_version='v2'
    )
    
    today = date.today()
    print(f"🔍 Checking Alpaca data for TODAY: {today}")
    print("=" * 60)
    
    # Get activities for today ONLY
    try:
        today_activities = api.get_activities(
            activity_types='FILL',
            date=today.strftime('%Y-%m-%d'),
            direction='desc',
            page_size=100
        )
        
        print(f"✅ Raw count from Alpaca: {len(today_activities)} activities")
        
        if not today_activities:
            print("❌ NO ACTIVITIES FOUND FOR TODAY!")
            return
        
        # Group by symbol
        symbols = {}
        total_cash_flow = 0
        
        print(f"\n📋 ALL ACTIVITIES FOR {today}:")
        print("-" * 60)
        
        for i, activity in enumerate(today_activities):
            symbol = activity.symbol
            side = activity.side
            qty = float(activity.qty)
            price = float(activity.price)
            value = qty * price
            
            # Calculate cash flow
            if side in ['sell', 'sell_short']:
                cash_flow = value  # Money in
                total_cash_flow += cash_flow
                flow_sign = "+"
            else:  # buy
                cash_flow = -value  # Money out
                total_cash_flow += cash_flow
                flow_sign = ""
            
            # Track by symbol
            if symbol not in symbols:
                symbols[symbol] = {'trades': 0, 'cash_flow': 0}
            symbols[symbol]['trades'] += 1
            symbols[symbol]['cash_flow'] += cash_flow
            
            print(f"{i+1:2d}. {activity.transaction_time.strftime('%H:%M:%S')} | "
                  f"{symbol:6s} | {side:10s} | {qty:6.0f} @ ${price:7.2f} | "
                  f"{flow_sign}${value:8.2f} | Flow: {flow_sign}${cash_flow:8.2f}")
        
        print("\n" + "=" * 60)
        print(f"📊 SUMMARY FOR {today}:")
        print(f"   Total Activities: {len(today_activities)}")
        print(f"   Unique Symbols: {len(symbols)}")
        print(f"   Total Cash Flow (P&L): ${total_cash_flow:.2f}")
        
        print(f"\n📈 BY SYMBOL:")
        for symbol, data in symbols.items():
            print(f"   {symbol}: {data['trades']} trades, ${data['cash_flow']:+.2f} P&L")
            
    except Exception as e:
        print(f"❌ Error getting activities: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
