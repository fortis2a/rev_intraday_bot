#!/usr/bin/env python3
"""
Test script to verify the date filtering fix in the dashboard
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# Add dashboard to path
sys.path.append(str(Path(__file__).parent / 'dashboard'))

# Import dashboard class
from interactive_dashboard import TradingDashboard

def test_date_filtering():
    """Test the date filtering functionality"""
    print("🧪 Testing Dashboard Date Filtering...")
    
    dashboard = TradingDashboard()
    # Don't setup the web server layout for testing
    
    # Test 1: Today's date (should show no data since market is closed)
    print("\n📅 Test 1: Today's date (2025-08-20)")
    today = datetime.now().date()
    df_today, account_today = dashboard.get_trading_data(
        start_date=datetime.combine(today, datetime.min.time()),
        end_date=datetime.combine(today, datetime.max.time())
    )
    
    print(f"   Result: {len(df_today)} orders found for today")
    if not df_today.empty:
        print(f"   Dates found: {sorted(df_today['date'].unique())}")
        print("   ❌ ERROR: Should show no data for today!")
    else:
        print("   ✅ CORRECT: No data for today (market closed)")
    
    # Test 2: Yesterday's date (should show data if any)
    print("\n📅 Test 2: Yesterday's date (2025-08-19)")
    yesterday = today - timedelta(days=1)
    df_yesterday, account_yesterday = dashboard.get_trading_data(
        start_date=datetime.combine(yesterday, datetime.min.time()),
        end_date=datetime.combine(yesterday, datetime.max.time())
    )
    
    print(f"   Result: {len(df_yesterday)} orders found for yesterday")
    if not df_yesterday.empty:
        print(f"   Dates found: {sorted(df_yesterday['date'].unique())}")
        # Check if all dates are within the requested range
        valid_dates = all(date == yesterday for date in df_yesterday['date'].unique())
        if valid_dates:
            print("   ✅ CORRECT: All data is from the requested date")
        else:
            print("   ❌ ERROR: Data contains dates outside the requested range!")
    
    # Test 3: Last week (should show data from multiple days)
    print("\n📅 Test 3: Last 7 days")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    df_week, account_week = dashboard.get_trading_data(
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"   Result: {len(df_week)} orders found for last 7 days")
    if not df_week.empty:
        print(f"   Date range found: {min(df_week['date'])} to {max(df_week['date'])}")
        # Check if dates are within range
        valid_range = all(
            start_date.date() <= date <= end_date.date() 
            for date in df_week['date'].unique()
        )
        if valid_range:
            print("   ✅ CORRECT: All data is within the requested date range")
        else:
            print("   ❌ ERROR: Data contains dates outside the requested range!")
    
    print("\n🏁 Date filtering test complete!")

if __name__ == "__main__":
    test_date_filtering()
