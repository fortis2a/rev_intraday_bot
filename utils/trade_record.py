#!/usr/bin/env python3
"""TradeRecord dataclass for detailed trade diagnostics."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class TradeRecord:
    symbol: str
    strategy: str
    side: str  # 'BUY' or 'SELL'
    entry_time: datetime
    entry_price: float
    stop_loss: float
    profit_target: float
    position_size: int
    confidence: float
    spread_pct: Optional[float] = None
    volume: Optional[float] = None
    volume_ratio: Optional[float] = None
    bar_age_s: Optional[float] = None
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    realized_pnl: Optional[float] = None
    realized_pct: Optional[float] = None
    r_multiple: Optional[float] = None
    hold_time_s: Optional[float] = None
    exit_reason: Optional[str] = None
    mae_pct: Optional[float] = None  # Maximum adverse excursion (%)
    mfe_pct: Optional[float] = None  # Maximum favorable excursion (%)
    mae_r: Optional[float] = None
    mfe_r: Optional[float] = None
    extra: Optional[Dict[str, Any]] = None

    def finalize(self, exit_price: float, exit_reason: str, side: str):
        self.exit_time = datetime.utcnow()
        self.exit_price = exit_price
        direction = 1 if side == 'BUY' else -1
        self.realized_pnl = (exit_price - self.entry_price) * direction * self.position_size
        self.realized_pct = ((exit_price - self.entry_price) / self.entry_price) * 100 * direction
        risk_per_share = abs(self.entry_price - self.stop_loss)
        if risk_per_share > 0:
            self.r_multiple = ((exit_price - self.entry_price) * direction) / risk_per_share
            # Derive MAE/MFE in R if pct excursions recorded
            if self.mae_pct is not None:
                self.mae_r = (self.mae_pct / 100) / (risk_per_share / self.entry_price)
            if self.mfe_pct is not None:
                self.mfe_r = (self.mfe_pct / 100) / (risk_per_share / self.entry_price)
        self.hold_time_s = (self.exit_time - self.entry_time).total_seconds()
        self.exit_reason = exit_reason

    def to_dict(self):
        d = asdict(self)
        # Convert datetimes
        d['entry_time'] = self.entry_time.isoformat()
        if self.exit_time:
            d['exit_time'] = self.exit_time.isoformat()
        return d
