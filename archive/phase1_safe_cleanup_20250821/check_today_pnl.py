#!/usr/bin/env python3
"""
Check Alpaca P&L for 8/20/25
Since 8/20 data is available, let's get the actual P&L
"""

import sys
import os
from pathlib import Path
from datetime import date

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from alpaca_pnl_fetcher import AlpacaPnLFetcher
from update_database_schema import update_with_alpaca_pnl

def check_today_pnl():
    """Check and update today's P&L data"""
    
    fetcher = AlpacaPnLFetcher()
    today = date(2025, 8, 20)
    
    print(f"🔍 Checking Alpaca P&L for {today}")
    print("=" * 40)
    
    # Try to get today's P&L
    result = fetcher.get_daily_pnl(today)
    
    if result.get('error'):
        print(f"❌ Alpaca P&L Error: {result['error']}")
        
        # Check what the latest available date is
        try:
            portfolio_history = fetcher.api.get_portfolio_history(
                period='1M',
                timeframe='1D'
            )
            
            if portfolio_history and portfolio_history.timestamp:
                print(f"\n📅 Available Portfolio History:")
                timestamps = portfolio_history.timestamp
                profit_loss = portfolio_history.profit_loss
                
                # Show last 5 days
                for i in range(max(0, len(timestamps)-5), len(timestamps)):
                    from datetime import datetime
                    ts_date = datetime.fromtimestamp(timestamps[i]).date()
                    pnl = profit_loss[i]
                    print(f"   {ts_date}: ${pnl:.2f}")
                    
        except Exception as e:
            print(f"❌ Error checking portfolio history: {str(e)}")
    else:
        print(f"✅ Alpaca P&L found: ${result['alpaca_pnl']:.2f}")
        
        # Update database
        import sqlite3
        db_path = Path("data/trading.db")
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE daily_summaries 
                SET alpaca_pnl = ?, trading_pnl = ?, updated_at = CURRENT_TIMESTAMP
                WHERE trade_date = ?
            """, (result['alpaca_pnl'], result['alpaca_pnl'], today))
            
            if cursor.rowcount > 0:
                print(f"✅ Database updated with Alpaca P&L")
            else:
                print(f"❌ No database record found for {today}")
            
            conn.commit()
    
    # Show current database status
    print(f"\n📊 Current Database Status:")
    import sqlite3
    db_path = Path("data/trading.db")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT trade_date, total_trades, cash_flow_pnl, alpaca_pnl, trading_pnl 
            FROM daily_summaries 
            ORDER BY trade_date DESC 
            LIMIT 3
        """)
        
        rows = cursor.fetchall()
        if rows:
            print(f"   {'Date':<12} {'Trades':<8} {'Cash Flow':<12} {'Alpaca P&L':<12} {'Trading P&L':<12}")
            print(f"   {'-'*12} {'-'*8} {'-'*12} {'-'*12} {'-'*12}")
            for row in rows:
                date_str, trades, cash_flow, alpaca_pnl, trading_pnl = row
                print(f"   {date_str:<12} {trades:<8} ${cash_flow:<11.2f} ${alpaca_pnl:<11.2f} ${trading_pnl:<11.2f}")

if __name__ == "__main__":
    check_today_pnl()
