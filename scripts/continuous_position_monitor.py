#!/usr/bin/env python3
"""
Continuous Position Monitor
Monitors all positions and adjusts protection in real-time
"""

import os
import sys
import time
import logging
from datetime import datetime
import alpaca_trade_api as tradeapi
from stock_specific_config import get_stock_thresholds

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import config

class ContinuousPositionMonitor:
    def __init__(self):
        self.api = tradeapi.REST(
            config['ALPACA_API_KEY'],
            config['ALPACA_SECRET_KEY'],
            config['ALPACA_BASE_URL'],
            api_version='v2'
        )
        self.logger = self._setup_logger()
        self.position_highs = {}  # Track highest profits for trailing
        self.position_lows = {}   # Track lowest prices for short trailing
        
    def _setup_logger(self):
        logger = logging.getLogger('position_monitor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
            # File handler
            log_file = f"logs/position_monitor_{datetime.now().strftime('%Y%m%d')}.log"
            os.makedirs('logs', exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(console_formatter)
            logger.addHandler(file_handler)
            
        return logger

    def get_positions_with_details(self):
        """Get all positions with current market data"""
        try:
            positions = self.api.list_positions()
            position_details = []
            
            for pos in positions:
                current_price = float(pos.market_value) / float(pos.qty)
                entry_price = float(pos.avg_entry_price)
                qty = float(pos.qty)
                side = 'long' if qty > 0 else 'short'
                
                if side == 'long':
                    profit_pct = (current_price - entry_price) / entry_price * 100
                else:
                    profit_pct = (entry_price - current_price) / entry_price * 100
                
                position_details.append({
                    'symbol': pos.symbol,
                    'side': side,
                    'qty': abs(qty),
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'profit_pct': profit_pct,
                    'unrealized_pl': float(pos.unrealized_pl),
                    'market_value': float(pos.market_value)
                })
            
            return position_details
            
        except Exception as e:
            self.logger.error(f"Error fetching positions: {e}")
            return []

    def update_trailing_stops(self, position):
        """Update trailing stops based on current profit levels"""
        symbol = position['symbol']
        side = position['side']
        current_profit = position['profit_pct']
        current_price = position['current_price']
        
        # Initialize tracking if first time seeing this position
        if symbol not in self.position_highs:
            self.position_highs[symbol] = current_profit
            self.position_lows[symbol] = current_price
            return False
        
        # Check if we should update trailing stops
        updated = False
        
        if side == 'long':
            # For long positions, track highest profit
            if current_profit > self.position_highs[symbol]:
                self.position_highs[symbol] = current_profit
                updated = True
                
                # Update trailing stop to lock in 75% of highest profit
                new_stop_price = position['entry_price'] * (1 + (current_profit * 0.75 / 100))
                
                try:
                    # Cancel existing trailing stops
                    orders = self.api.list_orders(status='open', symbols=symbol)
                    for order in orders:
                        if order.order_type == 'trailing_stop':
                            self.api.cancel_order(order.id)
                    
                    # Create new trailing stop
                    trail_amount = current_price * 0.01  # 1% trail
                    self.api.submit_order(
                        symbol=symbol,
                        qty=position['qty'],
                        side='sell',
                        type='trailing_stop',
                        trail_price=round(trail_amount, 2),
                        time_in_force='gtc'
                    )
                    
                    self.logger.info(f"[{symbol}] LONG: Updated trailing stop - New high profit: {current_profit:.2f}%")
                    
                except Exception as e:
                    self.logger.error(f"[{symbol}] Failed to update trailing stop: {e}")
                    
        else:  # short position
            # For short positions, track highest profit (price going down)
            if current_profit > self.position_highs[symbol]:
                self.position_highs[symbol] = current_profit
                # Track lowest price reached
                if current_price < self.position_lows[symbol]:
                    self.position_lows[symbol] = current_price
                updated = True
                
                try:
                    # Cancel existing trailing stops
                    orders = self.api.list_orders(status='open', symbols=symbol)
                    for order in orders:
                        if order.order_type == 'trailing_stop':
                            self.api.cancel_order(order.id)
                    
                    # Create new trailing stop (buy to cover)
                    trail_amount = current_price * 0.01  # 1% trail
                    self.api.submit_order(
                        symbol=symbol,
                        qty=position['qty'],
                        side='buy',
                        type='trailing_stop',
                        trail_price=round(trail_amount, 2),
                        time_in_force='gtc'
                    )
                    
                    self.logger.info(f"[{symbol}] SHORT: Updated trailing stop - New high profit: {current_profit:.2f}%")
                    
                except Exception as e:
                    self.logger.error(f"[{symbol}] Failed to update trailing stop: {e}")
        
        return updated

    def check_take_profit_targets(self, position):
        """Check if positions should be closed at take profit targets"""
        symbol = position['symbol']
        side = position['side']
        current_profit = position['profit_pct']
        
        # Get stock-specific take profit target
        thresholds = get_stock_thresholds(symbol)
        take_profit_target = thresholds['take_profit_pct'] * 100  # Convert to percentage
        
        if current_profit >= take_profit_target:
            try:
                # Close the position
                if side == 'long':
                    order = self.api.submit_order(
                        symbol=symbol,
                        qty=position['qty'],
                        side='sell',
                        type='market',
                        time_in_force='gtc'
                    )
                else:
                    order = self.api.submit_order(
                        symbol=symbol,
                        qty=position['qty'],
                        side='buy',
                        type='market',
                        time_in_force='gtc'
                    )
                
                self.logger.info(f"[{symbol}] 🎯 TAKE PROFIT EXECUTED at {current_profit:.2f}% "
                               f"(Target: {take_profit_target:.2f}%) - Order: {order.id}")
                
                # Remove from tracking
                if symbol in self.position_highs:
                    del self.position_highs[symbol]
                if symbol in self.position_lows:
                    del self.position_lows[symbol]
                
                return True
                
            except Exception as e:
                self.logger.error(f"[{symbol}] Failed to execute take profit: {e}")
        
        return False

    def monitor_positions(self):
        """Main monitoring loop"""
        self.logger.info("🔍 Starting Continuous Position Monitoring")
        self.logger.info("Monitoring profitable positions with dynamic trailing stops...")
        
        while True:
            try:
                positions = self.get_positions_with_details()
                
                if not positions:
                    self.logger.info("No positions to monitor")
                    time.sleep(30)
                    continue
                
                current_time = datetime.now().strftime("%H:%M:%S")
                
                for position in positions:
                    symbol = position['symbol']
                    side = position['side'].upper()
                    profit = position['profit_pct']
                    unrealized = position['unrealized_pl']
                    
                    # Only monitor profitable positions
                    if profit > 0:
                        # Check for take profit
                        if self.check_take_profit_targets(position):
                            continue  # Position was closed
                        
                        # Update trailing stops
                        self.update_trailing_stops(position)
                        
                        # Log current status
                        if symbol in self.position_highs:
                            max_profit = self.position_highs[symbol]
                            self.logger.info(f"[{current_time}] {symbol} ({side}): "
                                           f"Current: {profit:+.2f}% | Max: {max_profit:+.2f}% | "
                                           f"P&L: ${unrealized:+.2f}")
                    else:
                        # Log losing positions for awareness
                        self.logger.warning(f"[{current_time}] {symbol} ({side}): "
                                          f"LOSS: {profit:.2f}% | P&L: ${unrealized:.2f}")
                
                # Wait before next check
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    monitor = ContinuousPositionMonitor()
    monitor.monitor_positions()
