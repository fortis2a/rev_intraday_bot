#!/usr/bin/env python3
"""
Quick test to verify real P&L values are being fetched correctly
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import asyncio

from scripts.alpaca_connector import AlpacaRealTimeConnector


def test_real_pnl():
    """Test fetching real P&L values"""
    print("🧪 Testing real P&L fetching...")

    connector = AlpacaRealTimeConnector()

    # Get recent trades with real P&L
    trades = connector.get_recent_trades(hours_back=24)

    print(f"\n📊 Found {len(trades)} recent trades:")
    for trade in trades:
        print(
            f"  {trade['symbol']}: {trade['action']} @ ${trade['price']} | P&L: ${trade['pnl']}"
        )

    return trades


if __name__ == "__main__":
    trades = test_real_pnl()
    print(f"\n✅ Test complete - {len(trades)} trades with real P&L")
