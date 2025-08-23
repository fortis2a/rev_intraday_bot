#!/usr/bin/env python3
"""
Test Trailing Stop Synchronization
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.data_manager import DataManager
from core.order_manager import OrderManager


def test_sync():
    """Test the sync functionality"""
    print("🔄 TESTING TRAILING STOP SYNCHRONIZATION")
    print("=" * 50)

    try:
        # Initialize components
        data_manager = DataManager()
        order_manager = OrderManager(data_manager)
        tsm = order_manager.trailing_stop_manager

        print(f"Before sync - TSM positions: {len(tsm.active_positions)}")

        # Test sync method
        tsm.sync_with_account_positions(data_manager)

        print(f"After sync - TSM positions: {len(tsm.active_positions)}")

        if tsm.active_positions:
            for symbol, pos in tsm.active_positions.items():
                print(
                    f"✅ {symbol}: Entry ${pos.entry_price:.2f}, Stop ${pos.trailing_stop_price:.2f}"
                )

                # Test price update to trigger trailing
                current_price = data_manager.get_current_price(symbol)
                if current_price:
                    print(f"   Current price: ${current_price:.2f}")
                    update_result = tsm.update_position_price(symbol, current_price)
                    if update_result:
                        print(f"   ✅ Trailing update: {update_result}")
                    else:
                        print(f"   ℹ️  No trailing update needed")

        # Test the check_trailing_stop_triggers method (which calls sync)
        print("\n🎯 Testing check_trailing_stop_triggers...")
        triggers = order_manager.check_trailing_stop_triggers()
        print(f"Triggered positions: {triggers}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_sync()
