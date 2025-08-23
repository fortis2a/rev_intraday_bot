"""
Mean Reversion Strategy with Unified Technical Indicators
========================================================
This strategy identifies oversold/overbought conditions using specialized indicators.
Uses unified indicator service to avoid duplication with other systems.

Specialized Indicators:
- Bollinger Bands (focus on band position)
- Stochastic Oscillator (momentum exhaustion)
- Support/Resistance Levels (dynamic levels)

Shared Indicators (from unified service):
- RSI, EMA9/21 (no duplication with confidence monitor)
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta


class MeanReversionStrategy:
    """
    Optimized Mean Reversion Strategy using unified indicators
    Focuses on specialized indicators to avoid duplication
    """

    def __init__(self, symbol: str, timeframe: str = "1min"):
        self.symbol = symbol
        self.timeframe = timeframe
        self.logger = logging.getLogger(__name__)

        # Strategy focuses on specialized indicators only
        self.bb_period = 20
        self.bb_std = 2
        self.stoch_k = 14
        self.stoch_d = 3

        # Risk management
        self.max_position_size = 0.02  # 2% of portfolio
        self.stop_loss_pct = 0.015  # 1.5%
        self.take_profit_pct = 0.025  # 2.5%

    def calculate_support_resistance(
        self, df: pd.DataFrame, window: int = 20
    ) -> Dict[str, float]:
        """Calculate dynamic support and resistance levels"""
        recent_data = df.tail(window * 2)

        # Find local highs and lows
        highs = recent_data["high"].rolling(window=5, center=True).max()
        lows = recent_data["low"].rolling(window=5, center=True).min()

        # Resistance: average of recent highs
        resistance_levels = recent_data[recent_data["high"] == highs]["high"].dropna()
        resistance = (
            resistance_levels.tail(3).mean()
            if len(resistance_levels) > 0
            else recent_data["high"].max()
        )

        # Support: average of recent lows
        support_levels = recent_data[recent_data["low"] == lows]["low"].dropna()
        support = (
            support_levels.tail(3).mean()
            if len(support_levels) > 0
            else recent_data["low"].min()
        )

        return {
            "resistance": resistance,
            "support": support,
            "range_pct": ((resistance - support) / support) * 100,
        }

    def generate_signal(self, symbol: str, df: pd.DataFrame) -> Optional[Dict]:
        """Generate trading signal using unified indicators (no duplication)"""
        try:
            # Import unified service
            from core.unified_indicators import unified_indicator_service

            # Get strategy-specific indicators (avoids duplication)
            indicator_data = unified_indicator_service.get_indicators_for_strategy(
                df, symbol, "mean_reversion"
            )

            if "error" in indicator_data:
                return None

            indicators = indicator_data["indicators"]
            current_values = indicator_data["current_values"]

            # Calculate specialized indicators not in unified service
            sr_levels = self.calculate_support_resistance(df)

            # Mean reversion analysis using specialized indicators
            signal = "HOLD"
            confidence = 0
            reasons = []

            # Get current values
            current_price = current_values["price"]
            current_rsi = current_values["rsi"]
            bb_position = current_values["bb_position"]
            above_ema9 = current_values["above_ema9"]

            # Bollinger Bands analysis (our specialty)
            if bb_position is not None:
                if bb_position < 0.1:  # Near lower band (oversold)
                    signal = "BUY"
                    confidence += 40
                    reasons.append("Price near lower Bollinger Band (oversold)")
                elif bb_position > 0.9:  # Near upper band (overbought)
                    signal = "SELL"
                    confidence += 40
                    reasons.append("Price near upper Bollinger Band (overbought)")

            # Stochastic confirmation (our specialty)
            if len(indicators["stoch_k"]) > 0:
                current_stoch_k = indicators["stoch_k"].iloc[-1]
                if signal == "BUY" and current_stoch_k < 20:
                    confidence += 20
                    reasons.append(f"Stochastic oversold ({current_stoch_k:.1f})")
                elif signal == "SELL" and current_stoch_k > 80:
                    confidence += 20
                    reasons.append(f"Stochastic overbought ({current_stoch_k:.1f})")

            # Support/Resistance confirmation (our specialty)
            distance_to_support = (
                (current_price - sr_levels["support"]) / sr_levels["support"]
            ) * 100
            distance_to_resistance = (
                (sr_levels["resistance"] - current_price) / current_price
            ) * 100

            if signal == "BUY" and distance_to_support < 2:
                confidence += 15
                reasons.append("Near support level")
            elif signal == "SELL" and distance_to_resistance < 2:
                confidence += 15
                reasons.append("Near resistance level")

            # RSI confirmation (shared indicator - no calculation duplication)
            if current_rsi is not None:
                if signal == "BUY" and current_rsi < 30:
                    confidence += 10
                    reasons.append("RSI oversold")
                elif signal == "SELL" and current_rsi > 70:
                    confidence += 10
                    reasons.append("RSI overbought")

            # Volume confirmation (shared indicator)
            if len(indicators["volume_ratio"]) > 0:
                volume_ratio = indicators["volume_ratio"].iloc[-1]
                if volume_ratio > 1.2:
                    confidence += 10
                    reasons.append("Above average volume")

            # Only return signal if confidence meets threshold
            if confidence < 60:
                return None

            # Risk management
            if signal == "BUY":
                entry_price = current_price
                stop_loss = max(
                    sr_levels["support"] * 0.995, entry_price * (1 - self.stop_loss_pct)
                )
                take_profit = min(
                    sr_levels["resistance"] * 0.995,
                    entry_price * (1 + self.take_profit_pct),
                )
            elif signal == "SELL":
                entry_price = current_price
                stop_loss = min(
                    sr_levels["resistance"] * 1.005,
                    entry_price * (1 + self.stop_loss_pct),
                )
                take_profit = max(
                    sr_levels["support"] * 1.005,
                    entry_price * (1 - self.take_profit_pct),
                )
            else:
                return None

            return {
                "symbol": symbol,
                "action": signal,
                "reason": f"Mean Reversion: {', '.join(reasons[:2])}",
                "confidence": confidence / 100.0,  # Convert to 0-1 scale
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "strategy": "mean_reversion_optimized",
                "indicators": {
                    "bb_position": bb_position,
                    "stoch_k": (
                        indicators["stoch_k"].iloc[-1]
                        if len(indicators["stoch_k"]) > 0
                        else None
                    ),
                    "support": sr_levels["support"],
                    "resistance": sr_levels["resistance"],
                },
            }

        except Exception as e:
            self.logger.error(
                f"Mean reversion signal generation failed for {symbol}: {e}"
            )
            return None

    def analyze_market_data(self, df: pd.DataFrame) -> Dict:
        """Comprehensive technical analysis"""
        if len(df) < 50:
            return {"signal": "HOLD", "confidence": 0, "reason": "Insufficient data"}

        # Calculate all indicators
        close_prices = df["close"]

        # RSI
        rsi = self.calculate_rsi(close_prices, self.rsi_period)
        current_rsi = rsi.iloc[-1]

        # Bollinger Bands
        bb = self.calculate_bollinger_bands(close_prices, self.bb_period, self.bb_std)
        current_price = close_prices.iloc[-1]
        bb_position = (current_price - bb["lower"].iloc[-1]) / (
            bb["upper"].iloc[-1] - bb["lower"].iloc[-1]
        )

        # EMA
        ema_fast = self.calculate_ema(close_prices, self.ema_fast)
        ema_slow = self.calculate_ema(close_prices, self.ema_slow)

        # MACD
        macd = self.calculate_macd(
            close_prices, self.macd_fast, self.macd_slow, self.macd_signal
        )

        # Stochastic
        stoch = self.calculate_stochastic(
            df["high"], df["low"], df["close"], self.stoch_k, self.stoch_d
        )

        # Support/Resistance
        sr_levels = self.calculate_support_resistance(df)

        # Volume indicators
        volume_indicators = self.calculate_volume_indicators(df)

        # Analysis logic
        signal = "HOLD"
        confidence = 0
        reasons = []

        # Mean Reversion Signals
        oversold_signals = 0
        overbought_signals = 0

        # RSI Analysis
        if current_rsi < self.rsi_oversold:
            oversold_signals += 1
            reasons.append(f"RSI oversold ({current_rsi:.1f})")
        elif current_rsi > self.rsi_overbought:
            overbought_signals += 1
            reasons.append(f"RSI overbought ({current_rsi:.1f})")

        # Bollinger Bands Analysis
        if bb_position < 0.1:  # Near lower band
            oversold_signals += 1
            reasons.append("Price near lower Bollinger Band")
        elif bb_position > 0.9:  # Near upper band
            overbought_signals += 1
            reasons.append("Price near upper Bollinger Band")

        # Stochastic Analysis
        current_stoch_k = stoch["k"].iloc[-1]
        if current_stoch_k < 20:
            oversold_signals += 1
            reasons.append(f"Stochastic oversold ({current_stoch_k:.1f})")
        elif current_stoch_k > 80:
            overbought_signals += 1
            reasons.append(f"Stochastic overbought ({current_stoch_k:.1f})")

        # Volume confirmation
        volume_confirmation = (
            volume_indicators["volume_ratio"].iloc[-1] > 1.2
        )  # Above average volume

        # Support/Resistance levels
        distance_to_support = (
            (current_price - sr_levels["support"]) / sr_levels["support"]
        ) * 100
        distance_to_resistance = (
            (sr_levels["resistance"] - current_price) / current_price
        ) * 100

        # Generate signals
        if (
            oversold_signals >= 2 and distance_to_support < 2
        ):  # Near support with multiple oversold signals
            signal = "BUY"
            confidence = min(
                95, 40 + (oversold_signals * 15) + (20 if volume_confirmation else 0)
            )
            reasons.append("Multiple oversold indicators near support")

        elif (
            overbought_signals >= 2 and distance_to_resistance < 2
        ):  # Near resistance with multiple overbought signals
            signal = "SELL"
            confidence = min(
                95, 40 + (overbought_signals * 15) + (20 if volume_confirmation else 0)
            )
            reasons.append("Multiple overbought indicators near resistance")

        # MACD divergence check
        if len(macd["histogram"]) > 5:
            recent_histogram = macd["histogram"].tail(5)
            if (
                signal == "BUY"
                and recent_histogram.iloc[-1] > recent_histogram.iloc[-2]
            ):
                confidence += 10
                reasons.append("MACD histogram turning positive")
            elif (
                signal == "SELL"
                and recent_histogram.iloc[-1] < recent_histogram.iloc[-2]
            ):
                confidence += 10
                reasons.append("MACD histogram turning negative")

        # Risk management calculations
        if signal == "BUY":
            entry_price = current_price
            stop_loss = max(
                sr_levels["support"] * 0.995, entry_price * (1 - self.stop_loss_pct)
            )
            take_profit = min(
                sr_levels["resistance"] * 0.995,
                entry_price * (1 + self.take_profit_pct),
            )
        elif signal == "SELL":
            entry_price = current_price
            stop_loss = min(
                sr_levels["resistance"] * 1.005, entry_price * (1 + self.stop_loss_pct)
            )
            take_profit = max(
                sr_levels["support"] * 1.005, entry_price * (1 - self.take_profit_pct)
            )
        else:
            entry_price = stop_loss = take_profit = None

        return {
            "signal": signal,
            "confidence": confidence,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "reasons": reasons,
            "indicators": {
                "rsi": current_rsi,
                "bb_position": bb_position,
                "stoch_k": current_stoch_k,
                "macd": macd["macd"].iloc[-1],
                "macd_signal": macd["signal"].iloc[-1],
                "volume_ratio": volume_indicators["volume_ratio"].iloc[-1],
                "support": sr_levels["support"],
                "resistance": sr_levels["resistance"],
            },
            "timestamp": datetime.now().isoformat(),
        }

    def get_position_size(
        self, account_value: float, risk_per_trade: float = 0.02
    ) -> float:
        """Calculate position size based on risk management"""
        return account_value * min(risk_per_trade, self.max_position_size)

    def validate_signal(self, analysis: Dict, current_positions: Dict) -> bool:
        """Validate if signal should be executed based on current positions and risk"""
        if analysis["confidence"] < 60:
            return False

        # Check if already have position in this symbol
        if self.symbol in current_positions:
            return False

        # Check market conditions (could add more sophisticated filters here)
        return True


def create_mean_reversion_strategy(
    symbol: str, timeframe: str = "1min"
) -> MeanReversionStrategy:
    """Factory function to create a mean reversion strategy instance"""
    return MeanReversionStrategy(symbol, timeframe)


# Example usage
if __name__ == "__main__":
    # Example of how to use the strategy
    strategy = MeanReversionStrategy("AAPL", "1min")

    # Sample data (in real implementation, this would come from your data source)
    sample_data = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                start="2025-08-16 09:30", periods=100, freq="1min"
            ),
            "open": np.random.randn(100).cumsum() + 150,
            "high": np.random.randn(100).cumsum() + 152,
            "low": np.random.randn(100).cumsum() + 148,
            "close": np.random.randn(100).cumsum() + 150,
            "volume": np.random.randint(1000, 10000, 100),
        }
    )

    # Analyze the data
    analysis = strategy.analyze_market_data(sample_data)
    print(f"Signal: {analysis['signal']}")
    print(f"Confidence: {analysis['confidence']}%")
    print(f"Reasons: {', '.join(analysis['reasons'])}")
