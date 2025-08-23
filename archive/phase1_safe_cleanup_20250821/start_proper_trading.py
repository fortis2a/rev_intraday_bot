#!/usr/bin/env python3
"""
Proper Intraday Trading Bot Startup
Uses core.intraday_engine.IntradayEngine with proper trading hour restrictions
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the proper intraday engine from core
from core.intraday_engine import IntradayEngine
from utils.logger import setup_logger


def main():
    """Start the proper intraday engine with trading hour restrictions"""
    logger = setup_logger("trading_bot_startup")

    print("=" * 70)
    print("         INTRADAY TRADING BOT - PROPER STARTUP")
    print("=" * 70)
    print("✅ Using core.intraday_engine.IntradayEngine")
    print("✅ Trading Hours: 10:00 AM - 3:30 PM (with 30-min buffers)")
    print("✅ NO trading first 30 minutes (9:30-10:00 AM)")
    print("✅ NO trading last 30 minutes (3:30-4:00 PM)")
    print("=" * 70)

    try:
        # Initialize the proper intraday engine with restrictions
        engine = IntradayEngine(demo_mode=False, bypass_market_hours=False)

        logger.info("Starting proper intraday engine with trading hour restrictions")
        print("[START] Initializing trading engine...")

        # Start the engine (this will respect trading hour restrictions)
        engine.run()

    except KeyboardInterrupt:
        print("\n[STOP] Trading engine stopped by user")
        logger.info("Trading engine stopped by user")
    except Exception as e:
        print(f"[ERROR] Failed to start trading engine: {e}")
        logger.error(f"Failed to start trading engine: {e}")


if __name__ == "__main__":
    main()
