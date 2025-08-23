#!/usr/bin/env python3
"""
Debug script to test order placement for symbols that pass confidence
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from core.data_manager import DataManager
from core.order_manager import OrderManager
from stock_specific_config import should_execute_trade


def test_order_placement():
    print("=== ORDER PLACEMENT DEBUG ===")

    # Initialize components
    dm = DataManager()
    order_manager = OrderManager(dm)

    # Test symbols that should pass confidence (SOFI and NIO)
    test_symbols = ["SOFI", "NIO"]

    for symbol in test_symbols:
        print(f"\n--- Testing Order Placement for {symbol} ---")

        # Check confidence first
        decision = should_execute_trade(symbol, "BUY")
        print(
            f"Confidence Decision: Execute={decision['execute']}, Confidence={decision['confidence']:.1f}%"
        )

        if not decision["execute"]:
            print(f"SKIPPING {symbol} - Failed confidence check")
            continue

        # Check trading cooldown
        print(f"Checking trading cooldown...")
        if not order_manager.is_trading_allowed(symbol):
            print(f"BLOCKED: {symbol} - Trading cooldown active")
            continue

        # Check existing positions
        print(f"Checking existing positions...")
        positions = dm.get_positions()
        existing = next(
            (p for p in positions if p["symbol"] == symbol and p["side"] == "long"),
            None,
        )
        if existing:
            print(
                f"BLOCKED: {symbol} - Already have position: {existing['qty']} shares"
            )
            continue

        # Check position limit
        long_positions = [p for p in positions if p["side"] == "long"]
        max_positions = config.get("MAX_POSITIONS", 5)
        print(f"Current positions: {len(long_positions)}/{max_positions}")
        if len(long_positions) >= max_positions:
            print(f"BLOCKED: {symbol} - Position limit reached")
            continue

        # Check price and account info
        print(f"Getting current price and account info...")
        current_price = dm.get_current_price(symbol)
        account_info = dm.get_account_info()

        if not current_price:
            print(f"ERROR: Could not get current price for {symbol}")
            continue
        if not account_info:
            print(f"ERROR: Could not get account info")
            continue

        print(f"Current price: ${current_price:.2f}")
        print(f"Account equity: ${account_info['equity']:,.2f}")
        print(f"Buying power: ${account_info['buying_power']:,.2f}")

        # Calculate position size
        shares = order_manager.calculate_position_size(
            symbol, current_price, account_info["equity"]
        )
        required_cash = shares * current_price

        print(f"Calculated shares: {shares}")
        print(f"Required cash: ${required_cash:.2f}")

        if required_cash > account_info["buying_power"]:
            print(f"BLOCKED: {symbol} - Insufficient buying power")
            continue

        print(f"✅ ALL CHECKS PASSED for {symbol}")
        print(f"   - Confidence: {decision['confidence']:.1f}%")
        print(f"   - Price: ${current_price:.2f}")
        print(f"   - Shares: {shares}")
        print(f"   - Cost: ${required_cash:.2f}")
        print(f"   - Available: ${account_info['buying_power']:,.2f}")

        # Mock order placement (don't actually place orders in debug)
        print(
            f"⚠️  WOULD PLACE BUY ORDER FOR {symbol} (debug mode - not actually placing)"
        )


if __name__ == "__main__":
    test_order_placement()
