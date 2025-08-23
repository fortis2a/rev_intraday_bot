#!/usr/bin/env python3
"""
Data Manager for Intraday Trading Bot
Handles market data from Alpaca API
ASCII-only, no Unicode characters
"""

import alpaca_trade_api as tradeapi
import pandas as pd
from datetime import datetime, timedelta
import time
from config import config
from utils.logger import setup_logger, clean_message


class DataManager:
    """Manages market data and Alpaca API connection"""

    def __init__(self):
        self.logger = setup_logger("data_manager")
        self.logger.info("Initializing Data Manager...")

        # Initialize Alpaca API
        try:
            self.api = tradeapi.REST(
                config["ALPACA_API_KEY"],
                config["ALPACA_SECRET_KEY"],
                config["ALPACA_BASE_URL"],
                api_version="v2",
            )

            # Test connection
            account = self.api.get_account()
            equity = float(account.equity)
            buying_power = float(account.buying_power)

            self.logger.info(f"[ALPACA] Connected successfully")
            self.logger.info(f"[ALPACA] Account Equity: ${equity:,.2f}")
            self.logger.info(f"[ALPACA] Buying Power: ${buying_power:,.2f}")
            self.logger.info(f"[ALPACA] Status: {account.status}")

        except Exception as e:
            self.logger.error(f"[ERROR] Failed to connect to Alpaca: {e}")
            raise

    def ensure_connection(self):
        """Ensure API connection is working"""
        try:
            # Test connection with a simple API call
            account = self.api.get_account()
            return account is not None
        except Exception as e:
            self.logger.error(f"[ERROR] Connection check failed: {e}")
            return False

    def get_account_info(self):
        """Get current account information"""
        try:
            account = self.api.get_account()
            return {
                "equity": float(account.equity),
                "buying_power": float(account.buying_power),
                "cash": float(account.cash),
                "day_trading_buying_power": float(
                    getattr(account, "day_trading_buying_power", account.buying_power)
                ),
                "portfolio_value": float(account.portfolio_value),
            }
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to get account info: {e}")
            return None

    def get_daily_pnl(self):
        """Get Alpaca's official daily P&L calculation"""
        try:
            account = self.api.get_account()
            current_equity = float(account.equity)
            last_equity = float(account.last_equity)

            daily_pnl = current_equity - last_equity
            daily_return_pct = (daily_pnl / last_equity * 100) if last_equity > 0 else 0

            return {
                "daily_pnl": daily_pnl,
                "current_equity": current_equity,
                "last_equity": last_equity,
                "daily_return_pct": daily_return_pct,
            }
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to get daily P&L: {e}")
            return {
                "daily_pnl": 0.0,
                "current_equity": 0.0,
                "last_equity": 0.0,
                "daily_return_pct": 0.0,
            }

    def get_positions(self):
        """Get current positions"""
        try:
            positions = self.api.list_positions()
            position_data = []

            for pos in positions:
                position_data.append(
                    {
                        "symbol": pos.symbol,
                        "qty": float(pos.qty),
                        "side": pos.side,
                        "market_value": float(pos.market_value),
                        "unrealized_pl": float(pos.unrealized_pl),
                        "avg_entry_price": float(pos.avg_entry_price),
                    }
                )

            return position_data
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to get positions: {e}")
            return []

    def get_current_price(self, symbol):
        """Get current price for a symbol"""
        try:
            bars = self.api.get_latest_bar(symbol)
            return float(bars.c)  # closing price
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to get price for {symbol}: {e}")
            return None

    def get_bars(self, symbol, timeframe="15Min", limit=100):
        """Get historical bars for a symbol with sufficient data for indicators"""
        try:
            # Calculate start time with extended lookback to ensure sufficient data
            end_time = datetime.now()
            if timeframe == "1Min":
                start_time = end_time - timedelta(days=1)  # Extended for 1-min data
                limit = min(limit, 500)  # Ensure we don't hit API limits
            elif timeframe == "5Min":
                start_time = end_time - timedelta(days=3)  # Extended for 5-min data
                limit = min(limit, 300)
            elif timeframe == "15Min":
                start_time = end_time - timedelta(days=7)  # Extended for 15-min data
                limit = min(limit, 200)
            else:
                start_time = end_time - timedelta(
                    days=10
                )  # Extended for other timeframes
                limit = min(limit, 150)

            # Format timestamps for Alpaca API (RFC3339 format)
            start_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

            self.logger.debug(
                f"[DATA] Requesting {symbol} {timeframe} bars from {start_str} to {end_str} (limit: {limit})"
            )

            bars = self.api.get_bars(
                symbol, timeframe, start=start_str, end=end_str, limit=limit
            )

            # Convert to DataFrame
            df = pd.DataFrame(
                [
                    {
                        "timestamp": bar.t,
                        "open": float(bar.o),
                        "high": float(bar.h),
                        "low": float(bar.l),
                        "close": float(bar.c),
                        "volume": int(bar.v),
                    }
                    for bar in bars
                ]
            )

            if not df.empty:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df = df.set_index("timestamp")
                self.logger.debug(
                    f"[DATA] Retrieved {len(df)} bars for {symbol} {timeframe}"
                )

                # If we still don't have enough data, try extended historical request
                if len(df) < 30:  # Need minimum for MACD + buffer
                    self.logger.warning(
                        f"[DATA] Only {len(df)} bars for {symbol}, attempting extended historical request"
                    )
                    return self._get_extended_historical_data(symbol, timeframe)
            else:
                self.logger.warning(f"[DATA] No bars returned for {symbol}")

            return df

        except Exception as e:
            self.logger.error(f"[ERROR] Failed to get bars for {symbol}: {e}")
            return pd.DataFrame()

    def _get_extended_historical_data(self, symbol, timeframe):
        """Get extended historical data when initial request is insufficient"""
        try:
            # Go back further in time for extended data
            end_time = datetime.now()
            if timeframe == "15Min":
                start_time = end_time - timedelta(days=30)  # 30 days back
                limit = 500
            else:
                start_time = end_time - timedelta(days=14)
                limit = 400

            start_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

            self.logger.info(
                f"[EXTENDED] Requesting extended {symbol} data from {start_str} (limit: {limit})"
            )

            bars = self.api.get_bars(
                symbol, timeframe, start=start_str, end=end_str, limit=limit
            )

            df = pd.DataFrame(
                [
                    {
                        "timestamp": bar.t,
                        "open": float(bar.o),
                        "high": float(bar.h),
                        "low": float(bar.l),
                        "close": float(bar.c),
                        "volume": int(bar.v),
                    }
                    for bar in bars
                ]
            )

            if not df.empty:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df = df.set_index("timestamp")
                self.logger.info(
                    f"[EXTENDED] Retrieved {len(df)} extended bars for {symbol}"
                )

            return df

        except Exception as e:
            self.logger.error(f"[ERROR] Extended data request failed for {symbol}: {e}")
            return pd.DataFrame()

    def get_market_status(self):
        """Check if market is open"""
        try:
            clock = self.api.get_clock()
            return {
                "is_open": clock.is_open,
                "next_open": clock.next_open,
                "next_close": clock.next_close,
            }
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to get market status: {e}")
            return {"is_open": False}

    def calculate_indicators(self, df):
        """Calculate technical indicators - Enhanced with industry best practices"""
        if df.empty or len(df) < 26:  # Increased minimum for MACD
            return df

        try:
            # Simple Moving Averages
            df["sma_10"] = df["close"].rolling(window=10).mean()
            df["sma_20"] = df["close"].rolling(window=20).mean()

            # Exponential Moving Averages (Industry recommended)
            df["ema_9"] = df["close"].ewm(span=9, adjust=False).mean()
            df["ema_21"] = df["close"].ewm(span=21, adjust=False).mean()

            # RSI (14-period standard)
            delta = df["close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df["rsi"] = 100 - (100 / (1 + rs))

            # MACD (12, 26, 9) - Industry standard
            ema_12 = df["close"].ewm(span=12, adjust=False).mean()
            ema_26 = df["close"].ewm(span=26, adjust=False).mean()
            df["macd"] = ema_12 - ema_26
            df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
            df["macd_histogram"] = df["macd"] - df["macd_signal"]

            # VWAP (Volume Weighted Average Price)
            df["vwap"] = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()

            # Bollinger Bands (20-period, 2 std dev)
            df["bb_middle"] = df["close"].rolling(window=20).mean()
            bb_std = df["close"].rolling(window=20).std()
            df["bb_upper"] = df["bb_middle"] + (bb_std * 2)
            df["bb_lower"] = df["bb_middle"] - (bb_std * 2)
            df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]

            # Volume Analysis
            df["volume_sma"] = df["volume"].rolling(window=20).mean()
            df["volume_ratio"] = df["volume"] / df["volume_sma"]

            # Price Analysis
            df["price_change"] = df["close"].pct_change()
            df["price_vs_vwap"] = (df["close"] - df["vwap"]) / df["vwap"]

            # Trend Signals
            df["ema_cross_bullish"] = (df["ema_9"] > df["ema_21"]) & (
                df["ema_9"].shift(1) <= df["ema_21"].shift(1)
            )
            df["ema_cross_bearish"] = (df["ema_9"] < df["ema_21"]) & (
                df["ema_9"].shift(1) >= df["ema_21"].shift(1)
            )
            df["macd_cross_bullish"] = (df["macd"] > df["macd_signal"]) & (
                df["macd"].shift(1) <= df["macd_signal"].shift(1)
            )
            df["macd_cross_bearish"] = (df["macd"] < df["macd_signal"]) & (
                df["macd"].shift(1) >= df["macd_signal"].shift(1)
            )

            return df

        except Exception as e:
            self.logger.error(f"[ERROR] Failed to calculate indicators: {e}")
            return df
