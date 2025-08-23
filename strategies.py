#!/usr/bin/env python3
"""
Enhanced Trading Strategies for Intraday Trading Bot
ASCII-only, no Unicode characters
Implements industry best practices: MACD, EMA, VWAP, Bollinger Bands
"""

from datetime import datetime

import numpy as np
import pandas as pd

from config import config
from utils.logger import clean_message, setup_logger


class MomentumStrategy:
    """Enhanced Momentum-based trading strategy"""

    def __init__(self):
        self.logger = setup_logger("momentum_strategy")
        self.name = "Enhanced Momentum"
        self.logger.info("Enhanced Momentum Strategy initialized")

    def generate_signal(self, symbol, df):
        """Generate trading signal based on enhanced momentum analysis"""
        try:
            if df.empty or len(df) < 26:  # Increased for MACD
                return None

            latest = df.iloc[-1]
            prev = df.iloc[-2]

            # Enhanced momentum indicators
            price_change = latest["price_change"]
            volume_ratio = latest["volume_ratio"]
            rsi = latest["rsi"]
            macd = latest["macd"]
            macd_signal = latest["macd_signal"]
            price_vs_vwap = latest["price_vs_vwap"]

            # CRITICAL: Momentum strategy requires positive price movement
            if price_change <= 0:
                # No bullish momentum signal on negative or flat price action
                pass
            else:
                # Enhanced bullish momentum conditions
                bullish_conditions = [
                    price_change > config["MOMENTUM_THRESHOLD"],  # Strong price move
                    volume_ratio > config["VOLUME_MULTIPLIER"],  # High volume
                    rsi < 70,  # Not overbought
                    latest["close"] > latest["ema_9"],  # Above fast EMA
                    latest["ema_9"] > latest["ema_21"],  # EMA trend bullish
                    macd > macd_signal,  # MACD bullish
                    latest["close"] > latest["vwap"],  # Above VWAP
                    latest["macd_cross_bullish"]
                    or latest["ema_cross_bullish"],  # Fresh crossover
                ]

                # Count confirmations (need at least 5 of 8)
                bullish_score = sum(bullish_conditions)

                if bullish_score >= 5:
                    # Industry-standard confidence calculation
                    base_confidence = (
                        bullish_score / 8
                    ) * 0.85  # 85% max base confidence
                    volume_boost = min(
                        0.15, (volume_ratio - 1.5) * 0.05
                    )  # Volume confirmation bonus
                    momentum_boost = min(
                        0.10, abs(price_change) * 10
                    )  # Price momentum bonus

                    confidence = min(
                        0.95, base_confidence + volume_boost + momentum_boost
                    )

                    signal = {
                        "symbol": symbol,
                        "action": "BUY",
                        "strategy": self.name,
                        "confidence": confidence,
                        "reason": f"Enhanced momentum: {price_change:.1%} move, {volume_ratio:.1f}x vol, {bullish_score}/8 signals",
                        "price": latest["close"],
                        "rsi": rsi,
                        "macd": macd,
                        "volume_ratio": volume_ratio,
                        "price_vs_vwap": price_vs_vwap,
                        "bullish_score": bullish_score,
                    }

                    self.logger.info(f"[SIGNAL] {symbol} BUY - {signal['reason']}")
                    return signal

            # CRITICAL: Bearish momentum strategy requires negative price movement
            if price_change >= 0:
                # No bearish momentum signal on positive or flat price action
                pass
            else:
                # Enhanced bearish momentum conditions
                bearish_conditions = [
                    price_change < -config["MOMENTUM_THRESHOLD"],  # Strong price drop
                    volume_ratio > config["VOLUME_MULTIPLIER"],  # High volume
                    rsi > 30,  # Not oversold
                    latest["close"] < latest["ema_9"],  # Below fast EMA
                    latest["ema_9"] < latest["ema_21"],  # EMA trend bearish
                    macd < macd_signal,  # MACD bearish
                    latest["close"] < latest["vwap"],  # Below VWAP
                    latest["macd_cross_bearish"]
                    or latest["ema_cross_bearish"],  # Fresh crossover
                ]

                bearish_score = sum(bearish_conditions)

                if bearish_score >= 5:
                    # Industry-standard confidence calculation
                    base_confidence = (
                        bearish_score / 8
                    ) * 0.85  # 85% max base confidence
                    volume_boost = min(
                        0.15, (volume_ratio - 1.5) * 0.05
                    )  # Volume confirmation bonus
                    momentum_boost = min(
                        0.10, abs(price_change) * 10
                    )  # Price momentum bonus

                    confidence = min(
                        0.95, base_confidence + volume_boost + momentum_boost
                    )

                    signal = {
                        "symbol": symbol,
                        "action": "SELL",
                        "strategy": self.name,
                        "confidence": confidence,
                        "reason": f"Enhanced bearish: {price_change:.1%} drop, {volume_ratio:.1f}x vol, {bearish_score}/8 signals",
                        "price": latest["close"],
                        "rsi": rsi,
                        "macd": macd,
                        "volume_ratio": volume_ratio,
                        "price_vs_vwap": price_vs_vwap,
                        "bearish_score": bearish_score,
                    }

                    self.logger.info(f"[SIGNAL] {symbol} SELL - {signal['reason']}")
                    return signal

            return None

        except Exception as e:
            self.logger.error(
                f"[ERROR] Failed to generate momentum signal for {symbol}: {e}"
            )
            return None


class MeanReversionStrategy:
    """Enhanced Mean reversion trading strategy"""

    def __init__(self):
        self.logger = setup_logger("mean_reversion_strategy")
        self.name = "Enhanced Mean Reversion"
        self.logger.info("Enhanced Mean Reversion Strategy initialized")

    def generate_signal(self, symbol, df):
        """Generate trading signal based on enhanced mean reversion analysis"""
        try:
            if df.empty or len(df) < 26:
                return None

            latest = df.iloc[-1]
            prev = df.iloc[-2]

            # Enhanced mean reversion indicators
            rsi = latest["rsi"]
            price = latest["close"]
            bb_upper = latest["bb_upper"]
            bb_lower = latest["bb_lower"]
            bb_middle = latest["bb_middle"]
            price_vs_vwap = latest["price_vs_vwap"]
            macd = latest["macd"]
            macd_signal = latest["macd_signal"]
            volume_ratio = latest["volume_ratio"]

            # Enhanced oversold bounce conditions
            oversold_conditions = [
                rsi < config["RSI_OVERSOLD"],  # RSI oversold
                price < bb_lower,  # Below Bollinger lower band
                price_vs_vwap < -0.02,  # More than 2% below VWAP
                latest["close"] < latest["ema_21"],  # Below trend EMA
                macd < macd_signal,  # MACD showing weakness
                volume_ratio > 1.2,  # Volume confirmation
                rsi < prev["rsi"],  # RSI declining (momentum)
            ]

            oversold_score = sum(oversold_conditions)

            if oversold_score >= 4:  # Need 4 of 7 confirmations
                # Industry-standard confidence for mean reversion
                base_confidence = (
                    oversold_score / 7
                ) * 0.80  # 80% max for mean reversion
                rsi_strength = (
                    (config["RSI_OVERSOLD"] - rsi) / config["RSI_OVERSOLD"]
                ) * 0.15
                volume_boost = min(0.10, (volume_ratio - 1.2) * 0.05)

                confidence = min(0.90, base_confidence + rsi_strength + volume_boost)

                signal = {
                    "symbol": symbol,
                    "action": "BUY",
                    "strategy": self.name,
                    "confidence": confidence,
                    "reason": f"Enhanced oversold: RSI {rsi:.1f}, {price_vs_vwap:.1%} vs VWAP, {oversold_score}/7 signals",
                    "price": price,
                    "rsi": rsi,
                    "price_vs_vwap": price_vs_vwap,
                    "bb_position": (price - bb_lower) / (bb_upper - bb_lower),
                    "oversold_score": oversold_score,
                }

                self.logger.info(f"[SIGNAL] {symbol} BUY - {signal['reason']}")
                return signal

            # Enhanced overbought reversal conditions
            overbought_conditions = [
                rsi > config["RSI_OVERBOUGHT"],  # RSI overbought
                price > bb_upper,  # Above Bollinger upper band
                price_vs_vwap > 0.02,  # More than 2% above VWAP
                latest["close"] > latest["ema_21"],  # Above trend EMA
                macd > macd_signal,  # MACD showing strength
                volume_ratio > 1.2,  # Volume confirmation
                rsi > prev["rsi"],  # RSI rising (momentum)
            ]

            overbought_score = sum(overbought_conditions)

            if overbought_score >= 4:  # Need 4 of 7 confirmations
                # Industry-standard confidence for mean reversion
                base_confidence = (
                    overbought_score / 7
                ) * 0.80  # 80% max for mean reversion
                rsi_strength = (
                    (rsi - config["RSI_OVERBOUGHT"]) / (100 - config["RSI_OVERBOUGHT"])
                ) * 0.15
                volume_boost = min(0.10, (volume_ratio - 1.2) * 0.05)

                confidence = min(0.90, base_confidence + rsi_strength + volume_boost)

                signal = {
                    "symbol": symbol,
                    "action": "SELL",
                    "strategy": self.name,
                    "confidence": confidence,
                    "reason": f"Enhanced overbought: RSI {rsi:.1f}, {price_vs_vwap:.1%} vs VWAP, {overbought_score}/7 signals",
                    "price": price,
                    "rsi": rsi,
                    "price_vs_vwap": price_vs_vwap,
                    "bb_position": (price - bb_lower) / (bb_upper - bb_lower),
                    "overbought_score": overbought_score,
                }

                self.logger.info(f"[SIGNAL] {symbol} SELL - {signal['reason']}")
                return signal

            return None

        except Exception as e:
            self.logger.error(
                f"[ERROR] Failed to generate mean reversion signal for {symbol}: {e}"
            )
            return None


class VWAPStrategy:
    """Enhanced Volume Weighted Average Price strategy"""

    def __init__(self):
        self.logger = setup_logger("vwap_strategy")
        self.name = "Enhanced VWAP"
        self.logger.info("Enhanced VWAP Strategy initialized")

    def generate_signal(self, symbol, df):
        """Generate trading signal based on enhanced VWAP analysis"""
        try:
            if df.empty or len(df) < 26:
                return None

            latest = df.iloc[-1]
            prev = df.iloc[-2]

            # Enhanced VWAP indicators
            price = latest["close"]
            vwap = latest["vwap"]
            price_vs_vwap = latest["price_vs_vwap"]
            volume_ratio = latest["volume_ratio"]
            rsi = latest["rsi"]
            macd = latest["macd"]
            macd_signal = latest["macd_signal"]
            bb_upper = latest["bb_upper"]
            bb_lower = latest["bb_lower"]
            price_change = latest["price_change"]  # Add price change check

            # Enhanced VWAP bullish conditions (require positive price momentum)
            if (
                price_change > 0 and price > vwap
            ):  # Must have positive momentum AND be above VWAP
                vwap_bullish_conditions = [
                    price > vwap,  # Price above VWAP
                    prev["close"]
                    <= prev["vwap"],  # Previous price below VWAP (breakout)
                    price_vs_vwap > 0.005,  # At least 0.5% above VWAP
                    volume_ratio > 1.3,  # High volume confirmation
                    rsi < 70,  # Not overbought
                    macd > macd_signal,  # MACD bullish
                    latest["ema_9"] > latest["ema_21"],  # Short-term trend bullish
                    price > bb_lower,  # Above BB lower band
                ]

                vwap_bullish_score = sum(vwap_bullish_conditions)

                if vwap_bullish_score >= 5:  # Need 5 of 8 confirmations
                    # Industry-standard VWAP bullish confidence
                    base_confidence = (
                        vwap_bullish_score / 8
                    ) * 0.85  # 85% max for VWAP momentum
                    price_momentum = min(
                        0.10, abs(price_vs_vwap) * 20
                    )  # Price distance strength
                    volume_boost = min(0.10, (volume_ratio - 1.5) * 0.05)

                    confidence = min(
                        0.90, base_confidence + price_momentum + volume_boost
                    )

                    signal = {
                        "symbol": symbol,
                        "action": "BUY",
                        "strategy": self.name,
                        "confidence": confidence,
                        "reason": f"VWAP breakout: {price_vs_vwap:.1%} above VWAP, {volume_ratio:.1f}x vol, {vwap_bullish_score}/8 signals",
                        "price": price,
                        "vwap": vwap,
                        "price_vs_vwap": price_vs_vwap,
                        "volume_ratio": volume_ratio,
                        "vwap_bullish_score": vwap_bullish_score,
                    }

                    self.logger.info(f"[SIGNAL] {symbol} BUY - {signal['reason']}")
                    return signal

            # Enhanced VWAP bearish conditions (require negative price momentum)
            if (
                price_change < 0 and price < vwap
            ):  # Must have negative momentum AND be below VWAP
                vwap_bearish_conditions = [
                    price < vwap,  # Price below VWAP
                    prev["close"]
                    >= prev["vwap"],  # Previous price above VWAP (breakdown)
                    price_vs_vwap < -0.005,  # At least 0.5% below VWAP
                    volume_ratio > 1.3,  # High volume confirmation
                    rsi > 30,  # Not oversold
                    macd < macd_signal,  # MACD bearish
                    latest["ema_9"] < latest["ema_21"],  # Short-term trend bearish
                    price < bb_upper,  # Below BB upper band
                ]

                vwap_bearish_score = sum(vwap_bearish_conditions)

                if vwap_bearish_score >= 5:  # Need 5 of 8 confirmations
                    # Industry-standard VWAP bearish confidence
                    base_confidence = (
                        vwap_bearish_score / 8
                    ) * 0.85  # 85% max for VWAP momentum
                    price_momentum = min(
                        0.10, abs(price_vs_vwap) * 20
                    )  # Price distance strength
                    volume_boost = min(0.10, (volume_ratio - 1.5) * 0.05)

                    confidence = min(
                        0.90, base_confidence + price_momentum + volume_boost
                    )

                    signal = {
                        "symbol": symbol,
                        "action": "SELL",
                        "strategy": self.name,
                        "confidence": confidence,
                        "reason": f"VWAP breakdown: {price_vs_vwap:.1%} below VWAP, {volume_ratio:.1f}x vol, {vwap_bearish_score}/8 signals",
                        "price": price,
                        "vwap": vwap,
                        "price_vs_vwap": price_vs_vwap,
                        "volume_ratio": volume_ratio,
                        "vwap_bearish_score": vwap_bearish_score,
                    }

                    self.logger.info(f"[SIGNAL] {symbol} SELL - {signal['reason']}")
                    return signal

            return None

        except Exception as e:
            self.logger.error(
                f"[ERROR] Failed to generate VWAP signal for {symbol}: {e}"
            )
            return None
