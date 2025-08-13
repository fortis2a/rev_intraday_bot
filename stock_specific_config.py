#!/usr/bin/env python3
"""
Stock-Specific Configuration Module
Implements dynamic thresholds based on historical analysis
"""

# Stock-specific thresholds based on 60-day 15M historical analysis
STOCK_SPECIFIC_THRESHOLDS = {
    'IONQ': {
        'stop_loss_pct': 0.005,  # 0.5%
        'take_profit_pct': 0.010,  # 1.0%
        'trailing_activation_pct': 0.006,  # 0.6%
        'trailing_distance_pct': 0.010,  # 1.0%
        'confidence_multiplier': 0.890,
        'volatility': 0.90,
        'avg_range': 1.17,
        'profile': 'moderate_volatility'
    },
    'RGTI': {
        'stop_loss_pct': 0.0051,  # 0.51%
        'take_profit_pct': 0.010,  # 1.0%
        'trailing_activation_pct': 0.006,  # 0.6%
        'trailing_distance_pct': 0.010,  # 1.0%
        'confidence_multiplier': 0.907,
        'volatility': 1.07,
        'avg_range': 1.27,
        'profile': 'moderate_volatility'
    },
    'QBTS': {
        'stop_loss_pct': 0.0154,  # 1.54%
        'take_profit_pct': 0.0133,  # 1.33%
        'trailing_activation_pct': 0.008,  # 0.8%
        'trailing_distance_pct': 0.0251,  # 2.51%
        'confidence_multiplier': 1.042,
        'volatility': 2.42,
        'avg_range': 3.59,
        'profile': 'high_volatility'
    },
    'JNJ': {
        'stop_loss_pct': 0.005,  # 0.5%
        'take_profit_pct': 0.010,  # 1.0%
        'trailing_activation_pct': 0.006,  # 0.6%
        'trailing_distance_pct': 0.010,  # 1.0%
        'confidence_multiplier': 0.822,
        'volatility': 0.22,
        'avg_range': 0.25,
        'profile': 'low_volatility'
    },
    'PG': {
        'stop_loss_pct': 0.005,  # 0.5%
        'take_profit_pct': 0.010,  # 1.0%
        'trailing_activation_pct': 0.006,  # 0.6%
        'trailing_distance_pct': 0.010,  # 1.0%
        'confidence_multiplier': 0.819,
        'volatility': 0.19,
        'avg_range': 0.24,
        'profile': 'low_volatility'
    }
}

# Volatility profiles for risk management
VOLATILITY_PROFILES = {
    'low_volatility': {
        'max_position_multiplier': 1.5,  # Allow larger positions
        'confidence_boost': 0.05,  # +5% confidence for stable stocks
        'description': 'Blue chip stocks with low volatility'
    },
    'moderate_volatility': {
        'max_position_multiplier': 1.0,  # Standard position size
        'confidence_boost': 0.0,  # No adjustment
        'description': 'Balanced risk/reward stocks'
    },
    'high_volatility': {
        'max_position_multiplier': 0.7,  # Reduce position size
        'confidence_boost': -0.05,  # -5% confidence for volatile stocks
        'description': 'High volatility stocks requiring careful management'
    }
}

def get_stock_thresholds(symbol: str) -> dict:
    """Get stock-specific thresholds or defaults"""
    if symbol in STOCK_SPECIFIC_THRESHOLDS:
        return STOCK_SPECIFIC_THRESHOLDS[symbol]
    
    # Return conservative defaults for unknown stocks
    return {
        'stop_loss_pct': 0.015,  # 1.5% conservative default
        'take_profit_pct': 0.020,  # 2.0% conservative default
        'trailing_activation_pct': 0.010,  # 1.0%
        'trailing_distance_pct': 0.015,  # 1.5%
        'confidence_multiplier': 1.0,
        'volatility': 1.0,
        'avg_range': 1.0,
        'profile': 'moderate_volatility'
    }

def get_position_size_multiplier(symbol: str) -> float:
    """Get position size multiplier based on volatility profile"""
    thresholds = get_stock_thresholds(symbol)
    profile = thresholds.get('profile', 'moderate_volatility')
    return VOLATILITY_PROFILES[profile]['max_position_multiplier']

def get_confidence_adjustment(symbol: str) -> float:
    """Get confidence adjustment based on stock characteristics"""
    thresholds = get_stock_thresholds(symbol)
    profile = thresholds.get('profile', 'moderate_volatility')
    
    # Combine profile adjustment with stock-specific multiplier
    profile_adjustment = VOLATILITY_PROFILES[profile]['confidence_boost']
    stock_multiplier = thresholds.get('confidence_multiplier', 1.0)
    
    return profile_adjustment + (stock_multiplier - 1.0)

def print_stock_analysis_summary():
    """Print a summary of all stock configurations"""
    print("=" * 80)
    print("📊 STOCK-SPECIFIC CONFIGURATION SUMMARY")
    print("=" * 80)
    
    print(f"{'Stock':<6} {'Stop':<6} {'Profit':<7} {'Trail':<6} {'Volatility':<10} {'Profile':<15}")
    print("-" * 80)
    
    for symbol, config in STOCK_SPECIFIC_THRESHOLDS.items():
        print(f"{symbol:<6} {config['stop_loss_pct']*100:<6.1f} "
              f"{config['take_profit_pct']*100:<7.1f} "
              f"{config['trailing_distance_pct']*100:<6.1f} "
              f"{config['volatility']:<10.2f} {config['profile']:<15}")
    
    print("\n🎯 Key Insights:")
    print(f"• Low Volatility (JNJ, PG): Tight spreads, larger position sizes allowed")
    print(f"• Moderate Volatility (IONQ, RGTI): Balanced approach")
    print(f"• High Volatility (QBTS): Wider spreads, smaller position sizes")
    
if __name__ == "__main__":
    print_stock_analysis_summary()
