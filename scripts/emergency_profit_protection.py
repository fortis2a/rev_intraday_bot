#!/usr/bin/env python3
"""
Emergency Profit Protection System
Protects unrealized profits for both long and short positions
"""

import os
import sys
import logging
from datetime import datetime
import alpaca_trade_api as tradeapi
from stock_specific_config import get_stock_thresholds

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config

class EmergencyProfitProtection:
    def __init__(self):
        self.api = tradeapi.REST(
            config['ALPACA_API_KEY'],
            config['ALPACA_SECRET_KEY'],
            config['ALPACA_BASE_URL'],
            api_version='v2'
        )
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logger = logging.getLogger('profit_protection')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger

    def get_current_positions(self):
        """Get all current positions from Alpaca"""
        try:
            positions = self.api.list_positions()
            self.logger.info(f"Found {len(positions)} current positions")
            return positions
        except Exception as e:
            self.logger.error(f"Error fetching positions: {e}")
            return []

    def calculate_protection_levels(self, position):
        """Calculate profit protection levels for a position"""
        symbol = position.symbol
        side = position.side
        entry_price = float(position.avg_entry_price)
        current_price = float(position.market_value) / float(position.qty)
        unrealized_pl = float(position.unrealized_pl)
        
        # Get stock-specific thresholds
        thresholds = get_stock_thresholds(symbol)
        
        protection_levels = {
            'symbol': symbol,
            'side': side,
            'entry_price': entry_price,
            'current_price': current_price,
            'unrealized_pl': unrealized_pl,
            'qty': abs(float(position.qty))
        }
        
        if side == 'long':
            # For LONG positions - protect profits from downward moves
            profit_pct = (current_price - entry_price) / entry_price
            
            # Trailing stop: Lock in 75% of current profit
            trailing_stop_price = entry_price + (profit_pct * 0.75 * entry_price)
            
            # Take profit at stock-specific target
            take_profit_price = entry_price * (1 + thresholds['take_profit_pct'])
            
            protection_levels.update({
                'profit_pct': profit_pct * 100,
                'trailing_stop_price': trailing_stop_price,
                'take_profit_price': take_profit_price,
                'protection_type': 'LONG_PROFIT_PROTECTION'
            })
            
        else:  # short position
            # For SHORT positions - protect profits from upward moves
            profit_pct = (entry_price - current_price) / entry_price
            
            # Trailing stop: Lock in 75% of current profit (stop above current price)
            trailing_stop_price = entry_price - (profit_pct * 0.75 * entry_price)
            
            # Take profit at stock-specific target (below entry)
            take_profit_price = entry_price * (1 - thresholds['take_profit_pct'])
            
            protection_levels.update({
                'profit_pct': profit_pct * 100,
                'trailing_stop_price': trailing_stop_price,
                'take_profit_price': take_profit_price,
                'protection_type': 'SHORT_PROFIT_PROTECTION'
            })
        
        return protection_levels

    def create_protection_orders(self, protection_levels):
        """Create protective orders for a position"""
        symbol = protection_levels['symbol']
        side = protection_levels['side']
        qty = protection_levels['qty']
        
        orders_created = []
        
        try:
            # Cancel any existing orders for this symbol
            existing_orders = self.api.list_orders(status='open', symbols=symbol)
            for order in existing_orders:
                self.api.cancel_order(order.id)
                self.logger.info(f"[{symbol}] Cancelled existing order: {order.id}")
            
            if side == 'long':
                # Create trailing stop for long position
                trailing_order = self.api.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side='sell',
                    type='trailing_stop',
                    trail_price=round(protection_levels['entry_price'] * 0.005, 2),  # 0.5% trail
                    time_in_force='gtc'
                )
                orders_created.append(('trailing_stop', trailing_order.id))
                
                # Create take profit order
                take_profit_order = self.api.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side='sell',
                    type='limit',
                    limit_price=round(protection_levels['take_profit_price'], 2),
                    time_in_force='gtc'
                )
                orders_created.append(('take_profit', take_profit_order.id))
                
            else:  # short position
                # Create trailing stop for short position (buy to cover)
                trailing_order = self.api.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side='buy',
                    type='trailing_stop',
                    trail_price=round(protection_levels['entry_price'] * 0.005, 2),  # 0.5% trail
                    time_in_force='gtc'
                )
                orders_created.append(('trailing_stop', trailing_order.id))
                
                # Create take profit order (buy to cover)
                take_profit_order = self.api.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side='buy',
                    type='limit',
                    limit_price=round(protection_levels['take_profit_price'], 2),
                    time_in_force='gtc'
                )
                orders_created.append(('take_profit', take_profit_order.id))
            
            self.logger.info(f"[{symbol}] Created {len(orders_created)} protection orders")
            return orders_created
            
        except Exception as e:
            self.logger.error(f"[{symbol}] Failed to create protection orders: {e}")
            return []

    def protect_all_positions(self):
        """Main function to protect all profitable positions"""
        self.logger.info("🚀 STARTING EMERGENCY PROFIT PROTECTION")
        
        positions = self.get_current_positions()
        if not positions:
            self.logger.info("No positions found to protect")
            return
        
        protection_summary = []
        
        for position in positions:
            if float(position.unrealized_pl) > 0:  # Only protect profitable positions
                self.logger.info(f"\n📈 PROTECTING PROFITABLE POSITION: {position.symbol}")
                
                protection_levels = self.calculate_protection_levels(position)
                
                self.logger.info(f"[{position.symbol}] Side: {protection_levels['side'].upper()}")
                self.logger.info(f"[{position.symbol}] Entry: ${protection_levels['entry_price']:.2f}")
                self.logger.info(f"[{position.symbol}] Current: ${protection_levels['current_price']:.2f}")
                self.logger.info(f"[{position.symbol}] Profit: {protection_levels['profit_pct']:.2f}%")
                self.logger.info(f"[{position.symbol}] Unrealized P&L: ${protection_levels['unrealized_pl']:.2f}")
                
                orders = self.create_protection_orders(protection_levels)
                
                protection_summary.append({
                    'symbol': position.symbol,
                    'side': protection_levels['side'],
                    'profit_pct': protection_levels['profit_pct'],
                    'unrealized_pl': protection_levels['unrealized_pl'],
                    'orders_created': len(orders),
                    'protection_active': len(orders) > 0
                })
                
                self.logger.info(f"[{position.symbol}] ✅ Protection {'ACTIVE' if orders else 'FAILED'}")
        
        # Summary report
        self.logger.info(f"\n🎯 PROFIT PROTECTION SUMMARY")
        self.logger.info(f"{'='*50}")
        
        total_protected = sum(1 for p in protection_summary if p['protection_active'])
        total_profit = sum(p['unrealized_pl'] for p in protection_summary)
        
        for summary in protection_summary:
            status = "✅ PROTECTED" if summary['protection_active'] else "❌ FAILED"
            self.logger.info(f"{summary['symbol']} ({summary['side'].upper()}): "
                           f"{summary['profit_pct']:+.2f}% (${summary['unrealized_pl']:+.2f}) - {status}")
        
        self.logger.info(f"{'='*50}")
        self.logger.info(f"Positions Protected: {total_protected}/{len(protection_summary)}")
        self.logger.info(f"Total Unrealized Profit: ${total_profit:+.2f}")
        self.logger.info(f"🛡️  PROFIT PROTECTION {'COMPLETE' if total_protected == len(protection_summary) else 'PARTIAL'}")

if __name__ == "__main__":
    protector = EmergencyProfitProtection()
    protector.protect_all_positions()
