# 📊 EOD P&L Report Locations

**Date:** August 14, 2025  
**System:** Intraday Trading Bot

---

## 📁 Primary Report Location

### **Directory:**
```
reports/daily/
```

### **Full Path:**
```
C:\Users\will7\OneDrive - Sygma Data Analytics\Stock Trading\Scalping Bot System\reports\daily\
```

---

## 📄 Report Files Generated

When the trading engine stops (automatically at market close or manually), it generates **3 files**:

### **1. Symbol Summary CSV**
- **Filename:** `YYYYMMDD_symbol_summary.csv`
- **Today's File:** `20250814_symbol_summary.csv`
- **Contents:** Per-symbol performance metrics
  - Symbol name
  - Number of trades
  - Wins/losses
  - Win rate percentage
  - Net P&L
  - Average P&L per trade
  - Average R-multiple
  - Average holding time
  - Maximum drawdown
  - Risk metrics (MAE/MFE)

### **2. Time Buckets CSV**
- **Filename:** `YYYYMMDD_time_buckets.csv`
- **Today's File:** `20250814_time_buckets.csv`
- **Contents:** Hourly performance breakdown
  - Symbol
  - Time bucket (hour)
  - Number of trades in that hour
  - P&L for that time period

### **3. Summary Markdown Report**
- **Filename:** `YYYYMMDD_summary.md`
- **Today's File:** `20250814_summary.md`
- **Contents:** Human-readable summary
  - Daily trading overview
  - Per-symbol statistics
  - File references
  - Key performance metrics

---

## 🔄 When Reports Are Generated

### **Automatic Generation:**
- ✅ When trading engine stops via `engine.stop()` method
- ✅ At market close (3:30 PM ET when bot stops trading)
- ✅ When manually stopping the trading session

### **Manual Generation:**
```python
# Test EOD generation
python -c "from core.intraday_engine import IntradayEngine; IntradayEngine().generate_daily_reports()"

# Or use the verification script
python verify_eod_generation.py
```

---

## 📊 Current Status

### **Directory Status:**
- ✅ **reports/daily/** directory exists
- ❌ **No files yet** (no completed trading sessions today)
- ✅ **Ready for generation** when trading stops

### **Why No Files Yet:**
1. Trading session may still be active
2. No trades completed in current session
3. EOD reports only generate when engine stops

---

## 🔍 Additional Report Locations

### **Trade-Level Data:**
```
logs/trade_diagnostics.csv
```
- Individual trade records
- Real-time logging as trades complete
- Source data for EOD reports

### **Historical Reports:**
```
reports/2025-08-13/    # Previous day's analysis
```

### **Other Analysis Files:**
```
reports/trading_analysis_baseline_2025-07-28.md
reports/trading_analysis_summary_20250728.txt
```

---

## 🛠️ How to Access Reports

### **Command Line:**
```bash
# Navigate to reports directory
cd "reports/daily"

# List today's reports
ls *20250814*

# View summary report
type 20250814_summary.md

# Open CSV in Excel
start 20250814_symbol_summary.csv
```

### **File Explorer:**
Navigate to:
```
C:\Users\will7\OneDrive - Sygma Data Analytics\Stock Trading\Scalping Bot System\reports\daily\
```

---

## 🎯 Key Points

### **Automatic Process:**
- ✅ Reports auto-generate when trading stops
- ✅ No manual intervention required
- ✅ Comprehensive P&L analysis included

### **File Naming:**
- 📅 **Date-based:** YYYYMMDD format
- 📊 **Type-specific:** summary, time_buckets, markdown
- 🔍 **Easy to find:** Chronological organization

### **Data Sources:**
- 💹 **Trade records** from logs/trade_diagnostics.csv
- 📊 **Real-time P&L** from active positions
- 🎯 **Performance metrics** calculated during trading

---

## 📞 Quick Commands

```bash
# Check if reports exist for today
ls reports/daily/*20250814*

# Generate reports manually (if engine running)
python -c "from core.intraday_engine import IntradayEngine; IntradayEngine().generate_daily_reports()"

# View latest reports
ls reports/daily/ | sort | tail -3
```

**📍 Bottom Line:** EOD P&L reports are saved in `reports/daily/` with date-stamped filenames and are automatically generated when the trading engine stops.
