#!/usr/bin/env python3
"""
Real-time Confidence Calculator
Calculates live confidence levels based on current technical indicators
Updates throughout the trading day as market conditions change
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf

class RealTimeConfidenceCalculator:
    def __init__(self):
        self.base_confidence = 85.0  # Starting point
        self.min_confidence_threshold = 70.0  # Match config.py setting (lowered from 75%)
        self.indicator_weights = {
            'macd_alignment': 15,    # MACD signal strength
            'ema_trend': 15,         # EMA trend alignment
            'rsi_position': 10,      # RSI overbought/oversold
            'volume_confirmation': 15, # Volume vs average
            'vwap_position': 10,     # Price vs VWAP
            'bollinger_position': 10, # Bollinger band position
            'momentum_strength': 15,  # Price momentum
            'volatility_match': 10   # Current vs expected volatility
        }
    
    def get_live_market_data(self, symbol: str, period: str = "5d", interval: str = "15m"):
        """Get recent market data for calculations"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                print(f"[WARNING] No data received for {symbol}")
                return None
            
            return data
        except Exception as e:
            print(f"[ERROR] Failed to get data for {symbol}: {e}")
            return None
    
    def calculate_technical_indicators(self, data: pd.DataFrame):
        """Calculate all technical indicators for confidence scoring"""
        
        # MACD (12, 26, 9)
        ema_12 = data['Close'].ewm(span=12).mean()
        ema_26 = data['Close'].ewm(span=26).mean()
        macd_line = ema_12 - ema_26
        macd_signal = macd_line.ewm(span=9).mean()
        macd_histogram = macd_line - macd_signal
        
        # EMA (9, 21)
        ema_9 = data['Close'].ewm(span=9).mean()
        ema_21 = data['Close'].ewm(span=21).mean()
        
        # RSI (14 period)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # VWAP (Volume Weighted Average Price)
        vwap = (data['Close'] * data['Volume']).cumsum() / data['Volume'].cumsum()
        
        # Bollinger Bands (20, 2)
        bb_middle = data['Close'].rolling(window=20).mean()
        bb_std = data['Close'].rolling(window=20).std()
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)
        
        # Volume analysis
        avg_volume = data['Volume'].rolling(window=20).mean()
        volume_ratio = data['Volume'] / avg_volume
        
        # Price momentum
        momentum_1h = (data['Close'] - data['Close'].shift(4)) / data['Close'].shift(4) * 100  # 4 periods = 1 hour
        momentum_30m = (data['Close'] - data['Close'].shift(2)) / data['Close'].shift(2) * 100  # 2 periods = 30 min
        
        # Volatility (15-minute)
        returns = data['Close'].pct_change()
        volatility = returns.rolling(window=20).std() * 100
        
        return {
            'macd_line': macd_line,
            'macd_signal': macd_signal,
            'macd_histogram': macd_histogram,
            'ema_9': ema_9,
            'ema_21': ema_21,
            'rsi': rsi,
            'vwap': vwap,
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'volume_ratio': volume_ratio,
            'momentum_1h': momentum_1h,
            'momentum_30m': momentum_30m,
            'volatility': volatility,
            'current_price': data['Close'].iloc[-1],
            'current_volume': data['Volume'].iloc[-1]
        }
    
    def score_macd_alignment(self, indicators: dict) -> float:
        """Score MACD signal strength (0-100)"""
        macd_line = indicators['macd_line'].iloc[-1]
        macd_signal = indicators['macd_signal'].iloc[-1]
        macd_hist = indicators['macd_histogram'].iloc[-1]
        
        score = 50  # Neutral base
        
        # Strong bullish signal
        if macd_line > macd_signal and macd_hist > 0:
            score += min(abs(macd_hist) * 1000, 30)  # Max +30 points
        # Strong bearish signal (for short setups)
        elif macd_line < macd_signal and macd_hist < 0:
            score += min(abs(macd_hist) * 1000, 20)  # Max +20 points
        # Weak/conflicting signals
        else:
            score -= 20
        
        return max(0, min(100, score))
    
    def score_ema_trend(self, indicators: dict) -> float:
        """Score EMA trend alignment (0-100)"""
        ema_9 = indicators['ema_9'].iloc[-1]
        ema_21 = indicators['ema_21'].iloc[-1]
        current_price = indicators['current_price']
        
        score = 50  # Neutral base
        
        # Strong uptrend
        if current_price > ema_9 > ema_21:
            score += 40
        # Moderate uptrend
        elif current_price > ema_9 or ema_9 > ema_21:
            score += 20
        # Weak/sideways
        elif abs(ema_9 - ema_21) / ema_21 < 0.01:  # Within 1%
            score += 0
        # Downtrend
        else:
            score -= 20
        
        return max(0, min(100, score))
    
    def score_rsi_position(self, indicators: dict) -> float:
        """Score RSI positioning (0-100)"""
        rsi = indicators['rsi'].iloc[-1]
        
        # Optimal range for momentum continuation
        if 40 <= rsi <= 70:
            return 100
        elif 30 <= rsi <= 80:
            return 80
        elif 20 <= rsi <= 85:
            return 60
        else:
            return 20  # Extreme readings (overbought/oversold)
    
    def score_volume_confirmation(self, indicators: dict) -> float:
        """Score volume confirmation (0-100)"""
        volume_ratio = indicators['volume_ratio'].iloc[-1]
        
        if volume_ratio >= 1.5:  # 1.5x average volume
            return 100
        elif volume_ratio >= 1.2:
            return 80
        elif volume_ratio >= 1.0:
            return 60
        elif volume_ratio >= 0.8:
            return 40
        else:
            return 20  # Very low volume
    
    def score_vwap_position(self, indicators: dict) -> float:
        """Score price position relative to VWAP (0-100)"""
        current_price = indicators['current_price']
        vwap = indicators['vwap'].iloc[-1]
        
        price_diff_pct = ((current_price - vwap) / vwap) * 100
        
        # Slightly above VWAP is ideal for momentum
        if 0.1 <= price_diff_pct <= 0.5:
            return 100
        elif 0 <= price_diff_pct <= 1.0:
            return 80
        elif -0.2 <= price_diff_pct <= 0:
            return 70
        elif abs(price_diff_pct) <= 1.5:
            return 50
        else:
            return 20  # Too far from VWAP
    
    def score_bollinger_position(self, indicators: dict) -> float:
        """Score Bollinger Band positioning (0-100)"""
        current_price = indicators['current_price']
        bb_upper = indicators['bb_upper'].iloc[-1]
        bb_middle = indicators['bb_middle'].iloc[-1]
        bb_lower = indicators['bb_lower'].iloc[-1]
        
        # Calculate position within bands (0 = lower band, 1 = upper band)
        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
        
        # Optimal positions for momentum breakouts
        if 0.6 <= bb_position <= 0.8:  # Upper portion but not extreme
            return 100
        elif 0.4 <= bb_position <= 0.9:
            return 80
        elif 0.2 <= bb_position <= 0.95:
            return 60
        else:
            return 30  # Too extreme (squeeze or breakout risk)
    
    def score_momentum_strength(self, indicators: dict) -> float:
        """Score price momentum strength (0-100)"""
        momentum_1h = indicators['momentum_1h'].iloc[-1]
        momentum_30m = indicators['momentum_30m'].iloc[-1]
        
        # Both timeframes showing momentum
        if momentum_1h > 0.5 and momentum_30m > 0.2:
            return min(100, 60 + (momentum_1h * 20))
        # Mixed signals
        elif momentum_1h > 0 or momentum_30m > 0:
            return 60
        # Weak momentum
        elif abs(momentum_1h) < 0.3 and abs(momentum_30m) < 0.2:
            return 40
        # Negative momentum
        else:
            return 20
    
    def score_volatility_match(self, indicators: dict, expected_volatility: float) -> float:
        """Score how current volatility matches expected levels (0-100)"""
        current_vol = indicators['volatility'].iloc[-1]
        
        if pd.isna(current_vol):
            return 50  # Neutral if no data
        
        vol_ratio = current_vol / expected_volatility
        
        # Optimal volatility range (80-120% of expected)
        if 0.8 <= vol_ratio <= 1.2:
            return 100
        elif 0.6 <= vol_ratio <= 1.5:
            return 80
        elif 0.4 <= vol_ratio <= 2.0:
            return 60
        else:
            return 30  # Too low or too high volatility
    
    def calculate_real_time_confidence(self, symbol: str, expected_volatility: float = 1.0) -> dict:
        """
        Calculate real-time confidence level for a stock
        Returns confidence score and component breakdown
        """
        print(f"\n[CALC] Calculating real-time confidence for {symbol}...")
        
        # Get live market data
        data = self.get_live_market_data(symbol)
        if data is None or len(data) < 50:
            print(f"[ERROR] Insufficient data for {symbol}")
            return {'confidence': 0, 'tradeable': False, 'reason': 'Insufficient data'}
        
        # Calculate technical indicators
        indicators = self.calculate_technical_indicators(data)
        
        # Score each component
        scores = {
            'macd_alignment': self.score_macd_alignment(indicators),
            'ema_trend': self.score_ema_trend(indicators),
            'rsi_position': self.score_rsi_position(indicators),
            'volume_confirmation': self.score_volume_confirmation(indicators),
            'vwap_position': self.score_vwap_position(indicators),
            'bollinger_position': self.score_bollinger_position(indicators),
            'momentum_strength': self.score_momentum_strength(indicators),
            'volatility_match': self.score_volatility_match(indicators, expected_volatility)
        }
        
        # Calculate weighted confidence
        total_weight = sum(self.indicator_weights.values())
        weighted_score = sum(
            scores[indicator] * self.indicator_weights[indicator] 
            for indicator in scores
        ) / total_weight
        
        # Apply base confidence adjustment
        final_confidence = (self.base_confidence * 0.7) + (weighted_score * 0.3)
        
        # Determine if tradeable
        tradeable = final_confidence >= self.min_confidence_threshold
        
        # Detailed result
        result = {
            'symbol': symbol,
            'confidence': round(final_confidence, 1),
            'tradeable': tradeable,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'component_scores': scores,
            'current_price': indicators['current_price'],
            'current_volume': indicators['current_volume'],
            'technical_summary': {
                'macd_bullish': indicators['macd_line'].iloc[-1] > indicators['macd_signal'].iloc[-1],
                'above_ema9': indicators['current_price'] > indicators['ema_9'].iloc[-1],
                'above_vwap': indicators['current_price'] > indicators['vwap'].iloc[-1],
                'rsi_level': round(indicators['rsi'].iloc[-1], 1),
                'volume_multiple': round(indicators['volume_ratio'].iloc[-1], 2)
            }
        }
        
        print(f"[OK] {symbol}: {final_confidence:.1f}% confidence ({'TRADEABLE' if tradeable else 'SKIP'})")
        
        return result

def main():
    """Test real-time confidence calculation"""
    calculator = RealTimeConfidenceCalculator()
    
    # Test with budget watchlist
    test_symbols = ['SOXL', 'SOFI', 'TQQQ', 'INTC', 'NIO']
    
    print("[TEST] REAL-TIME CONFIDENCE CALCULATION TEST")
    print("=" * 60)
    
    results = []
    for symbol in test_symbols:
        result = calculator.calculate_real_time_confidence(symbol, 1.0)
        results.append(result)
    
    print(f"\n[SUMMARY] REAL-TIME RESULTS SUMMARY:")
    print("-" * 50)
    
    tradeable_count = 0
    for result in results:
        if result['confidence'] > 0:
            status = "[TRADE]" if result['tradeable'] else "[SKIP]"
            print(f"{result['symbol']}: {result['confidence']:.1f}% {status}")
            if result['tradeable']:
                tradeable_count += 1
    
    print(f"\n[SUMMARY] {tradeable_count}/{len(test_symbols)} stocks currently tradeable")
    
    return results

if __name__ == "__main__":
    results = main()
