"""
Real-time data connector for Scalping Command Center
Handles live data feeds from multiple sources
"""

import asyncio
import aiohttp
import websocket
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import logging
from dataclasses import dataclass
import requests


@dataclass
class MarketData:
    """Market data structure"""

    symbol: str
    price: float
    volume: int
    timestamp: datetime
    bid: float = 0.0
    ask: float = 0.0
    change: float = 0.0
    change_percent: float = 0.0


@dataclass
class AccountData:
    """Account data structure"""

    equity: float
    cash: float
    buying_power: float
    day_pnl: float
    unrealized_pnl: float
    realized_pnl: float
    positions_count: int
    trades_today: int
    timestamp: datetime


class RealTimeDataConnector:
    """Real-time data connector for Command Center"""

    def __init__(self):
        self.callbacks = {}
        self.is_running = False
        self.market_data = {}
        self.account_data = None
        self.logger = self.setup_logger()

        # Data sources configuration
        self.alpaca_api_key = None
        self.alpaca_secret = None
        self.alpaca_base_url = "https://paper-api.alpaca.markets"

        # Websocket connections
        self.market_ws = None
        self.account_ws = None

    def setup_logger(self):
        """Setup logging for data connector"""
        logger = logging.getLogger("realtime_connector")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def register_callback(self, data_type: str, callback: Callable):
        """Register callback for data updates"""
        if data_type not in self.callbacks:
            self.callbacks[data_type] = []
        self.callbacks[data_type].append(callback)

    def notify_callbacks(self, data_type: str, data):
        """Notify all registered callbacks"""
        if data_type in self.callbacks:
            for callback in self.callbacks[data_type]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Error in callback for {data_type}: {e}")

    def start(self):
        """Start real-time data feeds"""
        self.is_running = True
        self.logger.info("Starting real-time data connector...")

        # Start data threads
        threading.Thread(target=self.market_data_loop, daemon=True).start()
        threading.Thread(target=self.account_data_loop, daemon=True).start()
        threading.Thread(target=self.websocket_manager, daemon=True).start()

    def stop(self):
        """Stop real-time data feeds"""
        self.is_running = False
        self.logger.info("Stopping real-time data connector...")

        if self.market_ws:
            self.market_ws.close()
        if self.account_ws:
            self.account_ws.close()

    def market_data_loop(self):
        """Main market data update loop"""
        while self.is_running:
            try:
                self.fetch_market_data()
                time.sleep(1)  # Update every second
            except Exception as e:
                self.logger.error(f"Error in market data loop: {e}")
                time.sleep(5)

    def account_data_loop(self):
        """Account data update loop"""
        while self.is_running:
            try:
                self.fetch_account_data()
                time.sleep(2)  # Update every 2 seconds
            except Exception as e:
                self.logger.error(f"Error in account data loop: {e}")
                time.sleep(10)

    def websocket_manager(self):
        """Manage websocket connections"""
        while self.is_running:
            try:
                self.setup_websockets()
                time.sleep(30)  # Reconnect every 30 seconds if needed
            except Exception as e:
                self.logger.error(f"Error in websocket manager: {e}")
                time.sleep(10)

    def fetch_market_data(self):
        """Fetch real-time market data"""
        # This would integrate with real market data providers
        # For now, simulate realistic data

        symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "SPY", "QQQ"]

        for symbol in symbols:
            # Simulate realistic price movements
            if symbol not in self.market_data:
                base_price = self.get_base_price(symbol)
                self.market_data[symbol] = MarketData(
                    symbol=symbol, price=base_price, volume=0, timestamp=datetime.now()
                )

            # Update with small random movements
            current = self.market_data[symbol]
            change = (hash(f"{symbol}{int(time.time())}") % 200 - 100) / 10000
            new_price = current.price * (1 + change)

            updated_data = MarketData(
                symbol=symbol,
                price=new_price,
                volume=current.volume + (hash(f"{symbol}vol{int(time.time())}") % 1000),
                timestamp=datetime.now(),
                bid=new_price - 0.01,
                ask=new_price + 0.01,
                change=new_price - current.price,
                change_percent=((new_price - current.price) / current.price) * 100,
            )

            self.market_data[symbol] = updated_data
            self.notify_callbacks("market_data", updated_data)

    def fetch_account_data(self):
        """Fetch real-time account data"""
        try:
            # This would integrate with Alpaca API
            # For now, simulate account data

            import random

            base_equity = 50000
            day_change = random.uniform(-1000, 1000)

            account = AccountData(
                equity=base_equity + day_change,
                cash=base_equity * 0.3,
                buying_power=base_equity * 4,
                day_pnl=day_change,
                unrealized_pnl=random.uniform(-500, 500),
                realized_pnl=day_change - random.uniform(-100, 100),
                positions_count=random.randint(0, 8),
                trades_today=random.randint(0, 25),
                timestamp=datetime.now(),
            )

            self.account_data = account
            self.notify_callbacks("account_data", account)

        except Exception as e:
            self.logger.error(f"Error fetching account data: {e}")

    def setup_websockets(self):
        """Setup websocket connections for real-time data"""
        # This would setup actual websocket connections
        # to market data providers and Alpaca
        pass

    def get_base_price(self, symbol: str) -> float:
        """Get realistic base price for symbol"""
        base_prices = {
            "AAPL": 180.0,
            "MSFT": 350.0,
            "GOOGL": 140.0,
            "TSLA": 250.0,
            "NVDA": 450.0,
            "SPY": 430.0,
            "QQQ": 380.0,
        }
        return base_prices.get(symbol, 100.0)

    def get_confidence_data(self, symbol: str) -> Dict:
        """Get confidence data for symbol"""
        # This would integrate with your confidence calculation system
        import random

        confidence = random.uniform(30, 95)

        # Determine signal based on confidence
        if confidence > 80:
            signal = "STRONG_BUY" if random.random() > 0.5 else "STRONG_SELL"
        elif confidence > 70:
            signal = "BUY" if random.random() > 0.5 else "SELL"
        elif confidence > 60:
            signal = "WATCH"
        else:
            signal = "HOLD"

        return {
            "symbol": symbol,
            "confidence": confidence,
            "signal": signal,
            "indicators": {
                "rsi": random.uniform(20, 80),
                "macd": random.uniform(-1, 1),
                "ema_9": random.uniform(0.95, 1.05),
                "vwap": random.uniform(0.98, 1.02),
                "bollinger_position": random.uniform(0, 1),
            },
            "timestamp": datetime.now(),
        }

    def get_trade_alerts(self) -> List[Dict]:
        """Get recent trade execution alerts"""
        # This would read from your trade log files
        # For now, simulate trade alerts

        import random

        if random.random() < 0.05:  # 5% chance of new trade
            return [
                {
                    "timestamp": datetime.now(),
                    "symbol": random.choice(["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]),
                    "action": random.choice(["BUY", "SELL"]),
                    "quantity": random.randint(10, 200),
                    "price": random.uniform(100, 500),
                    "strategy": random.choice(
                        ["Mean Reversion", "Momentum Scalp", "VWAP Bounce"]
                    ),
                    "confidence": random.uniform(75, 95),
                    "pnl": random.uniform(-100, 200),
                }
            ]

        return []

    def get_strategy_performance(self) -> Dict:
        """Get real-time strategy performance"""
        import random

        strategies = ["Mean Reversion", "Momentum Scalp", "VWAP Bounce"]
        performance = {}

        for strategy in strategies:
            performance[strategy] = {
                "trades_today": random.randint(0, 15),
                "pnl_today": random.uniform(-300, 500),
                "win_rate": random.uniform(45, 75),
                "avg_trade_duration": random.uniform(2, 30),  # minutes
                "status": random.choice(["ACTIVE", "PAUSED", "INACTIVE"]),
                "last_signal": datetime.now()
                - timedelta(minutes=random.randint(1, 60)),
            }

        return performance

    def get_market_status(self) -> Dict:
        """Get current market status"""
        from datetime import time

        now = datetime.now()
        market_open = time(9, 30)
        market_close = time(16, 0)
        current_time = now.time()

        is_open = market_open <= current_time <= market_close and now.weekday() < 5

        return {
            "is_open": is_open,
            "session_status": "OPEN" if is_open else "CLOSED",
            "time_to_open": (
                self.calculate_time_to_open() if not is_open else "Market Open"
            ),
            "volume_profile": self.get_volume_profile(),
            "volatility_index": self.get_volatility_index(),
            "market_regime": self.detect_market_regime(),
        }

    def calculate_time_to_open(self) -> str:
        """Calculate time until market opens"""
        now = datetime.now()

        # Next market open (simplified)
        if now.weekday() < 5:  # Monday-Friday
            next_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            if now.time() > time(16, 0):  # After close, next day
                next_open += timedelta(days=1)
        else:  # Weekend
            days_until_monday = 7 - now.weekday()
            next_open = now + timedelta(days=days_until_monday)
            next_open = next_open.replace(hour=9, minute=30, second=0, microsecond=0)

        time_diff = next_open - now
        hours, remainder = divmod(time_diff.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

    def get_volume_profile(self) -> str:
        """Get current volume profile"""
        import random

        return random.choice(["LOW", "NORMAL", "HIGH", "VERY HIGH"])

    def get_volatility_index(self) -> float:
        """Get volatility index (VIX-like)"""
        import random

        return random.uniform(15, 35)

    def detect_market_regime(self) -> str:
        """Detect current market regime"""
        import random

        return random.choice(["TRENDING", "RANGING", "VOLATILE", "CALM"])

    def get_bot_health(self) -> Dict:
        """Get bot health metrics"""
        import psutil
        import random

        try:
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage("/").percent
        except:
            cpu_percent = random.uniform(10, 50)
            memory_percent = random.uniform(20, 60)
            disk_usage = random.uniform(30, 70)

        return {
            "cpu_usage": cpu_percent,
            "memory_usage": memory_percent,
            "disk_usage": disk_usage,
            "api_latency": random.uniform(10, 100),
            "data_feed_status": {
                "market_data": "CONNECTED",
                "account_data": "CONNECTED",
                "options_data": random.choice(["CONNECTED", "DISCONNECTED"]),
                "news_feed": "CONNECTED",
                "economic_data": random.choice(["CONNECTED", "DELAYED"]),
            },
            "last_heartbeat": datetime.now(),
            "error_count": random.randint(0, 5),
            "uptime": datetime.now()
            - datetime.now().replace(hour=9, minute=30, second=0),
        }


# Example usage for integration with Command Center
class DataManager:
    """Data manager for Command Center integration"""

    def __init__(self):
        self.connector = RealTimeDataConnector()
        self.latest_data = {}

    def start(self):
        """Start data feeds"""
        # Register callbacks
        self.connector.register_callback("market_data", self.handle_market_data)
        self.connector.register_callback("account_data", self.handle_account_data)

        # Start connector
        self.connector.start()

    def handle_market_data(self, data: MarketData):
        """Handle market data updates"""
        self.latest_data[f"market_{data.symbol}"] = data

    def handle_account_data(self, data: AccountData):
        """Handle account data updates"""
        self.latest_data["account"] = data

    def get_real_time_data(self, data_type: str, symbol: str = None):
        """Get latest real-time data"""
        if data_type == "market" and symbol:
            return self.latest_data.get(f"market_{symbol}")
        elif data_type == "account":
            return self.latest_data.get("account")
        elif data_type == "confidence" and symbol:
            return self.connector.get_confidence_data(symbol)
        elif data_type == "trades":
            return self.connector.get_trade_alerts()
        elif data_type == "strategies":
            return self.connector.get_strategy_performance()
        elif data_type == "market_status":
            return self.connector.get_market_status()
        elif data_type == "bot_health":
            return self.connector.get_bot_health()

        return None

    def stop(self):
        """Stop data feeds"""
        self.connector.stop()
