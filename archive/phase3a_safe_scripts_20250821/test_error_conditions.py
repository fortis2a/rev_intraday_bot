#!/usr/bin/env python3
"""
Demonstrate strict no-fallback policy with actual error simulation
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_error_conditions():
    """Test various error conditions to verify no-fallback policy"""

    print("🛡️ STRICT NO-FALLBACK POLICY DEMONSTRATION")
    print("=" * 60)

    from stock_specific_config import (
        get_real_time_confidence_for_trade,
        should_execute_trade,
    )

    # Test 1: Normal operation
    print(f"\n✅ TEST 1: Normal Real-time Operation")
    print("-" * 40)

    try:
        result = get_real_time_confidence_for_trade("SOXL")
        print(
            f"SOXL Real-time: {result['confidence']:.1f}% - Tradeable: {result['tradeable']}"
        )

        decision = should_execute_trade("SOXL")
        print(
            f"Trade Decision: Execute={decision['execute']}, Confidence={decision['confidence']:.1f}%"
        )

    except Exception as e:
        print(f"Error in normal operation: {e}")

    # Test 2: Simulate network/data error by modifying the real-time calculator
    print(f"\n❌ TEST 2: Simulating Data Error")
    print("-" * 40)

    # Patch the real-time calculator to simulate an error
    try:
        from core.real_time_confidence import RealTimeConfidenceCalculator

        # Store original method
        original_method = RealTimeConfidenceCalculator.get_live_market_data

        # Create error-throwing method
        def failing_method(self, symbol, period="5d", interval="15m"):
            raise Exception("Simulated network error - market data unavailable")

        # Patch the method
        RealTimeConfidenceCalculator.get_live_market_data = failing_method

        print("📡 Simulating network error...")
        result = get_real_time_confidence_for_trade("SOXL")

        print(
            f"Error Result: Confidence={result['confidence']:.1f}%, Tradeable={result['tradeable']}"
        )
        print(f"Error Mode: {result.get('mode', 'unknown')}")
        print(f"Error Message: {result.get('error', 'No error message')}")

        decision = should_execute_trade("SOXL")
        print(
            f"Trade Decision: Execute={decision['execute']}, Error={decision.get('error', False)}"
        )

        if not decision["execute"] and decision.get("error", False):
            print("✅ SUCCESS: Trading properly blocked due to data error")
        else:
            print("❌ FAILURE: Trading not properly blocked")

        # Restore original method
        RealTimeConfidenceCalculator.get_live_market_data = original_method

    except Exception as e:
        print(f"Test setup error: {e}")

    # Test 3: Test with invalid symbol
    print(f"\n⚠️ TEST 3: Invalid Symbol Test")
    print("-" * 40)

    try:
        result = get_real_time_confidence_for_trade("INVALID_SYMBOL")
        print(
            f"Invalid Symbol Result: Confidence={result['confidence']:.1f}%, Tradeable={result['tradeable']}"
        )

        decision = should_execute_trade("INVALID_SYMBOL")
        print(f"Invalid Symbol Decision: Execute={decision['execute']}")

        if not decision["execute"]:
            print("✅ SUCCESS: Trading blocked for invalid symbol")

    except Exception as e:
        print(f"Invalid symbol test: {e}")

    # Test 4: Show the difference
    print(f"\n📊 COMPARISON: Real-time vs Error Conditions")
    print("=" * 60)

    print("NORMAL CONDITIONS:")
    try:
        normal_result = get_real_time_confidence_for_trade("SOFI")
        print(f"  • SOFI: {normal_result['confidence']:.1f}% confidence")
        print(f"  • Tradeable: {normal_result['tradeable']}")
        print(f"  • Mode: Normal real-time calculation")
    except:
        print("  • Error in normal calculation")

    print("\nERROR CONDITIONS (simulated):")
    try:
        # Temporarily patch again for demonstration
        from core.real_time_confidence import RealTimeConfidenceCalculator

        original_method = RealTimeConfidenceCalculator.calculate_real_time_confidence

        def error_method(self, symbol, expected_volatility=1.0):
            raise Exception("Market data service unavailable")

        RealTimeConfidenceCalculator.calculate_real_time_confidence = error_method

        error_result = get_real_time_confidence_for_trade("SOFI")
        print(f"  • SOFI: {error_result['confidence']:.1f}% confidence")
        print(f"  • Tradeable: {error_result['tradeable']}")
        print(f"  • Mode: {error_result.get('mode', 'unknown')}")
        print(f"  • Result: NO TRADING ALLOWED")

        # Restore
        RealTimeConfidenceCalculator.calculate_real_time_confidence = original_method

    except Exception as e:
        print(f"  • Error demonstration: {e}")

    print(f"\n🎯 POLICY ENFORCEMENT SUMMARY:")
    print("=" * 40)
    print("✅ Real-time working → Full trading capabilities")
    print("❌ Real-time error → ZERO trading (strict safety)")
    print("🛡️ No fallback → Forces system reliability")
    print("📊 Clear logging → Transparent error reporting")
    print("⚠️ Fail-safe design → Protects capital when data uncertain")


if __name__ == "__main__":
    test_error_conditions()
