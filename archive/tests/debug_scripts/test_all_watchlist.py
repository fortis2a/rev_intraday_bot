#!/usr/bin/env python3
"""
Test all watchlist stocks for current signal generation
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from config import config
from core.data_manager import DataManager
from stock_specific_config import should_execute_trade
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum_scalp import MomentumScalpStrategy
from strategies.vwap_bounce import VWAPBounceStrategy


def test_all_watchlist():
    """Test all watchlist stocks for signal generation"""
    print("=" * 60)
    print("FULL WATCHLIST SIGNAL TEST")
    print("=" * 60)

    # Initialize components
    data_manager = DataManager()

    # Get the watchlist
    watchlist = config["INTRADAY_WATCHLIST"]
    print(f"Testing {len(watchlist)} stocks: {watchlist}")
    print()

    for symbol in watchlist:
        print(f"{'='*40}")
        print(f"TESTING: {symbol}")
        print(f"{'='*40}")

        try:
            # Get market data like the engine does
            df = data_manager.get_bars(symbol, config["TIMEFRAME"])
            if df.empty or len(df) < 26:
                print(
                    f"❌ {symbol}: Insufficient data ({len(df) if not df.empty else 0} bars)"
                )
                continue

            # Calculate indicators
            df = data_manager.calculate_indicators(df)
            current_price = df.iloc[-1]["close"]

            print(f"📊 {symbol}: {len(df)} bars, Current Price: ${current_price:.2f}")

            # Check price limits
            if (
                current_price < config["MIN_PRICE"]
                or current_price > config["MAX_PRICE"]
            ):
                print(
                    f"❌ {symbol}: Price ${current_price:.2f} outside limits (${config['MIN_PRICE']}-${config['MAX_PRICE']})"
                )
                continue

            # Test all strategies
            strategies = {
                "Mean Reversion": MeanReversionStrategy(symbol),
                "Momentum": MomentumScalpStrategy(symbol),
                "VWAP": VWAPBounceStrategy(symbol),
            }

            signals_found = False
            for strategy_name, strategy in strategies.items():
                try:
                    signal = strategy.generate_signal(symbol, df)
                    if signal:
                        signals_found = True
                        print(
                            f"🚨 {strategy_name} SIGNAL: {signal['action']} - {signal['reason']}"
                        )

                        # Check confidence
                        trade_decision = should_execute_trade(symbol)
                        confidence = trade_decision.get("confidence", 0)
                        should_trade = trade_decision.get("should_execute", False)

                        print(
                            f"   📈 Confidence: {confidence:.1f}% ({'✅ PASS' if should_trade else '❌ FAIL'})"
                        )

                    else:
                        print(f"   {strategy_name}: No signal")

                except Exception as e:
                    print(f"   {strategy_name}: Error - {e}")

            if not signals_found:
                print("   No signals from any strategy")

                # Show current technical conditions for debugging
                latest = df.iloc[-1]
                bb_upper = latest.get("bb_upper", 0)
                bb_lower = latest.get("bb_lower", 0)
                bb_middle = latest.get("bb_middle", 0)
                rsi = latest.get("rsi", 0)

                if bb_upper > 0:
                    bb_position = (
                        (current_price - bb_lower) / (bb_upper - bb_lower)
                    ) * 100
                    print(
                        f"   BB Position: {bb_position:.1f}% (Upper: ${bb_upper:.2f}, Lower: ${bb_lower:.2f})"
                    )
                    print(f"   RSI: {rsi:.1f}")

                    if bb_position > 95:
                        print("   📊 Very close to BB upper - may signal soon")
                    elif bb_position < 5:
                        print("   📊 Very close to BB lower - may signal soon")

        except Exception as e:
            print(f"❌ {symbol}: Error - {e}")
            import traceback

            traceback.print_exc()

        print()

    print("=" * 60)
    print("WATCHLIST TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_all_watchlist()
