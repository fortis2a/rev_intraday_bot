"""
Real-time Alpaca API integration for Command Center
Handles live account data, positions, and market data
"""

import requests
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass
import asyncio
import aiohttp
import websocket
import pandas as pd

try:
    from config import config
except ImportError:
    config = None

@dataclass
class AccountSnapshot:
    """Account snapshot data structure"""
    equity: float
    cash: float
    buying_power: float
    day_pnl: float
    unrealized_pnl: float
    portfolio_value: float
    positions_count: int
    timestamp: datetime

@dataclass
class PositionData:
    """Position data structure"""
    symbol: str
    qty: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_pc: float
    current_price: float
    timestamp: datetime

class AlpacaRealTimeConnector:
    """Real-time Alpaca API connector"""
    
    def __init__(self):
        self.logger = self.setup_logger()
        self.base_url = config.ALPACA_BASE_URL if config else "https://paper-api.alpaca.markets"
        self.api_key = config.ALPACA_API_KEY if config else None
        self.secret_key = config.ALPACA_SECRET_KEY if config else None
        
        # Data storage
        self.account_snapshot = None
        self.positions = {}
        self.market_data = {}
        self.last_update = datetime.now()
        
        # Connection state
        self.is_connected = False
        self.connection_error = None
        
        # Callbacks
        self.account_callbacks = []
        self.position_callbacks = []
        self.market_callbacks = []
        
        # Validate credentials
        if not self.api_key or not self.secret_key:
            self.logger.warning("Alpaca API credentials not found - running in simulation mode")
            self.is_connected = False
        else:
            self.logger.info("Alpaca API credentials loaded successfully")
            
    def setup_logger(self):
        """Setup logging for Alpaca connector"""
        logger = logging.getLogger("alpaca_connector")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def get_headers(self):
        """Get API headers for Alpaca requests"""
        return {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.secret_key,
            'Content-Type': 'application/json'
        }
        
    async def test_connection(self) -> bool:
        """Test connection to Alpaca API"""
        if not self.api_key or not self.secret_key:
            return False
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/v2/account",
                    headers=self.get_headers(),
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        self.is_connected = True
                        self.connection_error = None
                        self.logger.info("✅ Connected to Alpaca API successfully")
                        return True
                    else:
                        error_text = await response.text()
                        self.connection_error = f"HTTP {response.status}: {error_text}"
                        self.logger.error(f"❌ Alpaca API connection failed: {self.connection_error}")
                        return False
                        
        except Exception as e:
            self.connection_error = str(e)
            self.logger.error(f"❌ Alpaca API connection error: {e}")
            return False
            
    async def fetch_account_data(self) -> Optional[AccountSnapshot]:
        """Fetch real-time account data from Alpaca"""
        if not self.is_connected:
            return None
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/v2/account",
                    headers=self.get_headers(),
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        snapshot = AccountSnapshot(
                            equity=float(data.get('equity', 0)),
                            cash=float(data.get('cash', 0)),
                            buying_power=float(data.get('buying_power', 0)),
                            day_pnl=float(data.get('day_pnl_change', 0)),
                            unrealized_pnl=float(data.get('unrealized_pnl', 0)),
                            portfolio_value=float(data.get('portfolio_value', 0)),
                            positions_count=0,  # Will be updated separately
                            timestamp=datetime.now()
                        )
                        
                        self.account_snapshot = snapshot
                        
                        # Notify callbacks
                        for callback in self.account_callbacks:
                            try:
                                callback(snapshot)
                            except Exception as e:
                                self.logger.error(f"Error in account callback: {e}")
                                
                        return snapshot
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Failed to fetch account data: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Error fetching account data: {e}")
            return None
            
    async def fetch_positions(self) -> Dict[str, PositionData]:
        """Fetch current positions from Alpaca"""
        if not self.is_connected:
            return {}
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/v2/positions",
                    headers=self.get_headers(),
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        positions_data = await response.json()
                        positions = {}
                        
                        for pos in positions_data:
                            position = PositionData(
                                symbol=pos['symbol'],
                                qty=float(pos['qty']),
                                market_value=float(pos['market_value']),
                                unrealized_pnl=float(pos['unrealized_pnl']),
                                unrealized_pnl_pc=float(pos['unrealized_plpc']),
                                current_price=float(pos['current_price']),
                                timestamp=datetime.now()
                            )
                            positions[pos['symbol']] = position
                            
                        self.positions = positions
                        
                        # Update account positions count
                        if self.account_snapshot:
                            self.account_snapshot.positions_count = len(positions)
                            
                        # Notify callbacks
                        for callback in self.position_callbacks:
                            try:
                                callback(positions)
                            except Exception as e:
                                self.logger.error(f"Error in position callback: {e}")
                                
                        return positions
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Failed to fetch positions: {response.status} - {error_text}")
                        return {}
                        
        except Exception as e:
            self.logger.error(f"Error fetching positions: {e}")
            return {}
            
    async def fetch_market_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """Fetch real-time market data for symbols"""
        if not self.is_connected or not symbols:
            return {}
            
        try:
            # Get latest quotes for all symbols
            symbols_str = ','.join(symbols)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/v2/stocks/quotes/latest",
                    headers=self.get_headers(),
                    params={'symbols': symbols_str},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        market_data = {}
                        
                        for symbol, quote in data.get('quotes', {}).items():
                            market_data[symbol] = {
                                'price': float(quote.get('bp', 0)),  # bid price
                                'ask': float(quote.get('ap', 0)),    # ask price
                                'bid': float(quote.get('bp', 0)),    # bid price
                                'volume': int(quote.get('bs', 0)),   # bid size
                                'timestamp': datetime.fromisoformat(quote.get('t', '').replace('Z', '+00:00')),
                                'change': 0.0,  # Will calculate if we have previous data
                                'change_percent': 0.0
                            }
                            
                            # Calculate price change if we have previous data
                            if symbol in self.market_data:
                                prev_price = self.market_data[symbol].get('price', 0)
                                if prev_price > 0:
                                    current_price = market_data[symbol]['price']
                                    change = current_price - prev_price
                                    change_percent = (change / prev_price) * 100
                                    market_data[symbol]['change'] = change
                                    market_data[symbol]['change_percent'] = change_percent
                                    
                        self.market_data.update(market_data)
                        
                        # Notify callbacks
                        for callback in self.market_callbacks:
                            try:
                                callback(market_data)
                            except Exception as e:
                                self.logger.error(f"Error in market callback: {e}")
                                
                        return market_data
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Failed to fetch market data: {response.status} - {error_text}")
                        return {}
                        
        except Exception as e:
            self.logger.error(f"Error fetching market data: {e}")
            return {}
            
    def register_account_callback(self, callback):
        """Register callback for account updates"""
        self.account_callbacks.append(callback)
        
    def register_position_callback(self, callback):
        """Register callback for position updates"""
        self.position_callbacks.append(callback)
        
    def register_market_callback(self, callback):
        """Register callback for market data updates"""
        self.market_callbacks.append(callback)
        
    async def start_real_time_feed(self, symbols: List[str]):
        """Start real-time data feed"""
        await self.test_connection()
        
        if not self.is_connected:
            self.logger.warning("Cannot start real-time feed - not connected to Alpaca")
            return
            
        self.logger.info(f"🚀 Starting real-time feed for {len(symbols)} symbols")
        
        while True:
            try:
                # Fetch all data concurrently
                tasks = [
                    self.fetch_account_data(),
                    self.fetch_positions(),
                    self.fetch_market_data(symbols)
                ]
                
                await asyncio.gather(*tasks, return_exceptions=True)
                self.last_update = datetime.now()
                
                # Wait before next update
                await asyncio.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                self.logger.error(f"Error in real-time feed: {e}")
                await asyncio.sleep(5)  # Wait longer on error
                
    def get_latest_account_data(self) -> Optional[AccountSnapshot]:
        """Get latest account snapshot"""
        return self.account_snapshot
        
    def get_latest_positions(self) -> Dict[str, PositionData]:
        """Get latest positions"""
        return self.positions.copy()
        
    def get_latest_market_data(self, symbol: str = None) -> Dict:
        """Get latest market data for symbol or all symbols"""
        if symbol:
            return self.market_data.get(symbol, {})
        return self.market_data.copy()
    
    # Command Center compatibility methods
    def get_account(self):
        """Get account information compatible with Command Center"""
        account_data = self.get_latest_account_data()
        if account_data:
            return {
                'equity': account_data.portfolio_value,
                'cash': account_data.cash,
                'unrealized_pl': account_data.unrealized_pnl,
                'realized_pl': account_data.day_pnl,
                'buying_power': account_data.buying_power
            }
        return {
            'equity': 0,
            'cash': 0,
            'unrealized_pl': 0,
            'realized_pl': 0,
            'buying_power': 0
        }
    
    def get_positions(self):
        """Get positions compatible with Command Center"""
        positions_data = self.get_latest_positions()
        return [
            {
                'symbol': pos_data.symbol,
                'qty': int(pos_data.qty),
                'market_value': pos_data.market_value
            } for pos_data in positions_data.values()
        ]
        
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        try:
            now = datetime.now()
            # Simple check - market hours are 9:30 AM to 4:00 PM ET, Monday-Friday
            market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
            
            return (now.weekday() < 5 and  # Monday = 0, Friday = 4
                   market_open <= now <= market_close)
        except:
            return False
            
    def get_connection_status(self) -> Dict:
        """Get connection status info"""
        return {
            'connected': self.is_connected,
            'error': self.connection_error,
            'last_update': self.last_update,
            'market_open': self.is_market_open(),
            'base_url': self.base_url,
            'has_credentials': bool(self.api_key and self.secret_key)
        }

# Singleton instance for global use
alpaca_connector = AlpacaRealTimeConnector()

# Helper functions for easy integration
async def get_real_time_account() -> Optional[AccountSnapshot]:
    """Get real-time account data"""
    return await alpaca_connector.fetch_account_data()

async def get_real_time_positions() -> Dict[str, PositionData]:
    """Get real-time positions"""
    return await alpaca_connector.fetch_positions()

async def get_real_time_market_data(symbols: List[str]) -> Dict[str, Dict]:
    """Get real-time market data"""
    return await alpaca_connector.fetch_market_data(symbols)

def start_alpaca_feed(symbols: List[str]):
    """Start Alpaca real-time feed in background thread"""
    def run_feed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(alpaca_connector.start_real_time_feed(symbols))
        
    thread = threading.Thread(target=run_feed, daemon=True)
    thread.start()
    return thread
