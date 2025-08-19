# 🤖 Intraday Trading Bot System

## 🎯 Overview

This is a comprehensive intraday trading bot system designed for scalping strategies with advanced risk management, stock-specific thresholds, and dynamic trailing stops.

## 🚀 Key Features

### 📊 **Trading Strategies**
- **Momentum Scalping**: Captures short-term price movements
- **Mean Reversion**: Trades oversold/overbought conditions  
- **VWAP Bounce**: Volume-weighted average price strategies
- **Multi-factor Confirmation**: 5-8 signal confirmation system

### 🎯 **Stock-Specific Intelligence**
- **Dynamic Thresholds**: Customized stop/profit levels per stock
- **Volatility Profiles**: Low/Moderate/High volatility handling
- **Position Sizing**: Risk-adjusted position sizes
- **Historical Analysis**: 60-day 15-minute data optimization

### 🛡️ **Advanced Risk Management**
- **Trailing Stops**: Dynamic profit protection
- **Confidence Filtering**: 75% minimum confidence threshold
- **Daily Loss Limits**: Maximum risk controls
- **Real-time Monitoring**: Live position tracking

### 📈 **Technical Indicators**
- **MACD**: 12,26,9 configuration
- **EMA**: 9 and 21 period exponential moving averages
- **VWAP**: Volume-weighted average price
- **Bollinger Bands**: 20-period, 2 standard deviations
- **RSI**: Relative strength index with custom thresholds

## 🏗️ **System Architecture**

### **Core Components**
```
🏠 Main System
├── main.py - Trading engine
├── config.py - Configuration
├── data_manager.py - Market data
├── order_manager.py - Trade execution
├── strategies.py - Trading strategies
├── stock_specific_config.py - Stock thresholds
└── launcher.py - System launcher

📂 Core Modules (/core/)
└── trailing_stop_manager.py - Advanced trailing stops

🧪 Testing Suite (/tests/)
├── test_confidence_filter.py
├── test_stock_specific_thresholds.py
└── test_trailing_stops.py

📜 Utilities (/scripts/)
├── analyze_stock_thresholds.py
├── backup_system.py
├── eod_analysis.py
└── live_pnl_external.py
```

## ⚙️ **Configuration**

### **Watchlist Stocks**
- **IONQ**: Moderate volatility (0.90%)
- **RGTI**: Moderate volatility (1.07%) 
- **QBTS**: High volatility (2.42%)
- **JNJ**: Low volatility (0.22%)
- **PG**: Low volatility (0.19%)

### **Risk Parameters**
- **Stop Loss**: 0.5-1.54% (stock-specific)
- **Take Profit**: 1.0-1.33% (stock-specific)
- **Trailing Distance**: 1.0-2.51% (stock-specific)
- **Confidence Threshold**: 75% minimum
- **Max Position**: $1,000 per trade
- **Daily Loss Limit**: $500

## 🚀 **Quick Start**

### **1. Launch System**
```bash
python launcher.py
```

### **2. Trading Modes**
- **Live Mode**: Real trading with real money
- **Demo Mode**: Paper trading for testing
- **Test Mode**: Single cycle validation

### **3. Key Menu Options**
- **Option 1**: Start full trading session
- **Option 2**: Demo mode (safe testing)
- **Option 5**: Live trading with signal feed
- **Option 8**: Account information
- **Option 11**: GitHub backup
- **Option 13**: Test enhanced indicators

## 📊 **Stock-Specific Thresholds**

| Stock | Volatility | Stop Loss | Take Profit | Position Size |
|-------|------------|-----------|-------------|---------------|
| IONQ  | 0.90%      | 0.50%     | 1.00%       | 1.0x          |
| RGTI  | 1.07%      | 0.51%     | 1.00%       | 1.0x          |
| QBTS  | 2.42%      | 1.54%     | 1.33%       | 0.7x          |
| JNJ   | 0.22%      | 0.50%     | 1.00%       | 1.5x          |
| PG    | 0.19%      | 0.50%     | 1.00%       | 1.5x          |

## 🛡️ **Trailing Stop System**

### **Configuration**
- **Activation**: 1.0% profit threshold
- **Distance**: Stock-specific (1.0-2.51%)
- **Minimum Move**: 0.5% for adjustment
- **Protection**: Dynamic profit locking

### **Example Operation**
1. **Entry**: $100.00
2. **Initial Stop**: $98.50 (1.5% loss)
3. **Activation**: $101.00 (+1.0% profit)
4. **Trail Distance**: $99.48 (1.5% below peak)
5. **Dynamic Adjustment**: Follows price up, never down

## 📈 **Performance Optimization**

### **Confidence Scoring**
- **Base Score**: 85% for technical alignment
- **MACD Bonus**: +5% for strong momentum
- **Volume Bonus**: +5% for high volume
- **EMA Bonus**: +5% for trend alignment
- **Multi-timeframe**: +3% for confirmation
- **VWAP Bonus**: +2% for institutional support

### **Signal Filtering**
- **Minimum Confidence**: 75%
- **Multi-factor Confirmation**: 5/8 or 4/7 signals
- **Market Hours**: 10:00 AM - 3:30 PM ET
- **Volume Requirements**: 1.5x average volume

## 🔧 **Installation & Setup**

### **Dependencies**
```bash
pip install alpaca-trade-api pandas numpy yfinance python-dotenv
```

### **Environment Setup**
```bash
# Create .env file with:
ALPACA_API_KEY=your_api_key
ALPACA_SECRET_KEY=your_secret_key
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

### **Verification**
```bash
python launcher.py
# Select option 12 (Validate Environment)
```

## 🧪 **Testing**

### **Run All Tests**
```bash
python tests/test_confidence_filter.py
python tests/test_stock_specific_thresholds.py
python tests/test_trailing_stops.py
```

### **Analyze Stock Data**
```bash
python scripts/analyze_stock_thresholds.py
```

## 📊 **Monitoring & Reports**

### **Live Monitoring**
- Real-time P&L tracking
- Signal confidence display
- Position status updates
- Risk metric monitoring

### **End-of-Day Reports**
- Daily performance summary
- Win/loss analysis
- Strategy effectiveness
- Risk metrics review

## 🔄 **Backup & Maintenance**

### **Automatic Backup**
```bash
python scripts/backup_system.py backup
```

### **Manual Operations**
- **Option 11**: GitHub backup from launcher
- **Option 10**: EOD analysis
- **Option 9**: Generate trading reports

## ⚠️ **Risk Disclaimer**

This trading bot is for educational and research purposes. Past performance does not guarantee future results. Trading involves substantial risk and may not be suitable for all investors. Only trade with capital you can afford to lose.

## 📞 **Support**

- **Repository**: https://github.com/fortis2a/rev_intraday_bot
- **Documentation**: `/docs/` folder
- **Test Suite**: `/tests/` folder
- **Utilities**: `/scripts/` folder

---

**Built with advanced algorithmic trading techniques and institutional-grade risk management.**