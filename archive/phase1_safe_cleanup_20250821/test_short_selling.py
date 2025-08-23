#!/usr/bin/env python3
"""
Test Short Selling Functionality
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from core.data_manager import DataManager
from core.order_manager import OrderManager
from strategies.mean_reversion import MeanReversionStrategy
from stock_specific_config import should_execute_trade


def test_short_selling():
    """Test short selling functionality with current NIO overbought signal"""
    print("=" * 60)
    print("SHORT SELLING FUNCTIONALITY TEST")
    print("=" * 60)

    # Initialize components
    data_manager = DataManager()
    order_manager = OrderManager(data_manager)

    # Check configuration
    print(f"Short Selling Enabled: {config.get('ENABLE_SHORT_SELLING', False)}")
    print(f"Allowed Stocks: {config.get('SHORT_SELLING_STOCKS', [])}")
    print(f"Min Confidence: {config.get('SHORT_SELLING_MIN_CONFIDENCE', 75.0)}%")
    print(f"Max Position Size: ${config.get('SHORT_SELLING_MAX_POSITION_SIZE', 500)}")
    print()

    # Test NIO which is currently overbought
    symbol = "NIO"
    print(f"Testing Short Selling for {symbol}")
    print("-" * 40)

    try:
        # Get current market data
        df = data_manager.get_bars(symbol, config["TIMEFRAME"])
        if df.empty or len(df) < 26:
            print(f"❌ Insufficient data for {symbol}")
            return

        # Calculate indicators
        df = data_manager.calculate_indicators(df)

        # Generate signal
        mean_rev = MeanReversionStrategy(symbol)
        signal = mean_rev.generate_signal(symbol, df)

        if signal and signal["action"] == "SELL":
            print(f"✅ SELL Signal Generated: {signal['reason']}")

            # Check confidence
            trade_decision = should_execute_trade(symbol)
            confidence = trade_decision.get("confidence", 0)

            print(f"📊 Confidence: {confidence:.1f}%")

            # Check current positions
            positions = data_manager.get_positions()
            existing_position = next(
                (p for p in positions if p["symbol"] == symbol), None
            )

            if existing_position:
                print(
                    f"⚠️  Existing Position: {existing_position['side']} {existing_position['qty']} shares"
                )
            else:
                print("✅ No existing position - eligible for short selling")

                # Test short selling logic (DRY RUN)
                current_price = data_manager.get_current_price(symbol)
                account_info = data_manager.get_account_info()

                print(f"💰 Current Price: ${current_price:.2f}")
                print(f"💰 Account Equity: ${account_info['equity']:,.2f}")
                print(f"💰 Buying Power: ${account_info['buying_power']:,.2f}")

                # Calculate what short position would look like
                max_short_position = config.get("SHORT_SELLING_MAX_POSITION_SIZE", 500)
                shares = int(
                    min(max_short_position, account_info["equity"] * 0.01)
                    / current_price
                )

                print(f"📈 Calculated Shares: {shares}")
                print(f"📈 Position Value: ${shares * current_price:.2f}")

                # Check confidence requirement
                min_confidence = config.get("SHORT_SELLING_MIN_CONFIDENCE", 75.0)
                if confidence >= min_confidence:
                    print(
                        f"✅ Confidence Check: {confidence:.1f}% >= {min_confidence}%"
                    )
                    print()
                    print("🔴 SHORT SELLING WOULD BE EXECUTED!")
                    print(f"   - Symbol: {symbol}")
                    print(f"   - Action: SHORT SELL")
                    print(f"   - Shares: {shares}")
                    print(f"   - Entry Price: ${current_price:.2f}")
                    print(f"   - Confidence: {confidence:.1f}%")

                    # Show what stop loss and take profit would be
                    thresholds = order_manager.get_stock_thresholds(symbol)
                    stop_loss_price = current_price * (1 + thresholds["stop_loss_pct"])
                    take_profit_price = current_price * (
                        1 - thresholds["take_profit_pct"]
                    )

                    print(
                        f"   - Stop Loss: ${stop_loss_price:.2f} ({thresholds['stop_loss_pct']*100:.2f}%)"
                    )
                    print(
                        f"   - Take Profit: ${take_profit_price:.2f} ({thresholds['take_profit_pct']*100:.2f}%)"
                    )
                else:
                    print(f"❌ Confidence Check: {confidence:.1f}% < {min_confidence}%")
                    print("   Short selling would be skipped")
        else:
            print(f"⚪ No SELL signal for {symbol}")

    except Exception as e:
        print(f"❌ Error testing {symbol}: {e}")
        import traceback

        traceback.print_exc()

    print()
    print("=" * 60)
    print("SHORT SELLING TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_short_selling()
