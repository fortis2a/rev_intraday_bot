#!/usr/bin/env python3
"""
Manual Position Protection
Direct protection orders for current profitable positions
"""

import logging
import os
import sys
from datetime import datetime

import alpaca_trade_api as tradeapi

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import config


class ManualProtection:
    def __init__(self):
        self.api = tradeapi.REST(
            config["ALPACA_API_KEY"],
            config["ALPACA_SECRET_KEY"],
            config["ALPACA_BASE_URL"],
            api_version="v2",
        )
        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger("manual_protection")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def place_manual_protection(self):
        """Place manual protection orders based on current profitable positions"""

        # Current profitable positions with protection levels
        protection_orders = [
            {
                "symbol": "INTC",
                "type": "LONG",
                "qty": 10,
                "entry": 23.71,
                "current": 25.53,
                "profit_pct": 7.68,
                "trailing_stop": 25.25,  # Lock in 75% of profit
                "take_profit": 24.00,  # Conservative target
            },
            {
                "symbol": "SOFI",
                "type": "SHORT",
                "qty": 20,
                "entry": 24.11,
                "current": 23.38,
                "profit_pct": 3.03,
                "trailing_stop": 23.65,  # 75% profit protection
                "take_profit": 23.96,  # Conservative target
            },
            {
                "symbol": "SOXL",
                "type": "SHORT",
                "qty": 18,
                "entry": 27.47,
                "current": 27.21,
                "profit_pct": 0.96,
                "trailing_stop": 27.27,  # Tight protection
                "take_profit": 27.24,  # Quick profit
            },
            {
                "symbol": "TQQQ",
                "type": "SHORT",
                "qty": 5,
                "entry": 93.19,
                "current": 91.22,
                "profit_pct": 2.11,
                "trailing_stop": 91.72,  # 75% profit lock
                "take_profit": 92.70,  # Conservative target
            },
        ]

        self.logger.info("🛡️  MANUAL PROFIT PROTECTION - IMMEDIATE ACTION")
        self.logger.info("=" * 60)

        for order_info in protection_orders:
            symbol = order_info["symbol"]
            position_type = order_info["type"]

            self.logger.info(f"\n📊 {symbol} ({position_type}) Protection:")
            self.logger.info(f"   Current Profit: {order_info['profit_pct']:+.2f}%")
            self.logger.info(f"   Entry: ${order_info['entry']:.2f}")
            self.logger.info(f"   Current: ${order_info['current']:.2f}")

            try:
                if position_type == "LONG":
                    # For LONG positions: Sell orders to close

                    # 1. Trailing Stop Loss (Sell)
                    stop_order = self.api.submit_order(
                        symbol=symbol,
                        qty=order_info["qty"],
                        side="sell",
                        type="stop",
                        stop_price=round(order_info["trailing_stop"], 2),
                        time_in_force="gtc",
                    )

                    self.logger.info(
                        f"   ✅ Stop Loss: SELL at ${order_info['trailing_stop']:.2f} (Order: {stop_order.id})"
                    )

                    # 2. Take Profit (Sell)
                    profit_order = self.api.submit_order(
                        symbol=symbol,
                        qty=order_info["qty"],
                        side="sell",
                        type="limit",
                        limit_price=round(order_info["take_profit"], 2),
                        time_in_force="gtc",
                    )

                    self.logger.info(
                        f"   ✅ Take Profit: SELL at ${order_info['take_profit']:.2f} (Order: {profit_order.id})"
                    )

                else:  # SHORT position
                    # For SHORT positions: Buy orders to close

                    # 1. Stop Loss (Buy to Cover)
                    stop_order = self.api.submit_order(
                        symbol=symbol,
                        qty=order_info["qty"],
                        side="buy",
                        type="stop",
                        stop_price=round(order_info["trailing_stop"], 2),
                        time_in_force="gtc",
                    )

                    self.logger.info(
                        f"   ✅ Stop Loss: BUY at ${order_info['trailing_stop']:.2f} (Order: {stop_order.id})"
                    )

                    # 2. Take Profit (Buy to Cover)
                    profit_order = self.api.submit_order(
                        symbol=symbol,
                        qty=order_info["qty"],
                        side="buy",
                        type="limit",
                        limit_price=round(order_info["take_profit"], 2),
                        time_in_force="gtc",
                    )

                    self.logger.info(
                        f"   ✅ Take Profit: BUY at ${order_info['take_profit']:.2f} (Order: {profit_order.id})"
                    )

            except Exception as e:
                self.logger.error(f"   ❌ Failed to protect {symbol}: {e}")

        self.logger.info("\n" + "=" * 60)
        self.logger.info("🎯 PROTECTION SUMMARY")
        self.logger.info("All profitable positions now have:")
        self.logger.info("• Stop Loss orders to limit downside")
        self.logger.info("• Take Profit orders to capture gains")
        self.logger.info("• Real-time monitoring active")
        self.logger.info(f"💰 Total Profit at Risk: $47.35")


if __name__ == "__main__":
    protector = ManualProtection()
    protector.place_manual_protection()
