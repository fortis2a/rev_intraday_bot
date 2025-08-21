#!/usr/bin/env python3
"""Check trading_activities table structure"""

import sqlite3
from pathlib import Path

def check_table_structure():
    db_path = Path("data/trading.db")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get table structure
        cursor.execute("PRAGMA table_info(trading_activities)")
        columns = cursor.fetchall()
        
        print("Trading activities table structure:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Get sample data
        cursor.execute("SELECT * FROM trading_activities LIMIT 3")
        samples = cursor.fetchall()
        
        print(f"\nSample data ({len(samples)} rows):")
        for sample in samples:
            print(f"  {sample}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_table_structure()
