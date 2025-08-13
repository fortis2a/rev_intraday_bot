#!/usr/bin/env python3
"""
🧪 Paper Trading Evaluation Configuration
Disables PDT protection for performance testing while maintaining all analytics
"""

import os
from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path

# Import base config
from config import IntradayTradingConfig

@dataclass 
class PaperTradingEvalConfig(IntradayTradingConfig):
    """Paper trading configuration with PDT protection disabled for evaluation"""
    
    # 🧪 PAPER TRADING EVALUATION SETTINGS
    PAPER_TRADING_MODE: bool = True
    DISABLE_PDT_PROTECTION: bool = True  # 🚨 DISABLE PDT for evaluation
    UNLIMITED_DAY_TRADES: bool = True    # Allow unlimited day trades for testing
    
    # 📊 EVALUATION OVERRIDES
    MAX_DAILY_TRADES: int = 20           # Allow more trades for testing (vs normal 6)
    MAX_OPEN_POSITIONS: int = 5          # More positions for diversified testing
    
    # 🎯 PERFORMANCE TESTING ADJUSTMENTS
    ACCOUNT_RISK_PCT: float = 1.5        # Lower risk per trade for more trades
    MAX_POSITION_VALUE: float = 2000.0   # Smaller positions for more opportunities
    
    # ⚠️ EVALUATION WARNINGS
    SHOW_PDT_WARNINGS: bool = True       # Still show warnings but don't stop trading
    LOG_TRADE_COUNT: bool = True         # Track trades for analysis
    
    # 📈 PERFORMANCE TRACKING (Keep all analytics)
    TRACK_DAY_TRADES: bool = True        # Track for analysis but don't enforce
    TRACK_HOLD_TIMES: bool = True        # Monitor position hold times
    CALCULATE_PDT_IMPACT: bool = True    # Calculate what PDT would have cost
    
    # 🔄 RESET DAILY COUNTERS (for continuous testing)
    RESET_COUNTERS_ON_START: bool = True # Reset trade counters each run
    
    @classmethod
    def create_evaluation_mode(cls):
        """Create paper trading configuration optimized for bot evaluation"""
        config = cls()
        
        # Override safety limits for evaluation
        config.PAPER_TRADING_MODE = True
        config.DISABLE_PDT_PROTECTION = True
        config.UNLIMITED_DAY_TRADES = True
        config.MAX_DAILY_TRADES = 20
        
        return config

# 🧪 EVALUATION MODE INSTANCE
eval_config = PaperTradingEvalConfig.create_evaluation_mode()

def get_evaluation_config():
    """Get the paper trading evaluation configuration"""
    return eval_config

def is_paper_trading_eval() -> bool:
    """Check if running in paper trading evaluation mode"""
    return eval_config.PAPER_TRADING_MODE and eval_config.DISABLE_PDT_PROTECTION

print("📊 Paper Trading Evaluation Config Loaded")
print(f"🧪 PDT Protection: {'❌ DISABLED' if eval_config.DISABLE_PDT_PROTECTION else '✅ ENABLED'}")
print(f"📈 Max Daily Trades: {eval_config.MAX_DAILY_TRADES}")
print(f"🎯 Evaluation Mode: {'✅ ACTIVE' if is_paper_trading_eval() else '❌ INACTIVE'}")
