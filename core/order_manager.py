#!/usr/bin/env python3
"""
📈 Enhanced Order Manager for Intraday Trading Bot
Handles order submission with comprehensive error handling
"""

import sys
import re
import time
from pathlib import Path
from typing import Optional, Dict, Any, Union
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import config
from utils.cache_manager import cache_manager, CacheType
from utils.logger import setup_logger

class OrderManager:
    """Enhanced order management with error handling"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.alpaca_trader = None
        self.api = None
        self.orders = {}  # Track submitted orders
        # Track last error for higher-level diagnostics
        self.last_error = None  # type: Optional[Dict[str, Any]]
        self.last_error_time = None

    def _set_last_error(self, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Record the last error for retrieval by engine diagnostics."""
        from time import time as _now
        self.last_error = {
            'code': code,
            'message': message,
            'details': details or {}
        }
        self.last_error_time = _now()

    def get_last_error(self) -> Optional[Dict[str, Any]]:
        """Return the last submission error details, if any."""
        return self.last_error

    def clear_last_error(self):
        """Clear last error after a successful operation."""
        self.last_error = None
        self.last_error_time = None
        
    def initialize_trading(self):
        """Initialize Alpaca trading connection"""
        try:
            from utils.alpaca_trader import AlpacaTrader
            
            self.alpaca_trader = AlpacaTrader()
            
            # Check if connection was successful
            if self.alpaca_trader.is_connected():
                self.api = self.alpaca_trader.trading_client  # Use trading_client for compatibility
                self.logger.info("🔗 OrderManager initialized with Alpaca connection")
                return True
            else:
                self.logger.error("❌ Failed to connect to Alpaca")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize OrderManager: {e}")
            return False
    
    def round_price_to_tick(self, price, tick_size=0.01):
        """Round price to valid tick size (penny for most stocks)"""
        rounded = round(price / tick_size) * tick_size
        return round(rounded, 2)  # Ensure no floating point precision issues
    
    def submit_order(self, symbol, side, quantity, order_type="market", limit_price=None, stop_price=None, time_in_force="day"):
        """Submit order with enhanced error handling for wash trades and insufficient quantity"""
        try:
            # Auto-initialize trading connection if lost
            if not self.alpaca_trader:
                now = time.time()
                if not hasattr(self, '_last_reinit_attempt') or now - getattr(self, '_last_reinit_attempt', 0) > 10:
                    self._last_reinit_attempt = now
                    self.logger.warning("⚠️ AlpacaTrader missing before submit_order - attempting re-initialization")
                    try:
                        self.initialize_trading()
                    except Exception as reinit_err:
                        self.logger.error(f"❌ Re-initialization failed: {reinit_err}")
                if not self.alpaca_trader:
                    raise Exception("Alpaca trader not initialized")
            # Round prices to avoid sub-penny errors
            if limit_price:
                limit_price = self.round_price_to_tick(limit_price)
            if stop_price:
                stop_price = self.round_price_to_tick(stop_price)
                
            # Proactive wash trade prevention: Check for opposite side orders
            self._check_and_clear_conflicting_orders(symbol, side)
                
            # Clear relevant cache entries before order submission
            cache_manager.on_order_event(symbol, "order_submit")
            
            self.logger.info(f"📝 Submitting {side} order for {quantity} shares of {symbol}")
            
            if not self.alpaca_trader:
                raise Exception("Alpaca trader not initialized")
            
            # Submit the order using AlpacaTrader methods
            if order_type == "market":
                order_id = self.alpaca_trader.submit_market_order(symbol, side, quantity)
            elif order_type == "limit" and limit_price:
                order_id = self.alpaca_trader.submit_limit_order(symbol, side, quantity, limit_price)
            else:
                raise Exception(f"Unsupported order type: {order_type}")
            
            if order_id:
                self.logger.info(f"✅ Order submitted successfully: {order_id}")
                
                # Force cache refresh after successful order
                cache_manager.on_order_event(symbol, "order_event")
                # Clear any previous error
                self.clear_last_error()
                
                # Return a simple object with order ID
                class OrderResult:
                    def __init__(self, order_id):
                        self.id = order_id
                
                return OrderResult(order_id)
            else:
                self._set_last_error('order_submit_failed', 'Order submission failed', {'symbol': symbol, 'side': side, 'quantity': quantity, 'type': order_type})
                raise Exception("Order submission failed")
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"❌ Error submitting Alpaca order: {error_msg}")
            # Record error for diagnostics
            self._set_last_error('api_error', error_msg, {'symbol': symbol, 'side': side, 'quantity': quantity, 'type': order_type})
            
            # Try to parse JSON error if it looks like JSON
            error_data = None
            if error_msg.strip().startswith('{') and error_msg.strip().endswith('}'):
                try:
                    import json
                    error_data = json.loads(error_msg)
                except:
                    pass
            
            # Check for insufficient quantity error (check this first as it's more specific)
            is_insufficient_qty = False
            if error_data:
                # JSON format insufficient quantity check
                is_insufficient_qty = (error_data.get("code") == 40310000 and 
                                     "insufficient qty available" in error_data.get("message", "").lower())
            else:
                # Text format insufficient quantity check
                is_insufficient_qty = ("insufficient qty available" in error_msg.lower() or "40310000" in error_msg)
            
            if is_insufficient_qty:
                self.logger.warning(f"🔍 Insufficient quantity error detected for {symbol}")
                available_qty = self._extract_available_quantity(error_msg, symbol)
                
                # Check if it's a "held_for_orders" situation
                is_held_for_orders = False
                if error_data:
                    held_for_orders = error_data.get("held_for_orders")
                    existing_qty = error_data.get("existing_qty")
                    available = error_data.get("available")
                    
                    if (held_for_orders and existing_qty and available == "0" and 
                        int(held_for_orders) > 0 and int(existing_qty) > 0):
                        is_held_for_orders = True
                        self.logger.warning(f"🔒 Shares held for orders: {held_for_orders}/{existing_qty} for {symbol}")
                
                # If shares are held for pending orders, we need to handle this differently
                if is_held_for_orders:
                    self.logger.warning(f"⚠️ Cannot place order for {symbol} - all shares held for pending orders")
                    # Return None to indicate we should try cancelling orders first
                    return None
                
                # If we found available quantity and it's greater than 0, try partial order
                elif available_qty and available_qty > 0 and available_qty < quantity:
                    self.logger.warning(f"🔄 Retrying with partial quantity: {available_qty} instead of {quantity}")
                    return self._submit_alpaca_order_partial(symbol, side, available_qty, order_type, limit_price, stop_price, time_in_force)
            
            # Check for wash trade error (only if not insufficient quantity)
            else:
                is_wash_trade = False
                if error_data:
                    # JSON format wash trade check
                    is_wash_trade = (error_data.get("code") == 40310000 and 
                                   ("opposite side" in error_data.get("message", "").lower() or
                                    "related_orders" in error_data))
                else:
                    # Text format wash trade check
                    is_wash_trade = ("wash trade detected" in error_msg.lower() or 
                                   ("40310000" in error_msg and "opposite side" in error_msg.lower()))
                
                if is_wash_trade:
                    self.logger.warning(f"⚠️ Wash trade detected for {symbol}")
                    return self._handle_wash_trade_error(error_msg, symbol, side, quantity, order_type, limit_price, stop_price, time_in_force)
            
            return None
    
    def _handle_wash_trade_error(self, error_msg, symbol, side, quantity, order_type, limit_price=None, stop_price=None, time_in_force="day"):
        """Handle wash trade error by canceling ALL conflicting orders and retrying"""
        try:
            self.logger.warning(f"🚨 Wash trade detected for {symbol} - clearing all pending orders")
            
            # First, try to cancel ALL pending orders for this symbol
            cancelled_count = self.cancel_pending_orders_for_symbol(symbol)
            
            if cancelled_count > 0:
                self.logger.info(f"✅ Cancelled {cancelled_count} pending orders for {symbol}")
                
                # Wait longer for all cancellations to process
                time.sleep(2)
                
                # Clear cache to ensure fresh data
                cache_manager.on_order_event(symbol, "order_event")
                
                # Retry the original order
                self.logger.info(f"🔄 Retrying original order after clearing all conflicting orders")
                return self.submit_order(symbol, side, quantity, order_type, limit_price, stop_price, time_in_force)
            else:
                # Fallback: try to extract and cancel specific order ID from error message
                existing_order_id = self._extract_order_id_from_error(error_msg)
                
                if existing_order_id:
                    self.logger.info(f"🔍 Found specific conflicting order ID: {existing_order_id}")
                    
                    # Cancel the specific conflicting order
                    if self._cancel_conflicting_order(existing_order_id):
                        self.logger.info(f"✅ Cancelled specific conflicting order {existing_order_id}")
                        
                        # Wait a moment for cancellation to process
                        time.sleep(1)
                        
                        # Clear cache to ensure fresh data
                        cache_manager.on_order_event(symbol, "order_event")
                        
                        # Retry the original order
                        self.logger.info(f"🔄 Retrying original order after specific order cancellation")
                        return self.submit_order(symbol, side, quantity, order_type, limit_price, stop_price, time_in_force)
                    else:
                        self.logger.error(f"❌ Failed to cancel specific conflicting order {existing_order_id}")
                else:
                    self.logger.warning(f"⚠️ Could not cancel any orders for {symbol} - no pending orders found")
                
        except Exception as e:
            self.logger.error(f"❌ Error handling wash trade: {e}")
            
        return None
    
    def _extract_order_id_from_error(self, error_msg):
        """Extract order ID from wash trade error message"""
        try:
            # Try to parse as JSON first
            if error_msg.strip().startswith('{') and error_msg.strip().endswith('}'):
                try:
                    import json
                    error_data = json.loads(error_msg)
                    
                    # Check for related_orders array
                    if "related_orders" in error_data and error_data["related_orders"]:
                        order_id = error_data["related_orders"][0]
                        self.logger.info(f"🔍 Extracted order ID from JSON: {order_id}")
                        return order_id
                    
                    # Check for existing_order_id
                    if "existing_order_id" in error_data:
                        order_id = error_data["existing_order_id"]
                        self.logger.info(f"🔍 Extracted order ID from JSON: {order_id}")
                        return order_id
                except:
                    pass
            
            # Look for order ID patterns in text format
            # UUID pattern: 8-4-4-4-12 characters (hex)
            uuid_pattern = r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
            
            # Pattern 1: "existing_order_id":"5634e438-1b6e-496e-bd61-951b480d1941"
            order_id_pattern = rf'"existing_order_id"\s*:\s*"({uuid_pattern})"'
            match = re.search(order_id_pattern, error_msg)
            
            if match:
                return match.group(1)
            
            # Pattern 2: existing_order_id: 5634e438-1b6e-496e-bd61-951b480d1941
            alt_pattern = rf'existing_order_id\s*:\s*({uuid_pattern})'
            match = re.search(alt_pattern, error_msg)
            
            if match:
                return match.group(1)
            
            # Pattern 3: "related_orders":["5634e438-1b6e-496e-bd61-951b480d1941"]
            related_pattern = rf'"related_orders"\s*:\s*\[\s*"({uuid_pattern})"'
            match = re.search(related_pattern, error_msg)
            
            if match:
                return match.group(1)
                
        except Exception as e:
            self.logger.error(f"❌ Error extracting order ID: {e}")
            
        return None
    
    def _cancel_conflicting_order(self, order_id):
        """Cancel a conflicting order by ID"""
        try:
            if not self.alpaca_trader:
                self.logger.error("❌ AlpacaTrader not initialized for order cancellation")
                return False
                
            # Cancel the order using AlpacaTrader method
            success = self.alpaca_trader.cancel_order(order_id)
            if success:
                self.logger.info(f"📋 Cancellation request sent for order {order_id}")
                return True
            else:
                self.logger.error(f"❌ Failed to cancel order {order_id}")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Error cancelling order {order_id}: {e}")
            return False
    
    def _extract_available_quantity(self, error_msg, symbol):
        """Extract available quantity from insufficient quantity error"""
        try:
            # Try to parse as JSON first
            if error_msg.strip().startswith('{') and error_msg.strip().endswith('}'):
                try:
                    import json
                    error_data = json.loads(error_msg)
                    if "available" in error_data:
                        available_qty = int(error_data["available"])
                        self.logger.info(f"🔍 Extracted available quantity for {symbol}: {available_qty} (JSON)")
                        return available_qty
                except:
                    pass
            
            # Pattern 1: "requested: 17, available: 13"
            pattern1 = r"available:\s*(\d+)"
            match = re.search(pattern1, error_msg)
            
            if match:
                available_qty = int(match.group(1))
                self.logger.info(f"🔍 Extracted available quantity for {symbol}: {available_qty}")
                return available_qty
            
            # Pattern 2: "available":"3" (JSON format in text)
            pattern2 = r'"available"\s*:\s*"?(\d+)"?'
            match = re.search(pattern2, error_msg)
            
            if match:
                available_qty = int(match.group(1))
                self.logger.info(f"🔍 Extracted available quantity for {symbol}: {available_qty}")
                return available_qty
            
            self.logger.warning(f"⚠️ Could not extract available quantity from: {error_msg}")
            return None
                
        except Exception as e:
            self.logger.error(f"❌ Error extracting available quantity: {e}")
            return None
    
    def _submit_alpaca_order_partial(self, symbol, side, quantity, order_type, limit_price=None, stop_price=None, time_in_force="day"):
        """Submit partial order with available quantity"""
        try:
            # Round prices to avoid sub-penny errors
            if limit_price:
                limit_price = self.round_price_to_tick(limit_price)
            if stop_price:
                stop_price = self.round_price_to_tick(stop_price)
                
            self.logger.info(f"📝 Submitting partial {side} order for {quantity} shares of {symbol}")
            
            if not self.alpaca_trader:
                raise Exception("AlpacaTrader not initialized")
            
            # Submit the order using AlpacaTrader methods
            if order_type == "market":
                order_id = self.alpaca_trader.submit_market_order(symbol, side, quantity)
            elif order_type == "limit" and limit_price:
                order_id = self.alpaca_trader.submit_limit_order(symbol, side, quantity, limit_price)
            else:
                raise Exception(f"Unsupported order type: {order_type}")
            
            if order_id:
                self.logger.info(f"✅ Partial order submitted successfully: {order_id}")
                
                # Force cache refresh after successful order
                cache_manager.on_order_event(symbol, "order_event")
                
                return order_id
            else:
                raise Exception("Order submission returned None")
            
        except Exception as e:
            self.logger.error(f"❌ Error submitting partial order: {e}")
            return None
    
    def submit_bracket_order(self, symbol, side, quantity, take_profit_price, stop_loss_price, time_in_force="day"):
        """Submit bracket order with take profit and stop loss"""
        try:
            # Get current market price for the bracket order entry price
            from core.data_manager import DataManager
            dm = DataManager()
            current_data = dm.get_current_market_data(symbol)
            
            if not current_data:
                raise Exception(f"Could not get current price for {symbol}")
                
            entry_price = current_data['price']
            
            # Validate bracket order prices based on order side
            if side.lower() == 'buy':
                # For BUY orders:
                # - Take profit should be ABOVE entry price (sell higher)
                # - Stop loss should be BELOW entry price (sell lower to limit loss)
                if take_profit_price <= entry_price:
                    self.logger.warning(f"⚠️ Invalid take profit for BUY: ${take_profit_price} <= ${entry_price}")
                    take_profit_price = entry_price * 1.003  # 0.3% above entry
                    
                if stop_loss_price >= entry_price:
                    self.logger.warning(f"⚠️ Invalid stop loss for BUY: ${stop_loss_price} >= ${entry_price}")
                    stop_loss_price = entry_price * 0.998  # 0.2% below entry
                    
            else:  # SELL orders
                # For SELL orders:
                # - Take profit should be BELOW entry price (buy back lower)
                # - Stop loss should be ABOVE entry price (buy back higher to limit loss)
                if take_profit_price >= entry_price:
                    self.logger.warning(f"⚠️ Invalid take profit for SELL: ${take_profit_price} >= ${entry_price}")
                    take_profit_price = entry_price * 0.997  # 0.3% below entry
                    
                if stop_loss_price <= entry_price:
                    self.logger.warning(f"⚠️ Invalid stop loss for SELL: ${stop_loss_price} <= ${entry_price}")
                    stop_loss_price = entry_price * 1.002  # 0.2% above entry
            
            # Round prices to valid tick increments
            entry_price = self.round_price_to_tick(entry_price)
            take_profit_price = self.round_price_to_tick(take_profit_price)
            stop_loss_price = self.round_price_to_tick(stop_loss_price)
            
            # Clear relevant cache entries before order submission
            cache_manager.on_order_event(symbol, "order_event")
            
            self.logger.info(f"📝 Submitting bracket order for {quantity} shares of {symbol} ({side.upper()})")
            self.logger.info(f"   Entry: ${entry_price}, Take Profit: ${take_profit_price}, Stop Loss: ${stop_loss_price}")
            
            if not self.alpaca_trader:
                raise Exception("AlpacaTrader not initialized")
            
            # Use the AlpacaTrader's bracket order method
            order_id = self.alpaca_trader.submit_bracket_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                limit_price=entry_price,  # Use current price as limit price
                stop_loss=stop_loss_price,
                take_profit=take_profit_price
            )
            
            if order_id:
                self.logger.info(f"✅ Bracket order submitted successfully: {order_id}")
                
                # Track the order
                order_data = {
                    'id': order_id,
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'entry_price': entry_price,
                    'stop_loss': stop_loss_price,
                    'take_profit': take_profit_price,
                    'timestamp': datetime.now(),
                    'status': 'submitted'
                }
                
                self.orders[order_id] = order_data
                
                # Force cache refresh after successful order
                cache_manager.on_order_event(symbol, "order_event")
                
                return order_id
            else:
                raise Exception("Order submission failed - no order ID returned")
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"❌ Error submitting bracket order: {error_msg}")
            
            # Check for wash trade error
            if "wash trade detected" in error_msg.lower() or ("40310000" in error_msg and "opposite side" in error_msg.lower()):
                self.logger.warning(f"⚠️ Wash trade detected for bracket order on {symbol}")
                return None
            
            # Check for insufficient quantity error
            if "insufficient qty available for order" in error_msg.lower():
                available_qty = self._extract_available_quantity(error_msg)
                if available_qty and available_qty >= 1:
                    self.logger.info(f"🔄 Retrying bracket order with available quantity: {available_qty}")
                    return self.submit_bracket_order(symbol, side, available_qty, take_profit_price, stop_loss_price, time_in_force)
            
            return None
    
    def get_available_shares(self, symbol: str, context: str = "general", force_fresh: bool = False) -> int:
        """Get available shares for a symbol from current positions"""
        try:
            if not self.alpaca_trader:
                self.logger.warning(f"⚠️ AlpacaTrader not initialized - cannot get position for {symbol}")
                return 0
            
            # Get position from Alpaca
            position = self.alpaca_trader.get_position(symbol)
            
            if not position:
                self.logger.debug(f"📍 No position found for {symbol}")
                return 0
            
            available_qty = abs(int(position['qty']))  # Convert to positive integer shares
            
            self.logger.info(f"📊 Available shares for {symbol}: {available_qty} (context: {context})")
            return available_qty
            
        except Exception as e:
            self.logger.error(f"❌ Error getting available shares for {symbol}: {e}")
            return 0
    
    def cancel_pending_orders_for_symbol(self, symbol: str) -> int:
        """Cancel all pending orders for a specific symbol"""
        try:
            if not self.alpaca_trader:
                self.logger.warning(f"⚠️ AlpacaTrader not initialized - cannot cancel orders for {symbol}")
                return 0
            
            # Get all open orders for the symbol
            from alpaca.trading.enums import QueryOrderStatus
            orders = self.alpaca_trader.get_orders(
                status=QueryOrderStatus.OPEN,
                symbols=[symbol]
            )
            
            cancelled_count = 0
            for order in orders:
                try:
                    success = self.alpaca_trader.cancel_order(order['id'])
                    if success:
                        self.logger.info(f"✅ Cancelled order {order['id']} for {symbol}")
                        cancelled_count += 1
                    else:
                        self.logger.warning(f"⚠️ Failed to cancel order {order['id']}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to cancel order {order['id']}: {e}")
            
            self.logger.info(f"📊 Cancelled {cancelled_count} pending orders for {symbol}")
            return cancelled_count
            
        except Exception as e:
            self.logger.error(f"❌ Error cancelling pending orders for {symbol}: {e}")
            return 0
    
    def _check_and_clear_conflicting_orders(self, symbol: str, side: str):
        """Proactively check for and clear conflicting orders before submission"""
        try:
            if not self.alpaca_trader:
                return
            
            # Get all open orders for the symbol
            from alpaca.trading.enums import QueryOrderStatus
            orders = self.alpaca_trader.get_orders(
                status=QueryOrderStatus.OPEN,
                symbols=[symbol]
            )
            
            opposite_side = "sell" if side.lower() == "buy" else "buy"
            conflicting_orders = []
            
            for order in orders:
                # Check if order is on opposite side
                if order['side'].lower() == opposite_side:
                    conflicting_orders.append(order)
            
            if conflicting_orders:
                self.logger.warning(f"🚨 Found {len(conflicting_orders)} conflicting {opposite_side} orders for {symbol} - cancelling proactively")
                
                for order in conflicting_orders:
                    try:
                        success = self.alpaca_trader.cancel_order(order['id'])
                        if success:
                            self.logger.info(f"✅ Proactively cancelled conflicting {order['side']} order {order['id']}")
                        else:
                            self.logger.warning(f"⚠️ Failed to cancel conflicting order {order['id']}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to cancel conflicting order {order['id']}: {e}")
                
                # Wait for cancellations to process
                if conflicting_orders:
                    time.sleep(1.5)
                    self.logger.info(f"⏱️ Waited for order cancellations to process")
            
        except Exception as e:
            self.logger.error(f"❌ Error checking for conflicting orders: {e}")
    
    def get_position_info(self, symbol: str, context: str = "general", force_fresh: bool = False) -> dict:
        """Get detailed position information for a symbol"""
        try:
            if not self.alpaca_trader:
                now = time.time()
                if not hasattr(self, '_last_reinit_attempt') or now - getattr(self, '_last_reinit_attempt', 0) > 10:
                    self._last_reinit_attempt = now
                    self.logger.warning(f"⚠️ AlpacaTrader not initialized (context={context}) - attempting re-initialization")
                    try:
                        self.initialize_trading()
                    except Exception as re_err:
                        self.logger.error(f"❌ Re-init attempt failed: {re_err}")
                if not self.alpaca_trader:
                    return {}
            
            # Get position from Alpaca
            position = self.alpaca_trader.get_position(symbol)
            
            if not position:
                self.logger.debug(f"📍 No position found for {symbol}")
                return {}
            
            # Lower to debug to avoid log spam every cycle
            self.logger.debug(f"📊 Position info for {symbol}: {position['qty']} shares (context: {context})")
            return position
            
        except Exception as e:
            self.logger.error(f"❌ Error getting position info for {symbol}: {e}")
            return {}
    
    def cancel_all_orders(self, symbol=None):
        """Cancel all open orders, optionally filtered by symbol"""
        try:
            if not self.api:
                raise Exception("API not initialized")
            
            # Get all open orders
            orders = self.api.list_orders(status='open')
            
            if symbol:
                orders = [order for order in orders if order.symbol == symbol]
                self.logger.info(f"📋 Found {len(orders)} open orders for {symbol}")
            else:
                self.logger.info(f"📋 Found {len(orders)} total open orders")
            
            cancelled_count = 0
            for order in orders:
                try:
                    self.api.cancel_order(order.id)
                    self.logger.info(f"❌ Cancelled order {order.id} for {order.symbol}")
                    cancelled_count += 1
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to cancel order {order.id}: {e}")
            
            self.logger.info(f"✅ Successfully cancelled {cancelled_count} orders")
            
            # Clear cache after cancelling orders
            if symbol:
                cache_manager.on_order_event(symbol, "order_event")
            else:
                cache_manager.clear_all()
            
            return cancelled_count
            
        except Exception as e:
            self.logger.error(f"❌ Error cancelling orders: {e}")
            return 0
    
    def get_pending_orders(self, symbol=None):
        """Get all pending orders, optionally filtered by symbol"""
        try:
            if not self.api:
                raise Exception("API not initialized")
            
            orders = self.api.list_orders(status='open')
            
            if symbol:
                orders = [order for order in orders if order.symbol == symbol]
            
            return orders
            
        except Exception as e:
            self.logger.error(f"❌ Error getting pending orders: {e}")
            return []
    
    def submit_market_order(self, symbol, side, quantity, time_in_force="day"):
        """Convenience method for market orders - uses AlpacaTrader directly"""
        try:
            if not self.alpaca_trader:
                self._set_last_error('not_initialized', 'Alpaca trader not initialized', {'symbol': symbol})
                raise Exception("Alpaca trader not initialized")
            
            # Round prices to avoid sub-penny errors (not needed for market orders but for consistency)
            cache_manager.on_order_event(symbol, "order_event")
            
            self.logger.info(f"📝 Submitting {side} market order for {quantity} shares of {symbol}")
            
            # Validate quantity - Alpaca requires whole shares for most stocks
            if quantity <= 0:
                self._set_last_error('invalid_quantity', f'Invalid quantity: {quantity}', {'symbol': symbol, 'side': side})
                raise Exception(f"Invalid quantity: {quantity}. Quantity must be greater than 0.")
            
            # Check for fractional shares
            if quantity != int(quantity):
                # Round up fractional shares to nearest whole number
                rounded_quantity = max(1, int(round(quantity)))
                self.logger.warning(f"⚠️ Fractional shares not supported. Rounding {quantity} to {rounded_quantity} shares")
                actual_quantity = rounded_quantity
            else:
                actual_quantity = int(quantity)
            
            order_id = self.alpaca_trader.submit_market_order(symbol, side, actual_quantity)
            
            if order_id:
                self.logger.info(f"✅ Market order submitted successfully: {order_id}")
                
                # Force cache refresh after successful order
                cache_manager.on_order_event(symbol, "order_event")
                # Clear any previous error
                self.clear_last_error()
                
                # Return a simple object with order ID
                class OrderResult:
                    def __init__(self, order_id):
                        self.id = order_id
                
                return OrderResult(order_id)
            else:
                self.logger.error(f"❌ Failed to submit market order for {symbol}")
                self._set_last_error('order_submit_failed', 'Failed to submit market order', {'symbol': symbol, 'side': side, 'quantity': actual_quantity})
                return None
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"❌ Error submitting market order: {error_msg}")
            # Default record of the error
            base_details = {'symbol': symbol, 'side': side, 'quantity': quantity}
            self._set_last_error('api_error', error_msg, base_details)
            
            # Try to parse JSON error if it looks like JSON
            error_data = None
            if error_msg.strip().startswith('{') and error_msg.strip().endswith('}'):
                try:
                    import json
                    error_data = json.loads(error_msg)
                except:
                    pass
            
            # Check for insufficient quantity error (check this first as it's more specific)
            is_insufficient_qty = False
            if error_data:
                # JSON format insufficient quantity check
                is_insufficient_qty = (error_data.get("code") == 40310000 and 
                                     "insufficient qty available" in error_data.get("message", "").lower())
            else:
                # Text format insufficient quantity check
                is_insufficient_qty = ("insufficient qty available" in error_msg.lower() or "40310000" in error_msg)
            
            if is_insufficient_qty:
                self.logger.warning(f"🔍 Insufficient quantity error detected for {symbol}")
                available_qty = self._extract_available_quantity(error_msg, symbol)
                self._set_last_error('insufficient_qty', error_msg, {**base_details, 'available_qty': available_qty, 'raw': error_data or error_msg})
                
                # Check if it's a "held_for_orders" situation
                is_held_for_orders = False
                if error_data:
                    held_for_orders = error_data.get("held_for_orders")
                    existing_qty = error_data.get("existing_qty")
                    available = error_data.get("available")
                    
                    if (held_for_orders and existing_qty and available == "0" and 
                        int(held_for_orders) > 0 and int(existing_qty) > 0):
                        is_held_for_orders = True
                        self.logger.warning(f"🔒 Shares held for orders: {held_for_orders}/{existing_qty} for {symbol}")
                
                # If shares are held for pending orders, we need to handle this differently
                if is_held_for_orders:
                    self.logger.warning(f"⚠️ Cannot place order for {symbol} - all shares held for pending orders")
                    self._set_last_error('held_for_orders', 'All shares held for pending orders', {**base_details, 'raw': error_data or error_msg})
                    # Return None to indicate we should try cancelling orders first
                    return None
                
                # If we found available quantity and it's greater than 0, try partial order
                elif available_qty and available_qty > 0 and available_qty < quantity:
                    self.logger.warning(f"🔄 Retrying with partial quantity: {available_qty} instead of {quantity}")
                    self._set_last_error('retry_partial', 'Retrying with partial quantity', {**base_details, 'retry_qty': available_qty})
                    # Recursive call with available quantity
                    return self.submit_market_order(symbol, side, available_qty, time_in_force)
            
            # Check for wash trade error (only if not insufficient quantity)
            else:
                is_wash_trade = False
                if error_data:
                    # JSON format wash trade check
                    is_wash_trade = (error_data.get("code") == 40310000 and 
                                   ("opposite side" in error_data.get("message", "").lower() or
                                    "related_orders" in error_data))
                else:
                    # Text format wash trade check
                    is_wash_trade = ("wash trade detected" in error_msg.lower() or 
                                   ("40310000" in error_msg and "opposite side" in error_msg.lower()))
                
                if is_wash_trade:
                    self.logger.warning(f"⚠️ Wash trade detected for {symbol}")
                    self._set_last_error('wash_trade', error_msg, base_details)
                    return self._handle_wash_trade_error(error_msg, symbol, side, quantity, "market")
            
            return None
    
    def submit_limit_order(self, symbol, side, quantity, limit_price, time_in_force="day"):
        """Convenience method for limit orders - delegates to submit_order"""
        return self.submit_order(symbol, side, quantity, order_type="limit", limit_price=limit_price, time_in_force=time_in_force)
    
    def submit_stop_order(self, symbol, side, quantity, stop_price, time_in_force="day"):
        """Convenience method for stop orders - delegates to submit_order"""
        return self.submit_order(symbol, side, quantity, order_type="stop", stop_price=stop_price, time_in_force=time_in_force)

def round_price_to_penny(price: float) -> float:
    """Round price to valid penny increment for Alpaca"""
    return round(price, 2)

def round_price_to_tick(price: float, symbol: str = None) -> float:
    """Round price to valid tick increment
    
    Args:
        price: Price to round
        symbol: Stock symbol (for future tick size customization)
    
    Returns:
        Rounded price to nearest penny
    """
    return round(price, 2)
