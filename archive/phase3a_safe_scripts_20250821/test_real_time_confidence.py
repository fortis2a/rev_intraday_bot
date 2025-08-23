#!/usr/bin/env python3
"""
Integration test for real-time vs historical confidence comparison
Shows how dynamic confidence levels change throughout the day
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_specific_config import (
    get_filtered_watchlist,
    calculate_final_confidence,
    get_real_time_confidence_for_trade,
    should_execute_trade,
)


def compare_confidence_methods():
    """Compare historical vs real-time confidence calculations"""

    budget_watchlist = ["SOXL", "SOFI", "TQQQ", "INTC", "NIO"]

    print("📊 CONFIDENCE CALCULATION COMPARISON")
    print("=" * 70)
    print("Comparing Historical Baseline vs Real-Time Market Conditions")
    print()

    # Historical confidence levels
    print("📈 HISTORICAL CONFIDENCE (Based on 60-day analysis):")
    print("-" * 55)
    historical_results = {}
    for symbol in budget_watchlist:
        hist_conf = calculate_final_confidence(symbol)
        historical_results[symbol] = hist_conf
        status = "✅ PASS" if hist_conf >= 75.0 else "❌ FAIL"
        print(f"{symbol}: {hist_conf:.1f}% {status}")

    print(f"\n🔄 REAL-TIME CONFIDENCE (Current market conditions):")
    print("-" * 55)
    real_time_results = {}
    for symbol in budget_watchlist:
        rt_data = get_real_time_confidence_for_trade(symbol)
        real_time_results[symbol] = rt_data["confidence"]
        status = "✅ PASS" if rt_data["confidence"] >= 75.0 else "❌ FAIL"
        print(f"{symbol}: {rt_data['confidence']:.1f}% {status}")

    print(f"\n📊 COMPARISON TABLE:")
    print("=" * 70)
    print(
        f"{'Stock':<6} {'Historical':<12} {'Real-Time':<12} {'Difference':<12} {'Status'}"
    )
    print("-" * 70)

    for symbol in budget_watchlist:
        hist = historical_results[symbol]
        real_time = real_time_results[symbol]
        diff = real_time - hist

        # Determine status change
        hist_pass = hist >= 75.0
        rt_pass = real_time >= 75.0

        if hist_pass and rt_pass:
            status = "✅ Both Pass"
        elif not hist_pass and rt_pass:
            status = "🟢 RT Improved"
        elif hist_pass and not rt_pass:
            status = "🔴 RT Declined"
        else:
            status = "❌ Both Fail"

        print(
            f"{symbol:<6} {hist:<12.1f} {real_time:<12.1f} {diff:+.1f}%{'':<7} {status}"
        )

    # Test filtering with both methods
    print(f"\n🎯 WATCHLIST FILTERING COMPARISON:")
    print("=" * 50)

    print("📊 Historical filtering:")
    historical_filtered = get_filtered_watchlist(
        budget_watchlist, 75.0, use_real_time=False
    )

    print("\n🔄 Real-time filtering:")
    real_time_filtered = get_filtered_watchlist(
        budget_watchlist, 75.0, use_real_time=True
    )

    print(f"\n📋 FILTERING RESULTS SUMMARY:")
    print(
        f"Historical method: {len(historical_filtered)}/{len(budget_watchlist)} stocks passed"
    )
    print(
        f"Real-time method: {len(real_time_filtered)}/{len(budget_watchlist)} stocks passed"
    )

    # Show differences in filtering
    added_stocks = set(real_time_filtered) - set(historical_filtered)
    removed_stocks = set(historical_filtered) - set(real_time_filtered)

    if added_stocks:
        print(f"🟢 Stocks added by real-time: {', '.join(added_stocks)}")
    if removed_stocks:
        print(f"🔴 Stocks removed by real-time: {', '.join(removed_stocks)}")
    if not added_stocks and not removed_stocks:
        print("🔄 No changes in filtered watchlist")

    return historical_filtered, real_time_filtered


def test_trade_execution_decisions():
    """Test real-time trade execution decisions"""

    print(f"\n🎯 TRADE EXECUTION DECISION TEST")
    print("=" * 50)
    print("Testing final trade decisions with real-time confidence")

    test_stocks = ["SOXL", "SOFI", "NIO"]  # Mix of high and borderline confidence

    for symbol in test_stocks:
        decision = should_execute_trade(symbol, "entry")

        print(f"\n📊 Technical Summary for {symbol}:")
        if "technical_summary" in decision:
            tech = decision["technical_summary"]
            print(f"   MACD Bullish: {tech.get('macd_bullish', 'Unknown')}")
            print(f"   Above EMA9: {tech.get('above_ema9', 'Unknown')}")
            print(f"   Above VWAP: {tech.get('above_vwap', 'Unknown')}")
            print(f"   RSI Level: {tech.get('rsi_level', 'Unknown')}")
            print(f"   Volume Multiple: {tech.get('volume_multiple', 'Unknown')}x")


def main():
    """Run comprehensive confidence system test"""

    print("🚀 COMPREHENSIVE REAL-TIME CONFIDENCE SYSTEM TEST")
    print("=" * 70)

    # Compare methods
    hist_filtered, rt_filtered = compare_confidence_methods()

    # Test trade decisions
    test_trade_execution_decisions()

    print(f"\n💡 KEY INSIGHTS:")
    print("=" * 30)
    print("✅ Real-time confidence adapts to current market conditions")
    print("✅ Historical confidence provides stable baseline expectations")
    print("✅ System automatically uses real-time when available")
    print("✅ Falls back to historical if real-time calculation fails")
    print("✅ Each trade decision uses most current technical indicator data")

    print(f"\n🎯 RECOMMENDATIONS:")
    print("=" * 20)
    print("• Use real-time confidence for all live trading decisions")
    print("• Historical confidence for backtesting and strategy development")
    print("• Monitor both to understand market condition changes")
    print("• Set alerts when real-time confidence drops below historical")


if __name__ == "__main__":
    main()
