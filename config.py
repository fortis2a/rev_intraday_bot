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

# Watchlist - stocks to monitor
INTRADAY_WATCHLIST = [
    'IONQ', 'RGTI', 'QBTS', 'JNJ', 'PG'
]

# Risk Management
MAX_POSITION_SIZE = 1000  # Maximum position size in dollars
MAX_DAILY_LOSS = 500     # Maximum daily loss limit
STOP_LOSS_PCT = 0.02     # 2% stop loss
TAKE_PROFIT_PCT = 0.04   # 4% take profit

# Trading Hours (Eastern Time) - Avoid volatile opening/closing periods
MARKET_OPEN = time(10, 0)   # 10:00 AM (30 min after market open)
MARKET_CLOSE = time(15, 30)  # 3:30 PM (30 min before market close)

# Strategy Settings
MOMENTUM_THRESHOLD = 0.015   # 1.5% price movement for momentum
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
VOLUME_MULTIPLIER = 1.5      # Volume must be 1.5x average

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
    'MAX_POSITION_SIZE': MAX_POSITION_SIZE,
    'MAX_DAILY_LOSS': MAX_DAILY_LOSS,
    'STOP_LOSS_PCT': STOP_LOSS_PCT,
    'TAKE_PROFIT_PCT': TAKE_PROFIT_PCT,
    'MARKET_OPEN': MARKET_OPEN,
    'MARKET_CLOSE': MARKET_CLOSE,
    'MOMENTUM_THRESHOLD': MOMENTUM_THRESHOLD,
    'RSI_OVERSOLD': RSI_OVERSOLD,
    'RSI_OVERBOUGHT': RSI_OVERBOUGHT,
    'VOLUME_MULTIPLIER': VOLUME_MULTIPLIER,
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
    'MAX_PRICE': MAX_PRICE
}
