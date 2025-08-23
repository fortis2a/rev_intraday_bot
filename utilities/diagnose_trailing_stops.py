#!/usr/bin/env python3
"""
Trailing Stop Diagnostic Script
Checks the current state of trailing stops and position tracking
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.data_manager import DataManager
from core.order_manager import OrderManager
from core.trailing_stop_manager import TrailingStopManager


def diagnose_trailing_stops():
    """Diagnose trailing stop issues"""
    print("🔍 TRAILING STOP DIAGNOSTIC")
    print("=" * 50)

    try:
        # Initialize components
        print("1. Initializing components...")
        data_manager = DataManager()
        order_manager = OrderManager(data_manager)

        # Check actual account positions
        print("\n2. Checking actual account positions...")
        positions = data_manager.get_positions()
        print(f"   Found {len(positions)} positions in account:")
        for pos in positions:
            if float(pos["qty"]) != 0:
                print(
                    f"   • {pos['symbol']}: {pos['qty']} shares @ ${float(pos['avg_entry_price']):.2f}"
                )

        # Check trailing stop manager state
        print("\n3. Checking trailing stop manager state...")
        tsm = order_manager.trailing_stop_manager
        print(f"   Active positions in TSM: {len(tsm.active_positions)}")
        print(f"   Position symbols: {list(tsm.active_positions.keys())}")

        if tsm.active_positions:
            for symbol, pos in tsm.active_positions.items():
                print(f"   • {symbol}:")
                print(f"     Entry: ${pos.entry_price:.2f}")
                print(f"     Current: ${pos.current_price:.2f}")
                print(f"     Trailing Stop: ${pos.trailing_stop_price:.2f}")
                print(f"     Trailing Active: {pos.is_trailing_active}")
        else:
            print("   ❌ No positions tracked in trailing stop manager!")

        # Try to manually add the current position to TSM
        print("\n4. Testing manual position addition...")
        if positions and len(positions) > 0:
            pos = positions[0]
            symbol = pos["symbol"]
            entry_price = float(pos["avg_entry_price"])
            qty = int(pos["qty"])

            if qty != 0:
                print(f"   Adding {symbol} manually to TSM...")
                from stock_specific_config import get_stock_thresholds

                thresholds = get_stock_thresholds(symbol)

                tsm.add_position(
                    symbol=symbol,
                    entry_price=entry_price,
                    quantity=abs(qty),
                    side="long" if qty > 0 else "short",
                    custom_thresholds=thresholds,
                )

                print(f"   ✅ Position added to TSM")
                print(f"   Active positions now: {len(tsm.active_positions)}")

                # Test price update
                current_price = data_manager.get_current_price(symbol)
                if current_price:
                    print(
                        f"   Testing price update with current price: ${current_price:.2f}"
                    )
                    update_result = tsm.update_position_price(symbol, current_price)
                    if update_result:
                        print(f"   ✅ Update result: {update_result}")
                    else:
                        print(f"   ℹ️  No trailing stop update needed")

                    # Check position details
                    pos_data = tsm.active_positions[symbol]
                    activation_threshold = (
                        pos_data.entry_price * 1.005
                    )  # 0.5% activation
                    print(f"   Activation threshold: ${activation_threshold:.2f}")
                    print(f"   Current price: ${current_price:.2f}")
                    print(
                        f"   Should activate: {current_price >= activation_threshold}"
                    )
                    print(f"   Is trailing active: {pos_data.is_trailing_active}")

    except Exception as e:
        print(f"❌ Error during diagnosis: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    diagnose_trailing_stops()
