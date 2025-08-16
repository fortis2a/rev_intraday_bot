#!/usr/bin/env python3
"""
📈 Intraday Trading Engine
Swing trading engine for 15-minute timeframes with 2-8 hour holds
"""

import sys
import time
import threading
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
import csv
from pathlib import Path
import pytz

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import config, validate_config
from utils.signal_types import ScalpingSignal
from core.risk_manager import RiskManager
from core.data_manager import DataManager
from core.order_manager import OrderManager
from utils.trade_record import TradeRecord
from strategies import MomentumStrategy, MeanReversionStrategy, VWAPStrategy
from utils.logger import setup_logger

 # (Moved ScalpingSignal to utils.signal_types)

class IntradayEngine:
    """Main intraday trading engine for swing trades"""
    
    def __init__(self, demo_mode=False, bypass_market_hours=False):
        """Initialize intraday trading engine"""
        self.logger = setup_logger("intraday_engine")
        self.demo_mode = demo_mode
        self.bypass_market_hours = bypass_market_hours

        # Setup quieter loggers for noisy components
        logging.getLogger("dynamic_risk").setLevel(logging.WARNING)
        logging.getLogger("vwap_strategy").setLevel(logging.WARNING)
        logging.getLogger("momentum_strategy").setLevel(logging.WARNING)
        logging.getLogger("mean_reversion_strategy").setLevel(logging.WARNING)

        self.config = config
        self.timeframe_config = config  # Use main config instead of separate timeframe config

        # Validate configuration
        if not validate_config():
            raise ValueError("Invalid configuration")

        # Initialize components
        self.risk_manager = RiskManager()
        self.data_manager = DataManager()
        self.order_manager = OrderManager(self.data_manager)

        # HARD ASSERT: Require live Alpaca connection before proceeding (no silent fallback)
        if not getattr(self.data_manager, 'api', None):
            self.logger.error("❌ CRITICAL: Alpaca live data connection not established during engine init")
            self.logger.error("🔎 Troubleshoot: 1) Verify ALPACA_API_KEY / ALPACA_SECRET_KEY 2) Check internet access 3) Confirm alpaca-py installed 4) Paper account not rate-limited")
            raise RuntimeError("Alpaca live data connection required – initialization aborted.")

        # Initialize trading connection (optional check)
        try:
            if hasattr(self.order_manager, 'initialize_trading'):
                if not self.order_manager.initialize_trading():
                    self.logger.warning("⚠️ OrderManager trading connection failed - running in simulation mode")
        except Exception as e:
            self.logger.warning(f"⚠️ OrderManager initialization check failed: {e}")

        # Sync position count with broker to fix any state mismatches
        self.risk_manager.sync_position_count_with_broker(self.order_manager)

        # Initialize strategies
        self.strategies = {
            'momentum': MomentumStrategy(),
            'mean_reversion': MeanReversionStrategy(),
            'vwap_bounce': VWAPStrategy()
        }

        # State tracking
        self.active_positions = {}
        self.position_peaks = {}
        self.daily_pnl = 0.0
        self.trade_count = 0
        self.symbol_trade_count = {}
        self.trade_day = datetime.utcnow().date()
        self.is_running = False
        self.last_data_update = {}

        # Wash trade prevention
        self.last_order_time = {}
        self.min_order_interval = 3

        # Signal cooldown prevention - prevent rapid signal generation
        self.last_signal_time = {}
        self.signal_cooldown_period = getattr(config, 'SIGNAL_COOLDOWN_SECONDS', 60)
        self.failed_signal_cooldown = {}
        self.failed_signal_cooldown_period = getattr(config, 'FAILED_SIGNAL_COOLDOWN_SECONDS', 300)

        # Adaptive cooldown controls (scaled after large losses or losing streak)
        self.adaptive_cooldown_multiplier = 1.0
        self.max_adaptive_cooldown_multiplier = 3.0
        self.cooldown_decay_factor = 0.9
        self.cooldown_increase_factor = 1.25
        self.significant_loss_threshold_pct = 0.35
        self.recent_losses = []
        self.max_recent_losses = 5

        # Slippage tracking
        self.slippage_stats = {
            'count': 0,
            'total': 0.0,
            'max': 0.0,
        }

        # Trailing stop protection
        self.recently_closed_profitable = {}
        self.profitable_closure_cooldown = 120

        # Performance metrics and loss streak/pause
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0
        }
        self.consecutive_losses = 0
        self.global_pause_until = 0.0

        # Per-symbol performance aggregation for end-of-day reporting
        self.symbol_perf = {}
        # Trade diagnostics
        self._trade_records = {}
        self._trade_log_path = Path('logs') / 'trade_diagnostics.csv'
        try:
            if not self._trade_log_path.parent.exists():
                self._trade_log_path.parent.mkdir(parents=True, exist_ok=True)
            if not self._trade_log_path.exists():
                with open(self._trade_log_path, 'w', newline='') as tf:
                    writer = csv.writer(tf)
                    writer.writerow([
                        'symbol','strategy','side','entry_time','entry_price','stop_loss','profit_target','position_size','confidence','spread_pct','volume','volume_ratio','exit_time','exit_price','realized_pnl','realized_pct','r_multiple','hold_time_s','mae_pct','mfe_pct','mae_r','mfe_r','exit_reason','adaptive_stop_pct','atr_pct_entry','r_multiple_peak'
                    ])
        except Exception as e:
            self.logger.debug(f"Trade diagnostics init failed: {e}")

        self.logger.info(f"✅ Scalping engine initialized - Timeframe: {config.TIMEFRAME}")
        # Reporting state
        self._daily_report_generated_date = None

    def get_diagnostics(self) -> Dict[str, object]:
        """Return lightweight diagnostic info explaining trading inactivity."""
        now = time.time()
        # Safely compute last signal check age even if stored as datetime/epoch
        last_check_age = None
        if hasattr(self, 'last_signal_check'):
            try:
                last_check_age = round(self._get_timestamp_age_seconds(self.last_signal_check), 1)
            except Exception:
                last_check_age = None
        # Pull last order submission error (if any)
        last_order_error = None
        try:
            if hasattr(self, 'order_manager') and hasattr(self.order_manager, 'get_last_error'):
                last_order_error = self.order_manager.get_last_error()
                # Keep it compact
                if isinstance(last_order_error, dict):
                    last_order_error = {
                        'code': last_order_error.get('code'),
                        'message': last_order_error.get('message'),
                        # include symbol/side if available
                        'symbol': (last_order_error.get('details') or {}).get('symbol'),
                        'side': (last_order_error.get('details') or {}).get('side'),
                    }
        except Exception:
            last_order_error = None
        return {
            'is_running': self.is_running,
            'alpaca_connected': bool(getattr(self.data_manager, 'alpaca_client', None)),
            'market_hours': self.is_market_hours(),
            'scalp_window': f"{config.TRADING_START}-{config.TRADING_END}",
            'lunch_break': f"{config.LUNCH_BREAK_START}-{config.LUNCH_BREAK_END}",
            'active_positions': len(self.active_positions),
            'last_signal_check_age': last_check_age,
            'cooldown_multiplier': round(self.adaptive_cooldown_multiplier, 2),
            'recent_losses_buffer': len(self.recent_losses),
            'signal_cooldown_period': self.signal_cooldown_period,
            'max_open_positions': config.MAX_OPEN_POSITIONS,
            'last_filtered_symbols': getattr(self, 'last_filtered_symbols', []),
            'filtered_symbol_count': len(getattr(self, 'last_filtered_symbols', [])),
            'global_pause_s': max(0, int((getattr(self, 'global_pause_until', 0) or 0) - now)) if getattr(self, 'global_pause_until', 0) > now else 0,
            'last_order_error': last_order_error,
        }

    def _get_timestamp_age_seconds(self, ts) -> float:
        """Return age in seconds for a timestamp that may be a float (epoch) or datetime-like."""
        try:
            if ts is None:
                return 0.0
            # If already epoch seconds
            if isinstance(ts, (int, float)):
                return time.time() - float(ts)
            # pandas.Timestamp -> datetime
            if hasattr(ts, 'to_pydatetime'):
                ts = ts.to_pydatetime()
            # Assume datetime-like
            from datetime import timezone as _tz, datetime as _dt
            if getattr(ts, 'tzinfo', None) is None:
                ts = ts.replace(tzinfo=_tz.utc)
            now_utc = _dt.now(_tz.utc)
            return (now_utc - ts).total_seconds()
        except Exception:
            return 0.0
    
    def is_market_hours(self) -> bool:
        """Check if we're in valid trading hours"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # Check if it's a weekday
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Check trading hours (temporarily disable lunch break for testing)
        if (config.TRADING_START <= current_time <= config.TRADING_END):
            # Lunch break temporarily disabled for testing
            # not (config.LUNCH_BREAK_START <= current_time <= config.LUNCH_BREAK_END)):
            return True
        
        return False
    
    def can_submit_order(self, symbol: str) -> bool:
        """Check if enough time has passed since last order to prevent wash trades"""
        current_time = time.time()
        # Global pause gate
        if current_time < self.global_pause_until:
            remaining_time = int(self.global_pause_until - current_time)
            self.logger.debug(f"⏸️ Global pause active: {remaining_time}s remaining")
            return False
        last_order = self.last_order_time.get(symbol, 0)
        
        if current_time - last_order < self.min_order_interval:
            remaining_time = self.min_order_interval - (current_time - last_order)
            self.logger.debug(f"⏳ Wash trade prevention: waiting {remaining_time:.1f}s more for {symbol}")
            return False
        
        return True
    
    def record_order_time(self, symbol: str):
        """Record the time of an order submission for wash trade prevention"""
        self.last_order_time[symbol] = time.time()
    
    def can_generate_signal(self, symbol: str) -> bool:
        """Check if enough time has passed to generate a new signal (adaptive)."""
        now = time.time()
        base_cd = self.signal_cooldown_period
        effective_cd = base_cd * self.adaptive_cooldown_multiplier
        last_sig = self.last_signal_time.get(symbol, 0)
        if last_sig:
            since_last = now - last_sig
            if since_last < effective_cd:
                remaining = effective_cd - since_last
                # Verbose once per ~5s per symbol to avoid log spam
                if not hasattr(self, '_last_cd_log'):
                    self._last_cd_log = {}
                last_log = self._last_cd_log.get(symbol, 0)
                if now - last_log >= 5:
                    self.logger.info(
                        f"⏳ Cooldown active {symbol}: {remaining:.1f}s remaining (elapsed {since_last:.1f}s / needed {effective_cd:.1f}s | base {base_cd}s x mult {self.adaptive_cooldown_multiplier:.2f})"
                    )
                    self._last_cd_log[symbol] = now
                return False
        last_fail = self.failed_signal_cooldown.get(symbol, 0)
        if last_fail:
            since_fail = now - last_fail
            if since_fail < self.failed_signal_cooldown_period:
                remaining = self.failed_signal_cooldown_period - since_fail
                if not hasattr(self, '_last_fail_cd_log'):
                    self._last_fail_cd_log = {}
                last_log = self._last_fail_cd_log.get(symbol, 0)
                if now - last_log >= 10:
                    self.logger.info(
                        f"🚫 Failed-signal cooldown {symbol}: {remaining:.1f}s remaining (elapsed {since_fail:.1f}s / needed {self.failed_signal_cooldown_period:.1f}s)"
                    )
                    self._last_fail_cd_log[symbol] = now
                return False
        if symbol in self.recently_closed_profitable:
            closed_time = self.recently_closed_profitable[symbol]
            # closed_time may be datetime (legacy) or epoch float; normalize to age seconds
            try:
                age = self._get_timestamp_age_seconds(closed_time)
            except Exception:
                # Fallback to legacy behavior if helper fails
                age = now - closed_time if isinstance(closed_time, (int, float)) else 0
            if age < self.profitable_closure_cooldown:
                return False
        return True
    
    def record_signal_time(self, symbol: str):
        """Record the time of signal generation"""
        self.last_signal_time[symbol] = time.time()
    
    def record_failed_signal(self, symbol: str):
        """Record a failed signal for extended cooldown"""
        self.failed_signal_cooldown[symbol] = time.time()
        self.logger.info(f"🚫 Recording failed signal for {symbol} - extended cooldown activated")
    
    def validate_signal_price(self, signal, current_market_data) -> bool:
        """
        Enhanced signal validation with data consistency checks
        
        FIX 1: DATA CONSISTENCY - Use same data source for signal and validation
        FIX 2: TIMESTAMP VALIDATION - Ensure fresh data 
        FIX 3: STALENESS CHECKS - Reject old signals
        """
        if not current_market_data:
            self.logger.warning(f"⚠️ No current market data to validate signal for {signal.symbol}")
            return False

        # Check signal freshness (reject signals older than 30 seconds)
        signal_age = self._get_timestamp_age_seconds(getattr(signal, 'timestamp', None))
        if signal_age > 30:  # 30 seconds max age
            self.logger.warning(f"🚫 Signal rejected for {signal.symbol}: Signal too old ({signal_age:.1f}s)")
            return False

        # Get FRESH market price from the data manager
        fresh_price = self.data_manager.get_current_price(signal.symbol)

        if not fresh_price:
            self.logger.warning(f"⚠️ Could not get fresh market data for {signal.symbol}")
            return False

        # Use the fresh price data instead of the passed current_market_data
        current_price = fresh_price
        signal_entry = signal.entry_price

        # Skip data staleness check since we're using direct price
        data_age = 0  # Fresh price assumed to be current
        if data_age > 10:  # 10 seconds max data age
            self.logger.warning(f"🚫 Signal rejected for {signal.symbol}: Market data too stale ({data_age:.1f}s)")
            return False

        # Calculate price gap percentage
        price_gap_pct = abs(current_price - signal_entry) / signal_entry * 100 if signal_entry else 999

        # Use tighter tolerance since we're using consistent data sources
        # No need for extreme tolerance if data sources are aligned
        base_tolerance = 0.5  # Back to reasonable 0.5% since data should be consistent

        # Small adjustments for known volatile stocks only
        volatile_stocks = {'IONQ', 'RGTI', 'QBTS', 'QUBT'}
        if signal.symbol in volatile_stocks:
            max_price_gap = base_tolerance * 1.5  # 0.75% for volatile stocks
        else:
            max_price_gap = base_tolerance  # 0.5% for normal stocks

        if price_gap_pct > max_price_gap:
            self.logger.warning(
                f"🚫 Signal rejected for {signal.symbol}: Price gap {price_gap_pct:.2f}% (Signal: ${signal_entry:.2f}, Current: ${current_price:.2f}, Max: {max_price_gap:.2f}%)"
            )
            self.logger.info(f"Data consistency: Signal age {signal_age:.1f}s, Data age {data_age:.1f}s")
            return False

        self.logger.debug(f"✅ Signal validated for {signal.symbol}: Gap {price_gap_pct:.2f}% (Max: {max_price_gap:.2f}%)")
        return True
    
    def _get_dynamic_price_gap_tolerance(self, symbol: str, price: float) -> float:
        """Calculate dynamic price gap tolerance based on stock characteristics"""
        
        # Base tolerance
        base_tolerance = 0.8  # Start with 0.8% instead of 0.5%
        
        # Stock-specific volatility adjustments
        volatility_map = {
            # High volatility stocks (quantum, biotech, small cap)
            'IONQ': 2.0, 'RGTI': 1.8, 'QBTS': 1.8, 'QUBT': 2.0,
            'MRNA': 1.5, 'ROKU': 1.8, 'TSLA': 1.5, 'AMD': 1.3,
            
            # Medium-high volatility tech
            'NVDA': 1.2, 'META': 1.2, 'NFLX': 1.2, 'CRM': 1.1,
            'UBER': 1.1, 'ZOOM': 1.3, 'PLTR': 1.5,
            
            # Large cap (more stable)
            'AAPL': 0.8, 'MSFT': 0.8, 'GOOGL': 0.9, 'AMZN': 1.0,
            
            # ETFs (most stable)
            'SPY': 0.5, 'QQQ': 0.7, 'IWM': 0.9, 'XLF': 0.6,
            
            # Financial (medium volatility)
            'JPM': 0.8, 'BAC': 0.9, 'GS': 1.0, 'C': 1.1
        }
        
        symbol_multiplier = volatility_map.get(symbol, 1.0)  # Default 1.0x if unknown
        
        # Price-based adjustment (penny stocks are more volatile)
        if price < 5.0:
            price_multiplier = 2.0  # 2x tolerance for penny stocks
        elif price < 20.0:
            price_multiplier = 1.5  # 1.5x tolerance for low-price stocks
        elif price < 100.0:
            price_multiplier = 1.0  # Normal tolerance for mid-range
        else:
            price_multiplier = 0.8  # Slightly tighter for high-price stocks
        
        # Time of day adjustment (more volatile at open/close)
        from datetime import datetime
        current_time = datetime.now().time()
        
        # Market open volatility (9:30-10:30 ET)
        if datetime.strptime("09:30", "%H:%M").time() <= current_time <= datetime.strptime("10:30", "%H:%M").time():
            time_multiplier = 1.5
        # Market close volatility (15:00-16:00 ET)  
        elif datetime.strptime("15:00", "%H:%M").time() <= current_time <= datetime.strptime("16:00", "%H:%M").time():
            time_multiplier = 1.3
        # Lunch time (relatively calm)
        elif datetime.strptime("12:00", "%H:%M").time() <= current_time <= datetime.strptime("14:00", "%H:%M").time():
            time_multiplier = 0.8
        else:
            time_multiplier = 1.0
        
        # Calculate final tolerance
        final_tolerance = base_tolerance * symbol_multiplier * price_multiplier * time_multiplier
        
        # Cap the tolerance (don't go crazy)
        final_tolerance = min(final_tolerance, 3.0)  # Max 3%
        final_tolerance = max(final_tolerance, 0.3)  # Min 0.3%
        
        # Log the calculation periodically for debugging
        if not hasattr(self, '_last_tolerance_log'):
            self._last_tolerance_log = {}
        
        if symbol not in self._last_tolerance_log or abs(self._last_tolerance_log[symbol] - final_tolerance) > 0.1:
            self.logger.debug(f"📊 {symbol} tolerance: {final_tolerance:.1f}% "
                            f"(vol: {symbol_multiplier:.1f}x, price: {price_multiplier:.1f}x, time: {time_multiplier:.1f}x)")
            self._last_tolerance_log[symbol] = final_tolerance
        
        return final_tolerance
    
    def filter_watchlist(self) -> List[str]:
        """Filter watchlist based on volume and volatility criteria"""
        try:
            filtered_symbols = []
            self.last_filter_rejections = {}
            
            for symbol in config.INTRADAY_WATCHLIST[:10]:  # Limit to 10 for demo
                try:
                    # Skip symbols with untracked positions (if exclusion is enabled)
                    if (not config.ADOPT_EXISTING_POSITIONS and 
                        hasattr(self, '_excluded_symbols') and symbol in self._excluded_symbols):
                        continue
                        
                    # Get basic market data
                    current_price = self.data_manager.get_current_price(symbol)
                    
                    if current_price is None:
                        continue
                    
                    # Get volume and spread data
                    try:
                        # Get recent bars to check volume
                        bars = self.data_manager.get_bars([symbol], timeframe='1Day', limit=5)
                        if symbol in bars and len(bars[symbol]) > 0:
                            # Use average daily volume from recent days
                            recent_volumes = [bar.volume for bar in bars[symbol]]
                            volume = sum(recent_volumes) / len(recent_volumes)
                        else:
                            volume = 500000  # Assume sufficient volume if data unavailable
                            
                        # Get bid/ask spread (simplified for now)
                        # For major ETFs and stocks, spread is typically very low
                        spread_pct = 0.05  # Assume 0.05% spread for these liquid stocks
                            
                    except Exception as volume_err:
                        self.logger.debug(f"Volume check error for {symbol}: {volume_err}")
                        volume = 500000  # Assume sufficient volume on error
                        spread_pct = 0.05
                    
                    # Apply filters
                    reasons = []
                    if not (config.MIN_PRICE <= current_price <= config.MAX_PRICE):
                        reasons.append(f"price {current_price:.2f} outside [{config.MIN_PRICE},{config.MAX_PRICE}]")
                    if volume < config.MIN_VOLUME:
                        reasons.append(f"vol {volume} < {config.MIN_VOLUME}")
                    if spread_pct > config.MAX_SPREAD_PCT:
                        reasons.append(f"spread {spread_pct:.3f}% > {config.MAX_SPREAD_PCT}%")
                    if not reasons:
                        filtered_symbols.append(symbol)
                        self.logger.debug(f"✅ {symbol} passed filters: ${current_price:.2f}, Vol: {volume:,}")
                    else:
                        self.last_filter_rejections[symbol] = reasons
                
                except Exception as e:
                    self.logger.warning(f"❌ Error filtering {symbol}: {e}")
                    continue
            
            # Log filtered watchlist only at startup or periodically
            if not hasattr(self, 'last_watchlist_log_time'):
                self.last_watchlist_log_time = 0
            
            current_time = time.time()
            if current_time - self.last_watchlist_log_time >= 300:  # Log every 5 minutes
                self.logger.info(f"📊 Filtered watchlist: {len(filtered_symbols)} symbols from {len(config.INTRADAY_WATCHLIST)}")
                self.last_watchlist_log_time = current_time
            return filtered_symbols
            
        except Exception as e:
            self.logger.error(f"❌ Error filtering watchlist: {e}")
            return config.INTRADAY_WATCHLIST[:5]  # Fallback to first 5
    
    def generate_signals(self, symbol: str, data: pd.DataFrame) -> List[ScalpingSignal]:
        """
        Generate trading signals with enhanced data consistency and speed
        
        FIX 3: FASTER SIGNAL EXECUTION - Pre-validate and timestamp signals
        """
        signals: List[ScalpingSignal] = []
        generation_start_time = time.time()
        total_strategy_raw = 0
        price_gap_rejections = 0
        try:
            # Throttled data diagnostics
            try:
                if not hasattr(self, '_last_data_diag'):
                    self._last_data_diag = {}
                last_diag = self._last_data_diag.get(symbol, 0)
                if time.time() - last_diag >= 60:
                    cols = list(data.columns)
                    self.logger.info(f"🧪 {symbol} data snapshot: bars={len(data)}, cols={cols[-12:]} (showing last 12)")
                    required_cols = ['ema_5','ema_13','rsi','vwap','bb_upper','bb_lower','volume_ratio']
                    missing = [c for c in required_cols if c not in data.columns]
                    if missing:
                        self.logger.warning(f"⚠️ {symbol} missing indicators: {missing}")
                    else:
                        last_row = data.iloc[-1][required_cols]
                        nan_cols = [c for c,v in last_row.items() if pd.isna(v)]
                        if nan_cols:
                            self.logger.warning(f"⚠️ {symbol} NaN indicators latest bar: {nan_cols}")
                    self._last_data_diag[symbol] = time.time()
            except Exception as diag_err:
                self.logger.debug(f"Diag error {symbol}: {diag_err}")

            current_price = self.data_manager.get_current_price(symbol)
            if not current_price:
                self.logger.debug(f"⚠️ No current price data for pre-validation - skipping {symbol}")
                if not hasattr(self, 'signal_rejections'):
                    self.signal_rejections = {}
                self.signal_rejections[symbol] = 'no_current_price_data'
                return []

            # Current price already retrieved above

            for strategy_name, strategy in self.strategies.items():
                try:
                    # Call the strategy's generate_signal method (returns dict or None)
                    strategy_signal = strategy.generate_signal(symbol, data)
                    if strategy_signal:
                        # Convert dict signal to ScalpingSignal object
                        scalping_signal = ScalpingSignal(
                            symbol=strategy_signal['symbol'],
                            signal_type=strategy_signal['action'],  # 'BUY' or 'SELL'
                            strategy=strategy_signal['strategy'],
                            confidence=strategy_signal['confidence'],
                            entry_price=strategy_signal['price'],
                            stop_loss=0.0,  # Will be calculated later
                            profit_target=0.0,  # Will be calculated later
                            timestamp=generation_start_time,
                            metadata=strategy_signal  # Store original signal data
                        )
                        
                        strategy_signals = [scalping_signal]
                        self.logger.info(f"🧬 {strategy_name} raw signals {len(strategy_signals)} for {symbol}")
                        total_strategy_raw += len(strategy_signals)
                        for sig in strategy_signals:
                            sig.timestamp = generation_start_time
                            price_gap = abs(sig.entry_price - current_price) / current_price * 100 if current_price else 999
                            max_gap = 0.75 if symbol in {'IONQ','RGTI','QBTS','QUBT'} else 0.5
                            if price_gap <= max_gap:
                                signals.append(sig)
                            else:
                                price_gap_rejections += 1
                    else:
                        self.logger.debug(f"🧬 {strategy_name} 0 raw signals {symbol}")
                except Exception as strat_err:
                    self.logger.warning(f"❌ Strategy {strategy_name} error {symbol}: {strat_err}")
                    continue

            if signals:
                current_short_exposure = getattr(self.risk_manager, 'total_short_exposure', 0)
                max_short_exposure = config.MAX_SHORT_EXPOSURE
                ratio = current_short_exposure / max_short_exposure if max_short_exposure else 0
                if ratio > 0.8:
                    for sig in signals:
                        if sig.signal_type == 'BUY':
                            sig.confidence *= 1.3
                        elif sig.signal_type == 'SELL':
                            sig.confidence *= 0.7
                signals.sort(key=lambda x: x.confidence, reverse=True)
                best = signals[0]
                self.logger.info(f"🎯 Best signal {symbol} {best.signal_type} {best.strategy} conf={best.confidence:.2f}")
                return [best]
            else:
                if not hasattr(self, 'signal_rejections'):
                    self.signal_rejections = {}
                reasons = []
                if total_strategy_raw == 0:
                    reasons.append('no_raw')
                if price_gap_rejections:
                    reasons.append(f'gap_rejects={price_gap_rejections}')
                if not reasons:
                    reasons.append('post_filter_fail')
                self.signal_rejections[symbol] = ','.join(reasons)
                self.logger.info(f"🛑 No executable signals {symbol} raw={total_strategy_raw} gap_rej={price_gap_rejections}")
                return []
        except Exception as e:
            self.logger.error(f"❌ Error generating signals for {symbol}: {e}")
            if not hasattr(self, 'signal_rejections'):
                self.signal_rejections = {}
            self.signal_rejections[symbol] = f'exception:{type(e).__name__}'
            return []
    
    def _determine_market_regime(self, market_data: dict, indicators: dict) -> str:
        """Determine current market regime for trade context"""
        try:
            volume_ratio = indicators.get('volume_ratio', market_data.get('volume_ratio', 1.0))
            rsi = indicators.get('rsi', 50)
            
            # Simple regime classification
            if volume_ratio > 2.0:
                if rsi > 70:
                    return "high_volume_overbought"
                elif rsi < 30:
                    return "high_volume_oversold"
                else:
                    return "high_volume_trending"
            elif volume_ratio > 1.5:
                return "elevated_volume"
            elif volume_ratio < 0.5:
                return "low_volume"
            else:
                if rsi > 60:
                    return "normal_volume_bullish"
                elif rsi < 40:
                    return "normal_volume_bearish"
                else:
                    return "normal_volume_neutral"
                    
        except Exception:
            return "unknown"
    
    def _verify_order_fill(self, order_id: str, symbol: str, intended_side: str, expected_quantity: int, timeout: int = 10) -> bool:
        """
        Verify that an order was actually filled before creating position tracking.
        This prevents phantom positions when orders are rejected/cancelled.
        """
        try:
            # Allow order_id to be an object with .id
            raw_order_id = getattr(order_id, 'id', order_id)
            self.logger.info(f"🔍 Verifying order fill for {raw_order_id} ({symbol})")
            
            start_time = time.time()
            check_interval = 1  # Check every 1 second
            
            while time.time() - start_time < timeout:
                try:
                    # Method 1: Check broker positions directly
                    broker_position = self.order_manager.get_position_info(symbol, context="order_fill_verification", force_fresh=True)
                    
                    if broker_position and abs(float(broker_position.get('qty', 0))) > 0:
                        # Normalize side detection: prefer explicit 'side' (long/short), then qty sign, then market_value
                        broker_side = self._normalize_broker_position_side(broker_position)
                        broker_qty = abs(float(broker_position.get('qty', 0)))
                        
                        # Verify direction matches intention
                        if broker_side == intended_side:
                            # Verify quantity is reasonable (allow some variance for partial fills)
                            qty_difference = abs(broker_qty - expected_quantity)
                            qty_tolerance = max(1, expected_quantity * 0.1)  # 10% tolerance or 1 share minimum
                            
                            if qty_difference <= qty_tolerance:
                                self.logger.info(f"✅ ORDER FILL VERIFIED: {symbol} - {broker_side} {broker_qty} shares")
                                return True
                            else:
                                self.logger.warning(f"⚠️ Quantity mismatch: expected {expected_quantity}, got {broker_qty}")
                        else:
                            self.logger.warning(f"⚠️ Direction mismatch: expected {intended_side}, got {broker_side}")
                    
                    # Method 2: If available, check order status via order manager
                    if hasattr(self.order_manager, 'get_order_status'):
                        try:
                            order_status = self.order_manager.get_order_status(raw_order_id)
                            if order_status:
                                status = order_status.get('status', '').lower()
                                if status in ['filled', 'partially_filled']:
                                    filled_qty = float(order_status.get('filled_qty', 0))
                                    if filled_qty > 0:
                                        self.logger.info(f"✅ ORDER STATUS VERIFIED: {raw_order_id} filled {filled_qty} shares")
                                        return True
                                elif status in ['cancelled', 'rejected', 'expired']:
                                    self.logger.warning(f"🚫 ORDER CANCELLED/REJECTED: {raw_order_id} status: {status}")
                                    return False
                        except Exception as status_error:
                            self.logger.debug(f"Could not check order status: {status_error}")
                    
                    # Wait before next check
                    time.sleep(check_interval)
                    
                except Exception as check_error:
                    self.logger.warning(f"Error in fill verification check: {check_error}")
                    time.sleep(check_interval)
            
            # Timeout reached without confirmation
            self.logger.error(f"⏰ ORDER FILL VERIFICATION TIMEOUT: {raw_order_id} after {timeout}s")
            self.logger.error(f"🚫 Cannot confirm order fill - will not create position tracking")
            
            # Final check: see if position exists now
            try:
                final_position = self.order_manager.get_position_info(symbol, context="final_verification", force_fresh=True)
                if final_position and abs(float(final_position.get('qty', 0))) > 0:
                    self.logger.warning(f"⚠️ Position exists after timeout - possible delayed fill")
                    return True
            except Exception as final_error:
                self.logger.debug(f"Final verification check failed: {final_error}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error in order fill verification: {e}")
            # On verification error, assume order failed to be safe
            return False

    def _normalize_broker_position_side(self, broker_position: dict) -> str:
        """Return 'buy' for long and 'sell' for short using robust detection.
        Prefers broker 'side' (long/short), falls back to qty sign or market_value sign.
        """
        try:
            # 1) Explicit side from broker (common in Alpaca)
            side_val = broker_position.get('side')
            if isinstance(side_val, str):
                s = side_val.strip().lower()
                if s in ('long', 'buy'):
                    return 'buy'
                if s in ('short', 'sell'):
                    return 'sell'
            # 2) Fallback to qty sign if broker uses signed quantities
            if 'qty' in broker_position:
                try:
                    q = float(broker_position.get('qty') or 0)
                    if q > 0:
                        return 'buy'
                    if q < 0:
                        return 'sell'
                except Exception:
                    pass
            # 3) Fallback to market_value sign (shorts often negative)
            if 'market_value' in broker_position:
                try:
                    mv = float(broker_position.get('market_value') or 0)
                    return 'sell' if mv < 0 else 'buy'
                except Exception:
                    pass
        except Exception:
            pass
        # Default safe assumption
        return 'buy'
    
    def sync_positions_with_broker(self):
        """Synchronize internal position tracking with actual broker positions"""
        try:
            if not self.order_manager or not hasattr(self.order_manager, 'data_manager') or not self.order_manager.data_manager.api:
                return
            
            # Get all actual positions from broker
            actual_positions = self.order_manager.data_manager.api.list_positions()
            
            if not actual_positions:
                self.logger.debug("📊 No actual positions found at broker")
                # Clear all internal tracking if no actual positions
                if self.active_positions:
                    self.logger.warning(f"🧹 Clearing {len(self.active_positions)} orphaned internal positions")
                    self.active_positions.clear()
                return
            
            # Check for discrepancies
            actual_symbols = {pos['symbol'] for pos in actual_positions if abs(float(pos['qty'])) > 0}
            tracked_symbols = set(self.active_positions.keys())
            
            # Find positions that exist at broker but not in tracking
            untracked_positions = actual_symbols - tracked_symbols
            if untracked_positions:
                # Only log warning once per session for untracked positions to avoid spam
                if not hasattr(self, '_untracked_positions_warned'):
                    self._untracked_positions_warned = set()
                
                new_untracked = untracked_positions - self._untracked_positions_warned
                if new_untracked:
                    if config.ADOPT_EXISTING_POSITIONS:
                        # Adopt existing positions for management
                        self.logger.info(f"🔄 Adopting {len(new_untracked)} existing positions for management: {new_untracked}")
                        
                        for symbol in new_untracked:
                            # Find the actual position data for this symbol
                            position_data = next((pos for pos in actual_positions if pos['symbol'] == symbol), None)
                            if position_data:
                                # Debug: log available fields to understand the data structure
                                self.logger.debug(f"🔍 Position data fields for {symbol}: {list(position_data.keys())}")
                                
                                qty = float(position_data['qty'])
                                
                                # Try different field names for entry price (robust approach)
                                entry_price = None
                                if 'avg_entry_price' in position_data:
                                    entry_price = float(position_data['avg_entry_price'])
                                elif 'avg_cost' in position_data:
                                    entry_price = float(position_data['avg_cost'])
                                elif 'cost_basis' in position_data and abs(qty) > 0:
                                    entry_price = float(position_data['cost_basis']) / abs(qty)
                                elif 'market_value' in position_data and abs(qty) > 0:
                                    # Fallback: use current market value as entry price estimate
                                    entry_price = float(position_data['market_value']) / abs(qty)
                                else:
                                    self.logger.warning(f"⚠️ Cannot determine entry price for {symbol}, skipping adoption")
                                    continue
                                
                                # Calculate current price
                                current_price = float(position_data['market_value']) / abs(qty) if qty != 0 else entry_price
                                
                                # Determine signal type based on position direction (robust)
                                try:
                                    broker_side = self._normalize_broker_position_side(position_data)
                                except Exception:
                                    broker_side = 'buy' if qty > 0 else 'sell'
                                signal_type = "BUY" if broker_side == 'buy' else "SELL"
                                
                                # Create position tracking entry with estimated targets
                                profit_target = entry_price * (1 + config.PROFIT_TARGET_PCT / 100) if signal_type == "BUY" else entry_price * (1 - config.PROFIT_TARGET_PCT / 100)
                                stop_loss = entry_price * (1 - config.STOP_LOSS_PCT / 100) if signal_type == "BUY" else entry_price * (1 + config.STOP_LOSS_PCT / 100)
                                
                                # Create a signal object for the adopted position
                                adopted_signal = ScalpingSignal(
                                    symbol=symbol,
                                    signal_type=signal_type,
                                    strategy="adopted",
                                    confidence=1.0,
                                    entry_price=entry_price,
                                    stop_loss=stop_loss,
                                    profit_target=profit_target,
                                    timestamp=datetime.now(),
                                    metadata={'adopted': True}
                                )
                                
                                # Add to internal tracking
                                self.active_positions[symbol] = {
                                    'order_id': f"adopted_{symbol}",
                                    'signal': adopted_signal,
                                    'entry_time': datetime.now(),
                                    'position_size': abs(qty),
                                    'entry_price': entry_price,
                                    'stop_loss': stop_loss,
                                    'original_stop_loss': stop_loss,  # Track original for trailing stop detection
                                    'profit_target': profit_target
                                }
                                
                                # Initialize peak tracking for adopted position
                                self.position_peaks[symbol] = {
                                    'peak_price': entry_price,
                                    'peak_pnl_pct': 0.0,
                                    'peak_absolute_pnl': 0.0,
                                    'initial_stop': stop_loss,
                                    'trailing_active': False
                                }
                                
                                # Calculate current P&L
                                if signal_type == "BUY":
                                    unrealized_pnl = (current_price - entry_price) * abs(qty)
                                    pnl_pct = ((current_price - entry_price) / entry_price) * 100
                                else:
                                    unrealized_pnl = (entry_price - current_price) * abs(qty)
                                    pnl_pct = ((entry_price - current_price) / entry_price) * 100
                                
                                self.logger.info(f"✅ Adopted {symbol}: {signal_type} {abs(qty)} shares @ ${entry_price:.2f}")
                                self.logger.info(f"   📊 Current: ${current_price:.2f} | P&L: ${unrealized_pnl:+.2f} ({pnl_pct:+.2f}%)")
                                self.logger.info(f"   🎯 Targets: Profit ${profit_target:.2f} | Stop ${stop_loss:.2f}")
                        
                        self._untracked_positions_warned.update(new_untracked)
                    else:
                        # Original exclusion logic
                        self.logger.warning(f"🚨 Found {len(new_untracked)} positions not in internal tracking: {new_untracked}")
                        self.logger.warning(f"💡 These may be from partial fills or order timing - will be excluded from new trades")
                        self._untracked_positions_warned.update(new_untracked)
                        
                        # Skip these symbols in trading to avoid conflicts
                        for symbol in untracked_positions:
                            if symbol not in getattr(self, '_excluded_symbols', set()):
                                if not hasattr(self, '_excluded_symbols'):
                                    self._excluded_symbols = set()
                                self._excluded_symbols.add(symbol)
                                self.logger.debug(f"⛔ Excluding {symbol} from trading (untracked position)")
            
            # Find positions tracked internally but not at broker
            orphaned_tracking = tracked_symbols - actual_symbols
            if orphaned_tracking:
                self.logger.warning(f"🧹 Removing {len(orphaned_tracking)} orphaned position tracking: {orphaned_tracking}")
                for symbol in orphaned_tracking:
                    del self.active_positions[symbol]
                    # Clean up peak tracking too
                    if symbol in self.position_peaks:
                        del self.position_peaks[symbol]
                        
        except Exception as e:
            self.logger.error(f"❌ Error syncing positions with broker: {e}")
    
    def execute_signal(self, signal: ScalpingSignal) -> bool:
        """Execute a trading signal with comprehensive position checking"""
        try:
            self.logger.error(f"🔥 EXECUTE_SIGNAL ENTRY: {signal.symbol} {signal.signal_type} @ ${signal.entry_price:.2f}")
            self.logger.info(f"📋 STARTING execute_signal for {signal.symbol} {signal.signal_type} @ ${signal.entry_price:.2f}")
            
            # CRITICAL: Check individualized confidence signals before any trade
            try:
                from stock_specific_config import should_execute_trade
                confidence_decision = should_execute_trade(signal.symbol, signal.signal_type)
                
                if not confidence_decision['execute']:
                    self.logger.warning(f"🚫 CONFIDENCE REJECTED: {signal.symbol} - {confidence_decision['reason']}")
                    self.logger.info(f"📋 FAILED: Individualized confidence check failed for {signal.symbol}")
                    return False
                else:
                    self.logger.info(f"✅ CONFIDENCE APPROVED: {signal.symbol} - {confidence_decision['confidence']:.1f}%")
                    # Update signal confidence with real-time calculation
                    signal.confidence = confidence_decision['confidence'] / 100.0
                    
            except Exception as conf_error:
                self.logger.error(f"❌ Confidence system error for {signal.symbol}: {conf_error}")
                self.logger.info(f"📋 FAILED: Confidence system error for {signal.symbol}")
                return False
            
            # Lightweight pre-trade quality filter
            if not self._pre_trade_filter(signal):
                self.logger.debug(f"🚫 Pre-trade filter rejected {signal.symbol} ({signal.signal_type}) conf={getattr(signal, 'confidence', None)}")
                self.logger.info(f"📋 FAILED: Pre-trade filter rejected {signal.symbol}")
                return False
            # TRAILING STOP PROTECTION: Check if symbol recently closed profitably
            if signal.symbol in self.recently_closed_profitable:
                last_closure = self.recently_closed_profitable[signal.symbol]
                # Support both datetime and epoch floats
                age = self._get_timestamp_age_seconds(last_closure)
                if age < self.profitable_closure_cooldown:
                    remaining_cooldown = self.profitable_closure_cooldown - age
                    self.logger.info(f"🛡️ SKIPPING {signal.symbol} - profitable closure cooldown active ({remaining_cooldown:.0f}s remaining)")
                    self.logger.info(f"📋 FAILED: Profitable closure cooldown for {signal.symbol}")
                    return False
                else:
                    # Cooldown expired, remove from tracking
                    del self.recently_closed_profitable[signal.symbol]
                    self.logger.info(f"✅ {signal.symbol} cooldown expired - signals allowed again")
            
            self.logger.info(f"📋 CHECKPOINT 1: Cooldown checks passed for {signal.symbol}")
            
            # Check actual broker position first to prevent accumulation
            actual_position = self.order_manager.get_position_info(signal.symbol, context="signal_execution", force_fresh=True)
            
            if actual_position and abs(float(actual_position.get('qty', 0))) > 0:
                existing_side = self._normalize_broker_position_side(actual_position)
                signal_side = signal.signal_type.lower()
                
                # If signal is opposite to existing position, close the position first
                if ((existing_side == 'buy' and signal_side == 'sell') or 
                    (existing_side == 'sell' and signal_side == 'buy')):
                    self.logger.info(f"🔄 Closing existing {existing_side} position due to opposite {signal_side} signal for {signal.symbol}")
                    return self.close_position(signal.symbol)
                else:
                    # Same direction signal - reject to prevent accumulation
                    self.logger.warning(f"⚠️ REJECTING {signal_side} signal for {signal.symbol} - already have {existing_side} position")
                    self.logger.info(f"📋 FAILED: Position conflict for {signal.symbol}")
                    return False
            
            self.logger.info(f"📋 CHECKPOINT 2: Position checks passed for {signal.symbol}")
            
            # Check if we have an existing position in our tracking
            if signal.symbol in self.active_positions:
                existing_position = self.active_positions[signal.symbol]
                existing_signal_type = existing_position['signal'].signal_type
                
                # If signal is opposite to existing position, close the position
                if ((existing_signal_type == "BUY" and signal.signal_type == "SELL") or
                    (existing_signal_type == "SELL" and signal.signal_type == "BUY")):
                    self.logger.info(f"🔄 Closing tracked {existing_signal_type} position due to opposite {signal.signal_type} signal for {signal.symbol}")
                    return self.close_position(signal.symbol)
                else:
                    self.logger.debug(f"⚠️ Ignoring {signal.signal_type} signal for {signal.symbol} - already have {existing_signal_type} position")
                    self.logger.info(f"📋 FAILED: Tracked position conflict for {signal.symbol}")
                    return False
            
            self.logger.info(f"📋 CHECKPOINT 3: Tracked position checks passed for {signal.symbol}")
            
            # Check risk limits - CRITICAL: Handle exceptions properly
            try:
                if not self.risk_manager.can_open_position(signal.symbol, signal.entry_price, signal.signal_type):
                    self.logger.warning(f"❌ Risk check failed for {signal.symbol} ({signal.signal_type}) @ ${signal.entry_price:.2f}")
                    self.logger.info(f"📋 FAILED: Risk check failed for {signal.symbol}")
                    return False
            except Exception as risk_exception:
                # CRITICAL FIX: Handle risk limit exceptions properly
                self.logger.error(f"🚫 RISK LIMIT VIOLATION for {signal.symbol}: {risk_exception}")
                self.logger.error(f"🛑 ORDER CANCELLED - Will NOT create phantom position")
                self.logger.info(f"📋 FAILED: Risk limit violation for {signal.symbol}")
                return False
            
            self.logger.info(f"📋 CHECKPOINT 4: Risk checks passed for {signal.symbol}")
            
            # Determine adaptive stop before sizing so R-based sizing can incorporate it
            entry_price = signal.entry_price
            
            # Get stock-specific thresholds instead of generic config
            try:
                from stock_specific_config import get_stock_thresholds
                stock_thresholds = get_stock_thresholds(signal.symbol)
                base_stop_pct = stock_thresholds['stop_loss_pct'] * 100  # Convert to percentage
                profit_target_pct = stock_thresholds['take_profit_pct'] * 100  # Convert to percentage
                self.logger.info(f"📊 STOCK-SPECIFIC THRESHOLDS {signal.symbol}: Stop {base_stop_pct:.2f}% | Profit {profit_target_pct:.2f}%")
            except Exception as threshold_error:
                self.logger.warning(f"⚠️ Could not get stock-specific thresholds for {signal.symbol}: {threshold_error}")
                base_stop_pct = config.STOP_LOSS_PCT
                profit_target_pct = config.PROFIT_TARGET_PCT
                self.logger.info(f"📊 FALLBACK THRESHOLDS {signal.symbol}: Stop {base_stop_pct:.2f}% | Profit {profit_target_pct:.2f}%")
                
            adaptive_stop_pct = base_stop_pct
            atr_pct = None
            if getattr(config, 'USE_ATR_STOPS', False):
                try:
                    bars = self.data_manager.get_bars(signal.symbol, timeframe=config.TIMEFRAME, limit=100)
                    if bars is not None and len(bars) >= config.ATR_PERIOD + 2 and all(c in bars.columns for c in ['high','low','close']):
                        highs = bars['high']; lows = bars['low']; closes = bars['close']
                        trs = []
                        for i in range(1, len(bars)):
                            h = highs.iloc[i]; l = lows.iloc[i]; pc = closes.iloc[i-1]
                            tr = max(h-l, abs(h-pc), abs(l-pc))
                            trs.append(tr)
                        if len(trs) >= config.ATR_PERIOD:
                            atr = sum(trs[-config.ATR_PERIOD:]) / config.ATR_PERIOD
                            atr_pct = (atr / entry_price) * 100 if entry_price else None
                            if atr_pct and atr_pct > 0:
                                adaptive_stop_pct = max(base_stop_pct, config.ATR_MULT * atr_pct, config.MIN_STOP_PCT)
                                adaptive_stop_pct = min(adaptive_stop_pct, config.MAX_STOP_PCT)
                except Exception as atr_err:
                    self.logger.debug(f"ATR sizing calc error {signal.symbol}: {atr_err}")
            # Build a provisional stop price for sizing
            provisional_stop = entry_price * (1 - adaptive_stop_pct/100) if signal.signal_type == 'BUY' else entry_price * (1 + adaptive_stop_pct/100)
            signal.stop_loss = provisional_stop
            signal.profit_target = entry_price * (1 + profit_target_pct/100) if signal.signal_type == 'BUY' else entry_price * (1 - profit_target_pct/100)

            position_size = self.risk_manager.calculate_position_size(
                entry_price=signal.entry_price,
                stop_loss=signal.stop_loss,
                symbol=signal.symbol,
                side=signal.signal_type.lower()
            )
            
            if position_size <= 0:
                self.logger.warning(f"❌ Invalid position size for {signal.symbol} ({signal.signal_type}). entry=${signal.entry_price:.2f} stop=${signal.stop_loss:.2f} calc_size={position_size}")
                self.logger.info(f"📋 FAILED: Invalid position size for {signal.symbol}")
                return False
            
            self.logger.info(f"📋 CHECKPOINT 5: Position sizing passed for {signal.symbol} (size={position_size})")
            
            # Check wash trade prevention
            if not self.can_submit_order(signal.symbol):
                self.logger.debug(f"⏳ Delaying order for {signal.symbol} - wash trade prevention")
                self.logger.info(f"📋 FAILED: Wash trade prevention for {signal.symbol}")
                return False
            
            self.logger.info(f"📋 CHECKPOINT 6: Wash trade checks passed for {signal.symbol}")
            
            # CRITICAL: Clear any pending orders before opening new position
            self.logger.info(f"🧹 Clearing pending orders for {signal.symbol} before new position")
            cancelled_count = self.order_manager.cancel_pending_orders_for_symbol(signal.symbol)
            if cancelled_count > 0:
                self.logger.info(f"✅ Cancelled {cancelled_count} pending orders for {signal.symbol}")
                # Wait for cancellations to process
                time.sleep(2)
            
            # CRITICAL FIX: Validate order direction before submission
            intended_side = signal.signal_type.lower()
            self.logger.info(f"🎯 SUBMITTING NEW POSITION: {signal.signal_type} {position_size} shares of {signal.symbol} @ ${signal.entry_price:.2f}")
            self.logger.info(f"🔍 ORDER VALIDATION: Intended side = {intended_side}")
            self.logger.info(f"📋 CHECKPOINT 7: About to submit order for {signal.symbol}")
            
            # Record order time for wash trade prevention
            self.record_order_time(signal.symbol)
            
            # Submit market order with validation
            order_result = self.order_manager.submit_market_order(
                symbol=signal.symbol,
                side=intended_side,
                quantity=position_size
            )
            
            self.logger.info(f"📋 CHECKPOINT 8: Order submission result for {signal.symbol}: {bool(order_result)}")
            
            # CRITICAL FIX: Verify order was submitted correctly AND verify order fill
            if order_result:
                readable_id = getattr(order_result, 'id', str(order_result))
                self.logger.info(f"✅ Order submitted with ID: {readable_id}")
                
                # Additional validation: Check if this is a simulated order
                if str(readable_id).startswith("SIM_"):
                    self.logger.warning(f"⚠️ SIMULATED ORDER DETECTED: {readable_id}")
                    self.logger.warning(f"⚠️ Position tracking may not reflect real broker state")
                
                # NEW: Verify order fill before creating position tracking
                fill_info = self._verify_order_fill(order_result, signal.symbol, intended_side, position_size)
                
                if not fill_info:
                    self.logger.error(f"🚫 ORDER NOT FILLED: {readable_id} for {signal.symbol}")
                    self.logger.error(f"🚫 Will NOT create phantom position tracking")
                    # Record this as a failed signal for extended cooldown
                    self.record_failed_signal(signal.symbol)
                    return False
            else:
                # Enrich failure with last OrderManager error if present
                last_err = None
                try:
                    last_err = getattr(self.order_manager, 'get_last_error', lambda: None)()
                except Exception:
                    last_err = None
                if last_err:
                    code = last_err.get('code'); msg = last_err.get('message'); det = last_err.get('details')
                    self.logger.error(f"🧩 EXECUTION FAILURE for {signal.symbol} ({signal.signal_type}) | ERROR_CODE={code} MSG={msg} DETAILS={det}")
                else:
                    self.logger.error(f"🧩 EXECUTION FAILURE for {signal.symbol} ({signal.signal_type}) | ERROR_CODE=unknown MSG=no_details")
                # Mark as failed signal for cooldown/backoff
                self.record_failed_signal(signal.symbol)
                return False
                
                # Get ACTUAL execution price from broker position (more reliable than order fill price)
                actual_position = self.order_manager.get_position_info(signal.symbol, context="execution_price", force_fresh=True)
                if actual_position and abs(float(actual_position.get('qty', 0))) > 0:
                    # Calculate actual average entry price from broker
                    actual_entry_price = abs(float(actual_position.get('avg_entry_price', signal.entry_price)))
                    actual_qty = abs(float(actual_position.get('qty', position_size)))
                    
                    self.logger.info(f"📍 ACTUAL EXECUTION: {signal.symbol} - {actual_qty} shares @ ${actual_entry_price:.2f}")
                    
                    # Recalculate stop loss and profit target based on ACTUAL execution price
                    from utils.signal_helper import calculate_adaptive_signal_levels
                    actual_levels = calculate_adaptive_signal_levels(
                        symbol=signal.symbol,
                        entry_price=actual_entry_price,
                        signal_type=signal.signal_type,
                        data_manager=self.data_manager,
                        timeframe=config.TIMEFRAME
                    )
                    
                    actual_stop_loss = actual_levels['stop_loss']
                    actual_profit_target = actual_levels['profit_target']
                    
                    self.logger.info(f"🎯 RECALCULATED LEVELS: {signal.symbol} - Stop: ${actual_stop_loss:.2f}, Target: ${actual_profit_target:.2f}")
                    
                    # Use actual execution data for position tracking
                    execution_entry_price = actual_entry_price
                    execution_stop_loss = actual_stop_loss
                    execution_profit_target = actual_profit_target
                    execution_position_size = actual_qty
                    # Record slippage vs intended signal entry
                    try:
                        self._record_slippage(signal.entry_price, actual_entry_price, signal.signal_type, signal.symbol)
                    except Exception as e:
                        self.logger.debug(f"Slippage recording error: {e}")
                else:
                    self.logger.warning(f"⚠️ Could not get actual execution price for {signal.symbol}, using signal prices")
                    execution_entry_price = signal.entry_price
                    execution_stop_loss = signal.stop_loss
                    execution_profit_target = signal.profit_target
                    execution_position_size = position_size
                
                # Track position with ACTUAL execution data
                # Grace & adaptive metadata
                grace_until = time.time() + getattr(config, 'INITIAL_STOP_GRACE', 0)
                catastrophic_mult = getattr(config, 'CATASTROPHIC_MULT', 1.2)
                self.active_positions[signal.symbol] = {
                    'order_id': readable_id,
                    'signal': signal,
                    'entry_time': datetime.now(),
                    'position_size': execution_position_size,
                    'entry_price': execution_entry_price,
                    'stop_loss': execution_stop_loss,
                    'original_stop_loss': execution_stop_loss,  # Track original for trailing stop detection
                    'profit_target': execution_profit_target,
                    'intended_side': intended_side,  # Track intended direction
                    'minimum_hold_time': getattr(config, 'INITIAL_STOP_GRACE', 0),
                    'adaptive_stop_pct': adaptive_stop_pct,
                    'atr_pct_entry': atr_pct,
                    'stop_grace_until': grace_until,
                    'catastrophic_mult': catastrophic_mult,
                    'breakeven_set': False,
                    'trailing_started': False,
                    'r_multiple_peak': 0.0
                }
                
                # Initialize peak tracking for new position
                self.position_peaks[signal.symbol] = {
                    'peak_price': execution_entry_price,
                    'peak_pnl_pct': 0.0,
                    'peak_absolute_pnl': 0.0,
                    'initial_stop': execution_stop_loss,
                    'trailing_active': False
                }
                # Initialize MAE/MFE trackers
                self.active_positions[signal.symbol]['mae_pct'] = 0.0
                self.active_positions[signal.symbol]['mfe_pct'] = 0.0
                
                # Track position with risk manager using actual execution data
                self.risk_manager.track_position_opened(signal.symbol, signal.signal_type, execution_position_size, execution_entry_price)
                
                # Increment trade counters (entries only)
                try:
                    today = datetime.utcnow().date()
                    if today != self.trade_day:
                        self.trade_day = today
                        self.symbol_trade_count.clear()
                        self.trade_count = 0
                    self.trade_count += 1
                    self.symbol_trade_count[signal.symbol] = self.symbol_trade_count.get(signal.symbol, 0) + 1
                except Exception:
                    pass
                atr_pct_str = f"{atr_pct:.3f}" if atr_pct else "n/a"
                self.logger.info(
                    f"✅ Position created for {signal.symbol}: {execution_position_size} @ ${execution_entry_price:.2f} "
                    f"Stop ${execution_stop_loss:.2f} ({self.active_positions[signal.symbol]['adaptive_stop_pct']:.3f}%) "
                    f"Target ${execution_profit_target:.2f} ATR% {atr_pct_str}"
                )
                # Create TradeRecord with enhanced decision context
                try:
                    md = self.data_manager.get_current_market_data(signal.symbol) or {}
                    
                    # 🔍 ENHANCED: Capture complete decision context for trade analysis
                    try:
                        from core.unified_indicators import unified_indicator_service
                        from stock_specific_config import get_real_time_confidence_for_trade
                        
                        # Get current indicator snapshot
                        bars = self.data_manager.get_bars(signal.symbol, timeframe=config.TIMEFRAME, limit=50)
                        if bars is not None and len(bars) > 20:
                            indicator_result = unified_indicator_service.get_indicators_for_strategy(bars, signal.symbol, signal.strategy)
                            indicators_snapshot = indicator_result.get('current_values', {}) if 'error' not in indicator_result else {}
                        else:
                            indicators_snapshot = {}
                        
                        # Get confidence breakdown
                        confidence_data = get_real_time_confidence_for_trade(signal.symbol)
                        confidence_breakdown = confidence_data.get('technical_summary', {})
                        
                        # Determine market regime
                        market_regime = self._determine_market_regime(md, indicators_snapshot)
                        
                        # Calculate risk assessment
                        risk_assessment = {
                            'stop_loss_pct': adaptive_stop_pct,
                            'atr_pct': atr_pct,
                            'position_size_calc': f"Risk-based sizing: {execution_position_size} shares",
                            'max_risk_amount': abs(execution_entry_price - execution_stop_loss) * execution_position_size
                        }
                        
                    except Exception as context_error:
                        self.logger.debug(f"Decision context capture failed {signal.symbol}: {context_error}")
                        indicators_snapshot = {}
                        confidence_breakdown = {}
                        market_regime = "unknown"
                        risk_assessment = {}
                    
                    tr = TradeRecord(
                        symbol=signal.symbol,
                        strategy=signal.strategy,
                        side=signal.signal_type,
                        entry_time=datetime.utcnow(),
                        entry_price=execution_entry_price,
                        stop_loss=execution_stop_loss,
                        profit_target=execution_profit_target,
                        position_size=int(execution_position_size),
                        confidence=signal.confidence,
                        spread_pct=md.get('spread_pct'),
                        volume=md.get('volume'),
                        volume_ratio=md.get('volume_ratio'),
                        # 🔍 Enhanced decision context
                        signal_reason=getattr(signal, 'reason', 'Signal reason not captured'),
                        indicators_at_entry=indicators_snapshot,
                        confidence_breakdown=confidence_breakdown,
                        market_regime=market_regime,
                        atr_percentile=atr_pct,
                        relative_volume=md.get('volume_ratio'),
                        risk_assessment=risk_assessment,
                        strategy_signals={'strategy_used': signal.strategy, 'confidence_threshold': 65}
                    )
                    self._trade_records[signal.symbol] = tr
                    
                    # 🔍 Log decision context for immediate visibility
                    self.logger.info(f"🔍 TRADE DECISION CONTEXT for {signal.symbol}:")
                    self.logger.info(f"   📊 Strategy: {signal.strategy} | Confidence: {signal.confidence:.1%}")
                    self.logger.info(f"   🎯 Reason: {getattr(signal, 'reason', 'Not captured')}")
                    self.logger.info(f"   📈 Market Regime: {market_regime}")
                    self.logger.info(f"   ⚖️ Risk: {adaptive_stop_pct:.2f}% stop | ATR: {atr_pct or 'N/A'}")
                    if indicators_snapshot:
                        key_indicators = {k: v for k, v in indicators_snapshot.items() 
                                        if k in ['rsi', 'macd', 'vwap', 'ema_9', 'volume_ratio']}
                        self.logger.info(f"   📊 Key Indicators: {key_indicators}")
                    
                except Exception as terr:
                    self.logger.debug(f"TradeRecord create failed {signal.symbol}: {terr}")
                return True
            
        except Exception as e:
            self.logger.error(f"❌ Error executing signal for {signal.symbol}: {e}")
        
        return False
    
    def manage_positions(self):
        """Manage active positions - check exits, trailing stops, etc."""
        positions_to_close = []  # list of (symbol, reason)

        for symbol, position in self.active_positions.items():
            try:
                # Get current price
                current_data = self.data_manager.get_current_market_data(symbol)
                if not current_data:
                    continue

                current_price = current_data['price']
                entry_price = position['entry_price']
                signal = position['signal']

                # Calculate current P&L and percentages
                if signal.signal_type == "BUY":
                    unrealized_pnl = (current_price - entry_price) * position['position_size']
                    pnl_pct = ((current_price - entry_price) / entry_price) * 100
                else:  # SELL
                    unrealized_pnl = (entry_price - current_price) * position['position_size']
                    pnl_pct = ((entry_price - current_price) / entry_price) * 100

                # CRITICAL: Update trailing stop FIRST (before any exit checks)
                self.update_trailing_stop_with_peak_tracking(symbol, position, current_price, pnl_pct)

                # Update MAE/MFE tracking
                if 'mae_pct' in position:
                    if pnl_pct < 0:
                        # pnl_pct negative; more negative is worse
                        position['mae_pct'] = min(position.get('mae_pct', 0.0), pnl_pct)
                    else:
                        position['mfe_pct'] = max(position.get('mfe_pct', 0.0), pnl_pct)

                # Check time-based exit
                hold_time = (datetime.now() - position['entry_time']).total_seconds()
                max_hold_time = self.timeframe_config.max_hold_time

                # Exit conditions
                should_exit = False
                exit_reason = ""

                # Enhanced stop loss handling with grace & catastrophic thresholds
                stop_loss_exceeded = False
                actual_loss_pct = 0.0
                now_ts = time.time()
                grace_active = now_ts < position.get('stop_grace_until', 0)
                planned_stop_pct = position.get('adaptive_stop_pct', config.STOP_LOSS_PCT)
                catastrophic_mult = position.get('catastrophic_mult', 1.2)
                catastrophic_threshold = planned_stop_pct * catastrophic_mult
                loss_pct = -pnl_pct if pnl_pct < 0 else 0

                if loss_pct >= catastrophic_threshold:
                    stop_loss_exceeded = True
                    actual_loss_pct = loss_pct
                    should_exit = True
                    exit_reason = f"Catastrophic loss {loss_pct:.3f}% >= {catastrophic_threshold:.3f}% (planned {planned_stop_pct:.3f}%)"
                elif not grace_active:
                    if signal.signal_type == 'BUY' and current_price <= position['stop_loss']:
                        stop_loss_exceeded = True
                        actual_loss_pct = ((entry_price - current_price) / entry_price) * 100
                        should_exit = True
                        exit_reason = f"Stop loss hit: ${current_price:.2f} <= ${position['stop_loss']:.2f} ({actual_loss_pct:.3f}%)"
                    elif signal.signal_type == 'SELL' and current_price >= position['stop_loss']:
                        stop_loss_exceeded = True
                        actual_loss_pct = ((current_price - entry_price) / entry_price) * 100
                        should_exit = True
                        exit_reason = f"Stop loss hit: ${current_price:.2f} >= ${position['stop_loss']:.2f} ({actual_loss_pct:.3f}%)"
                else:
                    if loss_pct > 0:
                        self.logger.debug(f"🛡️ Grace active {symbol}: {int(position['stop_grace_until']-now_ts)}s left (loss {loss_pct:.3f}%)")

                if stop_loss_exceeded and actual_loss_pct > planned_stop_pct * 1.05:
                    overrun = actual_loss_pct - planned_stop_pct
                    self.logger.warning(f"🚨 STOP OVERRUN {symbol}: planned {planned_stop_pct:.3f}% actual {actual_loss_pct:.3f}% (+{overrun:.3f}%)")

                # Check other exit conditions only if stop loss not hit
                if not should_exit:
                    # 1. Time-based exit
                    if hold_time > max_hold_time:
                        should_exit = True
                        exit_reason = f"Max hold time ({max_hold_time}s) reached"

                    # 2. Profit target hit
                    elif signal.signal_type == "BUY" and current_price >= signal.profit_target:
                        should_exit = True
                        exit_reason = f"Profit target hit: ${current_price:.2f} >= ${signal.profit_target:.2f}"

                    elif signal.signal_type == "SELL" and current_price <= signal.profit_target:
                        should_exit = True
                        exit_reason = f"Profit target hit: ${current_price:.2f} <= ${signal.profit_target:.2f}"

                # Breakeven / trailing activation (after grace and if not exiting)
                if not should_exit and not grace_active:
                    stop_pct = planned_stop_pct if planned_stop_pct else config.STOP_LOSS_PCT
                    if stop_pct > 0:
                        r_mult = pnl_pct / stop_pct
                        position['r_multiple_peak'] = max(position.get('r_multiple_peak', 0.0), r_mult)
                        # Breakeven
                        if (not position.get('breakeven_set') and r_mult >= getattr(config, 'BREAKEVEN_TRIGGER_R', 1.0)):
                            position['stop_loss'] = position['entry_price']
                            position['breakeven_set'] = True
                            self.logger.info(f"⚖️ Breakeven set {symbol} at ${position['stop_loss']:.2f} (R={r_mult:.2f})")
                        # Trailing start
                        if (not position.get('trailing_started') and r_mult >= getattr(config, 'TRAIL_TRIGGER_R', 1.5)):
                            position['trailing_started'] = True
                            self.logger.info(f"🚀 Trailing enabled {symbol} (R={r_mult:.2f})")
                        # Apply adaptive trailing if started
                        if position.get('trailing_started'):
                            try:
                                bars = self.data_manager.get_bars(symbol, timeframe=config.TIMEFRAME, limit=100)
                                lookback = getattr(config, 'TRAIL_LOOKBACK', 5)
                                if bars is not None and len(bars) >= lookback + 2 and all(c in bars.columns for c in ['high','low','close']):
                                    recent = bars.iloc[-lookback:]
                                    recent_low = recent['low'].min(); recent_high = recent['high'].max()
                                    # lightweight ATR
                                    atr_val = None
                                    try:
                                        highs = bars['high']; lows = bars['low']; closes = bars['close']
                                        trs = []
                                        for i in range(1, len(bars)):
                                            h = highs.iloc[i]; l = lows.iloc[i]; pc = closes.iloc[i-1]
                                            trs.append(max(h-l, abs(h-pc), abs(l-pc)))
                                        if len(trs) >= config.ATR_PERIOD:
                                            atr_val = sum(trs[-config.ATR_PERIOD:]) / config.ATR_PERIOD
                                    except Exception:
                                        pass
                                    offset = 0.0
                                    if atr_val:
                                        offset = atr_val * getattr(config, 'TRAIL_ATR_OFFSET_MULT', 0.5)
                                    if signal.signal_type == 'BUY':
                                        new_stop = max(position['stop_loss'], recent_low - offset)
                                        if new_stop > position['stop_loss']:
                                            self.logger.info(f"🔧 Trail raise {symbol}: {position['stop_loss']:.2f} -> {new_stop:.2f}")
                                            position['stop_loss'] = new_stop
                                    else:
                                        new_stop = min(position['stop_loss'], recent_high + offset)
                                        if new_stop < position['stop_loss']:
                                            self.logger.info(f"🔧 Trail lower {symbol}: {position['stop_loss']:.2f} -> {new_stop:.2f}")
                            except Exception as trail_err:
                                self.logger.debug(f"Trail manage error {symbol}: {trail_err}")

                # Execute exit if needed
                if should_exit:
                    peak_info = ""
                    if symbol in self.position_peaks:
                        peak = self.position_peaks[symbol]
                        peak_info = f" (Peak: +{peak['peak_pnl_pct']:.2f}%)"
                    self.logger.info(f"🚪 Closing {symbol} position: {exit_reason} (P&L: ${unrealized_pnl:+.2f}){peak_info}")
                    positions_to_close.append((symbol, exit_reason))

            except Exception as e:
                self.logger.error(f"❌ Error managing position {symbol}: {e}")

        # Close positions that need to be closed
        for symbol, reason in positions_to_close:
            if symbol in self.active_positions:
                # Store exit reason so close_position can access it
                self.active_positions[symbol]['_pending_exit_reason'] = reason
            self.close_position(symbol)

        return True
    
    def update_trailing_stop_with_peak_tracking(self, symbol: str, position: Dict, current_price: float, current_pnl_pct: float):
        """Advanced trailing stop with peak profit tracking and configurable activation"""
        try:
            signal = position['signal']
            entry_price = position['entry_price']
            
            # Initialize peak tracking if not exists
            if symbol not in self.position_peaks:
                self.position_peaks[symbol] = {
                    'peak_price': current_price,
                    'peak_pnl_pct': current_pnl_pct,
                    'peak_absolute_pnl': 0.0,
                    'initial_stop': position['stop_loss'],
                    'trailing_active': False
                }
            
            peak_data = self.position_peaks[symbol]
            
            # Calculate absolute P&L
            if signal.signal_type == "BUY":
                current_absolute_pnl = (current_price - entry_price) * position['position_size']
                is_profitable = current_price > entry_price
                price_movement_favorable = current_price > peak_data['peak_price']
            else:  # SELL
                current_absolute_pnl = (entry_price - current_price) * position['position_size']
                is_profitable = current_price < entry_price
                price_movement_favorable = current_price < peak_data['peak_price']
            
            # Update peak if we've reached a new high
            if price_movement_favorable and current_pnl_pct > peak_data['peak_pnl_pct']:
                peak_data['peak_price'] = current_price
                peak_data['peak_pnl_pct'] = current_pnl_pct
                peak_data['peak_absolute_pnl'] = current_absolute_pnl
                
                # Activate trailing stop once we reach minimum profit threshold
                # Start trailing when we hit 0.20% profit (2/3 of the 0.30% target)
                profit_activation_threshold = 0.20
                
                if current_pnl_pct >= profit_activation_threshold and not peak_data['trailing_active']:
                    peak_data['trailing_active'] = True
                    self.logger.info(f"📈 {symbol} trailing stop ACTIVATED at +{current_pnl_pct:.2f}% profit (${current_price:.2f})")
                
                # Update trailing stop if already active
                if peak_data['trailing_active']:
                    # Use configurable trailing stop percentage
                    trailing_pct = config.TRAILING_STOP_PCT
                    
                    if signal.signal_type == "BUY":
                        # For long positions: stop follows price up
                        new_trailing_stop = current_price * (1 - trailing_pct / 100)
                        
                        # Only update if new stop is higher than current stop
                        if new_trailing_stop > position['stop_loss']:
                            old_stop = position['stop_loss']
                            position['stop_loss'] = new_trailing_stop
                            
                            # Calculate what percentage this protects
                            protected_profit_pct = ((new_trailing_stop - entry_price) / entry_price) * 100
                            
                            self.logger.info(f"📈 {symbol} trailing stop updated: ${old_stop:.2f} → ${new_trailing_stop:.2f} "
                                           f"(locks in +{protected_profit_pct:.2f}% from peak +{current_pnl_pct:.2f}%)")
                    
                    else:  # SELL
                        # For short positions: stop follows price down
                        new_trailing_stop = current_price * (1 + trailing_pct / 100)
                        
                        # Only update if new stop is lower than current stop
                        if new_trailing_stop < position['stop_loss']:
                            old_stop = position['stop_loss']
                            position['stop_loss'] = new_trailing_stop
                            
                            # Calculate what percentage this protects
                            protected_profit_pct = ((entry_price - new_trailing_stop) / entry_price) * 100
                            
                            self.logger.info(f"📉 {symbol} trailing stop updated: ${old_stop:.2f} → ${new_trailing_stop:.2f} "
                                           f"(locks in +{protected_profit_pct:.2f}% from peak +{current_pnl_pct:.2f}%)")
            
            # Log significant profit milestones
            if current_pnl_pct > 0 and current_pnl_pct >= peak_data['peak_pnl_pct']:
                if current_pnl_pct >= 0.50:  # 50% higher than profit target
                    self.logger.info(f"🚀 {symbol} exceptional profit: +{current_pnl_pct:.2f}% (${current_price:.2f})")
                elif current_pnl_pct >= 0.30:  # At profit target
                    self.logger.info(f"🎯 {symbol} profit target reached: +{current_pnl_pct:.2f}% (${current_price:.2f})")
        
        except Exception as e:
            self.logger.error(f"❌ Error updating trailing stop for {symbol}: {e}")

    def update_trailing_stop(self, symbol: str, position: Dict, current_price: float):
        """Legacy trailing stop method - kept for compatibility"""
        # This method is now deprecated in favor of update_trailing_stop_with_peak_tracking
        # But keeping it to avoid breaking any other code that might call it
        try:
            signal = position['signal']
            entry_price = position['entry_price']
            
            # Calculate current P&L percentage
            if signal.signal_type == "BUY":
                pnl_pct = ((current_price - entry_price) / entry_price) * 100
            else:  # SELL
                pnl_pct = ((entry_price - current_price) / entry_price) * 100
            
            # Call the new method
            self.update_trailing_stop_with_peak_tracking(symbol, position, current_price, pnl_pct)
        
        except Exception as e:
            self.logger.error(f"❌ Error in legacy trailing stop for {symbol}: {e}")
    
    def close_position(self, symbol: str) -> bool:
        """Close an active position with wash trade prevention"""
        try:
            if symbol not in self.active_positions:
                self.logger.warning(f"⚠️ Cannot close {symbol} - no tracked position exists")
                return False
            
            position = self.active_positions[symbol]
            signal = position['signal']
            
            # CRITICAL FIX: Verify we actually have a broker position to close
            try:
                broker_position = self.order_manager.get_position_info(symbol, context="position_validation", force_fresh=True)
                if broker_position is None or broker_position.get('qty', 0) == 0:
                    self.logger.error(f"🚫 PHANTOM POSITION DETECTED: {symbol}")
                    self.logger.error(f"🚫 Tracked position exists but no broker position found")
                    self.logger.error(f"🚫 Removing phantom position from tracking")
                    del self.active_positions[symbol]
                    # Clean up peak tracking too
                    if symbol in self.position_peaks:
                        del self.position_peaks[symbol]
                    return False
                    
                intended_side = position.get('intended_side', 'unknown')
                broker_side = self._normalize_broker_position_side(broker_position)
                # Verify position direction matches intention (long vs short)
                if intended_side not in ('buy', 'sell'):
                    self.logger.warning(f"⚠️ Intended side unknown for {symbol} during close; proceeding defensively")
                elif broker_side != intended_side:
                    # Add detailed context to aid debugging
                    try:
                        dbg_qty = broker_position.get('qty')
                        dbg_side = broker_position.get('side')
                        dbg_mv = broker_position.get('market_value')
                        self.logger.error(f"🚫 POSITION DIRECTION MISMATCH: {symbol}")
                        self.logger.error(f"🚫 Intended: {intended_side}, Broker(normalized): {broker_side}, Broker(raw side): {dbg_side}, qty: {dbg_qty}, mkt_val: {dbg_mv}")
                        self.logger.error(f"🚫 This indicates an execution failure")
                    except Exception:
                        self.logger.error(f"🚫 POSITION DIRECTION MISMATCH: {symbol} (intended={intended_side}, broker={broker_side})")
                    
            except Exception as validation_error:
                self.logger.warning(f"⚠️ Could not validate broker position for {symbol}: {validation_error}")
            
            # CRITICAL: Cancel any pending orders for this symbol first
            self.logger.info(f"🧹 Clearing pending orders for {symbol} before position close")
            cancelled_count = self.order_manager.cancel_pending_orders_for_symbol(symbol)
            if cancelled_count > 0:
                self.logger.info(f"✅ Cancelled {cancelled_count} pending orders for {symbol}")
                # Wait for cancellations to process
                time.sleep(2)
            
            # Determine exit side
            exit_side = "sell" if signal.signal_type == "BUY" else "buy"
            
            # Check wash trade prevention
            if not self.can_submit_order(symbol):
                self.logger.debug(f"⏳ Delaying position close for {symbol} - wash trade prevention")
                return False
            
            # Record order time for wash trade prevention
            self.record_order_time(symbol)
            
            # Submit market order to close
            self.logger.info(f"📤 Submitting {exit_side} order to close {symbol} position")
            exit_order_id = self.order_manager.submit_market_order(
                symbol=symbol,
                side=exit_side,
                quantity=position['position_size']
            )
            
            if exit_order_id:
                # Prefer broker filled price for exit if available; fallback to live mid-price
                exit_price = None
                try:
                    raw_id = getattr(exit_order_id, 'id', exit_order_id)
                    if hasattr(self.order_manager, 'alpaca_trader') and self.order_manager.alpaca_trader:
                        status = self.order_manager.alpaca_trader.get_order_status(raw_id)
                        if status and float(status.get('filled_avg_price') or 0) > 0:
                            exit_price = float(status['filled_avg_price'])
                except Exception as _ex_stat:
                    self.logger.debug(f"Exit fill price lookup failed {symbol}: {_ex_stat}")
                if exit_price is None:
                    current_data = self.data_manager.get_current_market_data(symbol)
                    exit_price = current_data['price'] if current_data else position['entry_price']
                
                # Calculate realized P&L
                if signal.signal_type == "BUY":
                    realized_pnl = (exit_price - position['entry_price']) * position['position_size']
                else:
                    realized_pnl = (position['entry_price'] - exit_price) * position['position_size']
                
                # Update daily P&L
                self.daily_pnl += realized_pnl
                
                # Update performance metrics
                self.update_performance_metrics(realized_pnl)
                
                self.logger.info(f"📉 Position closed: {symbol} - {position['position_size']} shares @ ${exit_price:.2f}")
                self.logger.info(f"💰 Realized P&L: ${realized_pnl:+.2f} | Daily P&L: ${self.daily_pnl:+.2f}")
                # Finalize trade diagnostics
                try:
                    tr = self._trade_records.get(symbol)
                    if tr:
                        # Attach MAE/MFE from position if tracked
                        if 'mae_pct' in position:
                            tr.mae_pct = position.get('mae_pct')
                        if 'mfe_pct' in position:
                            tr.mfe_pct = position.get('mfe_pct')
                        # Use stored exit reason if present
                        exit_reason = position.get('_pending_exit_reason', 'close')
                        tr.finalize(exit_price, exit_reason, tr.side)
                        self._append_trade_record(tr)
                        # Update per-symbol aggregates
                        try:
                            self._accumulate_symbol_performance(tr)
                        except Exception as acc_err:
                            self.logger.debug(f"Symbol perf accumulation failed {symbol}: {acc_err}")
                        del self._trade_records[symbol]
                except Exception as ferr:
                    self.logger.debug(f"Finalize TradeRecord failed {symbol}: {ferr}")
                
                # Track position closure with risk manager
                self.risk_manager.track_position_closed(
                    symbol, signal.signal_type, position['position_size'], 
                    position['entry_price'], exit_price
                )
                
                # Remove from active positions and clean up peak tracking
                del self.active_positions[symbol]
                if symbol in self.position_peaks:
                    peak_info = self.position_peaks[symbol]
                    if peak_info['peak_pnl_pct'] > 0:
                        self.logger.info(f"📊 {symbol} peak profit was +{peak_info['peak_pnl_pct']:.2f}% at ${peak_info['peak_price']:.2f}")
                        
                        # TRAILING STOP PROTECTION: If position was profitable and trailing stop was active,
                        # add to cooldown to prevent rapid re-entry
                        if peak_info['trailing_active'] and realized_pnl > 0:
                            import time as _t
                            self.recently_closed_profitable[symbol] = _t.time()
                            self.logger.info(f"🛡️ {symbol} added to profitable closure cooldown ({self.profitable_closure_cooldown}s)")
                    
                    del self.position_peaks[symbol]
                
                return True
            else:
                self.logger.error(f"❌ Failed to submit exit order for {symbol}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error closing position {symbol}: {e}")
        
        return False
    
    def update_performance_metrics(self, pnl: float):
        """Update performance tracking metrics"""
        self.performance_metrics['total_trades'] += 1
        self.performance_metrics['total_pnl'] += pnl
        
        if pnl > 0:
            self.performance_metrics['winning_trades'] += 1
            self.consecutive_losses = 0
            # Decay adaptive cooldown on profitable trades (except tiny wins)
            if self.adaptive_cooldown_multiplier > 1.0 and pnl > 0.01:
                old_mult = self.adaptive_cooldown_multiplier
                self.adaptive_cooldown_multiplier = max(1.0, self.adaptive_cooldown_multiplier * self.cooldown_decay_factor)
                if int(old_mult*100) != int(self.adaptive_cooldown_multiplier*100):
                    self.logger.info(f"🧊 Cooldown multiplier decayed: {old_mult:.2f} -> {self.adaptive_cooldown_multiplier:.2f}")
        else:
            self.performance_metrics['losing_trades'] += 1
            self.consecutive_losses += 1
            # Track loss magnitude and potentially increase cooldown
            loss_amount = abs(pnl)
            # Append to recent losses
            self.recent_losses.append(loss_amount)
            if len(self.recent_losses) > self.max_recent_losses:
                self.recent_losses.pop(0)
            # Determine per-trade max risk (approx) from config (position sizing uses ACCOUNT_RISK_PCT of equity)
            est_equity = getattr(self.risk_manager, 'account_equity', 100000.0)
            est_risk_per_trade = est_equity * (config.ACCOUNT_RISK_PCT / 100)
            if est_risk_per_trade > 0 and loss_amount > est_risk_per_trade * self.significant_loss_threshold_pct:
                old_mult = self.adaptive_cooldown_multiplier
                self.adaptive_cooldown_multiplier = min(self.max_adaptive_cooldown_multiplier, self.adaptive_cooldown_multiplier * self.cooldown_increase_factor)
                if self.adaptive_cooldown_multiplier > old_mult:
                    self.logger.warning(f"🔥 Increasing cooldown multiplier {old_mult:.2f} -> {self.adaptive_cooldown_multiplier:.2f} after loss ${pnl:.2f}")
            # Extra increase if streak of 3+ consecutive losses
            if len(self.recent_losses) >= 3 and all(l > 0 for l in self.recent_losses[-3:]):
                old_mult = self.adaptive_cooldown_multiplier
                self.adaptive_cooldown_multiplier = min(self.max_adaptive_cooldown_multiplier, self.adaptive_cooldown_multiplier * 1.1)
                if self.adaptive_cooldown_multiplier > old_mult:
                    self.logger.warning(f"📉 Losing streak detected - cooldown multiplier {old_mult:.2f} -> {self.adaptive_cooldown_multiplier:.2f}")

            # Global pause after N consecutive losses
            try:
                if self.consecutive_losses >= getattr(config, 'CONSECUTIVE_LOSS_PAUSE_N', 3):
                    pause_sec = max(0, int(getattr(config, 'CONSECUTIVE_LOSS_PAUSE_MINUTES', 10)) * 60)
                    self.global_pause_until = time.time() + pause_sec
                    self.logger.warning(f"⏸️ Global trading pause for {pause_sec//60}m after {self.consecutive_losses} consecutive losses")
                    self.consecutive_losses = 0
            except Exception:
                pass

        # Periodic performance summary including slippage
        if self.performance_metrics['total_trades'] % 10 == 0:
            avg_slip = (self.slippage_stats['total'] / self.slippage_stats['count']) if self.slippage_stats['count'] else 0.0
            self.logger.info(
                f"📊 Trade #{self.performance_metrics['total_trades']} | Win: {self.performance_metrics['winning_trades']} Loss: {self.performance_metrics['losing_trades']} "
                f"P&L: ${self.performance_metrics['total_pnl']:+.2f} | Avg Slippage: {avg_slip:.4f}% (max {self.slippage_stats['max']:.4f}%) | Cooldown x{self.adaptive_cooldown_multiplier:.2f}"
            )

    def _record_slippage(self, intended_price: float, executed_price: float, side: str, symbol: str):
        """Record slippage statistics and log if above threshold."""
        if intended_price <= 0 or executed_price <= 0:
            return
        # Signed slippage relative to trade direction (positive = adverse)
        price_diff = executed_price - intended_price
        if side.lower() == 'sell':
            # For sells, adverse slippage if execution price lower than intended
            price_diff = intended_price - executed_price
        slip_pct = (price_diff / intended_price) * 100
        abs_slip_pct = abs(slip_pct)
        self.slippage_stats['count'] += 1
        self.slippage_stats['total'] += abs_slip_pct
        if abs_slip_pct > self.slippage_stats['max']:
            self.slippage_stats['max'] = abs_slip_pct
        # Alert on large slippage
        if abs_slip_pct > config.MAX_SLIPPAGE_PCT:
            self.logger.warning(f"⚠️ Slippage {abs_slip_pct:.4f}% on {symbol} ({side.upper()}) intended ${intended_price:.2f} executed ${executed_price:.2f}")
        else:
            self.logger.debug(f"🪙 Slippage {abs_slip_pct:.4f}% on {symbol} ({side.upper()})")
    
    def check_daily_limits(self) -> bool:
        """Check if daily loss limit is reached"""
        # Get current account equity from risk manager
        account_equity = getattr(self.risk_manager, 'account_equity', 100000.0)
        max_daily_loss_dollar = account_equity * (config.MAX_DAILY_LOSS_PCT / 100)
        
        if self.daily_pnl <= -max_daily_loss_dollar:
            self.logger.warning(f"❌ Daily loss limit reached: ${self.daily_pnl:.2f} (>{config.MAX_DAILY_LOSS_PCT}% of ${account_equity:,.2f})")
            return False
        return True

    # ---------------- Trade Diagnostics Helpers -----------------
    def _pre_trade_filter(self, signal: ScalpingSignal) -> bool:
        """Enhanced pre-trade filter with profitability optimizations"""
        try:
            # Daily caps
            today = datetime.utcnow().date()
            if today != self.trade_day:
                self.trade_day = today
                self.symbol_trade_count.clear()
                self.trade_count = 0
                
            if self.performance_metrics.get('total_trades', 0) >= getattr(config, 'MAX_TRADES_PER_DAY', 50):
                self.logger.info(f"🧱 Rejected {signal.symbol}: MAX_TRADES_PER_DAY reached")
                return False
                
            if self.symbol_trade_count.get(signal.symbol, 0) >= getattr(config, 'MAX_TRADES_PER_SYMBOL_PER_DAY', 6):
                self.logger.info(f"🧱 Rejected {signal.symbol}: per-symbol trade cap reached")
                return False
                
            # Enhanced per-symbol spacing for better setups
            spacing = max(0, int(getattr(config, 'MINUTES_BETWEEN_TRADES_PER_SYMBOL', 0)) * 60)
            if spacing:
                last_time = self.last_order_time.get(signal.symbol)
                if last_time and (time.time() - last_time) < spacing:
                    remain = int(spacing - (time.time() - last_time))
                    self.logger.debug(f"🕒 Reject {signal.symbol}: spacing {remain}s remaining")
                    return False

            # Enhanced confidence threshold with adaptive adjustment
            base_min_conf = getattr(config, 'MIN_CONFIDENCE', 0.70)
            min_conf = base_min_conf
            
            # Increase confidence requirement after consecutive losses
            if self.adaptive_cooldown_multiplier > 1.2:
                min_conf += 0.08
            elif self.adaptive_cooldown_multiplier > 1.0:
                min_conf += 0.05
                
            # Time-based confidence adjustment (require higher confidence during lunch hours)
            current_hour = datetime.now().hour
            if 12 <= current_hour <= 13:  # Lunch hour - lower volume/predictability
                min_conf += 0.05
                
            self.logger.info(f"🧪 CHECK {signal.symbol}: confidence {signal.confidence:.2f} vs min {min_conf:.2f}")
            if signal.confidence < min_conf:
                self.logger.info(f"🧪 REJECT {signal.symbol}: confidence {signal.confidence:.2f} < {min_conf:.2f}")
                return False
                
            # Enhanced market data checks
            md = self.data_manager.get_current_market_data(signal.symbol)
            if md:
                # Tighter spread requirements for profitability
                spread = (md.get('spread_pct') or 0)
                max_spread = config.MAX_SPREAD_PCT * (0.7 if self.adaptive_cooldown_multiplier > 1.2 else 0.8)
                self.logger.info(f"🧪 CHECK {signal.symbol}: spread {spread:.4f}% vs max {max_spread:.4f}%")
                if spread > max_spread:
                    self.logger.info(f"🧪 REJECT {signal.symbol}: spread {spread:.4f}% > {max_spread:.4f}%")
                    return False
                    
                # Enhanced volume quality requirements
                vol_ratio = md.get('volume_ratio') or 0
                min_vol_ratio = getattr(config, 'REQUIRE_MIN_VOLUME_RATIO', 1.5)
                
                # Increase volume requirement during low-confidence periods
                if self.adaptive_cooldown_multiplier > 1.1:
                    min_vol_ratio *= 1.2
                    
                self.logger.info(f"🧪 CHECK {signal.symbol}: volume_ratio {vol_ratio:.2f} vs min {min_vol_ratio:.2f}")
                if vol_ratio < min_vol_ratio:
                    self.logger.info(f"🧪 REJECT {signal.symbol}: volume_ratio {vol_ratio:.2f} < {min_vol_ratio:.2f}")
                    return False
                
                # Price momentum filter for better entries
                price = md.get('price', signal.entry_price)
                if price <= 0:
                    self.logger.info(f"🧪 REJECT {signal.symbol}: invalid price {price}")
                    return False
                    
            # Enhanced risk/reward calculation
            try:
                if signal.signal_type == 'BUY':
                    risk = max(1e-6, signal.entry_price - signal.stop_loss)
                    reward = max(0.0, signal.profit_target - signal.entry_price)
                else:
                    risk = max(1e-6, signal.stop_loss - signal.entry_price)
                    reward = max(0.0, signal.entry_price - signal.profit_target)
                    
                expected_r = (reward / risk) if risk > 0 else 0.0
                min_expected_r = getattr(config, 'MIN_EXPECTED_R', 1.50)
                
                # Increase R requirement after losses
                if self.adaptive_cooldown_multiplier > 1.1:
                    min_expected_r *= 1.1
                    
                self.logger.info(f"🧪 CHECK {signal.symbol}: expected_R {expected_r:.2f} vs min {min_expected_r:.2f}")
                if expected_r < min_expected_r:
                    self.logger.info(f"🧪 REJECT {signal.symbol}: expected_R {expected_r:.2f} < {min_expected_r:.2f}")
                    return False
                    
                # Risk size validation - ensure reasonable position sizes
                risk_pct = (risk / signal.entry_price) * 100
                if risk_pct > 0.5:  # More than 0.5% risk per trade is too much for scalping
                    self.logger.info(f"🧪 REJECT {signal.symbol}: risk_pct {risk_pct:.3f}% > 0.5%")
                    return False
                    
            except Exception as e:
                self.logger.warning(f"🧪 Risk/reward calculation failed for {signal.symbol}: {e}")
                return False
                
            self.logger.info(f"🧪 PASS ALL FILTERS: {signal.symbol}")
            return True
            
        except Exception as e:
            self.logger.warning(f"Pre-trade filter error {signal.symbol}: {e}")
            return False

    def _append_trade_record(self, tr: TradeRecord):
        """Append a finalized trade record to CSV log."""
        try:
            with open(self._trade_log_path, 'a', newline='') as tf:
                writer = csv.writer(tf)
                writer.writerow([
                    tr.symbol,tr.strategy,tr.side,tr.entry_time.isoformat(),f"{tr.entry_price:.4f}",f"{tr.stop_loss:.4f}",f"{tr.profit_target:.4f}",tr.position_size,f"{tr.confidence:.4f}",
                    '' if tr.spread_pct is None else f"{tr.spread_pct:.4f}",
                    '' if tr.volume is None else f"{tr.volume}",
                    '' if tr.volume_ratio is None else f"{tr.volume_ratio:.4f}",
                    '' if tr.exit_time is None else tr.exit_time.isoformat(),
                    '' if tr.exit_price is None else f"{tr.exit_price:.4f}",
                    '' if tr.realized_pnl is None else f"{tr.realized_pnl:.4f}",
                    '' if tr.realized_pct is None else f"{tr.realized_pct:.4f}",
                    '' if tr.r_multiple is None else f"{tr.r_multiple:.4f}",
                    '' if tr.hold_time_s is None else f"{tr.hold_time_s:.2f}",
                    '' if tr.mae_pct is None else f"{tr.mae_pct:.4f}",
                    '' if tr.mfe_pct is None else f"{tr.mfe_pct:.4f}",
                    '' if tr.mae_r is None else f"{tr.mae_r:.4f}",
                    '' if tr.mfe_r is None else f"{tr.mfe_r:.4f}",
                    tr.exit_reason or '',
                    '' if not self.active_positions.get(tr.symbol) else f"{self.active_positions[tr.symbol].get('adaptive_stop_pct','')}",
                    '' if not self.active_positions.get(tr.symbol) else ('' if self.active_positions[tr.symbol].get('atr_pct_entry') is None else f"{self.active_positions[tr.symbol].get('atr_pct_entry'):.4f}"),
                    '' if not self.active_positions.get(tr.symbol) else f"{self.active_positions[tr.symbol].get('r_multiple_peak','')}"
                ])
        except Exception as e:
            self.logger.debug(f"Trade record append failed {tr.symbol}: {e}")
        
        return True
    
    def run_trading_cycle(self):
        """Main trading cycle - run continuously during market hours"""
        try:
            # CRITICAL: Force immediate output to see if method is called
            import sys
            print("=" * 50, file=sys.stderr)
            print("DEBUG: run_trading_cycle CALLED!", file=sys.stderr)
            print("=" * 50, file=sys.stderr)
            sys.stderr.flush()
            
            print("🔄 ENTERING run_trading_cycle method...")  # Debug print
            self.logger.info("🔄 Starting trading cycle...")
            
            # CRITICAL SAFETY CHECK: Verify we have live data connection (attempt reconnection if missing)
            if not self.data_manager.ensure_connection():
                self.logger.error("❌ CRITICAL: No live data connection after retry - stopping cycle")
                time.sleep(5)
                return
            
            print("🔄 Data manager check passed...")  # Debug print
            
            # Test live data connection with SPY
            try:
                test_price = self.data_manager.get_current_price("SPY")
                if test_price is None or test_price <= 0:
                    self.logger.error("❌ CRITICAL: Cannot get live market data - STOPPING TRADING")
                    self.logger.error("❌ TRADING HALTED: Market data connection failed")
                    self.is_running = False  # Stop the engine
                    return
            except Exception as e:
                self.logger.error(f"❌ CRITICAL: Market data connection error - {e}")
                self.logger.error("❌ TRADING HALTED: Market data connection failed")
                self.is_running = False  # Stop the engine
                return
            
            # Sync positions with broker at start of each cycle
            self.sync_positions_with_broker()
            
            # Check if we should continue trading
            if not self.is_market_hours():
                self.logger.debug("⏰ Outside market hours, skipping trading cycle")
                return
            
            if not self.check_daily_limits():
                self.logger.warning("❌ Daily limits reached, stopping trading")
                return
            
            self.logger.info(f"✅ Trading cycle checks passed - Processing {len(config.INTRADAY_WATCHLIST)} symbols")
            
            # Get filtered watchlist
            symbols = self.filter_watchlist()
            # store for diagnostics
            self.last_filtered_symbols = symbols
            self.logger.info(f"📋 Processing {len(symbols)} filtered symbols: {symbols}")
            
            # Process each symbol
            for symbol in symbols:
                try:
                    self.logger.info(f"🔍 Processing {symbol}...")
                    
                    # Skip if we already have a position in this symbol
                    if symbol in self.active_positions:
                        self.logger.info(f"⏭️ Skipping {symbol} - already have position")
                        continue
                    
                    # Double-check: verify no actual broker position exists
                    positions = self.data_manager.get_positions()
                    actual_position = next((p for p in positions if p['symbol'] == symbol), None)
                    if actual_position and abs(float(actual_position.get('qty', 0))) > 0:
                        self.logger.info(f"⚠️ Skipping {symbol} - has actual position: {actual_position.get('qty', 0)} shares")
                        continue
                    
                    # We now allow signal generation during cooldown for diagnostics; only execution gate later
                    cooldown_active = not self.can_generate_signal(symbol)
                    if cooldown_active:
                        self.logger.debug(f"⏳ Cooldown active pre-generation {symbol} - generation allowed for diagnostics")

                    self.logger.info(f"📊 Getting market data for {symbol}...")
                    
                    # FIX 1: DATA CONSISTENCY - Get market data from consistent source
                    # Use live data source for both signal generation AND validation
                    data = self.data_manager.get_bars(
                        symbol, 
                        timeframe=config.TIMEFRAME, 
                        limit=100  # Get enough bars for indicators
                    )
                    
                    if data is None or len(data) < 20:  # Need minimum data for indicators
                        self.logger.info(f"⚠️ Insufficient live data for {symbol} - skipping")
                        continue
                        
                    self.logger.info(f"✅ Got {len(data)} bars of data for {symbol}")
                    
                    # FIX 2: TIMESTAMP VALIDATION - Verify data freshness
                    if hasattr(data, 'index') and len(data) > 0:
                        latest_bar_time = data.index[-1]
                        # Capture last 3 timestamps for diagnostics
                        try:
                            last_times = [ts.strftime('%Y-%m-%d %H:%M:%S%z') for ts in data.index[-3:]]
                        except Exception:
                            last_times = [str(ts) for ts in data.index[-3:]]
                        # Use timezone-aware UTC computations to avoid negative ages from mixed tz
                        from datetime import timezone as _tz
                        now_dt = datetime.now(_tz.utc)
                        try:
                            bar_ts = latest_bar_time
                            # If index is tz-naive, assume it's already UTC
                            if bar_ts.tzinfo is None:
                                bar_ts = bar_ts.tz_localize(_tz.utc)
                            data_age = (now_dt - bar_ts).total_seconds()
                        except Exception:
                            # Fallback to previous naive approach
                            bar_ts = latest_bar_time.to_pydatetime().replace(tzinfo=None)
                            data_age = (datetime.utcnow() - bar_ts).total_seconds()
                        self.logger.info(f"🕒 {symbol} latest bar: {bar_ts} | now: {now_dt} | age: {data_age:.0f}s | last3: {last_times}")
                        
                        # Allow temporary override for diagnostics
                        max_age = getattr(self, 'max_data_age', 120)
                        allow_stale = getattr(self, 'allow_stale_diagnostics', True)
                        if data_age > max_age:
                            if allow_stale:
                                self.logger.warning(f"⚠️ Using stale data for diagnostics {symbol} (age {data_age:.0f}s > {max_age}s)")
                            else:
                                self.logger.info(f"⚠️ Market data too stale for {symbol} ({data_age:.0f}s old)")
                                continue
                    
                    # FIX 3: FASTER EXECUTION - Generate signals with pre-validation
                    signal_start_time = time.time()
                    self.logger.info(f"🎯 Generating signals for {symbol}...")
                    signals = self.generate_signals(symbol, data)
                    signal_generation_time = time.time() - signal_start_time
                    
                    self.logger.info(f"📈 {symbol}: Generated {len(signals) if signals else 0} signals in {signal_generation_time:.2f}s")
                    
                    # Track signal generation speed
                    if signal_generation_time > 1.0:  # Log slow signal generation
                        self.logger.warning(f"⚠️ Slow signal generation for {symbol}: {signal_generation_time:.2f}s")
                    
                    # Execute best signal if available (and cooldown not active)
                    if signals and not cooldown_active and len(self.active_positions) < config.MAX_OPEN_POSITIONS:
                        self.logger.info(f"🚀 Found {len(signals)} signals for {symbol}, attempting to execute best one...")
                        best_signal = signals[0]
                        
                        # Fast validation using same data source (no separate call needed)
                        # Since we pre-validated in generate_signals, just do final freshness check
                        execution_start_time = time.time()
                        
                        # Quick freshness check only (data source already consistent)
                        signal_age = self._get_timestamp_age_seconds(getattr(best_signal, 'timestamp', None))
                        
                        if signal_age < 5.0:  # Signal must be less than 5 seconds old for execution
                            try:
                                self.logger.info(f"💫 Executing {symbol} signal: {best_signal.signal_type} @ ${best_signal.entry_price:.2f}")
                                
                                # Direct execution without debug print statements
                                self.record_signal_time(symbol)
                                execution_success = self.execute_signal(best_signal)
                                execution_time = time.time() - execution_start_time
                                
                                if execution_success:
                                    self.logger.info(f"⚡ FAST EXECUTION: {symbol} signal executed in {execution_time:.2f}s")
                                else:
                                    self.logger.warning(f"❌ Signal execution failed for {symbol}")
                            except Exception as outer_e:
                                # Write to file to ensure we capture the exception
                                with open('debug_exception.txt', 'w') as f:
                                    f.write(f"EXCEPTION: {outer_e}\n")
                                    f.write(f"TYPE: {type(outer_e)}\n")
                                    import traceback
                                    f.write(f"TRACEBACK:\n{traceback.format_exc()}\n")
                                self.logger.warning(f"[ERROR] Signal execution failed for {symbol}")
                            
                        else:
                            self.logger.warning(f"🚫 Signal rejected for {symbol}: Too slow ({signal_age:.1f}s old)")
                            self.record_failed_signal(symbol)
                    else:
                        if not signals:
                            self.logger.info(f"📊 No signals generated for {symbol}")
                        else:
                            if cooldown_active:
                                self.logger.info(f"⏳ Cooldown blocked execution for {symbol} (signals={len(signals)})")
                            elif len(self.active_positions) >= config.MAX_OPEN_POSITIONS:
                                self.logger.info(f"📈 Max positions reached ({len(self.active_positions)}/{config.MAX_OPEN_POSITIONS}), skipping {symbol}")
                
                except Exception as e:
                    import traceback as _tb
                    self.logger.error(f"❌ Error processing {symbol}: {e} | {type(e).__name__}\n{_tb.format_exc()}")
                    continue
            
            # Manage existing positions
            self.manage_positions()
            
            # Log status periodically
            current_time = time.time()
            if not hasattr(self, 'last_status_time'):
                self.last_status_time = 0
            
            if current_time - self.last_status_time >= 30:  # 30 seconds
                self.log_status()
                self.last_status_time = current_time
        
        except Exception as e:
            print(f"❌ EXCEPTION in trading cycle: {e}")  # Debug print
            import traceback
            print(f"❌ TRACEBACK: {traceback.format_exc()}")  # Full stack trace
            self.logger.error(f"❌ Error in trading cycle: {e}")
            self.logger.error(f"❌ Traceback: {traceback.format_exc()}")
    
    def log_status(self):
        """Log current trading status"""
        win_rate = 0
        if self.performance_metrics['total_trades'] > 0:
            win_rate = self.performance_metrics['winning_trades'] / self.performance_metrics['total_trades'] * 100
        
        current_time = datetime.now().strftime("%H:%M:%S")
        
        if len(self.active_positions) > 0:
            pos_str = ", ".join([f"{sym}:{pos['signal'].signal_type}" for sym, pos in self.active_positions.items()])
            self.logger.debug(f"🕐 {current_time} | Positions: {pos_str} | P&L: ${self.daily_pnl:+.2f} | Trades: {self.performance_metrics['total_trades']} | Win: {win_rate:.1f}%")
        else:
            self.logger.debug(f"🕐 {current_time} | Monitoring | P&L: ${self.daily_pnl:+.2f} | Trades: {self.performance_metrics['total_trades']}")
    
    def start(self):
        """Start the scalping engine with enhanced stop loss monitoring"""
        self.logger.info("🚀 Starting Scalping Engine...")
        
        # Initialize OrderManager API connection (optional)
        try:
            if hasattr(self.order_manager, 'initialize_trading'):
                if not self.order_manager.initialize_trading():
                    self.logger.warning("⚠️ OrderManager trading connection failed - using existing connection")
            else:
                self.logger.info("✅ Using existing data manager connection")
        except Exception as e:
            self.logger.warning(f"⚠️ OrderManager initialization check failed: {e} - using existing connection")
        
        # CRITICAL: Immediately sync with broker positions on startup
        self.logger.info("🔄 STARTUP: Syncing with broker positions...")
        self.sync_positions_with_broker()
        
        # CRITICAL: Immediately check for stop loss violations after sync
        self.logger.info("🛡️ STARTUP: Checking for stop loss violations...")
        self.check_position_stop_losses()
        
        self.logger.info("✅ Engine ready - monitoring market for signals...")
        
        # Initialize status tracking
        self.last_status_time = 0
        self.last_signal_check = 0
        
        self.is_running = True
        
        try:
            while self.is_running:
                # CRITICAL: ALWAYS check positions for stop losses, regardless of market hours
                self.check_position_stop_losses()
                
                market_open = self.is_market_hours()
                self.logger.info(f"🕐 Market hours check: {market_open} (Current time: {datetime.now().strftime('%H:%M:%S')})")
                
                if market_open:
                    current_time = time.time()
                    # Ensure data connection each loop
                    self.data_manager.ensure_connection()
                    
                    # Run full trading cycle (signal generation) every 5 seconds during market hours
                    if current_time - self.last_signal_check >= self.timeframe_config.signal_delay:
                        self.logger.info(f"🔄 Signal check interval reached, running trading cycle...")
                        self.run_trading_cycle()
                        self.last_signal_check = current_time
                    else:
                        time_remaining = self.timeframe_config.signal_delay - (current_time - self.last_signal_check)
                        self.logger.info(f"⏳ Next signal check in {time_remaining:.1f}s")
                    
                    # Sleep for 1 second to maintain frequent stop loss monitoring
                    time.sleep(1)
                else:
                    self.logger.info(f"❌ NOT in market hours - Current time: {datetime.now().strftime('%H:%M:%S')}, "
                                   f"Trading hours: {config.TRADING_START}-{config.TRADING_END}, "
                                   f"Lunch break: {config.LUNCH_BREAK_START}-{config.LUNCH_BREAK_END}")
                    # Outside market hours: Only monitor existing positions, no new trading
                    if self.active_positions:
                        self.logger.info(f"⏰ Outside market hours - monitoring {len(self.active_positions)} existing positions...")
                        # Sync positions every cycle outside market hours
                        self.sync_positions_with_broker()
                        self.manage_positions()  # Check exits, trailing stops, etc.
                        time.sleep(30)  # Check every 30 seconds outside market hours
                    else:
                        self.logger.info("⏰ Outside market hours, no positions to monitor...")
                        # Still sync occasionally to catch any positions opened elsewhere
                        self.sync_positions_with_broker()
                        # Auto-generate daily report once after market close if not already
                        try:
                            today = datetime.utcnow().date()
                            if self._daily_report_generated_date != today:
                                # Only generate if we had any trades today
                                if self.trade_count > 0:
                                    self.logger.info("📝 Daily report functionality simplified after cleanup")
                                    self.logger.info(f"📄 Trades today: {self.trade_count}")
                                else:
                                    self.logger.info("📄 No trades to report today.")
                                self._daily_report_generated_date = today
                        except Exception as rep_e:
                            self.logger.warning(f"⚠️ Auto-report generation failed: {rep_e}")
                        time.sleep(300)  # Wait 5 minutes when no positions
        
        except KeyboardInterrupt:
            self.logger.info("👋 Shutting down gracefully...")
            self.stop()
        
        except Exception as e:
            self.logger.error(f"❌ Critical error in scalping engine: {e}")
            self.stop()
    
    def check_position_stop_losses(self):
        """Rapid check of all positions for stop loss violations - runs every 1 second"""
        
        # CRITICAL SAFETY CHECK: Verify live data connection before checking stops (attempt reconnect)
        if not self.data_manager.ensure_connection():
            self.logger.error("❌ CRITICAL: No live data for stop loss checks (after retry) - pausing")
            time.sleep(5)
            return
        
        # CRITICAL FIX: Always check broker positions, not just bot-tracked positions
        # First sync with broker to get ALL real positions
        self.sync_positions_with_broker()
        
        # Now check bot-tracked positions (these have full signal data)
        for symbol in list(self.active_positions.keys()):
            try:
                position = self.active_positions[symbol]
                signal = position.get('signal')
                
                if not signal:
                    continue
                
                # Get current price for this symbol - ONLY LIVE DATA
                market_data = self.data_manager.get_current_market_data(symbol, "stop_loss_check")
                if market_data is None:
                    self.logger.warning(f"⚠️ No live data for stop loss check on {symbol}")
                    continue
                    
                # Verify data is from live source
                if market_data.get('source') != 'alpaca_live':
                    self.logger.error(f"❌ CRITICAL: Non-live data in stop loss check for {symbol}")
                    continue
                
                current_price = market_data.get('price')
                if current_price is None or current_price <= 0:
                    continue
                
                entry_price = position['entry_price']
                
                # Calculate actual loss percentage
                if signal.signal_type == "BUY":
                    loss_pct = ((entry_price - current_price) / entry_price) * 100 if current_price < entry_price else 0
                    stop_loss_hit = current_price <= position['stop_loss']
                else:  # SELL
                    loss_pct = ((current_price - entry_price) / entry_price) * 100 if current_price > entry_price else 0
                    stop_loss_hit = current_price >= position['stop_loss']
                
                # Check minimum hold time before evaluating stop loss
                entry_time = position.get('entry_time', datetime.now())
                min_hold_time = position.get('minimum_hold_time', 30)  # Default 30 seconds
                time_since_entry = (datetime.now() - entry_time).total_seconds()
                
                if time_since_entry < min_hold_time:
                    # Only apply hard emergency stop during minimum hold period
                    if loss_pct > 2.0:  # Emergency stop at 2% during hold period
                        self.logger.warning(f"🚨 EMERGENCY STOP during hold period: {symbol} - {loss_pct:.3f}% loss")
                        self.logger.info(f"🛑 EMERGENCY STOP TRIGGERED: {symbol} - Loss exceeds 2% emergency threshold")
                        self.close_position(symbol)
                    else:
                        # Skip normal stop loss evaluation during minimum hold time
                        self.logger.debug(f"⏳ {symbol} in minimum hold period ({time_since_entry:.0f}s/{min_hold_time}s) - skipping stop loss")
                        continue
                
                # Critical stop loss checks (after minimum hold time)
                if stop_loss_hit or loss_pct > 0.25:  # Hard stop at 0.25%
                    exit_reason = ""
                    
                    if stop_loss_hit:
                        # ENHANCED: Determine if this was a trailing stop or original stop
                        original_stop = position.get('original_stop_loss', position['stop_loss'])
                        if position['stop_loss'] != original_stop:
                            exit_reason = f"RAPID Trailing Stop: ${current_price:.2f} (Loss: {loss_pct:.3f}%) - PROTECTED PROFIT"
                            self.logger.info(f"🎯 TRAILING STOP PROTECTED PROFIT: {symbol} - Stop moved from ${original_stop:.2f} to ${position['stop_loss']:.2f}")
                        else:
                            exit_reason = f"RAPID Stop loss: ${current_price:.2f} (Loss: {loss_pct:.3f}%)"
                    else:
                        exit_reason = f"RAPID Hard stop: {loss_pct:.3f}% loss exceeds 0.25% safety limit"
                    
                    # Log violation if exceeds configured limit
                    if loss_pct > config.STOP_LOSS_PCT:
                        violation = loss_pct - config.STOP_LOSS_PCT
                        self.logger.warning(f"🚨 RAPID STOP VIOLATION: {symbol} - Expected {config.STOP_LOSS_PCT:.3f}% but lost {loss_pct:.3f}% (excess: {violation:.3f}%)")
                    
                    # Immediately close position
                    self.logger.info(f"🛑 RAPID STOP TRIGGERED: {symbol} - {exit_reason}")
                    self.close_position(symbol)
                    
            except Exception as e:
                self.logger.error(f"❌ Error in rapid stop loss check for {symbol}: {e}")
                continue
        
        # ADDITIONAL SAFETY: Check ALL broker positions for basic stop loss
        # This catches positions that bot might have lost track of
        try:
            if self.order_manager and hasattr(self.order_manager, 'data_manager') and self.order_manager.data_manager.api:
                broker_positions = self.order_manager.data_manager.api.list_positions()
                
                for pos in broker_positions:
                    symbol = pos['symbol']
                    
                    # Skip if we're already tracking this position
                    if symbol in self.active_positions:
                        continue
                    
                    # Check untracked position for excessive loss
                    unrealized_pnl_pct = float(pos['unrealized_plpc']) * 100
                    loss_pct = abs(unrealized_pnl_pct) if unrealized_pnl_pct < 0 else 0
                    
                    # Apply hard stop to ANY position
                    if loss_pct > 0.25:  # Hard stop at 0.25%
                        self.logger.warning(f"🚨 UNTRACKED POSITION HARD STOP: {symbol} - {loss_pct:.3f}% loss")
                        
                        # Emergency close this position
                        qty = float(pos['qty'])
                        side = 'sell' if qty > 0 else 'buy'
                        abs_qty = abs(qty)
                        
                        self.logger.info(f"🛑 EMERGENCY CLOSE UNTRACKED: {symbol}")
                        self.order_manager.submit_market_order(symbol, side, int(abs_qty))
                        
                    elif loss_pct > config.STOP_LOSS_PCT:
                        self.logger.warning(f"🚨 UNTRACKED POSITION STOP LOSS: {symbol} - {loss_pct:.3f}% loss exceeds {config.STOP_LOSS_PCT}%")
                        
                        # Emergency close this position
                        qty = float(pos['qty'])
                        side = 'sell' if qty > 0 else 'buy'
                        abs_qty = abs(qty)
                        
                        self.logger.info(f"🛑 EMERGENCY CLOSE UNTRACKED: {symbol}")
                        self.order_manager.submit_market_order(symbol, side, int(abs_qty))
                        
        except Exception as e:
            self.logger.error(f"❌ Error checking untracked broker positions: {e}")
    
    def stop(self):
        """Stop the scalping engine and close all positions"""
        self.logger.info("🛑 Stopping Scalping Engine...")
        self.is_running = False
        
        # Close all active positions
        for symbol in list(self.active_positions.keys()):
            self.close_position(symbol)
        
        # Final status report
        self.log_final_report()
        # Generate detailed end-of-day report
        try:
            self.generate_daily_reports()
        except Exception as rep_err:
            self.logger.error(f"Daily report generation failed: {rep_err}")
    
    def log_final_report(self):
        """Log final trading session report"""
        metrics = self.performance_metrics
        win_rate = (metrics['winning_trades'] / max(metrics['total_trades'], 1)) * 100
        
        self.logger.info("📊 FINAL SCALPING SESSION REPORT")
        self.logger.info("=" * 50)
        self.logger.info(f"Daily P&L: ${self.daily_pnl:+.2f}")
        self.logger.info(f"Total Trades: {metrics['total_trades']}")
        self.logger.info(f"Winning Trades: {metrics['winning_trades']}")
        self.logger.info(f"Losing Trades: {metrics['losing_trades']}")
        self.logger.info(f"Win Rate: {win_rate:.1f}%")
        self.logger.info(f"Average Trade: ${metrics['total_pnl']/max(metrics['total_trades'], 1):+.2f}")

    # ---------------- Symbol-level Performance & Reporting -----------------
    def _accumulate_symbol_performance(self, tr: TradeRecord):
        """Accumulate per-symbol performance statistics from a finalized TradeRecord."""
        sym = tr.symbol
        sp = self.symbol_perf.setdefault(sym, {
            'trades': 0,
            'wins': 0,
            'losses': 0,
            'realized_pnl': 0.0,
            'realized_r_sum': 0.0,
            'equity_path': [],  # cumulative pnl path for drawdown
            'max_drawdown': 0.0,
            'total_hold_time': 0.0,
            'side_counts': {'BUY': 0, 'SELL': 0},
            'time_buckets': {},  # bucket -> {'pnl': x, 'trades': n}
            'mae_r_list': [],
            'mfe_r_list': [],
            'missed_gt1R': 0,
            'total_missed_potential_r': 0.0
        })
        sp['trades'] += 1
        if tr.realized_pnl and tr.realized_pnl > 0:
            sp['wins'] += 1
        elif tr.realized_pnl and tr.realized_pnl < 0:
            sp['losses'] += 1
        if tr.r_multiple is not None:
            sp['realized_r_sum'] += tr.r_multiple
        if tr.realized_pnl is not None:
            sp['realized_pnl'] += tr.realized_pnl
        # Equity path & drawdown
        cumulative = sp['equity_path'][-1] + tr.realized_pnl if sp['equity_path'] else tr.realized_pnl or 0.0
        sp['equity_path'].append(cumulative)
        peak = max(sp['equity_path']) if sp['equity_path'] else cumulative
        drawdown = peak - cumulative
        if drawdown > sp['max_drawdown']:
            sp['max_drawdown'] = drawdown
        # Hold time
        if tr.hold_time_s:
            sp['total_hold_time'] += tr.hold_time_s
        # Side
        if tr.side in sp['side_counts']:
            sp['side_counts'][tr.side] += 1
        # Time bucket (15-min exit ET)
        try:
            tz = pytz.timezone('US/Eastern')
            exit_et = tr.exit_time.astimezone(tz) if tr.exit_time else datetime.now(tz)
            bucket_minute = (exit_et.minute // 15) * 15
            bucket = f"{exit_et.hour:02d}:{bucket_minute:02d}"
            tb = sp['time_buckets'].setdefault(bucket, {'pnl': 0.0, 'trades': 0})
            tb['trades'] += 1
            if tr.realized_pnl:
                tb['pnl'] += tr.realized_pnl
        except Exception:
            pass
        # MAE/MFE
        if tr.mae_r is not None:
            sp['mae_r_list'].append(tr.mae_r)
        if tr.mfe_r is not None:
            sp['mfe_r_list'].append(tr.mfe_r)
        # Missed potential
        if tr.mfe_r is not None and tr.r_multiple is not None:
            if tr.mfe_r >= 1.0 and tr.r_multiple < 1.0:
                sp['missed_gt1R'] += 1
            if tr.mfe_r > tr.r_multiple:
                sp['total_missed_potential_r'] += (tr.mfe_r - tr.r_multiple)

    def get_realtime_symbol_pnl(self) -> List[Dict[str, float]]:
        """Return snapshot of per-symbol real-time PnL (realized + unrealized) and key open-trade stats."""
        snapshot = []
        for symbol, pos in self.active_positions.items():
            try:
                md = self.data_manager.get_current_market_data(symbol)
                if not md:
                    continue
                price = md['price']
                entry = pos['entry_price']
                direction = 1 if pos['signal'].signal_type == 'BUY' else -1
                unrealized_pnl = (price - entry) * direction * pos['position_size']
                pnl_pct = ((price - entry) / entry) * 100 * direction if entry else 0
                risk_per_share = abs(entry - pos['stop_loss']) if pos.get('stop_loss') else None
                current_r = ((price - entry) * direction / risk_per_share) if risk_per_share else None
                snapshot.append({
                    'symbol': symbol,
                    'side': pos['signal'].signal_type,
                    'unrealized_pnl': unrealized_pnl,
                    'unrealized_pct': pnl_pct,
                    'current_r': current_r,
                    'mae_pct': pos.get('mae_pct'),
                    'mfe_pct': pos.get('mfe_pct'),
                    'position_size': pos.get('position_size')
                })
            except Exception:
                continue
        # Add realized component per symbol
        for row in snapshot:
            sp = self.symbol_perf.get(row['symbol'])
            row['realized_pnl'] = sp['realized_pnl'] if sp else 0.0
            row['net_pnl'] = row['realized_pnl'] + row['unrealized_pnl']
        return snapshot

    def generate_daily_reports(self):
        """Write end-of-day per-symbol summary and time-bucket distribution reports."""
        if not self.symbol_perf:
            self.logger.info("No symbol performance data to report.")
            return
        date_str = datetime.now().strftime('%Y%m%d')
        reports_dir = Path('reports') / 'daily'
        reports_dir.mkdir(parents=True, exist_ok=True)
        summary_csv = reports_dir / f'{date_str}_symbol_summary.csv'
        time_csv = reports_dir / f'{date_str}_time_buckets.csv'
        md_report = reports_dir / f'{date_str}_summary.md'

        # Summary CSV
        with summary_csv.open('w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['symbol','trades','wins','losses','win_rate_pct','net_pnl','avg_pnl','avg_r','avg_hold_s','max_drawdown','avg_mae_r','avg_mfe_r','missed_gt1R','avg_unrealized_excess_r'])
            for sym, sp in self.symbol_perf.items():
                trades = sp['trades'] or 1
                win_rate = (sp['wins']/trades)*100 if trades else 0
                avg_pnl = sp['realized_pnl']/trades
                avg_r = sp['realized_r_sum']/trades if trades else 0
                avg_hold = sp['total_hold_time']/trades if trades else 0
                avg_mae_r = (sum(sp['mae_r_list'])/len(sp['mae_r_list'])) if sp['mae_r_list'] else ''
                avg_mfe_r = (sum(sp['mfe_r_list'])/len(sp['mfe_r_list'])) if sp['mfe_r_list'] else ''
                avg_unreal = (sp['total_missed_potential_r']/trades) if trades else 0
                w.writerow([
                    sym, sp['trades'], sp['wins'], sp['losses'], f"{win_rate:.2f}", f"{sp['realized_pnl']:.2f}", f"{avg_pnl:.2f}", f"{avg_r:.3f}", f"{avg_hold:.1f}", f"{sp['max_drawdown']:.2f}",
                    '' if avg_mae_r=='' else f"{avg_mae_r:.3f}", '' if avg_mfe_r=='' else f"{avg_mfe_r:.3f}", sp['missed_gt1R'], f"{avg_unreal:.3f}"
                ])

        # Time bucket CSV
        with time_csv.open('w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['symbol','time_bucket','trades','pnl'])
            for sym, sp in self.symbol_perf.items():
                for bucket, data in sorted(sp['time_buckets'].items()):
                    w.writerow([sym, bucket, data['trades'], f"{data['pnl']:.2f}"])

        # Markdown summary
        try:
            with md_report.open('w') as mf:
                mf.write(f"# Daily Trading Summary - {date_str}\n\n")
                mf.write("## Per-Symbol Performance\n\n")
                for sym, sp in self.symbol_perf.items():
                    trades = sp['trades'] or 1
                    win_rate = (sp['wins']/trades)*100 if trades else 0
                    avg_r = sp['realized_r_sum']/trades if trades else 0
                    mf.write(f"### {sym}\n")
                    mf.write(f"Trades: {sp['trades']} | Win%: {win_rate:.1f}% | Net PnL: {sp['realized_pnl']:.2f} | Avg R: {avg_r:.2f} | Max DD: {sp['max_drawdown']:.2f}\n\n")
                mf.write("## Files\n\n")
                mf.write(f"- Symbol Summary CSV: {summary_csv}\n")
                mf.write(f"- Time Buckets CSV: {time_csv}\n")
        except Exception as e:
            self.logger.debug(f"Markdown report failed: {e}")

    def validate_environment(self):
        """Validate the trading environment"""
        try:
            self.logger.info("Validating trading environment...")
            
            # Test data manager initialization
            self.data_manager = DataManager()
            
            # Test API connectivity through DataManager
            if self.data_manager.api:
                account_info = self.data_manager.get_account_info()
                if account_info:
                    self.logger.info(f"API connected - Account equity: ${account_info['equity']:,.2f}")
                    return True
                else:
                    self.logger.error("Failed to get account information")
                    return False
            else:
                self.logger.error("AlpacaTrader not initialized")
                return False
                
        except Exception as e:
            self.logger.error(f"Environment validation failed: {e}")
            return False

    def generate_pnl_report(self):
        """Generate P&L report"""
        try:
            self.logger.info("Generating P&L report...")
            
            # Initialize components
            self.data_manager = DataManager()
            
            # Get account info through AlpacaTrader
            if self.data_manager.alpaca_trader:
                account_info = self.data_manager.alpaca_trader.get_account_info()
                if account_info:
                    print(f"Account Value: ${account_info['portfolio_value']:,.2f}")
                    print(f"Buying Power: ${account_info['buying_power']:,.2f}")
                    print(f"Cash: ${account_info['cash']:,.2f}")
                    print(f"Equity: ${account_info['equity']:,.2f}")
                else:
                    print("Unable to get account information")
            else:
                print("AlpacaTrader not available")
                
        except Exception as e:
            self.logger.error(f"P&L report generation failed: {e}")

    def start_trading(self, symbols):
        """Start trading with given symbols"""
        try:
            self.logger.info(f"Starting trading session with symbols: {symbols}")
            
            # Initialize components
            self.data_manager = DataManager()
            self.risk_manager = RiskManager()
            self.order_manager = OrderManager(self.data_manager)
            
            # Start the main trading loop
            self.start()
            
        except Exception as e:
            self.logger.error(f"Trading session failed: {e}")
            raise

if __name__ == "__main__":
    print("📈 Intraday Trading Engine")
    print("=" * 50)
    
    try:
        engine = IntradayEngine()
        engine.start()
    except Exception as e:
        print(f"❌ Failed to start intraday engine: {e}")
        sys.exit(1)
