#!/usr/bin/env python3
"""
Trailing Stop Manager
Handles dynamic stop loss adjustments to protect profits
"""

import time
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config import config
from utils.logger import setup_logger
from utils.price_utils import round_to_cent, calculate_trailing_stop_price, validate_price_precision

@dataclass
class TrailingStopPosition:
    """Data class for tracking trailing stop positions"""
    symbol: str
    entry_price: float
    entry_time: datetime
    quantity: int
    side: str  # 'long' or 'short'
    current_price: float
    highest_price: float  # For long positions
    lowest_price: float   # For short positions
    trailing_stop_price: float
    initial_stop_price: float
    is_trailing_active: bool
    last_update_time: datetime
    profit_pct: float
    unrealized_pnl: float

class TrailingStopManager:
    """Manages trailing stop functionality for all positions"""
    
    def __init__(self, order_manager):
        self.logger = setup_logger("trailing_stop_manager")
        self.order_manager = order_manager
        self.active_positions: Dict[str, TrailingStopPosition] = {}
        self.stop_orders: Dict[str, str] = {}  # symbol -> stop_order_id
        self.logger.info("Trailing Stop Manager initialized")
        
        # Log configuration
        if config['TRAILING_STOP_ENABLED']:
            self.logger.info("Trailing stops ENABLED")
            self.logger.info(f"Trailing distance: {config['TRAILING_STOP_PCT']:.1%}")
            self.logger.info(f"Activation threshold: {config['TRAILING_STOP_ACTIVATION']:.1%}")
            self.logger.info(f"Minimum move: {config['TRAILING_STOP_MIN_MOVE']:.1%}")
        else:
            self.logger.info("Trailing stops DISABLED")
    
    def add_position(self, symbol: str, entry_price: float, quantity: int, 
                    side: str = 'long', initial_stop_price: float = None, custom_thresholds: dict = None):
        """Add a new position to trailing stop tracking with optional custom thresholds"""
        try:
            if not config['TRAILING_STOP_ENABLED']:
                self.logger.debug(f"[{symbol}] Trailing stops disabled - using fixed stop only")
                return
            
            # Use custom thresholds if provided, otherwise fall back to config defaults
            if custom_thresholds:
                trailing_pct = custom_thresholds.get('trailing_distance_pct', config['TRAILING_STOP_PCT'])
                activation_pct = custom_thresholds.get('trailing_activation_pct', config['TRAILING_STOP_ACTIVATION'])
                stop_loss_pct = custom_thresholds.get('stop_loss_pct', config['STOP_LOSS_PCT'])
                
                self.logger.info(f"[{symbol}] 🎯 Using custom thresholds:")
                self.logger.info(f"[{symbol}] 📊 Trailing distance: {trailing_pct:.1%}")
                self.logger.info(f"[{symbol}] 🚀 Activation threshold: {activation_pct:.1%}")
                self.logger.info(f"[{symbol}] 🛡️  Stop loss: {stop_loss_pct:.1%}")
            else:
                trailing_pct = config['TRAILING_STOP_PCT']
                activation_pct = config['TRAILING_STOP_ACTIVATION']
                stop_loss_pct = config['STOP_LOSS_PCT']
            
            if initial_stop_price is None:
                initial_stop_price = round_to_cent(entry_price * (1 - stop_loss_pct))
            
            position = TrailingStopPosition(
                symbol=symbol,
                entry_price=entry_price,
                entry_time=datetime.now(),
                quantity=quantity,
                side=side,
                current_price=entry_price,
                highest_price=entry_price,
                lowest_price=entry_price,
                trailing_stop_price=initial_stop_price,
                initial_stop_price=initial_stop_price,
                is_trailing_active=False,
                last_update_time=datetime.now(),
                profit_pct=0.0,
                unrealized_pnl=0.0
            )
            
            # Store custom thresholds with position for later use
            if custom_thresholds:
                position.custom_thresholds = custom_thresholds
            
            self.active_positions[symbol] = position
            self.logger.info(f"[{symbol}] 📍 Position added to trailing stop tracking")
            self.logger.info(f"[{symbol}] 💰 Entry: ${entry_price:.2f}, Initial Stop: ${initial_stop_price:.2f}")
            
        except Exception as e:
            self.logger.error(f"[{symbol}] ❌ Failed to add position: {e}")
    
    def update_position_price(self, symbol: str, current_price: float) -> Optional[Dict]:
        """Update position with current price and adjust trailing stop if needed"""
        try:
            if symbol not in self.active_positions:
                return None
            
            position = self.active_positions[symbol]
            position.current_price = current_price
            position.last_update_time = datetime.now()
            
            # Get thresholds (custom or default)
            if hasattr(position, 'custom_thresholds') and position.custom_thresholds:
                trailing_pct = position.custom_thresholds.get('trailing_distance_pct', config['TRAILING_STOP_PCT'])
                activation_pct = position.custom_thresholds.get('trailing_activation_pct', config['TRAILING_STOP_ACTIVATION'])
                min_move_pct = position.custom_thresholds.get('min_move_pct', config['TRAILING_STOP_MIN_MOVE'])
            else:
                trailing_pct = config['TRAILING_STOP_PCT']
                activation_pct = config['TRAILING_STOP_ACTIVATION']
                min_move_pct = config['TRAILING_STOP_MIN_MOVE']
            
            # Calculate profit metrics
            if position.side == 'long':
                position.profit_pct = (current_price - position.entry_price) / position.entry_price
                position.unrealized_pnl = (current_price - position.entry_price) * position.quantity
                
                # Update highest price seen
                if current_price > position.highest_price:
                    position.highest_price = current_price
                
                # Check if trailing should activate using custom thresholds
                activation_threshold = position.entry_price * (1 + activation_pct)
                if not position.is_trailing_active and current_price >= activation_threshold:
                    position.is_trailing_active = True
                    self.logger.info(f"[{symbol}] 🚀 Trailing stop ACTIVATED at ${current_price:.2f} (+{position.profit_pct:.1%})")
                    self.logger.info(f"[{symbol}] 🎯 Using custom activation: {activation_pct:.1%}")
                
                # Adjust trailing stop if active using custom distance
                if position.is_trailing_active:
                    new_trailing_stop = calculate_trailing_stop_price(position.highest_price, trailing_pct)
                    
                    # Validate price precision
                    if not validate_price_precision(new_trailing_stop, f"{symbol} trailing_stop"):
                        self.logger.warning(f"[{symbol}] Trailing stop precision issue: {new_trailing_stop}")
                        new_trailing_stop = round_to_cent(new_trailing_stop)
                    
                    # Only move stop up (never down)
                    if new_trailing_stop > position.trailing_stop_price:
                        # Check minimum move threshold
                        move_pct = (new_trailing_stop - position.trailing_stop_price) / position.trailing_stop_price
                        if move_pct >= min_move_pct:
                            old_stop = position.trailing_stop_price
                            position.trailing_stop_price = new_trailing_stop
                            
                            self.logger.info(f"[{symbol}] 📈 Trailing stop adjusted: ${old_stop:.2f} → ${new_trailing_stop:.2f}")
                            self.logger.info(f"[{symbol}] 🎯 Custom distance: {trailing_pct:.1%}")
                            self.logger.info(f"[{symbol}] 💎 Protected profit: {((new_trailing_stop - position.entry_price) / position.entry_price):.1%}")
                            
                            # Return update info for order modification
                            return {
                                'symbol': symbol,
                                'action': 'update_stop',
                                'new_stop_price': new_trailing_stop,
                                'old_stop_price': old_stop,
                                'profit_protected': ((new_trailing_stop - position.entry_price) / position.entry_price),
                                'current_profit': position.profit_pct
                            }
            
            return None
            
        except Exception as e:
            self.logger.error(f"[{symbol}] ❌ Failed to update position: {e}")
            return None
    
    def check_stop_triggered(self, symbol: str, current_price: float) -> bool:
        """Check if trailing stop has been triggered"""
        try:
            if symbol not in self.active_positions:
                return False
            
            position = self.active_positions[symbol]
            
            if position.side == 'long' and current_price <= position.trailing_stop_price:
                self.logger.warning(f"[{symbol}] 🛑 TRAILING STOP TRIGGERED!")
                self.logger.warning(f"[{symbol}] Price: ${current_price:.2f} ≤ Stop: ${position.trailing_stop_price:.2f}")
                self.logger.warning(f"[{symbol}] Final P&L: {position.profit_pct:.1%} (${position.unrealized_pnl:.2f})")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"[{symbol}] ❌ Failed to check stop trigger: {e}")
            return False
    
    def remove_position(self, symbol: str, reason: str = "Position closed"):
        """Remove position from trailing stop tracking"""
        try:
            if symbol in self.active_positions:
                position = self.active_positions[symbol]
                self.logger.info(f"[{symbol}] 🏁 Position removed from trailing stop tracking")
                self.logger.info(f"[{symbol}] Reason: {reason}")
                self.logger.info(f"[{symbol}] Final profit: {position.profit_pct:.1%} (${position.unrealized_pnl:.2f})")
                
                del self.active_positions[symbol]
                
                if symbol in self.stop_orders:
                    del self.stop_orders[symbol]
                    
        except Exception as e:
            self.logger.error(f"[{symbol}] ❌ Failed to remove position: {e}")
    
    def get_position_status(self, symbol: str) -> Optional[Dict]:
        """Get current status of a trailing stop position"""
        try:
            if symbol not in self.active_positions:
                return None
            
            position = self.active_positions[symbol]
            
            return {
                'symbol': symbol,
                'entry_price': position.entry_price,
                'current_price': position.current_price,
                'highest_price': position.highest_price,
                'trailing_stop_price': position.trailing_stop_price,
                'is_trailing_active': position.is_trailing_active,
                'profit_pct': position.profit_pct,
                'unrealized_pnl': position.unrealized_pnl,
                'profit_protected_pct': ((position.trailing_stop_price - position.entry_price) / position.entry_price) if position.is_trailing_active else 0.0,
                'distance_to_stop': ((position.current_price - position.trailing_stop_price) / position.current_price) if position.side == 'long' else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"[{symbol}] ❌ Failed to get position status: {e}")
            return None
    
    def get_all_positions_status(self) -> List[Dict]:
        """Get status of all active trailing stop positions"""
        try:
            statuses = []
            for symbol in self.active_positions:
                status = self.get_position_status(symbol)
                if status:
                    statuses.append(status)
            return statuses
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get all positions status: {e}")
            return []
    
    def log_position_summary(self):
        """Log summary of all active trailing stop positions"""
        try:
            if not self.active_positions:
                self.logger.info("📊 No active trailing stop positions")
                return
            
            self.logger.info("=" * 60)
            self.logger.info("📊 TRAILING STOP POSITIONS SUMMARY")
            self.logger.info("=" * 60)
            
            for symbol, position in self.active_positions.items():
                status = "🚀 TRAILING" if position.is_trailing_active else "⏳ WAITING"
                profit_protected = ((position.trailing_stop_price - position.entry_price) / position.entry_price) if position.is_trailing_active else 0.0
                
                self.logger.info(f"[{symbol}] {status}")
                self.logger.info(f"  💰 Entry: ${position.entry_price:.2f} | Current: ${position.current_price:.2f}")
                self.logger.info(f"  📈 Profit: {position.profit_pct:.1%} (${position.unrealized_pnl:.2f})")
                self.logger.info(f"  🛡️  Stop: ${position.trailing_stop_price:.2f} | Protected: {profit_protected:.1%}")
                self.logger.info(f"  🎯 High: ${position.highest_price:.2f}")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to log position summary: {e}")
