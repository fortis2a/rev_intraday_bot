#!/usr/bin/env python3
"""
Test script for real Alpaca trade data integration
Run this to verify the Command Center can pull real trade data
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from config import config
    from scripts.alpaca_connector import (
        alpaca_connector,
        get_real_strategy_performance,
        get_real_trade_history,
    )

    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)


async def test_alpaca_connection():
    """Test Alpaca API connection"""
    print("\n🔗 Testing Alpaca API Connection...")
    try:
        is_connected = await alpaca_connector.test_connection()
        if is_connected:
            print("✅ Alpaca API connection successful")

            # Test account data
            account = await alpaca_connector.fetch_account_data()
            if account:
                print(
                    f"✅ Account Data: Equity=${account.equity:,.2f}, Cash=${account.cash:,.2f}"
                )
            else:
                print("⚠️ Could not fetch account data")

            return True
        else:
            print(
                f"❌ Alpaca API connection failed: {alpaca_connector.connection_error}"
            )
            return False

    except Exception as e:
        print(f"❌ Connection test error: {e}")
        return False


def test_trade_history():
    """Test trade history fetching"""
    print("\n📊 Testing Trade History...")
    try:
        trades = get_real_trade_history(hours_back=24)

        if trades:
            print(f"✅ Found {len(trades)} recent trades:")
            for i, trade in enumerate(trades[:5]):  # Show first 5
                print(
                    f"  {i+1}. {trade['symbol']} {trade['action']} {trade['quantity']}@${trade['price']:.2f} "
                    f"P&L: ${trade['pnl']:.2f} ({trade['strategy']})"
                )

            if len(trades) > 5:
                print(f"  ... and {len(trades) - 5} more trades")

        else:
            print(
                "ℹ️ No recent trades found - this is normal for a new paper trading account"
            )

        return trades

    except Exception as e:
        print(f"❌ Trade history error: {e}")
        return []


def test_strategy_performance():
    """Test strategy performance calculation"""
    print("\n📈 Testing Strategy Performance...")
    try:
        performance = get_real_strategy_performance(hours_back=24)

        if performance:
            print(f"✅ Strategy performance for {len(performance)} symbols:")
            for symbol, perf in performance.items():
                print(
                    f"  {symbol}: {perf['trades']} trades, "
                    f"${perf['pnl']:.2f} P&L, "
                    f"{perf['win_rate']:.1f}% win rate, "
                    f"Best: {perf['best_strategy']}"
                )
        else:
            print("ℹ️ No strategy performance data - this is normal for a new account")

        return performance

    except Exception as e:
        print(f"❌ Strategy performance error: {e}")
        return {}


async def main():
    """Main test function"""
    print("🚀 Testing Real Alpaca Trade Data Integration")
    print("=" * 50)

    # Test connection
    connected = await test_alpaca_connection()

    if not connected:
        print("\n❌ Cannot proceed with trade tests - connection failed")
        print("💡 This is normal if:")
        print("   - Alpaca API keys are not set")
        print("   - Running outside market hours")
        print("   - Network connectivity issues")
        return

    # Test trade history
    trades = test_trade_history()

    # Test strategy performance
    performance = test_strategy_performance()

    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")

    if connected:
        print("✅ Alpaca API: Connected")
    else:
        print("❌ Alpaca API: Failed")

    if trades:
        print(f"✅ Trade History: {len(trades)} trades found")
    else:
        print("ℹ️ Trade History: No recent trades")

    if performance:
        print(f"✅ Strategy Performance: {len(performance)} symbols")
    else:
        print("ℹ️ Strategy Performance: No data yet")

    print("\n🎯 INTEGRATION STATUS:")
    if connected:
        print("✅ Ready for real trade data when market opens Monday!")
        print(
            "💡 Command Center will now pull actual trades from your Alpaca paper account"
        )
    else:
        print("⚠️ Will use simulation data until Alpaca connection is established")

    print("\n🚀 Run the Command Center to see live integration:")
    print("   python scripts/scalping_command_center.py")


if __name__ == "__main__":
    asyncio.run(main())
