#!/usr/bin/env python3
"""
Order Manager for Intraday Trading Bot
Handles trade execution and order management
ASCII-only, no Unicode characters
"""

import alpaca_trade_api as tradeapi
from datetime import datetime
from config import config
from logger import setup_logger, clean_message

class OrderManager:
    """Manages trade execution and orders"""
    
    def __init__(self, data_manager):
        self.logger = setup_logger('order_manager')
        self.data_manager = data_manager
        self.api = data_manager.api
        self.logger.info("Order Manager initialized")
    
    def calculate_position_size(self, price, account_equity):
        """Calculate appropriate position size"""
        try:
            # Use maximum position size or 10% of equity, whichever is smaller
            max_dollar_amount = min(
                config['MAX_POSITION_SIZE'],
                account_equity * 0.10
            )
            
            # Calculate shares
            shares = int(max_dollar_amount / price)
            
            # Ensure minimum viable position
            if shares < 1:
                shares = 1
            
            return shares
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to calculate position size: {e}")
            return 1
    
    def place_buy_order(self, symbol, signal_data):
        """Place a buy order"""
        try:
            # Get current price and account info
            current_price = self.data_manager.get_current_price(symbol)
            account_info = self.data_manager.get_account_info()
            
            if not current_price or not account_info:
                self.logger.error(f"[ERROR] Could not get price or account info for {symbol}")
                return None
            
            # Calculate position size
            shares = self.calculate_position_size(current_price, account_info['equity'])
            
            # Check buying power
            required_cash = shares * current_price
            if required_cash > account_info['buying_power']:
                self.logger.warning(f"[WARNING] Insufficient buying power for {symbol}")
                return None
            
            # Calculate stop loss and take profit
            stop_loss_price = current_price * (1 - config['STOP_LOSS_PCT'])
            take_profit_price = current_price * (1 + config['TAKE_PROFIT_PCT'])
            
            self.logger.info(f"[ORDER] Placing BUY order for {symbol}")
            self.logger.info(f"[ORDER] Shares: {shares}, Price: ${current_price:.2f}")
            self.logger.info(f"[ORDER] Stop Loss: ${stop_loss_price:.2f}")
            self.logger.info(f"[ORDER] Take Profit: ${take_profit_price:.2f}")
            
            # Place market buy order
            order = self.api.submit_order(
                symbol=symbol,
                qty=shares,
                side='buy',
                type='market',
                time_in_force='day'
            )
            
            self.logger.info(f"[SUCCESS] Buy order placed - Order ID: {order.id}")
            
            # Place stop loss order
            try:
                stop_order = self.api.submit_order(
                    symbol=symbol,
                    qty=shares,
                    side='sell',
                    type='stop',
                    stop_price=stop_loss_price,
                    time_in_force='day'
                )
                self.logger.info(f"[SUCCESS] Stop loss order placed - Order ID: {stop_order.id}")
            except Exception as e:
                self.logger.error(f"[ERROR] Failed to place stop loss: {e}")
            
            return {
                'order_id': order.id,
                'symbol': symbol,
                'side': 'buy',
                'qty': shares,
                'price': current_price,
                'stop_loss': stop_loss_price,
                'take_profit': take_profit_price,
                'signal': signal_data
            }
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to place buy order for {symbol}: {e}")
            return None
    
    def place_sell_order(self, symbol, qty=None):
        """Place a sell order"""
        try:
            # Get current position if qty not specified
            if qty is None:
                positions = self.data_manager.get_positions()
                position = next((p for p in positions if p['symbol'] == symbol), None)
                
                if not position:
                    self.logger.warning(f"[WARNING] No position found for {symbol}")
                    return None
                
                qty = abs(int(position['qty']))
            
            # Get current price
            current_price = self.data_manager.get_current_price(symbol)
            if not current_price:
                self.logger.error(f"[ERROR] Could not get current price for {symbol}")
                return None
            
            self.logger.info(f"[ORDER] Placing SELL order for {symbol}")
            self.logger.info(f"[ORDER] Shares: {qty}, Price: ${current_price:.2f}")
            
            # Place market sell order
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side='sell',
                type='market',
                time_in_force='day'
            )
            
            self.logger.info(f"[SUCCESS] Sell order placed - Order ID: {order.id}")
            
            return {
                'order_id': order.id,
                'symbol': symbol,
                'side': 'sell',
                'qty': qty,
                'price': current_price
            }
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to place sell order for {symbol}: {e}")
            return None
    
    def cancel_all_orders(self, symbol=None):
        """Cancel all open orders"""
        try:
            orders = self.api.list_orders(status='open')
            
            cancelled_count = 0
            for order in orders:
                if symbol is None or order.symbol == symbol:
                    self.api.cancel_order(order.id)
                    cancelled_count += 1
                    self.logger.info(f"[CANCELLED] Order {order.id} for {order.symbol}")
            
            self.logger.info(f"[INFO] Cancelled {cancelled_count} orders")
            return cancelled_count
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to cancel orders: {e}")
            return 0
    
    def get_open_orders(self):
        """Get all open orders"""
        try:
            orders = self.api.list_orders(status='open')
            return [{
                'id': order.id,
                'symbol': order.symbol,
                'qty': int(order.qty),
                'side': order.side,
                'type': order.order_type,
                'status': order.status
            } for order in orders]
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to get open orders: {e}")
            return []
