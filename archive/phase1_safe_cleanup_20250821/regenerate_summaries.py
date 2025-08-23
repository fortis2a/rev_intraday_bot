#!/usr/bin/env python3
"""
Regenerate Database Summaries with Enhanced P&L
Update existing daily summaries to include trading P&L
"""

import os
import sys
from datetime import date
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.trading_db import TradingDatabase


def regenerate_summaries():
    """Regenerate daily summaries with enhanced P&L"""

    db = TradingDatabase()

    print("🔄 Regenerating Daily Summaries with Enhanced P&L")
    print("=" * 55)

    # Get dates that have data
    dates_to_update = [date(2025, 8, 18), date(2025, 8, 19)]

    for target_date in dates_to_update:
        print(f"\n📅 Updating {target_date}...")

        # Check if data exists
        if db._date_exists(target_date):
            # Regenerate summary
            db._generate_daily_summary(target_date)

            # Get updated summary
            summary = db.get_daily_summary(target_date)
            if summary:
                print(f"   ✅ Updated: {summary['total_trades']} trades")
                print(f"   💰 Cash Flow P&L: ${summary['cash_flow_pnl']:,.2f}")
                print(f"   📊 Trading P&L: ${summary['trading_pnl']:,.2f}")
                print(
                    f"   🎯 Positions: {summary['positions_opened']} opened, {summary['positions_closed']} closed"
                )
                print(f"   ⚡ Day Trades: {summary['day_trades']}")
            else:
                print(f"   ❌ Failed to get updated summary")
        else:
            print(f"   ⏭️  No data for {target_date}")

    print(f"\n📊 Final Status:")
    status_df = db.get_collection_status()
    print(status_df.to_string(index=False))


if __name__ == "__main__":
    regenerate_summaries()
