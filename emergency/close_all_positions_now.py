#!/usr/bin/env python3
"""
Close All Positions Script
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

import alpaca_trade_api as tradeapi
from datetime import datetime


def close_all_positions():
    """Close all open positions"""
    print("\n🚨 CLOSING ALL POSITIONS 🚨")
    print("=" * 50)

    try:
        # Connect to Alpaca using environment variables
        api = tradeapi.REST(
            os.getenv("ALPACA_API_KEY"),
            os.getenv("ALPACA_SECRET_KEY"),
            os.getenv("ALPACA_BASE_URL"),
        )

        print("🔗 Connected to Alpaca API")

        # Get all positions
        positions = api.list_positions()

        if not positions:
            print("✅ No open positions found!")
            return

        print(f"\n📊 Found {len(positions)} open position(s):")
        print("-" * 50)

        # Display current positions
        for pos in positions:
            side = "LONG" if float(pos.qty) > 0 else "SHORT"
            print(f"{side} {pos.symbol}: {pos.qty} shares @ ${pos.avg_entry_price}")
            print(f"   Current: ${pos.current_price} | P&L: ${pos.unrealized_pl}")

        print("-" * 50)

        # Close all positions
        print("\n🔄 Closing all positions...")

        for pos in positions:
            try:
                # Submit market order to close position
                side = "sell" if float(pos.qty) > 0 else "buy"
                qty = abs(float(pos.qty))

                order = api.submit_order(
                    symbol=pos.symbol,
                    qty=qty,
                    side=side,
                    type="market",
                    time_in_force="day",
                )

                print(
                    f"✅ Submitted {side.upper()} order for {pos.symbol}: {qty} shares"
                )

            except Exception as e:
                print(f"❌ Error closing {pos.symbol}: {e}")

        print("\n✅ All close orders submitted!")
        print("🕒 Orders may take a few moments to execute.")

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    return True


if __name__ == "__main__":
    success = close_all_positions()
    if success:
        print("\n🎉 Position closure process completed!")
    else:
        print("\n💥 Position closure failed!")
