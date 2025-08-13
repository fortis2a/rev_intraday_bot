# 💰 Standalone P&L Monitor - Usage Guide

## 🚀 Quick Start

### Option 1: PowerShell Script (Recommended)
1. **Open a new PowerShell window**
2. **Navigate to your project directory:**
   ```powershell
   cd "C:\Users\will7\OneDrive - Sygma Data Analytics\Stock Trading\Scalping Bot System"
   ```
3. **Run the launcher:**
   ```powershell
   .\start_pnl_monitor.ps1
   ```

### Option 2: Batch File (Simple)
1. **Double-click `start_pnl_monitor.bat`** in Windows Explorer
2. **Or run from Command Prompt:**
   ```cmd
   start_pnl_monitor.bat
   ```

### Option 3: Direct Python Execution
```powershell
& "C:/Users/will7/OneDrive - Sygma Data Analytics/Stock Trading/Scalping Bot System/.venv/Scripts/python.exe" pnl_monitor.py
```

---

## 📊 What You'll See

### Real-time Display Includes:
- **💼 Account Summary**
  - Portfolio value with daily change percentage
  - Available buying power
  - Day trading count (PDT limit tracking)
  - Simulated vs real mode indicator

- **📈 Session Performance**  
  - Total daily P&L (realized + unrealized)
  - Breakdown: Realized vs Unrealized P&L
  - Trade statistics: win rate, best/worst trades
  - Session duration

- **📋 Active Positions**
  - All current positions with live P&L
  - Entry price vs current price
  - Percentage gain/loss per position
  - Total market value of positions

- **⚙️ System Status**
  - Market open/closed status
  - Connection status (P&L tracker, broker)
  - Risk management settings
  - Watchlist and system configuration

---

## 🔧 Command Line Options

### Basic Usage:
```bash
python pnl_monitor.py
```

### Custom Refresh Rate:
```bash
python pnl_monitor.py --refresh 1.5    # Update every 1.5 seconds
python pnl_monitor.py --refresh 5      # Update every 5 seconds
```

### Connection Test:
```bash
python pnl_monitor.py --test           # Test connections and exit
```

---

## 💡 Usage Tips

### 🔄 **Refresh Rates:**
- **Fast (0.5-1s)**: Real-time scalping monitoring
- **Normal (2-3s)**: Standard monitoring (recommended)
- **Slow (5-10s)**: Low-impact background monitoring

### 📱 **Window Management:**
1. **Resize the window** to fit your screen setup
2. **Use alongside main dashboard** for dual monitoring
3. **Pin to taskbar** for quick access
4. **Set as "Always on Top"** in window properties

### 🚨 **Error Handling:**
- If connection fails, the monitor will show error messages
- Missing data will display as "N/A" or "Loading..."
- Press **Ctrl+C** to stop monitoring gracefully

---

## 🔗 Integration with Main Bot

### **Run Simultaneously:**
1. **Terminal 1**: Main scalping bot with dashboard
   ```bash
   python scalping_bot.py --dashboard
   ```

2. **Terminal 2**: Standalone P&L monitor
   ```bash
   python pnl_monitor.py
   ```

### **Data Synchronization:**
- ✅ **Shares same database** for trade tracking
- ✅ **Real-time broker data** from same connection
- ✅ **Consistent P&L calculations** across both displays
- ✅ **Independent operation** - one can run without the other

---

## 🛠️ Troubleshooting

### **Common Issues:**

**❌ "Import error"**
- Ensure you're running from the project root directory
- Check virtual environment is activated

**❌ "Connection failed"**  
- Verify Alpaca API credentials are configured
- Check internet connection
- Run `python pnl_monitor.py --test` to diagnose

**❌ "No data displayed"**
- Main trading bot may not be running
- Check if positions exist in broker account
- Verify database permissions

**❌ "Slow updates"**
- Reduce refresh rate: `--refresh 1`
- Check system performance
- Verify network latency to broker

---

## 📈 Sample Output

```
===============================================================================
                    💰 REAL-TIME P&L MONITOR - EXTERNAL VIEW 💰
===============================================================================
🕐 Current Time: 2025-07-25 16:00:24 | ⏱️ Monitor Runtime: 0:05:32
🔄 Refresh Rate: 2.0s | 📊 Updates: 166

💼 ACCOUNT SUMMARY:
   Portfolio Value: $101,376.51 (+$45.23 / +0.04%)
   Buying Power: $202,407.66
   Day Trades Used: 2/3 (PDT limit)
   🧪 Simulated Mode: Using $2,000 virtual portfolio

📈 SESSION PERFORMANCE:
   📊 Total Daily P&L: +$47.89
   💰 Realized P&L: +$50.61
   📋 Unrealized P&L: -$2.72
   🎯 Total Trades: 5 (W:3 L:2)
   📈 Win Rate: 60.0%
   🏆 Best Trade: +$25.40
   📉 Worst Trade: -$8.20
   📊 Avg Trade: +$10.12
   ⏱️ Session Duration: 2:34:18

📋 ACTIVE POSITIONS:
   Symbol   Side   Qty    Entry    Current  P&L          P&L %   
   ----------------------------------------------------------------------
   IONQ     [LONG] 8      $43.51   $43.17   -$2.72       -0.8%
   ----------------------------------------------------------------------
   Total Market Value: $345.36

⚙️ SYSTEM STATUS:
   Market Status: 🟢 OPEN
   Watchlist: 1 symbols
   Max Positions: 3
   Risk per Trade: 2.0%
   Timeframe: 1Min
   P&L Tracker: 🟢 Connected
   Broker Connection: 🟢 Connected

Last Update: 16:00:24 | Press Ctrl+C to stop | Monitoring in real-time...
===============================================================================
```

---

## 🎯 Perfect For:

- **📊 Real-time P&L monitoring** while running main bot
- **👀 Quick portfolio status checks** 
- **📱 Dedicated monitoring window** on second screen
- **💰 Live position tracking** with current market prices
- **📈 Session performance analysis** throughout the day
- **⚡ High-frequency update monitoring** during active trading

**The standalone P&L monitor gives you a dedicated, clean view of your trading performance that updates in real-time!** 💪📈
