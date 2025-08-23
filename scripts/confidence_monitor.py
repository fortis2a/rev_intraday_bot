#!/usr/bin/env python3
"""
🎯 Real-Time Confidence Monitor
Live monitoring of confidence signals for all watchlist stocks
Shows which stocks exceed the 75% trading threshold
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import config
from core.real_time_confidence import RealTimeConfidenceCalculator
from stock_specific_config import get_stock_thresholds, should_execute_trade
from utils.logger import setup_logger


class ConfidenceMonitor:
    def __init__(self):
        self.logger = setup_logger("confidence_monitor")
        self.calculator = RealTimeConfidenceCalculator()
        self.watchlist = config.INTRADAY_WATCHLIST  # Use the correct attribute name
        self.confidence_threshold = 75.0
        self.refresh_interval = 10  # seconds

    def get_confidence_data(self, symbol):
        """Get comprehensive confidence data for a symbol"""
        try:
            # Test both BUY (LONG) and SELL (SHORT) signals
            buy_decision = should_execute_trade(symbol, "BUY")
            sell_decision = should_execute_trade(symbol, "SELL")

            # Get stock-specific thresholds
            thresholds = get_stock_thresholds(symbol)

            # Determine the best direction based on confidence
            if buy_decision["confidence"] >= sell_decision["confidence"]:
                primary_decision = buy_decision
                direction = "LONG"
                alt_confidence = sell_decision["confidence"]
                alt_direction = "SHORT"
            else:
                primary_decision = sell_decision
                direction = "SHORT"
                alt_confidence = buy_decision["confidence"]
                alt_direction = "LONG"

            return {
                "symbol": symbol,
                "confidence": primary_decision["confidence"],
                "direction": direction,
                "alt_confidence": alt_confidence,
                "alt_direction": alt_direction,
                "tradeable": primary_decision["execute"],
                "reason": primary_decision["reason"],
                "technical_summary": primary_decision.get("technical_summary", {}),
                "thresholds": thresholds,
                "timestamp": primary_decision.get(
                    "timestamp", datetime.now().strftime("%H:%M:%S")
                ),
            }
        except Exception as e:
            return {
                "symbol": symbol,
                "confidence": 0.0,
                "direction": "ERROR",
                "alt_confidence": 0.0,
                "alt_direction": "ERROR",
                "tradeable": False,
                "reason": f"Error: {str(e)}",
                "technical_summary": {},
                "thresholds": {},
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }

    def format_confidence_display(self, data):
        """Format confidence data for display"""
        symbol = data["symbol"]
        confidence = data["confidence"]
        direction = data["direction"]
        alt_confidence = data.get("alt_confidence", 0)
        alt_direction = data.get("alt_direction", "N/A")
        tradeable = data["tradeable"]
        tech = data["technical_summary"]
        thresholds = data["thresholds"]

        # Status indicator with direction
        if confidence >= self.confidence_threshold:
            status = f"🟢 {direction}" if tradeable else f"🟡 {direction}"
            status_color = "GREEN" if tradeable else "YELLOW"
        else:
            status = f"🔴 {direction}"
            status_color = "RED"

        # Technical indicators summary
        macd_status = "✅" if tech.get("macd_bullish", False) else "❌"
        ema9_status = "✅" if tech.get("above_ema9", False) else "❌"
        vwap_status = "✅" if tech.get("above_vwap", False) else "❌"

        # Risk thresholds
        stop_pct = thresholds.get("stop_loss_pct", 0) * 100
        profit_pct = thresholds.get("take_profit_pct", 0) * 100

        return {
            "symbol": symbol,
            "confidence": confidence,
            "direction": direction,
            "alt_confidence": alt_confidence,
            "alt_direction": alt_direction,
            "status": status,
            "status_color": status_color,
            "macd": macd_status,
            "ema9": ema9_status,
            "vwap": vwap_status,
            "rsi": tech.get("rsi_level", "N/A"),
            "volume": tech.get("volume_multiple", "N/A"),
            "stop_pct": stop_pct,
            "profit_pct": profit_pct,
            "timestamp": data["timestamp"],
        }

    def display_confidence_dashboard(self):
        """Display the real-time confidence dashboard"""
        # Clear screen safely
        import subprocess

        try:
            if os.name == "nt":
                subprocess.run(["cls"], shell=False, check=True, capture_output=True)
            else:
                subprocess.run(["clear"], shell=False, check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to simple screen clearing with ANSI codes
            print("\033[2J\033[H", end="")

        print("🎯 REAL-TIME CONFIDENCE MONITOR")
        print("=" * 120)
        print(
            f"⏰ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 🎯 Threshold: {self.confidence_threshold}% | 🔄 Refresh: {self.refresh_interval}s"
        )
        print()

        # Get confidence data for all symbols
        confidence_data = []
        for symbol in self.watchlist:
            data = self.get_confidence_data(symbol)
            formatted = self.format_confidence_display(data)
            confidence_data.append(formatted)

        # Sort by confidence (highest first)
        confidence_data.sort(key=lambda x: x["confidence"], reverse=True)

        # Display header
        print(
            f"{'Symbol':<6} {'Confidence':<11} {'Direction':<9} {'Alt':<7} {'MACD':<5} {'EMA9':<5} {'VWAP':<5} {'RSI':<6} {'Vol':<6} {'Stop%':<6} {'Profit%':<7} {'Updated':<8}"
        )
        print("-" * 120)

        # Display each stock
        tradeable_count = 0
        for data in confidence_data:
            if data["confidence"] >= self.confidence_threshold:
                tradeable_count += 1

            # Format values
            conf_str = f"{data['confidence']:.1f}%"
            alt_str = f"{data['alt_confidence']:.0f}%"
            rsi_str = (
                f"{data['rsi']}" if isinstance(data["rsi"], (int, float)) else "N/A"
            )
            vol_str = (
                f"{data['volume']:.1f}x"
                if isinstance(data["volume"], (int, float))
                else "N/A"
            )
            stop_str = f"{data['stop_pct']:.2f}%"
            profit_str = f"{data['profit_pct']:.2f}%"

            print(
                f"{data['symbol']:<6} {conf_str:<11} {data['status']:<9} {alt_str:<7} {data['macd']:<5} {data['ema9']:<5} {data['vwap']:<5} {rsi_str:<6} {vol_str:<6} {stop_str:<6} {profit_str:<7} {data['timestamp']:<8}"
            )

        print("-" * 120)
        print(
            f"📊 SUMMARY: {tradeable_count}/{len(self.watchlist)} stocks above {self.confidence_threshold}% threshold"
        )

        # Trading recommendations
        print(f"\n🎯 TRADING RECOMMENDATIONS:")
        tradeable_stocks = [
            data
            for data in confidence_data
            if data["confidence"] >= self.confidence_threshold
        ]

        if tradeable_stocks:
            print(f"✅ READY TO TRADE ({len(tradeable_stocks)} stocks):")
            for stock in tradeable_stocks:
                print(
                    f"   • {stock['symbol']}: {stock['confidence']:.1f}% confidence - {stock['direction']} (Alt: {stock['alt_direction']} {stock['alt_confidence']:.0f}%)"
                )
        else:
            print(
                f"⚠️  NO STOCKS currently meet the {self.confidence_threshold}% threshold"
            )

        # Warning for low confidence stocks
        low_confidence = [
            data
            for data in confidence_data
            if data["confidence"] < self.confidence_threshold
        ]
        if low_confidence:
            print(f"\n🚫 AVOID TRADING ({len(low_confidence)} stocks below threshold):")
            for stock in low_confidence[:3]:  # Show top 3 closest to threshold
                print(
                    f"   • {stock['symbol']}: {stock['confidence']:.1f}% confidence - {stock['status']}"
                )

        print(
            f"\n💡 LEGEND: 🟢=Trade Ready | 🟡=Review Required | 🔴=Skip | ✅=Bullish | ❌=Bearish"
        )
        print(
            f"⏰ Monitoring every {self.refresh_interval} seconds - Press Ctrl+C to stop"
        )

    def run_monitor(self):
        """Run the continuous monitoring loop"""
        print("🎯 Starting Real-Time Confidence Monitor...")
        print(
            f"📊 Monitoring {len(self.watchlist)} stocks: {', '.join(self.watchlist)}"
        )
        print(f"🎯 Trading threshold: {self.confidence_threshold}%")
        print(f"🔄 Refresh interval: {self.refresh_interval} seconds")
        print("\nPress Ctrl+C to stop monitoring\n")

        try:
            while True:
                self.display_confidence_dashboard()
                time.sleep(self.refresh_interval)

        except KeyboardInterrupt:
            print(f"\n\n🛑 Confidence monitoring stopped.")
            print(
                f"📊 Monitor can be restarted anytime using: python scripts/confidence_monitor.py"
            )
        except Exception as e:
            self.logger.error(f"❌ Error in confidence monitor: {e}")
            print(f"\n❌ Error: {e}")


def main():
    """Main entry point"""
    try:
        monitor = ConfidenceMonitor()
        monitor.run_monitor()
    except Exception as e:
        print(f"❌ Failed to start confidence monitor: {e}")
        import traceback

        print(f"Details: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
