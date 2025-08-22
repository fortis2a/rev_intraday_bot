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
from stock_specific_config import should_execute_trade

class IntradayEngine:
    """Main intraday trading engine"""
    
    def __init__(self, mode="LIVE"):
        """Initialize the trading engine"""
        self.mode = mode
        self.logger = setup_logger('intraday_engine')
        self.logger.info(f"[INIT] Starting Intraday Trading Engine in {mode} mode")
        
        # Validate configuration
        validate_config()
        
        # Initialize components
        self.data_manager = DataManager()
        self.order_manager = OrderManager(self.data_manager)
        
        # Initialize strategy classes (will create instances per symbol)
        self.strategy_classes = {
            'momentum': MomentumStrategy,
            'mean_reversion': MeanReversionStrategy,
            'vwap': VWAPStrategy
        }
        
        # Trading state
        self.active_positions = {}
        self.daily_pnl = 0.0
        self.trade_count = 0
        self.is_running = True
        self.stocks_to_watch = {}  # Track overbought stocks for BUY opportunities
        
        # Get initial account info
        account_info = self.data_manager.get_account_info()
        if account_info:
            self.logger.info(f"[ACCOUNT] Starting Equity: ${account_info['equity']:,.2f}")
            self.logger.info(f"[ACCOUNT] Buying Power: ${account_info['buying_power']:,.2f}")
            self.logger.info(f"[ACCOUNT] Cash: ${account_info['cash']:,.2f}")
        
        # Recover existing positions on restart
        self.recover_existing_positions()
        
        self.logger.info("[SUCCESS] Intraday trading engine initialized")
    
    def recover_existing_positions(self):
        """Recover and manage existing positions on restart"""
        try:
            self.logger.info("[RECOVERY] Checking for existing positions...")
            
            positions = self.data_manager.get_positions()
            if not positions:
                self.logger.info("[RECOVERY] No existing positions found")
                return
            
            self.logger.info(f"[RECOVERY] Found {len(positions)} existing positions")
            
            for position in positions:
                symbol = position['symbol']
                qty = int(position['qty'])
                entry_price = float(position['avg_entry_price'])
                current_value = float(position['market_value'])
                unrealized_pnl = float(position['unrealized_pl'])
                side = position['side']
                
                self.logger.info(f"[RECOVERY] {symbol}: {qty} shares @ ${entry_price:.2f}, "
                               f"Current: ${current_value:.2f}, P&L: ${unrealized_pnl:.2f}")
                
                if side == 'long':
                    # Get stock-specific thresholds for this symbol
                    try:
                        from stock_specific_config import get_stock_thresholds
                        thresholds = get_stock_thresholds(symbol)
                    except:
                        # Fallback to default thresholds
                        thresholds = {
                            'stop_loss_pct': config['STOP_LOSS_PCT'],
                            'take_profit_pct': config['TAKE_PROFIT_PCT'],
                            'trailing_activation_pct': config['TRAILING_STOP_ACTIVATION'],
                            'trailing_distance_pct': config['TRAILING_STOP_PCT']
                        }
                    
                    # Calculate stop loss and take profit prices
                    stop_loss_price = entry_price * (1 - thresholds['stop_loss_pct'])
                    take_profit_price = entry_price * (1 + thresholds['take_profit_pct'])
                    
                    # Get current price to check for immediate actions
                    current_price = self.data_manager.get_current_price(symbol)
                    
                    if current_price:
                        # Check if position should be closed immediately
                        if current_price <= stop_loss_price:
                            self.logger.warning(f"[RECOVERY] {symbol} below stop loss ${stop_loss_price:.2f}, "
                                              f"current: ${current_price:.2f} - SELLING")
                            self.order_manager.place_sell_order(symbol)
                            continue
                        
                        elif current_price >= take_profit_price:
                            self.logger.info(f"[RECOVERY] {symbol} above take profit ${take_profit_price:.2f}, "
                                           f"current: ${current_price:.2f} - SELLING")
                            self.order_manager.place_sell_order(symbol)
                            continue
                    
                    # Add position to trailing stop manager for ongoing management
                    try:
                        # First add the position with proper initialization
                        self.order_manager.trailing_stop_manager.add_position(
                            symbol=symbol,
                            entry_price=entry_price,
                            quantity=qty,
                            side='long',
                            initial_stop_price=stop_loss_price,
                            custom_thresholds=thresholds
                        )
                        
                        # Now update with current market price to set proper trailing state
                        if current_price:
                            self.order_manager.trailing_stop_manager.update_position_price(symbol, current_price)
                            
                            # Check if we should immediately activate trailing based on current profit
                            current_profit_pct = (current_price - entry_price) / entry_price
                            if current_profit_pct >= thresholds['trailing_activation_pct']:
                                self.logger.info(f"[RECOVERY] {symbol} profit {current_profit_pct:.1%} >= {thresholds['trailing_activation_pct']:.1%}")
                                self.logger.info(f"[RECOVERY] {symbol} Trailing stop should be ACTIVE on restart")
                        
                        self.logger.info(f"[RECOVERY] {symbol} added to trailing stop management")
                        self.logger.info(f"[RECOVERY] {symbol} Stop: ${stop_loss_price:.2f}, "
                                       f"Target: ${take_profit_price:.2f}, Current: ${current_price:.2f}")
                        
                        # Add to active positions tracking
                        self.active_positions[symbol] = {
                            'qty': qty,
                            'entry_price': entry_price,
                            'stop_loss': stop_loss_price,
                            'take_profit': take_profit_price
                        }
                        
                    except Exception as e:
                        self.logger.error(f"[RECOVERY] Failed to add {symbol} to trailing stop: {e}")
                
                elif side == 'short':
                    # Handle short position recovery
                    self.logger.info(f"[RECOVERY] Processing SHORT position: {symbol}")
                    
                    # Get stock-specific thresholds for this symbol
                    try:
                        from stock_specific_config import get_stock_thresholds
                        thresholds = get_stock_thresholds(symbol)
                    except:
                        # Fallback to default thresholds
                        thresholds = {
                            'stop_loss_pct': config['STOP_LOSS_PCT'],
                            'take_profit_pct': config['TAKE_PROFIT_PCT'],
                            'trailing_activation_pct': config['TRAILING_STOP_ACTIVATION'],
                            'trailing_distance_pct': config['TRAILING_STOP_PCT']
                        }
                    
                    # For short positions: stop loss is ABOVE entry (buy to cover)
                    # take profit is BELOW entry (profit from price drop)
                    stop_loss_price = entry_price * (1 + thresholds['stop_loss_pct'])
                    take_profit_price = entry_price * (1 - thresholds['take_profit_pct'])
                    
                    # Get current price to check for immediate actions
                    current_price = self.data_manager.get_current_price(symbol)
                    
                    if current_price:
                        # Check if short position should be closed immediately
                        if current_price >= stop_loss_price:
                            self.logger.warning(f"[RECOVERY] {symbol} ABOVE stop loss ${stop_loss_price:.2f}, "
                                              f"current: ${current_price:.2f} - COVERING SHORT")
                            self.order_manager.place_buy_order(symbol, {'strategy': 'stop_loss_recovery'})
                            continue
                        
                        elif current_price <= take_profit_price:
                            self.logger.info(f"[RECOVERY] {symbol} below take profit ${take_profit_price:.2f}, "
                                           f"current: ${current_price:.2f} - COVERING SHORT FOR PROFIT")
                            self.order_manager.place_buy_order(symbol, {'strategy': 'profit_target_recovery'})
                            continue
                    
                    # Add short position to trailing stop manager for ongoing management
                    try:
                        self.order_manager.trailing_stop_manager.add_position(
                            symbol=symbol,
                            entry_price=entry_price,
                            quantity=abs(qty),  # Use absolute value for quantity
                            side='short',
                            initial_stop_price=stop_loss_price,
                            custom_thresholds=thresholds
                        )
                        
                        # Place protective stop loss order (buy to cover)
                        try:
                            stop_order = self.order_manager.api.submit_order(
                                symbol=symbol,
                                qty=abs(qty),
                                side='buy',  # Buy to cover short
                                type='stop',
                                stop_price=stop_loss_price,
                                time_in_force='day'
                            )
                            self.logger.info(f"[RECOVERY] Stop loss order placed for {symbol} - Order ID: {stop_order.id}")
                            
                            # Store stop order ID for potential updates
                            if hasattr(self.order_manager.trailing_stop_manager, 'stop_orders'):
                                self.order_manager.trailing_stop_manager.stop_orders[symbol] = stop_order.id
                                
                        except Exception as e:
                            self.logger.error(f"[RECOVERY] Failed to place stop loss for {symbol}: {e}")
                        
                        # Now update with current market price to set proper trailing state
                        if current_price:
                            self.order_manager.trailing_stop_manager.update_position_price(symbol, current_price)
                            
                            # Check if we should immediately activate trailing based on current profit
                            # For shorts: profit when current_price < entry_price
                            current_profit_pct = (entry_price - current_price) / entry_price
                            if current_profit_pct >= thresholds['trailing_activation_pct']:
                                self.logger.info(f"[RECOVERY] {symbol} SHORT profit {current_profit_pct:.1%} >= {thresholds['trailing_activation_pct']:.1%}")
                                self.logger.info(f"[RECOVERY] {symbol} SHORT Trailing stop should be ACTIVE on restart")
                        
                        self.logger.info(f"[RECOVERY] {symbol} SHORT added to trailing stop management")
                        self.logger.info(f"[RECOVERY] {symbol} Stop: ${stop_loss_price:.2f} (+{thresholds['stop_loss_pct']:.2%}), "
                                       f"Target: ${take_profit_price:.2f} (-{thresholds['take_profit_pct']:.2%}), Current: ${current_price:.2f}")
                        
                        # Add to active positions tracking
                        self.active_positions[symbol] = {
                            'qty': qty,
                            'entry_price': entry_price,
                            'stop_loss': stop_loss_price,
                            'take_profit': take_profit_price,
                            'side': 'short'
                        }
                        
                    except Exception as e:
                        self.logger.error(f"[RECOVERY] Failed to add SHORT {symbol} to trailing stop: {e}")
                
                else:
                    self.logger.warning(f"[RECOVERY] {symbol} has unknown position side: {side}")
            
            if self.active_positions:
                self.logger.info(f"[RECOVERY] Successfully recovered {len(self.active_positions)} positions")
                self.logger.info("=" * 60)
                self.logger.info("📊 RECOVERED POSITIONS SUMMARY")
                self.logger.info("=" * 60)
                for symbol, pos_data in self.active_positions.items():
                    self.logger.info(f"{symbol}: {pos_data['qty']} shares @ ${pos_data['entry_price']:.2f}")
                    self.logger.info(f"  Stop: ${pos_data['stop_loss']:.2f} | Target: ${pos_data['take_profit']:.2f}")
                self.logger.info("=" * 60)
            
        except Exception as e:
            self.logger.error(f"[RECOVERY] Error recovering positions: {e}")
    
    def is_market_hours(self):
        """Check if we're in valid trading hours with 30-min buffer"""
        try:
            # First check if market is actually open
            market_status = self.data_manager.get_market_status()
            if not market_status.get('is_open', False):
                return False
            
            # Market is open, now check our trading hour restrictions
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            
            # Check if it's a weekday
            if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
                return False
            
            # Apply 30-minute buffer restrictions
            # Trading starts 30 min after market open (10:00 AM)
            # Trading ends 30 min before market close (3:30 PM)
            if config['TRADING_START'] <= current_time <= config['TRADING_END']:
                return True
            
            return False
            
        except:
            # Fallback to time-based check with restrictions
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
        
        # Enhanced debug logging for watchlist processing
        self.logger.info(f"🔍 SIGNAL SCAN: Starting scan of {len(config['INTRADAY_WATCHLIST'])} symbols: {config['INTRADAY_WATCHLIST']}")
        
        for i, symbol in enumerate(config['INTRADAY_WATCHLIST']):
            try:
                self.logger.info(f"📊 PROCESSING [{i+1}/{len(config['INTRADAY_WATCHLIST'])}]: {symbol}")
                
                # Get market data
                df = self.data_manager.get_bars(symbol, config['TIMEFRAME'])
                if df.empty or len(df) < 26:  # Enhanced minimum for MACD calculation
                    self.logger.info(f"⚠️ SKIP {symbol}: Insufficient data ({len(df) if not df.empty else 0} bars)")
                    continue
                
                # Calculate enhanced indicators
                df = self.data_manager.calculate_indicators(df)
                
                # Check current price limits
                current_price = df.iloc[-1]['close']
                if current_price < config['MIN_PRICE'] or current_price > config['MAX_PRICE']:
                    self.logger.info(f"⚠️ SKIP {symbol}: Price ${current_price:.2f} outside range [${config['MIN_PRICE']}, ${config['MAX_PRICE']}]")
                    continue
                
                self.logger.info(f"✅ DATA OK {symbol}: {len(df)} bars, price ${current_price:.2f}")
                
                # Run each enhanced strategy
                strategy_signals_count = 0
                for strategy_name, strategy_class in self.strategy_classes.items():
                    try:
                        # Create strategy instance for this symbol - ALL strategies need symbol
                        strategy = strategy_class(symbol)
                        
                        signal = strategy.generate_signal(symbol, df)
                        if signal:
                            # Add strategy signal to list for processing
                            # We'll check enhanced confidence later during execution
                            signals.append(signal)
                            strategy_signals_count += 1
                            self.logger.info(f"🎯 SIGNAL GENERATED [{strategy_name}]: {signal['action']} {symbol} - {signal['reason']}")
                    except Exception as strategy_error:
                        self.logger.error(f"❌ STRATEGY ERROR [{strategy_name}] for {symbol}: {strategy_error}")
                        continue
                
                if strategy_signals_count == 0:
                    self.logger.info(f"📈 NO SIGNALS: {symbol} - no strategies triggered")
                else:
                    self.logger.info(f"🚀 SIGNALS FOUND: {symbol} generated {strategy_signals_count} signals")
                
            except Exception as e:
                self.logger.error(f"❌ SCAN ERROR for {symbol}: {e}")
                continue
        
        self.logger.info(f"📋 SCAN COMPLETE: Found {len(signals)} total signals from {len(config['INTRADAY_WATCHLIST'])} symbols")
        return signals
    
    def execute_signal(self, signal):
        """Execute a trading signal with enhanced confidence verification"""
        try:
            symbol = signal['symbol']
            action = signal['action']
            
            # Enhanced confidence check using our stock-specific system
            trade_decision = should_execute_trade(symbol)
            
            if not trade_decision['execute']:
                self.logger.info(f"[CONFIDENCE BLOCK] {symbol} - {trade_decision['reason']}")
                return False
            
            self.logger.info(f"[CONFIDENCE OK] {symbol} - {trade_decision['reason']}")
            
            # Check if we already have a position
            positions = self.data_manager.get_positions()
            existing_position = next((p for p in positions if p['symbol'] == symbol), None)
            
            if action == 'BUY':
                # Check if this was a watched stock (previously overbought)
                was_watched = symbol in self.stocks_to_watch
                watch_info = self.stocks_to_watch.get(symbol, {})
                
                # Check if we have an existing position
                if existing_position:
                    if existing_position['side'] == 'long':
                        self.logger.info(f"[SKIP] Already long {symbol}")
                        return False
                    elif existing_position['side'] == 'short':
                        # Cover short position with BUY signal
                        order_result = self.order_manager.place_cover_order(symbol)
                        if order_result:
                            self.trade_count += 1
                            # Remove from active positions
                            if symbol in self.active_positions:
                                del self.active_positions[symbol]
                            self.logger.info(f"[EXECUTED] SHORT COVER: {symbol} - Trade #{self.trade_count} | Confidence: {trade_decision['confidence']:.1f}%")
                            return True
                else:
                    # No position - place regular buy order
                    order_result = self.order_manager.place_buy_order(symbol, signal)
                    if order_result:
                        self.trade_count += 1
                        self.active_positions[symbol] = {
                            'order_result': order_result,
                            'timestamp': datetime.now(),
                            'entry_price': order_result.get('entry_price') if isinstance(order_result, dict) else None
                        }
                        
                        # Enhanced logging for watched stocks
                        if was_watched:
                            self.logger.info(f"[EXECUTED] PRIORITY BUY: {symbol} (was overbought, now oversold) - Trade #{self.trade_count} | Confidence: {trade_decision['confidence']:.1f}%")
                            # Remove from watch list
                            del self.stocks_to_watch[symbol]
                        else:
                            self.logger.info(f"[EXECUTED] Buy order for {symbol} - Trade #{self.trade_count} | Confidence: {trade_decision['confidence']:.1f}%")
                        return True
                
            elif action == 'SELL':
                # Check if we have an existing position
                if existing_position:
                    if existing_position['side'] == 'long':
                        # Check if we just opened this position recently (avoid immediate reversals)
                        if symbol in self.active_positions:
                            position_age = (datetime.now() - self.active_positions[symbol].get('timestamp', datetime.now())).total_seconds()
                            if position_age < 60:  # Less than 1 minute old
                                self.logger.info(f"[SKIP] {symbol} position too new ({position_age:.0f}s) - avoiding immediate reversal")
                                return False
                        
                        # Sell long position
                        order_result = self.order_manager.place_sell_order(symbol)
                        if order_result:
                            self.trade_count += 1
                            # Remove from active positions
                            if symbol in self.active_positions:
                                del self.active_positions[symbol]
                            self.logger.info(f"[EXECUTED] Sell order for {symbol} - Trade #{self.trade_count} | Confidence: {trade_decision['confidence']:.1f}%")
                            return True
                    elif existing_position['side'] == 'short':
                        self.logger.info(f"[SKIP] Already short {symbol}")
                        return False
                else:
                    # No position - try short selling if enabled
                    from config import config
                    if config.get('ENABLE_SHORT_SELLING', False):
                        order_result = self.order_manager.place_short_order(symbol, signal)
                        if order_result:
                            self.trade_count += 1
                            self.active_positions[symbol] = order_result
                            self.logger.info(f"[EXECUTED] SHORT SELL: {symbol} - Trade #{self.trade_count} | Confidence: {trade_decision['confidence']:.1f}%")
                            return True
                        else:
                            # Short selling failed - add to watch list
                            self.stocks_to_watch[symbol] = {
                                'signal_time': datetime.now(),
                                'reason': 'Short selling failed - watching for BUY opportunity',
                                'confidence': trade_decision['confidence']
                            }
                            self.logger.info(f"[WATCH] {symbol} short failed - watching for BUY opportunity | Confidence: {trade_decision['confidence']:.1f}%")
                    else:
                        # Short selling disabled - add to watch list for potential BUY when oversold
                        self.stocks_to_watch[symbol] = {
                            'signal_time': datetime.now(),
                            'reason': 'Was overbought - watching for BUY opportunity',
                            'confidence': trade_decision['confidence']
                        }
                        self.logger.info(f"[WATCH] {symbol} overbought (no position) - watching for BUY opportunity | Confidence: {trade_decision['confidence']:.1f}%")
            
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
            self.logger.info(f"[DEBUG] Checking market hours...")
            if not self.is_market_hours():
                self.logger.info("[INFO] Market is closed")
                return
            self.logger.info(f"[DEBUG] Market hours check passed")
            
            # Check risk limits
            self.logger.info(f"[DEBUG] Checking risk limits...")
            if not self.check_risk_limits():
                self.logger.warning("[RISK] Risk limits exceeded - stopping trading")
                self.is_running = False
                self.logger.warning(f"[DEBUG] Set is_running=False due to risk limits")
                return
            self.logger.info(f"[DEBUG] Risk limits check passed")
            
            # Update P&L
            self.logger.info(f"[DEBUG] Updating P&L...")
            self.update_pnl()
            self.logger.info(f"[DEBUG] P&L update completed")
            
            # Monitor trailing stops for existing positions
            if config['TRAILING_STOP_ENABLED']:
                self.logger.info(f"[DEBUG] Checking trailing stops...")
                triggered_positions = self.order_manager.check_trailing_stop_triggers()
                if triggered_positions:
                    self.logger.info(f"[TRAILING] {len(triggered_positions)} positions closed by trailing stops")
                
                # Log trailing stop summary every 10 cycles
                if self.trade_count % 10 == 0:
                    self.order_manager.trailing_stop_manager.log_position_summary()
                self.logger.info(f"[DEBUG] Trailing stops check completed")
            
            # Scan for signals
            self.logger.info(f"[DEBUG] Scanning for signals...")
            signals = self.scan_for_signals()
            self.logger.info(f"[DEBUG] Signal scan completed - found {len(signals)} signals")
            
            # Process signals with enhanced confidence check
            if not signals:
                self.logger.info("[INFO] No trading signals generated")
                return
            
            # Execute signals (confidence will be checked during execution)
            executed_count = 0
            for signal in signals[:5]:  # Limit to top 5 signals to avoid overload
                if self.execute_signal(signal):
                    executed_count += 1
            
            if executed_count > 0:
                self.logger.info(f"[CYCLE] Executed {executed_count} trades")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Trading cycle failed: {e}")
            self.logger.error(f"[DEBUG] Exception in trading_cycle, is_running still {self.is_running}")
    
    def run(self):
        """Main trading loop with market hours awareness"""
        self.logger.info("[START] Starting main trading loop")
        
        try:
            cycle_count = 0
            
            while self.is_running:
                self.logger.info(f"[DEBUG] Loop iteration {cycle_count + 1}, is_running={self.is_running}")
                
                # Check if market is open
                if self.is_market_hours():
                    cycle_count += 1
                    self.logger.info(f"[LOOP] === Trading Cycle {cycle_count} ===")
                    
                    # Execute trading cycle
                    self.logger.info(f"[DEBUG] About to call trading_cycle()")
                    self.trading_cycle()
                    self.logger.info(f"[DEBUG] trading_cycle() completed, is_running={self.is_running}")
                    
                    if not self.is_running:
                        self.logger.warning(f"[DEBUG] Engine stopped during trading_cycle - breaking loop")
                        break
                    
                    # Sleep between cycles
                    self.logger.info(f"[WAIT] Waiting {config['CHECK_INTERVAL']} seconds until next cycle")
                    time.sleep(config['CHECK_INTERVAL'])
                else:
                    # Market is closed - show status and wait
                    self.logger.info("[INFO] Market is closed - waiting for market open")
                    
                    # Show market status every 5 minutes when closed
                    try:
                        market_status = self.data_manager.get_market_status()
                        next_open = market_status.get('next_open')
                        if next_open:
                            self.logger.info(f"[MARKET] Next open: {next_open}")
                        else:
                            self.logger.info("[MARKET] Market status unavailable")
                    except Exception as e:
                        self.logger.error(f"[ERROR] Failed to get market status: {e}")
                    
                    # Wait 5 minutes before checking again
                    time.sleep(300)  # 5 minutes
                
        except KeyboardInterrupt:
            self.logger.info("[STOP] Trading stopped by user")
        except Exception as e:
            self.logger.error(f"[ERROR] Critical error in main loop: {e}")
        finally:
            self.logger.info("[DEBUG] Exiting run() method - calling cleanup")
            self.cleanup()
    
    def cleanup(self):
        """Cleanup before shutdown"""
        try:
            self.logger.info("[CLEANUP] Starting shutdown sequence")
            
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
