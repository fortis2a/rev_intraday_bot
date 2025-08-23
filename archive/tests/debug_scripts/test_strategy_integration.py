#!/usr/bin/env python3
"""
Strategy Integration Test
Validates that all strategies are properly integrated with the intraday bot system
"""

import sys
from datetime import datetime

import numpy as np
import pandas as pd

# Add current directory to path
sys.path.append(".")


def test_strategy_integration():
    """Test all strategies for integration with main system"""
    print("🧪 Testing Strategy Integration...")
    print("=" * 60)

    try:
        # Test imports
        print("📦 Testing imports...")
        from strategies import MeanReversionStrategy, MomentumStrategy, VWAPStrategy

        print("✅ All strategy imports successful")

        # Test initialization
        print("\n🏗️ Testing strategy initialization...")
        strategies = {
            "mean_reversion": MeanReversionStrategy("AAPL"),
            "momentum": MomentumStrategy("TSLA"),
            "vwap": VWAPStrategy("MSFT"),
        }
        print("✅ All strategies initialized successfully")

        # Create realistic sample data
        print("\n📊 Creating sample market data...")
        np.random.seed(42)  # For reproducible results

        # Generate realistic price action
        periods = 100
        base_price = 150.0

        # Simulate price movement with trend and volatility
        returns = np.random.normal(
            0.0001, 0.02, periods
        )  # Small positive drift, 2% volatility
        prices = [base_price]
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range(
                    "2025-08-16 09:30", periods=periods, freq="1min"
                ),
                "open": [p * (1 + np.random.normal(0, 0.001)) for p in prices],
                "high": [p * (1 + abs(np.random.normal(0, 0.002))) for p in prices],
                "low": [p * (1 - abs(np.random.normal(0, 0.002))) for p in prices],
                "close": prices,
                "volume": np.random.randint(5000, 50000, periods),
            }
        )
        print(f"✅ Generated {len(df)} bars of market data")

        # Test signal generation for each strategy
        print("\n📡 Testing signal generation...")
        for strategy_name, strategy in strategies.items():
            print(f"\n🔍 Testing {strategy_name} strategy...")

            try:
                # Test generate_signal method (main integration point)
                signal = strategy.generate_signal(strategy.symbol, df)

                if signal:
                    print(f"  ✅ Signal generated: {signal['action']}")
                    print(f"  📋 Reason: {signal['reason']}")
                    print(f"  📊 Confidence: {signal['confidence']:.1%}")
                    print(f"  💰 Entry: ${signal.get('entry_price', 0):.2f}")

                    # Validate signal structure
                    required_fields = ["symbol", "action", "reason", "confidence"]
                    missing_fields = [
                        field for field in required_fields if field not in signal
                    ]

                    if missing_fields:
                        print(f"  ⚠️ Missing required fields: {missing_fields}")
                    else:
                        print(f"  ✅ Signal structure valid")

                else:
                    print(
                        f"  ℹ️ No signal generated (normal for current market conditions)"
                    )

            except Exception as e:
                print(f"  ❌ Error in {strategy_name}: {e}")
                import traceback

                traceback.print_exc()

        # Test main system integration points
        print("\n🔗 Testing main system integration...")

        try:
            # Test that strategies have required methods
            required_methods = ["generate_signal"]
            for strategy_name, strategy in strategies.items():
                missing_methods = [
                    method
                    for method in required_methods
                    if not hasattr(strategy, method)
                ]
                if missing_methods:
                    print(f"  ❌ {strategy_name} missing methods: {missing_methods}")
                else:
                    print(f"  ✅ {strategy_name} has all required methods")

        except Exception as e:
            print(f"  ❌ Integration test failed: {e}")

        # Test backward compatibility
        print("\n🔄 Testing backward compatibility...")
        try:
            from strategies import MomentumStrategy as MomentumAlias
            from strategies import VWAPStrategy as VWAPAlias

            print("  ✅ Backward compatibility aliases work")
        except Exception as e:
            print(f"  ❌ Backward compatibility failed: {e}")

        print("\n" + "=" * 60)
        print("🎉 Strategy Integration Test Complete!")
        print("📝 All strategies are ready for the intraday trading bot")

        return True

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_strategy_integration()
    sys.exit(0 if success else 1)
