#!/usr/bin/env python3
"""
🎯 Dynamic Signal Helper
Helper functions for creating adaptive trading signals
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import config
from utils.dynamic_risk import dynamic_risk

def round_price_to_tick(price: float, tick_size: float = 0.01) -> float:
    """Round price to valid tick increment"""
    return round(price / tick_size) * tick_size

def calculate_adaptive_signal_levels(symbol: str, entry_price: float, signal_type: str, 
                                   data_manager=None, timeframe: str = None) -> dict:
    """Calculate adaptive stop loss and profit target for a signal"""
    try:
        # Use dynamic risk calculator with timeframe awareness
        levels = dynamic_risk.calculate_adaptive_levels(
            symbol=symbol,
            entry_price=entry_price,
            signal_type=signal_type,
            data_manager=data_manager,
            timeframe=timeframe
        )
        
        # Round to valid tick sizes
        stop_loss = round_price_to_tick(levels['stop_loss'])
        profit_target = round_price_to_tick(levels['profit_target'])
        
        return {
            'stop_loss': stop_loss,
            'profit_target': profit_target,
            'trailing_stop_pct': levels['trailing_stop_pct'],
            'volatility': levels['volatility'],
            'stop_loss_pct': levels['stop_loss_pct'],
            'profit_target_pct': levels['profit_target_pct']
        }
        
    except Exception as e:
        # Fallback to static configuration
        if signal_type == "BUY":
            stop_loss = round_price_to_tick(entry_price * (1 - config.STOP_LOSS_PCT / 100))
            profit_target = round_price_to_tick(entry_price * (1 + config.PROFIT_TARGET_PCT / 100))
        else:  # SELL
            stop_loss = round_price_to_tick(entry_price * (1 + config.STOP_LOSS_PCT / 100))
            profit_target = round_price_to_tick(entry_price * (1 - config.PROFIT_TARGET_PCT / 100))
        
        return {
            'stop_loss': stop_loss,
            'profit_target': profit_target,
            'trailing_stop_pct': config.TRAILING_STOP_PCT,
            'volatility': 2.5,  # Default
            'stop_loss_pct': config.STOP_LOSS_PCT,
            'profit_target_pct': config.PROFIT_TARGET_PCT
        }
