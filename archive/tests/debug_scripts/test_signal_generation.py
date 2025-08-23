#!/usr/bin/env python3
"""
Debug script to test signal generation for high-confidence symbols
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from core.data_manager import DataManager
from stock_specific_config import should_execute_trade
from strategies import MeanReversionStrategy, MomentumStrategy, VWAPStrategy


def test_signal_generation():
    print("=== SIGNAL GENERATION DEBUG ===")

    # Initialize components
    dm = DataManager()

    # Strategy classes
    strategy_classes = {
        "momentum": MomentumStrategy,
        "mean_reversion": MeanReversionStrategy,
        "vwap": VWAPStrategy,
    }

    # Test symbols that pass confidence
    test_symbols = ["SOFI", "NIO"]

    for symbol in test_symbols:
        print(f"\n--- Testing Signal Generation for {symbol} ---")

        # Check confidence first
        decision = should_execute_trade(symbol, "BUY")
        print(
            f"Confidence: {decision['confidence']:.1f}% (Execute: {decision['execute']})"
        )

        try:
            # Get market data
            df = dm.get_bars(symbol, config["TIMEFRAME"])
            if df.empty or len(df) < 14:  # Reduced minimum for real-time trading
                print(
                    f"ERROR: Insufficient data for {symbol}: {len(df) if not df.empty else 0} bars"
                )
                continue

            print(f"Market data: {len(df)} bars available")

            # Calculate indicators
            df = dm.calculate_indicators(df)

            # Check current price limits
            current_price = df.iloc[-1]["close"]
            print(f"Current price: ${current_price:.2f}")

            if (
                current_price < config["MIN_PRICE"]
                or current_price > config["MAX_PRICE"]
            ):
                print(
                    f"BLOCKED: Price ${current_price:.2f} outside limits ${config['MIN_PRICE']}-${config['MAX_PRICE']}"
                )
                continue

            # Test each strategy
            signals_generated = []
            for strategy_name, strategy_class in strategy_classes.items():
                try:
                    print(f"\n  Testing {strategy_name} strategy...")

                    # Create strategy instance
                    strategy = strategy_class(
                        symbol
                    )  # All strategies need symbol parameter

                    # Generate signal
                    signal = strategy.generate_signal(symbol, df)

                    if signal:
                        signals_generated.append(signal)
                        print(
                            f"  ✅ {strategy_name}: {signal['action']} - {signal['reason']}"
                        )
                        print(f"     Confidence: {signal.get('confidence', 'N/A')}")
                    else:
                        print(f"  ❌ {strategy_name}: No signal generated")

                except Exception as e:
                    print(f"  ❌ {strategy_name}: ERROR - {e}")

            print(f"\nSUMMARY for {symbol}:")
            print(
                f"  - Confidence: {decision['confidence']:.1f}% ({'PASS' if decision['execute'] else 'FAIL'})"
            )
            print(f"  - Signals generated: {len(signals_generated)}")

            if decision["execute"] and signals_generated:
                print(f"  🚀 {symbol} SHOULD TRADE (high confidence + signals)")
            elif decision["execute"] and not signals_generated:
                print(f"  ⚠️  {symbol} high confidence but NO SIGNALS")
            elif not decision["execute"] and signals_generated:
                print(f"  ⚠️  {symbol} has signals but LOW CONFIDENCE")
            else:
                print(f"  ❌ {symbol} no signals and low confidence")

        except Exception as e:
            print(f"ERROR processing {symbol}: {e}")


if __name__ == "__main__":
    test_signal_generation()
