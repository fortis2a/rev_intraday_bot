#!/usr/bin/env python3
"""
Simple test script to verify date filtering works correctly
"""

import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_date_filtering_simple():
    """Test date filtering using direct API calls"""
    print("🧪 Testing Date Filtering Logic...")
    
    # Initialize API
    api = tradeapi.REST(
        os.getenv('ALPACA_API_KEY'),
        os.getenv('ALPACA_SECRET_KEY'),
        base_url=os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    )
    
    # Test today's date
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    print(f"\n📅 Testing date: {today} (today)")
    print(f"📅 Yesterday: {yesterday}")
    
    # Fetch orders with buffer (like the dashboard does)
    start_date = datetime.combine(today, datetime.min.time())
    end_date = datetime.combine(today, datetime.max.time())
    buffer_start = start_date - timedelta(days=1)
    
    print(f"🔍 Fetching orders from {buffer_start.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    try:
        orders = api.list_orders(
            status='all',
            after=buffer_start.strftime('%Y-%m-%dT%H:%M:%SZ')
        )
        
        filled_orders = [o for o in orders if o.status == 'filled']
        print(f"📊 Found {len(filled_orders)} filled orders total")
        
        if filled_orders:
            # Convert to DataFrame
            orders_data = []
            for order in filled_orders:
                orders_data.append({
                    'symbol': order.symbol,
                    'side': order.side,
                    'filled_at': order.filled_at,
                    'price': float(order.filled_avg_price)
                })
            
            df = pd.DataFrame(orders_data)
            df['date'] = df['filled_at'].dt.date
            
            print(f"📅 Dates in raw data: {sorted(df['date'].unique())}")
            
            # Apply the filter
            start_date_only = start_date.date()
            end_date_only = end_date.date()
            df_filtered = df[(df['date'] >= start_date_only) & (df['date'] <= end_date_only)]
            
            print(f"🎯 After filtering to {start_date_only} - {end_date_only}:")
            print(f"   Original orders: {len(df)}")
            print(f"   Filtered orders: {len(df_filtered)}")
            
            if not df_filtered.empty:
                print(f"   Filtered dates: {sorted(df_filtered['date'].unique())}")
                print("   ❌ ERROR: Should show no orders for today!")
            else:
                print("   ✅ CORRECT: No orders for today (market closed)")
                
        else:
            print("   ✅ CORRECT: No filled orders found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_date_filtering_simple()
