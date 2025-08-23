#!/usr/bin/env python3
"""
Simple Close All - Cancel stop orders, then close positions
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, OrderSide, TimeInForce
from config import ALPACA_API_KEY, ALPACA_SECRET_KEY


def simple_close_all():
    """Cancel stop orders then close all positions"""
    print("\n🎯 SIMPLE CLOSE ALL 🎯")
    print("=" * 40)

    try:
        client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)

        # Step 1: Cancel all orders
        print("🗑️ Cancelling all orders...")
        try:
            client.cancel_orders()
            print("✅ All orders cancelled")
        except Exception as e:
            print(f"⚠️ Cancel error: {e}")

        # Step 2: Get positions and close them
        print("\n📊 Getting positions...")
        positions = client.get_all_positions()

        if not positions:
            print("✅ No positions to close")
            return

        print(f"Found {len(positions)} positions to close:")

        for pos in positions:
            symbol = pos.symbol
            qty = abs(int(float(pos.qty)))
            side = pos.side.name

            print(f"\n🔄 Closing {symbol}: {side} {qty} shares")

            try:
                # Determine order side
                order_side = OrderSide.SELL if side == "LONG" else OrderSide.BUY

                # Create market order to close
                market_order_data = MarketOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=order_side,
                    time_in_force=TimeInForce.DAY,
                )

                order = client.submit_order(order_data=market_order_data)
                print(f"✅ Order submitted: {order.id}")

            except Exception as e:
                print(f"❌ Failed to close {symbol}: {e}")

        print(f"\n🔍 Checking final positions...")
        final_positions = client.get_all_positions()

        if final_positions:
            print(f"⚠️ {len(final_positions)} positions still open:")
            for pos in final_positions:
                print(f"  • {pos.symbol}: {pos.qty} shares")
        else:
            print("🎉 ALL POSITIONS CLOSED!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    simple_close_all()
