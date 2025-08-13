#!/usr/bin/env python3
"""Quick sanity checks for strategies to ensure they return well-formed signals.
Run manually: python -m tests.test_strategy_quick_checks
"""
import pandas as pd
from datetime import datetime, timedelta
from strategies.momentum_scalp import MomentumScalpStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.vwap_bounce import VWAPBounceStrategy
from utils.signal_types import ScalpingSignal

# Generate synthetic bar data with required columns

def make_dummy_data(rows=40, start_price=100.0):
    data = []
    price = start_price
    for i in range(rows):
        open_p = price
        # small random walk deterministic
        price += (0.05 if i % 5 == 0 else -0.03 if i % 7 == 0 else 0.01)
        high = max(open_p, price) + 0.05
        low = min(open_p, price) - 0.05
        close = price
        volume = 10000 + (i * 50)
        ts = datetime.utcnow() - timedelta(minutes=rows - i)
        data.append({
            'open': open_p,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume,
            # basic indicators placeholders
            'rsi': 50,
            'ema_5': close * 0.999,
            'ema_13': close * 1.001,
            'vwap': close * 1.0005,
            'bb_upper': close * 1.01,
            'bb_lower': close * 0.99,
            'bb_mid': close,
            'price_change_5': 0.001,
        })
    return pd.DataFrame(data)


def validate_signals(name, signals):
    for s in signals:
        assert isinstance(s, ScalpingSignal), f"{name}: Signal not instance of ScalpingSignal"
        assert s.symbol, f"{name}: Missing symbol"
        assert s.signal_type in ("BUY", "SELL"), f"{name}: Invalid signal_type"
        assert 0 < s.entry_price < 10000, f"{name}: Unreasonable entry price {s.entry_price}"
        assert s.stop_loss > 0 and s.profit_target > 0, f"{name}: Non-positive stop/target"
        assert s.confidence >= 0, f"{name}: Negative confidence"


def run_quick_checks():
    df = make_dummy_data()
    strategies = [
        ("momentum", MomentumScalpStrategy()),
        ("mean_reversion", MeanReversionStrategy()),
        ("vwap_bounce", VWAPBounceStrategy()),
    ]
    summary = {}
    for name, strat in strategies:
        sigs = strat.generate_signals("TEST", df)
        validate_signals(name, sigs)
        summary[name] = len(sigs)
    return summary

if __name__ == "__main__":
    result = run_quick_checks()
    print("Strategy signal counts:", result)
