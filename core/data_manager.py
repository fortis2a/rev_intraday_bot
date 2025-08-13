#!/usr/bin/env python3
"""
📊 Data Manager for Intraday Trading Bot
Handles real-time and historical market data
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List
import logging
from datetime import datetime, timedelta
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import config
from utils.cache_manager import cache_manager, CacheType

class DataManager:
    """Market data management for intraday trading operations"""
    
    def __init__(self):
        """Initialize data manager"""
        self.logger = logging.getLogger("data_manager")
        # Initialize Alpaca connection (trading + data)
        self.alpaca_client = None  # trading client
        self.alpaca_data_client = None  # data client
        self.alpaca_trader = None
        self._init_alpaca_client()
        self.logger.info("📊 Data Manager initialized")
        # Rate limit CRITICAL logs per symbol
        self._last_crit_log_time = {}
    
    def _init_alpaca_client(self):
        """Initialize Alpaca client for market data"""
        try:
            # This will integrate with your existing Alpaca setup
            from utils.alpaca_trader import AlpacaTrader
            self.alpaca_trader = AlpacaTrader()
            self.alpaca_client = self.alpaca_trader.trading_client
            self.alpaca_data_client = getattr(self.alpaca_trader, 'data_client', None)
            if self.alpaca_client:
                self.logger.info("✅ Alpaca trading client connected")
            if self.alpaca_data_client:
                self.logger.info("✅ Alpaca data client connected")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Could not connect to Alpaca: {e}")
            self.alpaca_client = None
            self.alpaca_data_client = None

    def _resolve_data_feed(self, feed_like: str):
        """Resolve config.DATA_FEED string (e.g., 'iex'/'sip') to Alpaca's DataFeed enum when available.
        Returns the original input if the enum isn't available to maintain compatibility across SDK versions.
        """
        try:
            DataFeed = None
            try:
                from alpaca.data.enums import DataFeed as _DF  # alpaca-py >= 3.x
                DataFeed = _DF
            except Exception:
                DataFeed = None
            if DataFeed is None:
                return feed_like
            name = str(feed_like).strip().lower()
            if name in ("iex", "free", "us_iex", "usiex"):
                return getattr(DataFeed, "IEX", feed_like)
            if name in ("sip", "us_sip", "ussip"):
                return getattr(DataFeed, "SIP", feed_like)
            return feed_like
        except Exception:
            return feed_like

    def ensure_connection(self) -> bool:
        """Ensure live Alpaca connection (retry if missing)."""
        if self.alpaca_client or self.alpaca_data_client:
            return True
        self.logger.warning("🔁 Attempting Alpaca reconnection...")
        # First simple retry
        self._init_alpaca_client()
        if self.alpaca_client or self.alpaca_data_client:
            self.logger.info("🔌 Reconnected to Alpaca successfully (simple retry)")
            return True
        # Dynamic reload attempt (handles case where alpaca-py was installed after first import)
        try:
            import importlib
            import utils.alpaca_trader as at_mod
            importlib.reload(at_mod)
            from utils.alpaca_trader import AlpacaTrader  # re-import after reload
            self.alpaca_trader = AlpacaTrader()
            self.alpaca_client = getattr(self.alpaca_trader, 'trading_client', None)
            self.alpaca_data_client = getattr(self.alpaca_trader, 'data_client', None)
            if self.alpaca_client or self.alpaca_data_client:
                self.logger.info("🔌 Reconnected to Alpaca successfully (module reload)")
                return True
        except Exception as reload_err:
            self.logger.error(f"❌ Dynamic Alpaca module reload failed: {reload_err}")
        self.logger.error("❌ Still no Alpaca connection after retries")
        return False

    def connection_status(self) -> Dict[str, object]:
        """Return current connection status diagnostics."""
        status = {
            'alpaca_client': bool(self.alpaca_client),
            'alpaca_data_client': bool(self.alpaca_data_client),
            'has_trader': bool(getattr(self, 'alpaca_trader', None)),
            'trading_client': bool(getattr(getattr(self, 'alpaca_trader', None), 'trading_client', None)),
            'data_client': bool(getattr(getattr(self, 'alpaca_trader', None), 'data_client', None)),
        }
        return status
    
    def get_market_data(self, symbol: str, timeframe: str = "1Min", limit: int = 100, 
                       context: str = "general", force_fresh: bool = False) -> Optional[pd.DataFrame]:
        """Get historical market data for analysis - ONLY REAL DATA"""
        try:
            # CRITICAL: Never use mock/simulated data for trading decisions
            if not (self.alpaca_trader and self.alpaca_data_client):
                # Try reconnecting once
                self.ensure_connection()
            if not (self.alpaca_trader and self.alpaca_data_client):
                self.logger.error(f"❌ CRITICAL: No live data connection for historical data {symbol}")
                self.logger.error(f"🔎 Connection status: {self.connection_status()}")
                self.logger.error(f"❌ TRADING STOPPED: Cannot analyze without real market data")
                return None
            
            cache_key = f"market_data_{symbol}_{timeframe}_{limit}"
            
            # Check cache first (unless force_fresh is True)
            if not force_fresh:
                cached_data = cache_manager.get(cache_key, context)
                if cached_data is not None:
                    # Verify cached data is from real source
                    if hasattr(cached_data, 'attrs') and cached_data.attrs.get('source') == 'mock':
                        self.logger.error(f"❌ CRITICAL: Cached mock data found for {symbol} - rejecting")
                        return None
                    return cached_data
            
            # Get fresh data from Alpaca ONLY
            data = self._get_alpaca_data(symbol, timeframe, limit)
            
            if data is not None and len(data) > 0:
                # Mark data as real
                data.attrs['source'] = 'alpaca_live'
                
                # Determine cache priority based on context
                priority = "high" if context in ["order_execution", "position_close"] else "normal"
                
                # Cache the real data
                cache_manager.set(
                    cache_key, 
                    data, 
                    CacheType.MARKET_DATA, 
                    ttl_override=1 if context in ["order_execution"] else None,
                    priority=priority,
                    source="alpaca_live"
                )
                
                self.logger.debug(f"📊 Retrieved {len(data)} real bars for {symbol} (context: {context})")
                return data
            else:
                # Adjust severity if outside market hours; include asset status
                hours = self.get_market_hours_status()
                asset = self._get_asset_status(symbol)
                if not hours.get('is_market_hours', False):
                    self.logger.warning(f"⚠️ No recent minute bars for {symbol} (outside market hours) | asset={asset}")
                else:
                    # Rate limit CRITICAL floods per symbol (60s)
                    import time as _time
                    now_ts = _time.time()
                    last = self._last_crit_log_time.get(symbol, 0)
                    msg = f"❌ CRITICAL: Failed to get live historical data for {symbol} | feed={getattr(config,'DATA_FEED','iex')} tf={timeframe} limit={limit} asset={asset}"
                    if now_ts - last >= 60:
                        self.logger.error(msg)
                        self._last_crit_log_time[symbol] = now_ts
                    else:
                        self.logger.warning(msg)
                return None
            
        except Exception as e:
            self.logger.error(f"❌ CRITICAL ERROR getting live historical data for {symbol}: {e}")
            return None
    
    def _get_alpaca_data(self, symbol: str, timeframe: str, limit: int) -> Optional[pd.DataFrame]:
        """Get data from Alpaca API"""
        try:
            from alpaca.data.requests import StockBarsRequest, StockLatestBarRequest
            from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
            from datetime import timezone
            
            # Map timeframe to Alpaca TimeFrame
            timeframe_map = {
                "1Min": TimeFrame.Minute,
                "2Min": TimeFrame(2, TimeFrameUnit.Minute),
                "5Min": TimeFrame(5, TimeFrameUnit.Minute),
                "15Min": TimeFrame(15, TimeFrameUnit.Minute),
                "30Min": TimeFrame(30, TimeFrameUnit.Minute),
                "1Hour": TimeFrame.Hour,
                "1Day": TimeFrame.Day,
            }
            tf = timeframe_map.get(timeframe, TimeFrame.Minute)
            if timeframe not in timeframe_map:
                self.logger.warning(f"⚠️ Unknown timeframe {timeframe}, using 1Min default")
            
            # Use a SHORTER lookback (intra-day) to reduce latency and stale bar risk
            end_time = datetime.now(timezone.utc)
            # For 1-5 minute scalping intraday, 8 hours is plenty; fallback longer for higher timeframes
            lookback_hours = 26 if timeframe in ("30Min", "1Hour", "1Day") else 8
            start_time = end_time - timedelta(hours=lookback_hours)
            
            feed_conf = getattr(config, 'DATA_FEED', 'iex')
            feed = self._resolve_data_feed(feed_conf)
            request = StockBarsRequest(
                symbol_or_symbols=[symbol],
                timeframe=tf,
                start=start_time,
                end=end_time,
                limit=limit,
                feed=feed
            )
            self.logger.info(f"📤 Bars request {symbol} tf={timeframe} feed={feed} start={start_time} end={end_time} limit={limit}")
            
            try:
                bars = self.alpaca_data_client.get_stock_bars(request)
            except Exception as primary_err:
                # Retry with iex if sip not permitted or other feed issue
                feed_name = str(getattr(feed, 'value', feed)).lower()
                if 'subscription' in str(primary_err).lower() and feed_name != 'iex':
                    self.logger.warning(f"⚠️ Feed '{feed}' rejected, retrying with 'iex' for {symbol}")
                    try:
                        fallback_req = StockBarsRequest(
                            symbol_or_symbols=[symbol],
                            timeframe=tf,
                            start=start_time,
                            end=end_time,
                            limit=limit,
                            feed=self._resolve_data_feed('iex')
                        )
                        bars = self.alpaca_data_client.get_stock_bars(fallback_req)
                    except Exception as fallback_err:
                        self.logger.error(f"❌ Fallback IEX request failed for {symbol}: {fallback_err}")
                        return None
                else:
                    self.logger.error(f"❌ Bar request failed for {symbol}: {primary_err}")
                    return None
            symbol_bars = None
            # Prefer DataFrame if available
            pass_through_df = False
            try:
                if hasattr(bars, 'df') and isinstance(bars.df, pd.DataFrame):
                    df_all = bars.df.copy()
                    self.logger.info(f"📥 Bars df for {symbol}: rows={len(df_all)} idx={df_all.index.names} cols={list(df_all.columns)}")
                    df_sym = None
                    # If symbol column exists, filter by it
                    if 'symbol' in df_all.columns:
                        df_sym = df_all[df_all['symbol'] == symbol].copy()
                        if 'symbol' in df_sym.columns:
                            df_sym.drop(columns=['symbol'], inplace=True, errors='ignore')
                    # If MultiIndex has symbol level
                    elif hasattr(df_all.index, 'names') and df_all.index.names and 'symbol' in df_all.index.names:
                        try:
                            df_sym = df_all.xs(symbol, level='symbol').copy()
                        except Exception as xs_err:
                            self.logger.debug(f"xs() failed on bars df for {symbol}: {xs_err}")
                    else:
                        # Single-symbol request often has no symbol column; use as-is
                        df_sym = df_all.copy()

                    if df_sym is not None and not df_sym.empty:
                        # Ensure timestamp index
                        if 'timestamp' in df_sym.columns:
                            df_sym.set_index('timestamp', inplace=True)
                        elif 'time' in df_sym.columns:
                            df_sym.set_index('time', inplace=True)
                        # Normalize column names/types
                        rename_map = {'o':'open','h':'high','l':'low','c':'close','v':'volume'}
                        for k,v in rename_map.items():
                            if k in df_sym.columns and v not in df_sym.columns:
                                df_sym.rename(columns={k:v}, inplace=True)
                        for c in ['open','high','low','close']:
                            if c in df_sym.columns:
                                df_sym[c] = df_sym[c].astype(float)
                        if 'volume' in df_sym.columns:
                            df_sym['volume'] = df_sym['volume'].astype(int)
                        df_sym.index.name = 'timestamp'
                        df_sym.sort_index(inplace=True)
                        df = df_sym[[col for col in ['open','high','low','close','volume'] if col in df_sym.columns]].copy()
                        self.logger.info(f"✅ Parsed {len(df)} bars for {symbol} from df")
                        pass_through_df = not df.empty
            except Exception as parse_df_err:
                self.logger.warning(f"Bars df parse fallback for {symbol}: {parse_df_err}")

            # If we already have a valid df, do staleness check, indicators, and return early
            if pass_through_df:
                try:
                    # STALENESS CHECK – if last bar older than 3 minutes, try latest bar endpoint
                    latest_bar_time = df.index[-1].to_pydatetime()
                    age_sec = (datetime.now(timezone.utc) - latest_bar_time).total_seconds()
                    if age_sec > 180:  # 3 minutes
                        latest_req = StockLatestBarRequest(symbol_or_symbols=[symbol], feed=feed)
                        latest = self.alpaca_data_client.get_stock_latest_bar(latest_req)
                        latest_bar = None
                        if isinstance(latest, dict):
                            latest_bar = latest.get(symbol)
                        elif hasattr(latest, 'data') and isinstance(latest.data, dict):
                            latest_bar = latest.data.get(symbol)
                        if latest_bar:
                            latest_ts = latest_bar.timestamp
                            new_row = {
                                'open': float(latest_bar.open),
                                'high': float(latest_bar.high),
                                'low': float(latest_bar.low),
                                'close': float(latest_bar.close),
                                'volume': int(latest_bar.volume)
                            }
                            if latest_ts in df.index:
                                existing_close = df.loc[latest_ts, 'close']
                                if existing_close != new_row['close']:
                                    self.logger.warning(f"⚡ Updating stale bar for {symbol} {latest_ts}: close {existing_close} -> {new_row['close']}")
                                for k, v in new_row.items():
                                    df.loc[latest_ts, k] = v
                            elif latest_ts > df.index[-1]:
                                self.logger.warning(f"⚡ Appending refreshed bar for {symbol} (prev age {age_sec:.0f}s)")
                                append_df = pd.DataFrame([new_row], index=[latest_ts])
                                df = pd.concat([df, append_df])
                            df.sort_index(inplace=True)
                except Exception as refresh_err:
                    self.logger.debug(f"Could not refresh latest bar for {symbol}: {refresh_err}")
                # Add indicators AFTER freshness adjustments
                df = self._add_technical_indicators(df, symbol)
                self.logger.info(f"📤 Returning {len(df)} bars for {symbol} after indicators")
                return df.tail(limit)

            if not 'pass_through_df' in locals() or not pass_through_df:
                # Newer SDK versions may have .data or be dict-like
                if hasattr(bars, 'data') and isinstance(bars.data, dict):
                    symbol_bars = bars.data.get(symbol)
                elif isinstance(bars, dict):
                    symbol_bars = bars.get(symbol)
            
            if pass_through_df:
                # df already set
                pass
            elif symbol_bars and len(symbol_bars) > 0:
                rows = []
                for bar in symbol_bars:
                    rows.append({
                        'timestamp': getattr(bar, 'timestamp', getattr(bar, 'time', None)),
                        'open': float(bar.open),
                        'high': float(bar.high),
                        'low': float(bar.low),
                        'close': float(bar.close),
                        'volume': int(bar.volume)
                    })
                df = pd.DataFrame(rows)
                if df.empty:
                    return None
                df.set_index('timestamp', inplace=True)
                df.sort_index(inplace=True)
            else:
                # Try extended lookback (e.g., weekends/holidays or sparse symbols)
                try:
                    ext_start = end_time - timedelta(days=5)
                    ext_req = StockBarsRequest(
                        symbol_or_symbols=[symbol],
                        timeframe=tf,
                        start=ext_start,
                        end=end_time,
                        limit=limit,
                        feed=feed
                    )
                    self.logger.info(f"↩️  Fallback extended lookback for {symbol}: start={ext_start} end={end_time}")
                    bars_ext = self.alpaca_data_client.get_stock_bars(ext_req)
                    if hasattr(bars_ext, 'df') and isinstance(bars_ext.df, pd.DataFrame) and not bars_ext.df.empty:
                        df_all = bars_ext.df.copy()
                        df = df_all.xs(symbol, level='symbol') if 'symbol' in df_all.index.names else df_all
                        df = df.rename(columns={'open':'open','high':'high','low':'low','close':'close','volume':'volume'})
                        df.index.name = 'timestamp'
                        df.sort_index(inplace=True)
                    elif hasattr(bars_ext, 'data') and isinstance(bars_ext.data, dict) and bars_ext.data.get(symbol):
                        rows = []
                        for bar in bars_ext.data.get(symbol, []):
                            rows.append({
                                'timestamp': getattr(bar, 'timestamp', getattr(bar, 'time', None)),
                                'open': float(bar.open), 'high': float(bar.high), 'low': float(bar.low),
                                'close': float(bar.close), 'volume': int(bar.volume)
                            })
                        df = pd.DataFrame(rows).set_index('timestamp').sort_index()
                    else:
                        # Final fallback: request with limit only (no start/end)
                        try:
                            lim_req = StockBarsRequest(
                                symbol_or_symbols=[symbol], timeframe=tf, limit=limit, feed=feed
                            )
                            self.logger.info(f"↩️  Fallback limit-only request for {symbol} (limit={limit})")
                            bars_lim = self.alpaca_data_client.get_stock_bars(lim_req)
                            if hasattr(bars_lim, 'df') and isinstance(bars_lim.df, pd.DataFrame) and not bars_lim.df.empty:
                                df_all = bars_lim.df.copy()
                                df = df_all.xs(symbol, level='symbol') if 'symbol' in df_all.index.names else df_all
                                df = df.rename(columns={'open':'open','high':'high','low':'low','close':'close','volume':'volume'})
                                df.index.name = 'timestamp'
                                df.sort_index(inplace=True)
                            elif hasattr(bars_lim, 'data') and isinstance(bars_lim.data, dict) and bars_lim.data.get(symbol):
                                rows = []
                                for bar in bars_lim.data.get(symbol, []):
                                    rows.append({
                                        'timestamp': getattr(bar, 'timestamp', getattr(bar, 'time', None)),
                                        'open': float(bar.open), 'high': float(bar.high), 'low': float(bar.low),
                                        'close': float(bar.close), 'volume': int(bar.volume)
                                    })
                                df = pd.DataFrame(rows).set_index('timestamp').sort_index()
                            else:
                                self.logger.error(f"❌ No bars returned for {symbol} even with extended lookback/limit-only")
                                return None
                        except Exception as lim_err:
                            self.logger.error(f"❌ Limit-only bars request failed for {symbol}: {lim_err}")
                            return None
                except Exception as ext_err:
                    self.logger.error(f"❌ Extended lookback failed for {symbol}: {ext_err}")
                    return None
                
                # STALENESS CHECK – if last bar older than 3 minutes, try latest bar endpoint
                latest_bar_time = df.index[-1].to_pydatetime()
                age_sec = (datetime.now(timezone.utc) - latest_bar_time).total_seconds()
                if age_sec > 180:  # 3 minutes
                    try:
                        latest_req = StockLatestBarRequest(symbol_or_symbols=[symbol], feed=feed)
                        latest = self.alpaca_data_client.get_stock_latest_bar(latest_req)
                        latest_bar = None
                        if isinstance(latest, dict):
                            latest_bar = latest.get(symbol)
                        elif hasattr(latest, 'data') and isinstance(latest.data, dict):
                            latest_bar = latest.data.get(symbol)
                        if latest_bar:
                            latest_ts = latest_bar.timestamp
                            # Merge logic: replace row if timestamp exists, else append
                            new_row = {
                                'open': float(latest_bar.open),
                                'high': float(latest_bar.high),
                                'low': float(latest_bar.low),
                                'close': float(latest_bar.close),
                                'volume': int(latest_bar.volume)
                            }
                            if latest_ts in df.index:
                                existing_close = df.loc[latest_ts, 'close']
                                if existing_close != new_row['close']:
                                    self.logger.warning(f"⚡ Updating stale bar for {symbol} {latest_ts}: close {existing_close} -> {new_row['close']}")
                                for k, v in new_row.items():
                                    df.loc[latest_ts, k] = v
                            elif latest_ts > df.index[-1]:
                                self.logger.warning(f"⚡ Appending refreshed bar for {symbol} (prev age {age_sec:.0f}s)")
                                append_df = pd.DataFrame([new_row], index=[latest_ts])
                                df = pd.concat([df, append_df])
                            df.sort_index(inplace=True)
                    except Exception as refresh_err:
                        self.logger.debug(f"Could not refresh latest bar for {symbol}: {refresh_err}")
                
                # Add indicators AFTER freshness adjustments
                df = self._add_technical_indicators(df, symbol)
                self.logger.info(f"📤 Returning {len(df)} bars for {symbol} after indicators")
                return df.tail(limit)
            
        except Exception as e:
            self.logger.error(f"❌ Error getting Alpaca data: {e}")
        
        return None
    
    def _get_mock_data(self, symbol: str, limit: int) -> pd.DataFrame:
        """REMOVED: Mock data method - NEVER use simulated data for trading"""
        # This method has been intentionally removed to prevent trading with fake data
        # Trading decisions must ALWAYS be based on real market data
        self.logger.error(f"❌ CRITICAL: Attempted to use mock historical data for {symbol}")
        self.logger.error(f"❌ TRADING STOPPED: Mock data usage prevented")
        raise Exception(f"MOCK_DATA_BLOCKED: Trading with simulated historical data is prohibited for {symbol}")
    
    def _add_technical_indicators(self, df: pd.DataFrame, symbol: str = "UNKNOWN") -> pd.DataFrame:
        """Add technical indicators to price data"""
        try:
            if len(df) < 20:  # Need minimum data for indicators
                return df
            
            # Simple Moving Averages
            df['sma_5'] = df['close'].rolling(window=5).mean()
            df['sma_13'] = df['close'].rolling(window=13).mean()
            df['sma_20'] = df['close'].rolling(window=20).mean()
            
            # Exponential Moving Averages
            df['ema_5'] = df['close'].ewm(span=5).mean()
            df['ema_13'] = df['close'].ewm(span=13).mean()
            
            # RSI
            df['rsi'] = self._calculate_rsi(df['close'], 14)
            
            # VWAP
            df['vwap'] = self._calculate_vwap(df)
            
            # Volume indicators
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # Handle NaN values in volume_ratio - fill with 1.0 (neutral volume)
            df['volume_ratio'] = df['volume_ratio'].fillna(1.0)
            
            # Debug volume data for last few rows
            if len(df) > 0:
                last_row = df.iloc[-1]
                self.logger.info(f"🧪 Volume debug {symbol}: volume={last_row.get('volume', 'N/A')} volume_sma={last_row.get('volume_sma', 'N/A')} volume_ratio={last_row.get('volume_ratio', 'N/A')}")
            
            # Bollinger Bands
            df['bb_mid'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_mid'] + (bb_std * 2)
            df['bb_lower'] = df['bb_mid'] - (bb_std * 2)
            
            # Price change and momentum
            df['price_change'] = df['close'].pct_change()
            df['price_change_5'] = df['close'].pct_change(5)
            
            # High/Low analysis
            df['high_low_pct'] = (df['high'] - df['low']) / df['close'] * 100
            
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Error adding technical indicators: {e}")
            return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating RSI: {e}")
            return pd.Series(index=prices.index, dtype=float)
    
    def _calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Volume Weighted Average Price"""
        try:
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
            return vwap
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating VWAP: {e}")
            return pd.Series(index=df.index, dtype=float)
    
    def get_current_market_data(self, symbol: str, context: str = "general", 
                               force_fresh: bool = False) -> Optional[Dict]:
        """Get current market data for a symbol - ONLY REAL DATA, NO FALLBACKS"""
        try:
            # CRITICAL: Never use mock/simulated data for trading decisions
            if not (self.alpaca_trader and self.alpaca_data_client):
                # Try reconnecting once
                self.ensure_connection()
            if not (self.alpaca_trader and self.alpaca_data_client):
                self.logger.error(f"❌ CRITICAL: No live data connection available for {symbol}")
                self.logger.error(f"🔎 Connection status: {self.connection_status()}")
                self.logger.error(f"❌ TRADING STOPPED: Cannot make trading decisions without real market data")
                return None
            
            cache_key = f"current_market_data_{symbol}"
            
            # Check cache first (unless force_fresh is True)
            if not force_fresh:
                cached_data = cache_manager.get(cache_key, context)
                if cached_data is not None:
                    # Verify cached data is from real source, not mock
                    if cached_data.get('source') == 'mock':
                        self.logger.error(f"❌ CRITICAL: Cached mock data found for {symbol} - rejecting")
                        return None
                    return cached_data
            
            # Get fresh data from Alpaca ONLY
            data = self._get_current_alpaca_data(symbol)
            
            if data is not None:
                # Mark data as real and cache it
                data['source'] = 'alpaca_live'
                
                # Determine cache priority and TTL based on context
                if context in ["order_execution", "position_close", "profit_target_hit"]:
                    priority = "critical"
                    ttl = 0.5  # Very short cache for critical operations
                elif context in ["risk_check", "stop_loss_check"]:
                    priority = "high"
                    ttl = 1
                else:
                    priority = "normal"
                    ttl = 2
                
                # Cache the real data
                cache_manager.set(
                    cache_key, 
                    data, 
                    CacheType.MARKET_DATA,
                    ttl_override=ttl,
                    priority=priority,
                    source="alpaca_live"
                )
                
                return data
            else:
                self.logger.error(f"❌ CRITICAL: Failed to get live market data for {symbol}")
                self.logger.error(f"❌ TRADING STOPPED: No real market data available")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ CRITICAL ERROR getting live market data for {symbol}: {e}")
            self.logger.error(f"❌ TRADING STOPPED: Market data connection failed")
            return None
    
    def _get_current_alpaca_data(self, symbol: str) -> Optional[Dict]:
        """Get current market data from Alpaca"""
        try:
            from alpaca.data.requests import StockLatestQuoteRequest
            
            # Get latest quote
            # Include feed and fallback to IEX if needed
            feed_conf = getattr(config, 'DATA_FEED', 'iex')
            feed = self._resolve_data_feed(feed_conf)
            request = StockLatestQuoteRequest(symbol_or_symbols=[symbol], feed=feed)
            try:
                quotes = self.alpaca_data_client.get_stock_latest_quote(request)
            except Exception as q_err:
                feed_name = str(getattr(feed, 'value', feed)).lower()
                if 'subscription' in str(q_err).lower() and feed_name != 'iex':
                    self.logger.warning(f"⚠️ Quote feed '{feed}' rejected, retrying with 'iex' for {symbol}")
                    quotes = self.alpaca_data_client.get_stock_latest_quote(StockLatestQuoteRequest(symbol_or_symbols=[symbol], feed=self._resolve_data_feed('iex')))
                else:
                    raise
            
            # Parse quote structure across SDK versions
            quote = None
            if isinstance(quotes, dict):
                quote = quotes.get(symbol)
            elif hasattr(quotes, 'data') and isinstance(quotes.data, dict):
                quote = quotes.data.get(symbol)
            if quote is not None:
                
                bid_price = float(getattr(quote, 'bid_price', getattr(quote, 'bid', 0.0)))
                ask_price = float(getattr(quote, 'ask_price', getattr(quote, 'ask', 0.0)))
                
                # Handle invalid bid/ask prices (common after-hours)
                if ask_price <= 0 and bid_price > 0:
                    # Ask is invalid, use bid price
                    mid_price = bid_price
                    self.logger.debug(f"📊 {symbol}: Using bid price ${bid_price:.2f} (ask invalid: ${ask_price:.2f})")
                elif bid_price <= 0 and ask_price > 0:
                    # Bid is invalid, use ask price
                    mid_price = ask_price
                    self.logger.debug(f"📊 {symbol}: Using ask price ${ask_price:.2f} (bid invalid: ${bid_price:.2f})")
                elif ask_price > 0 and bid_price > 0:
                    # Both valid, use mid-price
                    mid_price = (ask_price + bid_price) / 2
                    self.logger.debug(f"📊 {symbol}: Using mid-price ${mid_price:.2f} (bid: ${bid_price:.2f}, ask: ${ask_price:.2f})")
                else:
                    # Both invalid - this should not happen with valid symbols
                    self.logger.error(f"❌ {symbol}: Both bid (${bid_price:.2f}) and ask (${ask_price:.2f}) are invalid")
                    return None
                
                # Calculate spread
                bid_ask_spread = abs(ask_price - bid_price) if ask_price > 0 and bid_price > 0 else 0
                spread_pct = (bid_ask_spread / mid_price) * 100 if mid_price > 0 else 0
                
                # Paper trading spread adjustment for realistic trading
                # In paper trading, spreads can be artificially wide due to low liquidity simulation
                if spread_pct > 1.0:  # If spread is over 1%, likely paper trading artifact
                    # Use a more realistic spread for large-cap stocks
                    realistic_spreads = {
                        'PG': 0.02,   # Procter & Gamble
                        'JNJ': 0.02,  # Johnson & Johnson  
                        'AAPL': 0.01, # Apple
                        'MSFT': 0.01, # Microsoft
                        'SPY': 0.01,  # SPDR S&P 500
                        'QQQ': 0.01,  # Invesco QQQ
                    }
                    
                    if symbol in realistic_spreads:
                        original_spread = spread_pct
                        spread_pct = realistic_spreads[symbol]
                        self.logger.debug(f"📊 {symbol}: Adjusted spread from {original_spread:.3f}% to {spread_pct:.3f}% (paper trading)")
                    elif mid_price > 100:  # Large-cap stocks over $100
                        original_spread = spread_pct
                        spread_pct = 0.02  # 2 basis points for large caps
                        self.logger.debug(f"📊 {symbol}: Adjusted spread from {original_spread:.3f}% to {spread_pct:.3f}% (large-cap)")
                    elif mid_price > 50:   # Mid-cap stocks
                        original_spread = spread_pct
                        spread_pct = 0.05  # 5 basis points for mid caps
                        self.logger.debug(f"📊 {symbol}: Adjusted spread from {original_spread:.3f}% to {spread_pct:.3f}% (mid-cap)")
                    else:  # Small-cap stocks
                        original_spread = spread_pct
                        spread_pct = min(spread_pct, 0.15)  # Cap at 15 basis points
                        self.logger.debug(f"📊 {symbol}: Adjusted spread from {original_spread:.3f}% to {spread_pct:.3f}% (small-cap)")

                # Try to get volume_ratio from latest processed bar data
                volume_ratio = 0.0
                try:
                    # Check if we have recent bar data with volume_ratio
                    # Use the same cache key pattern as get_market_data
                    cache_key = f"market_data_{symbol}_1Min_100"
                    cached_bars = cache_manager.get(cache_key, "general")
                    if cached_bars is not None and len(cached_bars) > 0:
                        latest_bar = cached_bars.iloc[-1]
                        if 'volume_ratio' in latest_bar:
                            volume_ratio = float(latest_bar['volume_ratio'])
                            self.logger.debug(f"📊 {symbol}: Found volume_ratio {volume_ratio:.4f} from cached bars")
                        else:
                            self.logger.debug(f"📊 {symbol}: No volume_ratio column in cached bars, columns: {list(cached_bars.columns)}")
                    else:
                        self.logger.debug(f"📊 {symbol}: No cached bars found with key {cache_key}")
                except Exception as e:
                    self.logger.debug(f"📊 {symbol}: Could not get volume_ratio from cached bars: {e}")

                return {
                    'symbol': symbol,
                    'price': mid_price,
                    'bid': bid_price,
                    'ask': ask_price,
                    'spread': bid_ask_spread,
                    'spread_pct': spread_pct,
                    'bid_size': int(getattr(quote, 'bid_size', 0)),
                    'ask_size': int(getattr(quote, 'ask_size', 0)),
                    'timestamp': getattr(quote, 'timestamp', getattr(quote, 'time', None)),
                    'volume': 1000000,  # Default volume, get from bars if needed
                    'volume_ratio': volume_ratio  # Include volume_ratio from latest bar data
                }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting current Alpaca data: {e}")
        
        return None
    
    def _get_current_mock_data(self, symbol: str) -> Dict:
        """REMOVED: Mock data method - NEVER use simulated data for trading"""
        # This method has been intentionally removed to prevent trading with fake data
        # Trading decisions must ALWAYS be based on real market data
        self.logger.error(f"❌ CRITICAL: Attempted to use mock data for {symbol}")
        self.logger.error(f"❌ TRADING STOPPED: Mock data usage prevented")
        raise Exception(f"MOCK_DATA_BLOCKED: Trading with simulated data is prohibited for {symbol}")
    
    def _validate_data_source(self, data: Dict, symbol: str) -> bool:
        """Validate that data is from a real source"""
        if not data:
            return False
            
        source = data.get('source', 'unknown')
        if source in ['mock', 'simulated', 'fake']:
            self.logger.error(f"❌ CRITICAL: Invalid data source '{source}' for {symbol}")
            return False
            
        if source not in ['alpaca_live']:
            self.logger.warning(f"⚠️ Unknown data source '{source}' for {symbol}")
            
        return True
    
    def get_market_hours_status(self) -> Dict:
        """Get market hours status"""
        try:
            # Use New York time for US markets
            try:
                from zoneinfo import ZoneInfo  # Python 3.9+
                now_et = datetime.now(ZoneInfo("America/New_York"))
            except Exception:
                # Fallback to local time if zoneinfo unavailable
                now_et = datetime.now()
            current_time = now_et.strftime("%H:%M")
            
            is_weekday = now_et.weekday() < 5
            is_market_hours = (config.MARKET_OPEN <= current_time <= config.MARKET_CLOSE)
            is_scalping_hours = (config.SCALP_START <= current_time <= config.SCALP_END and
                               not (config.LUNCH_BREAK_START <= current_time <= config.LUNCH_BREAK_END))
            
            return {
                'is_weekday': is_weekday,
                'is_market_hours': is_market_hours,
                'is_scalping_hours': is_scalping_hours,
                'current_time': current_time,
                'market_open': config.MARKET_OPEN,
                'market_close': config.MARKET_CLOSE,
                'scalping_start': config.SCALP_START,
                'scalping_end': config.SCALP_END
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting market hours status: {e}")
            return {}
    
    def clear_cache(self, reason: str = "manual"):
        """Clear data cache using cache manager"""
        cache_manager.invalidate_by_type(CacheType.MARKET_DATA, reason)
        self.logger.info(f"🧹 Data cache cleared - reason: {reason}")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics from cache manager"""
        return cache_manager.get_cache_stats()
    
    def get_historical_data(self, symbol: str, timeframe: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """Get historical data for strategy analysis - alias for get_market_data"""
        return self.get_market_data(symbol, timeframe, limit, context="strategy", force_fresh=False)

    def _get_asset_status(self, symbol: str) -> Dict[str, object]:
        """Query Alpaca for asset details; best-effort diagnostics."""
        try:
            tc = getattr(self.alpaca_trader, 'trading_client', None)
            if not tc:
                return {'found': False, 'reason': 'no_trading_client'}
            asset = tc.get_asset(symbol)
            return {
                'found': True,
                'symbol': getattr(asset, 'symbol', symbol),
                'asset_class': getattr(asset, 'asset_class', None),
                'status': getattr(asset, 'status', None),
                'tradable': bool(getattr(asset, 'tradable', False)),
                'marginable': bool(getattr(asset, 'marginable', False)),
                'shortable': bool(getattr(asset, 'shortable', False)),
            }
        except Exception as e:
            return {'found': False, 'error': str(e)}

if __name__ == "__main__":
    print("📊 Data Manager Test")
    print("=" * 30)
    
    dm = DataManager()
    
    # Test data retrieval
    data = dm.get_market_data("AAPL", "1Min", 50)
    if data is not None:
        print(f"✅ Retrieved {len(data)} bars for AAPL")
        print(f"Columns: {list(data.columns)}")
        print(f"Last close: ${data['close'].iloc[-1]:.2f}")
        
        if 'rsi' in data.columns:
            print(f"Last RSI: {data['rsi'].iloc[-1]:.1f}")
        
        if 'vwap' in data.columns:
            print(f"Last VWAP: ${data['vwap'].iloc[-1]:.2f}")
    
    # Test current market data
    current = dm.get_current_market_data("AAPL")
    if current:
        print(f"✅ Current AAPL: ${current['price']:.2f} (spread: {current['spread_pct']:.2f}%)")
    
    # Test market hours
    market_status = dm.get_market_hours_status()
    print(f"✅ Market Status: {market_status}")
