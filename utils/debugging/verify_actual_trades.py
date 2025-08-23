#!/usr/bin/env python3
"""
Verify Actual Trades Script
Check what actual trades are being pulled for the dashboard
"""

import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_manager import DataManager


def verify_actual_trades():
    """Verify what actual trades exist"""

    print("=" * 70)
    print("VERIFYING ACTUAL TRADE DATA")
    print("=" * 70)

    try:
        # Initialize data manager
        dm = DataManager()
        api = dm.api

        # Check orders from last 30 days
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        print(f"📅 Checking orders from {start_date} to now")

        # Get filled orders only
        orders = api.list_orders(
            status="filled", limit=500, nested=False, after=start_date
        )

        print(f"\n📊 RESULTS:")
        print(f"   Total filled orders: {len(orders)}")

        if len(orders) > 0:
            print(f"\n🔍 SAMPLE ORDERS (first 5):")
            for i, order in enumerate(orders[:5]):
                print(
                    f"   {i+1}. {order.symbol} | {order.side} | {order.filled_qty} shares | ${order.filled_avg_price} | {order.filled_at}"
                )

            # Group by symbol
            by_symbol = {}
            for order in orders:
                symbol = order.symbol
                if symbol not in by_symbol:
                    by_symbol[symbol] = {"count": 0, "volume": 0}
                by_symbol[symbol]["count"] += 1
                if order.filled_qty:
                    by_symbol[symbol]["volume"] += float(order.filled_qty)

            print(f"\n📈 BY SYMBOL:")
            for symbol, data in sorted(
                by_symbol.items(), key=lambda x: x[1]["count"], reverse=True
            ):
                print(
                    f"   {symbol}: {data['count']} orders, {data['volume']:.0f} shares"
                )

        else:
            print("   ❌ No filled orders found")

        print("\n" + "=" * 70)
        print("VERIFICATION COMPLETE")
        print("=" * 70)

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    verify_actual_trades()
