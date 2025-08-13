#!/usr/bin/env python3
"""
🔄 Mean Reversion Intraday Strategy
Captures price reversions to the mean on intraday timeframes
"""

import sys
import pandas as pd
import numpy as np
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

class MeanReversionIntradayStrategy:
    """Mean reversion intraday strategy"""
    
    def __init__(self):
        """Initialize mean reversion strategy"""
        self.logger = logging.getLogger("mean_reversion_strategy")
        self.name = "mean_reversion"
        self.config = get_strategy_config(self.name)
        self.min_bars = 30  # Need more data for mean reversion
        
        self.logger.info("🔄 Mean Reversion Strategy initialized")
    
    def generate_signals(self, symbol: str, data: pd.DataFrame) -> List[ScalpingSignal]:
        """Generate mean reversion signals"""
        try:
            if len(data) < self.min_bars:
                return []
            
            signals = []
            
            # Check mean reversion conditions
            reversion_signals = self._check_mean_reversion_conditions(data, symbol)
            
            for signal_data in reversion_signals:
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
            self.logger.error(f"❌ Error generating mean reversion signals for {symbol}: {e}")
            return []
    
    def _check_mean_reversion_conditions(self, data: pd.DataFrame, symbol: str) -> List[dict]:
        """Check for mean reversion trading conditions"""
        signals = []
        
        try:
            current = data.iloc[-1]
            prev = data.iloc[-2]
            
            current_price = current['close']
            
            # Calculate mean and standard deviation
            lookback_period = 20
            recent_data = data.tail(lookback_period)
            mean_price = recent_data['close'].mean()
            std_price = recent_data['close'].std()
            
            # Z-score (how many standard deviations from mean)
            z_score = (current_price - mean_price) / std_price if std_price > 0 else 0
            
            # Bollinger Bands
            bb_upper = current.get('bb_upper', mean_price + 2 * std_price)
            bb_lower = current.get('bb_lower', mean_price - 2 * std_price)
            bb_mid = current.get('bb_mid', mean_price)
            
            # RSI for oversold/overbought conditions
            rsi = current.get('rsi', 50)
            
            # VWAP analysis
            vwap = current.get('vwap', current_price)
            vwap_distance = (current_price - vwap) / vwap * 100
            
            # Volume analysis
            volume = current['volume']
            avg_volume = data['volume'].rolling(20).mean().iloc[-1]
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1
            
            # Price momentum for reversal detection
            price_change = (current_price - prev['close']) / prev['close'] * 100
            short_ema = current.get('ema_5', current_price)
            long_ema = current.get('ema_13', current_price)
            
            # 1. Oversold Mean Reversion (Buy Signal)
            oversold_conditions = [
                z_score <= -self.config.get('deviation_threshold', 2.0),  # 2+ std devs below mean
                current_price <= bb_lower,                                # Below lower Bollinger Band
                rsi <= config.RSI_OVERSOLD + 5,                          # Oversold but not extreme
                vwap_distance <= -0.3,                                   # Below VWAP
                price_change <= -0.2,                                    # Recent decline
                current_price < short_ema                                # Below short-term average
            ]
            
            # Check for reversal signs
            reversal_signs = [
                current['low'] > prev['low'],      # Higher low
                current['close'] > current['open'], # Green candle
                volume_ratio >= 0.8,              # Decent volume
                rsi > 25                          # Not extremely oversold
            ]
            
            if sum(oversold_conditions) >= 4 and sum(reversal_signs) >= 2:
                confidence = (sum(oversold_conditions) + sum(reversal_signs)) / (len(oversold_conditions) + len(reversal_signs))
                
                # Calculate reversion target
                reversion_target = mean_price * self.config.get('reversion_target', 0.5) + current_price * 0.5
                
                entry_price = current_price
                # Get adaptive levels first
                levels = calculate_adaptive_signal_levels(
                    symbol=symbol,
                    entry_price=entry_price,
                    signal_type='BUY'
                )

                # Use adaptive stop loss, but choose the nearer (more conservative) profit target for mean reversion
                stop_loss = levels['stop_loss']
                profit_target = round_price_to_tick(min(reversion_target, levels['profit_target']))
                
                signals.append({
                    'type': 'BUY',
                    'confidence': confidence,
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'profit_target': profit_target,
                    'metadata': {
                        'z_score': z_score,
                        'rsi': rsi,
                        'vwap_distance': vwap_distance,
                        'bb_position': (current_price - bb_lower) / (bb_upper - bb_lower),
                        'mean_price': mean_price,
                        'reversion_target': reversion_target,
                        'oversold_conditions': sum(oversold_conditions),
                        'reversal_signs': sum(reversal_signs),
                        'trigger': 'oversold_reversion'
                    }
                })
                
                self.logger.info(f"🟢 Oversold reversion signal: {symbol} - "
                               f"Price: ${entry_price:.2f}, "
                               f"Z-score: {z_score:.2f}, "
                               f"RSI: {rsi:.1f}, "
                               f"Target: ${profit_target:.2f}")
            
            # 2. Overbought Mean Reversion (Sell Signal)
            overbought_conditions = [
                z_score >= self.config.get('deviation_threshold', 2.0),   # 2+ std devs above mean
                current_price >= bb_upper,                                # Above upper Bollinger Band
                rsi >= config.RSI_OVERBOUGHT - 5,                        # Overbought but not extreme
                vwap_distance >= 0.3,                                    # Above VWAP
                price_change >= 0.2,                                     # Recent rally
                current_price > short_ema                                # Above short-term average
            ]
            
            # Check for reversal signs
            reversal_signs = [
                current['high'] < prev['high'],    # Lower high
                current['close'] < current['open'], # Red candle
                volume_ratio >= 0.8,              # Decent volume
                rsi < 75                          # Not extremely overbought
            ]
            
            if sum(overbought_conditions) >= 4 and sum(reversal_signs) >= 2:
                confidence = (sum(overbought_conditions) + sum(reversal_signs)) / (len(overbought_conditions) + len(reversal_signs))
                
                # Calculate reversion target
                reversion_target = mean_price * self.config.get('reversion_target', 0.5) + current_price * 0.5
                
                entry_price = current_price
                # Get adaptive levels first
                levels = calculate_adaptive_signal_levels(
                    symbol=symbol,
                    entry_price=entry_price,
                    signal_type='SELL'
                )

                # Use adaptive stop loss, but choose the nearer (more conservative) profit target for mean reversion
                stop_loss = levels['stop_loss']
                profit_target = round_price_to_tick(max(reversion_target, levels['profit_target']))
                
                signals.append({
                    'type': 'SELL',
                    'confidence': confidence,
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'profit_target': profit_target,
                    'metadata': {
                        'z_score': z_score,
                        'rsi': rsi,
                        'vwap_distance': vwap_distance,
                        'bb_position': (current_price - bb_lower) / (bb_upper - bb_lower),
                        'mean_price': mean_price,
                        'reversion_target': reversion_target,
                        'overbought_conditions': sum(overbought_conditions),
                        'reversal_signs': sum(reversal_signs),
                        'trigger': 'overbought_reversion'
                    }
                })
                
                self.logger.info(f"🔴 Overbought reversion signal: {symbol} - "
                               f"Price: ${entry_price:.2f}, "
                               f"Z-score: {z_score:.2f}, "
                               f"RSI: {rsi:.1f}, "
                               f"Target: ${profit_target:.2f}")
            
            # 3. VWAP Reversion Signal
            vwap_signals = self._check_vwap_reversion(data, symbol)
            signals.extend(vwap_signals)
            
            return signals
            
        except Exception as e:
            self.logger.error(f"❌ Error checking mean reversion conditions: {e}")
            return []
    
    def _check_vwap_reversion(self, data: pd.DataFrame, symbol: str) -> List[dict]:
        """Check for VWAP reversion opportunities"""
        signals = []
        
        try:
            current = data.iloc[-1]
            current_price = current['close']
            vwap = current.get('vwap', current_price)
            
            if vwap == current_price:  # No VWAP data
                return signals
            
            # VWAP distance
            vwap_distance = (current_price - vwap) / vwap * 100
            
            # Volume analysis
            volume = current['volume']
            avg_volume = data['volume'].rolling(20).mean().iloc[-1]
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1
            
            # Price action analysis
            price_change = (current_price - data.iloc[-2]['close']) / data.iloc[-2]['close'] * 100
            
            # RSI for confirmation
            rsi = current.get('rsi', 50)
            
            # VWAP reversion tolerance
            vwap_tolerance = 0.3  # 0.3%
            
            # 1. Price stretched above VWAP - expect reversion down
            if (vwap_distance >= vwap_tolerance and 
                price_change <= -0.1 and  # Starting to decline
                volume_ratio >= 1.0 and   # Good volume
                rsi >= 55):               # Not oversold
                
                confidence = min(0.7, abs(vwap_distance) / 1.0)  # Higher confidence for bigger stretches
                
                entry_price = current_price
                # Get adaptive levels
                levels = calculate_adaptive_signal_levels(
                    symbol=symbol,
                    entry_price=entry_price,
                    signal_type='SELL'
                )

                stop_loss = levels['stop_loss']
                profit_target = round_price_to_tick(vwap)  # Revert to VWAP
                
                signals.append({
                    'type': 'SELL',
                    'confidence': confidence,
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'profit_target': profit_target,
                    'metadata': {
                        'vwap': vwap,
                        'vwap_distance': vwap_distance,
                        'volume_ratio': volume_ratio,
                        'price_change': price_change,
                        'rsi': rsi,
                        'trigger': 'vwap_reversion_down'
                    }
                })
                
                self.logger.info(f"⬇️ VWAP reversion down: {symbol} - "
                               f"Price: ${entry_price:.2f}, "
                               f"VWAP: ${vwap:.2f}, "
                               f"Distance: {vwap_distance:+.2f}%")
            
            # 2. Price stretched below VWAP - expect reversion up
            elif (vwap_distance <= -vwap_tolerance and 
                  price_change >= 0.1 and   # Starting to rise
                  volume_ratio >= 1.0 and   # Good volume
                  rsi <= 45):               # Not overbought
                
                confidence = min(0.7, abs(vwap_distance) / 1.0)
                
                entry_price = current_price
                # Get adaptive levels
                levels = calculate_adaptive_signal_levels(
                    symbol=symbol,
                    entry_price=entry_price,
                    signal_type='BUY'
                )

                stop_loss = levels['stop_loss']
                profit_target = round_price_to_tick(vwap)  # Revert to VWAP
                
                signals.append({
                    'type': 'BUY',
                    'confidence': confidence,
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'profit_target': profit_target,
                    'metadata': {
                        'vwap': vwap,
                        'vwap_distance': vwap_distance,
                        'volume_ratio': volume_ratio,
                        'price_change': price_change,
                        'rsi': rsi,
                        'trigger': 'vwap_reversion_up'
                    }
                })
                
                self.logger.info(f"⬆️ VWAP reversion up: {symbol} - "
                               f"Price: ${entry_price:.2f}, "
                               f"VWAP: ${vwap:.2f}, "
                               f"Distance: {vwap_distance:+.2f}%")
            
            return signals
            
        except Exception as e:
            self.logger.error(f"❌ Error checking VWAP reversion: {e}")
            return []
    
    def validate_signal(self, signal: ScalpingSignal, market_data: dict) -> bool:
        """Validate mean reversion signal"""
        try:
            # Standard validations
            spread_pct = market_data.get('spread_pct', 0)
            if spread_pct > config.MAX_SPREAD_PCT:
                return False
            
            # For mean reversion, we want reasonable volume but not excessive
            volume = market_data.get('volume', 0)
            if volume < config.MIN_VOLUME * 0.5:  # Allow lower volume for reversion
                return False
            
            # Check that we're not too close to stop loss (bad risk/reward)
            if signal.signal_type == "BUY":
                risk = signal.entry_price - signal.stop_loss
                reward = signal.profit_target - signal.entry_price
            else:
                risk = signal.stop_loss - signal.entry_price
                reward = signal.entry_price - signal.profit_target
            
            if risk <= 0 or reward <= 0:
                return False
            
            risk_reward_ratio = reward / risk
            if risk_reward_ratio < 1.0:  # At least 1:1 for mean reversion
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error validating mean reversion signal: {e}")
            return False

if __name__ == "__main__":
    print("🔄 Mean Reversion Strategy Test")
    print("=" * 40)
    
    # Create test data with mean reversion pattern
    dates = pd.date_range(start='2025-01-01', periods=100, freq='1min')
    
    # Generate price data that oscillates around a mean
    base_price = 150.0
    trend = np.linspace(0, 0.02, 100)  # Slight upward trend
    
    # Add mean-reverting component
    mean_revert = np.sin(np.linspace(0, 4*np.pi, 100)) * 0.01  # Oscillation
    noise = np.random.normal(0, 0.001, 100)
    
    returns = trend + mean_revert + noise
    prices = base_price * np.exp(np.cumsum(returns))
    
    # Add extreme moves for testing
    prices[80] *= 1.015  # Spike up
    prices[85] *= 0.985  # Spike down
    
    volumes = np.random.randint(1000, 3000, 100)
    
    test_data = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': prices * 1.002,
        'low': prices * 0.998,
        'close': prices,
        'volume': volumes
    })
    
    test_data.set_index('timestamp', inplace=True)
    
    # Add indicators
    test_data['ema_5'] = test_data['close'].ewm(span=5).mean()
    test_data['ema_13'] = test_data['close'].ewm(span=13).mean()
    
    # RSI calculation
    delta = test_data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    test_data['rsi'] = 100 - (100 / (1 + rs))
    
    # VWAP and Bollinger Bands
    test_data['vwap'] = test_data['close'].rolling(20).mean()
    test_data['bb_mid'] = test_data['close'].rolling(20).mean()
    bb_std = test_data['close'].rolling(20).std()
    test_data['bb_upper'] = test_data['bb_mid'] + (bb_std * 2)
    test_data['bb_lower'] = test_data['bb_mid'] - (bb_std * 2)
    
    # Test strategy
    strategy = MeanReversionIntradayStrategy()
    signals = strategy.generate_signals("TEST", test_data)
    
    print(f"Generated {len(signals)} signals")
    
    for signal in signals:
        print(f"Signal: {signal.signal_type} @ ${signal.entry_price:.2f} "
              f"(confidence: {signal.confidence:.2f}, "
              f"trigger: {signal.metadata.get('trigger', 'unknown')}, "
              f"target: ${signal.profit_target:.2f})")
