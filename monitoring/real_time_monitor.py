#!/usr/bin/env python3
"""
REAL-TIME BOT MONITOR
====================

This script monitors the trading bot in real-time and displays:
- Signal generation
- Trade executions
- Order placements
- Position changes
- Risk management actions

Run this in a separate terminal while the bot is running.
"""

import os
import subprocess
import time
from datetime import datetime
from pathlib import Path


class RealTimeBotMonitor:
    def __init__(self):
        self.log_dir = Path("logs")
        self.today = datetime.now().strftime("%Y%m%d")

        # Key log files to monitor
        self.log_files = {
            "engine": f"intraday_intraday_engine_{self.today}.log",
            "order_manager": f"intraday_order_manager_{self.today}.log",
            "risk_manager": f"intraday_risk_manager_{self.today}.log",
            "trailing_stop": f"intraday_trailing_stop_manager_{self.today}.log",
        }

        # Track last read positions
        self.last_positions = {}

        print("🤖 REAL-TIME BOT MONITOR STARTED")
        print("=" * 60)
        print(f"📅 Date: {self.today}")
        print(f"📂 Monitoring: {len(self.log_files)} log files")
        print("=" * 60)

    def get_latest_lines(self, log_file, num_lines=5):
        """Get the latest lines from a log file"""
        file_path = self.log_dir / log_file

        if not file_path.exists():
            return []

        try:
            # Use PowerShell to get tail (since this is Windows)
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f"Get-Content '{file_path}' -Tail {num_lines}",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                return (
                    result.stdout.strip().split("\n") if result.stdout.strip() else []
                )
            else:
                return []
        except Exception as e:
            return []

    def check_for_signals(self):
        """Check for trading signals in the logs"""
        signal_keywords = [
            "SIGNAL",
            "BUY",
            "SELL",
            "ORDER",
            "EXECUTION",
            "PROFIT",
            "STOP",
            "TRAIL",
            "POSITION",
        ]

        for log_name, log_file in self.log_files.items():
            recent_lines = self.get_latest_lines(log_file, 3)

            for line in recent_lines:
                if any(keyword in line.upper() for keyword in signal_keywords):
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"🔥 [{timestamp}] {log_name.upper()}: {line.strip()}")

    def check_process_status(self):
        """Check if the bot processes are running"""
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Get-Process python -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                count = (
                    int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
                )
                if count > 0:
                    return f"✅ {count} Python processes running"
                else:
                    return "❌ No Python processes detected"
            else:
                return "❓ Unable to check process status"
        except Exception as e:
            return f"⚠️ Error checking processes: {e}"

    def show_summary(self):
        """Show current trading summary"""
        print(f"\n📊 TRADING SUMMARY - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 50)

        # Check engine log for latest activity
        engine_lines = self.get_latest_lines(self.log_files["engine"], 10)
        if engine_lines:
            print("🔄 Latest Engine Activity:")
            for line in engine_lines[-3:]:  # Show last 3 lines
                if line.strip():
                    print(f"   {line.strip()}")

        # Check order manager for signals
        order_lines = self.get_latest_lines(self.log_files["order_manager"], 5)
        if order_lines:
            print("\n📈 Latest Order Activity:")
            for line in order_lines[-2:]:  # Show last 2 lines
                if line.strip():
                    print(f"   {line.strip()}")

        # Process status
        print(f"\n🖥️ Process Status: {self.check_process_status()}")
        print("-" * 50)

    def monitor_live(self):
        """Start live monitoring"""
        print("🎯 LIVE MONITORING ACTIVE")
        print("Press Ctrl+C to stop monitoring\n")

        try:
            while True:
                # Show summary every 30 seconds
                self.show_summary()

                # Check for signals every 5 seconds
                for i in range(6):  # 6 * 5 = 30 seconds
                    self.check_for_signals()
                    time.sleep(5)

        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Error during monitoring: {e}")


def main():
    """Main function"""
    monitor = RealTimeBotMonitor()
    monitor.monitor_live()


if __name__ == "__main__":
    main()
