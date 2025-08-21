#!/usr/bin/env python3
"""
Three-Day Trading Summary
Complete overview of 8/18, 8/19, and 8/20 trading performance
"""

import sys
import os
from pathlib import Path
from datetime import date
import sqlite3

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def generate_three_day_summary():
    """Generate summary for the three trading days"""
    
    print("📊 THREE-DAY TRADING SUMMARY")
    print("=" * 60)
    print("Database System with Alpaca P&L Integration")
    print()
    
    # Connect to database
    db_path = Path("data/trading.db")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Get all three days
        cursor.execute("""
            SELECT 
                trade_date, 
                total_trades, 
                unique_symbols,
                symbols_traded,
                cash_flow_pnl, 
                alpaca_pnl, 
                trading_pnl,
                total_volume
            FROM daily_summaries 
            WHERE trade_date IN ('2025-08-18', '2025-08-19', '2025-08-20')
            ORDER BY trade_date
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("❌ No data found for the three days")
            return
        
        total_trades = 0
        total_cash_flow = 0
        total_alpaca_pnl = 0
        total_volume = 0
        all_symbols = set()
        
        print(f"{'Date':<12} {'Trades':<8} {'Symbols':<8} {'Cash Flow':<12} {'Alpaca P&L':<12} {'Status':<15}")
        print(f"{'-'*12} {'-'*8} {'-'*8} {'-'*12} {'-'*12} {'-'*15}")
        
        for row in rows:
            date_str, trades, unique_symbols, symbols_traded, cash_flow, alpaca_pnl, trading_pnl, volume = row
            
            # Accumulate totals
            total_trades += trades
            total_cash_flow += cash_flow
            total_alpaca_pnl += alpaca_pnl
            total_volume += volume
            
            if symbols_traded:
                all_symbols.update(symbols_traded.split(','))
            
            # Determine data source
            if abs(cash_flow - alpaca_pnl) < 0.01:
                status = "Cash Flow" if date_str == '2025-08-20' else "Alpaca P&L"
            else:
                status = "Alpaca P&L"
            
            print(f"{date_str:<12} {trades:<8} {unique_symbols:<8} ${cash_flow:<11.2f} ${alpaca_pnl:<11.2f} {status:<15}")
        
        print(f"{'-'*12} {'-'*8} {'-'*8} {'-'*12} {'-'*12} {'-'*15}")
        print(f"{'TOTAL':<12} {total_trades:<8} {len(all_symbols):<8} ${total_cash_flow:<11.2f} ${total_alpaca_pnl:<11.2f}")
        
        # Performance analysis
        print(f"\n📈 PERFORMANCE ANALYSIS:")
        print(f"   • Total Trades: {total_trades}")
        print(f"   • Unique Symbols: {len(all_symbols)}")
        print(f"   • Total Volume: ${total_volume:,.2f}")
        print(f"   • Net Alpaca P&L: ${total_alpaca_pnl:.2f}")
        print(f"   • Average per Trade: ${total_alpaca_pnl/total_trades:.2f}")
        print(f"   • Symbols Traded: {', '.join(sorted(all_symbols))}")
        
        # Daily breakdown
        print(f"\n📅 DAILY BREAKDOWN:")
        for row in rows:
            date_str, trades, unique_symbols, symbols_traded, cash_flow, alpaca_pnl, trading_pnl, volume = row
            
            avg_per_trade = alpaca_pnl / trades if trades > 0 else 0
            pnl_icon = "📈" if alpaca_pnl > 0 else "📉" if alpaca_pnl < 0 else "➡️"
            
            print(f"   {pnl_icon} {date_str}: {trades} trades, ${alpaca_pnl:.2f} P&L (${avg_per_trade:.2f}/trade)")
            if symbols_traded:
                print(f"     Symbols: {symbols_traded}")
        
        # Data source notes
        print(f"\n📊 DATA SOURCE NOTES:")
        print(f"   • 8/18 & 8/19: Alpaca Portfolio History (includes fees/commissions)")
        print(f"   • 8/20: Cash Flow (Alpaca P&L updates after market close)")
        print(f"   • System automatically uses Alpaca as source of truth when available")
        
        # Collection status
        cursor.execute("""
            SELECT collection_date, activities_fetched, status 
            FROM collection_log 
            WHERE collection_date IN ('2025-08-18', '2025-08-19', '2025-08-20')
            ORDER BY collection_date
        """)
        
        collection_rows = cursor.fetchall()
        
        if collection_rows:
            print(f"\n📋 COLLECTION STATUS:")
            for col_date, activities, status in collection_rows:
                status_icon = "✅" if status == "SUCCESS" else "❌"
                print(f"   {status_icon} {col_date}: {activities} activities collected")

if __name__ == "__main__":
    generate_three_day_summary()
