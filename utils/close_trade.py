#!/usr/bin/env python3
"""
Close Specific Trade Script
Allows you to close a particular stock position manually
"""

import sys
import argparse
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

from core.data_manager import DataManager
from core.order_manager import OrderManager
from utils.logger import setup_logger


class TradeCloser:
    """Utility to close specific trades"""

    def __init__(self):
        self.logger = setup_logger("trade_closer")
        self.data_manager = DataManager()
        self.order_manager = OrderManager(self.data_manager)

    def list_open_positions(self):
        """List all open positions"""
        try:
            positions = self.data_manager.get_positions()

            if not positions:
                print("📭 No open positions found")
                return []

            print("\n" + "=" * 60)
            print("         CURRENT OPEN POSITIONS")
            print("=" * 60)

            for i, position in enumerate(positions, 1):
                symbol = position["symbol"]
                qty = int(position["qty"])
                entry_price = float(position["avg_entry_price"])
                current_value = float(position["market_value"])
                unrealized_pnl = float(position["unrealized_pl"])
                side = position["side"]

                current_price = current_value / qty if qty != 0 else 0
                pnl_pct = (
                    (unrealized_pnl / (entry_price * qty)) * 100
                    if entry_price * qty != 0
                    else 0
                )

                status_emoji = "🟢" if unrealized_pnl >= 0 else "🔴"

                print(f"{status_emoji} {i}. {symbol}")
                print(f"    Side: {side.upper()}")
                print(f"    Quantity: {qty} shares")
                print(f"    Entry Price: ${entry_price:.2f}")
                print(f"    Current Price: ${current_price:.2f}")
                print(f"    P&L: ${unrealized_pnl:.2f} ({pnl_pct:+.1f}%)")
                print(f"    Market Value: ${current_value:.2f}")
                print()

            return positions

        except Exception as e:
            print(f"❌ Error getting positions: {e}")
            return []

    def close_position(self, symbol):
        """Close a specific position"""
        try:
            print(f"\n🎯 Attempting to close position: {symbol}")

            # Check if position exists
            positions = self.data_manager.get_positions()
            position = next(
                (p for p in positions if p["symbol"].upper() == symbol.upper()), None
            )

            if not position:
                print(f"❌ No open position found for {symbol}")
                return False

            qty = abs(int(position["qty"]))
            side = position["side"]

            print(f"📊 Position Details:")
            print(f"    Symbol: {symbol}")
            print(f"    Side: {side}")
            print(f"    Quantity: {qty} shares")
            print(f"    Entry: ${float(position['avg_entry_price']):.2f}")
            print(f"    Current P&L: ${float(position['unrealized_pl']):.2f}")

            # Confirm closure
            confirm = (
                input(f"\n⚠️  Are you sure you want to close {symbol}? (y/N): ")
                .strip()
                .lower()
            )

            if confirm != "y":
                print("❌ Trade closure cancelled")
                return False

            # Close the position
            print(f"🔄 Closing {symbol} position...")
            result = self.order_manager.place_sell_order(symbol, qty)

            if result:
                print(f"✅ Successfully placed sell order for {symbol}")
                print(f"📋 Order ID: {result.get('order_id', 'N/A')}")
                return True
            else:
                print(f"❌ Failed to close position for {symbol}")
                return False

        except Exception as e:
            print(f"❌ Error closing position {symbol}: {e}")
            return False

    def close_all_positions(self):
        """Close all open positions"""
        try:
            positions = self.data_manager.get_positions()

            if not positions:
                print("📭 No positions to close")
                return

            print(f"\n⚠️  You are about to close {len(positions)} positions:")
            for pos in positions:
                print(f"    - {pos['symbol']}: {pos['qty']} shares")

            confirm = (
                input(f"\n⚠️  Are you sure you want to close ALL positions? (y/N): ")
                .strip()
                .lower()
            )

            if confirm != "y":
                print("❌ Mass closure cancelled")
                return

            closed_count = 0
            for position in positions:
                symbol = position["symbol"]
                print(f"\n🔄 Closing {symbol}...")

                if self.close_position_silent(symbol):
                    print(f"✅ {symbol} closed successfully")
                    closed_count += 1
                else:
                    print(f"❌ Failed to close {symbol}")

            print(f"\n📊 Summary: {closed_count}/{len(positions)} positions closed")

        except Exception as e:
            print(f"❌ Error in mass closure: {e}")

    def close_position_silent(self, symbol):
        """Close position without confirmation prompts"""
        try:
            positions = self.data_manager.get_positions()
            position = next(
                (p for p in positions if p["symbol"].upper() == symbol.upper()), None
            )

            if not position:
                return False

            qty = abs(int(position["qty"]))
            result = self.order_manager.place_sell_order(symbol, qty)
            return result is not None

        except Exception as e:
            self.logger.error(f"Error closing {symbol}: {e}")
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Close specific trades")
    parser.add_argument("--symbol", "-s", type=str, help="Symbol to close (e.g., AAPL)")
    parser.add_argument(
        "--list", "-l", action="store_true", help="List all open positions"
    )
    parser.add_argument("--close-all", action="store_true", help="Close all positions")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive mode"
    )

    args = parser.parse_args()

    closer = TradeCloser()

    # Interactive mode
    if args.interactive or (not args.symbol and not args.list and not args.close_all):
        print("\n🎯 TRADE CLOSER - Interactive Mode")

        while True:
            print("\n" + "=" * 40)
            print("Options:")
            print("1. List open positions")
            print("2. Close specific position")
            print("3. Close all positions")
            print("4. Exit")
            print("=" * 40)

            choice = input("Select option (1-4): ").strip()

            if choice == "1":
                closer.list_open_positions()

            elif choice == "2":
                positions = closer.list_open_positions()
                if positions:
                    symbol = input("\nEnter symbol to close: ").strip().upper()
                    if symbol:
                        closer.close_position(symbol)

            elif choice == "3":
                closer.close_all_positions()

            elif choice == "4":
                print("👋 Goodbye!")
                break

            else:
                print("❌ Invalid choice")

    # Command line modes
    elif args.list:
        closer.list_open_positions()

    elif args.close_all:
        closer.close_all_positions()

    elif args.symbol:
        closer.close_position(args.symbol.upper())

    else:
        print("❌ No action specified. Use --help for options")


if __name__ == "__main__":
    main()
