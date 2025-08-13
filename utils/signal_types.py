#!/usr/bin/env python3
"""Unified signal data structures used across strategies and engine."""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

@dataclass
class IntradaySignal:
    symbol: str
    signal_type: str   # 'BUY' or 'SELL'
    strategy: str
    confidence: float
    entry_price: float
    stop_loss: float
    profit_target: float
    timestamp: datetime
    metadata: Optional[Dict] = None

    def as_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'type': self.signal_type,
            'strategy': self.strategy,
            'confidence': self.confidence,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'profit_target': self.profit_target,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata or {}
        }

# Backward compatibility alias
ScalpingSignal = IntradaySignal
