#!/usr/bin/env python3
"""
Trading Engine Diagnostics Tool
Check if the trading engine is working properly and identify configuration issues
"""

import sys
import time
from datetime import datetime

from config import config, validate_config
from core.data_manager import DataManager
from utils.logger import setup_logger


def run_diagnostics():
    """Run comprehensive diagnostics on the trading engine"""

    print("🔍 TRADING ENGINE DIAGNOSTICS")
    print("=" * 50)

    # Initialize logger
    logger = setup_logger("diagnostics")
    logger.info("Starting trading engine diagnostics")

    try:
        # 1. Configuration Check
        print("\n1️⃣ CONFIGURATION CHECK")
        try:
            validate_config()
            print("✅ Configuration validation: PASSED")
        except Exception as e:
            print(f"❌ Configuration validation: FAILED - {e}")
            return False

        # 2. API Connection Check
        print("\n2️⃣ API CONNECTION CHECK")
        try:
            data_manager = DataManager()
            account = data_manager.get_account_info()
            print(f"✅ API Connection: PASSED")
            print(f"   Account Equity: ${account['equity']:,.2f}")
            print(f"   Buying Power: ${account['buying_power']:,.2f}")
            print(f"   Account Status: {account.get('status', 'ACTIVE')}")
        except Exception as e:
            print(f"❌ API Connection: FAILED - {e}")
            return False

        # 3. Market Hours Check
        print("\n3️⃣ MARKET HOURS CHECK")
        try:
            market_status = data_manager.get_market_status()
            is_open = market_status.get("is_open", False)
            next_open = market_status.get("next_open", "Unknown")
            next_close = market_status.get("next_close", "Unknown")

            print(f"✅ Market Status Check: PASSED")
            print(f"   Market Open: {'YES' if is_open else 'NO'}")
            print(f"   Next Open: {next_open}")
            print(f"   Next Close: {next_close}")

            if not is_open:
                print("⚠️  WARNING: Market is currently closed")
                print("   This explains why trading engine might be quiet")
        except Exception as e:
            print(f"❌ Market Status Check: FAILED - {e}")

        # 4. Watchlist Check
        print("\n4️⃣ WATCHLIST CHECK")
        try:
            watchlist = config["INTRADAY_WATCHLIST"]
            print(f"✅ Watchlist: {len(watchlist)} symbols")
            print(f"   Symbols: {', '.join(watchlist)}")

            # Test data for first symbol
            if watchlist:
                test_symbol = watchlist[0]
                df = data_manager.get_bars(test_symbol, config["TIMEFRAME"])
                print(f"✅ Data Fetch Test ({test_symbol}): {len(df)} bars")
        except Exception as e:
            print(f"❌ Watchlist Check: FAILED - {e}")

        # 5. Trading Parameters Check
        print("\n5️⃣ TRADING PARAMETERS CHECK")
        key_params = [
            "CHECK_INTERVAL",
            "TIMEFRAME",
            "MAX_POSITIONS",
            "POSITION_SIZE",
            "RISK_PER_TRADE",
            "MAX_DAILY_LOSS",
        ]

        for param in key_params:
            value = config.get(param, "NOT SET")
            print(f"   {param}: {value}")

        # 6. Risk Limits Check
        print("\n6️⃣ RISK LIMITS CHECK")
        try:
            positions = data_manager.get_positions()
            print(f"✅ Current Positions: {len(positions)}")
            print(f"   Max Allowed: {config['MAX_POSITIONS']}")

            if len(positions) >= config["MAX_POSITIONS"]:
                print("⚠️  WARNING: Maximum positions reached - no new trades allowed")
        except Exception as e:
            print(f"❌ Risk Check: FAILED - {e}")

        # 7. Process Check
        print("\n7️⃣ PROCESS STATUS CHECK")
        try:
            # Use PowerShell to check processes
            import subprocess

            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    'Get-Process | Where-Object {$_.ProcessName -eq "python"} | Select-Object Id, ProcessName',
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                print("✅ Python processes found running")
                print(f"   Output: {result.stdout.strip()}")
            else:
                print("❌ No Python processes found")
        except Exception as e:
            print(f"⚠️  Process Check: Could not verify - {e}")

        # 8. Log File Check
        print("\n8️⃣ LOG FILE STATUS")
        import os

        log_files = [
            "intraday_intraday_engine_20250820.log",
            "intraday_order_manager_20250820.log",
            "intraday_trading_launcher_20250820.log",
        ]

        for log_file in log_files:
            path = f"logs/{log_file}"
            if os.path.exists(path):
                size = os.path.getsize(path)
                modified = datetime.fromtimestamp(os.path.getmtime(path))
                print(f"✅ {log_file}: {size} bytes, last modified {modified}")

                # Check if recently modified (within last hour)
                age_minutes = (datetime.now() - modified).total_seconds() / 60
                if age_minutes > 60:
                    print(
                        f"   ⚠️  WARNING: Log not updated in {age_minutes:.0f} minutes"
                    )
            else:
                print(f"❌ {log_file}: NOT FOUND")

        print("\n" + "=" * 50)
        print("🎯 DIAGNOSTIC SUMMARY")
        print("If you see warnings above, those might explain")
        print("why the trading engine appears quiet.")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        logger.error(f"Diagnostics failed: {e}")
        return False


if __name__ == "__main__":
    run_diagnostics()
