# 🚀 Scalping Bot System

## 📊 **Overview**
Advanced algorithmic trading system for scalping operations with multi-strategy support, comprehensive risk management, and real-time execution through Alpaca Markets.

## ⚡ **Quick Start**
```bash
# Configure Python environment
python scalping_bot.py

# Run analysis on recent trades
python analysis/trading_analysis.py

# Validate system after updates
python tests/validate_bug_fixes.py
```

## 🎯 **Key Features**
- **Multi-Strategy Trading**: Momentum, Mean Reversion, VWAP Bounce
- **Advanced Risk Management**: Position limits, stop-loss, take-profit
- **Real-time Execution**: Alpaca Markets integration
- **Comprehensive Logging**: Detailed trade and system logs
- **Performance Analytics**: P&L tracking and strategy analysis

## 🔧 **Recent Updates** 
### **Critical Bug Fixes (July 28, 2025)**
- ✅ Fixed execution flaw where SELL signals became BUY orders
- ✅ Enhanced risk manager exception handling
- ✅ Added phantom position detection
- ✅ Increased short exposure limits to $1,500
- ✅ Improved order validation and monitoring

**Impact**: Fixed $859 QBTS loss that should have been profitable

## 📁 **Project Structure**
```
├── core/           # Trading engine components
├── strategies/     # Trading algorithms
├── analysis/       # Performance analysis tools
├── tests/          # Validation and testing
├── docs/           # Documentation and guides
├── reports/        # Trading reports
├── logs/           # System logs
└── config.py       # Configuration settings
```

## 🎮 **Usage**

### **Running the Bot**
```bash
python scalping_bot.py
```

### **Analyzing Performance**
```bash
# Generate comprehensive P&L report
python analysis/trading_analysis.py

# Analyze specific strategy performance  
python analysis/qbts_strategy_analysis.py
```

### **Testing & Validation**
```bash
# Validate recent bug fixes
python tests/validate_bug_fixes.py

# Check rule compliance
python analysis/rule_violation_analysis.py
```

### Test Suite Organization

The test suite is organized to keep actively maintained tests separate from historical/diagnostic scripts:

```
tests/
	test_*.py                # Active, fast unit/integration tests (run in CI)
	validate_bug_fixes.py    # Consolidated regression validation
	legacy/                  # Older one-off diagnostic or exploratory tests
```

Legacy tests are marked with the `@pytest.mark.legacy` marker (or reside in `tests/legacy/`). They are excluded from default runs via the `-m "not legacy"` filter configured in `pytest.ini`.

Run active tests (default):
```bash
pytest -q
```

Run including legacy tests:
```bash
pytest -m legacy -q              # only legacy
pytest -m "legacy or not legacy" # everything
```

Promote a legacy test back to active by moving it out of `tests/legacy/` and (optionally) removing the `@pytest.mark.legacy` decorator if present.


## ⚙️ **Configuration**
Key settings in `config.py`:
- **Position Limits**: $50-$800 per trade
- **Risk Management**: 2% account risk, 0.15% stop-loss
- **Exposure Limits**: $1,500 short exposure
- **Strategies**: All three strategies enabled

## 📈 **Performance Highlights**
Based on July 28, 2025 analysis:
- **RGTI Short Strategy**: +$1,136 profit
- **IONQ Short Strategy**: +$254 profit  
- **QBTS Execution**: Fixed critical bug causing losses

## 🚨 **Monitoring**
Watch for these log messages:
- `PHANTOM POSITION DETECTED` - Position validation alert
- `RISK LIMIT VIOLATION` - Risk management enforcement
- `EXECUTION_ERROR` - Order execution issues

## 📚 **Documentation**
- **[Bug Fix Summary](docs/BUG_FIX_SUMMARY.md)** - Critical fixes implemented
- **[Workspace Organization](docs/WORKSPACE_ORGANIZATION.md)** - Project structure
- **[Trading Baseline](reports/trading_analysis_baseline_2025-07-28.md)** - Performance baseline

## 🛠️ **Development**
- **Language**: Python 3.11+
- **Broker**: Alpaca Markets API
- **Dependencies**: pandas, numpy, alpaca-trade-api
- **Logging**: Structured logging with daily rotation

## ⚠️ **Important Notes**
1. **Test Mode**: Always test in paper trading before live deployment
2. **Risk Management**: System enforces strict position and exposure limits
3. **Monitoring**: Review logs daily for phantom position alerts
4. **Updates**: Validate all changes with test scripts before deployment

## 📊 Supported Timeframes

| Timeframe | Signal Delay | Max Hold Time | Best For |
|-----------|-------------|---------------|----------|
| 1Min | 5 seconds | 5 minutes | Ultra-fast scalping |
| 2Min | 10 seconds | 10 minutes | Balanced approach |
| 5Min | 30 seconds | 30 minutes | Swing scalping |

## 🚀 Quick Start

### Prerequisites
```bash
# Install required packages
pip install pandas numpy alpaca-py python-dotenv
```

### Environment Setup
Create a `.env` file in the parent directory:
```env
ALPACA_API_KEY=your_api_key
ALPACA_SECRET_KEY=your_secret_key
```

### Basic Usage

#### Test Strategies (Safe)
```bash
# Test strategies on AAPL
python scalping_bot.py --test AAPL

# Test with different timeframe
python scalping_bot.py --test TSLA --timeframe 5Min
```

#### Paper Trading
```bash
# Run paper trading (recommended first)
python scalping_bot.py --dry-run

# Paper trading with 2-minute timeframe
python scalping_bot.py --dry-run --timeframe 2Min
```

#### Live Trading (Advanced)
```bash
# Live trading (real money!)
python scalping_bot.py

# Validate environment only
python scalping_bot.py --validate-only
```

## ⚙️ Configuration

### Risk Settings (config.py)
```python
MAX_POSITION_SIZE = 1000        # Max shares per position
MAX_DAILY_LOSS = 500.0         # Stop trading if daily loss exceeds
MAX_OPEN_POSITIONS = 3         # Max concurrent positions
STOP_LOSS_PCT = 0.15           # 0.15% stop loss
PROFIT_TARGET_PCT = 0.30       # 0.30% profit target (2:1 ratio)
ACCOUNT_RISK_PCT = 1.0         # Risk 1% of account per trade
```

### Stock Selection Criteria
```python
MIN_VOLUME = 1000000           # Minimum daily volume
MIN_PRICE = 10.0              # Minimum stock price  
MAX_PRICE = 200.0             # Maximum stock price
MAX_SPREAD_PCT = 0.1          # Maximum bid-ask spread %
```

### Market Hours
```python
SCALP_START = "09:35"         # Start 5 min after open
SCALP_END = "15:55"           # Stop 5 min before close
LUNCH_BREAK_START = "12:00"   # Avoid lunch hour
LUNCH_BREAK_END = "13:00"
```

## 📈 Strategy Details

### 1. Momentum Scalping
**Triggers:**
- Price change ≥ 0.3% with volume spike (1.5x+)
- EMA alignment (5 > 13)
- RSI not overbought/oversold
- Price above/below VWAP

**Entry Types:**
- Bullish momentum breakouts
- Bearish momentum breakdowns
- Volume-confirmed price spikes

### 2. Mean Reversion
**Triggers:**
- Z-score ≥ 2 standard deviations from mean
- Bollinger Band touches
- RSI extreme levels with reversal signs
- VWAP distance reversion

**Entry Types:**
- Oversold bounces
- Overbought rejections
- Failed breakdown/breakout reversals

### 3. VWAP Bounce
**Triggers:**
- Price within 0.05% of VWAP
- Volume confirmation (1.2x+ average)
- Bounce confirmation patterns
- Support/resistance at VWAP

**Entry Types:**
- Direct VWAP bounces
- Pullback to VWAP after trend
- Failed VWAP breakdown/breakout

## 🛡️ Risk Management

### Position Sizing
- Dynamic position sizing based on stop loss distance
- Account risk percentage enforcement (default 1%)
- Maximum position value limits
- Minimum position value filters

### Stop Loss Management
- Automatic stop loss orders
- Trailing stops for profitable positions
- Time-based exits for stale positions
- Maximum hold time enforcement

### Portfolio Protection
- Daily loss limits with automatic shutdown
- Maximum concurrent positions
- Correlation monitoring
- Real-time P&L tracking

## 📊 Performance Monitoring

### Real-Time Metrics
- Daily P&L and trade count
- Win rate and profit factor
- Active positions and risk exposure
- Strategy performance breakdown

### Logging
- Comprehensive trade logging
- Error tracking and debugging
- Performance analytics
- Market condition analysis

## 🔧 File Structure

```
scalping-bot/
├── scalping_bot.py           # Main launcher
├── config.py                 # Configuration settings
├── core/
│   ├── scalping_engine.py    # Main trading engine
│   ├── risk_manager.py       # Risk management
│   ├── data_manager.py       # Market data handling
│   └── order_manager.py      # Order execution
├── strategies/
│   ├── momentum_scalp.py     # Momentum strategy
│   ├── mean_reversion.py     # Mean reversion strategy
│   └── vwap_bounce.py        # VWAP bounce strategy
├── utils/
│   └── logger.py             # Logging utilities
└── README.md                 # This file
```

## ⚠️ Important Warnings

### Risk Disclosure
- **High Risk**: Scalping involves rapid trading with significant risk
- **Leverage Risk**: High frequency trading can amplify losses
- **Market Risk**: Past performance does not guarantee future results
- **Technical Risk**: System failures can result in unexpected losses

### Best Practices
1. **Start with paper trading** to test strategies
2. **Monitor actively** - this is automated but requires supervision  
3. **Respect risk limits** - never risk more than you can afford
4. **Test thoroughly** before live trading
5. **Keep detailed logs** for performance analysis

### System Requirements
- **Stable internet connection** for real-time data
- **Low latency** connection to broker
- **Sufficient computing power** for real-time analysis
- **Backup systems** for critical trading periods

## 📞 Support & Troubleshooting

### Common Issues

#### Environment Validation Fails
```bash
# Check API keys
python scalping_bot.py --validate-only

# Test individual components
python core/data_manager.py
python core/order_manager.py
```

#### No Signals Generated
- Check market hours and volume filters
- Verify technical indicators are calculating
- Review strategy parameters in config.py
- Test with known volatile symbols

#### Connection Issues
- Verify Alpaca API credentials
- Check internet connection stability
- Test with paper trading first
- Review firewall settings

### Performance Optimization
- Use faster timeframes for more signals
- Adjust volume and volatility filters
- Optimize strategy parameters
- Monitor system resource usage

## 📊 Expected Performance

### Realistic Expectations
- **Win Rate**: 60-70% (varies by market conditions)
- **Risk/Reward**: 2:1 to 3:1 ratio
- **Daily Trades**: 10-50 depending on timeframe and volatility
- **Drawdown**: Expect 2-5% maximum drawdown periods

### Performance Factors
- Market volatility and volume
- Timeframe selection
- Risk management parameters
- Strategy combination effectiveness
- Market regime (trending vs ranging)

## 🔄 Updates & Maintenance

### Regular Maintenance
- Review and adjust strategy parameters
- Monitor performance metrics
- Update watchlist based on volume/volatility
- Backup trading logs and data
- Test system updates in paper trading

### Continuous Improvement
- Analyze trade logs for optimization opportunities
- Adjust risk parameters based on performance
- Add new strategies based on market conditions
- Optimize execution speed and accuracy

---

**⚠️ DISCLAIMER**: This software is for educational purposes. Trading involves substantial risk of loss. Past performance is not indicative of future results. Always use paper trading before risking real capital.
