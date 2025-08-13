#!/usr/bin/env python3
"""
🚀 Momentum Intraday Strategy
Captures medium-term momentum moves with volume confirmation for 15-minute swings
"""

import sys
import pandas as pd
import numpy as np
import time
from pathlib import Path
from typing import List, Optional
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import config, get_strategy_config
from utils.signal_helper import calculate_adaptive_signal_levels
from utils.signal_types import ScalpingSignal

def round_price_to_tick(price: float) -> float:
    """Round price to valid tick increment for trading"""
    return round(price, 2)

 # Using unified ScalpingSignal from utils.signal_types

class MomentumIntradayStrategy:
    """Momentum-based intraday trading strategy"""
    
    def __init__(self):
        """Initialize momentum intraday strategy"""
        self.logger = logging.getLogger("momentum_strategy")
        self.name = "momentum_scalp"
        self.config = get_strategy_config(self.name)
        self.min_bars = 20  # Minimum bars needed for analysis
        
        self.logger.info("🚀 Momentum Scalping Strategy initialized")
    
    def generate_signals(self, symbol: str, data: pd.DataFrame) -> List[ScalpingSignal]:
        """Generate momentum-based scalping signals"""
        try:
            if len(data) < self.min_bars:
                return []
            
            signals = []
            current_bar = data.iloc[-1]
            prev_bar = data.iloc[-2]
            
            # Get current market conditions
            current_price = current_bar['close']
            volume = current_bar['volume']
            avg_volume = data['volume'].rolling(20).mean().iloc[-1]
            
            # Check momentum conditions
            momentum_signals = self._check_momentum_conditions(data, symbol)
            
            for signal_data in momentum_signals:
                signal = ScalpingSignal(
                    symbol=symbol,
                    signal_type=signal_data['type'],
                    strategy=self.name,
                    confidence=signal_data['confidence'],
                    entry_price=signal_data['entry_price'],
                    stop_loss=signal_data['stop_loss'],
                    profit_target=signal_data['profit_target'],
                    timestamp=datetime.now(),
                    metadata=signal_data['metadata']
                )
                signals.append(signal)
            
            return signals
            
        except Exception as e:
            self.logger.error(f"❌ Error generating momentum signals for {symbol}: {e}")
            return []
    
    def _check_momentum_conditions(self, data: pd.DataFrame, symbol: str) -> List[dict]:
        """Check for momentum trading conditions with enhanced profitability filters"""
        signals = []
        
        try:
            current = data.iloc[-1]
            prev = data.iloc[-2]
            prev2 = data.iloc[-3] if len(data) > 3 else prev
            
            # Key metrics
            current_price = current['close']
            volume = current['volume']
            avg_volume = data['volume'].rolling(20).mean().iloc[-1]
            rsi = current.get('rsi', 50)
            
            # Enhanced momentum analysis
            price_change = (current_price - prev['close']) / prev['close'] * 100
            price_change_5 = current.get('price_change_5', 0) * 100
            
            # Multi-timeframe momentum
            ema_5 = current.get('ema_5', current_price)
            ema_13 = current.get('ema_13', current_price)
            
            # Volume analysis with stricter requirements
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1
            
            # VWAP analysis for institutional flow
            vwap = current.get('vwap', current_price)
            vwap_deviation = (current_price - vwap) / vwap * 100
            
            # Volatility filter - only trade during higher volatility
            recent_volatility = data['high_low_pct'].rolling(10).mean().iloc[-1]
            
            # Enhanced signal criteria for profitability
            strong_volume = volume_ratio >= 1.5  # Require 50% above average volume
            trending_up = ema_5 > ema_13 and current_price > ema_5
            trending_down = ema_5 < ema_13 and current_price < ema_5
            
            # Momentum continuation patterns
            momentum_up = (price_change > 0.05 and price_change_5 > 0.1 and 
                          current_price > prev['high'] and strong_volume)
            momentum_down = (price_change < -0.05 and price_change_5 < -0.1 and 
                            current_price < prev['low'] and strong_volume)
            
            # Mean reversion after momentum (countertrend scalp)
            oversold_bounce = (rsi < 25 and price_change > 0.03 and 
                              current_price < vwap * 0.998 and strong_volume)
            overbought_drop = (rsi > 75 and price_change < -0.03 and 
                              current_price > vwap * 1.002 and strong_volume)
            
            # Volatility requirement for scalping
            min_volatility = recent_volatility > 0.15  # At least 0.15% daily range
            
            # LONG SIGNAL: Momentum continuation or oversold bounce
            if min_volatility and (
                (momentum_up and trending_up and rsi < 70) or
                (oversold_bounce and 30 < rsi < 50)
            ):
                # Calculate adaptive levels
                levels = calculate_adaptive_signal_levels(
                    data, 'BUY', current_price, self.config
                )
                
                # Enhanced confidence scoring
                confidence = 0.65  # Base confidence
                
                # Volume boost
                if volume_ratio > 2.0:
                    confidence += 0.10
                elif volume_ratio > 1.5:
                    confidence += 0.05
                    
                # Trend alignment boost
                if trending_up and current_price > vwap:
                    confidence += 0.08
                    
                # RSI positioning boost
                if 35 < rsi < 65:  # Sweet spot for momentum
                    confidence += 0.05
                    
                # Momentum strength boost
                if price_change > 0.10:
                    confidence += 0.07
                
                confidence = min(confidence, 0.95)  # Cap at 95%
                
                signals.append({
                    'type': 'BUY',
                    'confidence': confidence,
                    'entry_price': round_price_to_tick(current_price),
                    'stop_loss': levels['stop_loss'],
                    'profit_target': levels['profit_target'],
                    'metadata': {
                        'volume_ratio': volume_ratio,
                        'rsi': rsi,
                        'price_change': price_change,
                        'vwap_dev': vwap_deviation,
                        'volatility': recent_volatility,
                        'pattern': 'momentum_up' if momentum_up else 'oversold_bounce'
                    }
                })
            
            # SHORT SIGNAL: Momentum continuation or overbought drop
            if min_volatility and (
                (momentum_down and trending_down and rsi > 30) or
                (overbought_drop and 50 < rsi < 70)
            ):
                # Calculate adaptive levels
                levels = calculate_adaptive_signal_levels(
                    data, 'SELL', current_price, self.config
                )
                
                # Enhanced confidence scoring
                confidence = 0.65  # Base confidence
                
                # Volume boost
                if volume_ratio > 2.0:
                    confidence += 0.10
                elif volume_ratio > 1.5:
                    confidence += 0.05
                    
                # Trend alignment boost
                if trending_down and current_price < vwap:
                    confidence += 0.08
                    
                # RSI positioning boost
                if 35 < rsi < 65:  # Sweet spot for momentum
                    confidence += 0.05
                    
                # Momentum strength boost
                if price_change < -0.10:
                    confidence += 0.07
                
                confidence = min(confidence, 0.95)  # Cap at 95%
                
                signals.append({
                    'type': 'SELL',
                    'confidence': confidence,
                    'entry_price': round_price_to_tick(current_price),
                    'stop_loss': levels['stop_loss'],
                    'profit_target': levels['profit_target'],
                    'metadata': {
                        'volume_ratio': volume_ratio,
                        'rsi': rsi,
                        'price_change': price_change,
                        'vwap_dev': vwap_deviation,
                        'volatility': recent_volatility,
                        'pattern': 'momentum_down' if momentum_down else 'overbought_drop'
                    }
                })
            
            return signals
            ema_5 = current.get('ema_5', current_price)
            ema_13 = current.get('ema_13', current_price)
            
            # VWAP analysis
            vwap = current.get('vwap', current_price)
            vwap_distance = (current_price - vwap) / vwap * 100
            
            # 1. Bullish Momentum Signal
            bullish_conditions = [
                price_change >= self.config.get('price_change_threshold', 0.3),  # Strong price move
                volume_ratio >= self.config.get('min_volume_spike', 1.5),       # Volume confirmation
                current_price > ema_5,                                          # Above short EMA
                ema_5 > ema_13,                                                # EMA alignment
                rsi < 70,                                                       # Not overbought
                vwap_distance > -0.5                                           # Not too far below VWAP
            ]
            
            if sum(bullish_conditions) >= 4:  # Need at least 4/6 conditions
                confidence = sum(bullish_conditions) / len(bullish_conditions)
                
                # Calculate adaptive entry, stop, and target levels
                entry_price = current_price
                levels = calculate_adaptive_signal_levels(
                    symbol=symbol,
                    entry_price=entry_price,
                    signal_type='BUY'
                )
                stop_loss = levels['stop_loss']
                profit_target = levels['profit_target']
                
                signals.append({
                    'type': 'BUY',
                    'confidence': confidence,
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'profit_target': profit_target,
                    'metadata': {
                        'price_change': price_change,
                        'volume_ratio': volume_ratio,
                        'rsi': rsi,
                        'vwap_distance': vwap_distance,
                        'conditions_met': sum(bullish_conditions),
                        'trigger': 'bullish_momentum'
                    }
                })
                
                self.logger.info(f"🟢 Bullish momentum signal: {symbol} - "
                               f"Price: ${entry_price:.2f}, "
                               f"Change: {price_change:+.2f}%, "
                               f"Volume: {volume_ratio:.1f}x, "
                               f"Confidence: {confidence:.2f}")
            
            # 2. Bearish Momentum Signal
            bearish_conditions = [
                price_change <= -self.config.get('price_change_threshold', 0.3),  # Strong price decline
                volume_ratio >= self.config.get('min_volume_spike', 1.5),        # Volume confirmation
                current_price < ema_5,                                           # Below short EMA
                ema_5 < ema_13,                                                 # EMA alignment
                rsi > 30,                                                        # Not oversold
                vwap_distance < 0.5                                             # Not too far above VWAP
            ]
            
            if sum(bearish_conditions) >= 4:  # Need at least 4/6 conditions
                confidence = sum(bearish_conditions) / len(bearish_conditions)
                
                # Calculate adaptive entry, stop, and target levels for short
                entry_price = current_price
                levels = calculate_adaptive_signal_levels(
                    symbol=symbol,
                    entry_price=entry_price,
                    signal_type='SELL'
                )
                stop_loss = levels['stop_loss']
                profit_target = levels['profit_target']
                
                signals.append({
                    'type': 'SELL',
                    'confidence': confidence,
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'profit_target': profit_target,
                    'metadata': {
                        'price_change': price_change,
                        'volume_ratio': volume_ratio,
                        'rsi': rsi,
                        'vwap_distance': vwap_distance,
                        'conditions_met': sum(bearish_conditions),
                        'trigger': 'bearish_momentum'
                    }
                })
                
                self.logger.info(f"🔴 Bearish momentum signal: {symbol} - "
                               f"Price: ${entry_price:.2f}, "
                               f"Change: {price_change:+.2f}%, "
                               f"Volume: {volume_ratio:.1f}x, "
                               f"Confidence: {confidence:.2f}")
            
            # 3. Breakout Momentum Signal
            breakout_signals = self._check_breakout_momentum(data, symbol)
            signals.extend(breakout_signals)
            
            return signals
            
        except Exception as e:
            # Throttle error messages to prevent spam
            if not hasattr(self, 'last_error_time'):
                self.last_error_time = {}
            
            current_time = time.time()
            error_key = f"momentum_{symbol}"
            
            if (error_key not in self.last_error_time or 
                current_time - self.last_error_time[error_key] >= 60):  # Log error max once per minute
                self.logger.error(f"❌ Error checking momentum conditions: {e}")
                self.last_error_time[error_key] = current_time
            return []
    
    def _check_breakout_momentum(self, data: pd.DataFrame, symbol: str) -> List[dict]:
        """Check for breakout momentum signals"""
        signals = []
        
        try:
            # Look for price breakouts with volume
            current = data.iloc[-1]
            recent_data = data.tail(10)  # Last 10 bars
            
            current_price = current['close']
            volume = current['volume']
            avg_volume = data['volume'].rolling(20).mean().iloc[-1]
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1
            
            # Calculate recent high/low
            recent_high = recent_data['high'].max()
            recent_low = recent_data['low'].min()
            
            # Breakout conditions
            min_breakout_volume = self.config.get('breakout_volume', 2.0)
            min_breakout_move = self.config.get('breakout_threshold', 0.2)
            
            # Bullish breakout (break above recent high)
            if (current_price > recent_high and 
                volume_ratio >= min_breakout_volume and
                (current_price - recent_high) / recent_high * 100 >= min_breakout_move):
                
                confidence = 0.8  # High confidence for breakouts
                
                entry_price = current_price
                stop_loss = round_price_to_tick(recent_high * 0.998)  # Just below breakout level
                profit_target = round_price_to_tick(entry_price * (1 + config.PROFIT_TARGET_PCT / 100))
                
                signals.append({
                    'type': 'BUY',
                    'confidence': confidence,
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'profit_target': profit_target,
                    'metadata': {
                        'breakout_level': recent_high,
                        'breakout_move': (current_price - recent_high) / recent_high * 100,
                        'volume_ratio': volume_ratio,
                        'trigger': 'bullish_breakout'
                    }
                })
                
                self.logger.info(f"⬆️ Bullish breakout: {symbol} @ ${current_price:.2f} "
                               f"(broke ${recent_high:.2f}, vol: {volume_ratio:.1f}x)")
            
            # Bearish breakdown (break below recent low)
            elif (current_price < recent_low and 
                  volume_ratio >= min_breakout_volume and
                  (recent_low - current_price) / recent_low * 100 >= min_breakout_move):
                
                confidence = 0.8  # High confidence for breakdowns
                
                entry_price = current_price
                stop_loss = round_price_to_tick(recent_low * 1.002)  # Just above breakdown level
                profit_target = round_price_to_tick(entry_price * (1 - config.PROFIT_TARGET_PCT / 100))
                
                signals.append({
                    'type': 'SELL',
                    'confidence': confidence,
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'profit_target': profit_target,
                    'metadata': {
                        'breakdown_level': recent_low,
                        'breakdown_move': (recent_low - current_price) / recent_low * 100,
                        'volume_ratio': volume_ratio,
                        'trigger': 'bearish_breakdown'
                    }
                })
                
                self.logger.info(f"⬇️ Bearish breakdown: {symbol} @ ${current_price:.2f} "
                               f"(broke ${recent_low:.2f}, vol: {volume_ratio:.1f}x)")
            
            return signals
            
        except Exception as e:
            self.logger.error(f"❌ Error checking breakout momentum: {e}")
            return []
    
    def validate_signal(self, signal: ScalpingSignal, market_data: dict) -> bool:
        """Validate signal before execution"""
        try:
            # Check spread
            spread_pct = market_data.get('spread_pct', 0)
            if spread_pct > config.MAX_SPREAD_PCT:
                self.logger.warning(f"❌ Spread too wide for {signal.symbol}: {spread_pct:.2f}%")
                return False
            
            # Check volume
            volume = market_data.get('volume', 0)
            if volume < config.MIN_VOLUME:
                self.logger.warning(f"❌ Volume too low for {signal.symbol}: {volume:,}")
                return False
            
            # Check risk/reward ratio
            if signal.signal_type == "BUY":
                risk = signal.entry_price - signal.stop_loss
                reward = signal.profit_target - signal.entry_price
            else:
                risk = signal.stop_loss - signal.entry_price
                reward = signal.entry_price - signal.profit_target
            
            risk_reward_ratio = reward / risk if risk > 0 else 0
            
            if risk_reward_ratio < 1.5:  # Minimum 1.5:1 ratio
                self.logger.warning(f"❌ Poor risk/reward for {signal.symbol}: {risk_reward_ratio:.2f}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error validating signal: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Momentum Scalping Strategy Test")
    print("=" * 40)
    
    # Create test data
    dates = pd.date_range(start='2025-01-01', periods=100, freq='1min')
    
    # Generate sample price data with momentum
    base_price = 150.0
    returns = np.random.normal(0, 0.002, 100)
    returns[80:85] = 0.008  # Add momentum spike
    
    prices = base_price * np.exp(np.cumsum(returns))
    volumes = np.random.randint(1000, 5000, 100)
    volumes[80:85] = np.random.randint(8000, 12000, 5)  # Volume spike
    
    test_data = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': prices * 1.002,
        'low': prices * 0.998,
        'close': prices,
        'volume': volumes
    })
    
    test_data.set_index('timestamp', inplace=True)
    
    # Add indicators (simplified)
    test_data['ema_5'] = test_data['close'].ewm(span=5).mean()
    test_data['ema_13'] = test_data['close'].ewm(span=13).mean()
    test_data['rsi'] = 50  # Simplified
    test_data['vwap'] = test_data['close'].rolling(20).mean()
    test_data['price_change_5'] = test_data['close'].pct_change(5)
    
    # Test strategy
    strategy = MomentumIntradayStrategy()
    signals = strategy.generate_signals("TEST", test_data)
    
    print(f"Generated {len(signals)} signals")
    
    for signal in signals:
        print(f"Signal: {signal.signal_type} @ ${signal.entry_price:.2f} "
              f"(confidence: {signal.confidence:.2f}, "
              f"trigger: {signal.metadata.get('trigger', 'unknown')})")
