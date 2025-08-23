#!/usr/bin/env python3
"""
Test if live signals are being generated in real-time
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from core.data_manager import DataManager
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum_scalp import MomentumScalpStrategy
from strategies.vwap_bounce import VWAPBounceStrategy
from utils.logger import setup_logger
import logging
import time


def test_live_signals():
    """Test if signals are being generated in real-time"""
    print("=" * 50)
    print("LIVE SIGNAL GENERATION TEST - EXACTLY LIKE MAIN.PY")
    print("=" * 50)

    # Initialize components (same as main.py)
    data_manager = DataManager()

    # Strategy classes (same as main.py)
    strategy_classes = {
        "momentum": MomentumScalpStrategy,
        "mean_reversion": MeanReversionStrategy,
        "vwap_bounce": VWAPBounceStrategy,
    }

    # Test symbols from watchlist
    from config import config

    test_symbols = config["INTRADAY_WATCHLIST"][:2]  # Test first 2 symbols

    print(f"Testing symbols: {test_symbols}")
    print(f"Timeframe: {config['TIMEFRAME']}")

    signals = []

    for symbol in test_symbols:
        print(f"\n--- Scanning {symbol} (like main.py scan_for_signals) ---")

        try:
            # Get market data (exactly like main.py)
            df = data_manager.get_bars(symbol, config["TIMEFRAME"])

            print(f"Data retrieved: {len(df) if not df.empty else 0} bars")

            if df.empty or len(df) < 26:
                print(
                    f"❌ Insufficient data for {symbol}: {len(df) if not df.empty else 0} bars"
                )
                continue

            # Calculate indicators (exactly like main.py)
            df = data_manager.calculate_indicators(df)

            # Check price limits (exactly like main.py)
            current_price = df.iloc[-1]["close"]
            print(f"Current price: ${current_price:.2f}")

            if (
                current_price < config["MIN_PRICE"]
                or current_price > config["MAX_PRICE"]
            ):
                print(
                    f"❌ Price ${current_price:.2f} outside limits (${config['MIN_PRICE']}-${config['MAX_PRICE']})"
                )
                continue

            # Run each strategy (exactly like main.py)
            for strategy_name, strategy_class in strategy_classes.items():
                try:
                    print(f"  Testing {strategy_name} strategy...")

                    # Create strategy instance (exactly like main.py)
                    strategy = strategy_class(symbol)

                    # Generate signal (exactly like main.py)
                    signal = strategy.generate_signal(symbol, df)

                    if signal:
                        signals.append(signal)
                        print(
                            f"  ✅ {strategy_name}: {signal['action']} {symbol} - {signal['reason']}"
                        )
                    else:
                        print(f"  ⚪ {strategy_name}: No signal")

                except Exception as strategy_error:
                    print(f"  ❌ {strategy_name} failed: {strategy_error}")
                    import traceback

                    traceback.print_exc()

        except Exception as e:
            print(f"❌ Failed to scan {symbol}: {e}")
            import traceback

            traceback.print_exc()

    print(f"\n" + "=" * 50)
    print(f"TEST COMPLETE - Found {len(signals)} signals")
    for signal in signals:
        print(f"  📡 {signal['action']} {signal['symbol']} - {signal['reason']}")
    print("=" * 50)


if __name__ == "__main__":
    test_live_signals()
