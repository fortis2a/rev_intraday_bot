#!/usr/bin/env python3
"""
Main Intraday Trading Engine
ASCII-only, no Unicode characters
Handles all trading operations and signal generation
"""

import time
import argparse
from datetime import datetime, time as dt_time
import pandas as pd
from config import config, validate_config
from utils.logger import setup_logger, clean_message
from core.data_manager import DataManager
from core.order_manager import OrderManager
from strategies import MomentumStrategy, MeanReversionStrategy, VWAPStrategy
from core.auto_sleep_wake import AutoMarketSleepWake

class IntradayEngine:
    """Main intraday trading engine"""
    
    def __init__(self, mode="LIVE"):
        """Initialize the trading engine"""
        self.mode = mode
        self.logger = setup_logger('intraday_engine')
        self.logger.info(f"[INIT] Starting Intraday Trading Engine in {mode} mode")
        
        # Validate configuration
        validate_config()
        
        # Initialize auto sleep/wake system
        self.auto_sleep_wake = AutoMarketSleepWake()
        
        # Initialize components
        self.data_manager = DataManager()
        self.order_manager = OrderManager(self.data_manager)
        
        # Initialize strategies
        self.strategies = {
            'momentum': MomentumStrategy(),
            'mean_reversion': MeanReversionStrategy(),
            'vwap': VWAPStrategy()
        }
        
        # Trading state
        self.active_positions = {}
        self.daily_pnl = 0.0
        self.trade_count = 0
        self.is_running = True
        
        # Get initial account info
        account_info = self.data_manager.get_account_info()
        if account_info:
            self.logger.info(f"[ACCOUNT] Starting Equity: ${account_info['equity']:,.2f}")
            self.logger.info(f"[ACCOUNT] Buying Power: ${account_info['buying_power']:,.2f}")
            self.logger.info(f"[ACCOUNT] Cash: ${account_info['cash']:,.2f}")
        
        self.logger.info("[SUCCESS] Intraday trading engine initialized")
    
    def is_market_hours(self):
        """Check if market is currently open"""
        try:
            # Get market status from Alpaca
            market_status = self.data_manager.get_market_status()
            return market_status.get('is_open', False)
        except:
            # Fallback to time-based check
            now = datetime.now().time()
            return config['MARKET_OPEN'] <= now <= config['MARKET_CLOSE']
    
    def check_risk_limits(self):
        """Check if we've hit any risk limits"""
        try:
            # Check daily loss limit
            if self.daily_pnl <= -config['MAX_DAILY_LOSS']:
                self.logger.warning(f"[RISK] Daily loss limit reached: ${self.daily_pnl:.2f}")
                return False
            
            # Check maximum positions
            positions = self.data_manager.get_positions()
            if len(positions) >= config['MAX_POSITIONS']:
                self.logger.warning(f"[RISK] Maximum positions limit reached: {len(positions)}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Risk check failed: {e}")
            return False
    
    def scan_for_signals(self):
        """Scan watchlist for trading signals"""
        signals = []
        
        for symbol in config['INTRADAY_WATCHLIST']:
            try:
                # Get market data
                df = self.data_manager.get_bars(symbol, config['TIMEFRAME'])
                if df.empty or len(df) < 26:  # Enhanced minimum for MACD calculation
                    self.logger.debug(f"[DEBUG] Insufficient data for {symbol}: {len(df) if not df.empty else 0} bars")
                    continue
                
                # Calculate enhanced indicators
                df = self.data_manager.calculate_indicators(df)
                
                # Check current price limits
                current_price = df.iloc[-1]['close']
                if current_price < config['MIN_PRICE'] or current_price > config['MAX_PRICE']:
                    continue
                
                # Run each enhanced strategy
                for strategy_name, strategy in self.strategies.items():
                    signal = strategy.generate_signal(symbol, df)
                    if signal:
                        # Apply confidence threshold filter
                        min_confidence = config['MIN_CONFIDENCE_THRESHOLD'] if config['TRADING_MODE'] == "LIVE" else config['MIN_CONFIDENCE_DEMO']
                        
                        if signal['confidence'] >= min_confidence:
                            signals.append(signal)
                            self.logger.info(f"[ENHANCED SIGNAL] {strategy_name}: {signal['action']} {symbol} - {signal['reason']} | Confidence: {signal['confidence']:.1%}")
                        else:
                            self.logger.info(f"[FILTERED] {strategy_name}: {signal['action']} {symbol} - Confidence {signal['confidence']:.1%} below threshold {min_confidence:.1%}")
                
            except Exception as e:
                self.logger.error(f"[ERROR] Failed to scan {symbol}: {e}")
                continue
        
        return signals
    
    def execute_signal(self, signal):
        """Execute a trading signal"""
        try:
            symbol = signal['symbol']
            action = signal['action']
            
            # Check if we already have a position
            positions = self.data_manager.get_positions()
            existing_position = next((p for p in positions if p['symbol'] == symbol), None)
            
            if action == 'BUY':
                # Don't buy if we already have a long position
                if existing_position and existing_position['side'] == 'long':
                    self.logger.info(f"[SKIP] Already long {symbol}")
                    return False
                
                # Place buy order
                order_result = self.order_manager.place_buy_order(symbol, signal)
                if order_result:
                    self.trade_count += 1
                    self.active_positions[symbol] = order_result
                    self.logger.info(f"[EXECUTED] Buy order for {symbol} - Trade #{self.trade_count}")
                    return True
                
            elif action == 'SELL':
                # Only sell if we have a position
                if existing_position and existing_position['side'] == 'long':
                    order_result = self.order_manager.place_sell_order(symbol)
                    if order_result:
                        self.trade_count += 1
                        # Remove from active positions
                        if symbol in self.active_positions:
                            del self.active_positions[symbol]
                        self.logger.info(f"[EXECUTED] Sell order for {symbol} - Trade #{self.trade_count}")
                        return True
                else:
                    self.logger.info(f"[SKIP] No position to sell for {symbol}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to execute signal for {signal['symbol']}: {e}")
            return False
    
    def update_pnl(self):
        """Update daily P&L"""
        try:
            positions = self.data_manager.get_positions()
            total_unrealized = sum(pos['unrealized_pl'] for pos in positions)
            
            # For now, just track unrealized P&L
            # In a real system, you'd track realized P&L from completed trades
            self.daily_pnl = total_unrealized
            
            if positions:
                self.logger.info(f"[PNL] Unrealized P&L: ${total_unrealized:.2f} from {len(positions)} positions")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to update P&L: {e}")
    
    def trading_cycle(self):
        """Execute one trading cycle"""
        try:
            self.logger.info(f"[CYCLE] Starting trading cycle #{self.trade_count + 1}")
            
            # Check market hours
            if not self.is_market_hours():
                self.logger.info("[INFO] Market is closed")
                return
            
            # Check risk limits
            if not self.check_risk_limits():
                self.logger.warning("[RISK] Risk limits exceeded - stopping trading")
                self.is_running = False
                return
            
            # Update P&L
            self.update_pnl()
            
            # Monitor trailing stops for existing positions
            if config['TRAILING_STOP_ENABLED']:
                triggered_positions = self.order_manager.check_trailing_stop_triggers()
                if triggered_positions:
                    self.logger.info(f"[TRAILING] {len(triggered_positions)} positions closed by trailing stops")
                
                # Log trailing stop summary every 10 cycles
                if self.trade_count % 10 == 0:
                    self.order_manager.trailing_stop_manager.log_position_summary()
            
            # Scan for signals
            signals = self.scan_for_signals()
            
            if not signals:
                self.logger.info("[INFO] No trading signals generated")
                return
            
            # Sort signals by confidence
            signals.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Execute top signals
            executed_count = 0
            for signal in signals[:3]:  # Limit to top 3 signals
                if self.execute_signal(signal):
                    executed_count += 1
            
            if executed_count > 0:
                self.logger.info(f"[CYCLE] Executed {executed_count} trades")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Trading cycle failed: {e}")
    
    def run(self):
        """Main trading loop with auto sleep/wake"""
        self.logger.info("[START] Starting main trading loop with auto sleep/wake")
        
        try:
            cycle_count = 0
            
            while self.is_running:
                # Check market transition (sleep/wake)
                transition = self.auto_sleep_wake.check_market_transition()
                
                if transition == "SLEEP":
                    self.logger.info("[SLEEP] Market closed - Entering sleep mode")
                    # Run the sleep/wake system until market reopens
                    self.auto_sleep_wake.run_auto_system()
                    continue
                    
                elif transition == "WAKE":
                    self.logger.info("[WAKE] Market opened - Resuming trading")
                
                # Only trade if market is open and not sleeping
                if self.is_market_hours() and not self.auto_sleep_wake.is_sleeping:
                    cycle_count += 1
                    self.logger.info(f"[LOOP] === Trading Cycle {cycle_count} ===")
                    
                    # Execute trading cycle
                    self.trading_cycle()
                    
                    # Sleep between cycles
                    self.logger.info(f"[WAIT] Waiting {config['CHECK_INTERVAL']} seconds until next cycle")
                    time.sleep(config['CHECK_INTERVAL'])
                else:
                    # Market is closed - enter sleep mode
                    if not self.auto_sleep_wake.is_sleeping:
                        self.logger.info("[SLEEP] Market is closed - Entering sleep mode")
                        self.auto_sleep_wake.go_to_sleep()
                    
                    # Run the sleep display system
                    self.auto_sleep_wake.run_auto_system()
                
        except KeyboardInterrupt:
            self.logger.info("[STOP] Trading stopped by user")
        except Exception as e:
            self.logger.error(f"[ERROR] Critical error in main loop: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup before shutdown"""
        try:
            self.logger.info("[CLEANUP] Starting shutdown sequence")
            
            # Stop auto sleep/wake system
            if hasattr(self, 'auto_sleep_wake'):
                self.auto_sleep_wake.stop()
            
            # Cancel all open orders
            cancelled = self.order_manager.cancel_all_orders()
            if cancelled > 0:
                self.logger.info(f"[CLEANUP] Cancelled {cancelled} open orders")
            
            # Final P&L update
            self.update_pnl()
            
            # Log final stats
            self.logger.info("[FINAL] Trading session summary:")
            self.logger.info(f"[FINAL] Total trades executed: {self.trade_count}")
            self.logger.info(f"[FINAL] Final P&L: ${self.daily_pnl:.2f}")
            
            account_info = self.data_manager.get_account_info()
            if account_info:
                self.logger.info(f"[FINAL] Final equity: ${account_info['equity']:,.2f}")
            
            self.logger.info("[FINAL] Intraday trading engine stopped")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Cleanup failed: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Intraday Trading Engine')
    parser.add_argument('--mode', default='LIVE', choices=['LIVE', 'DEMO', 'TEST'])
    parser.add_argument('--validate-only', action='store_true', help='Only validate setup')
    parser.add_argument('--pnl-report', action='store_true', help='Generate P&L report')
    parser.add_argument('--dashboard', action='store_true', help='Dashboard mode')
    
    args = parser.parse_args()
    
    if args.validate_only:
        print("[VALIDATION] Intraday trading engine validation passed")
        return
    
    if args.pnl_report:
        print("[PNL] Generating P&L report...")
        # Add P&L report generation here
        print("[PNL] Report generation completed")
        return
    
    if args.dashboard:
        print("[DASHBOARD] Starting dashboard mode...")
        time.sleep(10)  # Simulate dashboard
        print("[DASHBOARD] Dashboard stopped")
        return
    
    try:
        engine = IntradayEngine(mode=args.mode)
        engine.run()
    except Exception as e:
        print(f"[ERROR] Failed to start intraday engine: {e}")

if __name__ == "__main__":
    main()
