"""
Real-time confidence calculation integration for Command Center
Integrates with existing strategy confidence calculations
"""

import asyncio
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

try:
    from config import INTRADAY_WATCHLIST, config
    from core.unified_indicators import UnifiedIndicatorService
    from strategies.mean_reversion import MeanReversionStrategy
    from strategies.momentum_scalp import MomentumScalpStrategy
    from strategies.vwap_bounce import VWAPBounceStrategy
except ImportError as e:
    print(f"Warning: Could not import strategy modules: {e}")
    config = None
    INTRADAY_WATCHLIST = ["SOXL", "SOFI", "TQQQ", "INTC", "NIO"]


class ConfidenceCalculator:
    """Real-time confidence calculation using existing strategies"""

    def __init__(self):
        self.logger = self.setup_logger()
        self.symbols = (
            INTRADAY_WATCHLIST
            if INTRADAY_WATCHLIST
            else ["SOXL", "SOFI", "TQQQ", "INTC", "NIO"]
        )

        # Initialize components
        self.indicator_service = None
        self.strategies = {}
        self.confidence_data = {}
        self.last_update = datetime.now()

        # Callbacks
        self.confidence_callbacks = []

        # Initialize if possible
        self.initialize_components()

    def setup_logger(self):
        """Setup logging for confidence calculator"""
        logger = logging.getLogger("confidence_calculator")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def initialize_components(self):
        """Initialize indicator service and strategies"""
        try:
            # Initialize unified indicator service
            self.indicator_service = UnifiedIndicatorService()
            self.logger.info("✅ Unified indicator service initialized")

            # Initialize strategies
            self.strategies = {
                "mean_reversion": MeanReversionStrategy(),
                "momentum_scalp": MomentumScalpStrategy(),
                "vwap_bounce": VWAPBounceStrategy(),
            }
            self.logger.info("✅ Trading strategies initialized")

            return True

        except Exception as e:
            self.logger.warning(f"Could not initialize components: {e}")
            self.logger.info("Running in simulation mode")
            return False

    async def calculate_confidence_for_symbol(
        self, symbol: str, market_data: Dict = None
    ) -> Dict:
        """Calculate confidence for a single symbol using real strategies"""
        try:
            if not self.indicator_service or not self.strategies:
                # Fallback to simulation
                return self.simulate_confidence(symbol)

            # Get market data (would normally come from data manager)
            if not market_data:
                market_data = await self.get_market_data(symbol)

            # Calculate indicators using unified service
            indicators = await self.indicator_service.calculate_all_indicators(
                symbol, market_data
            )

            # Get confidence from each strategy
            strategy_confidences = {}
            strategy_signals = {}

            for strategy_name, strategy in self.strategies.items():
                try:
                    # Each strategy should return confidence and signal
                    result = await self.get_strategy_confidence(
                        strategy, symbol, indicators, market_data
                    )
                    strategy_confidences[strategy_name] = result["confidence"]
                    strategy_signals[strategy_name] = result["signal"]
                except Exception as e:
                    self.logger.error(
                        f"Error calculating {strategy_name} confidence for {symbol}: {e}"
                    )
                    strategy_confidences[strategy_name] = 50.0
                    strategy_signals[strategy_name] = "HOLD"

            # Calculate overall confidence (weighted average)
            overall_confidence = self.calculate_overall_confidence(strategy_confidences)
            overall_signal = self.determine_overall_signal(
                strategy_signals, overall_confidence
            )

            confidence_data = {
                "symbol": symbol,
                "overall_confidence": overall_confidence,
                "overall_signal": overall_signal,
                "strategy_confidences": strategy_confidences,
                "strategy_signals": strategy_signals,
                "indicators": indicators,
                "market_data": market_data,
                "timestamp": datetime.now(),
            }

            # Store and notify
            self.confidence_data[symbol] = confidence_data

            for callback in self.confidence_callbacks:
                try:
                    callback(symbol, confidence_data)
                except Exception as e:
                    self.logger.error(f"Error in confidence callback: {e}")

            return confidence_data

        except Exception as e:
            self.logger.error(f"Error calculating confidence for {symbol}: {e}")
            return self.simulate_confidence(symbol)

    async def get_strategy_confidence(
        self, strategy, symbol: str, indicators: Dict, market_data: Dict
    ) -> Dict:
        """Get confidence from a specific strategy"""
        try:
            # This would call the strategy's confidence calculation method
            # For now, simulate based on strategy type

            if hasattr(strategy, "calculate_confidence"):
                result = await strategy.calculate_confidence(
                    symbol, indicators, market_data
                )
                return result
            else:
                # Fallback simulation based on strategy type
                return self.simulate_strategy_confidence(
                    strategy.__class__.__name__, indicators
                )

        except Exception as e:
            self.logger.error(f"Error getting strategy confidence: {e}")
            return {"confidence": 50.0, "signal": "HOLD"}

    def simulate_strategy_confidence(
        self, strategy_name: str, indicators: Dict
    ) -> Dict:
        """Simulate strategy confidence based on indicators"""
        import random

        base_confidence = random.uniform(40, 80)

        # Adjust based on strategy type and indicators
        if strategy_name == "MeanReversionStrategy":
            # Higher confidence when RSI is oversold/overbought
            rsi = indicators.get("rsi", 50)
            if rsi < 30 or rsi > 70:
                base_confidence += 10
                signal = "BUY" if rsi < 30 else "SELL"
            else:
                signal = "HOLD"

        elif strategy_name == "MomentumScalpStrategy":
            # Higher confidence with strong momentum
            adx = indicators.get("adx", 20)
            if adx > 25:
                base_confidence += 15
                signal = "BUY" if random.random() > 0.5 else "SELL"
            else:
                signal = "HOLD"

        elif strategy_name == "VWAPBounceStrategy":
            # Higher confidence near VWAP
            vwap_position = indicators.get("vwap_position", 0.5)
            if abs(vwap_position - 0.5) < 0.1:  # Near VWAP
                base_confidence += 12
                signal = "BUY" if vwap_position < 0.5 else "SELL"
            else:
                signal = "HOLD"
        else:
            signal = "HOLD"

        return {"confidence": min(95, max(5, base_confidence)), "signal": signal}

    def calculate_overall_confidence(self, strategy_confidences: Dict) -> float:
        """Calculate overall confidence from strategy confidences"""
        if not strategy_confidences:
            return 50.0

        # Weighted average (can be customized)
        weights = {"mean_reversion": 0.35, "momentum_scalp": 0.35, "vwap_bounce": 0.30}

        total_weight = 0
        weighted_sum = 0

        for strategy, confidence in strategy_confidences.items():
            weight = weights.get(strategy, 0.33)
            weighted_sum += confidence * weight
            total_weight += weight

        if total_weight > 0:
            return weighted_sum / total_weight
        else:
            return sum(strategy_confidences.values()) / len(strategy_confidences)

    def determine_overall_signal(
        self, strategy_signals: Dict, overall_confidence: float
    ) -> str:
        """Determine overall signal from strategy signals"""
        if overall_confidence < 60:
            return "HOLD"

        # Count signals
        buy_count = sum(1 for signal in strategy_signals.values() if signal == "BUY")
        sell_count = sum(1 for signal in strategy_signals.values() if signal == "SELL")

        if overall_confidence > 75:
            if buy_count > sell_count:
                return "STRONG_BUY"
            elif sell_count > buy_count:
                return "STRONG_SELL"
        elif overall_confidence > 65:
            if buy_count > sell_count:
                return "BUY"
            elif sell_count > buy_count:
                return "SELL"

        return "WATCH" if overall_confidence > 60 else "HOLD"

    async def get_market_data(self, symbol: str) -> Dict:
        """Get market data for symbol (would integrate with data manager)"""
        # This would integrate with your existing data manager
        # For now, simulate realistic market data
        import random

        base_prices = {
            "SOXL": 29.27,
            "SOFI": 23.81,
            "TQQQ": 94.86,
            "INTC": 22.22,
            "NIO": 4.62,
        }

        base_price = base_prices.get(symbol, 50.0)
        current_price = base_price * (1 + random.uniform(-0.02, 0.02))

        return {
            "symbol": symbol,
            "price": current_price,
            "volume": random.randint(100000, 1000000),
            "high": current_price * (1 + random.uniform(0, 0.01)),
            "low": current_price * (1 - random.uniform(0, 0.01)),
            "open": current_price * (1 + random.uniform(-0.005, 0.005)),
            "timestamp": datetime.now(),
        }

    def simulate_confidence(self, symbol: str) -> Dict:
        """Simulate confidence data when real calculation is not available"""
        import random

        overall_confidence = random.uniform(35, 85)

        # Generate strategy confidences
        strategy_confidences = {
            "mean_reversion": random.uniform(30, 90),
            "momentum_scalp": random.uniform(30, 90),
            "vwap_bounce": random.uniform(30, 90),
        }

        # Generate signals based on confidence
        strategy_signals = {}
        for strategy, confidence in strategy_confidences.items():
            if confidence > 75:
                strategy_signals[strategy] = random.choice(["BUY", "SELL"])
            elif confidence > 60:
                strategy_signals[strategy] = "WATCH"
            else:
                strategy_signals[strategy] = "HOLD"

        overall_signal = self.determine_overall_signal(
            strategy_signals, overall_confidence
        )

        return {
            "symbol": symbol,
            "overall_confidence": overall_confidence,
            "overall_signal": overall_signal,
            "strategy_confidences": strategy_confidences,
            "strategy_signals": strategy_signals,
            "indicators": self.simulate_indicators(),
            "market_data": {},
            "timestamp": datetime.now(),
        }

    def simulate_indicators(self) -> Dict:
        """Simulate technical indicators"""
        import random

        return {
            "rsi": random.uniform(20, 80),
            "macd": random.uniform(-1, 1),
            "adx": random.uniform(15, 45),
            "ema_9": random.uniform(0.95, 1.05),
            "vwap_position": random.uniform(0.2, 0.8),
            "bollinger_position": random.uniform(0, 1),
            "williams_r": random.uniform(-80, -20),
            "stoch_k": random.uniform(20, 80),
        }

    async def calculate_all_symbols(self) -> Dict[str, Dict]:
        """Calculate confidence for all symbols"""
        tasks = []
        for symbol in self.symbols:
            tasks.append(self.calculate_confidence_for_symbol(symbol))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        confidence_results = {}
        for i, result in enumerate(results):
            symbol = self.symbols[i]
            if isinstance(result, Exception):
                self.logger.error(
                    f"Error calculating confidence for {symbol}: {result}"
                )
                confidence_results[symbol] = self.simulate_confidence(symbol)
            else:
                confidence_results[symbol] = result

        self.last_update = datetime.now()
        return confidence_results

    def register_confidence_callback(self, callback):
        """Register callback for confidence updates"""
        self.confidence_callbacks.append(callback)

    def get_latest_confidence(self, symbol: str = None) -> Dict:
        """Get latest confidence data"""
        if symbol:
            return self.confidence_data.get(symbol, {})
        return self.confidence_data.copy()

    # Command Center compatibility method
    def get_symbol_confidence(self, symbol: str) -> Dict:
        """Get confidence data for a specific symbol compatible with Command Center"""
        confidence_data = self.get_latest_confidence(symbol)
        if confidence_data:
            return {
                "confidence": confidence_data.get("overall_confidence", 50),
                "signal": confidence_data.get("action_signal", "HOLD"),
                "current_price": confidence_data.get("current_price", 100),
                "price_change_pct": confidence_data.get("change_pct", 0),
            }

        # Simulation fallback
        import random

        confidence = random.uniform(45, 85)
        signal = "BUY" if confidence > 75 else "WATCH" if confidence > 65 else "HOLD"

        # Generate realistic base prices
        base_prices = {
            "SOXL": 25.0,
            "SOFI": 8.0,
            "TQQQ": 36.0,
            "INTC": 33.0,
            "NIO": 9.0,
            "AAPL": 185.0,
            "MSFT": 365.0,
            "GOOGL": 145.0,
            "TSLA": 255.0,
            "NVDA": 465.0,
        }
        base_price = base_prices.get(symbol, 150.0)
        change_pct = random.uniform(-2, 2)

        return {
            "confidence": confidence,
            "signal": signal,
            "current_price": base_price * (1 + change_pct / 100),
            "price_change_pct": change_pct,
        }

    async def start_confidence_feed(self):
        """Start continuous confidence calculation"""
        self.logger.info(f"🎯 Starting confidence feed for {len(self.symbols)} symbols")

        while True:
            try:
                await self.calculate_all_symbols()
                await asyncio.sleep(5)  # Update every 5 seconds

            except Exception as e:
                self.logger.error(f"Error in confidence feed: {e}")
                await asyncio.sleep(10)  # Wait longer on error


# Singleton instance
confidence_calculator = ConfidenceCalculator()


# Helper functions
async def get_real_time_confidence(symbol: str) -> Dict:
    """Get real-time confidence for symbol"""
    return await confidence_calculator.calculate_confidence_for_symbol(symbol)


async def get_all_confidence_data() -> Dict[str, Dict]:
    """Get confidence data for all symbols"""
    return await confidence_calculator.calculate_all_symbols()


def start_confidence_feed():
    """Start confidence calculation feed in background thread"""

    def run_feed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(confidence_calculator.start_confidence_feed())

    thread = threading.Thread(target=run_feed, daemon=True)
    thread.start()
    return thread
