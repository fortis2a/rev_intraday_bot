# 📊 PnL Monitoring Guide

## Overview
This guide covers the comprehensive PnL monitoring system for the intraday trading bot, including real-time tracking, cost analysis, and performance reporting.

## 🚀 Quick Start

### Launch Real-Time PnL Monitor
```bash
# Windows PowerShell
.\start_pnl_monitor.ps1

# Windows Command Prompt  
start_pnl_monitor.bat

# Direct Python execution
python live_pnl_monitor.py
```

### Generate End-of-Day Reports
```bash
# Windows PowerShell
.\generate_eod_report.ps1

# Windows Command Prompt
generate_eod_report.bat

# Direct Python execution
python generate_eod_report.py
```

## 💰 Enhanced PnL Features

### Real-Time Cost Tracking
- **Actual Fill Prices**: Uses Alpaca's `filled_avg_price` for precise calculations
- **Slippage Monitoring**: Tracks difference between expected and actual prices
- **Regulatory Fees**: Includes SEC, FINRA TAF, and NSCC fees
- **Net vs Gross PnL**: Separates trading performance from transaction costs

### Fee Structure (Alpaca)
```
Commission: $0.00 (commission-free)
SEC Fee: $0.008 per $1000 of sales
FINRA TAF: $0.145 per $1000 of principal
NSCC Fee: $0.0175 per $1000 of principal
```

### Slippage Analysis
- **Entry Slippage**: Difference between signal price and fill price
- **Exit Slippage**: Difference between target exit and actual fill
- **Impact Analysis**: Cost as percentage of trade value
- **Running Averages**: Track slippage trends over time

## 📈 Real-Time Dashboard

### Live Metrics Displayed
- Current session P&L (gross and net)
- Active positions and unrealized P&L
- Today's trade count and win rate
- Average slippage and total costs
- Efficiency ratio (net/gross PnL)

### Performance Indicators
- 🟢 **Green**: Profitable session
- 🟡 **Yellow**: Breaking even (±0.1%)
- 🔴 **Red**: Losing session
- ⚡ **Flash**: New trade executed

## 📊 Detailed Reports

### Session Summary Report
```
📊 TRADING SESSION SUMMARY
========================
Session Date: 2025-08-13
Trading Period: 09:30 - 16:00
Bot Configuration: Intraday (15min)

💹 PERFORMANCE METRICS
Total Trades: 6
Winning Trades: 4 (66.7%)
Losing Trades: 2 (33.3%)
Average Hold Time: 2.3 hours

💰 PNL BREAKDOWN
Gross P&L: $456.78
Transaction Costs: $12.34
Net P&L: $444.44
Cost Impact: 2.7%
Efficiency Ratio: 0.973

📉 SLIPPAGE ANALYSIS
Average Entry Slippage: $0.02 (0.013%)
Average Exit Slippage: $0.03 (0.020%)
Total Slippage Cost: $18.50

🎯 TRADE QUALITY
Best Trade: AAPL +$89.23 (0.59%)
Worst Trade: TSLA -$23.45 (-0.15%)
Largest Position: $3,000 (NVDA)
```

### Daily Performance Report
- Trade-by-trade breakdown
- Symbol performance analysis
- Time-of-day patterns
- Strategy effectiveness
- Cost efficiency trends

## 🔧 Configuration

### Database Location
```
data/trading_history.db
```

### Log Files
```
logs/scalping_pnl_tracker_YYYYMMDD.log
logs/enhanced_pnl_YYYYMMDD.log
```

### Report Output
```
reports/daily/YYYYMMDD_session_summary.md
reports/daily/YYYYMMDD_cost_analysis.csv
reports/daily/YYYYMMDD_trades.csv
```

## 🚨 Alerts and Notifications

### Cost Alerts
- **High Slippage Warning**: >0.05% per trade
- **Excessive Fees Alert**: >5% of gross PnL
- **Efficiency Warning**: Net/Gross ratio <0.90

### Performance Alerts
- **Daily Loss Limit**: Stop trading at -3% daily loss
- **Consecutive Losses**: Pause after 3 consecutive losses
- **Position Size Warning**: Alert if position >$3,000

## 📱 Integration

### Trading Bot Integration
```python
from live_pnl_monitor import EnhancedPnLMonitor

# Initialize in trading engine
pnl_monitor = EnhancedPnLMonitor()

# Record trade entry
trade_id = pnl_monitor.record_enhanced_trade_entry({
    'symbol': 'AAPL',
    'side': 'BUY',
    'quantity': 100,
    'expected_price': 150.00,
    'actual_fill_price': 150.02,
    'strategy': 'momentum_scalp'
})

# Record trade exit  
pnl_monitor.record_enhanced_trade_exit(trade_id, {
    'expected_price': 150.40,
    'actual_fill_price': 150.38,
    'exit_reason': 'profit_target'
})
```

### Real-Time Display
```python
# Get current session stats
stats = pnl_monitor.get_cost_analysis()
print(f"Net P&L: ${stats['net_pnl']:.2f}")
print(f"Cost Impact: {stats['cost_impact_pct']:.2f}%")
```

## 🛠️ Troubleshooting

### Common Issues

**Empty Database**
```bash
# Reset database
python -c "from utils.pnl_tracker import PnLTracker; PnLTracker()._init_database()"
```

**Missing Reports**
```bash
# Regenerate reports
python generate_eod_report.py --date 2025-08-13
```

**Incorrect Calculations**
- Verify Alpaca fill prices are being captured
- Check timezone alignment (market hours)
- Validate fee calculations against broker statements

### Debug Mode
```bash
# Run with debug logging
python live_pnl_monitor.py --debug

# Check specific trade
python -c "
from utils.pnl_tracker import PnLTracker
tracker = PnLTracker()
print(tracker.get_trade_details('trade_20250813_093045_123456'))
"
```

## 📚 Advanced Features

### Custom Reporting
- Export to Excel/CSV for analysis
- Integration with external accounting systems  
- Performance comparison vs benchmarks
- Risk-adjusted return calculations

### API Access
```python
# Get programmatic access to PnL data
from live_pnl_monitor import EnhancedPnLMonitor

monitor = EnhancedPnLMonitor()
session_data = monitor.get_cost_analysis()

# Export for external systems
import json
with open('session_pnl.json', 'w') as f:
    json.dump(session_data, f, indent=2)
```

### Historical Analysis
- Compare current session to historical performance
- Identify patterns in slippage and costs
- Optimize entry/exit timing
- Strategy performance attribution

## 📞 Support

For technical issues or questions about PnL monitoring:
1. Check the debug logs in `logs/`
2. Verify database integrity
3. Ensure Alpaca API connectivity
4. Review trading bot configuration

The enhanced PnL monitoring system provides complete transparency into your trading costs and actual performance, essential for profitable intraday trading.
