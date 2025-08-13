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
from logger import setup_logger, clean_message

class DataManager:
    """Manages market data and Alpaca API connection"""
    
    def __init__(self):
        self.logger = setup_logger('data_manager')
        self.logger.info("Initializing Data Manager...")
        
        # Initialize Alpaca API
        try:
            self.api = tradeapi.REST(
                config['ALPACA_API_KEY'],
                config['ALPACA_SECRET_KEY'],
                config['ALPACA_BASE_URL'],
                api_version='v2'
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
    
    def get_account_info(self):
        """Get current account information"""
        try:
            account = self.api.get_account()
            return {
                'equity': float(account.equity),
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'day_trading_buying_power': float(getattr(account, 'day_trading_buying_power', account.buying_power)),
                'portfolio_value': float(account.portfolio_value)
            }
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to get account info: {e}")
            return None
    
    def get_positions(self):
        """Get current positions"""
        try:
            positions = self.api.list_positions()
            position_data = []
            
            for pos in positions:
                position_data.append({
                    'symbol': pos.symbol,
                    'qty': float(pos.qty),
                    'side': pos.side,
                    'market_value': float(pos.market_value),
                    'unrealized_pl': float(pos.unrealized_pl),
                    'avg_entry_price': float(pos.avg_entry_price)
                })
            
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
    
    def get_bars(self, symbol, timeframe='15Min', limit=100):
        """Get historical bars for a symbol"""
        try:
            # Calculate start time
            end_time = datetime.now()
            if timeframe == '1Min':
                start_time = end_time - timedelta(hours=2)
            elif timeframe == '5Min':
                start_time = end_time - timedelta(hours=8)
            elif timeframe == '15Min':
                start_time = end_time - timedelta(days=2)
            else:
                start_time = end_time - timedelta(days=5)
            
            bars = self.api.get_bars(
                symbol,
                timeframe,
                start=start_time.isoformat(),
                end=end_time.isoformat(),
                limit=limit
            )
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'timestamp': bar.t,
                'open': float(bar.o),
                'high': float(bar.h),
                'low': float(bar.l),
                'close': float(bar.c),
                'volume': int(bar.v)
            } for bar in bars])
            
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.set_index('timestamp')
            
            return df
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to get bars for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_market_status(self):
        """Check if market is open"""
        try:
            clock = self.api.get_clock()
            return {
                'is_open': clock.is_open,
                'next_open': clock.next_open,
                'next_close': clock.next_close
            }
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to get market status: {e}")
            return {'is_open': False}
    
    def calculate_indicators(self, df):
        """Calculate technical indicators"""
        if df.empty or len(df) < 20:
            return df
        
        try:
            # Simple Moving Averages
            df['sma_10'] = df['close'].rolling(window=10).mean()
            df['sma_20'] = df['close'].rolling(window=20).mean()
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Volume Moving Average
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # Price change
            df['price_change'] = df['close'].pct_change()
            
            return df
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to calculate indicators: {e}")
            return df
