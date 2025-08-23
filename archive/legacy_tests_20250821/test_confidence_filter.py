#!/usr/bin/env python3
"""
Test script for confidence filter functionality
Demonstrates how signals are filtered based on confidence thresholds
"""

import sys
from pathlib import Path

# Add parent directory to path to access main modules
sys.path.append(str(Path(__file__).parent.parent))

from data_manager import DataManager
from logger import setup_logger

from config import config
from strategies import MeanReversionStrategy, MomentumStrategy, VWAPStrategy


def test_confidence_filter():
    """Test confidence filtering with different thresholds"""
    logger = setup_logger("confidence_filter_test")

    print("=" * 60)
    print("CONFIDENCE FILTER TESTING")
    print("=" * 60)

    # Initialize data manager and strategies
    data_manager = DataManager()
    strategies = {
        "momentum": MomentumStrategy(),
        "mean_reversion": MeanReversionStrategy(),
        "vwap": VWAPStrategy(),
    }

    # Test with IONQ
    symbol = "IONQ"
    print(f"\n[TESTING] Symbol: {symbol}")

    # Get data and calculate indicators
    df = data_manager.get_bars(symbol, config["TIMEFRAME"])
    if df.empty or len(df) < 26:
        print(f"[ERROR] Insufficient data for {symbol}")
        return

    df = data_manager.calculate_indicators(df)

    # Generate signals from all strategies
    signals = []
    for strategy_name, strategy in strategies.items():
        signal = strategy.generate_signal(symbol, df)
        if signal:
            signals.append({"strategy": strategy_name, "signal": signal})

    if not signals:
        print("[INFO] No signals generated")
        return

    # Test different confidence thresholds
    thresholds = [0.50, 0.60, 0.70, 0.75, 0.80, 0.85]

    print(f"\n[SIGNALS GENERATED] {len(signals)} signals found:")
    for item in signals:
        signal = item["signal"]
        print(
            f"  {item['strategy']}: {signal['action']} - Confidence: {signal['confidence']:.1%}"
        )

    print(f"\n[CONFIDENCE FILTER RESULTS]")
    print(f"{'Threshold':<12} {'Signals Passed':<15} {'Details'}")
    print("-" * 60)

    for threshold in thresholds:
        passed_signals = []
        filtered_signals = []

        for item in signals:
            signal = item["signal"]
            if signal["confidence"] >= threshold:
                passed_signals.append(
                    f"{item['strategy']} ({signal['confidence']:.1%})"
                )
            else:
                filtered_signals.append(
                    f"{item['strategy']} ({signal['confidence']:.1%})"
                )

        print(
            f"{threshold:.1%}          {len(passed_signals):<15} {', '.join(passed_signals) if passed_signals else 'None'}"
        )
        if filtered_signals:
            print(f"{'':12} {'Filtered:':<15} {', '.join(filtered_signals)}")

    # Current bot configuration
    live_threshold = config["MIN_CONFIDENCE_THRESHOLD"]
    demo_threshold = config["MIN_CONFIDENCE_DEMO"]

    print(f"\n[CURRENT BOT CONFIGURATION]")
    print(f"Live Trading Threshold: {live_threshold:.1%}")
    print(f"Demo Trading Threshold: {demo_threshold:.1%}")

    # Show what would happen with current config
    live_passed = [
        item for item in signals if item["signal"]["confidence"] >= live_threshold
    ]
    demo_passed = [
        item for item in signals if item["signal"]["confidence"] >= demo_threshold
    ]

    print(f"\n[LIVE TRADING MODE] (75% threshold):")
    if live_passed:
        for item in live_passed:
            signal = item["signal"]
            print(
                f"  ✅ {item['strategy']}: {signal['action']} - {signal['confidence']:.1%} - {signal['reason']}"
            )
    else:
        print("  ❌ NO SIGNALS would be executed (all below 75% threshold)")

    print(f"\n[DEMO TRADING MODE] (50% threshold):")
    if demo_passed:
        for item in demo_passed:
            signal = item["signal"]
            print(
                f"  ✅ {item['strategy']}: {signal['action']} - {signal['confidence']:.1%} - {signal['reason']}"
            )
    else:
        print("  ❌ NO SIGNALS would be executed")

    print("\n" + "=" * 60)
    print("CONFIDENCE FILTER TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    test_confidence_filter()
