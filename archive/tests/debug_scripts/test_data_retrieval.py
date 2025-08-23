#!/usr/bin/env python3
"""
Test script to verify enhanced data retrieval
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from core.data_manager import DataManager


def test_data_retrieval():
    print("=== ENHANCED DATA RETRIEVAL TEST ===")

    dm = DataManager()
    test_symbols = ["SOFI", "NIO", "SOXL"]

    for symbol in test_symbols:
        print(f"\n--- Testing data retrieval for {symbol} ---")

        # Test with 15Min timeframe (default)
        df = dm.get_bars(symbol, config["TIMEFRAME"])

        if df.empty:
            print(f"❌ {symbol}: No data retrieved")
        else:
            print(f"✅ {symbol}: {len(df)} bars retrieved")
            print(f"   Date range: {df.index[0]} to {df.index[-1]}")
            print(f"   Latest price: ${df.iloc[-1]['close']:.2f}")

            if len(df) >= 26:
                print(f"   ✅ Sufficient for MACD (26+ bars)")
            else:
                print(f"   ❌ Insufficient for MACD ({len(df)} < 26 bars)")


if __name__ == "__main__":
    test_data_retrieval()
