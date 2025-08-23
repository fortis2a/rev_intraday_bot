#!/usr/bin/env python3
"""
Trading Database Manager
Handles storage and retrieval of trading activities from Alpaca
"""

import logging
import os
import sqlite3
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import alpaca_trade_api as tradeapi
import pandas as pd
from dotenv import load_dotenv

# Load environment
load_dotenv()


class TradingDatabase:
    """Manages trading data storage and retrieval"""

    def __init__(self, db_path: str = "data/trading.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize Alpaca API
        self.api = tradeapi.REST(
            os.getenv("ALPACA_API_KEY"),
            os.getenv("ALPACA_SECRET_KEY"),
            os.getenv("ALPACA_BASE_URL"),
            api_version="v2",
        )

        # Setup logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Trading activities table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS trading_activities (
                    id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    value REAL NOT NULL,
                    transaction_time TIMESTAMP NOT NULL,
                    trade_date DATE NOT NULL,
                    hour INTEGER NOT NULL,
                    minute INTEGER NOT NULL,
                    activity_type TEXT DEFAULT 'FILL',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(id, transaction_time)
                )
            """
            )

            # Daily summaries table for quick lookups
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_summaries (
                    trade_date DATE PRIMARY KEY,
                    total_trades INTEGER NOT NULL,
                    unique_symbols INTEGER NOT NULL,
                    total_volume REAL NOT NULL,
                    cash_flow_pnl REAL NOT NULL,
                    trading_pnl REAL NOT NULL,
                    positions_opened INTEGER DEFAULT 0,
                    positions_closed INTEGER DEFAULT 0,
                    day_trades INTEGER DEFAULT 0,
                    symbols_traded TEXT NOT NULL,
                    first_trade_time TIMESTAMP,
                    last_trade_time TIMESTAMP,
                    trading_hours REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Data collection log
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS collection_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    collection_date DATE NOT NULL,
                    activities_fetched INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    error_message TEXT,
                    collection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(collection_date)
                )
            """
            )

            # Create indexes for performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_activities_date ON trading_activities(trade_date)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_activities_symbol ON trading_activities(symbol)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_activities_time ON trading_activities(transaction_time)"
            )

            conn.commit()
            self.logger.info("Database initialized successfully")

    def fetch_and_store_activities(self, target_date: date) -> Tuple[int, bool]:
        """
        Fetch activities for a specific date and store in database
        Returns: (activities_count, success)
        """
        try:
            self.logger.info(f"Fetching activities for {target_date}")

            # Check if data already exists
            if self._date_exists(target_date):
                self.logger.info(f"Data for {target_date} already exists, skipping...")
                return 0, True

            # Fetch from Alpaca with pagination (page_size max is 100)
            all_activities = []
            page_token = None

            while True:
                activities = self.api.get_activities(
                    activity_types="FILL",
                    date=target_date.strftime("%Y-%m-%d"),
                    direction="desc",
                    page_size=100,
                    page_token=page_token,
                )

                if not activities:
                    break

                all_activities.extend(activities)

                # Check if there are more pages
                if len(activities) < 100:
                    break

                # Get page token for next page (if available)
                page_token = getattr(activities[-1], "page_token", None)
                if not page_token:
                    break

            activities = all_activities

            if not activities:
                self.logger.info(f"No activities found for {target_date}")
                self._log_collection(target_date, 0, "SUCCESS", None)
                return 0, True

            # Store activities
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                for activity in activities:
                    # Convert timestamp to string for SQLite
                    transaction_time_str = activity.transaction_time.isoformat()

                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO trading_activities 
                        (id, symbol, side, quantity, price, value, transaction_time, 
                         trade_date, hour, minute, activity_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            activity.id,
                            activity.symbol,
                            activity.side,
                            float(activity.qty),
                            float(activity.price),
                            float(activity.qty) * float(activity.price),
                            transaction_time_str,
                            target_date,
                            activity.transaction_time.hour,
                            activity.transaction_time.minute,
                            "FILL",
                        ),
                    )

                conn.commit()

            # Generate daily summary
            self._generate_daily_summary(target_date)

            # Log successful collection
            self._log_collection(target_date, len(activities), "SUCCESS", None)

            self.logger.info(
                f"Successfully stored {len(activities)} activities for {target_date}"
            )
            return len(activities), True

        except Exception as e:
            error_msg = str(e)
            self.logger.error(
                f"Error fetching activities for {target_date}: {error_msg}"
            )
            self._log_collection(target_date, 0, "ERROR", error_msg)
            return 0, False

    def _date_exists(self, target_date: date) -> bool:
        """Check if data for date already exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM trading_activities WHERE trade_date = ?",
                (target_date,),
            )
            return cursor.fetchone()[0] > 0

    def _generate_daily_summary(self, target_date: date):
        """Generate daily summary for the given date with Alpaca P&L"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Calculate basic summary metrics
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_trades,
                    COUNT(DISTINCT symbol) as unique_symbols,
                    SUM(value) as total_volume,
                    MIN(transaction_time) as first_trade,
                    MAX(transaction_time) as last_trade,
                    GROUP_CONCAT(DISTINCT symbol) as symbols
                FROM trading_activities 
                WHERE trade_date = ?
            """,
                (target_date,),
            )

            row = cursor.fetchone()
            if not row or row[0] == 0:
                return

            (
                total_trades,
                unique_symbols,
                total_volume,
                first_trade,
                last_trade,
                symbols,
            ) = row

            # Calculate cash flow P&L
            cursor.execute(
                """
                SELECT side, SUM(value) as total_value
                FROM trading_activities 
                WHERE trade_date = ?
                GROUP BY side
            """,
                (target_date,),
            )

            side_totals = {side: total for side, total in cursor.fetchall()}

            # Calculate cash flow P&L (sells + short_sells - buys)
            sells = side_totals.get("sell", 0) + side_totals.get("sell_short", 0)
            buys = side_totals.get("buy", 0)
            cash_flow_pnl = sells - buys

            # Get Alpaca's actual P&L (source of truth)
            try:
                sys.path.insert(0, str(Path(__file__).parent.parent))
                from alpaca_pnl_fetcher import AlpacaPnLFetcher

                fetcher = AlpacaPnLFetcher()
                alpaca_result = fetcher.get_daily_pnl(target_date)

                if alpaca_result.get("error"):
                    self.logger.warning(
                        f"Alpaca P&L fetch failed: {alpaca_result['error']}"
                    )
                    alpaca_pnl = cash_flow_pnl  # Fallback
                    trading_pnl = cash_flow_pnl
                else:
                    alpaca_pnl = alpaca_result["alpaca_pnl"]
                    trading_pnl = alpaca_pnl  # Use Alpaca as source of truth

            except Exception as e:
                self.logger.warning(f"Alpaca P&L calculation failed: {str(e)}")
                alpaca_pnl = cash_flow_pnl
                trading_pnl = cash_flow_pnl

            # Calculate trading hours
            if first_trade and last_trade:
                first_dt = datetime.fromisoformat(first_trade.replace("Z", "+00:00"))
                last_dt = datetime.fromisoformat(last_trade.replace("Z", "+00:00"))
                trading_hours = (last_dt - first_dt).total_seconds() / 3600
            else:
                trading_hours = 0

            # Insert or update daily summary
            cursor.execute(
                """
                INSERT OR REPLACE INTO daily_summaries 
                (trade_date, total_trades, unique_symbols, total_volume, cash_flow_pnl, 
                 trading_pnl, alpaca_pnl, positions_opened, positions_closed, day_trades,
                 symbols_traded, first_trade_time, last_trade_time, trading_hours, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
                (
                    target_date,
                    total_trades,
                    unique_symbols,
                    total_volume,
                    cash_flow_pnl,
                    trading_pnl,
                    alpaca_pnl,
                    0,
                    0,
                    0,  # positions data placeholder
                    symbols,
                    first_trade,
                    last_trade,
                    trading_hours,
                ),
            )

            conn.commit()
            self.logger.info(
                f"Generated daily summary for {target_date}: {total_trades} trades, "
                f"Cash Flow: ${cash_flow_pnl:.2f}, Alpaca P&L: ${alpaca_pnl:.2f}"
            )

    def _log_collection(
        self, target_date: date, count: int, status: str, error: Optional[str]
    ):
        """Log collection attempt"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO collection_log 
                (collection_date, activities_fetched, status, error_message, collection_time)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
                (target_date, count, status, error),
            )
            conn.commit()

    def get_activities(self, start_date: date, end_date: date = None) -> pd.DataFrame:
        """Get activities for date range"""
        if end_date is None:
            end_date = start_date

        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT * FROM trading_activities 
                WHERE trade_date BETWEEN ? AND ?
                ORDER BY transaction_time
            """
            return pd.read_sql_query(query, conn, params=(start_date, end_date))

    def get_daily_summary(self, target_date: date) -> Optional[Dict]:
        """Get daily summary for a specific date"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM daily_summaries WHERE trade_date = ?", (target_date,)
            )
            row = cursor.fetchone()

            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None

    def get_date_range_summaries(
        self, start_date: date, end_date: date
    ) -> pd.DataFrame:
        """Get daily summaries for date range"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT * FROM daily_summaries 
                WHERE trade_date BETWEEN ? AND ?
                ORDER BY trade_date
            """
            return pd.read_sql_query(query, conn, params=(start_date, end_date))

    def backfill_historical_data(self, start_date: date, end_date: date = None):
        """Backfill historical data for date range"""
        if end_date is None:
            end_date = date.today() - timedelta(days=1)  # Yesterday

        current_date = start_date
        success_count = 0
        error_count = 0

        self.logger.info(f"Starting backfill from {start_date} to {end_date}")

        while current_date <= end_date:
            # Skip weekends (Saturday=5, Sunday=6)
            if current_date.weekday() < 5:  # Monday=0 to Friday=4
                count, success = self.fetch_and_store_activities(current_date)
                if success:
                    success_count += 1
                    if count > 0:
                        self.logger.info(f"✅ {current_date}: {count} activities")
                    else:
                        self.logger.info(f"📅 {current_date}: No trading activity")
                else:
                    error_count += 1
                    self.logger.error(f"❌ {current_date}: Failed to fetch data")
            else:
                self.logger.info(f"⏭️  {current_date}: Skipping weekend")

            current_date += timedelta(days=1)

        self.logger.info(
            f"Backfill complete: {success_count} successful, {error_count} errors"
        )

    def get_collection_status(self) -> pd.DataFrame:
        """Get collection log status"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT * FROM collection_log 
                ORDER BY collection_date DESC
                LIMIT 30
            """
            return pd.read_sql_query(query, conn)


if __name__ == "__main__":
    # Initialize database
    db = TradingDatabase()

    # Backfill from 8/18/25 to yesterday
    start_date = date(2025, 8, 18)
    yesterday = date.today() - timedelta(days=1)

    print(f"🚀 Starting historical data collection from {start_date} to {yesterday}")
    db.backfill_historical_data(start_date, yesterday)

    print("\n📊 Collection Status:")
    status_df = db.get_collection_status()
    print(status_df.to_string(index=False))
