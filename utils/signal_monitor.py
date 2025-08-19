#!/usr/bin/env python3
"""
Real-Time Signal Monitor
Shows actual signals generated, confidence checks, and execution decisions
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from datetime import datetime
from config import config
from core.data_manager import DataManager
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum_scalp import MomentumScalpStrategy
from strategies.vwap_bounce import VWAPBounceStrategy
from stock_specific_config import should_execute_trade

class SignalMonitor:
    """Real-time signal monitoring and execution tracking"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.signal_history = []
        self.execution_log = []
        
    def scan_for_signals_debug(self):
        """Scan for signals with detailed logging like main.py does"""
        signals = []
        watchlist = config['INTRADAY_WATCHLIST']
        
        print(f"\n🔍 SCANNING {len(watchlist)} STOCKS: {watchlist}")
        print("=" * 80)
        
        strategy_classes = {
            'mean_reversion': MeanReversionStrategy,
            'momentum': MomentumScalpStrategy,
            'vwap': VWAPBounceStrategy
        }
        
        for symbol in watchlist:
            print(f"\n📊 {symbol}")
            print("-" * 40)
            
            try:
                # Get market data exactly like main.py
                df = self.data_manager.get_bars(symbol, config['TIMEFRAME'])
                if df.empty or len(df) < 26:
                    print(f"  ❌ Insufficient data: {len(df) if not df.empty else 0} bars")
                    continue
                
                # Calculate indicators
                df = self.data_manager.calculate_indicators(df)
                
                # Check price limits
                current_price = df.iloc[-1]['close']
                if current_price < config['MIN_PRICE'] or current_price > config['MAX_PRICE']:
                    print(f"  ❌ Price ${current_price:.2f} outside limits (${config['MIN_PRICE']}-${config['MAX_PRICE']})")
                    continue
                
                print(f"  💰 Price: ${current_price:.2f} ✅")
                print(f"  📈 Data: {len(df)} bars ✅")
                
                # Test each strategy
                signals_found = 0
                for strategy_name, strategy_class in strategy_classes.items():
                    try:
                        strategy = strategy_class(symbol)
                        signal = strategy.generate_signal(symbol, df)
                        
                        if signal:
                            signals_found += 1
                            signals.append(signal)
                            
                            print(f"  🚨 {strategy_name.upper()}: {signal['action']} - {signal['reason']}")
                            
                            # Check confidence immediately
                            trade_decision = should_execute_trade(symbol)
                            confidence = trade_decision.get('confidence', 0)
                            should_execute = trade_decision.get('execute', False)
                            
                            print(f"     📊 Confidence: {confidence:.1f}% {'✅ PASS' if should_execute else '❌ FAIL'}")
                            
                            # Check positions
                            positions = self.data_manager.get_positions()
                            existing_position = next((p for p in positions if p['symbol'] == symbol), None)
                            
                            if existing_position:
                                print(f"     📍 Position: {existing_position['side']} {existing_position['qty']} shares")
                            else:
                                print(f"     📍 Position: None")
                            
                            # Simulate execution decision
                            execution_result = self.simulate_execution(signal, trade_decision, existing_position)
                            print(f"     🎯 Decision: {execution_result}")
                            
                        else:
                            print(f"  ⚪ {strategy_name}: No signal")
                            
                    except Exception as e:
                        print(f"  ❌ {strategy_name}: Error - {e}")
                
                if signals_found == 0:
                    print(f"  💤 No signals from any strategy")
                    
            except Exception as e:
                print(f"  ❌ Error scanning {symbol}: {e}")
        
        print(f"\n📋 SCAN COMPLETE: Found {len(signals)} total signals")
        return signals
    
    def simulate_execution(self, signal, trade_decision, existing_position):
        """Simulate what the execution logic would do"""
        symbol = signal['symbol']
        action = signal['action']
        
        if not trade_decision['execute']:
            return f"❌ BLOCKED - {trade_decision['reason']}"
        
        if action == 'BUY':
            if existing_position:
                if existing_position['side'] == 'long':
                    return "⏭️ SKIP - Already long"
                elif existing_position['side'] == 'short':
                    return "⚡ EXECUTE - Cover short position"
            else:
                return "✅ EXECUTE - Buy order"
        
        elif action == 'SELL':
            if existing_position:
                if existing_position['side'] == 'long':
                    return "✅ EXECUTE - Sell long position"
                elif existing_position['side'] == 'short':
                    return "⏭️ SKIP - Already short"
            else:
                # Check short selling
                if config.get('ENABLE_SHORT_SELLING', False):
                    return "🔴 EXECUTE - Short sell"
                else:
                    return "👁️ WATCH - Add to watch list"
        
        return "❓ UNKNOWN"
    
    def monitor_continuously(self, cycles=5):
        """Monitor signals continuously for specified cycles"""
        print("🎯 REAL-TIME SIGNAL MONITOR")
        print("=" * 80)
        print(f"Monitoring for {cycles} cycles (30 seconds each)")
        print(f"Short Selling: {'✅ ENABLED' if config.get('ENABLE_SHORT_SELLING', False) else '❌ DISABLED'}")
        
        for cycle in range(1, cycles + 1):
            print(f"\n{'='*20} CYCLE {cycle}/{cycles} - {datetime.now().strftime('%H:%M:%S')} {'='*20}")
            
            signals = self.scan_for_signals_debug()
            
            if signals:
                print(f"\n🔥 ACTIVE SIGNALS DETECTED!")
                for signal in signals:
                    print(f"   📌 {signal['symbol']}: {signal['action']} - Confidence pending execution")
            else:
                print(f"\n💤 No signals in this cycle")
            
            if cycle < cycles:
                print(f"\n⏰ Waiting 30 seconds for next cycle...")
                time.sleep(30)
        
        print(f"\n🏁 MONITORING COMPLETE")

def main():
    """Run the signal monitor"""
    try:
        monitor = SignalMonitor()
        monitor.monitor_continuously(cycles=3)  # Monitor for 3 cycles
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Monitor error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
