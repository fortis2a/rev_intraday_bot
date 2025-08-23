#!/usr/bin/env python3
"""
Daily Data Collector - Scheduled to run at 4:15 PM
Fetches daily trading activities and stores in database
"""

import sys
import os
from pathlib import Path
from datetime import date, datetime, timedelta
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.trading_db import TradingDatabase


def setup_logging():
    """Setup logging for daily collection"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"daily_collection_{date.today().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )

    return logging.getLogger(__name__)


def collect_today_data():
    """Collect today's trading data"""
    logger = setup_logging()

    try:
        # Initialize database
        db = TradingDatabase()

        # Get today's date
        today = date.today()

        # Check if market is open today (weekday only)
        if today.weekday() >= 5:  # Saturday=5, Sunday=6
            logger.info(
                f"Market closed today ({today.strftime('%A')}), skipping collection"
            )
            return True

        logger.info(f"🕐 Starting daily data collection for {today}")

        # Fetch and store today's activities
        count, success = db.fetch_and_store_activities(today)

        if success:
            if count > 0:
                logger.info(
                    f"✅ Successfully collected {count} trading activities for {today}"
                )

                # Get summary for verification
                summary = db.get_daily_summary(today)
                if summary:
                    alpaca_pnl = summary.get("alpaca_pnl", summary.get("net_pnl", 0))
                    logger.info(
                        f"📊 Daily Summary: {summary['total_trades']} trades, "
                        f"${alpaca_pnl:.2f} Alpaca P&L, "
                        f"{summary['unique_symbols']} symbols: {summary['symbols_traded']}"
                    )
            else:
                logger.info(f"📅 No trading activity found for {today}")

            return True
        else:
            logger.error(f"❌ Failed to collect data for {today}")
            return False

    except Exception as e:
        logger.error(f"🚨 Critical error during daily collection: {str(e)}")
        return False


def collect_yesterday_if_missing():
    """Collect yesterday's data if missing (fallback)"""
    logger = logging.getLogger(__name__)

    try:
        db = TradingDatabase()
        yesterday = date.today() - timedelta(days=1)

        # Skip weekends
        if yesterday.weekday() >= 5:
            return True

        # Check if yesterday's data exists
        if not db._date_exists(yesterday):
            logger.info(f"🔄 Yesterday's data missing, collecting for {yesterday}")
            count, success = db.fetch_and_store_activities(yesterday)

            if success and count > 0:
                logger.info(f"✅ Collected {count} activities for {yesterday}")
            return success
        else:
            logger.info(f"✅ Yesterday's data ({yesterday}) already exists")
            return True

    except Exception as e:
        logger.error(f"Error collecting yesterday's data: {str(e)}")
        return False


if __name__ == "__main__":
    print(f"🕐 Daily Data Collection - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Collect yesterday's data if missing (fallback)
    collect_yesterday_if_missing()

    # Collect today's data
    success = collect_today_data()

    if success:
        print("✅ Daily data collection completed successfully")
        sys.exit(0)
    else:
        print("❌ Daily data collection failed")
        sys.exit(1)
