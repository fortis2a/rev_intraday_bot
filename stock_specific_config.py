#!/usr/bin/env python3
"""
Stock-Specific Configuration Module
Implements dynamic thresholds based on historical analysis
"""

from config import config  # Import config for threshold values

# Stock-specific thresholds based on 60-day 15M historical analysis
STOCK_SPECIFIC_THRESHOLDS = {
    # Budget-friendly watchlist - Primary trading stocks (2025-08-13 analysis)
    'SOXL': {
        'stop_loss_pct': 0.0048,  # 0.48%
        'take_profit_pct': 0.0086,  # 0.86%
        'trailing_activation_pct': 0.006,  # 0.6%
        'trailing_distance_pct': 0.0072,  # 0.72%
        'confidence_multiplier': 1.077,  # 87.7/100 * 1.23 adjustment
        'volatility': 0.90,
        'avg_range': 5.78,
        'profile': 'moderate_volatility_leveraged'
    },
    'SOFI': {
        'stop_loss_pct': 0.0036,  # 0.36%
        'take_profit_pct': 0.0064,  # 0.64%
        'trailing_activation_pct': 0.005,  # 0.5%
        'trailing_distance_pct': 0.0053,  # 0.53%
        'confidence_multiplier': 1.046,  # 84.6/100 * 1.24 adjustment
        'volatility': 0.65,
        'avg_range': 4.43,
        'profile': 'moderate_volatility_fintech'
    },
    'TQQQ': {
        'stop_loss_pct': 0.0030,  # 0.30%
        'take_profit_pct': 0.0054,  # 0.54%
        'trailing_activation_pct': 0.004,  # 0.4%
        'trailing_distance_pct': 0.0045,  # 0.45%
        'confidence_multiplier': 1.012,  # 81.2/100 * 1.25 adjustment
        'volatility': 0.46,
        'avg_range': 3.12,
        'profile': 'low_volatility_leveraged'
    },
    'INTC': {
        'stop_loss_pct': 0.0030,  # 0.30%
        'take_profit_pct': 0.0054,  # 0.54%
        'trailing_activation_pct': 0.004,  # 0.4%
        'trailing_distance_pct': 0.0045,  # 0.45%
        'confidence_multiplier': 0.998,  # 79.8/100 * 1.25 adjustment
        'volatility': 0.45,
        'avg_range': 3.40,
        'profile': 'low_volatility_tech'
    },
    'NIO': {
        'stop_loss_pct': 0.0030,  # 0.30% (conservative for $4.62 stock)
        'take_profit_pct': 0.0054,  # 0.54%
        'trailing_activation_pct': 0.004,  # 0.4%
        'trailing_distance_pct': 0.0045,  # 0.45%
        'confidence_multiplier': 0.996,  # 79.6/100 * 1.25 adjustment
        'volatility': 0.58,
        'avg_range': 4.14,
        'profile': 'moderate_volatility_ev'
    },
    
    # Original watchlist - Alternative/backup stocks
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
    },
    # New profiles for budget-friendly stocks
    'low_volatility_leveraged': {
        'max_position_multiplier': 1.2,  # Slightly larger positions for TQQQ
        'confidence_boost': 0.03,  # +3% confidence for stable leveraged ETF
        'description': 'Low volatility leveraged ETF with good liquidity'
    },
    'moderate_volatility_leveraged': {
        'max_position_multiplier': 0.9,  # Slightly smaller for SOXL risk
        'confidence_boost': 0.02,  # +2% confidence for high-performance ETF
        'description': 'Moderate volatility leveraged ETF requiring attention'
    },
    'moderate_volatility_fintech': {
        'max_position_multiplier': 1.1,  # Slightly larger for SOFI
        'confidence_boost': 0.02,  # +2% confidence for strong fundamentals
        'description': 'Growing fintech with good trading characteristics'
    },
    'low_volatility_tech': {
        'max_position_multiplier': 1.3,  # Larger positions for INTC
        'confidence_boost': 0.03,  # +3% confidence for established tech
        'description': 'Established tech stock with consistent patterns'
    },
    'moderate_volatility_ev': {
        'max_position_multiplier': 0.8,  # Smaller positions for NIO (low price)
        'confidence_boost': 0.0,  # No adjustment for EV volatility
        'description': 'Electric vehicle stock with moderate volatility'
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

def calculate_final_confidence(symbol: str, base_confidence: float = 85.0) -> float:
    """
    Calculate final confidence level for a stock
    Includes all adjustments: score, profile, consistency, volume
    """
    if symbol not in STOCK_SPECIFIC_THRESHOLDS:
        return base_confidence
    
    thresholds = get_stock_thresholds(symbol)
    
    # Get stock-specific data based on analysis
    stock_data = {
        'SOXL': {'score': 87.7, 'consistency': 7.7, 'volume_score': 30},
        'SOFI': {'score': 84.6, 'consistency': 9.6, 'volume_score': 30},
        'TQQQ': {'score': 81.2, 'consistency': 11.2, 'volume_score': 30},
        'INTC': {'score': 79.8, 'consistency': 9.8, 'volume_score': 30},
        'NIO': {'score': 79.6, 'consistency': 6.7, 'volume_score': 30},
        # Original stocks
        'IONQ': {'score': 75.0, 'consistency': 8.0, 'volume_score': 25},
        'RGTI': {'score': 76.0, 'consistency': 8.5, 'volume_score': 25},
        'QBTS': {'score': 65.0, 'consistency': 6.0, 'volume_score': 20},
        'JNJ': {'score': 70.0, 'consistency': 15.0, 'volume_score': 20},
        'PG': {'score': 69.0, 'consistency': 16.0, 'volume_score': 18}
    }
    
    if symbol not in stock_data:
        return base_confidence
    
    data = stock_data[symbol]
    
    # Apply score-based adjustment
    score_adjustment = (data['score'] / 100) * base_confidence - base_confidence
    
    # Apply profile boost
    profile = thresholds.get('profile', 'moderate_volatility')
    profile_boost = VOLATILITY_PROFILES[profile]['confidence_boost'] * 100
    
    # Apply consistency bonus (higher consistency = more confidence)
    consistency_bonus = (data['consistency'] / 20) * 5  # Max 5% bonus
    
    # Apply volume bonus
    volume_bonus = (data['volume_score'] / 30) * 3  # Max 3% bonus
    
    # Calculate final confidence
    final_confidence = (
        base_confidence + 
        score_adjustment + 
        profile_boost + 
        consistency_bonus + 
        volume_bonus
    )
    
    return round(final_confidence, 1)

def meets_confidence_threshold(symbol: str, min_threshold: float = 75.0) -> bool:
    """
    Check if stock meets minimum confidence threshold for trading
    Returns True if stock should be traded, False to skip
    """
    final_confidence = calculate_final_confidence(symbol)
    meets_threshold = final_confidence >= min_threshold
    
    if not meets_threshold:
        print(f"[CONFIDENCE FILTER] {symbol}: {final_confidence:.1f}% < {min_threshold}% - SKIPPING TRADE")
    else:
        print(f"[CONFIDENCE FILTER] {symbol}: {final_confidence:.1f}% >= {min_threshold}% - TRADE ALLOWED")
    
    return meets_threshold

def get_filtered_watchlist(watchlist: list, min_confidence: float = 75.0, use_real_time: bool = True) -> list:
    """
    Filter watchlist to only include stocks meeting confidence threshold
    STRICT POLICY: If real-time calculation fails, stock is excluded from trading
    """
    filtered_list = []
    
    print(f"\n🎯 FILTERING WATCHLIST (Min Confidence: {min_confidence}%)")
    print(f"📊 Mode: {'Real-time calculation (STRICT - no fallback)' if use_real_time else 'Historical baseline'}")
    print("=" * 60)
    
    if use_real_time:
        # Import real-time calculator
        try:
            from core.real_time_confidence import RealTimeConfidenceCalculator
            calculator = RealTimeConfidenceCalculator()
            
            for symbol in watchlist:
                # Get expected volatility from historical data
                thresholds = get_stock_thresholds(symbol)
                expected_vol = thresholds.get('volatility', 1.0)
                
                try:
                    # Calculate real-time confidence
                    result = calculator.calculate_real_time_confidence(symbol, expected_vol)
                    
                    if result['confidence'] >= min_confidence:
                        filtered_list.append(symbol)
                        print(f"[REAL-TIME] {symbol}: {result['confidence']:.1f}% >= {min_confidence}% - TRADE ALLOWED")
                    else:
                        print(f"[REAL-TIME] {symbol}: {result['confidence']:.1f}% < {min_confidence}% - SKIPPING TRADE")
                        
                except Exception as e:
                    print(f"[ERROR] {symbol}: Real-time calculation failed ({e}) - EXCLUDED FROM TRADING")
                    # Do not add to filtered list - strict no-fallback policy
                    
        except ImportError as e:
            print(f"[ERROR] Real-time calculator unavailable: {e}")
            print("[STRICT POLICY] No fallback allowed - NO TRADING when real-time fails")
            return []  # Return empty list - no trading without real-time data
    
    else:
        # Use historical confidence levels (for testing/analysis only)
        print("[WARNING] Using historical confidence - NOT recommended for live trading")
        for symbol in watchlist:
            if meets_confidence_threshold(symbol, min_confidence):
                filtered_list.append(symbol)
    
    print(f"\n📊 RESULTS: {len(filtered_list)}/{len(watchlist)} stocks passed confidence filter")
    print(f"✅ Trading: {', '.join(filtered_list) if filtered_list else 'NONE - Real-time required'}")
    
    if len(filtered_list) != len(watchlist):
        skipped = [s for s in watchlist if s not in filtered_list]
        print(f"⚠️  Excluded: {', '.join(skipped)}")
    
    return filtered_list

def get_real_time_confidence_for_trade(symbol: str) -> dict:
    """
    Get real-time confidence data for a specific trade decision
    Returns detailed breakdown for logging and decision making
    NO FALLBACK - if real-time fails, trading is disabled for safety
    """
    try:
        from core.real_time_confidence import RealTimeConfidenceCalculator
        calculator = RealTimeConfidenceCalculator()
        
        # Get expected volatility from historical data
        thresholds = get_stock_thresholds(symbol)
        expected_vol = thresholds.get('volatility', 1.0)
        
        # Calculate real-time confidence
        result = calculator.calculate_real_time_confidence(symbol, expected_vol)
        
        return result
        
    except ImportError as e:
        print(f"[ERROR] Real-time confidence calculator not available for {symbol}: {e}")
        return {
            'symbol': symbol,
            'confidence': 0,  # Force no trading
            'tradeable': False,
            'timestamp': 'Real-time calculation failed',
            'mode': 'error',
            'error': str(e)
        }
    except Exception as e:
        print(f"[ERROR] Real-time confidence calculation failed for {symbol}: {e}")
        return {
            'symbol': symbol,
            'confidence': 0,  # Force no trading
            'tradeable': False,
            'timestamp': 'Real-time calculation failed',
            'mode': 'error',
            'error': str(e)
        }

def should_execute_trade(symbol: str, signal_type: str = 'entry') -> dict:
    """
    Final trade execution decision based on real-time confidence
    STRICT POLICY: No fallback - if real-time fails, no trading
    Called immediately before placing orders
    """
    print(f"\n🎯 FINAL TRADE DECISION CHECK: {symbol} ({signal_type})")
    
    # Get real-time confidence
    confidence_data = get_real_time_confidence_for_trade(symbol)
    
    # Check for errors in real-time calculation
    if confidence_data.get('mode') == 'error':
        print(f"❌ TRADING BLOCKED: {symbol} - Real-time calculation failed")
        print(f"   Error: {confidence_data.get('error', 'Unknown error')}")
        return {
            'symbol': symbol,
            'execute': False,
            'confidence': 0,
            'reason': f"Real-time calculation failed: {confidence_data.get('error', 'Unknown error')}",
            'thresholds': None,
            'timestamp': confidence_data.get('timestamp', 'Unknown'),
            'error': True
        }
    
    # Get stock-specific thresholds
    thresholds = get_stock_thresholds(symbol)
    
    # Get minimum confidence threshold from config
    min_confidence = config.get('MIN_CONFIDENCE_THRESHOLD', 0.75) * 100  # Convert to percentage
    
    # Decision logic - trade only if confidence meets minimum threshold
    meets_threshold = confidence_data['confidence'] >= min_confidence
    execute_trade = confidence_data['tradeable'] and meets_threshold
    
    decision = {
        'symbol': symbol,
        'execute': execute_trade,
        'confidence': confidence_data['confidence'],
        'reason': f"Real-time confidence: {confidence_data['confidence']:.1f}%",
        'thresholds': thresholds if execute_trade else None,
        'timestamp': confidence_data.get('timestamp', 'Unknown'),
        'technical_summary': confidence_data.get('technical_summary', {}),
        'error': False
    }
    
    if execute_trade:
        print(f"✅ EXECUTE TRADE: {symbol} - Real-time confidence: {confidence_data['confidence']:.1f}%")
    else:
        if confidence_data['confidence'] > 0:
            print(f"❌ SKIP TRADE: {symbol} - Real-time confidence: {confidence_data['confidence']:.1f}% below {min_confidence:.0f}% threshold")
        else:
            print(f"❌ SKIP TRADE: {symbol} - Real-time calculation failed or returned 0% confidence")
    
    return decision
    
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
