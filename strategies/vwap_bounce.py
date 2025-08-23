"""
VWAP Bounce Strategy with Specialized Volume Indicators
======================================================
This strategy focuses on volume-based indicators unique to VWAP analysis.
Uses unified indicator service to avoid duplication with other systems.

Specialized Indicators:
- VWAP Standard Deviation Bands (multiple levels)
- Volume Profile analysis
- Point of Control (POC) identification
- Value Area calculations
- On Balance Volume (OBV)

Shared Indicators (from unified service):
- VWAP (no duplication with confidence monitor)
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta


class VWAPBounceStrategy:
    """
    Optimized VWAP bounce strategy using specialized volume indicators
    Focuses on unique volume profile indicators to avoid duplication
    """

    def __init__(self, symbol: str, timeframe: str = "1min"):
        self.symbol = symbol
        self.timeframe = timeframe
        self.logger = logging.getLogger(__name__)

        # Specialized VWAP settings
        self.vwap_std_multipliers = [0.5, 1.0, 1.5, 2.0]  # Standard deviation bands
        self.volume_profile_periods = 50
        self.poc_threshold = 0.3  # Point of Control significance threshold

        # Bounce detection settings
        self.bounce_proximity_pct = 0.1  # Within 0.1% of VWAP for bounce setup
        self.bounce_confirmation_pct = 0.05  # Move away from VWAP for confirmation

        # Risk management
        self.max_position_size = 0.015  # 1.5% of portfolio
        self.stop_loss_pct = 0.01  # 1% stop loss
        self.take_profit_pct = 0.02  # 2% take profit
        self.max_distance_from_vwap = 0.5  # Max 0.5% away from VWAP to trade

    def calculate_volume_profile(self, df: pd.DataFrame, periods: int = 50) -> Dict:
        """Calculate volume profile for recent periods (specialized indicator)"""
        recent_data = df.tail(periods)

        # Create price bins
        price_range = recent_data["high"].max() - recent_data["low"].min()
        num_bins = min(20, len(recent_data) // 3)  # Adaptive number of bins
        bin_size = price_range / num_bins if num_bins > 0 else price_range

        # Calculate volume at each price level
        volume_profile = {}

        for _, row in recent_data.iterrows():
            # Distribute volume across price range for this bar
            bar_range = row["high"] - row["low"]
            if bar_range > 0:
                # Simple distribution - could be more sophisticated
                mid_price = (row["high"] + row["low"]) / 2
                bin_index = (
                    int((mid_price - recent_data["low"].min()) / bin_size)
                    if bin_size > 0
                    else 0
                )
                bin_index = max(0, min(num_bins - 1, bin_index))

                bin_price = recent_data["low"].min() + (bin_index * bin_size)

                if bin_price not in volume_profile:
                    volume_profile[bin_price] = 0
                volume_profile[bin_price] += row["volume"]

        # Find Point of Control (POC) - price level with highest volume
        if volume_profile:
            poc_price = max(volume_profile, key=volume_profile.get)
            poc_volume = volume_profile[poc_price]
            total_volume = sum(volume_profile.values())

            # Find Value Area (prices containing 70% of volume)
            sorted_levels = sorted(
                volume_profile.items(), key=lambda x: x[1], reverse=True
            )
            cumulative_volume = 0
            value_area = []

            for price, volume in sorted_levels:
                cumulative_volume += volume
                value_area.append(price)
                if cumulative_volume >= total_volume * 0.7:
                    break

            value_area_high = max(value_area) if value_area else poc_price
            value_area_low = min(value_area) if value_area else poc_price

        else:
            poc_price = recent_data["close"].iloc[-1]
            poc_volume = 0
            value_area_high = value_area_low = poc_price

        return {
            "poc_price": poc_price,
            "poc_volume": poc_volume,
            "value_area_high": value_area_high,
            "value_area_low": value_area_low,
            "profile": volume_profile,
        }

    def detect_vwap_bounce_setup(
        self, current_price: float, vwap_bands: Dict
    ) -> Dict[str, bool]:
        """Detect VWAP bounce setup conditions using specialized analysis"""

        # Distance from VWAP bands
        near_vwap_upper_1 = (
            abs(current_price - vwap_bands["vwap_upper_1"]) / current_price < 0.001
        )
        near_vwap_lower_1 = (
            abs(current_price - vwap_bands["vwap_lower_1"]) / current_price < 0.001
        )
        near_vwap_upper_2 = (
            abs(current_price - vwap_bands["vwap_upper_2"]) / current_price < 0.001
        )
        near_vwap_lower_2 = (
            abs(current_price - vwap_bands["vwap_lower_2"]) / current_price < 0.001
        )

        # VWAP band positioning
        above_vwap = current_price > vwap_bands["vwap"]
        below_vwap = current_price < vwap_bands["vwap"]

        return {
            "near_vwap_upper_1": near_vwap_upper_1,
            "near_vwap_lower_1": near_vwap_lower_1,
            "near_vwap_upper_2": near_vwap_upper_2,
            "near_vwap_lower_2": near_vwap_lower_2,
            "above_vwap": above_vwap,
            "below_vwap": below_vwap,
        }

    def generate_signal(self, symbol: str, df: pd.DataFrame) -> Optional[Dict]:
        """Generate trading signal using specialized VWAP indicators"""
        try:
            # Import unified service
            from core.unified_indicators import unified_indicator_service

            # Get strategy-specific indicators (avoids duplication)
            indicator_data = unified_indicator_service.get_indicators_for_strategy(
                df, symbol, "vwap_bounce"
            )

            if "error" in indicator_data:
                return None

            indicators = indicator_data["indicators"]
            current_values = indicator_data["current_values"]
            current_price = current_values["price"]

            # Check if price is within tradeable distance from VWAP
            vwap_current = indicators["vwap"].iloc[-1]
            vwap_distance = abs((current_price - vwap_current) / vwap_current) * 100
            if vwap_distance > self.max_distance_from_vwap:
                return None

            # Calculate specialized indicators
            volume_profile = self.calculate_volume_profile(
                df, self.volume_profile_periods
            )

            # Create VWAP bands dictionary for bounce detection
            vwap_bands = {
                "vwap": vwap_current,
                "vwap_upper_1": indicators["vwap_upper_1"].iloc[-1],
                "vwap_lower_1": indicators["vwap_lower_1"].iloc[-1],
                "vwap_upper_2": indicators["vwap_upper_2"].iloc[-1],
                "vwap_lower_2": indicators["vwap_lower_2"].iloc[-1],
            }

            bounce_setup = self.detect_vwap_bounce_setup(current_price, vwap_bands)

            # Signal generation using specialized VWAP indicators
            signal = "HOLD"
            confidence = 0
            reasons = []

            bullish_signals = 0
            bearish_signals = 0

            # VWAP band bounce analysis (our specialty)
            if bounce_setup["near_vwap_lower_1"]:
                bullish_signals += 2
                reasons.append("Bouncing off VWAP lower band (1σ)")
            elif bounce_setup["near_vwap_lower_2"]:
                bullish_signals += 3
                reasons.append("Bouncing off VWAP lower band (2σ)")
            elif bounce_setup["near_vwap_upper_1"]:
                bearish_signals += 2
                reasons.append("Rejecting at VWAP upper band (1σ)")
            elif bounce_setup["near_vwap_upper_2"]:
                bearish_signals += 3
                reasons.append("Rejecting at VWAP upper band (2σ)")

            # Volume Profile analysis (our specialty)
            if (
                current_price < volume_profile["poc_price"]
                and current_price > volume_profile["value_area_low"]
            ):
                bullish_signals += 1
                reasons.append("Price near volume support area")
            elif (
                current_price > volume_profile["poc_price"]
                and current_price < volume_profile["value_area_high"]
            ):
                bearish_signals += 1
                reasons.append("Price near volume resistance area")

            # Point of Control proximity (our specialty)
            poc_distance = (
                abs(
                    (current_price - volume_profile["poc_price"])
                    / volume_profile["poc_price"]
                )
                * 100
            )
            if poc_distance < 0.2:  # Very close to POC
                if bounce_setup["above_vwap"]:
                    bullish_signals += 1
                    reasons.append("Above VWAP at Point of Control")
                else:
                    bearish_signals += 1
                    reasons.append("Below VWAP at Point of Control")

            # OBV trend confirmation (our specialty)
            if len(indicators["obv"]) > 1:
                obv_current = indicators["obv"].iloc[-1]
                obv_prev = indicators["obv"].iloc[-2]
                obv_trending_up = obv_current > obv_prev

                if obv_trending_up and bullish_signals > 0:
                    bullish_signals += 0.5
                    reasons.append("OBV confirming bullish momentum")
                elif not obv_trending_up and bearish_signals > 0:
                    bearish_signals += 0.5
                    reasons.append("OBV confirming bearish momentum")

            # Volume confirmation (shared indicator)
            if len(indicators["volume_ratio"]) > 0:
                volume_ratio = indicators["volume_ratio"].iloc[-1]
                high_volume = volume_ratio > 1.5
                if high_volume:
                    reasons.append(f"High volume ({volume_ratio:.1f}x)")
            else:
                high_volume = False

            # Generate final signal (require strong VWAP-based confirmations)
            min_signals = 2.0

            if bullish_signals >= min_signals and high_volume:
                signal = "BUY"
                base_confidence = 45 + (bullish_signals * 10)
                volume_bonus = 15 if volume_ratio > 2.0 else 0
                proximity_bonus = 10 if vwap_distance < 0.05 else 0
                confidence = min(90, base_confidence + volume_bonus + proximity_bonus)

            elif bearish_signals >= min_signals and high_volume:
                signal = "SELL"
                base_confidence = 45 + (bearish_signals * 10)
                volume_bonus = 15 if volume_ratio > 2.0 else 0
                proximity_bonus = 10 if vwap_distance < 0.05 else 0
                confidence = min(90, base_confidence + volume_bonus + proximity_bonus)

            # Only return signal if confidence meets threshold
            if confidence < 65:
                return None

            # Risk management using VWAP bands
            if signal == "BUY":
                entry_price = current_price
                stop_loss = max(
                    vwap_bands["vwap_lower_2"], entry_price * (1 - self.stop_loss_pct)
                )
                take_profit = min(
                    vwap_bands["vwap_upper_1"], entry_price * (1 + self.take_profit_pct)
                )
            elif signal == "SELL":
                entry_price = current_price
                stop_loss = min(
                    vwap_bands["vwap_upper_2"], entry_price * (1 + self.stop_loss_pct)
                )
                take_profit = max(
                    vwap_bands["vwap_lower_1"], entry_price * (1 - self.take_profit_pct)
                )
            else:
                return None

            return {
                "symbol": symbol,
                "action": signal,
                "reason": f"VWAP Bounce: {', '.join(reasons[:2])}",
                "confidence": confidence / 100.0,  # Convert to 0-1 scale
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "strategy": "vwap_bounce_optimized",
                "indicators": {
                    "vwap_distance_pct": vwap_distance,
                    "poc_price": volume_profile["poc_price"],
                    "value_area_high": volume_profile["value_area_high"],
                    "value_area_low": volume_profile["value_area_low"],
                    "volume_ratio": (
                        volume_ratio if "volume_ratio" in locals() else None
                    ),
                },
            }

        except Exception as e:
            self.logger.error(f"VWAP bounce signal generation failed for {symbol}: {e}")
            return None

    def analyze_market_data(self, df: pd.DataFrame) -> Dict:
        """Comprehensive VWAP bounce analysis"""
        if len(df) < 60:
            return {"signal": "HOLD", "confidence": 0, "reason": "Insufficient data"}

        current_price = df["close"].iloc[-1]

        # Calculate VWAP and related indicators
        session_vwap = self.calculate_vwap(df)
        rolling_vwap_20 = self.calculate_vwap(df, 20)
        rolling_vwap_50 = self.calculate_vwap(df, 50)

        vwap_bands = self.calculate_vwap_bands(df, session_vwap, 20)
        volume_profile = self.calculate_volume_profile(df, self.volume_profile_periods)
        volume_indicators = self.calculate_volume_indicators(df)
        bounce_setup = self.detect_vwap_bounce_setup(df, session_vwap, vwap_bands)

        # Current values
        current_vwap = session_vwap.iloc[-1]
        current_vwap_20 = rolling_vwap_20.iloc[-1]
        current_relative_volume = volume_indicators["relative_volume"].iloc[-1]
        current_volume_oscillator = volume_indicators["volume_oscillator"].iloc[-1]
        current_obv = volume_indicators["obv"].iloc[-1]
        prev_obv = volume_indicators["obv"].iloc[-2]

        # Signal generation
        signal = "HOLD"
        confidence = 0
        reasons = []

        # Check if price is within tradeable distance from VWAP
        vwap_distance = abs((current_price - current_vwap) / current_vwap) * 100
        if vwap_distance > self.max_distance_from_vwap:
            return {
                "signal": "HOLD",
                "confidence": 0,
                "reasons": [f"Too far from VWAP ({vwap_distance:.2f}%)"],
                "indicators": {"vwap_distance": vwap_distance},
                "timestamp": datetime.now().isoformat(),
            }

        # Volume confirmation
        high_volume = current_relative_volume > self.high_volume_threshold
        volume_trending_up = current_volume_oscillator > 0

        # VWAP bounce signals
        bullish_signals = 0
        bearish_signals = 0

        # Bullish bounce scenarios
        if bounce_setup["bullish_bounce_setup"]:
            bullish_signals += 2
            reasons.append("Bullish VWAP bounce setup detected")

        if current_price > current_vwap and bounce_setup["near_lower_band"]:
            bullish_signals += 1
            reasons.append("Price bouncing off lower VWAP band")

        if (
            current_price < volume_profile["poc_price"]
            and current_price > volume_profile["value_area_low"]
        ):
            bullish_signals += 1
            reasons.append("Price near volume support area")

        # Bearish bounce scenarios
        if bounce_setup["bearish_bounce_setup"]:
            bearish_signals += 2
            reasons.append("Bearish VWAP bounce setup detected")

        if current_price < current_vwap and bounce_setup["near_upper_band"]:
            bearish_signals += 1
            reasons.append("Price rejecting at upper VWAP band")

        if (
            current_price > volume_profile["poc_price"]
            and current_price < volume_profile["value_area_high"]
        ):
            bearish_signals += 1
            reasons.append("Price near volume resistance area")

        # Volume confirmation signals
        if high_volume:
            reasons.append(f"High relative volume ({current_relative_volume:.1f}x)")
            if bounce_setup["bullish_bounce_setup"]:
                bullish_signals += 1
            elif bounce_setup["bearish_bounce_setup"]:
                bearish_signals += 1

        # OBV confirmation
        obv_trending_up = current_obv > prev_obv
        if obv_trending_up and bounce_setup["bullish_bounce_setup"]:
            bullish_signals += 0.5
            reasons.append("OBV confirming bullish momentum")
        elif not obv_trending_up and bounce_setup["bearish_bounce_setup"]:
            bearish_signals += 0.5
            reasons.append("OBV confirming bearish momentum")

        # Multiple VWAP timeframe alignment
        vwap_alignment_bullish = current_price > current_vwap > current_vwap_20
        vwap_alignment_bearish = current_price < current_vwap < current_vwap_20

        if vwap_alignment_bullish:
            bullish_signals += 0.5
            reasons.append("Multiple VWAP timeframe alignment bullish")
        elif vwap_alignment_bearish:
            bearish_signals += 0.5
            reasons.append("Multiple VWAP timeframe alignment bearish")

        # Generate final signal
        min_signals = 2.0

        if bullish_signals >= min_signals:
            signal = "BUY"
            base_confidence = 45 + (bullish_signals * 8)
            volume_bonus = 15 if high_volume else 0
            proximity_bonus = 10 if bounce_setup["vwap_distance_pct"] < 0.05 else 0
            confidence = min(90, base_confidence + volume_bonus + proximity_bonus)

        elif bearish_signals >= min_signals:
            signal = "SELL"
            base_confidence = 45 + (bearish_signals * 8)
            volume_bonus = 15 if high_volume else 0
            proximity_bonus = 10 if bounce_setup["vwap_distance_pct"] < 0.05 else 0
            confidence = min(90, base_confidence + volume_bonus + proximity_bonus)

        # Risk management
        if signal in ["BUY", "SELL"]:
            vwap_std = vwap_bands["vwap_std"].iloc[-1]

            if signal == "BUY":
                entry_price = current_price
                stop_loss = max(
                    current_vwap - (vwap_std * 1.5),
                    entry_price * (1 - self.stop_loss_pct),
                )
                take_profit = min(
                    current_vwap + (vwap_std * 2.0),
                    entry_price * (1 + self.take_profit_pct),
                )
            else:  # SELL
                entry_price = current_price
                stop_loss = min(
                    current_vwap + (vwap_std * 1.5),
                    entry_price * (1 + self.stop_loss_pct),
                )
                take_profit = max(
                    current_vwap - (vwap_std * 2.0),
                    entry_price * (1 - self.take_profit_pct),
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
                "session_vwap": current_vwap,
                "rolling_vwap_20": current_vwap_20,
                "vwap_distance_pct": vwap_distance,
                "vwap_std": vwap_bands["vwap_std"].iloc[-1],
                "poc_price": volume_profile["poc_price"],
                "value_area_high": volume_profile["value_area_high"],
                "value_area_low": volume_profile["value_area_low"],
                "relative_volume": current_relative_volume,
                "volume_oscillator": current_volume_oscillator,
                "obv": current_obv,
            },
            "bounce_setup": bounce_setup,
            "volume_profile": volume_profile,
            "timestamp": datetime.now().isoformat(),
        }

    def get_position_size(self, account_value: float, vwap_std: float) -> float:
        """Calculate position size based on VWAP volatility"""
        base_size = account_value * self.max_position_size

        # Adjust for VWAP volatility
        if vwap_std > 0.01:  # High volatility
            base_size *= 0.7
        elif vwap_std > 0.005:  # Medium volatility
            base_size *= 0.85

        return base_size

    def is_market_session_active(self) -> bool:
        """Check if we're in active market session for VWAP calculations"""
        now = datetime.now()
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)

        return market_open <= now <= market_close and now.weekday() < 5


def create_vwap_bounce_strategy(
    symbol: str, timeframe: str = "1min"
) -> VWAPBounceStrategy:
    """Factory function to create a VWAP bounce strategy instance"""
    return VWAPBounceStrategy(symbol, timeframe)


# Example usage
if __name__ == "__main__":
    # Example of how to use the strategy
    strategy = VWAPBounceStrategy("AAPL", "1min")

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
            "volume": np.random.randint(5000, 25000, 100),
        }
    )

    # Analyze the data
    analysis = strategy.analyze_market_data(sample_data)
    print(f"Signal: {analysis['signal']}")
    print(f"Confidence: {analysis['confidence']}%")
    print(f"Reasons: {', '.join(analysis['reasons'])}")
