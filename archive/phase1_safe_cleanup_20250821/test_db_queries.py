#!/usr/bin/env python3
"""Test database connection for realtime monitor"""

import sqlite3
from pathlib import Path
from datetime import datetime

def test_database_queries():
    db_path = Path("data/trading.db")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("✅ Database connected")
        
        # Test the queries used in realtime monitor
        print("\n🔍 Testing queries...")
        
        # 1. Get latest daily summary
        cursor.execute("""
            SELECT trade_date, total_trades, cash_flow_pnl, alpaca_pnl, total_volume
            FROM daily_summaries 
            ORDER BY trade_date DESC 
            LIMIT 1
        """)
        latest_day = cursor.fetchone()
        print(f"Latest daily summary: {latest_day}")
        
        # 2. Get today's activities
        today_str = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM trading_activities WHERE DATE(timestamp) = ?", (today_str,))
        today_count = cursor.fetchone()[0]
        print(f"Today's activities count: {today_count}")
        
        conn.close()
        print("✅ All queries successful")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_queries()
