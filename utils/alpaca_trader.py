#!/usr/bin/env python3
"""
🔗 Alpaca Trading Client
Wrapper for Alpaca API integration
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import config

# Try to import Alpaca API
try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockLatestQuoteRequest, StockBarsRequest
    from alpaca.data.timeframe import TimeFrame
    ALPACA_AVAILABLE = True
except ImportError as e:
    ALPACA_AVAILABLE = False
    print(f"⚠️ Alpaca API not available: {e}")

class AlpacaTrader:
    """Alpaca trading client wrapper"""
    
    def __init__(self):
        """Initialize Alpaca trader"""
        self.logger = logging.getLogger("alpaca_trader")
        self.trading_client = None
        self.data_client = None
        
        if ALPACA_AVAILABLE:
            self._init_clients()
        else:
            self.logger.warning("⚠️ Alpaca API not available - running in simulation mode")
    
    def _init_clients(self):
        """Initialize Alpaca clients"""
        try:
            # Initialize trading client
            self.trading_client = TradingClient(
                api_key=config.ALPACA_API_KEY,
                secret_key=config.ALPACA_SECRET_KEY,
                paper=True if 'paper' in config.ALPACA_BASE_URL else False
            )
            
            # Initialize data client
            self.data_client = StockHistoricalDataClient(
                api_key=config.ALPACA_API_KEY,
                secret_key=config.ALPACA_SECRET_KEY
            )
            
            # Test connection
            account = self.trading_client.get_account()
            self.logger.info(f"✅ Connected to Alpaca - Account: {account.account_number}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Alpaca clients: {e}")
            self.trading_client = None
            self.data_client = None
    
    def is_connected(self) -> bool:
        """Check if connected to Alpaca"""
        return self.trading_client is not None
    
    def get_account_info(self) -> Optional[Dict]:
        """Get account information"""
        try:
            if not self.trading_client:
                return None
            
            account = self.trading_client.get_account()
            return {
                'account_number': account.account_number,
                'equity': float(account.equity),
                'last_equity': float(getattr(account, 'last_equity', account.equity)),
                'portfolio_value': float(account.portfolio_value),
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'day_trade_count': getattr(account, 'day_trade_count', 0),
                'pattern_day_trader': getattr(account, 'pattern_day_trader', False)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting account info: {e}")
            return None
    
    def get_account_info_simple(self) -> Optional[Dict]:
        """Get simplified account information"""
        try:
            account_info = self.get_account_info()
            if account_info:
                return {
                    'portfolio_value': account_info['portfolio_value'],
                    'buying_power': account_info['buying_power'],
                    'cash': account_info['cash']
                }
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error getting simple account info: {e}")
            return None
    
    def submit_market_order(self, symbol: str, side: str, quantity: int) -> Optional[str]:
        """Submit a market order"""
        try:
            if not self.trading_client:
                self.logger.warning("⚠️ No Alpaca connection - simulating order")
                return f"SIM_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{symbol}"
            
            order_side = OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL
            
            market_order = MarketOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=order_side,
                time_in_force=TimeInForce.DAY
            )
            
            order = self.trading_client.submit_order(order_data=market_order)
            self.logger.info(f"✅ Market order submitted: {order.id} - {side} {quantity} {symbol}")
            return order.id
            
        except Exception as e:
            self.logger.error(f"❌ Error submitting market order: {e}")
            # Re-raise the exception so OrderManager can handle it with enhanced error handling
            raise e
    
    def submit_limit_order(self, symbol: str, side: str, quantity: int, limit_price: float) -> Optional[str]:
        """Submit a limit order"""
        try:
            if not self.trading_client:
                self.logger.warning("⚠️ No Alpaca connection - simulating order")
                return f"SIM_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{symbol}"
            
            order_side = OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL
            
            limit_order = LimitOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=order_side,
                time_in_force=TimeInForce.DAY,
                limit_price=limit_price
            )
            
            order = self.trading_client.submit_order(order_data=limit_order)
            self.logger.info(f"✅ Limit order submitted: {order.id} - {side} {quantity} {symbol} @ ${limit_price}")
            return order.id
            
        except Exception as e:
            self.logger.error(f"❌ Error submitting limit order: {e}")
            return None
    
    def submit_bracket_order(self, symbol: str, side: str, quantity: int, 
                           limit_price: float, stop_loss: float, take_profit: float) -> Optional[str]:
        """Submit a bracket order with stop loss and take profit"""
        try:
            if not self.trading_client:
                self.logger.warning("⚠️ No Alpaca connection - simulating bracket order")
                return f"SIM_BRACKET_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{symbol}"
            
            order_side = OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL
            
            bracket_order = LimitOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=order_side,
                time_in_force=TimeInForce.DAY,
                limit_price=limit_price,
                order_class=OrderClass.BRACKET,
                stop_loss={'stop_price': stop_loss},
                take_profit={'limit_price': take_profit}
            )
            
            order = self.trading_client.submit_order(order_data=bracket_order)
            self.logger.info(f"✅ Bracket order submitted: {order.id} - {side} {quantity} {symbol} @ ${limit_price} "
                           f"(SL: ${stop_loss}, TP: ${take_profit})")
            return order.id
            
        except Exception as e:
            self.logger.error(f"❌ Error submitting bracket order: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            if not self.trading_client:
                self.logger.warning(f"⚠️ No Alpaca connection - simulating cancel order {order_id}")
                return True
            
            self.trading_client.cancel_order_by_id(order_id)
            self.logger.info(f"✅ Order cancelled: {order_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error cancelling order {order_id}: {e}")
            return False
    
    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """Get order status"""
        try:
            if not self.trading_client:
                return {
                    'id': order_id,
                    'status': 'filled' if order_id.startswith('SIM') else 'unknown',
                    'filled_qty': 0,
                    'filled_avg_price': 0.0
                }
            
            order = self.trading_client.get_order_by_id(order_id)
            return {
                'id': order.id,
                'symbol': order.symbol,
                'status': order.status.value,
                'side': order.side.value,
                'qty': int(order.qty),
                'filled_qty': int(order.filled_qty or 0),
                'filled_avg_price': float(order.filled_avg_price or 0.0),
                'limit_price': float(order.limit_price or 0.0),
                'created_at': order.created_at
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting order status {order_id}: {e}")
            return None
    
    def get_orders(self, status=None, symbols=None) -> List[Dict]:
        """Get orders with optional filtering"""
        try:
            if not self.trading_client:
                return []
            
            # Import required enums
            from alpaca.trading.enums import QueryOrderStatus
            from alpaca.trading.requests import GetOrdersRequest
            
            # Build request parameters
            request_params = {}
            
            if status:
                request_params['status'] = status
            if symbols:
                request_params['symbols'] = symbols
            
            # Create request object if we have parameters
            if request_params:
                request = GetOrdersRequest(**request_params)
                orders = self.trading_client.get_orders(filter=request)
            else:
                orders = self.trading_client.get_orders()
            
            # Convert to simplified format
            return [
                {
                    'id': order.id,
                    'symbol': order.symbol,
                    'side': order.side.value.lower(),
                    'qty': float(order.qty),
                    'status': order.status.value,
                    'order_type': order.order_type.value,
                    'created_at': order.created_at,
                    'filled_qty': float(order.filled_qty) if order.filled_qty else 0.0,
                    'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else 0.0
                }
                for order in orders
            ]
            
        except Exception as e:
            self.logger.error(f"❌ Error getting orders: {e}")
            return []
    
    def get_positions(self) -> List[Dict]:
        """Get all positions"""
        try:
            if not self.trading_client:
                return []
            
            positions = self.trading_client.get_all_positions()
            return [
                {
                    'symbol': pos.symbol,
                    'qty': float(pos.qty),  # Use float to handle decimal positions
                    'side': 'long' if float(pos.qty) > 0 else 'short',
                    'market_value': float(pos.market_value),
                    'avg_entry_price': float(pos.avg_entry_price),
                    'unrealized_pl': float(pos.unrealized_pl),
                    'unrealized_plpc': float(pos.unrealized_plpc)
                }
                for pos in positions
            ]
            
        except Exception as e:
            self.logger.error(f"❌ Error getting positions: {e}")
            return []
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get position for specific symbol"""
        try:
            if not self.trading_client:
                return None
            
            position = self.trading_client.get_open_position(symbol)
            return {
                'symbol': position.symbol,
                'qty': float(position.qty),  # Use float to handle decimal positions
                'side': 'long' if float(position.qty) > 0 else 'short',
                'market_value': float(position.market_value),
                'avg_entry_price': float(position.avg_entry_price),
                'unrealized_pl': float(position.unrealized_pl),
                'unrealized_plpc': float(position.unrealized_plpc)
            }
            
        except Exception as e:
            # Position not found is normal
            if "position does not exist" in str(e).lower():
                return None
            self.logger.error(f"❌ Error getting position for {symbol}: {e}")
            return None

if __name__ == "__main__":
    print("🔗 Alpaca Trader Test")
    print("=" * 30)
    
    trader = AlpacaTrader()
    
    if trader.is_connected():
        print("✅ Connected to Alpaca")
        
        # Test account info
        account = trader.get_account_info_simple()
        if account:
            print(f"💰 Portfolio Value: ${account['portfolio_value']:,.2f}")
            print(f"💵 Buying Power: ${account['buying_power']:,.2f}")
        
        # Test positions
        positions = trader.get_positions()
        print(f"📊 Open Positions: {len(positions)}")
        
    else:
        print("❌ Not connected to Alpaca")
