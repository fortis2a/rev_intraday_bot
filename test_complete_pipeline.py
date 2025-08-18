#!/usr/bin/env python3
"""
Test the complete trading pipeline with actual signals
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from core.data_manager import DataManager
from strategies import MomentumStrategy, MeanReversionStrategy, VWAPStrategy
from stock_specific_config import should_execute_trade

def test_complete_pipeline():
    print("=== COMPLETE TRADING PIPELINE TEST ===")
    
    dm = DataManager()
    strategy_classes = {
        'momentum': MomentumStrategy,
        'mean_reversion': MeanReversionStrategy,
        'vwap': VWAPStrategy
    }
    
    test_symbols = ['SOFI', 'NIO']
    
    for symbol in test_symbols:
        print(f"\n--- Complete Pipeline Test for {symbol} ---")
        
        # Get market data
        df = dm.get_bars(symbol, config['TIMEFRAME'])
        if df.empty or len(df) < 26:
            print(f"❌ {symbol}: Insufficient data")
            continue
        
        df = dm.calculate_indicators(df)
        current_price = df.iloc[-1]['close']
        
        print(f"Data: {len(df)} bars, Price: ${current_price:.2f}")
        
        # Check price limits
        if current_price < config['MIN_PRICE'] or current_price > config['MAX_PRICE']:
            print(f"❌ {symbol}: Price outside limits")
            continue
        
        # Generate signals
        signals_found = []
        for strategy_name, strategy_class in strategy_classes.items():
            try:
                strategy = strategy_class(symbol)
                signal = strategy.generate_signal(symbol, df)
                if signal:
                    signals_found.append(signal)
                    print(f"  📊 {strategy_name}: {signal['action']} - {signal['reason']}")
                    
                    # Test confidence for this signal's action
                    decision = should_execute_trade(symbol, signal['action'])
                    print(f"     Confidence: {decision['confidence']:.1f}% (Execute: {decision['execute']})")
                    
                    if decision['execute']:
                        print(f"     ✅ {signal['action']} TRADE APPROVED for {symbol}")
                    else:
                        print(f"     ❌ {signal['action']} trade blocked by confidence")
            except Exception as e:
                print(f"  ❌ {strategy_name}: Error - {e}")
        
        print(f"\nResult for {symbol}: {len(signals_found)} signals generated")

if __name__ == "__main__":
    test_complete_pipeline()
