"""
Signal types for trading system
"""
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ScalpingSignal:
    """Represents a scalping trading signal"""
    symbol: str
    signal_type: str  # "BUY" or "SELL"
    strategy: str
    confidence: float
    entry_price: float
    stop_loss: float
    profit_target: float
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary"""
        return {
            'symbol': self.symbol,
            'signal_type': self.signal_type,
            'strategy': self.strategy,
            'confidence': self.confidence,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'profit_target': self.profit_target,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'metadata': self.metadata
        }
    
    def __str__(self) -> str:
        return f"{self.signal_type} {self.symbol} @ ${self.entry_price:.2f} ({self.strategy}, {self.confidence:.1%})"