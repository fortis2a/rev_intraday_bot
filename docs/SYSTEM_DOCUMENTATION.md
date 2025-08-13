# Intraday Trading Bot - Complete System Documentation

## 🚀 System Overview

This is a comprehensive intraday trading bot system with full automation, monitoring, analysis, and backup capabilities.

### 📊 Current Configuration
- **Watchlist:** IONQ, RGTI, QBTS, JNJ, PG (Quantum computing + stable stocks)
- **Trading Hours:** 10:00 AM - 3:30 PM ET (avoiding volatile periods)
- **Risk Management:** 2% stop loss, 4% take profit, $1000 max position
- **Account:** $97,299.21 equity, $389,196.84 buying power (Alpaca Paper)

## 🏗️ System Components

### Core Trading Engine
- **main.py** - Main trading engine (LIVE/DEMO/TEST modes)
- **launcher.py** - System controller with 14 options
- **data_manager.py** - Alpaca API integration
- **config.py** - Configuration and settings

### Trading Strategies (strategies/)
- **momentum_scalp.py** - Momentum-based scalping
- **mean_reversion.py** - Mean reversion trading
- **vwap_bounce.py** - VWAP bounce strategy

### Core Components (core/)
- **scalping_engine.py** - Main trading engine
- **order_manager.py** - Order execution
- **risk_manager.py** - Risk management

### Monitoring & Analysis
- **live_pnl_external.py** - Colorized live P&L monitor
- **eod_analysis.py** - Comprehensive EOD reports
- **eod_scheduler.py** - Auto EOD analysis at 4:30 PM

### Backup System
- **backup_system.py** - GitHub backup automation
- **Auto midnight backup** to https://github.com/fortis2a/rev_intraday_bot

## 🎯 How to Use

### Quick Start Options
1. **Double-click launcher files:**
   - `Live_PnL_Monitor.bat` - Colorized external P&L monitor
   - `EOD_Analysis.bat` - Comprehensive trading reports
   - `GitHub_Backup.bat` - Manual backup to GitHub

2. **Run main system:**
   ```bash
   python launcher.py
   ```

### Launcher Menu (14 Options)
1. **Start Full Trading Session (Live Mode)** - Full live trading
2. **Start Demo Mode (Safe Testing)** - Safe demo trading
3. **Start Test Mode (Single Cycle)** - Single test cycle
4. **Start P&L Monitor Only** - Monitor only mode
5. **Start Live Trading + Show Signal Feed** - Live with signals
6. **Start Dashboard** - Trading dashboard
7. **Show Live Logs** - View real-time logs
8. **Show Account Information** - Account details
9. **Generate Trading Report** - Quick reports
10. **EOD Analysis (End-of-Day Reports)** - Comprehensive analysis
11. **GitHub Backup (Manual & Auto Scheduler)** - Backup system
12. **Validate Environment** - System validation
13. **Stop All Processes** - Emergency stop
14. **Exit** - Clean shutdown

## 📈 Live P&L Monitor Features

### Colorized Display
- **GREEN** - Gains, profits, long positions
- **RED** - Losses, short positions
- **BLUE** - Watching status, info
- **CYAN** - Stock symbols, cash values
- **YELLOW** - Neutral values, separators
- **MAGENTA** - Holdings, totals

### Real-time Data
- Account equity and buying power
- Live position tracking
- Market prices (updates every 5 seconds)
- P&L calculations with percentages
- Day trade counter

## 📊 EOD Analysis System

### Generated Reports
- **Stock-by-stock P&L breakdown**
- **Long vs Short performance analysis**
- **Hourly trading patterns**
- **Win/loss distribution charts**
- **Interactive HTML dashboard**
- **Detailed statistics and metrics**

### Chart Types
- PNG charts (high-quality static)
- Interactive Plotly dashboard
- Time-series analysis
- Distribution histograms
- Performance breakdowns

### Auto-Schedule
- Runs automatically at 4:30 PM daily
- Windows Task Scheduler integration
- Email notifications (configurable)
- Auto-retry on failure

## 💾 Backup System

### GitHub Integration
- **Repository:** https://github.com/fortis2a/rev_intraday_bot
- **Auto-backup:** Daily at midnight
- **Manual backup:** Available anytime
- **Smart exclusions:** No logs, .env, or cache files

### Backup Content
- All Python source code
- Configuration files
- Trading strategies
- Documentation
- Launcher scripts

### Setup Options
1. **Manual:** Run `GitHub_Backup.bat`
2. **Scheduled:** Run `Setup_Auto_GitHub_Backup.bat`
3. **Launcher:** Option 11 in main menu

## ⚙️ Automation Features

### Daily Schedules
- **4:30 PM** - EOD Analysis (auto-generates reports)
- **12:00 AM** - GitHub Backup (auto-saves to repository)

### Windows Task Scheduler
- **EOD Analysis Task** - TradingBot_EOD_Analysis
- **GitHub Backup Task** - TradingBot_GitHub_Backup

## 🛡️ Risk Management

### Position Limits
- Maximum position size: $1,000
- Maximum daily loss: $500
- Stop loss: 2%
- Take profit: 4%

### Trading Hours Protection
- No trading before 10:00 AM (avoid opening volatility)
- No trading after 3:30 PM (avoid closing volatility)
- Only trades during stable market hours

### Account Protection
- Paper trading environment (safe testing)
- Real-time position monitoring
- Automatic stop-loss execution
- Day trade limit tracking

## 📝 File Structure

```
Scalping Bot System/
├── main.py                    # Main trading engine
├── launcher.py                # System controller
├── data_manager.py            # Alpaca integration
├── config.py                  # Configuration
├── live_pnl_external.py       # Live P&L monitor
├── eod_analysis.py            # EOD analysis
├── eod_scheduler.py           # EOD automation
├── backup_system.py           # GitHub backup
├── core/                      # Core components
│   ├── scalping_engine.py
│   ├── order_manager.py
│   └── risk_manager.py
├── strategies/                # Trading strategies
│   ├── momentum_scalp.py
│   ├── mean_reversion.py
│   └── vwap_bounce.py
├── utils/                     # Utilities
│   └── logger.py
├── *.bat                      # Windows launchers
└── logs/                      # System logs
```

## 🚀 Next Steps

1. **Start with Demo Mode** - Test the system safely
2. **Monitor Live P&L** - Watch real-time performance
3. **Review EOD Reports** - Analyze daily performance
4. **Set Auto-Backup** - Ensure code is saved
5. **Graduate to Live Trading** - When confident

## 📞 Support

- All code is well-documented with comments
- Comprehensive error handling and logging
- Professional-grade exception management
- Detailed status reporting

---

**Last Updated:** August 13, 2025
**System Status:** Fully Operational
**Repository:** https://github.com/fortis2a/rev_intraday_bot
