#!/usr/bin/env python3
"""
Enhanced Dynamic Risk Calculator with Real Historical Movement Analysis
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import config
from utils.logger import setup_logger

class HistoricalMovementAnalyzer:
    """Analyze actual historical price movements for each timeframe"""
    
    def __init__(self):
        self.logger = setup_logger("historical_analyzer", config.LOG_LEVEL)
        self.movement_cache = {}
        self.last_update = {}
        
    def calculate_real_movements(self, symbol: str, timeframe: str = "1Min", 
                                days_back: int = 7, data_manager=None) -> dict:
        """Calculate actual price movements from historical data"""
        try:
            # Check cache (update daily)
            cache_key = f"{symbol}_{timeframe}_{days_back}d"
            now = datetime.now()
            
            if (cache_key in self.movement_cache and 
                cache_key in self.last_update and 
                (now - self.last_update[cache_key]).total_seconds() < 86400):  # 24 hours
                return self.movement_cache[cache_key]
            
            if data_manager is None:
                from core.data_manager import DataManager
                data_manager = DataManager()
            
            # Get historical data
            # For 5-minute movements, we need enough bars to analyze
            bars_needed = self._calculate_bars_needed(timeframe, days_back)
            bars = data_manager.get_market_data(symbol, timeframe, bars_needed)
            
            if bars is None or len(bars) < 20:
                self.logger.warning(f"⚠️ Insufficient data for {symbol} {timeframe}")
                return self._get_fallback_movements(symbol, timeframe)
            
            # Calculate actual movements
            movements = self._analyze_price_movements(bars, timeframe)
            
            # Cache the results
            self.movement_cache[cache_key] = movements
            self.last_update[cache_key] = now
            
            self.logger.info(f"📊 {symbol} {timeframe} movements: "
                           f"Avg={movements['avg_move_pct']:.3f}%, "
                           f"P75={movements['p75_move_pct']:.3f}%, "
                           f"P90={movements['p90_move_pct']:.3f}%")
            
            return movements
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating movements for {symbol}: {e}")
            return self._get_fallback_movements(symbol, timeframe)
    
    def _calculate_bars_needed(self, timeframe: str, days_back: int) -> int:
        """Calculate how many bars we need for the analysis"""
        if timeframe == "1Min":
            return days_back * 390  # ~390 trading minutes per day
        elif timeframe == "2Min":
            return days_back * 195
        elif timeframe == "5Min":
            return days_back * 78
        else:
            return days_back * 20  # Default for longer timeframes
    
    def _analyze_price_movements(self, bars: pd.DataFrame, timeframe: str) -> dict:
        """Analyze actual price movements from the data"""
        try:
            # Calculate price changes for each bar
            bars = bars.copy()
            bars['price_change'] = bars['close'].pct_change() * 100  # Percentage change
            bars['abs_change'] = abs(bars['price_change'])
            
            # Remove first row (NaN) and outliers (>10% moves are likely data errors)
            valid_moves = bars['abs_change'].dropna()
            valid_moves = valid_moves[valid_moves <= 10.0]  # Remove extreme outliers
            
            if len(valid_moves) < 10:
                raise ValueError("Insufficient valid movement data")
            
            # Calculate movement statistics
            movements = {
                'timeframe': timeframe,
                'total_bars': len(valid_moves),
                'avg_move_pct': valid_moves.mean(),
                'median_move_pct': valid_moves.median(),
                'std_move_pct': valid_moves.std(),
                'p25_move_pct': valid_moves.quantile(0.25),
                'p50_move_pct': valid_moves.quantile(0.50),
                'p75_move_pct': valid_moves.quantile(0.75),
                'p90_move_pct': valid_moves.quantile(0.90),
                'p95_move_pct': valid_moves.quantile(0.95),
                'max_move_pct': valid_moves.max(),
            }
            
            # Calculate suggested stop loss and profit targets
            movements.update(self._calculate_suggested_levels(movements))
            
            return movements
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing movements: {e}")
            raise
    
    def _calculate_suggested_levels(self, movements: dict) -> dict:
        """Calculate suggested stop loss and profit targets from movement data"""
        # Use percentile-based approach
        # Stop loss: Should catch ~75-80% of normal moves (avoid false exits)
        suggested_stop_pct = movements['p75_move_pct'] * 1.2  # 20% buffer above 75th percentile
        
        # Profit target: Aim for moves that happen ~25-30% of the time
        suggested_profit_pct = movements['p75_move_pct'] * 1.5  # Target larger moves
        
        # Ensure minimum risk/reward ratio of 1:1.5
        if suggested_profit_pct < suggested_stop_pct * 1.5:
            suggested_profit_pct = suggested_stop_pct * 1.5
        
        return {
            'suggested_stop_pct': min(suggested_stop_pct, 2.0),    # Cap at 2%
            'suggested_profit_pct': min(suggested_profit_pct, 3.0), # Cap at 3%
            'risk_reward_ratio': suggested_profit_pct / suggested_stop_pct if suggested_stop_pct > 0 else 1.5
        }
    
    def _get_fallback_movements(self, symbol: str, timeframe: str) -> dict:
        """Fallback to estimated movements if no data available"""
        # Import the old dynamic risk for fallback
        from utils.dynamic_risk import dynamic_risk
        
        # Get estimated daily volatility
        daily_vol = dynamic_risk._get_default_volatility(symbol)
        
        # Scale down for timeframe (very rough estimate)
        if timeframe == "1Min":
            timeframe_vol = daily_vol * 0.05  # ~5% of daily move per minute
        elif timeframe == "2Min":
            timeframe_vol = daily_vol * 0.08  # ~8% of daily move per 2min
        elif timeframe == "5Min":
            timeframe_vol = daily_vol * 0.15  # ~15% of daily move per 5min
        else:
            timeframe_vol = daily_vol * 0.3
        
        return {
            'timeframe': timeframe,
            'total_bars': 0,
            'avg_move_pct': timeframe_vol * 0.5,
            'median_move_pct': timeframe_vol * 0.4,
            'std_move_pct': timeframe_vol * 0.3,
            'p75_move_pct': timeframe_vol * 0.7,
            'p90_move_pct': timeframe_vol * 1.0,
            'suggested_stop_pct': timeframe_vol * 0.8,
            'suggested_profit_pct': timeframe_vol * 1.2,
            'risk_reward_ratio': 1.5,
            'is_fallback': True
        }

# Global instance
historical_analyzer = HistoricalMovementAnalyzer()

def test_historical_analysis():
    """Test the historical movement analysis"""
    symbols = ['IONQ', 'AAPL', 'TSLA', 'SPY']
    timeframe = '1Min'
    
    print(f"📊 Historical Movement Analysis ({timeframe} timeframe)")
    print("=" * 70)
    
    for symbol in symbols:
        print(f"\n🔍 {symbol}:")
        movements = historical_analyzer.calculate_real_movements(symbol, timeframe, days_back=7)
        
        if movements.get('is_fallback'):
            print("   (Using fallback estimates - no real data)")
        else:
            print(f"   Analyzed {movements['total_bars']} bars")
        
        print(f"   Average Move:    {movements['avg_move_pct']:.3f}%")
        print(f"   75th Percentile: {movements['p75_move_pct']:.3f}%")
        print(f"   90th Percentile: {movements['p90_move_pct']:.3f}%")
        print(f"   Suggested Stop:  {movements['suggested_stop_pct']:.3f}%")
        print(f"   Suggested Profit:{movements['suggested_profit_pct']:.3f}%")
        print(f"   Risk/Reward:     1:{movements['risk_reward_ratio']:.1f}")

if __name__ == "__main__":
    test_historical_analysis()
