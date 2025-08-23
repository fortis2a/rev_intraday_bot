#!/usr/bin/env python3
"""
Risk Manager
Handles position sizing, risk limits, and exposure management for intraday trading
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import config
from utils.logger import setup_logger


class RiskManager:
    """Manages risk parameters and position limits for intraday trading"""

    def __init__(self):
        self.logger = setup_logger("risk_manager")

        # Risk tracking
        self.account_equity = 100000.0  # Default, will be updated from broker
        self.open_positions_count = 0
        self.total_long_exposure = 0.0
        self.total_short_exposure = 0.0
        self.daily_pnl = 0.0
        self.positions_tracker = {}  # symbol -> position info

        self.logger.info("🛡️ Risk Manager initialized")
        self.logger.info(f"📊 Max positions: {config.get('MAX_OPEN_POSITIONS', 5)}")
        self.logger.info(
            f"💰 Max position size: ${config.get('MAX_POSITION_SIZE', 5000)}"
        )

    def sync_position_count_with_broker(self, order_manager):
        """Sync position counts with broker data"""
        try:
            # Get current positions from broker
            positions = order_manager.get_current_positions_qty()
            self.open_positions_count = len(positions)

            # Calculate total exposure
            self.total_long_exposure = 0.0
            self.total_short_exposure = 0.0

            for symbol, qty in positions.items():
                if qty > 0:
                    # Get current price for exposure calculation
                    try:
                        current_price = order_manager.data_manager.get_current_price(
                            symbol
                        )
                        if current_price:
                            exposure = qty * current_price
                            self.total_long_exposure += exposure
                    except Exception as e:
                        self.logger.warning(
                            f"Could not calculate exposure for {symbol}: {e}"
                        )

            # Update account equity
            try:
                account_info = order_manager.data_manager.api.get_account()
                self.account_equity = float(account_info.equity)
            except Exception as e:
                self.logger.warning(f"Could not update account equity: {e}")

            self.logger.info(
                f"📊 Synced with broker - Positions: {self.open_positions_count}, "
                f"Long exposure: ${self.total_long_exposure:.2f}, "
                f"Account equity: ${self.account_equity:.2f}"
            )

        except Exception as e:
            self.logger.error(f"Failed to sync with broker: {e}")

    def can_open_position(
        self, symbol: str, entry_price: float, signal_type: str
    ) -> bool:
        """Check if we can open a new position based on risk limits"""
        try:
            # Check position count limit
            max_positions = config.get("MAX_OPEN_POSITIONS", 5)
            if self.open_positions_count >= max_positions:
                self.logger.warning(
                    f"[{symbol}] Position limit reached ({self.open_positions_count}/{max_positions})"
                )
                return False

            # Check if we already have a position in this symbol
            if symbol in self.positions_tracker:
                self.logger.warning(f"[{symbol}] Already have position in this symbol")
                return False

            # Check daily loss limit
            daily_loss_limit = config.get("DAILY_LOSS_LIMIT", 1000)
            if self.daily_pnl <= -daily_loss_limit:
                self.logger.warning(
                    f"[{symbol}] Daily loss limit reached (${self.daily_pnl:.2f})"
                )
                return False

            # Check total exposure limit
            max_total_exposure = self.account_equity * config.get(
                "MAX_TOTAL_EXPOSURE_PCT", 0.8
            )
            current_exposure = self.total_long_exposure + self.total_short_exposure

            position_value = (
                self.calculate_position_size(symbol, entry_price, self.account_equity)
                * entry_price
            )

            if current_exposure + position_value > max_total_exposure:
                self.logger.warning(
                    f"[{symbol}] Total exposure limit would be exceeded"
                )
                return False

            return True

        except Exception as e:
            self.logger.error(f"[{symbol}] Error checking position limits: {e}")
            return False

    def calculate_position_size(
        self, symbol: str, price: float, account_equity: float
    ) -> int:
        """Calculate appropriate position size based on risk parameters"""
        try:
            # Use configured max position size or percentage of equity
            max_position_value = min(
                config.get("MAX_POSITION_SIZE", 5000),
                account_equity * config.get("MAX_POSITION_PCT", 0.1),
            )

            # Calculate shares
            shares = int(max_position_value / price)

            # Minimum viable position
            if shares < 1:
                shares = 1

            self.logger.debug(
                f"[{symbol}] Position size: {shares} shares (${shares * price:.2f})"
            )
            return shares

        except Exception as e:
            self.logger.error(f"[{symbol}] Error calculating position size: {e}")
            return 1

    def track_position_opened(
        self, symbol: str, signal_type: str, quantity: int, entry_price: float
    ):
        """Track when a position is opened"""
        try:
            position_value = quantity * entry_price

            self.positions_tracker[symbol] = {
                "signal_type": signal_type,
                "quantity": quantity,
                "entry_price": entry_price,
                "entry_time": datetime.now(),
                "position_value": position_value,
            }

            self.open_positions_count += 1

            if signal_type in ["buy", "long"]:
                self.total_long_exposure += position_value
            else:
                self.total_short_exposure += position_value

            self.logger.info(
                f"[{symbol}] Position opened - {signal_type.upper()} {quantity} @ ${entry_price:.2f}"
            )
            self.logger.info(
                f"📊 Total positions: {self.open_positions_count}, "
                f"Long exposure: ${self.total_long_exposure:.2f}"
            )

        except Exception as e:
            self.logger.error(f"[{symbol}] Error tracking position opened: {e}")

    def track_position_closed(
        self, symbol: str, quantity: int, exit_price: float, pnl: float
    ):
        """Track when a position is closed"""
        try:
            if symbol in self.positions_tracker:
                position_info = self.positions_tracker[symbol]
                position_value = position_info["position_value"]
                signal_type = position_info["signal_type"]

                # Update exposure
                if signal_type in ["buy", "long"]:
                    self.total_long_exposure = max(
                        0, self.total_long_exposure - position_value
                    )
                else:
                    self.total_short_exposure = max(
                        0, self.total_short_exposure - position_value
                    )

                # Update daily P&L
                self.daily_pnl += pnl

                # Remove from tracker
                del self.positions_tracker[symbol]
                self.open_positions_count = max(0, self.open_positions_count - 1)

                self.logger.info(
                    f"[{symbol}] Position closed - {quantity} @ ${exit_price:.2f}, "
                    f"P&L: ${pnl:.2f}"
                )
                self.logger.info(
                    f"📊 Total positions: {self.open_positions_count}, "
                    f"Daily P&L: ${self.daily_pnl:.2f}"
                )

        except Exception as e:
            self.logger.error(f"[{symbol}] Error tracking position closed: {e}")

    def get_risk_summary(self) -> Dict:
        """Get current risk summary"""
        return {
            "account_equity": self.account_equity,
            "open_positions": self.open_positions_count,
            "total_long_exposure": self.total_long_exposure,
            "total_short_exposure": self.total_short_exposure,
            "daily_pnl": self.daily_pnl,
            "exposure_pct": (
                (self.total_long_exposure + self.total_short_exposure)
                / self.account_equity
                if self.account_equity > 0
                else 0
            ),
            "positions": list(self.positions_tracker.keys()),
        }

    def reset_daily_tracking(self):
        """Reset daily tracking counters (call at market open)"""
        self.daily_pnl = 0.0
        self.logger.info("🔄 Daily risk tracking reset")
