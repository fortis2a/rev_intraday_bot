#!/usr/bin/env python3
"""Debug yesterday's data calculation"""

import os
from datetime import date, datetime, timedelta

import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

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
    yesterday = today - timedelta(days=1)
    
    print(f"🔍 Debugging YESTERDAY's data: {yesterday}")
    print("=" * 60)
    
    # Get yesterday's activities
    try:
        yesterday_activities = api.get_activities(
            activity_types='FILL',
            date=yesterday.strftime('%Y-%m-%d'),
            direction='desc',
            page_size=100
        )
        
        print(f"✅ Raw count from Alpaca for {yesterday}: {len(yesterday_activities)} activities")
        
        if not yesterday_activities:
            print("❌ NO ACTIVITIES FOUND FOR YESTERDAY!")
            return
        
        # Calculate P&L the same way as the report
        total_cash_flow = 0
        total_volume = 0
        symbols = set()
        
        print(f"\n📋 YESTERDAY'S ACTIVITIES ({yesterday}):")
        print("-" * 60)
        
        for i, activity in enumerate(yesterday_activities[:10]):  # Show first 10
            symbol = activity.symbol
            side = activity.side
            qty = float(activity.qty)
            price = float(activity.price)
            value = qty * price
            
            symbols.add(symbol)
            total_volume += value
            
            # Calculate cash flow (THIS IS WHERE THE BUG MIGHT BE)
            if side in ['sell', 'sell_short']:
                cash_flow = value  # Money in
                total_cash_flow += cash_flow
                flow_sign = "+"
            else:  # buy
                cash_flow = -value  # Money out
                total_cash_flow += cash_flow
                flow_sign = ""
            
            print(f"{i+1:2d}. {activity.transaction_time.strftime('%H:%M:%S')} | "
                  f"{symbol:6s} | {side:10s} | {qty:6.0f} @ ${price:7.2f} | "
                  f"{flow_sign}${value:8.2f} | Flow: {flow_sign}${cash_flow:8.2f}")
        
        print("\n" + "=" * 60)
        print(f"📊 YESTERDAY'S CALCULATED SUMMARY:")
        print(f"   Total Activities: {len(yesterday_activities)}")
        print(f"   Unique Symbols: {len(symbols)}")
        print(f"   Total Volume: ${total_volume:.2f}")
        print(f"   Calculated P&L: ${total_cash_flow:.2f}")
        print(f"   Expected P&L: ~$61.0")
        print(f"   ERROR: ${total_cash_flow - 61.0:.2f}")
        
        print(f"\n📈 SYMBOLS TRADED YESTERDAY:")
        for symbol in symbols:
            print(f"   {symbol}")
            
    except Exception as e:
        print(f"❌ Error getting yesterday's activities: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
