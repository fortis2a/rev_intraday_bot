#!/usr/bin/env python3
"""
Technical Indicator Overlap Analysis
Identifies duplicated indicators and potential signal conflicts
"""

import sys
sys.path.append(".")

def analyze_indicator_overlap():
    print('🔍 TECHNICAL INDICATOR OVERLAP ANALYSIS')
    print('=' * 70)
    
    # Map all indicators by system
    systems = {
        'Confidence Monitor': {
            'indicators': ['MACD (12/26/9)', 'EMA9', 'EMA21', 'VWAP', 'RSI (14)', 'Bollinger Bands (20/2)', 'Volume Ratio'],
            'purpose': 'Base approval filter (75%+ threshold)',
            'timeframe': '15min real-time data'
        },
        'Mean Reversion Strategy': {
            'indicators': ['RSI (14)', 'Bollinger Bands (20/2)', 'EMA (9/21)', 'MACD (12/26/9)', 'Stochastic', 'Support/Resistance', 'Volume Analysis'],
            'purpose': 'Oversold/overbought bounces',
            'timeframe': '1min strategy data'
        },
        'Momentum Scalp Strategy': {
            'indicators': ['Multi-EMA (8/13/21/50)', 'MACD (12/26/9)', 'ADX', 'Williams %R', 'ROC', 'VWAP', 'Volume Flow', 'MFI'],
            'purpose': 'High-frequency momentum trades', 
            'timeframe': '1min strategy data'
        },
        'VWAP Bounce Strategy': {
            'indicators': ['VWAP (multiple periods)', 'VWAP Bands', 'Volume Profile', 'POC', 'Value Area', 'OBV', 'Volume Oscillator'],
            'purpose': 'Volume-based level bounces',
            'timeframe': '1min strategy data'
        }
    }
    
    # Identify overlapping indicators
    print('\n📊 INDICATOR OVERLAP MATRIX:')
    print('-' * 70)
    
    overlaps = {
        'RSI (14)': ['Confidence Monitor', 'Mean Reversion Strategy'],
        'MACD (12/26/9)': ['Confidence Monitor', 'Mean Reversion Strategy', 'Momentum Scalp Strategy'], 
        'EMA9/21': ['Confidence Monitor', 'Mean Reversion Strategy'],
        'VWAP': ['Confidence Monitor', 'Momentum Scalp Strategy', 'VWAP Bounce Strategy'],
        'Bollinger Bands': ['Confidence Monitor', 'Mean Reversion Strategy'],
        'Volume Analysis': ['Confidence Monitor', 'Mean Reversion Strategy', 'Momentum Scalp Strategy', 'VWAP Bounce Strategy']
    }
    
    for indicator, used_by in overlaps.items():
        print(f'🔄 {indicator:<20} → Used by: {", ".join(used_by)}')
        if len(used_by) > 2:
            print(f'   ⚠️  HIGH OVERLAP - {len(used_by)} systems using same indicator')
    
    # Potential conflicts
    print(f'\n⚠️  POTENTIAL CONFLICT SCENARIOS:')
    print('-' * 70)
    
    conflicts = [
        {
            'scenario': 'RSI Contradiction',
            'description': 'Confidence Monitor RSI says overbought (>70) but Mean Reversion says buy signal',
            'likelihood': 'High - Different timeframes (15min vs 1min)',
            'impact': 'Conflicting buy/sell signals'
        },
        {
            'scenario': 'MACD Divergence', 
            'description': 'Real-time MACD bullish but strategy MACD bearish due to timing differences',
            'likelihood': 'Medium - Same parameters but different data refresh rates',
            'impact': 'Trade approval vs rejection conflict'
        },
        {
            'scenario': 'VWAP Position Conflict',
            'description': 'Confidence Monitor VWAP vs Strategy VWAP calculations differ',
            'likelihood': 'Medium - Different calculation methods and periods',
            'impact': 'Conflicting position assessment'
        },
        {
            'scenario': 'EMA Trend Disagreement',
            'description': 'Different EMA calculations giving opposite trend signals',
            'likelihood': 'Low - Similar parameters',
            'impact': 'Trend direction confusion'
        }
    ]
    
    for conflict in conflicts:
        print(f'🚨 {conflict["scenario"]}')
        print(f'   Description: {conflict["description"]}')
        print(f'   Likelihood: {conflict["likelihood"]}')
        print(f'   Impact: {conflict["impact"]}')
        print()
    
    # Recommendations
    print(f'💡 OPTIMIZATION RECOMMENDATIONS:')
    print('-' * 70)
    
    recommendations = [
        '1. DEDUPLICATE CORE INDICATORS',
        '   • Use ONE RSI calculation (14-period) shared across all systems',
        '   • Use ONE MACD calculation (12/26/9) shared across all systems', 
        '   • Use ONE VWAP calculation with consistent parameters',
        '',
        '2. SPECIALIZE STRATEGIES BY INDICATOR TYPE',
        '   • Confidence Monitor: Keep MACD, EMA9/21, VWAP, RSI, Volume (base approval)',
        '   • Mean Reversion: Focus on Bollinger Bands, Stochastic, Support/Resistance',
        '   • Momentum Scalp: Focus on ADX, Williams %R, ROC, MFI (unique momentum indicators)',
        '   • VWAP Bounce: Focus on Volume Profile, POC, Value Area, OBV (unique volume indicators)',
        '',
        '3. CREATE UNIFIED INDICATOR SERVICE',
        '   • Calculate each indicator ONCE per symbol/timeframe',
        '   • Share results across all strategies',
        '   • Eliminate calculation redundancy and timing conflicts',
        '',
        '4. IMPLEMENT CONFLICT RESOLUTION',
        '   • Priority system: Confidence Monitor > Strategy signals',
        '   • Timeframe hierarchy: Real-time data > Historical data',
        '   • Weighted voting when indicators conflict'
    ]
    
    for rec in recommendations:
        print(rec)
    
    print(f'\n🎯 CONCLUSION:')
    print('YES - Current duplication is problematic and should be optimized')
    print('SOLUTION - Implement unified indicator service with specialized strategy focus')

if __name__ == "__main__":
    analyze_indicator_overlap()
