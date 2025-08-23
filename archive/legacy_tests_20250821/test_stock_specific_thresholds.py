#!/usr/bin/env python3
"""
Test Stock-Specific Thresholds
Demonstrates the implementation of dynamic thresholds for each stock
"""

import sys
from pathlib import Path

# Add parent directory to path to access main modules
sys.path.append(str(Path(__file__).parent.parent))

from stock_specific_config import (
    get_stock_thresholds,
    get_position_size_multiplier,
    get_confidence_adjustment,
    print_stock_analysis_summary,
    STOCK_SPECIFIC_THRESHOLDS,
)
from config import config


def test_stock_specific_implementation():
    """Test the stock-specific threshold implementation"""

    print("🧪 TESTING STOCK-SPECIFIC THRESHOLD IMPLEMENTATION")
    print("=" * 70)

    # Display summary
    print_stock_analysis_summary()

    print(f"\n🔧 DETAILED THRESHOLD TESTING")
    print("=" * 70)

    # Test each stock in the watchlist
    watchlist = config["INTRADAY_WATCHLIST"]

    for symbol in watchlist:
        print(f"\n📊 {symbol} Analysis:")
        print("-" * 30)

        # Get thresholds
        thresholds = get_stock_thresholds(symbol)
        position_multiplier = get_position_size_multiplier(symbol)
        confidence_adj = get_confidence_adjustment(symbol)

        print(f"Stop Loss: {thresholds['stop_loss_pct']*100:.2f}%")
        print(f"Take Profit: {thresholds['take_profit_pct']*100:.2f}%")
        print(f"Trailing Activation: {thresholds['trailing_activation_pct']*100:.2f}%")
        print(f"Trailing Distance: {thresholds['trailing_distance_pct']*100:.2f}%")
        print(f"Position Size Multiplier: {position_multiplier:.2f}x")
        print(f"Confidence Adjustment: {confidence_adj:+.1%}")
        print(f"Volatility Profile: {thresholds.get('profile', 'N/A')}")

        # Calculate example position for $100 stock
        example_price = 100.00
        example_equity = 10000.00

        base_position = (
            min(config["MAX_POSITION_SIZE"], example_equity * 0.10) / example_price
        )
        adjusted_position = base_position * position_multiplier

        print(f"\nExample for ${example_price:.2f} stock:")
        print(
            f"  Base position: {int(base_position)} shares (${int(base_position) * example_price:.2f})"
        )
        print(
            f"  Adjusted position: {int(adjusted_position)} shares (${int(adjusted_position) * example_price:.2f})"
        )

        # Show price levels
        stop_price = example_price * (1 - thresholds["stop_loss_pct"])
        profit_price = example_price * (1 + thresholds["take_profit_pct"])
        trail_activation = example_price * (1 + thresholds["trailing_activation_pct"])

        print(f"  Stop Loss: ${stop_price:.2f}")
        print(f"  Take Profit: ${profit_price:.2f}")
        print(f"  Trail Activation: ${trail_activation:.2f}")


def compare_with_defaults():
    """Compare stock-specific vs default settings"""

    print(f"\n🔄 COMPARISON WITH DEFAULT SETTINGS")
    print("=" * 70)

    # Show default settings
    print(f"Current Default Settings:")
    print(f"  Stop Loss: {config['STOP_LOSS_PCT']*100:.2f}%")
    print(f"  Take Profit: {config['TAKE_PROFIT_PCT']*100:.2f}%")
    print(f"  Trailing Activation: {config['TRAILING_STOP_ACTIVATION']*100:.2f}%")
    print(f"  Trailing Distance: {config['TRAILING_STOP_PCT']*100:.2f}%")

    print(f"\nStock-Specific Adjustments:")
    print(
        f"{'Stock':<6} {'Stop Δ':<8} {'Profit Δ':<9} {'Trail Δ':<8} {'Reasoning':<25}"
    )
    print("-" * 70)

    for symbol in config["INTRADAY_WATCHLIST"]:
        thresholds = get_stock_thresholds(symbol)

        stop_delta = (thresholds["stop_loss_pct"] - config["STOP_LOSS_PCT"]) * 100
        profit_delta = (thresholds["take_profit_pct"] - config["TAKE_PROFIT_PCT"]) * 100
        trail_delta = (
            thresholds["trailing_distance_pct"] - config["TRAILING_STOP_PCT"]
        ) * 100

        # Determine reasoning
        if thresholds.get("volatility", 1.0) > 1.5:
            reasoning = "High volatility - wider stops"
        elif thresholds.get("volatility", 1.0) < 0.5:
            reasoning = "Low volatility - tighter stops"
        else:
            reasoning = "Moderate volatility - balanced"

        print(
            f"{symbol:<6} {stop_delta:+.2f}%   {profit_delta:+.2f}%    {trail_delta:+.2f}%   {reasoning:<25}"
        )


def simulation_example():
    """Show a simulation example of how this affects trading"""

    print(f"\n🎬 TRADING SIMULATION EXAMPLE")
    print("=" * 70)

    print("Scenario: Each stock reaches +2% gain, then reverses to -1%")
    print("Comparing default vs stock-specific trailing stops:\n")

    entry_price = 100.00
    peak_price = 102.00  # +2%
    final_price = 99.00  # -1%

    print(f"{'Stock':<6} {'Default Stop':<12} {'Stock Stop':<11} {'Advantage':<10}")
    print("-" * 50)

    for symbol in config["INTRADAY_WATCHLIST"]:
        thresholds = get_stock_thresholds(symbol)

        # Default trailing stop
        default_trail_stop = peak_price * (1 - config["TRAILING_STOP_PCT"])

        # Stock-specific trailing stop
        stock_trail_stop = peak_price * (1 - thresholds["trailing_distance_pct"])

        # Determine if stopped out
        if final_price <= default_trail_stop:
            default_result = f"${default_trail_stop:.2f}"
        else:
            default_result = f"${final_price:.2f}"

        if final_price <= stock_trail_stop:
            stock_result = f"${stock_trail_stop:.2f}"
        else:
            stock_result = f"${final_price:.2f}"

        # Calculate advantage
        default_pnl = (
            (float(default_result.replace("$", "")) - entry_price) / entry_price * 100
        )
        stock_pnl = (
            (float(stock_result.replace("$", "")) - entry_price) / entry_price * 100
        )
        advantage = stock_pnl - default_pnl

        print(f"{symbol:<6} {default_result:<12} {stock_result:<11} {advantage:+.1f}%")


if __name__ == "__main__":
    print("🚀 Starting Stock-Specific Threshold Testing...")

    # Run tests
    test_stock_specific_implementation()
    compare_with_defaults()
    simulation_example()

    print(f"\n✅ Testing complete!")
    print(f"📝 Stock-specific thresholds are ready for implementation")
    print(
        f"🎯 Each stock now has optimized risk management based on historical analysis"
    )
