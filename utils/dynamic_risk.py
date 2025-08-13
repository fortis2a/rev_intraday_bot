#!/usr/bin/env python3
"""
🎯 Dynamic Risk Calculator
Calculates adaptive stop loss and profit targets based on stock volatility
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from config import config
from utils.logger import setup_logger

class DynamicRiskCalculator:
    """Calculate adaptive risk parameters based on stock characteristics"""
    
    def __init__(self):
        self.logger = setup_logger("dynamic_risk")
        self.volatility_cache = {}
        self.last_update = {}
        
    def get_stock_volatility(self, symbol: str, data_manager=None) -> float:
        """Get daily volatility for a stock"""
        try:
            # Check cache (update every hour)
            now = datetime.now()
            if (symbol in self.volatility_cache and 
                symbol in self.last_update and 
                (now - self.last_update[symbol]).total_seconds() < 3600):
                return self.volatility_cache[symbol]
            
            # If no data manager provided, use default volatility
            if data_manager is None:
                default_vol = self._get_default_volatility(symbol)
                self.logger.debug(f"📊 {symbol} using default volatility: {default_vol:.2f}%")
                return default_vol
            
            # Get 20 days of daily data for volatility calculation
            bars = data_manager.get_market_data(symbol, "1Day", 20)
            
            if bars is None or len(bars) < 10:
                # Fallback to default volatility
                default_vol = self._get_default_volatility(symbol)
                self.logger.warning(f"⚠️ No data for {symbol}, using default volatility: {default_vol:.2f}%")
                return default_vol
            
            # Calculate daily returns
            bars['daily_return'] = bars['close'].pct_change()
            
            # Calculate volatility (standard deviation of returns)
            volatility = bars['daily_return'].std() * 100  # Convert to percentage
            
            # Cache the result
            self.volatility_cache[symbol] = volatility
            self.last_update[symbol] = now
            
            self.logger.debug(f"📊 {symbol} daily volatility: {volatility:.2f}%")
            return volatility
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating volatility for {symbol}: {e}")
            return self._get_default_volatility(symbol)
    
    def _get_default_volatility(self, symbol: str) -> float:
        """Get default volatility estimates for common stocks"""
        # Common volatility estimates (daily %)
        volatility_map = {
            # Tech stocks (higher volatility)
            'TSLA': 4.0, 'AMD': 3.5, 'NVDA': 3.2, 'ROKU': 4.5,
            'ZOOM': 3.8, 'UBER': 3.0, 'NFLX': 2.8,
            
            # Mega-cap tech (medium-high volatility)
            'AAPL': 2.2, 'MSFT': 2.0, 'GOOGL': 2.5, 'AMZN': 2.8,
            'META': 3.0, 'CRM': 2.5,
            
            # Quantum/biotech (very high volatility)
            'IONQ': 5.0, 'MRNA': 4.2, 'PFE': 1.8,
            
            # Financial (medium volatility)
            'JPM': 2.0, 'BAC': 2.2, 'WFC': 2.4, 'C': 2.8, 'GS': 2.6,
            
            # ETFs (lower volatility)
            'SPY': 1.2, 'QQQ': 1.8, 'IWM': 2.0, 'XLF': 1.8, 'XLK': 2.2,
            
            # Commodities (high volatility)
            'XOM': 2.5, 'CVX': 2.3, 'VALE': 3.5, 'FCX': 4.0,
        }
        
        return volatility_map.get(symbol, 2.5)  # Default 2.5% if unknown
    
    def calculate_adaptive_levels(self, symbol: str, entry_price: float, 
                                signal_type: str = "BUY", data_manager=None, timeframe: str = None) -> Dict[str, float]:
        """Calculate adaptive stop loss, profit target, and trailing stop using historical data"""
        try:
            # Import config here to get current timeframe
            from config import config, get_timeframe_config
            from utils.historical_analyzer import historical_analyzer
            
            # Use provided timeframe or fall back to config
            if timeframe is None:
                timeframe = config.TIMEFRAME
            
            # Get timeframe-specific settings
            timeframe_config = get_timeframe_config(timeframe)
            max_hold_time = timeframe_config.get('max_hold_time', 300)  # seconds
            
            # Get real historical movements for this stock and timeframe
            movements = historical_analyzer.calculate_real_movements(
                symbol=symbol, 
                timeframe=timeframe, 
                days_back=7, 
                data_manager=data_manager
            )
            
            # Use historical data if available, otherwise fall back to volatility-based
            if movements.get('is_fallback', False):
                # Fallback to old volatility-based method
                self.logger.warning(f"⚠️ Using fallback volatility method for {symbol}")
                return self._calculate_volatility_based_levels(
                    symbol, entry_price, signal_type, timeframe, max_hold_time
                )
            
            # Use historical movement analysis
            base_stop_pct = movements['suggested_stop_pct']
            base_profit_pct = movements['suggested_profit_pct']
            
            # Get trailing stop based on movement patterns
            trailing_stop_pct = min(base_stop_pct * 0.7, 0.4)  # 70% of stop loss, max 0.4%
            
            # Calculate actual price levels
            if signal_type == "BUY":
                stop_loss = entry_price * (1 - base_stop_pct / 100)
                profit_target = entry_price * (1 + base_profit_pct / 100)
            else:  # SELL
                stop_loss = entry_price * (1 + base_stop_pct / 100)
                profit_target = entry_price * (1 - base_profit_pct / 100)
            
            # Log historical levels only on first calculation or significant changes
            if not hasattr(self, 'last_levels_log'):
                self.last_levels_log = {}
            
            should_log = (symbol not in self.last_levels_log or 
                         abs(movements['avg_move_pct'] - self.last_levels_log.get(symbol, {}).get('avg_move_pct', 0)) > 0.01)
            
            if should_log:
                self.logger.info(f"📊 {symbol} historical levels ({timeframe}, {movements['total_bars']} bars): "
                               f"AvgMove={movements['avg_move_pct']:.3f}%, "
                               f"Stop={base_stop_pct:.3f}%, "
                               f"Target={base_profit_pct:.3f}%, "
                               f"Trail={trailing_stop_pct:.3f}%")
                self.last_levels_log[symbol] = movements
            
            return {
                'stop_loss': stop_loss,
                'profit_target': profit_target,
                'trailing_stop_pct': trailing_stop_pct,
                'volatility': movements['avg_move_pct'],  # Use average move as "volatility"
                'stop_loss_pct': base_stop_pct,
                'profit_target_pct': base_profit_pct,
                'method': 'historical',
                'bars_analyzed': movements['total_bars'],
                'avg_move_pct': movements['avg_move_pct'],
                'p75_move_pct': movements['p75_move_pct'],
                'p90_move_pct': movements['p90_move_pct']
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating historical levels for {symbol}: {e}")
            # Fallback to volatility-based method
            return self._calculate_volatility_based_levels(
                symbol, entry_price, signal_type, timeframe or config.TIMEFRAME, 
                max_hold_time if 'max_hold_time' in locals() else 300
            )
    
    def _calculate_volatility_based_levels(self, symbol: str, entry_price: float, 
                                         signal_type: str, timeframe: str, max_hold_time: int) -> Dict[str, float]:
        """Fallback to volatility-based calculation when historical data unavailable"""
        try:
            # Get stock volatility
            volatility = self.get_stock_volatility(symbol, None)
            
            # Calculate base adaptive parameters based on volatility
            base_stop_multiplier = self._get_stop_multiplier(volatility)
            base_profit_multiplier = self._get_profit_multiplier(volatility)
            base_trailing_multiplier = self._get_trailing_multiplier(volatility)
            
            # Apply timeframe scaling to profit targets
            timeframe_scale = self._get_timeframe_scale(max_hold_time)
            
            # Scale profit targets based on timeframe (stops stay based on volatility)
            scaled_profit_multiplier = base_profit_multiplier * timeframe_scale
            
            # Calculate actual levels
            if signal_type == "BUY":
                stop_loss = entry_price * (1 - base_stop_multiplier / 100)
                profit_target = entry_price * (1 + scaled_profit_multiplier / 100)
                trailing_stop_pct = base_trailing_multiplier
            else:  # SELL
                stop_loss = entry_price * (1 + base_stop_multiplier / 100)
                profit_target = entry_price * (1 - scaled_profit_multiplier / 100)
                trailing_stop_pct = base_trailing_multiplier
            
            # Log the volatility-based fallback calculation
            self.logger.info(f"🎯 {symbol} volatility-based levels ({timeframe}, {max_hold_time}s): Vol={volatility:.2f}%, "
                           f"Stop={base_stop_multiplier:.2f}%, "
                           f"Target={scaled_profit_multiplier:.2f}% (scale: {timeframe_scale:.2f}), "
                           f"Trail={base_trailing_multiplier:.2f}%")
            
            return {
                'stop_loss': stop_loss,
                'profit_target': profit_target,
                'trailing_stop_pct': trailing_stop_pct,
                'volatility': volatility,
                'stop_loss_pct': base_stop_multiplier,
                'profit_target_pct': scaled_profit_multiplier,
                'timeframe_scale': timeframe_scale,
                'method': 'volatility_fallback'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error in volatility fallback for {symbol}: {e}")
            # Final fallback to static configuration
            return self._get_static_levels(entry_price, signal_type)
    
    def get_adaptive_trailing_stop(self, symbol: str, data_manager=None, timeframe: str = None) -> float:
        """Get adaptive trailing stop percentage for a symbol"""
        try:
            from config import config
            from utils.historical_analyzer import historical_analyzer
            
            if timeframe is None:
                timeframe = config.TIMEFRAME
            
            # Try to get historical movement data
            movements = historical_analyzer.calculate_real_movements(
                symbol=symbol, 
                timeframe=timeframe, 
                days_back=7, 
                data_manager=data_manager
            )
            
            if not movements.get('is_fallback', False):
                # Use historical data
                trailing_pct = min(movements['suggested_stop_pct'] * 0.7, 0.4)  # 70% of stop loss
                self.logger.debug(f"🔄 {symbol} historical trailing stop: {trailing_pct:.3f}% "
                                f"(based on {movements['total_bars']} bars)")
                return trailing_pct
            else:
                # Fallback to volatility-based
                volatility = self.get_stock_volatility(symbol, data_manager)
                trailing_pct = self._get_trailing_multiplier(volatility)
                self.logger.debug(f"🔄 {symbol} volatility trailing stop: {trailing_pct:.2f}% (vol: {volatility:.2f}%)")
                return trailing_pct
            
        except Exception as e:
            self.logger.error(f"❌ Error getting adaptive trailing stop for {symbol}: {e}")
            return config.TRAILING_STOP_PCT  # Fallback to static value
    
    def _get_stop_multiplier(self, volatility: float) -> float:
        """Calculate stop loss percentage based on volatility"""
        # Adaptive stop loss: 0.4 to 0.6 times daily volatility
        # More volatile stocks get wider stops
        if volatility < 1.0:      # Very stable (SPY, bonds)
            return max(0.08, volatility * 0.5)  # Min 0.08%
        elif volatility < 2.0:    # Stable (AAPL, MSFT)
            return volatility * 0.4
        elif volatility < 3.0:    # Medium (most stocks)
            return volatility * 0.45
        elif volatility < 4.0:    # Volatile (TSLA, AMD)
            return volatility * 0.5
        else:                     # Very volatile (IONQ, biotech)
            return min(0.8, volatility * 0.6)  # Max 0.8%
    
    def _get_profit_multiplier(self, volatility: float) -> float:
        """Calculate profit target percentage based on volatility"""
        # Maintain 2:1 risk/reward ratio minimum
        stop_mult = self._get_stop_multiplier(volatility)
        return max(stop_mult * 2.0, 0.2)  # Min 0.2% profit target
    
    def _get_trailing_multiplier(self, volatility: float) -> float:
        """Calculate trailing stop percentage based on volatility"""
        # Trailing stop: 0.3 to 0.5 times daily volatility
        if volatility < 1.5:
            return max(0.05, volatility * 0.3)  # Min 0.05%
        elif volatility < 3.0:
            return volatility * 0.35
        else:
            return min(0.4, volatility * 0.4)   # Max 0.4%
    
    def _get_timeframe_scale(self, max_hold_time_seconds: int) -> float:
        """Scale profit targets based on maximum hold time"""
        # Shorter timeframes need smaller profit targets
        # Base scaling on max hold time in minutes
        hold_minutes = max_hold_time_seconds / 60
        
        if hold_minutes <= 5:      # 1-5 minute scalping
            return 0.5             # 50% of daily target (quick scalps but maintain 1:1 ratio)
        elif hold_minutes <= 10:   # 5-10 minute holds
            return 0.65            # 65% of daily target
        elif hold_minutes <= 30:   # 10-30 minute holds  
            return 0.85            # 85% of daily target
        else:                      # 30+ minute holds
            return 1.0             # Full daily target
    
    def _get_static_levels(self, entry_price: float, signal_type: str) -> Dict[str, float]:
        """Fallback to static configuration levels"""
        if signal_type == "BUY":
            stop_loss = entry_price * (1 - config.STOP_LOSS_PCT / 100)
            profit_target = entry_price * (1 + config.PROFIT_TARGET_PCT / 100)
        else:  # SELL
            stop_loss = entry_price * (1 + config.STOP_LOSS_PCT / 100)
            profit_target = entry_price * (1 - config.PROFIT_TARGET_PCT / 100)
        
        return {
            'stop_loss': stop_loss,
            'profit_target': profit_target,
            'trailing_stop_pct': config.TRAILING_STOP_PCT,
            'volatility': 2.5,  # Default
            'stop_loss_pct': config.STOP_LOSS_PCT,
            'profit_target_pct': config.PROFIT_TARGET_PCT
        }
    
    def get_comparison_table(self, symbols: list = None) -> str:
        """Generate a comparison table of adaptive vs static levels"""
        if symbols is None:
            symbols = ['AAPL', 'TSLA', 'IONQ', 'SPY', 'AMD']
        
        table = "\n📊 ADAPTIVE vs STATIC COMPARISON\n"
        table += "=" * 80 + "\n"
        table += f"{'Stock':<6} {'Vol%':<6} {'Static':<12} {'Adaptive':<12} {'Difference':<12}\n"
        table += "-" * 80 + "\n"
        
        for symbol in symbols:
            try:
                vol = self.get_stock_volatility(symbol)
                static_stop = config.STOP_LOSS_PCT
                adaptive_stop = self._get_stop_multiplier(vol)
                difference = adaptive_stop - static_stop
                
                table += f"{symbol:<6} {vol:<6.1f} {static_stop:<12.2f} {adaptive_stop:<12.2f} "
                table += f"{difference:+.2f}%\n"
                
            except Exception as e:
                table += f"{symbol:<6} ERROR: {str(e)[:40]}\n"
        
        table += "=" * 80 + "\n"
        return table

# Global instance
dynamic_risk = DynamicRiskCalculator()

def test_adaptive_calculations():
    """Test the adaptive risk calculation system"""
    print("🧪 Testing Adaptive Risk Calculations")
    print("=" * 60)
    
    test_symbols = ['AAPL', 'TSLA', 'IONQ', 'SPY', 'AMD', 'MSFT']
    entry_price = 100.0  # Test price
    
    for symbol in test_symbols:
        try:
            levels = dynamic_risk.calculate_adaptive_levels(symbol, entry_price, "BUY")
            vol = levels['volatility']
            stop_pct = levels['stop_loss_pct']
            target_pct = levels['profit_target_pct']
            trail_pct = levels['trailing_stop_pct']
            
            print(f"\n{symbol}:")
            print(f"  Volatility: {vol:.2f}%")
            print(f"  Stop Loss: {stop_pct:.2f}% (${entry_price - levels['stop_loss']:.2f})")
            print(f"  Profit Target: {target_pct:.2f}% (${levels['profit_target'] - entry_price:.2f})")
            print(f"  Trailing Stop: {trail_pct:.2f}%")
            print(f"  Risk/Reward: 1:{target_pct/stop_pct:.1f}")
            
        except Exception as e:
            print(f"\n{symbol}: ERROR - {e}")
    
    print(f"\n{dynamic_risk.get_comparison_table()}")

if __name__ == "__main__":
    test_adaptive_calculations()
