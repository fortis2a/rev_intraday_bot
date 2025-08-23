#!/usr/bin/env python3
"""
Trade Record
Data class for tracking trading performance and analytics
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TradeRecord:
    """Records trade details for performance tracking and analysis"""

    # Required fields for initialization (matching intraday_engine.py usage)
    symbol: str
    strategy: str
    side: str
    entry_time: datetime
    entry_price: float
    stop_loss: float
    profit_target: float
    position_size: int
    confidence: float

    # Optional market data fields
    spread_pct: Optional[float] = None
    volume: Optional[int] = None
    volume_ratio: Optional[float] = None

    # 🔍 ENHANCED: Decision context fields for trade analysis
    signal_reason: Optional[str] = None
    indicators_at_entry: Optional[dict] = None
    confidence_breakdown: Optional[dict] = None
    market_regime: Optional[str] = None
    atr_percentile: Optional[float] = None
    relative_volume: Optional[float] = None

    # Strategy-specific decision details
    strategy_signals: Optional[dict] = None
    alternative_signals: Optional[list] = None
    risk_assessment: Optional[dict] = None

    # Exit information (set when trade closes)
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None

    # Performance metrics (calculated in finalize method)
    realized_pnl: Optional[float] = None
    realized_pct: Optional[float] = None
    r_multiple: Optional[float] = None
    hold_time_s: Optional[float] = None

    # MAE/MFE tracking (Maximum Adverse/Favorable Excursion)
    mae_pct: Optional[float] = None
    mfe_pct: Optional[float] = None
    mae_r: Optional[float] = None
    mfe_r: Optional[float] = None

    def finalize(self, exit_price: float, exit_reason: str, side: str):
        """Finalize trade with exit information - matches intraday_engine.py signature"""
        self.exit_price = exit_price
        self.exit_reason = exit_reason
        self.exit_time = datetime.utcnow()

        # Calculate realized P&L
        if side.upper() == "BUY":
            self.realized_pnl = (exit_price - self.entry_price) * self.position_size
            self.realized_pct = (exit_price - self.entry_price) / self.entry_price
        else:  # SELL
            self.realized_pnl = (self.entry_price - exit_price) * self.position_size
            self.realized_pct = (self.entry_price - exit_price) / self.entry_price

        # Calculate R-multiple
        risk = abs(self.entry_price - self.stop_loss)
        if risk > 0:
            self.r_multiple = abs(self.realized_pnl) / (risk * self.position_size)
            if self.realized_pnl < 0:
                self.r_multiple = -self.r_multiple

        # Calculate hold time
        if self.entry_time:
            self.hold_time_s = (self.exit_time - self.entry_time).total_seconds()

    def to_analysis_dict(self) -> dict:
        """Convert to dictionary optimized for trade analysis"""
        return {
            # Basic trade info
            "symbol": self.symbol,
            "strategy": self.strategy,
            "side": self.side,
            "entry_time": self.entry_time.isoformat() if self.entry_time else None,
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "position_size": self.position_size,
            # Performance metrics
            "realized_pnl": self.realized_pnl,
            "realized_pct": self.realized_pct,
            "r_multiple": self.r_multiple,
            "hold_time_s": self.hold_time_s,
            "mae_pct": self.mae_pct,
            "mfe_pct": self.mfe_pct,
            # 🔍 Decision analysis data
            "confidence": self.confidence,
            "signal_reason": self.signal_reason,
            "indicators_at_entry": self.indicators_at_entry,
            "confidence_breakdown": self.confidence_breakdown,
            "market_regime": self.market_regime,
            "atr_percentile": self.atr_percentile,
            "relative_volume": self.relative_volume,
            "strategy_signals": self.strategy_signals,
            "risk_assessment": self.risk_assessment,
            # Market context
            "spread_pct": self.spread_pct,
            "volume": self.volume,
            "volume_ratio": self.volume_ratio,
            "exit_reason": self.exit_reason,
        }

    def __str__(self):
        """String representation"""
        status = "CLOSED" if self.exit_price else "OPEN"
        pnl_str = f"${self.realized_pnl:.2f}" if self.realized_pnl else "N/A"
        return f"TradeRecord({self.symbol} {self.side} {self.position_size}@${self.entry_price:.2f} {status} P&L:{pnl_str})"
