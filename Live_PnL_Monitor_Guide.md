# 📊 Live P&L Monitor Setup Guide

## 🚀 Quick Start

### **Method 1: PowerShell Launcher (Recommended)**
```powershell
.\launch_live_pnl.ps1
```

### **Method 2: Batch File Launcher**
```cmd
.\launch_live_pnl.bat
```

### **Method 3: Direct Python Execution**
```bash
# Enhanced monitor (per-stock breakdown)
python enhanced_live_pnl.py

# Standard monitor (simple)
python live_pnl_monitor.py
```

---

## 📊 Monitor Options

### **1. Enhanced P&L Monitor**
- ✅ **Per-stock P&L breakdown**
- ✅ **Real-time position tracking**
- ✅ **Current market prices**
- ✅ **Session P&L summary**
- ✅ **Performance metrics**

### **2. Standard P&L Monitor**
- ✅ **Simple P&L tracking**
- ✅ **Account summary**
- ✅ **Basic position info**

### **3. Both Monitors (Side-by-Side)**
- ✅ **Enhanced + Standard running together**
- ✅ **Different perspectives**
- ✅ **Cross-validation**

---

## 🖥️ Display Format

### Enhanced Monitor Sample:
```
📊 ENHANCED LIVE P&L MONITOR
======================================================================
🕐 2025-08-12 20:19:41 ET
🎯 Quantum Watchlist: IONQ, PG, QBTS, RGTI, JNJ
======================================================================

💰 ACCOUNT SUMMARY:
   Total Equity: $97,299.26
   Buying Power: $389,209.52
   Session P&L: 🟢 +$142.50 (🟢 +0.15%)
   Day Trades Used: 2/3

📊 POSITION DETAILS:
──────────────────────────────────────────────────────────────────────
Symbol   Qty        Price      P&L             P&L%       Value       
──────────────────────────────────────────────────────────────────────
IONQ     📈50       $43.25     🟢 +$75.00     🟢 +3.5%   $2,162
PG       📈25       $155.80    🟢 +$67.50     🟢 +1.7%   $3,895
QBTS     --         $18.45     No Position             --                 --
RGTI     --         $16.30     No Position             --                 --
JNJ      --         $172.90    No Position             --                 --
──────────────────────────────────────────────────────────────────────
TOTAL                          🟢 +$142.50                               $6,057

📈 MARKET PRICES:
────────────────────────────────────────
IONQ     $43.25      📊 HOLDING (LONG)
PG       $155.80     📊 HOLDING (LONG)
QBTS     $18.45      👀 WATCHING
RGTI     $16.30      👀 WATCHING
JNJ      $172.90     👀 WATCHING

📊 PERFORMANCE METRICS:
   Active Positions: 2
   Average P&L%: 🟢 +2.6%
   Total Position Value: $6,057.00

🔄 Auto-refresh every 5 seconds | Press Ctrl+C to exit
======================================================================
```

---

## 🛠️ Usage Workflow

### **Recommended Setup:**
1. **Launch P&L Monitor:** `.\launch_live_pnl.ps1`
2. **Choose Enhanced Monitor:** Option 1
3. **Start Trading Bot:** Run `python launcher.py` in main window
4. **Monitor Both:** Watch P&L in external window, trading in main

### **Multiple Monitor Setup:**
1. **Launch Both Monitors:** Choose option 3 in launcher
2. **Position Windows:** Enhanced on left, Standard on right
3. **Start Trading:** Use main window for trading bot
4. **Monitor Performance:** Watch real-time P&L updates

---

## 🔧 Features

### **Real-Time Updates:**
- ✅ **5-second refresh rate**
- ✅ **Live position tracking**
- ✅ **Current market prices**
- ✅ **Session P&L calculation**

### **Visual Indicators:**
- 🟢 **Green for profits**
- 🔴 **Red for losses**
- ⚪ **White for neutral**
- 📈 **Long positions**
- 📉 **Short positions**
- 👀 **Watching (no position)**

### **Key Metrics:**
- 💰 **Total equity & buying power**
- 📊 **Per-stock P&L breakdown**
- 🎯 **Session performance**
- 📈 **Day trade usage**
- 💎 **Position values**

---

## 🚨 Troubleshooting

### **If Monitor Won't Start:**
1. Check virtual environment is activated
2. Ensure Alpaca API keys are configured
3. Verify internet connection
4. Check market hours (data may be limited when closed)

### **If No Positions Show:**
- Normal if you haven't opened any positions yet
- Monitor will show "No Position" for unwatched stocks
- Prices may show $0.00 when market is closed

### **If Prices Show $0.00:**
- Market may be closed (normal)
- API rate limits (wait a moment)
- Network connectivity issues

---

## 💡 Pro Tips

1. **Run monitor BEFORE starting trading bot** for baseline
2. **Use Enhanced monitor for detailed tracking**
3. **Keep monitor window visible** during trading
4. **Watch for real-time P&L changes** as trades execute
5. **Use session P&L** to track daily performance

**Happy Trading! 📈**
