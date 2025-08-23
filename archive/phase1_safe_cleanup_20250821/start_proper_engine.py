#!/usr/bin/env python3
"""
Proper Intraday Engine Starter with Trading Hour Restrictions
Uses the core intraday engine that respects 30-minute buffers
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the proper core intraday engine
from core.intraday_engine import IntradayEngine
from utils.logger import setup_logger


def main():
    """Start the proper intraday engine with trading hour restrictions"""
    logger = setup_logger("start_proper_engine")

    print("=" * 70)
    print("         STARTING PROPER INTRADAY ENGINE")
    print("=" * 70)
    print("✅ Using core.intraday_engine.IntradayEngine")
    print("✅ Trading Hours: 10:00 AM - 3:30 PM (30-min buffers)")
    print("✅ NO trading first 30 minutes (9:30-10:00 AM)")
    print("✅ NO trading last 30 minutes (3:30-4:00 PM)")
    print("✅ Proper momentum strategy with confidence filtering")
    print("=" * 70)

    try:
        # Create the proper intraday engine with restrictions
        engine = IntradayEngine(demo_mode=False, bypass_market_hours=False)

        logger.info("Starting proper intraday engine with trading hour restrictions")
        print(f"[START] Engine initialized at {datetime.now().strftime('%H:%M:%S')}")

        # Start the engine
        engine.run()

    except KeyboardInterrupt:
        print("\n[STOP] Trading engine stopped by user")
        logger.info("Trading engine stopped by user")
    except Exception as e:
        print(f"[ERROR] Failed to start intraday engine: {e}")
        logger.error(f"Failed to start intraday engine: {e}")


if __name__ == "__main__":
    main()
