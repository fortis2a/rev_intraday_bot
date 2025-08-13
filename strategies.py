#!/usr/bin/env python3
"""
Trading Strategies for Intraday Trading Bot
ASCII-only, no Unicode characters
"""

import pandas as pd
import numpy as np
from datetime import datetime
from config import config
from logger import setup_logger, clean_message

class MomentumStrategy:
    """Momentum-based trading strategy"""
    
    def __init__(self):
        self.logger = setup_logger('momentum_strategy')
        self.name = "Momentum"
        self.logger.info("Momentum Strategy initialized")
    
    def generate_signal(self, symbol, df):
        """Generate trading signal based on momentum"""
        try:
            if df.empty or len(df) < 20:
                return None
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Check for momentum conditions
            price_change = latest['price_change']
            volume_ratio = latest['volume_ratio']
            rsi = latest['rsi']
            
            # Strong upward momentum signal
            if (price_change > config['MOMENTUM_THRESHOLD'] and 
                volume_ratio > config['VOLUME_MULTIPLIER'] and 
                rsi < 70 and 
                latest['close'] > latest['sma_10']):
                
                signal = {
                    'symbol': symbol,
                    'action': 'BUY',
                    'strategy': self.name,
                    'confidence': min(0.95, price_change * 20),
                    'reason': f"Strong momentum: {price_change:.1%} price move, {volume_ratio:.1f}x volume",
                    'price': latest['close'],
                    'rsi': rsi,
                    'volume_ratio': volume_ratio
                }
                
                self.logger.info(f"[SIGNAL] {symbol} BUY - {signal['reason']}")
                return signal
            
            # Strong downward momentum - avoid or sell
            elif (price_change < -config['MOMENTUM_THRESHOLD'] and 
                  volume_ratio > config['VOLUME_MULTIPLIER']):
                
                signal = {
                    'symbol': symbol,
                    'action': 'SELL',
                    'strategy': self.name,
                    'confidence': min(0.95, abs(price_change) * 20),
                    'reason': f"Negative momentum: {price_change:.1%} price drop, {volume_ratio:.1f}x volume",
                    'price': latest['close'],
                    'rsi': rsi,
                    'volume_ratio': volume_ratio
                }
                
                self.logger.info(f"[SIGNAL] {symbol} SELL - {signal['reason']}")
                return signal
            
            return None
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to generate momentum signal for {symbol}: {e}")
            return None

class MeanReversionStrategy:
    """Mean reversion trading strategy"""
    
    def __init__(self):
        self.logger = setup_logger('mean_reversion_strategy')
        self.name = "Mean Reversion"
        self.logger.info("Mean Reversion Strategy initialized")
    
    def generate_signal(self, symbol, df):
        """Generate trading signal based on mean reversion"""
        try:
            if df.empty or len(df) < 20:
                return None
            
            latest = df.iloc[-1]
            
            # Check for oversold conditions
            rsi = latest['rsi']
            price = latest['close']
            sma_20 = latest['sma_20']
            volume_ratio = latest['volume_ratio']
            
            # Oversold bounce signal
            if (rsi < config['RSI_OVERSOLD'] and 
                price < sma_20 * 0.98 and  # Price below SMA
                volume_ratio > 1.2):  # Some volume
                
                signal = {
                    'symbol': symbol,
                    'action': 'BUY',
                    'strategy': self.name,
                    'confidence': (config['RSI_OVERSOLD'] - rsi) / config['RSI_OVERSOLD'],
                    'reason': f"Oversold bounce: RSI {rsi:.1f}, price {((price/sma_20-1)*100):.1f}% below SMA",
                    'price': price,
                    'rsi': rsi,
                    'sma_distance': (price / sma_20 - 1) * 100
                }
                
                self.logger.info(f"[SIGNAL] {symbol} BUY - {signal['reason']}")
                return signal
            
            # Overbought reversal signal
            elif (rsi > config['RSI_OVERBOUGHT'] and 
                  price > sma_20 * 1.02):  # Price above SMA
                
                signal = {
                    'symbol': symbol,
                    'action': 'SELL',
                    'strategy': self.name,
                    'confidence': (rsi - config['RSI_OVERBOUGHT']) / (100 - config['RSI_OVERBOUGHT']),
                    'reason': f"Overbought reversal: RSI {rsi:.1f}, price {((price/sma_20-1)*100):.1f}% above SMA",
                    'price': price,
                    'rsi': rsi,
                    'sma_distance': (price / sma_20 - 1) * 100
                }
                
                self.logger.info(f"[SIGNAL] {symbol} SELL - {signal['reason']}")
                return signal
            
            return None
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to generate mean reversion signal for {symbol}: {e}")
            return None

class VWAPStrategy:
    """Volume Weighted Average Price strategy"""
    
    def __init__(self):
        self.logger = setup_logger('vwap_strategy')
        self.name = "VWAP"
        self.logger.info("VWAP Strategy initialized")
    
    def calculate_vwap(self, df):
        """Calculate VWAP"""
        try:
            if df.empty:
                return df
            
            # Typical price
            df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
            
            # Volume * Typical Price
            df['volume_price'] = df['typical_price'] * df['volume']
            
            # Cumulative values
            df['cum_volume_price'] = df['volume_price'].cumsum()
            df['cum_volume'] = df['volume'].cumsum()
            
            # VWAP
            df['vwap'] = df['cum_volume_price'] / df['cum_volume']
            
            return df
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to calculate VWAP: {e}")
            return df
    
    def generate_signal(self, symbol, df):
        """Generate trading signal based on VWAP"""
        try:
            if df.empty or len(df) < 10:
                return None
            
            # Calculate VWAP
            df = self.calculate_vwap(df)
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            price = latest['close']
            vwap = latest['vwap']
            volume_ratio = latest['volume_ratio']
            
            # Price crossing above VWAP with volume
            if (price > vwap and 
                prev['close'] <= prev['vwap'] and 
                volume_ratio > 1.3):
                
                signal = {
                    'symbol': symbol,
                    'action': 'BUY',
                    'strategy': self.name,
                    'confidence': min(0.9, volume_ratio / 2),
                    'reason': f"VWAP breakout: price ${price:.2f} above VWAP ${vwap:.2f}",
                    'price': price,
                    'vwap': vwap,
                    'vwap_distance': (price / vwap - 1) * 100
                }
                
                self.logger.info(f"[SIGNAL] {symbol} BUY - {signal['reason']}")
                return signal
            
            # Price falling below VWAP with volume
            elif (price < vwap and 
                  prev['close'] >= prev['vwap'] and 
                  volume_ratio > 1.3):
                
                signal = {
                    'symbol': symbol,
                    'action': 'SELL',
                    'strategy': self.name,
                    'confidence': min(0.9, volume_ratio / 2),
                    'reason': f"VWAP breakdown: price ${price:.2f} below VWAP ${vwap:.2f}",
                    'price': price,
                    'vwap': vwap,
                    'vwap_distance': (price / vwap - 1) * 100
                }
                
                self.logger.info(f"[SIGNAL] {symbol} SELL - {signal['reason']}")
                return signal
            
            return None
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to generate VWAP signal for {symbol}: {e}")
            return None
