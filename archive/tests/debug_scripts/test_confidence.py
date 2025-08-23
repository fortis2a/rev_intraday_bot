#!/usr/bin/env python3
"""
Debug script to test confidence calculations for trading
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from stock_specific_config import (
    get_real_time_confidence_for_trade,
    should_execute_trade,
)


def test_confidence_calculations():
    print("=== CONFIDENCE CALCULATION DEBUG ===")

    # Test each symbol in watchlist
    symbols = config["INTRADAY_WATCHLIST"]
    print(f"Testing confidence for symbols: {symbols}")
    print(f"Confidence threshold: {config['MIN_CONFIDENCE_THRESHOLD'] * 100:.0f}%")
    print()

    for symbol in symbols:
        print(f"--- Testing {symbol} ---")

        # Test raw confidence calculation
        try:
            confidence_data = get_real_time_confidence_for_trade(symbol)
            print(f"Raw confidence data: {confidence_data}")
        except Exception as e:
            print(f"Error in raw confidence calculation: {e}")

        # Test full trade decision
        try:
            decision = should_execute_trade(symbol, "BUY")
            print(
                f"Trade decision: Execute={decision['execute']}, Confidence={decision['confidence']:.1f}%"
            )
            print(f"Reason: {decision['reason']}")

            if decision.get("error"):
                print(f"ERROR: {decision['reason']}")
        except Exception as e:
            print(f"Error in trade decision: {e}")

        print()


if __name__ == "__main__":
    test_confidence_calculations()
