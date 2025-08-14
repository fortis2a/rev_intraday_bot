#!/usr/bin/env python3
"""
Configuration file for Intraday Trading Bot
ASCII-only, no Unicode characters
Loads API keys from .env file
"""

import os
from datetime import time

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[INFO] Loaded environment variables from .env file")
except ImportError:
    print("[WARNING] python-dotenv not installed - loading from system environment")

# Trading Configuration
TRADING_MODE = "LIVE"  # LIVE, DEMO, TEST
TIMEFRAME = "15Min"  # 1Min, 5Min, 15Min, 1Hour

# Watchlist - PRIMARY stocks to monitor (Budget-friendly, high-performance)
INTRADAY_WATCHLIST = [
    'SOXL',  # $29.27 - 87.7/100 (Excellent) - 3x Leveraged Semiconductor ETF
    'SOFI',  # $23.81 - 84.6/100 (Excellent) - Financial Services/Fintech
    'TQQQ',  # $94.86 - 81.2/100 (Excellent) - 3x Leveraged NASDAQ ETF
    'INTC',  # $22.22 - 79.8/100 (Good) - Intel Corporation
    'NIO'    # $4.62 - 79.6/100 (Good) - Electric Vehicle Company
]

# Alternative watchlist - Original research stocks (backup/testing)
INTRADAY_WATCHLIST2 = [
    'IONQ', 'RGTI', 'QBTS', 'JNJ', 'PG'
]

# Risk Management - Default values (can be overridden by stock-specific settings)
MAX_POSITION_SIZE = 1000  # Maximum position size in dollars
MAX_DAILY_LOSS = 500     # Maximum daily loss limit
STOP_LOSS_PCT = 0.015    # 1.5% default stop loss (conservative)
TAKE_PROFIT_PCT = 0.020  # 2.0% default take profit (conservative)

# Enable stock-specific thresholds
USE_STOCK_SPECIFIC_THRESHOLDS = True

# Trailing Stop Configuration - Default values
TRAILING_STOP_ENABLED = True        # Enable trailing stop functionality
TRAILING_STOP_PCT = 0.015           # 1.5% default trailing stop distance
TRAILING_STOP_ACTIVATION = 0.010    # 1.0% profit before trailing activates
TRAILING_STOP_MIN_MOVE = 0.005      # 0.5% minimum move to adjust trailing stop

# Trading Hours (Eastern Time) - Avoid volatile opening/closing periods
MARKET_OPEN = time(10, 0)   # 10:00 AM (30 min after market open)
MARKET_CLOSE = time(15, 30)  # 3:30 PM (30 min before market close)

# Trading Hours for Intraday Engine (string format expected by engine)
TRADING_START = "10:00"     # 10:00 AM (30 min after market open)
TRADING_END = "15:30"       # 3:30 PM (30 min before market close)
LUNCH_BREAK_START = "12:00" # 12:00 PM (lunch break start)
LUNCH_BREAK_END = "13:00"   # 1:00 PM (lunch break end)

# Strategy Settings
MOMENTUM_THRESHOLD = 0.015   # 1.5% price movement for momentum
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
VOLUME_MULTIPLIER = 1.5      # Volume must be 1.5x average

# Signal Quality Filters
MIN_CONFIDENCE_THRESHOLD = 0.75  # 75% minimum confidence for live trading
MIN_CONFIDENCE_DEMO = 0.50      # 50% minimum for demo/testing

# Trading Control Settings
TRADE_COOLDOWN_MINUTES = 5   # Minimum minutes between trades for same symbol
MAX_TRADES_PER_HOUR = 6     # Maximum trades per hour per symbol

# API Configuration - Load from .env file
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
ALPACA_TRADING_ENV = os.getenv("ALPACA_TRADING_ENV", "paper")

print(f"[CONFIG] Alpaca API Key: {'SET' if ALPACA_API_KEY else 'NOT SET'}")
print(f"[CONFIG] Alpaca Secret Key: {'SET' if ALPACA_SECRET_KEY else 'NOT SET'}")
print(f"[CONFIG] Alpaca Base URL: {ALPACA_BASE_URL}")
print(f"[CONFIG] Trading Environment: {ALPACA_TRADING_ENV}")

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_TO_FILE = True
LOG_DIRECTORY = "logs"

# System Settings
CHECK_INTERVAL = 30  # seconds between market checks
MAX_POSITIONS = 5    # maximum concurrent positions
MIN_PRICE = 5.00     # minimum stock price to trade
MAX_PRICE = 500.00   # maximum stock price to trade

# Additional Engine Settings
MAX_OPEN_POSITIONS = 5      # Maximum open positions (same as MAX_POSITIONS)
ADOPT_EXISTING_POSITIONS = True  # Whether to adopt existing broker positions
MIN_VOLUME = 100000         # Minimum daily volume
MAX_SPREAD_PCT = 0.5        # Maximum bid-ask spread percentage

def validate_config():
    """Validate configuration settings"""
    if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
        raise ValueError("Alpaca API credentials not found in environment variables")
    
    if MAX_DAILY_LOSS <= 0:
        raise ValueError("MAX_DAILY_LOSS must be positive")
    
    if STOP_LOSS_PCT <= 0 or STOP_LOSS_PCT >= 1:
        raise ValueError("STOP_LOSS_PCT must be between 0 and 1")
    
    print("[CONFIG] Configuration validation passed")
    return True

# Export main config object
config = {
    'TRADING_MODE': TRADING_MODE,
    'TIMEFRAME': TIMEFRAME,
    'INTRADAY_WATCHLIST': INTRADAY_WATCHLIST,
    'INTRADAY_WATCHLIST2': INTRADAY_WATCHLIST2,
    'MAX_POSITION_SIZE': MAX_POSITION_SIZE,
    'MAX_DAILY_LOSS': MAX_DAILY_LOSS,
    'STOP_LOSS_PCT': STOP_LOSS_PCT,
    'TAKE_PROFIT_PCT': TAKE_PROFIT_PCT,
    'USE_STOCK_SPECIFIC_THRESHOLDS': USE_STOCK_SPECIFIC_THRESHOLDS,
    'TRAILING_STOP_ENABLED': TRAILING_STOP_ENABLED,
    'TRAILING_STOP_PCT': TRAILING_STOP_PCT,
    'TRAILING_STOP_ACTIVATION': TRAILING_STOP_ACTIVATION,
    'TRAILING_STOP_MIN_MOVE': TRAILING_STOP_MIN_MOVE,
    'MARKET_OPEN': MARKET_OPEN,
    'MARKET_CLOSE': MARKET_CLOSE,
    'TRADING_START': TRADING_START,
    'TRADING_END': TRADING_END,
    'LUNCH_BREAK_START': LUNCH_BREAK_START,
    'LUNCH_BREAK_END': LUNCH_BREAK_END,
    'MOMENTUM_THRESHOLD': MOMENTUM_THRESHOLD,
    'RSI_OVERSOLD': RSI_OVERSOLD,
    'RSI_OVERBOUGHT': RSI_OVERBOUGHT,
    'VOLUME_MULTIPLIER': VOLUME_MULTIPLIER,
    'MIN_CONFIDENCE_THRESHOLD': MIN_CONFIDENCE_THRESHOLD,
    'MIN_CONFIDENCE_DEMO': MIN_CONFIDENCE_DEMO,
    'TRADE_COOLDOWN_MINUTES': TRADE_COOLDOWN_MINUTES,
    'MAX_TRADES_PER_HOUR': MAX_TRADES_PER_HOUR,
    'ALPACA_BASE_URL': ALPACA_BASE_URL,
    'ALPACA_API_KEY': ALPACA_API_KEY,
    'ALPACA_SECRET_KEY': ALPACA_SECRET_KEY,
    'ALPACA_TRADING_ENV': ALPACA_TRADING_ENV,
    'LOG_LEVEL': LOG_LEVEL,
    'LOG_TO_FILE': LOG_TO_FILE,
    'LOG_DIRECTORY': LOG_DIRECTORY,
    'CHECK_INTERVAL': CHECK_INTERVAL,
    'MAX_POSITIONS': MAX_POSITIONS,
    'MIN_PRICE': MIN_PRICE,
    'MAX_PRICE': MAX_PRICE,
    'MAX_OPEN_POSITIONS': MAX_OPEN_POSITIONS,
    'ADOPT_EXISTING_POSITIONS': ADOPT_EXISTING_POSITIONS,
    'MIN_VOLUME': MIN_VOLUME,
    'MAX_SPREAD_PCT': MAX_SPREAD_PCT
}

# Create a simple object-like interface for dot notation access
class ConfigObject:
    def __init__(self, config_dict):
        self._config = config_dict
        for key, value in config_dict.items():
            setattr(self, key, value)
    
    def get(self, key, default=None):
        return getattr(self, key, default)
    
    def __getitem__(self, key):
        """Support dictionary-style access"""
        return self._config[key]
    
    def __contains__(self, key):
        """Support 'in' operator"""
        return key in self._config
    
    def keys(self):
        """Support .keys() method"""
        return self._config.keys()
    
    def values(self):
        """Support .values() method"""
        return self._config.values()
    
    def items(self):
        """Support .items() method"""
        return self._config.items()

# Replace the dictionary with an object that supports both dict and dot notation
config = ConfigObject(config)
