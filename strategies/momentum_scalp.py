"""
Momentum Scalping Strategy with Specialized Technical Indicators
==============================================================
This strategy focuses on momentum indicators unique to scalping.
Uses unified indicator service to avoid duplication with other systems.

Specialized Indicators:
- ADX (Average Directional Index) - trend strength
- Williams %R - momentum oscillator
- Rate of Change (ROC) - price momentum
- Multi-EMA system (8/13/50) - extended trend analysis

Shared Indicators (from unified service):
- MACD, VWAP, EMA9/21 (no duplication with confidence monitor)
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta


class MomentumScalpStrategy:
    """
    Optimized momentum scalping strategy using specialized indicators
    Focuses on unique momentum indicators to avoid duplication
    """

    def __init__(self, symbol: str, timeframe: str = "1min"):
        self.symbol = symbol
        self.timeframe = timeframe
        self.logger = logging.getLogger(__name__)

        # Specialized indicator settings
        self.adx_period = 14
        self.adx_threshold = 25  # Minimum ADX for trend strength
        self.williams_period = 14
        self.roc_period = 10

        # Risk management for scalping
        self.max_position_size = 0.01  # 1% of portfolio (smaller for scalping)
        self.stop_loss_pct = 0.008  # 0.8% (tight stops for scalping)
        self.take_profit_pct = 0.012  # 1.2% (quick profits)
        self.max_holding_minutes = 15  # Maximum holding time for scalp

    def calculate_adx(self, df: pd.DataFrame, period: int = 14) -> Dict[str, pd.Series]:
        """Calculate Average Directional Index (specialized indicator)"""
        high = df["high"]
        low = df["low"]
        close = df["close"]

        # True Range calculation
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Directional Movement calculation
        dm_plus = high.diff()
        dm_minus = low.diff() * -1

        dm_plus[dm_plus < 0] = 0
        dm_minus[dm_minus < 0] = 0
        dm_plus[(dm_plus - dm_minus) <= 0] = 0
        dm_minus[(dm_minus - dm_plus) <= 0] = 0

        # Smoothed averages
        atr = true_range.rolling(window=period).mean()
        di_plus = (dm_plus.rolling(window=period).mean() / atr) * 100
        di_minus = (dm_minus.rolling(window=period).mean() / atr) * 100

        # ADX calculation
        dx = abs(di_plus - di_minus) / (di_plus + di_minus) * 100
        adx = dx.rolling(window=period).mean()

        return {"adx": adx, "di_plus": di_plus, "di_minus": di_minus, "atr": atr}

    def detect_momentum_patterns(
        self, indicators: Dict, current_price: float
    ) -> Dict[str, bool]:
        """Detect specific momentum patterns using specialized indicators"""

        # EMA alignment for trend (using specialized EMA periods)
        ema_9 = indicators["ema_9"].iloc[-1]
        ema_13 = indicators["ema_13"].iloc[-1]
        ema_21 = indicators["ema_21"].iloc[-1]
        ema_50 = indicators["ema_50"].iloc[-1]

        # Check specialized EMA alignment
        bullish_ema_alignment = ema_9 > ema_13 > ema_21 > ema_50
        bearish_ema_alignment = ema_9 < ema_13 < ema_21 < ema_50

        # Price above/below EMAs
        price_above_emas = current_price > ema_9
        price_below_emas = current_price < ema_9

        # Recent breakout detection
        recent_high = current_price * 1.001  # Simple breakout detection
        recent_low = current_price * 0.999

        # ROC momentum acceleration
        if len(indicators["roc"]) > 1:
            roc_current = indicators["roc"].iloc[-1]
            roc_prev = indicators["roc"].iloc[-2]
            momentum_accelerating = roc_current > roc_prev
            momentum_decelerating = roc_current < roc_prev
        else:
            momentum_accelerating = False
            momentum_decelerating = False

        return {
            "bullish_ema_alignment": bullish_ema_alignment,
            "bearish_ema_alignment": bearish_ema_alignment,
            "price_above_emas": price_above_emas,
            "price_below_emas": price_below_emas,
            "momentum_accelerating": momentum_accelerating,
            "momentum_decelerating": momentum_decelerating,
        }

    def generate_signal(self, symbol: str, df: pd.DataFrame) -> Optional[Dict]:
        """Generate trading signal using specialized momentum indicators"""
        try:
            # Import unified service
            from core.unified_indicators import unified_indicator_service

            # Get strategy-specific indicators (avoids duplication)
            indicator_data = unified_indicator_service.get_indicators_for_strategy(
                df, symbol, "momentum_scalp"
            )

            if "error" in indicator_data:
                return None

            indicators = indicator_data["indicators"]
            current_values = indicator_data["current_values"]
            current_price = current_values["price"]

            # Calculate specialized indicators not in unified service
            adx_indicators = self.calculate_adx(df, self.adx_period)

            # Detect momentum patterns using specialized indicators
            patterns = self.detect_momentum_patterns(indicators, current_price)

            # Signal generation using specialized momentum indicators
            signal = "HOLD"
            confidence = 0
            reasons = []

            bullish_signals = 0
            bearish_signals = 0

            # ADX trend strength (our specialty)
            if len(adx_indicators["adx"]) > 0:
                current_adx = adx_indicators["adx"].iloc[-1]
                current_di_plus = adx_indicators["di_plus"].iloc[-1]
                current_di_minus = adx_indicators["di_minus"].iloc[-1]

                strong_trend = current_adx > self.adx_threshold
                if strong_trend:
                    if current_di_plus > current_di_minus:
                        bullish_signals += 2
                        reasons.append(f"Strong uptrend (ADX: {current_adx:.1f})")
                    else:
                        bearish_signals += 2
                        reasons.append(f"Strong downtrend (ADX: {current_adx:.1f})")

            # Williams %R momentum (our specialty)
            if len(indicators["williams_r"]) > 0:
                current_williams = indicators["williams_r"].iloc[-1]
                if (
                    current_williams > -20 and patterns["momentum_accelerating"]
                ):  # Momentum continuation
                    bullish_signals += 1
                    reasons.append(f"Williams %R momentum continuation")
                elif current_williams < -80 and patterns["momentum_accelerating"]:
                    bearish_signals += 1
                    reasons.append(f"Williams %R bearish momentum")

            # Rate of Change (our specialty)
            if len(indicators["roc"]) > 0:
                current_roc = indicators["roc"].iloc[-1]
                if current_roc > 1.0:  # Strong positive momentum
                    bullish_signals += 2
                    reasons.append(
                        f"Strong positive momentum (ROC: {current_roc:.2f}%)"
                    )
                elif current_roc < -1.0:  # Strong negative momentum
                    bearish_signals += 2
                    reasons.append(
                        f"Strong negative momentum (ROC: {current_roc:.2f}%)"
                    )

            # MACD confirmation (shared indicator - no calculation duplication)
            macd_bullish = current_values["macd_bullish"]
            if macd_bullish and patterns["bullish_ema_alignment"]:
                bullish_signals += 1
                reasons.append("MACD + EMA alignment bullish")
            elif not macd_bullish and patterns["bearish_ema_alignment"]:
                bearish_signals += 1
                reasons.append("MACD + EMA alignment bearish")

            # VWAP position (shared indicator)
            above_vwap = current_values["above_vwap"]
            if above_vwap and patterns["momentum_accelerating"]:
                bullish_signals += 0.5
                reasons.append("Above VWAP with momentum")
            elif not above_vwap and patterns["momentum_accelerating"]:
                bearish_signals += 0.5
                reasons.append("Below VWAP with momentum")

            # Volume confirmation (shared indicator)
            if len(indicators["volume_ratio"]) > 0:
                volume_ratio = indicators["volume_ratio"].iloc[-1]
                volume_confirmation = volume_ratio > 1.5
                if volume_confirmation:
                    reasons.append(f"High volume ({volume_ratio:.1f}x)")
            else:
                volume_confirmation = False

            # Generate final signal (require multiple specialized confirmations)
            min_signals = 2.5

            if bullish_signals >= min_signals and volume_confirmation:
                signal = "BUY"
                base_confidence = 50 + (bullish_signals * 10)
                trend_bonus = 15 if strong_trend else 0
                volume_bonus = 10 if volume_ratio > 2.0 else 0
                confidence = min(95, base_confidence + trend_bonus + volume_bonus)

            elif bearish_signals >= min_signals and volume_confirmation:
                signal = "SELL"
                base_confidence = 50 + (bearish_signals * 10)
                trend_bonus = 15 if strong_trend else 0
                volume_bonus = 10 if volume_ratio > 2.0 else 0
                confidence = min(95, base_confidence + trend_bonus + volume_bonus)

            # Only return signal if confidence meets threshold
            if confidence < 65:
                return None

            # Risk management for scalping
            if signal in ["BUY", "SELL"]:
                atr = (
                    adx_indicators["atr"].iloc[-1]
                    if len(adx_indicators["atr"]) > 0
                    else current_price * 0.01
                )

                if signal == "BUY":
                    entry_price = current_price
                    stop_loss = entry_price - (atr * 1.5)  # ATR-based stop
                    take_profit = entry_price + (atr * 2.0)  # ATR-based target
                else:  # SELL
                    entry_price = current_price
                    stop_loss = entry_price + (atr * 1.5)
                    take_profit = entry_price - (atr * 2.0)
            else:
                return None

            return {
                "symbol": symbol,
                "action": signal,
                "reason": f"Momentum Scalp: {', '.join(reasons[:2])}",
                "confidence": confidence / 100.0,  # Convert to 0-1 scale
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "max_holding_minutes": self.max_holding_minutes,
                "strategy": "momentum_scalp_optimized",
                "indicators": {
                    "adx": current_adx if "current_adx" in locals() else None,
                    "williams_r": (
                        current_williams if "current_williams" in locals() else None
                    ),
                    "roc": current_roc if "current_roc" in locals() else None,
                    "atr": atr,
                },
            }

        except Exception as e:
            self.logger.error(
                f"Momentum scalp signal generation failed for {symbol}: {e}"
            )
            return None

    def analyze_market_data(self, df: pd.DataFrame) -> Dict:
        """Comprehensive momentum analysis for scalping opportunities"""
        if len(df) < 60:
            return {"signal": "HOLD", "confidence": 0, "reason": "Insufficient data"}

        close_prices = df["close"]
        current_price = close_prices.iloc[-1]

        # Calculate all indicators
        macd = self.calculate_macd(
            close_prices, self.macd_fast, self.macd_slow, self.macd_signal
        )
        adx_indicators = self.calculate_adx(df, self.adx_period)
        williams_r = self.calculate_williams_r(df, self.williams_period)
        roc = self.calculate_rate_of_change(close_prices, self.roc_period)
        momentum = self.calculate_momentum(close_prices, self.momentum_period)
        vwap = self.calculate_vwap(df)
        volume_indicators = self.calculate_volume_indicators(df)
        patterns = self.detect_momentum_patterns(df)

        # Current values
        current_macd = macd["macd"].iloc[-1]
        current_macd_signal = macd["signal"].iloc[-1]
        current_macd_hist = macd["histogram"].iloc[-1]
        current_adx = adx_indicators["adx"].iloc[-1]
        current_di_plus = adx_indicators["di_plus"].iloc[-1]
        current_di_minus = adx_indicators["di_minus"].iloc[-1]
        current_williams = williams_r.iloc[-1]
        current_roc = roc.iloc[-1]
        current_momentum = momentum.iloc[-1]
        current_vwap = vwap.iloc[-1]
        current_relative_volume = volume_indicators["relative_volume"].iloc[-1]
        current_mfi = volume_indicators["mfi"].iloc[-1]

        # Signal generation logic
        signal = "HOLD"
        confidence = 0
        reasons = []

        # Bullish momentum signals
        bullish_signals = 0
        bearish_signals = 0

        # MACD analysis
        if current_macd > current_macd_signal and current_macd_hist > 0:
            bullish_signals += 1
            reasons.append("MACD bullish crossover")
        elif current_macd < current_macd_signal and current_macd_hist < 0:
            bearish_signals += 1
            reasons.append("MACD bearish crossover")

        # ADX trend strength
        strong_trend = current_adx > self.adx_threshold
        if strong_trend:
            if current_di_plus > current_di_minus:
                bullish_signals += 1
                reasons.append(f"Strong uptrend (ADX: {current_adx:.1f})")
            else:
                bearish_signals += 1
                reasons.append(f"Strong downtrend (ADX: {current_adx:.1f})")

        # Williams %R momentum
        if current_williams > -20:  # Overbought but with momentum
            if patterns["momentum_accelerating"]:
                bullish_signals += 0.5
        elif current_williams < -80:  # Oversold but with momentum
            if patterns["momentum_accelerating"]:
                bearish_signals += 0.5

        # Rate of Change
        if current_roc > 0.5:  # Positive momentum
            bullish_signals += 1
            reasons.append(f"Positive momentum (ROC: {current_roc:.2f}%)")
        elif current_roc < -0.5:  # Negative momentum
            bearish_signals += 1
            reasons.append(f"Negative momentum (ROC: {current_roc:.2f}%)")

        # VWAP position
        vwap_distance = ((current_price - current_vwap) / current_vwap) * 100
        if abs(vwap_distance) < 0.1:  # Near VWAP
            if current_price > current_vwap and patterns["momentum_accelerating"]:
                bullish_signals += 0.5
                reasons.append("Breaking above VWAP with momentum")
            elif current_price < current_vwap and patterns["momentum_accelerating"]:
                bearish_signals += 0.5
                reasons.append("Breaking below VWAP with momentum")

        # Volume confirmation
        volume_confirmation = current_relative_volume > self.volume_threshold
        if volume_confirmation:
            reasons.append(f"High relative volume ({current_relative_volume:.1f}x)")

        # Pattern confirmation
        if patterns["bullish_ema_alignment"] and patterns["breakout_high"]:
            bullish_signals += 1
            reasons.append("Bullish EMA alignment with breakout")
        elif patterns["bearish_ema_alignment"] and patterns["breakout_low"]:
            bearish_signals += 1
            reasons.append("Bearish EMA alignment with breakdown")

        # Generate final signal
        min_signals = 2.5  # Require multiple confirmations for scalping

        if bullish_signals >= min_signals and volume_confirmation:
            signal = "BUY"
            base_confidence = 50 + (bullish_signals * 10)
            trend_bonus = 15 if strong_trend else 0
            volume_bonus = 10 if current_relative_volume > 2.0 else 0
            confidence = min(95, base_confidence + trend_bonus + volume_bonus)

        elif bearish_signals >= min_signals and volume_confirmation:
            signal = "SELL"
            base_confidence = 50 + (bearish_signals * 10)
            trend_bonus = 15 if strong_trend else 0
            volume_bonus = 10 if current_relative_volume > 2.0 else 0
            confidence = min(95, base_confidence + trend_bonus + volume_bonus)

        # Risk management for scalping
        if signal in ["BUY", "SELL"]:
            atr = adx_indicators["atr"].iloc[-1]

            if signal == "BUY":
                entry_price = current_price
                stop_loss = entry_price - (atr * 1.5)  # ATR-based stop
                take_profit = entry_price + (atr * 2.0)  # ATR-based target
            else:  # SELL
                entry_price = current_price
                stop_loss = entry_price + (atr * 1.5)
                take_profit = entry_price - (atr * 2.0)
        else:
            entry_price = stop_loss = take_profit = None

        return {
            "signal": signal,
            "confidence": confidence,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "max_holding_minutes": self.max_holding_minutes,
            "reasons": reasons,
            "indicators": {
                "macd": current_macd,
                "macd_signal": current_macd_signal,
                "macd_histogram": current_macd_hist,
                "adx": current_adx,
                "di_plus": current_di_plus,
                "di_minus": current_di_minus,
                "williams_r": current_williams,
                "roc": current_roc,
                "momentum": current_momentum,
                "vwap": current_vwap,
                "vwap_distance_pct": vwap_distance,
                "relative_volume": current_relative_volume,
                "mfi": current_mfi,
            },
            "patterns": patterns,
            "timestamp": datetime.now().isoformat(),
        }

    def get_scalp_position_size(self, account_value: float, volatility: float) -> float:
        """Calculate position size for scalping based on volatility"""
        base_size = account_value * self.max_position_size

        # Adjust for volatility (reduce size in high volatility)
        if volatility > 0.02:  # High volatility
            base_size *= 0.5
        elif volatility > 0.015:  # Medium volatility
            base_size *= 0.75

        return base_size

    def should_exit_scalp(
        self, entry_time: datetime, current_pnl_pct: float
    ) -> Tuple[bool, str]:
        """Determine if scalp position should be exited based on time and P&L"""
        minutes_held = (datetime.now() - entry_time).total_seconds() / 60

        # Time-based exit
        if minutes_held >= self.max_holding_minutes:
            return True, "Max holding time reached"

        # Quick profit taking for scalps
        if current_pnl_pct >= 0.008:  # 0.8% profit
            return True, "Quick scalp profit target hit"

        # Quick stop loss
        if current_pnl_pct <= -0.005:  # 0.5% loss
            return True, "Quick scalp stop loss"

        return False, ""


def create_momentum_scalp_strategy(
    symbol: str, timeframe: str = "1min"
) -> MomentumScalpStrategy:
    """Factory function to create a momentum scalping strategy instance"""
    return MomentumScalpStrategy(symbol, timeframe)


# Example usage
if __name__ == "__main__":
    # Example of how to use the strategy
    strategy = MomentumScalpStrategy("AAPL", "1min")

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
            "volume": np.random.randint(10000, 50000, 100),
        }
    )

    # Analyze the data
    analysis = strategy.analyze_market_data(sample_data)
    print(f"Signal: {analysis['signal']}")
    print(f"Confidence: {analysis['confidence']}%")
    print(f"Reasons: {', '.join(analysis['reasons'])}")
