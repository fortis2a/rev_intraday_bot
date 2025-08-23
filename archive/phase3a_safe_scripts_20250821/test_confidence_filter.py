#!/usr/bin/env python3
"""
Test the 75% confidence filter for the new budget-friendly watchlist
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_specific_config import (
    calculate_final_confidence,
    get_filtered_watchlist,
    meets_confidence_threshold,
)


def test_confidence_filter():
    """Test the confidence filtering system"""

    # Current watchlists
    budget_watchlist = ["SOXL", "SOFI", "TQQQ", "INTC", "NIO"]
    original_watchlist = ["IONQ", "RGTI", "QBTS", "JNJ", "PG"]

    print("🧪 TESTING 75% CONFIDENCE FILTER")
    print("=" * 50)

    print("\n📊 INDIVIDUAL CONFIDENCE LEVELS:")
    print("-" * 40)

    all_stocks = budget_watchlist + original_watchlist
    confidence_results = {}

    for symbol in all_stocks:
        confidence = calculate_final_confidence(symbol)
        confidence_results[symbol] = confidence
        status = "✅ PASS" if confidence >= 75.0 else "❌ FAIL"
        print(f"{symbol}: {confidence:.1f}% {status}")

    print(f"\n🎯 BUDGET-FRIENDLY WATCHLIST FILTER TEST:")
    filtered_budget = get_filtered_watchlist(budget_watchlist, 75.0)

    print(f"\n📈 ORIGINAL WATCHLIST FILTER TEST:")
    filtered_original = get_filtered_watchlist(original_watchlist, 75.0)

    print(f"\n📋 SUMMARY COMPARISON:")
    print("=" * 50)
    print(f"Budget Watchlist: {len(filtered_budget)}/{len(budget_watchlist)} passed")
    print(
        f"Original Watchlist: {len(filtered_original)}/{len(original_watchlist)} passed"
    )

    print(f"\n🏆 RECOMMENDED TRADING STOCKS (>75% confidence):")
    all_filtered = filtered_budget + filtered_original
    all_filtered_with_conf = [(s, confidence_results[s]) for s in all_filtered]
    all_filtered_with_conf.sort(key=lambda x: x[1], reverse=True)

    for symbol, conf in all_filtered_with_conf:
        list_type = "Budget" if symbol in budget_watchlist else "Original"
        print(f"  {symbol}: {conf:.1f}% ({list_type})")

    print(f"\n⚠️  STOCKS BELOW 75% THRESHOLD:")
    failed_stocks = [
        (s, confidence_results[s]) for s in all_stocks if confidence_results[s] < 75.0
    ]
    if failed_stocks:
        for symbol, conf in failed_stocks:
            list_type = "Budget" if symbol in budget_watchlist else "Original"
            print(f"  {symbol}: {conf:.1f}% ({list_type}) - Will be skipped")
    else:
        print("  None! All stocks meet the threshold.")

    return filtered_budget, filtered_original


if __name__ == "__main__":
    filtered_budget, filtered_original = test_confidence_filter()
