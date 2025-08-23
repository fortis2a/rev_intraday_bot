#!/usr/bin/env python3
"""
Real-time Trading Engine Status Monitor
Shows live status and alerts you to problems
"""

import os
import time
from datetime import datetime, timedelta


def monitor_trading_status():
    """Monitor trading engine status in real-time"""

    print("🔴 TRADING ENGINE STATUS MONITOR")
    print("Press Ctrl+C to stop monitoring")
    print("=" * 60)

    last_engine_size = 0
    last_order_size = 0
    alerts_shown = set()

    try:
        while True:
            current_time = datetime.now()
            print(f"\n⏰ {current_time.strftime('%H:%M:%S')} - Status Check")

            # Check engine log
            engine_log = "logs/intraday_intraday_engine_20250820.log"
            if os.path.exists(engine_log):
                current_size = os.path.getsize(engine_log)
                modified = datetime.fromtimestamp(os.path.getmtime(engine_log))
                age_minutes = (datetime.now() - modified).total_seconds() / 60

                if current_size > last_engine_size:
                    print(
                        f"✅ Trading Engine: ACTIVE (log growing: {current_size} bytes)"
                    )
                    last_engine_size = current_size
                    if "engine_stale" in alerts_shown:
                        alerts_shown.remove("engine_stale")
                elif age_minutes > 5:
                    if "engine_stale" not in alerts_shown:
                        print(
                            f"🚨 ALERT: Trading Engine STALE ({age_minutes:.0f} min since update)"
                        )
                        alerts_shown.add("engine_stale")
                    else:
                        print(f"⚠️  Trading Engine: STALE ({age_minutes:.0f} min)")
                else:
                    print(
                        f"⏳ Trading Engine: Waiting (last update {age_minutes:.1f} min ago)"
                    )
            else:
                print("❌ Trading Engine: LOG NOT FOUND")

            # Check order manager
            order_log = "logs/intraday_order_manager_20250820.log"
            if os.path.exists(order_log):
                current_size = os.path.getsize(order_log)
                if current_size > last_order_size:
                    print(f"💰 Order Manager: TRADES DETECTED ({current_size} bytes)")
                    last_order_size = current_size
                elif current_size == 0:
                    print(f"📋 Order Manager: No trades yet")
                else:
                    print(f"📋 Order Manager: {current_size} bytes logged")

            # Check command center activity
            cc_log = "logs/intraday_command_center_20250820.log"
            if os.path.exists(cc_log):
                modified = datetime.fromtimestamp(os.path.getmtime(cc_log))
                age_seconds = (datetime.now() - modified).total_seconds()
                if age_seconds < 10:
                    print(f"📊 Command Center: ACTIVE (updated {age_seconds:.0f}s ago)")
                else:
                    print(f"📊 Command Center: Last update {age_seconds:.0f}s ago")

            # Show market time remaining
            market_close = current_time.replace(
                hour=16, minute=0, second=0, microsecond=0
            )
            if current_time < market_close:
                remaining = market_close - current_time
                hours, remainder = divmod(remaining.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                print(f"🕐 Market closes in: {int(hours)}h {int(minutes)}m")
            else:
                print(f"🔴 Market is CLOSED")

            print("-" * 40)
            time.sleep(30)  # Check every 30 seconds

    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")


if __name__ == "__main__":
    monitor_trading_status()
