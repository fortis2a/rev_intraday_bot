#!/usr/bin/env python3
"""
Show ALL orders including pending/accepted ones
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from alpaca.trading.client import TradingClient

from config import ALPACA_API_KEY, ALPACA_SECRET_KEY


def show_all_orders():
    """Show all orders including pending ones"""
    print("\n📋 ALL ORDERS STATUS 📋")
    print("=" * 40)

    try:
        client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)

        # Get all orders
        orders = client.get_orders()

        if not orders:
            print("📭 No orders found")
            return

        print(f"Found {len(orders)} total orders:")
        print()

        for i, order in enumerate(orders, 1):
            print(f"[{i}] {order.symbol}")
            print(f"    ID: {order.id}")
            print(f"    Side: {order.side.name}")
            print(f"    Qty: {order.qty}")
            print(f"    Type: {order.order_type.name}")
            print(f"    Status: {order.status.name}")
            print(f"    Time in Force: {order.time_in_force.name}")
            if hasattr(order, "submitted_at"):
                print(f"    Submitted: {order.submitted_at}")
            print()

        # Check market status
        clock = client.get_clock()
        print(f"📈 Market Status: {'OPEN' if clock.is_open else 'CLOSED'}")

        if not clock.is_open:
            print(f"📅 Next market open: {clock.next_open}")
            print()
            print("💡 EXPLANATION:")
            print("   The close orders are queued and will execute when market opens.")
            print("   Your positions will be automatically closed at market open.")
            print("   This is normal behavior for after-hours order submission.")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    show_all_orders()
