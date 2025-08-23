#!/usr/bin/env python3
"""
Database Verification Script
Compare database cached data vs direct API calls
"""

import os
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.trading_db import TradingDatabase


def verify_database_accuracy():
    """Verify database data matches API data"""
    
    db = TradingDatabase()
    
    print("🔍 Database Verification Report")
    print("=" * 50)
    
    # Check yesterday's data (8/19/25)
    yesterday = date(2025, 8, 19)
    
    print(f"\n📅 Checking data for {yesterday}")
    
    # Get from database
    db_summary = db.get_daily_summary(yesterday)
    db_activities = db.get_activities(yesterday)
    
    if db_summary:
        print(f"✅ Database Summary:")
        print(f"   • Total Trades: {db_summary['total_trades']}")
        print(f"   • Net P&L: ${db_summary['net_pnl']:.2f}")
        print(f"   • Symbols: {db_summary['symbols_traded']}")
        print(f"   • Unique Symbols: {db_summary['unique_symbols']}")
        print(f"   • Total Volume: ${db_summary['total_volume']:,.2f}")
    
    # Get direct from API for comparison
    try:
        print(f"\n🔄 Fetching fresh data from API...")
        api_activities = db.api.get_activities(
            activity_types='FILL',
            date=yesterday.strftime('%Y-%m-%d'),
            direction='desc',
            page_size=100
        )
        
        if api_activities:
            # Calculate API metrics
            api_count = len(api_activities)
            
            # Calculate P&L using cash flow method
            side_totals = {}
            total_volume = 0
            symbols = set()
            
            for activity in api_activities:
                side = activity.side
                value = float(activity.qty) * float(activity.price)
                
                if side not in side_totals:
                    side_totals[side] = 0
                side_totals[side] += value
                
                total_volume += value
                symbols.add(activity.symbol)
            
            # Calculate net P&L (sells + short_sells - buys)
            sells = side_totals.get('sell', 0) + side_totals.get('sell_short', 0)
            buys = side_totals.get('buy', 0)
            api_pnl = sells - buys
            
            print(f"📡 Fresh API Data:")
            print(f"   • Total Trades: {api_count}")
            print(f"   • Net P&L: ${api_pnl:.2f}")
            print(f"   • Symbols: {', '.join(sorted(symbols))}")
            print(f"   • Unique Symbols: {len(symbols)}")
            print(f"   • Total Volume: ${total_volume:,.2f}")
            
            # Compare
            print(f"\n⚖️  Comparison:")
            trades_match = db_summary['total_trades'] == api_count
            pnl_match = abs(db_summary['net_pnl'] - api_pnl) < 0.01
            symbols_match = db_summary['unique_symbols'] == len(symbols)
            
            print(f"   • Trades Match: {'✅' if trades_match else '❌'} ({db_summary['total_trades']} vs {api_count})")
            print(f"   • P&L Match: {'✅' if pnl_match else '❌'} (${db_summary['net_pnl']:.2f} vs ${api_pnl:.2f})")
            print(f"   • Symbols Match: {'✅' if symbols_match else '❌'} ({db_summary['unique_symbols']} vs {len(symbols)})")
            
            if trades_match and pnl_match and symbols_match:
                print(f"\n🎉 DATABASE ACCURACY: PERFECT MATCH!")
            else:
                print(f"\n⚠️  DATABASE ACCURACY: DISCREPANCIES FOUND")
        
        else:
            print(f"📭 No API activities found for {yesterday}")
            
    except Exception as e:
        print(f"❌ Error fetching API data: {str(e)}")
    
    # Show collection status
    print(f"\n📊 Collection Status:")
    status_df = db.get_collection_status()
    print(status_df.to_string(index=False))
    
    # Show recent database activities
    print(f"\n📋 Recent Database Activities (last 5):")
    if not db_activities.empty:
        recent = db_activities.tail(5)[['transaction_time', 'symbol', 'side', 'quantity', 'price', 'value']]
        print(recent.to_string(index=False))
    else:
        print("No activities found in database")

if __name__ == "__main__":
    verify_database_accuracy()
