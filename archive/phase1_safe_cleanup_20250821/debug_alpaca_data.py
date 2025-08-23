#!/usr/bin/env python3
"""Debug script to see exactly what Alpaca is returning"""

import os
from datetime import datetime, timedelta

import alpaca_trade_api as tradeapi
import pandas as pd
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
    
    print("🔍 DEBUGGING ALPACA DATA")
    print("=" * 50)
    
    # Get today's date
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    print(f"📅 Checking data for: {today}")
    print(f"📅 Yesterday: {yesterday}")
    
    # Get activities for today
    print("\n🔄 Getting TODAY'S ACTIVITIES...")
    try:
        today_activities = api.get_activities(
            activity_types='FILL',
            date=today.strftime('%Y-%m-%d'),
            direction='desc',
            page_size=100
        )
        print(f"✅ Found {len(today_activities)} activities today")
        
        # Print details of first few activities
        for i, activity in enumerate(today_activities[:5]):
            print(f"\n📋 Activity {i+1}:")
            print(f"   Symbol: {activity.symbol}")
            print(f"   Side: {activity.side}")
            print(f"   Qty: {activity.qty}")
            print(f"   Price: {activity.price}")
            print(f"   Value: ${float(activity.qty) * float(activity.price):.2f}")
            print(f"   Time: {activity.transaction_time}")
            print(f"   ID: {activity.id}")
            
    except Exception as e:
        print(f"❌ Error getting today's activities: {e}")
        today_activities = []
    
    # Get orders for today (for comparison)
    print("\n🔄 Getting TODAY'S ORDERS...")
    try:
        today_orders = api.list_orders(
            status='filled',
            after=today.strftime('%Y-%m-%d'),
            direction='desc',
            limit=100
        )
        print(f"✅ Found {len(today_orders)} filled orders today")
        
        # Print details of first few orders
        for i, order in enumerate(today_orders[:5]):
            print(f"\n📋 Order {i+1}:")
            print(f"   Symbol: {order.symbol}")
            print(f"   Side: {order.side}")
            print(f"   Qty: {order.filled_qty}")
            print(f"   Price: {order.filled_avg_price}")
            print(f"   Value: ${float(order.filled_qty) * float(order.filled_avg_price):.2f}")
            print(f"   Time: {order.filled_at}")
            print(f"   ID: {order.id}")
            
    except Exception as e:
        print(f"❌ Error getting today's orders: {e}")
        today_orders = []
    
    # Calculate actual P&L from activities
    print("\n💰 CALCULATING ACTUAL P&L FROM ACTIVITIES...")
    total_cash_flow = 0
    for activity in today_activities:
        value = float(activity.qty) * float(activity.price)
        if activity.side in ['sell', 'sell_short']:
            cash_flow = value  # Money in
            total_cash_flow += cash_flow
            print(f"   {activity.symbol} {activity.side}: +${value:.2f}")
        else:  # buy
            cash_flow = -value  # Money out
            total_cash_flow += cash_flow
            print(f"   {activity.symbol} {activity.side}: -${value:.2f}")
    
    print(f"\n📊 ACTUAL P&L FROM ACTIVITIES: ${total_cash_flow:.2f}")
    
    # Show what the market close report is calculating
    print("\n🔍 CHECKING WHAT MARKET CLOSE REPORT SEES...")
    from market_close_report import MarketCloseReportGenerator
    
    generator = MarketCloseReportGenerator()
    
    # Get the data the same way the report does
    today_data = generator.get_extended_orders(today.strftime('%Y-%m-%d'))
    yesterday_data = generator.get_extended_orders(yesterday.strftime('%Y-%m-%d'))
    
    print(f"📈 Report sees {len(today_data)} today items")
    print(f"📈 Report sees {len(yesterday_data)} yesterday items")
    
    if today_data:
        print("\n📋 First 3 items from report data:")
        for i, item in enumerate(today_data[:3]):
            print(f"   Item {i+1}: {item}")

if __name__ == "__main__":
    main()
