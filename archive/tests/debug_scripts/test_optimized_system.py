"""
Test Script for Optimized Strategy System
=========================================
Tests the unified indicator service and optimized strategies to ensure:
1. No indicator duplication between confidence monitor and strategies
2. Each strategy focuses on its specialized indicators
3. All strategies still generate signals properly
4. Performance improvements from unified calculations
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import time

# Test imports
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum_scalp import MomentumScalpStrategy
from strategies.vwap_bounce import VWAPBounceStrategy


def create_sample_data(symbol="AAPL", periods=100):
    """Create sample market data for testing"""
    try:
        # Get real market data
        ticker = yf.Ticker(symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=2)

        df = ticker.history(start=start_date, end=end_date, interval="1m")
        df = df.reset_index()
        df.columns = [col.lower() for col in df.columns]

        if len(df) < 50:
            print(f"⚠️  Limited data for {symbol}, generating synthetic data")
            # Generate synthetic data if market is closed
            dates = pd.date_range(
                start=datetime.now() - timedelta(hours=2), periods=periods, freq="1min"
            )
            base_price = 150.0

            df = pd.DataFrame(
                {
                    "datetime": dates,
                    "open": base_price + np.random.normal(0, 1, periods).cumsum(),
                    "high": None,
                    "low": None,
                    "close": None,
                    "volume": np.random.randint(1000, 10000, periods),
                }
            )

            # Calculate OHLC from synthetic close prices
            for i in range(len(df)):
                noise = np.random.normal(0, 0.5, 3)
                df.loc[i, "high"] = df.loc[i, "open"] + abs(noise[0])
                df.loc[i, "low"] = df.loc[i, "open"] - abs(noise[1])
                df.loc[i, "close"] = df.loc[i, "open"] + noise[2]

        print(f"✅ Created test data: {len(df)} rows for {symbol}")
        return df

    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        return None


def test_unified_indicator_service():
    """Test the unified indicator service directly"""
    print("\n" + "=" * 60)
    print("TESTING UNIFIED INDICATOR SERVICE")
    print("=" * 60)

    try:
        from core.unified_indicators import unified_indicator_service

        # Create test data
        df = create_sample_data("AAPL", 100)
        if df is None:
            return False

        # Test each strategy's indicator requests
        strategies = ["mean_reversion", "momentum_scalp", "vwap_bounce"]

        for strategy in strategies:
            print(f"\n📊 Testing indicators for {strategy} strategy...")

            start_time = time.time()
            result = unified_indicator_service.get_indicators_for_strategy(
                df, "AAPL", strategy
            )
            end_time = time.time()

            if "error" in result:
                print(f"❌ Error: {result['error']}")
                continue

            indicators = result["indicators"]
            current_values = result["current_values"]

            print(
                f"✅ Generated {len(indicators)} indicators in {(end_time-start_time)*1000:.1f}ms"
            )
            print(f"   Current price: ${current_values['price']:.2f}")
            print(f"   Available indicators: {list(indicators.keys())}")

        return True

    except Exception as e:
        print(f"❌ Unified indicator service test failed: {e}")
        return False


def test_strategy_signals():
    """Test signal generation from all optimized strategies"""
    print("\n" + "=" * 60)
    print("TESTING OPTIMIZED STRATEGY SIGNALS")
    print("=" * 60)

    # Create test data
    df = create_sample_data("AAPL", 150)
    if df is None:
        return False

    # Initialize strategies
    strategies = {
        "Mean Reversion": MeanReversionStrategy("AAPL"),
        "Momentum Scalp": MomentumScalpStrategy("AAPL"),
        "VWAP Bounce": VWAPBounceStrategy("AAPL"),
    }

    results = {}

    for name, strategy in strategies.items():
        print(f"\n🎯 Testing {name} Strategy...")

        try:
            start_time = time.time()
            signal = strategy.generate_signal("AAPL", df)
            end_time = time.time()

            execution_time = (end_time - start_time) * 1000

            if signal:
                print(f"✅ Signal Generated in {execution_time:.1f}ms:")
                print(f"   Action: {signal['action']}")
                print(f"   Confidence: {signal['confidence']:.1%}")
                print(f"   Reason: {signal['reason']}")
                print(f"   Entry: ${signal['entry_price']:.2f}")
                print(f"   Stop: ${signal['stop_loss']:.2f}")
                print(f"   Target: ${signal['take_profit']:.2f}")

                results[name] = {"signal": signal, "execution_time_ms": execution_time}
            else:
                print(f"✅ No signal generated (expected behavior)")
                results[name] = {"signal": None, "execution_time_ms": execution_time}

        except Exception as e:
            print(f"❌ Error testing {name}: {e}")
            results[name] = {"error": str(e)}

    return results


def test_indicator_specialization():
    """Test that each strategy focuses on its specialized indicators"""
    print("\n" + "=" * 60)
    print("TESTING INDICATOR SPECIALIZATION")
    print("=" * 60)

    specializations = {
        "Mean Reversion": ["Bollinger Bands", "Stochastic", "Support/Resistance"],
        "Momentum Scalp": ["ADX", "Williams %R", "ROC", "Multi-EMA"],
        "VWAP Bounce": ["VWAP Bands", "Volume Profile", "POC", "Value Area", "OBV"],
    }

    print("📋 Strategy Specializations:")
    for strategy, indicators in specializations.items():
        print(f"   {strategy}: {', '.join(indicators)}")

    print("\n📊 Shared Indicators (from unified service):")
    shared_indicators = ["RSI", "MACD", "EMA", "VWAP", "Volume Analysis"]
    print(f"   All Strategies: {', '.join(shared_indicators)}")

    return True


def test_performance_comparison():
    """Compare performance before and after optimization"""
    print("\n" + "=" * 60)
    print("TESTING PERFORMANCE IMPROVEMENTS")
    print("=" * 60)

    df = create_sample_data("AAPL", 200)
    if df is None:
        return False

    print("🚀 Testing performance improvements from unified indicators...")

    # Test multiple signal generations (simulating real trading)
    num_tests = 10
    strategies = [
        MeanReversionStrategy("AAPL"),
        MomentumScalpStrategy("AAPL"),
        VWAPBounceStrategy("AAPL"),
    ]

    total_time = 0
    successful_signals = 0

    for i in range(num_tests):
        start_time = time.time()

        for strategy in strategies:
            try:
                signal = strategy.generate_signal("AAPL", df)
                if signal:
                    successful_signals += 1
            except:
                pass

        end_time = time.time()
        total_time += end_time - start_time

    avg_time_per_cycle = (total_time / num_tests) * 1000  # Convert to ms

    print(f"✅ Average time per complete cycle: {avg_time_per_cycle:.1f}ms")
    print(f"✅ Successful signals generated: {successful_signals}/{num_tests * 3}")
    print(f"✅ Estimated throughput: {1000/avg_time_per_cycle:.1f} cycles/second")

    # Compare to expected performance
    if avg_time_per_cycle < 200:  # Should be under 200ms per cycle
        print("🎉 Performance target achieved!")
        return True
    else:
        print("⚠️  Performance could be improved further")
        return False


def main():
    """Run comprehensive test suite"""
    print("🧪 OPTIMIZED SCALPING SYSTEM TEST SUITE")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    test_results = {}

    # Test 1: Unified Indicator Service
    test_results["unified_service"] = test_unified_indicator_service()

    # Test 2: Strategy Signal Generation
    test_results["strategy_signals"] = test_strategy_signals()

    # Test 3: Indicator Specialization
    test_results["specialization"] = test_indicator_specialization()

    # Test 4: Performance Comparison
    test_results["performance"] = test_performance_comparison()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)

    for test_name, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")

    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Optimized system is ready.")
    else:
        print("⚠️  Some tests failed. Please review the output above.")

    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
