#!/usr/bin/env python3
"""
📊 VWAP Bounce Intraday Strategy
Trades bounces off the Volume Weighted Average Price on intraday timeframes
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

class VWAPBounceIntradayStrategy:
    """VWAP bounce intraday strategy"""
    
    def __init__(self):
        """Initialize VWAP bounce strategy"""
        self.logger = logging.getLogger("vwap_strategy")
        self.name = "vwap_bounce"
        self.config = get_strategy_config(self.name)
        self.min_bars = 25  # Need sufficient data for VWAP
        
        self.logger.info("📊 VWAP Bounce Strategy initialized")
    
    def generate_signals(self, symbol: str, data: pd.DataFrame) -> List[ScalpingSignal]:
        """Generate VWAP bounce signals"""
        try:
            if len(data) < self.min_bars:
                return []
            
            signals = []
            
            # Check VWAP bounce conditions
            bounce_signals = self._check_vwap_bounce_conditions(data, symbol)
            
            for signal_data in bounce_signals:
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
            self.logger.error(f"❌ Error generating VWAP bounce signals for {symbol}: {e}")
            return []
    
    def _check_vwap_bounce_conditions(self, data: pd.DataFrame, symbol: str) -> List[dict]:
        """Check for VWAP bounce trading conditions with enhanced profitability"""
        signals = []
        
        try:
            current = data.iloc[-1]
            prev = data.iloc[-2]
            prev2 = data.iloc[-3] if len(data) >= 3 else prev
            
            current_price = current['close']
            vwap = current.get('vwap', current_price)
            
            if vwap == current_price:  # No VWAP data
                return signals
            
            # VWAP distance and trend analysis
            vwap_distance = (current_price - vwap) / vwap * 100
            prev_vwap_distance = (prev['close'] - prev.get('vwap', prev['close'])) / prev.get('vwap', prev['close']) * 100 if prev.get('vwap') else vwap_distance
            
            # Enhanced volume analysis
            volume = current['volume']
            avg_volume = data['volume'].rolling(20).mean().iloc[-1]
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1
            volume_trend = volume > data['volume'].rolling(5).mean().iloc[-1]
            
            # Price action momentum
            price_change = (current_price - prev['close']) / prev['close'] * 100
            price_momentum = data['close'].pct_change(3).iloc[-1] * 100  # 3-bar momentum
            
            # Technical indicators
            rsi = current.get('rsi', 50)
            ema_5 = current.get('ema_5', current_price)
            ema_13 = current.get('ema_13', current_price)
            
            # Bollinger Bands for mean reversion
            bb_upper = current.get('bb_upper', current_price * 1.02)
            bb_lower = current.get('bb_lower', current_price * 0.98)
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5
            
            # Enhanced VWAP touch criteria
            touch_tolerance = 0.08  # Tighter tolerance for better entries
            strong_volume_threshold = 1.8  # Require stronger volume
            
            # Market structure analysis
            recent_high = data['high'].rolling(10).max().iloc[-1]
            recent_low = data['low'].rolling(10).min().iloc[-1]
            price_position = (current_price - recent_low) / (recent_high - recent_low) if recent_high != recent_low else 0.5
            
            # 1. Enhanced Bullish VWAP Bounce
            # Price near or below VWAP with bullish reversal signals
            near_vwap_support = (-0.15 <= vwap_distance <= 0.05)  # Tighter range
            bounce_confirmation = (current_price > prev['low'] and price_change > 0.02)
            strong_volume_support = (volume_ratio >= strong_volume_threshold and volume_trend)
            oversold_condition = (rsi < 45 or bb_position < 0.3)
            momentum_reversal = (price_momentum < 0 and price_change > 0)  # Recent decline, current bounce
            
            if (near_vwap_support and bounce_confirmation and strong_volume_support and 
                oversold_condition and current_price < vwap * 1.001):
                
                # Enhanced confidence calculation
                confidence = 0.65  # Base confidence
                
                # Volume confirmation boost
                if volume_ratio >= 2.5:
                    confidence += 0.12
                elif volume_ratio >= 2.0:
                    confidence += 0.08
                elif volume_ratio >= 1.8:
                    confidence += 0.05
                
                # VWAP precision boost
                if abs(vwap_distance) < 0.05:  # Very close to VWAP
                    confidence += 0.10
                elif abs(vwap_distance) < 0.10:
                    confidence += 0.05
                
                # RSI positioning boost
                if 25 < rsi < 40:  # Oversold but not extreme
                    confidence += 0.08
                
                # Momentum reversal boost
                if momentum_reversal and price_change > 0.05:
                    confidence += 0.07
                
                # Market position boost
                if price_position < 0.4:  # Near recent lows
                    confidence += 0.05
                
                confidence = min(confidence, 0.92)  # Cap confidence
                
                # Calculate levels
                levels = calculate_adaptive_signal_levels(
                    data, 'BUY', current_price, self.config
                )
                
                # Tighter stop below VWAP
                vwap_stop = vwap * (1 - touch_tolerance/100)
                stop_loss = min(levels['stop_loss'], vwap_stop)
                
                signals.append({
                    'type': 'BUY',
                    'confidence': confidence,
                    'entry_price': round_price_to_tick(current_price),
                    'stop_loss': round_price_to_tick(stop_loss),
                    'profit_target': levels['profit_target'],
                    'metadata': {
                        'vwap': vwap,
                        'vwap_distance': vwap_distance,
                        'volume_ratio': volume_ratio,
                        'rsi': rsi,
                        'bb_position': bb_position,
                        'price_position': price_position,
                        'bounce_type': 'vwap_support_bounce'
                    }
                })
            
            # 2. Enhanced Bearish VWAP Rejection
            # Price near or above VWAP with bearish reversal signals
            near_vwap_resistance = (-0.05 <= vwap_distance <= 0.15)  # Tighter range
            rejection_confirmation = (current_price < prev['high'] and price_change < -0.02)
            strong_volume_resistance = (volume_ratio >= strong_volume_threshold and volume_trend)
            overbought_condition = (rsi > 55 or bb_position > 0.7)
            momentum_reversal_bear = (price_momentum > 0 and price_change < 0)  # Recent rally, current decline
            
            if (near_vwap_resistance and rejection_confirmation and strong_volume_resistance and 
                overbought_condition and current_price > vwap * 0.999):
                
                # Enhanced confidence calculation
                confidence = 0.65  # Base confidence
                
                # Volume confirmation boost
                if volume_ratio >= 2.5:
                    confidence += 0.12
                elif volume_ratio >= 2.0:
                    confidence += 0.08
                elif volume_ratio >= 1.8:
                    confidence += 0.05
                
                # VWAP precision boost
                if abs(vwap_distance) < 0.05:  # Very close to VWAP
                    confidence += 0.10
                elif abs(vwap_distance) < 0.10:
                    confidence += 0.05
                
                # RSI positioning boost
                if 60 < rsi < 75:  # Overbought but not extreme
                    confidence += 0.08
                
                # Momentum reversal boost
                if momentum_reversal_bear and price_change < -0.05:
                    confidence += 0.07
                
                # Market position boost
                if price_position > 0.6:  # Near recent highs
                    confidence += 0.05
                
                confidence = min(confidence, 0.92)  # Cap confidence
                
                # Calculate levels
                levels = calculate_adaptive_signal_levels(
                    data, 'SELL', current_price, self.config
                )
                
                # Tighter stop above VWAP
                vwap_stop = vwap * (1 + touch_tolerance/100)
                stop_loss = max(levels['stop_loss'], vwap_stop)
                
                signals.append({
                    'type': 'SELL',
                    'confidence': confidence,
                    'entry_price': round_price_to_tick(current_price),
                    'stop_loss': round_price_to_tick(stop_loss),
                    'profit_target': levels['profit_target'],
                    'metadata': {
                        'vwap': vwap,
                        'vwap_distance': vwap_distance,
                        'volume_ratio': volume_ratio,
                        'rsi': rsi,
                        'bb_position': bb_position,
                        'price_position': price_position,
                        'bounce_type': 'vwap_resistance_rejection'
                    }
                })
            
            return signals
            
        except Exception as e:
            self.logger.error(f"❌ Error in VWAP bounce analysis for {symbol}: {e}")
            return signals
            error_key = f"vwap_bounce_{symbol}"
            
            if (error_key not in self.last_error_time or 
                current_time - self.last_error_time[error_key] >= 60):  # Log error max once per minute
                self.logger.error(f"❌ Error checking VWAP bounce conditions: {e}")
                self.last_error_time[error_key] = current_time
            return []
    
    def _check_bullish_vwap_bounce(self, data: pd.DataFrame, current: pd.Series, prev: pd.Series, prev2: pd.Series,
                                  vwap: float, vwap_distance: float, prev_vwap_distance: float,
                                  volume_ratio: float, price_change: float, rsi: float,
                                  touch_tolerance: float, volume_confirmation: float) -> dict:
        """Check for bullish VWAP bounce conditions"""
        try:
            current_price = current['close']
            
            # Type 1: Direct bounce from VWAP
            near_vwap = abs(vwap_distance) <= touch_tolerance
            bouncing_up = (prev_vwap_distance < -touch_tolerance/2 and vwap_distance > prev_vwap_distance)
            volume_ok = volume_ratio >= volume_confirmation
            rsi_not_overbought = rsi <= 65
            green_candle = current['close'] > current['open']
            
            direct_bounce_conditions = [
                near_vwap,
                bouncing_up,
                volume_ok,
                rsi_not_overbought,
                green_candle,
                price_change >= 0.05  # Small positive move
            ]
            
            # Type 2: Pullback to VWAP after uptrend
            recent_uptrend = current['close'] > data.iloc[-5]['close']  # Higher than 5 bars ago
            pullback_to_vwap = (prev_vwap_distance > touch_tolerance and 
                               abs(vwap_distance) <= touch_tolerance)
            support_hold = current['low'] >= vwap * 0.999  # Didn't break below VWAP
            
            pullback_conditions = [
                recent_uptrend,
                pullback_to_vwap,
                support_hold,
                volume_ok,
                rsi >= 40,  # Not oversold
                current['close'] >= current['open']  # Not breaking down
            ]
            
            # Type 3: Failed breakdown bounce
            tried_breakdown = prev['low'] <= vwap and current['low'] > vwap
            quick_recovery = current['close'] > prev['close']
            volume_spike = volume_ratio >= 1.5
            
            failed_breakdown_conditions = [
                tried_breakdown,
                quick_recovery,
                volume_spike,
                rsi >= 35,
                current['close'] > current['open']
            ]
            
            # Determine best signal
            best_signal = None
            max_conditions = 0
            
            if sum(direct_bounce_conditions) >= 4:
                confidence = sum(direct_bounce_conditions) / len(direct_bounce_conditions)
                best_signal = {
                    'signal': True,
                    'confidence': confidence,
                    'bounce_type': 'direct_bounce',
                    'conditions_met': sum(direct_bounce_conditions)
                }
                max_conditions = sum(direct_bounce_conditions)
            
            if sum(pullback_conditions) >= 4 and sum(pullback_conditions) > max_conditions:
                confidence = sum(pullback_conditions) / len(pullback_conditions)
                best_signal = {
                    'signal': True,
                    'confidence': confidence,
                    'bounce_type': 'pullback_bounce',
                    'conditions_met': sum(pullback_conditions)
                }
                max_conditions = sum(pullback_conditions)
            
            if sum(failed_breakdown_conditions) >= 4 and sum(failed_breakdown_conditions) > max_conditions:
                confidence = sum(failed_breakdown_conditions) / len(failed_breakdown_conditions)
                best_signal = {
                    'signal': True,
                    'confidence': confidence,
                    'bounce_type': 'failed_breakdown',
                    'conditions_met': sum(failed_breakdown_conditions)
                }
            
            return best_signal or {'signal': False, 'confidence': 0, 'bounce_type': None, 'conditions_met': 0}
            
        except Exception as e:
            self.logger.error(f"❌ Error checking bullish VWAP bounce: {e}")
            return {'signal': False, 'confidence': 0, 'bounce_type': None, 'conditions_met': 0}
    
    def _check_bearish_vwap_bounce(self, data: pd.DataFrame, current: pd.Series, prev: pd.Series, prev2: pd.Series,
                                  vwap: float, vwap_distance: float, prev_vwap_distance: float,
                                  volume_ratio: float, price_change: float, rsi: float,
                                  touch_tolerance: float, volume_confirmation: float) -> dict:
        """Check for bearish VWAP bounce conditions"""
        try:
            current_price = current['close']
            
            # Type 1: Direct rejection from VWAP
            near_vwap = abs(vwap_distance) <= touch_tolerance
            rejecting_down = (prev_vwap_distance > touch_tolerance/2 and vwap_distance < prev_vwap_distance)
            volume_ok = volume_ratio >= volume_confirmation
            rsi_not_oversold = rsi >= 35
            red_candle = current['close'] < current['open']
            
            direct_rejection_conditions = [
                near_vwap,
                rejecting_down,
                volume_ok,
                rsi_not_oversold,
                red_candle,
                price_change <= -0.05  # Small negative move
            ]
            
            # Type 2: Rally to VWAP after downtrend
            recent_downtrend = current['close'] < data.iloc[-5]['close']  # Lower than 5 bars ago
            rally_to_vwap = (prev_vwap_distance < -touch_tolerance and 
                            abs(vwap_distance) <= touch_tolerance)
            resistance_hold = current['high'] <= vwap * 1.001  # Didn't break above VWAP
            
            rally_conditions = [
                recent_downtrend,
                rally_to_vwap,
                resistance_hold,
                volume_ok,
                rsi <= 60,  # Not overbought
                current['close'] <= current['open']  # Not breaking up
            ]
            
            # Type 3: Failed breakout rejection
            tried_breakout = prev['high'] >= vwap and current['high'] < vwap
            quick_selloff = current['close'] < prev['close']
            volume_spike = volume_ratio >= 1.5
            
            failed_breakout_conditions = [
                tried_breakout,
                quick_selloff,
                volume_spike,
                rsi <= 65,
                current['close'] < current['open']
            ]
            
            # Determine best signal
            best_signal = None
            max_conditions = 0
            
            if sum(direct_rejection_conditions) >= 4:
                confidence = sum(direct_rejection_conditions) / len(direct_rejection_conditions)
                best_signal = {
                    'signal': True,
                    'confidence': confidence,
                    'bounce_type': 'direct_rejection',
                    'conditions_met': sum(direct_rejection_conditions)
                }
                max_conditions = sum(direct_rejection_conditions)
            
            if sum(rally_conditions) >= 4 and sum(rally_conditions) > max_conditions:
                confidence = sum(rally_conditions) / len(rally_conditions)
                best_signal = {
                    'signal': True,
                    'confidence': confidence,
                    'bounce_type': 'rally_rejection',
                    'conditions_met': sum(rally_conditions)
                }
                max_conditions = sum(rally_conditions)
            
            if sum(failed_breakout_conditions) >= 4 and sum(failed_breakout_conditions) > max_conditions:
                confidence = sum(failed_breakout_conditions) / len(failed_breakout_conditions)
                best_signal = {
                    'signal': True,
                    'confidence': confidence,
                    'bounce_type': 'failed_breakout',
                    'conditions_met': sum(failed_breakout_conditions)
                }
            
            return best_signal or {'signal': False, 'confidence': 0, 'bounce_type': None, 'conditions_met': 0}
            
        except Exception as e:
            self.logger.error(f"❌ Error checking bearish VWAP bounce: {e}")
            return {'signal': False, 'confidence': 0, 'bounce_type': None, 'conditions_met': 0}
    
    def validate_signal(self, signal: ScalpingSignal, market_data: dict) -> bool:
        """Validate VWAP bounce signal"""
        try:
            # Standard validations
            spread_pct = market_data.get('spread_pct', 0)
            if spread_pct > config.MAX_SPREAD_PCT:
                return False
            
            # VWAP bounce needs good volume
            volume = market_data.get('volume', 0)
            if volume < config.MIN_VOLUME * 0.8:
                return False
            
            # Check VWAP is available and meaningful
            vwap = signal.metadata.get('vwap')
            if not vwap or vwap <= 0:
                return False
            
            # Ensure we're close enough to VWAP to be meaningful
            vwap_distance = abs(signal.metadata.get('vwap_distance', 0))
            if vwap_distance > 1.0:  # More than 1% from VWAP
                return False
            
            # Risk/reward validation
            if signal.signal_type == "BUY":
                risk = signal.entry_price - signal.stop_loss
                reward = signal.profit_target - signal.entry_price
            else:
                risk = signal.stop_loss - signal.entry_price
                reward = signal.entry_price - signal.profit_target
            
            if risk <= 0 or reward <= 0:
                return False
            
            risk_reward_ratio = reward / risk
            if risk_reward_ratio < 1.5:  # At least 1.5:1 for VWAP bounces
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error validating VWAP bounce signal: {e}")
            return False

if __name__ == "__main__":
    print("📊 VWAP Bounce Strategy Test")
    print("=" * 40)
    
    # Create test data with VWAP interactions
    dates = pd.date_range(start='2025-01-01', periods=100, freq='1min')
    
    # Generate price data that interacts with VWAP
    base_price = 150.0
    vwap_line = base_price + np.sin(np.linspace(0, 2*np.pi, 100)) * 2  # Wavy VWAP
    
    # Price oscillates around VWAP
    price_offset = np.sin(np.linspace(0, 8*np.pi, 100)) * 1.5  # Higher frequency oscillation
    noise = np.random.normal(0, 0.2, 100)
    
    prices = vwap_line + price_offset + noise
    
    # Add some bounces and rejections
    for i in [30, 50, 70, 90]:
        if i < len(prices):
            # Create bounce pattern
            if prices[i] < vwap_line[i]:  # Below VWAP
                prices[i:i+3] = np.linspace(prices[i], vwap_line[i] + 0.5, 3)  # Bounce up
            else:  # Above VWAP
                prices[i:i+3] = np.linspace(prices[i], vwap_line[i] - 0.5, 3)  # Reject down
    
    volumes = np.random.randint(1000, 3000, 100)
    # Add volume spikes at bounce points
    for i in [30, 50, 70, 90]:
        if i < len(volumes):
            volumes[i] = np.random.randint(4000, 6000)
    
    test_data = pd.DataFrame({
        'timestamp': dates,
        'open': prices * 0.999,
        'high': prices * 1.001,
        'low': prices * 0.999,
        'close': prices,
        'volume': volumes
    })
    
    test_data.set_index('timestamp', inplace=True)
    
    # Add indicators
    test_data['ema_5'] = test_data['close'].ewm(span=5).mean()
    test_data['ema_13'] = test_data['close'].ewm(span=13).mean()
    test_data['vwap'] = vwap_line  # Use our constructed VWAP
    
    # RSI calculation
    delta = test_data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    test_data['rsi'] = 100 - (100 / (1 + rs))
    
    # Test strategy
    strategy = VWAPBounceIntradayStrategy()
    signals = strategy.generate_signals("TEST", test_data)
    
    print(f"Generated {len(signals)} signals")
    
    for signal in signals:
        vwap_dist = signal.metadata.get('vwap_distance', 0)
        bounce_type = signal.metadata.get('bounce_type', 'unknown')
        print(f"Signal: {signal.signal_type} @ ${signal.entry_price:.2f} "
              f"(VWAP: ${signal.metadata.get('vwap', 0):.2f}, "
              f"dist: {vwap_dist:+.2f}%, "
              f"type: {bounce_type}, "
              f"confidence: {signal.confidence:.2f})")
