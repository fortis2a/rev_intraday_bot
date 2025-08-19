# 🎯 Trade Closing Guide

Quick reference for closing specific trades and managing positions in the Intraday Trading Bot.

## 📋 Overview

The trade closing system provides multiple ways to close individual positions or all positions with safety confirmations and real-time market data.

## 🚀 Quick Commands

### **Interactive Mode (Recommended)**
```powershell
& "C:/Users/will7/OneDrive - Sygma Data Analytics/Stock Trading/Scalping Bot System/.venv/Scripts/python.exe" close_trade.py --interactive
```
**Or simply double-click:** `close_trade.bat`

### **List Current Positions**
```powershell
& "C:/Users/will7/OneDrive - Sygma Data Analytics/Stock Trading/Scalping Bot System/.venv/Scripts/python.exe" close_trade.py --list
```

### **Close Specific Symbol**
```powershell
& "C:/Users/will7/OneDrive - Sygma Data Analytics/Stock Trading/Scalping Bot System/.venv/Scripts/python.exe" close_trade.py --symbol SOXL
```

### **Close All Positions (Emergency)**
```powershell
& "C:/Users/will7/OneDrive - Sygma Data Analytics/Stock Trading/Scalping Bot System/.venv/Scripts/python.exe" close_trade.py --close-all
```

## 🎮 Interactive Mode Features

When you run interactive mode, you'll see:

```
🎯 TRADE CLOSER - Interactive Mode

========================================
Options:
1. List open positions
2. Close specific position  
3. Close all positions
4. Exit
========================================
```

### Position Display Example:
```
🟢 1. SOXL
    Side: LONG
    Quantity: 20 shares
    Entry Price: $28.63
    Current Price: $28.70
    P&L: $1.40 (+0.2%)
    Market Value: $574.00

🔴 2. INTC
    Side: LONG
    Quantity: 10 shares
    Entry Price: $22.39
    Current Price: $22.32
    P&L: -$0.70 (-0.3%)
    Market Value: $223.20
```

## 🛠️ Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--interactive` | `-i` | Launch interactive menu |
| `--list` | `-l` | Show all open positions |
| `--symbol SYMBOL` | `-s SYMBOL` | Close specific symbol |
| `--close-all` | | Close all positions with confirmation |

## 📝 Examples

### Close a specific stock:
```powershell
# Close INTC position
& ".venv/Scripts/python.exe" close_trade.py --symbol INTC

# Close SOXL position  
& ".venv/Scripts/python.exe" close_trade.py -s SOXL
```

### Check positions only:
```powershell
& ".venv/Scripts/python.exe" close_trade.py --list
```

### Emergency close all:
```powershell
& ".venv/Scripts/python.exe" close_trade.py --close-all
```

## ✨ Safety Features

- ✅ **Confirmation Prompts**: Prevents accidental closures
- ✅ **Position Validation**: Checks if position exists before closing
- ✅ **Real-time Pricing**: Uses current market prices
- ✅ **P&L Display**: Shows profit/loss before closing
- ✅ **Error Handling**: Graceful error management
- ✅ **Order Tracking**: Provides order IDs for reference

## 🎯 Best Practices

1. **Use Interactive Mode** for exploring positions
2. **Check P&L** before closing positions
3. **Use specific symbol** commands for quick single closures
4. **Keep order IDs** for record keeping
5. **Verify closure** by listing positions after closing

## 🆘 Emergency Procedures

### Stop All Trading and Close All Positions:
```powershell
# 1. Stop all Python processes
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force

# 2. Close all positions
& ".venv/Scripts/python.exe" close_trade.py --close-all
```

### Manual Position Check:
```powershell
# Quick position overview
& ".venv/Scripts/python.exe" close_trade.py -l
```

## 📁 Files Created

- `close_trade.py` - Main trade closing script
- `close_trade.bat` - Windows batch file for easy access
- `docs/TRADE_CLOSING_GUIDE.md` - This documentation

## 🔧 Technical Details

The trade closer uses:
- **DataManager**: For position retrieval and market data
- **OrderManager**: For executing sell orders
- **Real-time API**: Current market prices via Alpaca
- **Logging**: All actions logged for audit trail

## 📞 Support

If you encounter issues:
1. Check that the bot's virtual environment is activated
2. Verify Alpaca API connection
3. Ensure positions exist before trying to close
4. Check logs for detailed error messages

---

*Last updated: August 14, 2025*
