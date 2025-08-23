#!/usr/bin/env python3
"""
Update Database Schema for Alpaca P&L
Add trading_pnl column and update with Alpaca's actual P&L data
"""

import sqlite3
import sys
import os
from pathlib import Path
from datetime import date

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from alpaca_pnl_fetcher import AlpacaPnLFetcher


def update_database_schema():
    """Update database schema to include Alpaca P&L fields"""

    db_path = Path("data/trading.db")

    print("🔧 Updating Database Schema for Alpaca P&L")
    print("=" * 50)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Add new columns to daily_summaries table
        try:
            # First, rename the old net_pnl column to cash_flow_pnl if it exists
            cursor.execute("PRAGMA table_info(daily_summaries)")
            columns = [col[1] for col in cursor.fetchall()]

            print(f"📊 Current columns: {columns}")

            if "net_pnl" in columns and "cash_flow_pnl" not in columns:
                print("🔄 Renaming net_pnl to cash_flow_pnl...")
                cursor.execute(
                    "ALTER TABLE daily_summaries RENAME COLUMN net_pnl TO cash_flow_pnl"
                )

            # Add trading_pnl column if it doesn't exist
            if "trading_pnl" not in columns:
                print("➕ Adding trading_pnl column...")
                cursor.execute(
                    "ALTER TABLE daily_summaries ADD COLUMN trading_pnl REAL DEFAULT 0"
                )

            # Add alpaca_pnl column for the source of truth
            if "alpaca_pnl" not in columns:
                print("➕ Adding alpaca_pnl column...")
                cursor.execute(
                    "ALTER TABLE daily_summaries ADD COLUMN alpaca_pnl REAL DEFAULT 0"
                )

            # Add positions tracking columns if they don't exist
            if "positions_opened" not in columns:
                print("➕ Adding positions_opened column...")
                cursor.execute(
                    "ALTER TABLE daily_summaries ADD COLUMN positions_opened INTEGER DEFAULT 0"
                )

            if "positions_closed" not in columns:
                print("➕ Adding positions_closed column...")
                cursor.execute(
                    "ALTER TABLE daily_summaries ADD COLUMN positions_closed INTEGER DEFAULT 0"
                )

            if "day_trades" not in columns:
                print("➕ Adding day_trades column...")
                cursor.execute(
                    "ALTER TABLE daily_summaries ADD COLUMN day_trades INTEGER DEFAULT 0"
                )

            conn.commit()
            print("✅ Database schema updated successfully")

        except Exception as e:
            print(f"❌ Error updating schema: {str(e)}")
            return False

    return True


def update_with_alpaca_pnl():
    """Update database with Alpaca's actual P&L data"""

    db_path = Path("data/trading.db")
    fetcher = AlpacaPnLFetcher()

    print("\n💰 Updating with Alpaca's Actual P&L")
    print("=" * 40)

    # Dates to update
    dates_to_update = [date(2025, 8, 18), date(2025, 8, 19)]

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        for target_date in dates_to_update:
            print(f"\n📅 Processing {target_date}...")

            # Get Alpaca's actual P&L
            alpaca_result = fetcher.get_daily_pnl(target_date)

            if alpaca_result.get("error"):
                print(f"   ❌ Alpaca Error: {alpaca_result['error']}")
                continue

            alpaca_pnl = alpaca_result["alpaca_pnl"]
            print(f"   💰 Alpaca P&L: ${alpaca_pnl:.2f}")

            # Update database
            cursor.execute(
                """
                UPDATE daily_summaries 
                SET alpaca_pnl = ?, trading_pnl = ?, updated_at = CURRENT_TIMESTAMP
                WHERE trade_date = ?
            """,
                (alpaca_pnl, alpaca_pnl, target_date),
            )

            if cursor.rowcount > 0:
                print(f"   ✅ Updated database")
            else:
                print(f"   ❌ No rows updated - check if summary exists")

        conn.commit()

    # Verify updates
    print(f"\n📊 Verification:")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT trade_date, total_trades, cash_flow_pnl, alpaca_pnl, trading_pnl 
            FROM daily_summaries 
            ORDER BY trade_date DESC 
            LIMIT 5
        """
        )

        rows = cursor.fetchall()
        if rows:
            print(
                f"   {'Date':<12} {'Trades':<8} {'Cash Flow':<12} {'Alpaca P&L':<12} {'Trading P&L':<12}"
            )
            print(f"   {'-'*12} {'-'*8} {'-'*12} {'-'*12} {'-'*12}")
            for row in rows:
                date_str, trades, cash_flow, alpaca_pnl, trading_pnl = row
                print(
                    f"   {date_str:<12} {trades:<8} ${cash_flow:<11.2f} ${alpaca_pnl:<11.2f} ${trading_pnl:<11.2f}"
                )
        else:
            print(f"   No data found in daily_summaries")


if __name__ == "__main__":
    # Update schema first
    if update_database_schema():
        # Then update with Alpaca P&L
        update_with_alpaca_pnl()
    else:
        print("❌ Schema update failed, skipping P&L update")
