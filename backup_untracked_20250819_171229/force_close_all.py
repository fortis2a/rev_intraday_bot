#!/usr/bin/env python3
"""
Force Close All Positions Individually
More aggressive approach when API close_all fails
"""

import sys
import time
from pathlib import Path

import alpaca_trade_api as tradeapi

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from config import config


def force_close_all_individually():
    """Force close each position individually"""
    print("\n🔥 FORCE CLOSE ALL POSITIONS INDIVIDUALLY 🔥")
    print("=" * 60)

    try:
        # Connect to Alpaca
        api = tradeapi.REST(
            config["ALPACA_API_KEY"],
            config["ALPACA_SECRET_KEY"],
            config["ALPACA_BASE_URL"],
        )

        print("🔗 Connected to Alpaca API")

        # Get positions
        positions = api.list_positions()

        if not positions:
            print("📭 No positions found to close")
            return

        print(f"\n🎯 Force closing {len(positions)} positions individually...")

        closed_count = 0
        failed_symbols = []

        for i, pos in enumerate(positions, 1):
            symbol = pos.symbol
            qty = int(pos.qty)
            abs_qty = abs(qty)
            side = "LONG" if qty > 0 else "SHORT"
            pnl = float(pos.unrealized_pl)

            print(
                f"\n[{i}/{len(positions)}] Closing {symbol}: {side} {abs_qty} shares (P&L: ${pnl:.2f})"
            )

            try:
                # Determine order side to close position
                if qty > 0:
                    # Close long position with sell order
                    order_side = "sell"
                    print(f"  📤 Selling {abs_qty} shares of {symbol}")
                else:
                    # Close short position with buy order
                    order_side = "buy"
                    print(f"  📥 Buying {abs_qty} shares to cover {symbol} short")

                # Submit market order to close
                order = api.submit_order(
                    symbol=symbol,
                    qty=abs_qty,
                    side=order_side,
                    type="market",
                    time_in_force="day",
                )

                print(f"  ✅ Order submitted: {order.id} ({order.status})")
                closed_count += 1

                # Small delay between orders
                time.sleep(0.5)

            except Exception as e:
                print(f"  ❌ Failed to close {symbol}: {e}")
                failed_symbols.append(symbol)

        print(f"\n📊 RESULTS:")
        print(f"✅ Successfully closed: {closed_count}/{len(positions)} positions")

        if failed_symbols:
            print(f"❌ Failed to close: {', '.join(failed_symbols)}")
        else:
            print("🎉 All positions closed successfully!")

        # Check remaining positions
        print(f"\n🔍 Checking remaining positions...")
        remaining = api.list_positions()

        if remaining:
            print(f"⚠️  {len(remaining)} positions still open:")
            for pos in remaining:
                print(f"  • {pos.symbol}: {int(pos.qty)} shares")
        else:
            print("✨ All positions successfully closed!")

    except Exception as e:
        print(f"❌ Fatal error: {e}")


if __name__ == "__main__":
    force_close_all_individually()
