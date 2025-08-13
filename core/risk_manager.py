#!/usr/bin/env python3
"""
🛡️ Risk Manager for Intraday Trading Bot
Handles position sizing, risk limits, and portfolio protection
"""

import sys
from pathlib import Path
from typing import Optional, Dict
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import config

class RiskManager:
    """Risk management system for intraday trading operations"""
    
    def __init__(self):
        """Initialize risk manager"""
        self.logger = logging.getLogger("risk_manager")
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.max_portfolio_risk = 0.05  # 5% max portfolio risk
        self.position_count = 0
        self.total_short_exposure = 0.0  # Track total short position value
        self.short_positions = {}  # Track individual short positions: {symbol: {qty: int, price: float}}
        
        # Get account info (will be connected to broker or simulated)
        if config.SIMULATE_PORTFOLIO:
            self.account_equity = config.SIMULATED_PORTFOLIO_VALUE
            self.logger.info(f"🧪 Using simulated portfolio: ${config.SIMULATED_PORTFOLIO_VALUE:,.2f}")
        else:
            self.account_equity = 100000.0  # Default, will update from broker
        
        self.logger.info("🛡️ Risk Manager initialized")
        self.logger.info(f"📊 Initial short exposure: ${self.total_short_exposure:.2f}")
    
    def track_position_opened(self, symbol: str, signal_type: str, position_size: int, entry_price: float):
        """Track when a position is opened"""
        self.position_count += 1
        
        if signal_type == "SELL":
            # Track short exposure
            short_value = position_size * entry_price
            self.total_short_exposure += short_value
            
            # Track individual short position
            if symbol in self.short_positions:
                # Add to existing short position
                existing_qty = self.short_positions[symbol]['qty']
                existing_avg_price = self.short_positions[symbol]['price']
                total_qty = existing_qty + position_size
                new_avg_price = ((existing_qty * existing_avg_price) + (position_size * entry_price)) / total_qty
                self.short_positions[symbol] = {'qty': total_qty, 'price': new_avg_price}
            else:
                # New short position
                self.short_positions[symbol] = {'qty': position_size, 'price': entry_price}
            
            self.logger.info(f"📊 Short exposure updated: +${short_value:.2f}, Total: ${self.total_short_exposure:.2f}")
            self.logger.info(f"📊 Short position tracked: {symbol} {self.short_positions[symbol]['qty']} shares @ ${self.short_positions[symbol]['price']:.2f}")
        else:
            self.logger.debug(f"📊 Long position opened: {symbol} {position_size} shares @ ${entry_price:.2f}")
    
    def track_position_closed(self, symbol: str, signal_type: str, position_size: int, entry_price: float, exit_price: float):
        """Track when a position is closed"""
        self.position_count = max(0, self.position_count - 1)
        
        # Calculate P&L
        if signal_type == "BUY":
            pnl = (exit_price - entry_price) * position_size
        else:  # SELL (short)
            pnl = (entry_price - exit_price) * position_size
            # Remove from short exposure
            short_value = position_size * entry_price
            self.total_short_exposure = max(0, self.total_short_exposure - short_value)
            
            # Update individual short position tracking
            if symbol in self.short_positions:
                current_qty = self.short_positions[symbol]['qty']
                if current_qty <= position_size:
                    # Fully closing the short position
                    del self.short_positions[symbol]
                    self.logger.info(f"📊 Short position fully closed: {symbol}")
                else:
                    # Partially closing the short position
                    self.short_positions[symbol]['qty'] = current_qty - position_size
                    self.logger.info(f"📊 Short position partially closed: {symbol} remaining {self.short_positions[symbol]['qty']} shares")
            
            self.logger.info(f"📊 Short exposure updated: -${short_value:.2f}, Total: ${self.total_short_exposure:.2f}")
        
        self.daily_pnl += pnl
        self.daily_trades += 1
        self.logger.debug(f"💰 Position closed: ${pnl:+.2f} P&L, Daily: ${self.daily_pnl:+.2f}")
    
    def _get_available_shares(self, symbol: str) -> int:
        """Get available shares for a symbol (for sell orders)"""
        try:
            # Check with the order manager for actual available shares
            from core.order_manager import OrderManager
            om = OrderManager()
            
            if hasattr(om, 'get_available_shares'):
                available_shares = om.get_available_shares(symbol)
                if available_shares is not None:
                    self.logger.debug(f"📊 Available shares for {symbol}: {available_shares}")
                    return available_shares
            
            # Fallback: try to get position information directly
            if hasattr(om, 'alpaca_trader') and om.alpaca_trader:
                try:
                    position = om.alpaca_trader.get_position(symbol)
                    if position and hasattr(position, 'qty'):
                        qty = int(float(position.qty))
                        self.logger.debug(f"📊 Position quantity for {symbol}: {qty}")
                        return max(0, qty)  # Can't sell negative shares
                except:
                    pass
                    
            # If we can't determine available shares, return 0 to prevent overselling
            self.logger.warning(f"⚠️ Could not determine available shares for {symbol}, returning 0")
            return 0
            
        except Exception as e:
            self.logger.error(f"❌ Error getting available shares for {symbol}: {e}")
            return 0  # Safe default - don't allow sell if we can't verify
    
    def update_account_equity(self, equity: float):
        """Update current account equity"""
        if config.SIMULATE_PORTFOLIO:
            # Keep using simulated value, but log the real account for reference
            self.logger.debug(f"🏦 Real account equity: ${equity:,.2f} (using simulated: ${self.account_equity:,.2f})")
        else:
            self.account_equity = equity
            self.logger.debug(f"💰 Account equity updated: ${equity:,.2f}")
    
    def can_open_position(self, symbol: str, entry_price: float, signal_type: str = "BUY") -> bool:
        """Check if we can open a new position"""
        try:
            # CRITICAL FIX: Auto-sync with broker before checking short exposure limits
            if signal_type == "SELL" and config.ALLOW_SHORT_SELLING:
                self.logger.debug(f"🔍 Checking short exposure for {symbol} - Current: ${self.total_short_exposure:.2f}")
                
                # Try to sync with broker if possible, but don't fail if not available
                try:
                    from core.order_manager import OrderManager
                    om = OrderManager()
                    
                    # Only try to sync if we have a proper broker connection
                    if hasattr(om, 'alpaca_trader') and om.alpaca_trader and hasattr(om.alpaca_trader, 'get_positions'):
                        actual_positions = om.alpaca_trader.get_positions()
                        if actual_positions is not None:
                            old_exposure = self.total_short_exposure
                            self._sync_short_exposure_with_broker(actual_positions)
                            if old_exposure != self.total_short_exposure:
                                self.logger.info(f"🔄 Pre-check sync: ${old_exposure:.2f} → ${self.total_short_exposure:.2f}")
                            else:
                                self.logger.debug(f"✅ Pre-check sync: exposure confirmed at ${self.total_short_exposure:.2f}")
                    else:
                        self.logger.debug("ℹ️ No broker connection available for sync - using cached tracking")
                        
                        # In simulation mode, if we have stale data, reset it
                        if self.total_short_exposure > 0 and not self.short_positions:
                            self.logger.warning("🔄 Simulation mode: resetting stale short exposure tracking")
                            self.total_short_exposure = 0.0
                            
                except Exception as sync_error:
                    self.logger.warning(f"⚠️ Could not sync short exposure before check: {sync_error}")
                    
                    # Fallback: If sync fails and we have inconsistent data, reset it
                    if self.total_short_exposure > 0 and not self.short_positions:
                        self.logger.warning("🔄 Sync failed: resetting inconsistent tracking as fallback")
                        self.total_short_exposure = 0.0
            
            # Check position limits
            if self.position_count >= config.MAX_OPEN_POSITIONS:
                self.logger.warning(f"❌ Max positions reached: {self.position_count}/{config.MAX_OPEN_POSITIONS}")
                return False
            
            # Check daily loss limit (percentage-based)
            max_daily_loss_dollar = self.account_equity * (config.MAX_DAILY_LOSS_PCT / 100)
            if self.daily_pnl <= -max_daily_loss_dollar:
                self.logger.warning(f"❌ Daily loss limit reached: ${self.daily_pnl:.2f} (>{config.MAX_DAILY_LOSS_PCT}% of ${self.account_equity:,.2f})")
                return False
            
            # Check short exposure limits ONLY for SELL signals (short positions)
            if signal_type == "SELL" and config.ALLOW_SHORT_SELLING:
                position_value = self.calculate_position_size(entry_price, entry_price * 0.998, symbol, "sell") * entry_price
                new_total_exposure = self.total_short_exposure + position_value
                
                self.logger.info(f"📊 Short exposure check: Current=${self.total_short_exposure:.2f}, New Position=${position_value:.2f}, Total=${new_total_exposure:.2f}, Limit=${config.MAX_SHORT_EXPOSURE:.2f}")
                
                if new_total_exposure > config.MAX_SHORT_EXPOSURE:
                    # Log detailed information about short positions for debugging
                    self.logger.warning(f"❌ Short exposure limit would be exceeded: ${new_total_exposure:.2f} > ${config.MAX_SHORT_EXPOSURE:.2f}")
                    
                    if self.short_positions:
                        self.logger.info("📊 Current tracked short positions:")
                        tracked_total = 0.0
                        for sym, pos in self.short_positions.items():
                            value = pos['qty'] * pos['price']
                            tracked_total += value
                            self.logger.info(f"  - {sym}: {pos['qty']} shares @ ${pos['price']:.2f} = ${value:.2f}")
                        self.logger.info(f"📊 Tracked total: ${tracked_total:.2f}, Recorded total: ${self.total_short_exposure:.2f}")
                    else:
                        self.logger.warning(f"📊 No tracked short positions but total_short_exposure = ${self.total_short_exposure:.2f}")
                        
                        # FALLBACK FIX: If no tracked positions but exposure exists, reset tracking
                        if self.total_short_exposure > 0:
                            self.logger.warning("🔄 Resetting inconsistent short exposure tracking...")
                            self.total_short_exposure = 0.0
                            self.short_positions = {}
                            # Retry the check with reset values
                            new_total_exposure = self.total_short_exposure + position_value
                            self.logger.info(f"🔄 After reset - New total: ${new_total_exposure:.2f}")
                            
                            if new_total_exposure <= config.MAX_SHORT_EXPOSURE:
                                self.logger.info("✅ Position now allowed after tracking reset")
                                return True  # Allow the position after reset
                    
                    # CRITICAL FIX: Raise exception to completely stop order processing
                    raise Exception(f"SHORT_EXPOSURE_LIMIT_EXCEEDED: Cannot open short position for {symbol} - would exceed ${config.MAX_SHORT_EXPOSURE:.2f} limit")
            elif signal_type == "SELL" and not config.ALLOW_SHORT_SELLING:
                # If short selling is disabled, only allow SELL orders to close existing long positions
                available_shares = self._get_available_shares(symbol)
                if available_shares <= 0:
                    self.logger.warning(f"❌ Short selling disabled and no shares available to sell for {symbol}")
                    # CRITICAL FIX: Raise exception to completely stop order processing  
                    raise Exception(f"SHORT_SELLING_DISABLED: Cannot short {symbol} - short selling disabled and no long position to close")
            
            # For BUY signals (long positions), check buying power
            position_value = self.calculate_position_size(entry_price, entry_price * 0.998, symbol, signal_type.lower()) * entry_price
            required_buying_power = position_value * 1.1  # Add 10% buffer
            
            available_equity = self.account_equity * 0.8  # Use max 80% of equity
            
            if required_buying_power > available_equity:
                self.logger.warning(f"❌ Insufficient buying power: ${required_buying_power:.2f} > ${available_equity:.2f}")
                return False
            
            # Check portfolio concentration (max 40% in any single position for smaller portfolios)
            # Use 40% for portfolios under $5K, 20% for larger portfolios
            max_concentration_pct = 0.4 if self.account_equity < 5000 else 0.2
            max_position_value = min(
                self.account_equity * max_concentration_pct,
                config.MAX_POSITION_VALUE
            )
            if position_value > max_position_value:
                self.logger.warning(f"❌ Position too large: ${position_value:.2f} > ${max_position_value:.2f}")
                return False
            
            self.logger.debug(f"✅ Position approved: {signal_type} {symbol} @ ${entry_price:.2f} (${position_value:.2f})")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error checking position eligibility: {e}")
            return False
    
    def calculate_position_size(self, entry_price: float, stop_loss: float, symbol: str = None, side: str = "buy") -> int:
        """Calculate position size based on risk per trade"""
        try:
            # Calculate risk per share
            risk_per_share = abs(entry_price - stop_loss)
            
            if risk_per_share <= 0:
                self.logger.warning(f"❌ Invalid risk per share: {risk_per_share}")
                return 0
            
            # Calculate dollar risk (percentage of account)
            dollar_risk = self.account_equity * (config.ACCOUNT_RISK_PCT / 100)
            
            # Calculate shares based on risk
            shares = int(dollar_risk / risk_per_share)
            
            # Apply position size limits
            max_shares_by_value = int(config.MAX_POSITION_VALUE / entry_price)
            min_shares_by_value = max(1, int(config.MIN_POSITION_VALUE / entry_price))
            
            # Take the minimum of calculated shares and limits
            shares = min(shares, config.MAX_POSITION_SIZE, max_shares_by_value)
            shares = max(shares, min_shares_by_value)
            
            # For sell orders (short selling), check if this is closing an existing position or opening a new short
            if side.lower() == "sell" and symbol:
                available_shares = self._get_available_shares(symbol)
                
                if available_shares > 0:
                    # We have shares to sell (closing long position)
                    shares = min(shares, available_shares)
                    self.logger.debug(f"📊 Limited sell order to available shares: {shares} (available: {available_shares})")
                else:
                    # No shares available - this would be a short sale (selling shares we don't own)
                    if not config.ALLOW_SHORT_SELLING:
                        self.logger.warning(f"❌ Short selling not allowed for {symbol}")
                        return 0
                    
                    # For short selling, we need to check if broker allows it and if we have enough buying power
                    self.logger.info(f"📊 Short sale order for {symbol}: {shares} shares @ ${entry_price:.2f}")
                    
                    # Check if position value exceeds our limits for short positions
                    short_position_value = shares * entry_price
                    if short_position_value > config.MAX_SHORT_EXPOSURE:
                        shares = int(config.MAX_SHORT_EXPOSURE / entry_price)
                        self.logger.debug(f"📊 Limited short position size due to short exposure limit: {shares} shares")
                    
                    if short_position_value > config.MAX_POSITION_VALUE:
                        shares = int(config.MAX_POSITION_VALUE / entry_price)
                        self.logger.debug(f"📊 Limited short position size due to position value limit: {shares} shares")
            
            # For buy orders, no special handling needed (standard long positions)
            
            # Final validation
            position_value = shares * entry_price
            
            if position_value < config.MIN_POSITION_VALUE:
                self.logger.warning(f"❌ Position value too small: ${position_value:.2f}")
                return 0
            
            if position_value > config.MAX_POSITION_VALUE:
                shares = int(config.MAX_POSITION_VALUE / entry_price)
            
            self.logger.debug(f"📊 Position size for ${entry_price:.2f}: {shares} shares (${position_value:.2f} value)")
            return shares
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating position size: {e}")
            return 0
    
    def validate_order(self, symbol: str, side: str, quantity: int, price: float) -> bool:
        """Validate an order before submission"""
        try:
            # Basic validation
            if quantity <= 0:
                self.logger.warning(f"❌ Invalid quantity: {quantity}")
                return False
            
            if price <= 0:
                self.logger.warning(f"❌ Invalid price: {price}")
                return False
            
            # Check order value limits
            order_value = quantity * price
            
            if order_value < config.MIN_POSITION_VALUE:
                self.logger.warning(f"❌ Order value too small: ${order_value:.2f}")
                return False
            
            if order_value > config.MAX_POSITION_VALUE:
                self.logger.warning(f"❌ Order value too large: ${order_value:.2f}")
                return False
            
            # Check if we're within daily trading limits
            if self.daily_trades >= 100:  # Max 100 trades per day
                self.logger.warning(f"❌ Daily trade limit reached: {self.daily_trades}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error validating order: {e}")
            return False
    
    def update_position_opened(self, symbol: str, quantity: int, price: float):
        """Update risk tracking when position is opened"""
        try:
            self.position_count += 1
            self.daily_trades += 1
            
            order_value = quantity * price
            self.logger.info(f"📈 Position opened: {symbol} - {quantity} shares @ ${price:.2f} (${order_value:.2f})")
            
        except Exception as e:
            self.logger.error(f"❌ Error updating position opened: {e}")
    
    def update_position_closed(self, symbol: str, quantity: int, entry_price: float, exit_price: float):
        """Update risk tracking when position is closed"""
        try:
            self.position_count = max(0, self.position_count - 1)
            
            # Calculate P&L
            pnl = (exit_price - entry_price) * quantity
            self.daily_pnl += pnl
            
            self.logger.info(f"📉 Position closed: {symbol} - P&L: ${pnl:+.2f}, Daily P&L: ${self.daily_pnl:+.2f}")
            
        except Exception as e:
            self.logger.error(f"❌ Error updating position closed: {e}")
    
    def get_max_position_size_for_symbol(self, symbol: str, price: float) -> int:
        """Get maximum allowed position size for a symbol"""
        try:
            # Based on price and position value limits
            max_by_value = int(config.MAX_POSITION_VALUE / price)
            max_by_config = config.MAX_POSITION_SIZE
            
            return min(max_by_value, max_by_config)
            
        except Exception as e:
            self.logger.error(f"❌ Error getting max position size: {e}")
            return 0
    
    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """Calculate stop loss price"""
        try:
            if side.lower() == "buy":
                stop_loss = entry_price * (1 - config.STOP_LOSS_PCT / 100)
            else:  # sell/short
                stop_loss = entry_price * (1 + config.STOP_LOSS_PCT / 100)
            
            return round(stop_loss, 2)
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating stop loss: {e}")
            return entry_price
    
    def calculate_profit_target(self, entry_price: float, side: str) -> float:
        """Calculate profit target price"""
        try:
            if side.lower() == "buy":
                profit_target = entry_price * (1 + config.PROFIT_TARGET_PCT / 100)
            else:  # sell/short
                profit_target = entry_price * (1 - config.PROFIT_TARGET_PCT / 100)
            
            return round(profit_target, 2)
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating profit target: {e}")
            return entry_price
    
    def get_risk_metrics(self) -> Dict:
        """Get current risk metrics"""
        try:
            portfolio_risk_pct = (abs(self.daily_pnl) / self.account_equity) * 100 if self.account_equity > 0 else 0
            max_daily_loss_dollar = self.account_equity * (config.MAX_DAILY_LOSS_PCT / 100)
            
            return {
                'daily_pnl': self.daily_pnl,
                'daily_trades': self.daily_trades,
                'active_positions': self.position_count,
                'account_equity': self.account_equity,
                'portfolio_risk_pct': portfolio_risk_pct,
                'max_daily_loss_pct': config.MAX_DAILY_LOSS_PCT,
                'max_daily_loss_dollar': max_daily_loss_dollar,
                'max_positions': config.MAX_OPEN_POSITIONS,
                'risk_per_trade_pct': config.ACCOUNT_RISK_PCT
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting risk metrics: {e}")
            return {}
    
    def get_live_pnl_metrics(self, order_manager=None, target_date=None) -> Dict:
        """Get live P&L metrics directly from Alpaca account"""
        try:
            import pytz
            from datetime import datetime, timedelta
            
            # Default to today if no date specified
            if target_date is None:
                et_timezone = pytz.timezone('US/Eastern')
                target_date = datetime.now(et_timezone)
            
            date_str = target_date.strftime('%Y-%m-%d')
            
            # Initialize default values
            live_metrics = {
                'daily_pnl': 0.0,
                'daily_trades': 0,
                'active_positions': 0,
                'account_equity': self.account_equity,
                'portfolio_risk_pct': 0.0,
                'win_rate': 0.0,
                'trade_details': [],
                'data_source': 'internal_tracking'
            }
            
            if not order_manager or not hasattr(order_manager, 'alpaca_trader') or not order_manager.alpaca_trader:
                self.logger.warning("⚠️ No order manager available for live P&L data")
                return live_metrics
            
            # Get account info
            account_info = order_manager.alpaca_trader.get_account_info_simple()
            if account_info:
                live_metrics['account_equity'] = float(account_info.get('portfolio_value', self.account_equity))
            
            # Get current positions
            positions = order_manager.alpaca_trader.get_positions()
            if positions:
                live_metrics['active_positions'] = len([pos for pos in positions if abs(float(pos.get('qty', 0))) > 0])
            
            # Get orders for the target date
            all_orders = order_manager.alpaca_trader.get_orders(status='all')
            
            if not all_orders:
                self.logger.warning(f"⚠️ No orders found in account")
                return live_metrics
            
            # Filter orders for target date and extract filled orders
            filled_orders = []
            target_date_str = date_str
            
            for order in all_orders:
                order_date = None
                
                # Try to extract date from various timestamp fields
                for date_field in ['created_at', 'submitted_at', 'filled_at']:
                    if date_field in order and order[date_field]:
                        try:
                            if isinstance(order[date_field], str):
                                order_datetime = datetime.fromisoformat(order[date_field].replace('Z', '+00:00'))
                            else:
                                order_datetime = order[date_field]
                            order_date = order_datetime.strftime('%Y-%m-%d')
                            break
                        except:
                            continue
                
                # Check if order is from target date and is filled
                if (order_date == target_date_str and 
                    order.get('status') == 'filled' and 
                    order.get('filled_avg_price') and 
                    float(order.get('filled_avg_price', 0)) > 0):
                    filled_orders.append(order)
            
            if not filled_orders:
                self.logger.info(f"📊 No filled orders found for {date_str}")
                return live_metrics
            
            # Calculate P&L from filled orders
            symbol_trades = {}
            total_pnl = 0.0
            
            for order in filled_orders:
                symbol = order.get('symbol', '')
                side = order.get('side', '')
                qty = float(order.get('qty', 0))
                price = float(order.get('filled_avg_price', 0))
                
                if symbol not in symbol_trades:
                    symbol_trades[symbol] = {'buys': [], 'sells': []}
                
                trade_data = {'qty': qty, 'price': price, 'order': order}
                symbol_trades[symbol][f"{side}s"].append(trade_data)
                
                # Add to trade details
                live_metrics['trade_details'].append({
                    'symbol': symbol,
                    'side': side,
                    'qty': qty,
                    'price': price,
                    'value': qty * price
                })
            
            # Calculate P&L per symbol
            profitable_symbols = 0
            total_symbols = len(symbol_trades)
            
            for symbol, trades in symbol_trades.items():
                buy_volume = sum(t['qty'] * t['price'] for t in trades['buys'])
                sell_volume = sum(t['qty'] * t['price'] for t in trades['sells'])
                symbol_pnl = sell_volume - buy_volume
                total_pnl += symbol_pnl
                
                if symbol_pnl > 0:
                    profitable_symbols += 1
            
            # Update live metrics
            live_metrics.update({
                'daily_pnl': total_pnl,
                'daily_trades': len(filled_orders),
                'win_rate': (profitable_symbols / total_symbols * 100) if total_symbols > 0 else 0,
                'portfolio_risk_pct': (abs(total_pnl) / live_metrics['account_equity']) * 100,
                'data_source': 'alpaca_live',
                'symbols_traded': list(symbol_trades.keys()),
                'profitable_symbols': profitable_symbols,
                'total_symbols': total_symbols
            })
            
            self.logger.info(f"✅ Retrieved live P&L data: ${total_pnl:.2f} from {len(filled_orders)} trades")
            return live_metrics
            
        except Exception as e:
            self.logger.error(f"❌ Error getting live P&L metrics: {e}")
            import traceback
            traceback.print_exc()
            return live_metrics
    
    def sync_position_count_with_broker(self, order_manager=None):
        """Sync position count with actual broker positions"""
        try:
            if order_manager and hasattr(order_manager, 'alpaca_trader') and order_manager.alpaca_trader:
                actual_positions = order_manager.alpaca_trader.get_positions()
                if actual_positions:
                    # Count non-zero positions
                    actual_count = len([pos for pos in actual_positions if abs(float(pos.get('qty', 0))) > 0])
                    old_count = self.position_count
                    self.position_count = actual_count
                    
                    # Also sync short exposure with actual short positions
                    self._sync_short_exposure_with_broker(actual_positions)
                    
                    if old_count != actual_count:
                        self.logger.info(f"🔄 Position count synced: {old_count} → {actual_count}")
                    else:
                        self.logger.debug(f"✅ Position count already synced: {actual_count}")
                    
                    return actual_count
                else:
                    self.position_count = 0
                    self.total_short_exposure = 0.0
                    self.short_positions = {}
                    self.logger.info("🔄 No broker positions found, position count reset to 0")
                    return 0
            else:
                self.logger.warning("⚠️ Cannot sync position count - no order manager connection")
                return self.position_count
                
        except Exception as e:
            self.logger.error(f"❌ Error syncing position count: {e}")
            return self.position_count
    
    def _sync_short_exposure_with_broker(self, broker_positions):
        """Sync short exposure tracking with actual broker positions"""
        try:
            old_exposure = self.total_short_exposure
            old_positions = self.short_positions.copy()
            
            # Reset tracking
            self.total_short_exposure = 0.0
            self.short_positions = {}
            
            # Rebuild from actual broker positions
            for pos in broker_positions:
                symbol = pos.get('symbol', '')
                qty = float(pos.get('qty', 0))
                market_value = abs(float(pos.get('market_value', 0)))
                
                if qty < 0:  # Short position (negative quantity)
                    qty = abs(qty)  # Work with positive quantity for calculations
                    avg_price = market_value / qty if qty > 0 else 0
                    
                    self.short_positions[symbol] = {'qty': qty, 'price': avg_price}
                    self.total_short_exposure += market_value
                    
                    self.logger.info(f"📊 Synced short position: {symbol} {qty} shares @ ${avg_price:.2f} = ${market_value:.2f}")
            
            if old_exposure != self.total_short_exposure:
                self.logger.info(f"🔄 Short exposure synced: ${old_exposure:.2f} → ${self.total_short_exposure:.2f}")
            else:
                self.logger.debug(f"✅ Short exposure already synced: ${self.total_short_exposure:.2f}")
                
        except Exception as e:
            self.logger.error(f"❌ Error syncing short exposure: {e}")
            # Restore previous values if sync fails
            self.total_short_exposure = old_exposure
            self.short_positions = old_positions
    
    def reset_short_exposure_tracking(self):
        """Reset short exposure tracking (use when debugging or after major changes)"""
        old_exposure = self.total_short_exposure
        self.total_short_exposure = 0.0
        self.short_positions = {}
        self.logger.warning(f"🔄 Short exposure tracking manually reset: ${old_exposure:.2f} → $0.00")
        self.logger.warning("⚠️ This should only be used for debugging - ensure no actual short positions exist!")
    
    def reset_daily_metrics(self):
        """Reset daily risk metrics (call at market open)"""
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.logger.info("🔄 Daily risk metrics reset")

if __name__ == "__main__":
    print("🛡️ Risk Manager Test")
    print("=" * 30)
    
    rm = RiskManager()
    rm.update_account_equity(50000.0)
    
    # Test position sizing
    entry_price = 150.0
    stop_loss = 149.0
    size = rm.calculate_position_size(entry_price, stop_loss)
    
    print(f"Entry: ${entry_price}")
    print(f"Stop: ${stop_loss}")
    print(f"Size: {size} shares")
    print(f"Value: ${size * entry_price:.2f}")
    print(f"Risk: ${size * abs(entry_price - stop_loss):.2f}")
