"""
Unified Technical Indicator Service
Calculates each indicator ONCE and shares across all strategies
Eliminates duplication and potential conflicts
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from datetime import datetime
import logging

class UnifiedIndicatorService:
    """
    Centralized indicator calculation service
    Prevents duplication and ensures consistency across all strategies
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._indicator_cache = {}
        self._last_calculation_time = {}
        
    def calculate_unified_indicators(self, df: pd.DataFrame, symbol: str) -> Dict:
        """
        Calculate all indicators ONCE and return unified results
        This replaces individual strategy calculations
        """
        if len(df) < 50:
            return {'error': 'Insufficient data', 'indicators': {}}
        
        cache_key = f"{symbol}_{len(df)}_{df.iloc[-1]['close']}"
        
        # Return cached results if recent (within same bar)
        if cache_key in self._indicator_cache:
            return self._indicator_cache[cache_key]
        
        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']
        
        indicators = {}
        
        # CORE INDICATORS (calculated once, used by multiple strategies)
        
        # 1. RSI (14) - Used by Confidence Monitor & Mean Reversion
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators['rsi'] = 100 - (100 / (1 + rs))
        
        # 2. MACD (12/26/9) - Used by Confidence Monitor, Mean Reversion & Momentum
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        macd_signal = macd_line.ewm(span=9, adjust=False).mean()
        indicators['macd'] = macd_line
        indicators['macd_signal'] = macd_signal
        indicators['macd_histogram'] = macd_line - macd_signal
        
        # 3. EMA (9/21) - Used by Confidence Monitor & Mean Reversion
        indicators['ema_9'] = close.ewm(span=9, adjust=False).mean()
        indicators['ema_21'] = close.ewm(span=21, adjust=False).mean()
        
        # 4. VWAP - Used by Confidence Monitor, Momentum & VWAP Bounce
        typical_price = (high + low + close) / 3
        indicators['vwap'] = (typical_price * volume).cumsum() / volume.cumsum()
        
        # 5. Volume Analysis - Used by all strategies
        volume_ma = volume.rolling(window=20).mean()
        indicators['volume_ratio'] = volume / volume_ma
        
        # SPECIALIZED INDICATORS (strategy-specific)
        
        # Mean Reversion Specific
        indicators['bb_middle'] = close.rolling(window=20).mean()
        bb_std = close.rolling(window=20).std()
        indicators['bb_upper'] = indicators['bb_middle'] + (bb_std * 2)
        indicators['bb_lower'] = indicators['bb_middle'] - (bb_std * 2)
        
        # Stochastic for Mean Reversion
        lowest_low = low.rolling(window=14).min()
        highest_high = high.rolling(window=14).max()
        indicators['stoch_k'] = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        indicators['stoch_d'] = indicators['stoch_k'].rolling(window=3).mean()
        
        # Momentum Scalp Specific
        indicators['ema_13'] = close.ewm(span=13, adjust=False).mean()
        indicators['ema_50'] = close.ewm(span=50, adjust=False).mean()
        
        # ADX for Momentum
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=14).mean()
        indicators['atr'] = atr
        
        # Williams %R for Momentum
        indicators['williams_r'] = ((highest_high - close) / (highest_high - lowest_low)) * -100
        
        # Rate of Change for Momentum
        indicators['roc'] = ((close - close.shift(10)) / close.shift(10)) * 100
        
        # VWAP Bounce Specific
        # VWAP Standard Deviation Bands
        vwap_std = ((typical_price - indicators['vwap']) ** 2 * volume).rolling(window=20).sum() / volume.rolling(window=20).sum()
        vwap_std = np.sqrt(vwap_std)
        indicators['vwap_upper_1'] = indicators['vwap'] + vwap_std
        indicators['vwap_lower_1'] = indicators['vwap'] - vwap_std
        indicators['vwap_upper_2'] = indicators['vwap'] + (vwap_std * 2)
        indicators['vwap_lower_2'] = indicators['vwap'] - (vwap_std * 2)
        
        # On Balance Volume for VWAP Bounce
        obv = volume.where(close > close.shift(1), -volume).where(close != close.shift(1), 0).cumsum()
        indicators['obv'] = obv
        
        # Cache results
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'indicators': indicators,
            'current_values': {
                'price': close.iloc[-1],
                'volume': volume.iloc[-1],
                'rsi': indicators['rsi'].iloc[-1] if len(indicators['rsi']) > 0 else None,
                'macd_bullish': indicators['macd'].iloc[-1] > indicators['macd_signal'].iloc[-1] if len(indicators['macd']) > 0 else None,
                'above_ema9': close.iloc[-1] > indicators['ema_9'].iloc[-1] if len(indicators['ema_9']) > 0 else None,
                'above_vwap': close.iloc[-1] > indicators['vwap'].iloc[-1] if len(indicators['vwap']) > 0 else None,
                'bb_position': ((close.iloc[-1] - indicators['bb_lower'].iloc[-1]) / (indicators['bb_upper'].iloc[-1] - indicators['bb_lower'].iloc[-1])) if len(indicators['bb_lower']) > 0 else None
            }
        }
        
        self._indicator_cache[cache_key] = result
        self._last_calculation_time[symbol] = datetime.now()
        
        return result
    
    def get_indicators_for_strategy(self, df: pd.DataFrame, symbol: str, strategy_type: str) -> Dict:
        """
        Get strategy-specific indicator subset from unified calculations
        """
        unified_result = self.calculate_unified_indicators(df, symbol)
        
        if 'error' in unified_result:
            return unified_result
        
        indicators = unified_result['indicators']
        current = unified_result['current_values']
        
        if strategy_type == 'mean_reversion':
            return {
                'indicators': {
                    # Core shared indicators
                    'rsi': indicators['rsi'],
                    'bb_upper': indicators['bb_upper'],
                    'bb_middle': indicators['bb_middle'], 
                    'bb_lower': indicators['bb_lower'],
                    'ema_9': indicators['ema_9'],
                    'ema_21': indicators['ema_21'],
                    # Specialized indicators
                    'stoch_k': indicators['stoch_k'],
                    'stoch_d': indicators['stoch_d'],
                    'volume_ratio': indicators['volume_ratio']
                },
                'current_values': current
            }
            
        elif strategy_type == 'momentum_scalp':
            return {
                'indicators': {
                    # Core shared indicators (no duplication)
                    'macd': indicators['macd'],
                    'macd_signal': indicators['macd_signal'],
                    'macd_histogram': indicators['macd_histogram'],
                    'vwap': indicators['vwap'],
                    'ema_9': indicators['ema_9'],
                    'ema_21': indicators['ema_21'],
                    # Specialized indicators
                    'ema_13': indicators['ema_13'],
                    'ema_50': indicators['ema_50'],
                    'atr': indicators['atr'],
                    'williams_r': indicators['williams_r'],
                    'roc': indicators['roc'],
                    'volume_ratio': indicators['volume_ratio']
                },
                'current_values': current
            }
            
        elif strategy_type == 'vwap_bounce':
            return {
                'indicators': {
                    # Core shared indicators
                    'vwap': indicators['vwap'],
                    'volume_ratio': indicators['volume_ratio'],
                    # Specialized indicators
                    'vwap_upper_1': indicators['vwap_upper_1'],
                    'vwap_lower_1': indicators['vwap_lower_1'],
                    'vwap_upper_2': indicators['vwap_upper_2'],
                    'vwap_lower_2': indicators['vwap_lower_2'],
                    'obv': indicators['obv']
                },
                'current_values': current
            }
            
        else:
            # Return all indicators for confidence monitor or unknown strategy
            return unified_result
    
    def clear_cache(self, symbol: Optional[str] = None):
        """Clear indicator cache for symbol or all symbols"""
        if symbol:
            keys_to_remove = [k for k in self._indicator_cache.keys() if k.startswith(symbol)]
            for key in keys_to_remove:
                del self._indicator_cache[key]
            if symbol in self._last_calculation_time:
                del self._last_calculation_time[symbol]
        else:
            self._indicator_cache.clear()
            self._last_calculation_time.clear()

# Global unified service instance
unified_indicator_service = UnifiedIndicatorService()
