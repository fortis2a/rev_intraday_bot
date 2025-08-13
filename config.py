#!/usr/bin/env python3
"""
📈 Intraday Trading Bot Configuration
Optimized for 2-8 hour swing trades with higher profit margins
"""

import os
from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
except ImportError:
    print("⚠️ python-dotenv not installed - environment variables from .env file will not be loaded")
    print("💡 Install with: pip install python-dotenv")

@dataclass
class IntradayTradingConfig:
    """Intraday trading bot configuration settings"""
    
    # Trading Parameters - Optimized for Intraday Swings
    TIMEFRAME: str = "15Min"  # Primary timeframe for signals
    ENTRY_TIMEFRAME: str = "5Min"  # For precise entries
    TREND_TIMEFRAME: str = "1Hour"  # For trend confirmation
    MAX_POSITION_SIZE: int = 50  # Larger position sizes for fewer trades
    MAX_DAILY_LOSS_PCT: float = 3.0  # Stop trading if daily loss exceeds 3%
    MAX_OPEN_POSITIONS: int = 3  # Fewer concurrent positions for better management
    
    # Risk Management - Higher Targets, Proportional Stops
    STOP_LOSS_PCT: float = 0.45  # 0.45% stop loss for intraday swings
    PROFIT_TARGET_PCT: float = 1.20  # 1.20% profit target (2.67:1 R:R ratio)
    TRAILING_STOP_PCT: float = 0.25  # Trailing stop percentage

    # Adaptive Stop / Volatility Controls - Adjusted for Longer Holds
    USE_ATR_STOPS: bool = True
    ATR_PERIOD: int = 20  # Longer period for intraday volatility
    ATR_MULT: float = 1.8  # Higher multiplier for swing trades
    MIN_STOP_PCT: float = 0.30  # Minimum stop for intraday moves
    MAX_STOP_PCT: float = 0.80  # Maximum stop tolerance
    INITIAL_STOP_GRACE: int = 300  # 5 minutes grace for larger moves
    CATASTROPHIC_MULT: float = 2.0  # Higher threshold for swing trades
    BREAKEVEN_TRIGGER_R: float = 1.0  # Move to breakeven at 1R
    TRAIL_TRIGGER_R: float = 1.5  # Start trailing at 1.5R
    TRAIL_LOOKBACK: int = 8  # Longer lookback for swing trailing
    TRAIL_ATR_OFFSET_MULT: float = 0.8  # Wider trailing offset
    
    # Position Sizing - Larger Positions for Better Economics
    ACCOUNT_RISK_PCT: float = 2.5  # Higher risk per trade (fewer trades)
    MIN_POSITION_VALUE: float = 200.0  # Higher minimum for better economics
    MAX_POSITION_VALUE: float = 3000.0  # Larger positions for intraday trades
    
    # Portfolio Simulation (for testing with smaller amounts)
    SIMULATE_PORTFOLIO: bool = False  # Disabled - Using Alpaca Paper Trading
    SIMULATED_PORTFOLIO_VALUE: float = 2000.0  # Not used when SIMULATE_PORTFOLIO=False
    
    # Short Selling Configuration - Enhanced for Swings
    ALLOW_SHORT_SELLING: bool = True  # Enable short selling for bearish signals
    MAX_SHORT_EXPOSURE: float = 3000.0  # Higher exposure for swing trades
    SHORT_LOCATE_REQUIRED: bool = False  # Whether to check for shares available to borrow
    
    # Position Management Configuration
    ADOPT_EXISTING_POSITIONS: bool = True  # Adopt existing positions for profit/loss management
    EXCLUDE_UNTRACKED_POSITIONS: bool = False  # Whether to exclude untracked positions from trading
    
    # Market Hours - Extended for Intraday Trading
    MARKET_OPEN: str = "09:30"
    MARKET_CLOSE: str = "16:00"
    TRADING_START: str = "09:45"  # Start trading 15 min after open
    TRADING_END: str = "15:30"    # Stop new trades 30 min before close
    LUNCH_BREAK_START: str = "12:00"  # Avoid lunch hour volatility
    LUNCH_BREAK_END: str = "13:00"
    
    # Stock Selection Criteria - Enhanced for Intraday Moves
    MIN_VOLUME: int = 5000000  # Higher volume for better intraday liquidity
    MIN_PRICE: float = 25.0    # Higher minimum price for institutional interest
    MAX_PRICE: float = 300.0   # Higher range for better swing opportunities
    MAX_SPREAD_PCT: float = 0.03  # Tighter spread for better execution
    MIN_VOLATILITY: float = 1.2  # Higher volatility for intraday moves
    MAX_VOLATILITY: float = 4.0  # Controlled maximum for risk management
    
    # Technical Indicators - Adjusted for 15-minute timeframe
    RSI_OVERSOLD: int = 25  # More extreme levels for swing trades
    RSI_OVERBOUGHT: int = 75
    RSI_PERIOD: int = 14
    
    EMA_FAST: int = 20  # Longer EMAs for intraday trends
    EMA_SLOW: int = 50
    
    VWAP_PERIODS: int = 50  # Longer VWAP for daily context

    # Data Feed (Alpaca: 'iex' for free plan, 'sip' for paid)
    DATA_FEED: str = "iex"
    
    # Execution Settings
    ORDER_TIMEOUT: int = 30  # Order timeout in seconds
    MAX_SLIPPAGE_PCT: float = 0.05  # Maximum acceptable slippage
    
    # Logging and Monitoring
    LOG_LEVEL: str = "INFO"
    SAVE_TRADES: bool = True
    REAL_TIME_MONITORING: bool = True

    # Cooldown Controls
    SIGNAL_COOLDOWN_SECONDS: int = 45  # Cooldown between signals per symbol
    FAILED_SIGNAL_COOLDOWN_SECONDS: int = 180  # Extended cooldown after failed execution

    # Overtrading Guards / Quality Gates - Optimized for Intraday
    MAX_TRADES_PER_DAY: int = 6  # Dramatically reduced for quality focus
    MAX_TRADES_PER_SYMBOL_PER_DAY: int = 2  # Maximum 2 per symbol
    MINUTES_BETWEEN_TRADES_PER_SYMBOL: int = 60  # 1 hour spacing for better setups
    MIN_CONFIDENCE: float = 0.75  # Higher confidence for swing trades
    MIN_EXPECTED_R: float = 2.0  # Much higher R:R requirement
    REQUIRE_MIN_VOLUME_RATIO: float = 1.8  # Strong volume confirmation
    CONSECUTIVE_LOSS_PAUSE_N: int = 2  # Pause after 2 losses
    CONSECUTIVE_LOSS_PAUSE_MINUTES: int = 120  # 2-hour pause for reflection
    
    # Hold Time Management for Intraday Swings
    MIN_HOLD_TIME_MINUTES: int = 30  # Minimum hold time for signal development
    MAX_HOLD_TIME_MINUTES: int = 480  # Maximum 8 hours per position
    PROFIT_ACCELERATION_R: float = 2.5  # Accelerate exit at 2.5R
    
    # Multi-timeframe Analysis
    USE_MULTI_TIMEFRAME: bool = True
    TREND_CONFIRMATION_REQUIRED: bool = True  # Require hourly trend alignment
    VOLUME_PROFILE_ANALYSIS: bool = True  # Use volume profile for entries
    
    # Alpaca Settings (from environment)
    ALPACA_API_KEY: str = os.getenv("ALPACA_API_KEY", "PK3PR3B144HUY1BPOTSI")
    ALPACA_SECRET_KEY: str = os.getenv("ALPACA_SECRET_KEY", "HTFUB2U7seFy8oezkc9U7Dq7zXtJg6rGo0DmGhnJ")
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets"  # Paper trading
    
    # Watchlist - High volume, liquid stocks for scalping
    SCALPING_WATCHLIST: List[str] = None
    
    def __post_init__(self):
        if self.SCALPING_WATCHLIST is None:
            # Try to import custom watchlist, fallback to default
            try:
                from stock_watchlist import ACTIVE_WATCHLIST
                self.SCALPING_WATCHLIST = ACTIVE_WATCHLIST
            except ImportError:
                # Optimized watchlist for intraday swing trading
                self.SCALPING_WATCHLIST = [
                    # Large-cap tech with strong intraday movement
                    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "NFLX",
                    "AMD", "CRM", "ADBE", "PYPL", "UBER", "ZM",
                    
                    # Financial sector - responsive to market moves
                    "JPM", "BAC", "WFC", "C", "GS", "MS", "AXP",
                    
                    # Major ETFs for broad market plays
                    "SPY", "QQQ", "IWM", "XLF", "XLK", "XLE", "XLV",
                    
                    # High-volume healthcare and consumer
                    "JNJ", "UNH", "PFE", "KO", "PG", "WMT", "HD",
                    
                    # Energy and materials for sector rotation
                    "XOM", "CVX", "COP", "SLB",
                    
                    # Semiconductor sector
                    "SMH", "SOXX", "TSM"
                ]

# Global configuration instance
config = IntradayTradingConfig()

# Timeframe configurations for intraday trading
TIMEFRAME_CONFIGS = {
    "15Min": {
        "data_frequency": "15Min",
        "lookback_periods": 50,
        "signal_delay": 30,  # 30 seconds for 15-min signals
        "max_hold_time": 28800,  # 8 hours max hold
        "momentum_threshold": 0.8,
        "volatility_window": 20,
        "volume_confirmation": 2.0
    },
    "5Min": {
        "data_frequency": "5Min",
        "lookback_periods": 100,
        "signal_delay": 10,  # 10 seconds for 5-min entries
        "max_hold_time": 28800,
        "momentum_threshold": 0.4,
        "volatility_window": 30,
        "volume_confirmation": 1.8
    },
    "1Hour": {
        "data_frequency": "1Hour",
        "lookback_periods": 24,
        "signal_delay": 60,  # 1 minute for hourly confirmation
        "max_hold_time": 28800,
        "momentum_threshold": 1.5,
        "volatility_window": 10,
        "volume_confirmation": 1.5
    }
}

# Strategy-specific configurations for intraday trading
STRATEGY_CONFIGS = {
    "momentum_scalp": {
        "enabled": True,
        "weight": 0.4,
        "min_confidence": 0.75,
        "min_volume_spike": 2.0,  # Higher volume spike for intraday
        "price_change_threshold": 0.8,  # Larger price moves for swings
        "confirmation_bars": 3,  # More confirmation for larger moves
        "trend_alignment_required": True,
        "rsi_oversold": 25,
        "rsi_overbought": 75
    },
    "mean_reversion": {
        "enabled": True,
        "weight": 0.3,
        "min_confidence": 0.75,
        "deviation_threshold": 2.5,  # Larger deviations for swing trades
        "reversion_target": 0.6,     # 60% reversion target
        "max_deviation_time": 3600,  # 1 hour max for intraday
        "bollinger_periods": 20,
        "volume_confirmation": 1.8
    },
    "vwap_bounce": {
        "enabled": True,
        "weight": 0.3,
        "min_confidence": 0.75,
        "vwap_touch_tolerance": 0.15,  # Wider tolerance for swing trades
        "bounce_confirmation": 3,       # More confirmation needed
        "volume_confirmation": 2.0,     # Stronger volume requirement
        "daily_vwap": True,
        "support_resistance_levels": True
    }
}

def get_timeframe_config(timeframe: str = None) -> Dict:
    """Get configuration for specific timeframe"""
    if timeframe is None:
        timeframe = config.TIMEFRAME
    return TIMEFRAME_CONFIGS.get(timeframe, TIMEFRAME_CONFIGS["15Min"])

def get_strategy_config(strategy: str) -> Dict:
    """Get configuration for specific strategy"""
    return STRATEGY_CONFIGS.get(strategy, {})

def validate_config() -> bool:
    """Validate configuration settings"""
    errors = []
    
    # Check required API keys
    if not config.ALPACA_API_KEY:
        errors.append("ALPACA_API_KEY not set")
    if not config.ALPACA_SECRET_KEY:
        errors.append("ALPACA_SECRET_KEY not set")
    
    # Validate risk parameters
    if config.STOP_LOSS_PCT <= 0:
        errors.append("STOP_LOSS_PCT must be positive")
    if config.PROFIT_TARGET_PCT <= config.STOP_LOSS_PCT:
        errors.append("PROFIT_TARGET_PCT must be greater than STOP_LOSS_PCT")
    
    # Validate position limits
    if config.MAX_POSITION_SIZE <= 0:
        errors.append("MAX_POSITION_SIZE must be positive")
    if config.MAX_OPEN_POSITIONS <= 0:
        errors.append("MAX_OPEN_POSITIONS must be positive")
    
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    return True

if __name__ == "__main__":
    print("⚡ Scalping Bot Configuration")
    print("=" * 50)
    print(f"Timeframe: {config.TIMEFRAME}")
    print(f"Max Positions: {config.MAX_OPEN_POSITIONS}")
    print(f"Stop Loss: {config.STOP_LOSS_PCT}%")
    print(f"Profit Target: {config.PROFIT_TARGET_PCT}%")
    print(f"Watchlist: {len(config.SCALPING_WATCHLIST)} symbols")
    print(f"Valid Config: {validate_config()}")
