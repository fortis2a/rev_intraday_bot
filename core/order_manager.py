#!/usr/bin/env python3
"""
Order Manager for Intraday Trading Bot
Handles trade execution and order management with stock-specific thresholds
ASCII-only, no Unicode characters
"""

import alpaca_trade_api as tradeapi
from datetime import datetime
from config import config
from utils.logger import setup_logger, clean_message
from utils.price_utils import round_to_cent, calculate_stop_loss_price, calculate_take_profit_price, validate_price_precision
from core.trailing_stop_manager import TrailingStopManager

# Import stock-specific configuration
try:
    from stock_specific_config import get_stock_thresholds, get_position_size_multiplier, get_confidence_adjustment
    STOCK_SPECIFIC_AVAILABLE = True
except ImportError:
    STOCK_SPECIFIC_AVAILABLE = False

class OrderManager:
    """Manages trade execution and orders"""
    
    def __init__(self, data_manager):
        self.logger = setup_logger('order_manager')
        self.data_manager = data_manager
        self.api = data_manager.api
        
        # Initialize trailing stop manager
        self.trailing_stop_manager = TrailingStopManager(self)
        
        # Trading cooldown tracking
        self.last_trade_times = {}  # symbol -> last trade timestamp
        
        self.logger.info("Order Manager initialized with trailing stop support")
    
    def is_trading_allowed(self, symbol):
        """Check if trading is allowed based on cooldown period"""
        if symbol not in self.last_trade_times:
            return True
            
        from config import config
        cooldown_minutes = config.get('TRADE_COOLDOWN_MINUTES', 5)
        last_trade_time = self.last_trade_times[symbol]
        current_time = datetime.now()
        time_diff = (current_time - last_trade_time).total_seconds() / 60
        
        if time_diff < cooldown_minutes:
            self.logger.info(f"[{symbol}] Trade cooldown active: {time_diff:.1f}/{cooldown_minutes} minutes")
            return False
        
        return True
    
    def update_last_trade_time(self, symbol):
        """Update the last trade time for a symbol"""
        self.last_trade_times[symbol] = datetime.now()
    
    def calculate_position_size(self, symbol, price, account_equity):
        """Calculate appropriate position size - Limited to 10 shares per trade"""
        try:
            # Fixed position size of 10 shares for all trades
            shares = 10
            
            # Get stock-specific position size multiplier for logging purposes
            base_multiplier = 1.0
            if STOCK_SPECIFIC_AVAILABLE and config['USE_STOCK_SPECIFIC_THRESHOLDS']:
                base_multiplier = get_position_size_multiplier(symbol)
            
            self.logger.info(f"[{symbol}] Position size: {shares} shares "
                           f"(${shares * price:.2f}, fixed size)")
            
            return shares
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to calculate position size: {e}")
            return 10  # Return 10 shares even if there's an error
    
    def get_stock_thresholds(self, symbol):
        """Get stock-specific thresholds or defaults"""
        if STOCK_SPECIFIC_AVAILABLE and config['USE_STOCK_SPECIFIC_THRESHOLDS']:
            thresholds = get_stock_thresholds(symbol)
            
            self.logger.info(f"[{symbol}] Using stock-specific thresholds: "
                           f"Stop: {thresholds['stop_loss_pct']*100:.2f}%, "
                           f"Profit: {thresholds['take_profit_pct']*100:.2f}%, "
                           f"Trail: {thresholds['trailing_distance_pct']*100:.2f}%")
            
            return thresholds
        else:
            # Use config defaults
            return {
                'stop_loss_pct': config['STOP_LOSS_PCT'],
                'take_profit_pct': config['TAKE_PROFIT_PCT'],
                'trailing_activation_pct': config['TRAILING_STOP_ACTIVATION'],
                'trailing_distance_pct': config['TRAILING_STOP_PCT'],
                'confidence_multiplier': 1.0,
                'profile': 'moderate_volatility'
            }
    
    def place_buy_order(self, symbol, signal_data):
        """Place a buy order with cooldown and precision checks"""
        try:
            # Check trading cooldown
            if not self.is_trading_allowed(symbol):
                return None
            
            # Double-check for existing positions (safety measure)
            positions = self.data_manager.get_positions()
            existing_position = next((p for p in positions if p['symbol'] == symbol and p['side'] == 'long'), None)
            
            if existing_position:
                self.logger.info(f"[SAFETY BLOCK] {symbol} - Already have long position: {existing_position['qty']} shares")
                return None
            
            # Check maximum position limit
            long_positions = [p for p in positions if p['side'] == 'long']
            max_positions = config.get('MAX_POSITIONS', 5)
            
            if len(long_positions) >= max_positions:
                self.logger.info(f"[POSITION LIMIT] Cannot open new position - already have {len(long_positions)}/{max_positions} positions")
                return None
            
            # Get current price and account info
            current_price = self.data_manager.get_current_price(symbol)
            account_info = self.data_manager.get_account_info()
            
            if not current_price or not account_info:
                self.logger.error(f"[ERROR] Could not get price or account info for {symbol}")
                return None
            
            # Calculate position size with stock-specific adjustments
            shares = self.calculate_position_size(symbol, current_price, account_info['equity'])
            
            # Check buying power
            required_cash = shares * current_price
            if required_cash > account_info['buying_power']:
                self.logger.warning(f"[WARNING] Insufficient buying power for {symbol}")
                return None
            
            # Get stock-specific thresholds
            thresholds = self.get_stock_thresholds(symbol)
            
            # Calculate stop loss and take profit using stock-specific values with proper rounding
            stop_loss_price = calculate_stop_loss_price(current_price, thresholds['stop_loss_pct'])
            take_profit_price = calculate_take_profit_price(current_price, thresholds['take_profit_pct'])
            
            # Validate price precision to prevent sub-penny errors
            if not validate_price_precision(stop_loss_price, f"{symbol} stop_loss"):
                self.logger.warning(f"[WARNING] {symbol} stop loss price precision issue: {stop_loss_price}")
                stop_loss_price = round_to_cent(stop_loss_price)
                
            if not validate_price_precision(take_profit_price, f"{symbol} take_profit"):
                self.logger.warning(f"[WARNING] {symbol} take profit price precision issue: {take_profit_price}")
                take_profit_price = round_to_cent(take_profit_price)
            
            self.logger.info(f"[ORDER] Placing BUY order for {symbol}")
            self.logger.info(f"[ORDER] Shares: {shares}, Price: ${current_price:.2f}")
            self.logger.info(f"[ORDER] Stop Loss: ${stop_loss_price:.2f} ({thresholds['stop_loss_pct']*100:.2f}%)")
            self.logger.info(f"[ORDER] Take Profit: ${take_profit_price:.2f} ({thresholds['take_profit_pct']*100:.2f}%)")
            self.logger.info(f"[ORDER] Strategy: {signal_data.get('strategy', 'Unknown')}, "
                           f"Confidence: {signal_data.get('confidence', 0)*100:.1f}%")
            
            # Place market buy order
            order = self.api.submit_order(
                symbol=symbol,
                qty=shares,
                side='buy',
                type='market',
                time_in_force='day'
            )
            
            self.logger.info(f"[SUCCESS] Buy order placed - Order ID: {order.id}")
            
            # Update last trade time for cooldown tracking
            self.update_last_trade_time(symbol)
            
            # Add position to trailing stop manager with stock-specific settings
            self.trailing_stop_manager.add_position(
                symbol=symbol,
                entry_price=current_price,
                quantity=shares,
                side='long',
                initial_stop_price=stop_loss_price,
                custom_thresholds=thresholds
            )
            
            # Place stop loss order (will be managed by trailing stop system)
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
                
                # Store stop order ID for potential updates
                if hasattr(self.trailing_stop_manager, 'stop_orders'):
                    self.trailing_stop_manager.stop_orders[symbol] = stop_order.id
                    
            except Exception as e:
                self.logger.error(f"[ERROR] Failed to place stop loss: {e}")
            
            # Log position details with stock-specific trailing stop info
            self.logger.info("=" * 50)
            self.logger.info(f"🎯 POSITION OPENED: {symbol}")
            self.logger.info(f"💰 Entry Price: ${current_price:.2f}")
            self.logger.info(f"📊 Quantity: {shares} shares")
            self.logger.info(f"💸 Total Value: ${shares * current_price:.2f}")
            self.logger.info(f"🛡️  Initial Stop: ${stop_loss_price:.2f} (-{thresholds['stop_loss_pct']:.1%})")
            self.logger.info(f"🎯 Take Profit: ${take_profit_price:.2f} (+{thresholds['take_profit_pct']:.1%})")
            
            if config['TRAILING_STOP_ENABLED']:
                activation_price = current_price * (1 + thresholds['trailing_activation_pct'])
                self.logger.info(f"🚀 Trailing Activation: ${activation_price:.2f} (+{thresholds['trailing_activation_pct']:.1%})")
                self.logger.info(f"📏 Trailing Distance: {thresholds['trailing_distance_pct']:.1%}")
                
                # Show stock profile info if available
                if 'profile' in thresholds:
                    self.logger.info(f"📊 Volatility Profile: {thresholds['profile']}")
            else:
                self.logger.info("⚠️  Trailing stops: DISABLED")
            
            self.logger.info("=" * 50)
            
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
    
    def update_trailing_stops(self, symbol: str, current_price: float):
        """Update trailing stops for a position"""
        try:
            if not config['TRAILING_STOP_ENABLED']:
                return
            
            update_info = self.trailing_stop_manager.update_position_price(symbol, current_price)
            
            if update_info and update_info['action'] == 'update_stop':
                # Cancel existing stop order and place new one
                if symbol in self.trailing_stop_manager.stop_orders:
                    try:
                        old_order_id = self.trailing_stop_manager.stop_orders[symbol]
                        self.api.cancel_order(old_order_id)
                        self.logger.info(f"[{symbol}] Cancelled old stop order: {old_order_id}")
                    except Exception as e:
                        self.logger.warning(f"[{symbol}] Failed to cancel old stop order: {e}")
                
                # Place new trailing stop order
                try:
                    position_status = self.trailing_stop_manager.get_position_status(symbol)
                    if position_status:
                        # Ensure stop price is properly rounded to prevent sub-penny errors
                        stop_price = round_to_cent(update_info['new_stop_price'])
                        
                        # Validate the price precision
                        if not validate_price_precision(stop_price, f"{symbol} updated_stop"):
                            self.logger.warning(f"[{symbol}] Updated stop price precision issue: {stop_price}")
                            stop_price = round_to_cent(stop_price)
                        
                        new_stop_order = self.api.submit_order(
                            symbol=symbol,
                            qty=position_status['symbol'] in self.get_current_positions_qty(),  # Get actual quantity
                            side='sell',
                            type='stop',
                            stop_price=stop_price,
                            time_in_force='day'
                        )
                        
                        self.trailing_stop_manager.stop_orders[symbol] = new_stop_order.id
                        self.logger.info(f"[{symbol}] New trailing stop order placed: {new_stop_order.id} at ${stop_price:.2f}")
                        
                except Exception as e:
                    self.logger.error(f"[{symbol}] Failed to place new trailing stop order: {e}")
        
        except Exception as e:
            self.logger.error(f"[{symbol}] Failed to update trailing stops: {e}")
    
    def get_current_positions_qty(self) -> dict:
        """Get current position quantities for all symbols"""
        try:
            positions = self.data_manager.get_positions()
            qty_dict = {}
            for pos in positions:
                qty_dict[pos['symbol']] = abs(int(pos['qty']))
            return qty_dict
        except Exception as e:
            self.logger.error(f"Failed to get position quantities: {e}")
            return {}
    
    def check_trailing_stop_triggers(self):
        """Check if any trailing stops have been triggered"""
        try:
            if not config['TRAILING_STOP_ENABLED']:
                return []
            
            triggered_positions = []
            
            for symbol in list(self.trailing_stop_manager.active_positions.keys()):
                # Get current price
                try:
                    current_price = self.data_manager.get_current_price(symbol)
                    if current_price:
                        # Update position and check for trigger
                        self.update_trailing_stops(symbol, current_price)
                        
                        if self.trailing_stop_manager.check_stop_triggered(symbol, current_price):
                            triggered_positions.append(symbol)
                            
                            # Execute market sell order
                            position_status = self.trailing_stop_manager.get_position_status(symbol)
                            if position_status:
                                self.logger.warning(f"[{symbol}] 🛑 EXECUTING TRAILING STOP SELL")
                                sell_result = self.place_sell_order(symbol)
                                if sell_result:
                                    self.trailing_stop_manager.remove_position(symbol, "Trailing stop triggered")
                
                except Exception as e:
                    self.logger.error(f"[{symbol}] Failed to check trailing stop trigger: {e}")
            
            return triggered_positions
            
        except Exception as e:
            self.logger.error(f"Failed to check trailing stop triggers: {e}")
            return []
    
    def get_trailing_stop_summary(self) -> str:
        """Get formatted summary of all trailing stop positions"""
        try:
            if not config['TRAILING_STOP_ENABLED']:
                return "Trailing stops are disabled"
            
            positions = self.trailing_stop_manager.get_all_positions_status()
            
            if not positions:
                return "No active trailing stop positions"
            
            summary = "🎯 TRAILING STOP POSITIONS:\n"
            summary += "=" * 50 + "\n"
            
            for pos in positions:
                status_icon = "🚀" if pos['is_trailing_active'] else "⏳"
                summary += f"{status_icon} {pos['symbol']}\n"
                summary += f"  💰 Entry: ${pos['entry_price']:.2f} | Current: ${pos['current_price']:.2f}\n"
                summary += f"  📈 Profit: {pos['profit_pct']:.1%} (${pos['unrealized_pnl']:.2f})\n"
                summary += f"  🛡️  Stop: ${pos['trailing_stop_price']:.2f} | Protected: {pos['profit_protected_pct']:.1%}\n"
                summary += f"  📏 Distance to Stop: {pos['distance_to_stop']:.1%}\n\n"
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get trailing stop summary: {e}")
            return "Error generating trailing stop summary"
    
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
