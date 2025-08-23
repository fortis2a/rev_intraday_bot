#!/usr/bin/env python3
"""
ENHANCED SIGNAL MONITOR
=======================

Monitor live trading signals, cycles, and actions with detailed output.
"""

import os
import time
import subprocess
from datetime import datetime


def get_latest_log_content(log_file, lines=50):
    """Get latest content from log file"""
    try:
        result = subprocess.run(
            [
                "powershell",
                "-Command",
                f"Get-Content 'logs\\{log_file}' -Tail {lines} 2>$null",
            ],
            capture_output=True,
            text=True,
            timeout=3,
        )

        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split("\n")
        return []
    except:
        return []


def filter_trading_signals(lines):
    """Filter lines for actual trading signals and actions"""
    signal_keywords = [
        "SIGNAL",
        "BUY",
        "SELL",
        "ORDER",
        "EXECUTION",
        "FILLED",
        "CYCLE",
        "SCANNING",
        "GENERATED",
        "PLACED",
        "CANCELLED",
        "PROFIT",
        "STOP",
        "TRAIL",
        "POSITION",
        "ENTRY",
        "EXIT",
    ]

    trading_lines = []
    for line in lines:
        if any(keyword in line.upper() for keyword in signal_keywords):
            # Only show recent entries (from today)
            if (
                "10:" in line
                or "11:" in line
                or "12:" in line
                or "13:" in line
                or "14:" in line
                or "15:" in line
            ):
                trading_lines.append(line.strip())

    return trading_lines[-10:]  # Return last 10 trading-related entries


def main():
    print("🔍 ENHANCED SIGNAL MONITOR - LIVE TRADING ACTIVITY")
    print("=" * 70)

    today = datetime.now().strftime("%Y%m%d")

    # Track last seen entries to show only new ones
    last_engine_entry = ""
    last_order_entry = ""

    while True:
        print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Live Trading Activity")
        print("-" * 70)

        # Check intraday engine for trading cycles and signals
        engine_logs = get_latest_log_content(
            f"intraday_intraday_engine_{today}.log", 100
        )
        trading_signals = filter_trading_signals(engine_logs)

        if trading_signals:
            print("🎯 TRADING SIGNALS & CYCLES:")
            for line in trading_signals[-5:]:  # Show last 5 signal-related entries
                if "CYCLE" in line.upper():
                    print(f"   🔄 {line}")
                elif "SIGNAL" in line.upper():
                    print(f"   ⚡ {line}")
                elif "SCANNING" in line.upper():
                    print(f"   🔍 {line}")
                else:
                    print(f"   📊 {line}")
        else:
            print("🎯 TRADING SIGNALS & CYCLES:")
            print("   ⏳ No recent trading signals detected")

        # Check order manager for actual trades
        order_logs = get_latest_log_content(f"intraday_order_manager_{today}.log", 50)
        order_signals = filter_trading_signals(order_logs)

        if order_signals:
            print("\n� ORDERS & EXECUTIONS:")
            for line in order_signals[-5:]:  # Show last 5 order-related entries
                if "BUY" in line.upper() or "SELL" in line.upper():
                    print(f"   🚀 {line}")
                elif "ORDER" in line.upper():
                    print(f"   📋 {line}")
                elif "EXECUTION" in line.upper() or "FILLED" in line.upper():
                    print(f"   ✅ {line}")
                else:
                    print(f"   � {line}")
        else:
            print("\n💰 ORDERS & EXECUTIONS:")
            print("   💤 No recent order activity")

        # Check risk manager for stops and trailing
        risk_logs = get_latest_log_content(f"intraday_risk_manager_{today}.log", 30)
        risk_signals = filter_trading_signals(risk_logs)

        if risk_signals:
            print("\n🛡️ RISK MANAGEMENT:")
            for line in risk_signals[-3:]:  # Show last 3 risk-related entries
                if "STOP" in line.upper():
                    print(f"   🛑 {line}")
                elif "TRAIL" in line.upper():
                    print(f"   📈 {line}")
                else:
                    print(f"   🔒 {line}")

        # Check trailing stop manager
        trail_logs = get_latest_log_content(
            f"intraday_trailing_stop_manager_{today}.log", 30
        )
        trail_signals = filter_trading_signals(trail_logs)

        if trail_signals:
            print("\n� TRAILING STOPS:")
            for line in trail_signals[-3:]:
                print(f"   📉 {line}")

        # Show current bot status
        launcher_logs = get_latest_log_content(
            f"intraday_trading_launcher_{today}.log", 5
        )
        if launcher_logs:
            print(
                f"\n🤖 BOT STATUS: {launcher_logs[-1] if launcher_logs else 'Unknown'}"
            )

        print("\n" + "=" * 70)
        print("💡 Watching for: SIGNALS, ORDERS, EXECUTIONS, STOPS, TRAILS")
        print("🔄 Updates every 8 seconds - Press Ctrl+C to stop")

        time.sleep(8)  # Update every 8 seconds for more responsive monitoring


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")
