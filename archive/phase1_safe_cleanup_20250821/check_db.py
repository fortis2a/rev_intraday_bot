#!/usr/bin/env python3
"""Check database structure"""

import sqlite3
from pathlib import Path

def check_database():
    db_path = Path("data/trading.db")
    
    if not db_path.exists():
        print("❌ Database file does not exist")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"✅ Database found at: {db_path}")
        print(f"📊 Tables: {[table[0] for table in tables]}")
        
        # Check if trades table exists and has data
        if ('trades',) in tables:
            cursor.execute("SELECT COUNT(*) FROM trades")
            trade_count = cursor.fetchone()[0]
            print(f"📈 Total trades in database: {trade_count}")
            
            # Get latest trade
            cursor.execute("SELECT * FROM trades ORDER BY entry_time DESC LIMIT 1")
            latest_trade = cursor.fetchone()
            if latest_trade:
                print(f"🕒 Latest trade: {latest_trade}")
        
        conn.close()
        print("✅ Database connection successful")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_database()
