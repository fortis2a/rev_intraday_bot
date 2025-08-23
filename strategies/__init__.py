"""
Strategy Module Initialization
Imports all available trading strategies for the intraday bot
"""

from .mean_reversion import (MeanReversionStrategy,
                             create_mean_reversion_strategy)
from .momentum_scalp import (MomentumScalpStrategy,
                             create_momentum_scalp_strategy)
from .vwap_bounce import VWAPBounceStrategy, create_vwap_bounce_strategy

# Backward compatibility aliases
MomentumStrategy = MomentumScalpStrategy
VWAPStrategy = VWAPBounceStrategy

__all__ = [
    "MeanReversionStrategy",
    "MomentumScalpStrategy",
    "VWAPBounceStrategy",
    "MomentumStrategy",  # Alias for backward compatibility
    "VWAPStrategy",  # Alias for backward compatibility
    "create_mean_reversion_strategy",
    "create_momentum_scalp_strategy",
    "create_vwap_bounce_strategy",
]
