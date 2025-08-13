# 🖥️ Scalping Bot Interface Options

The scalping bot now offers multiple interface options to suit different needs:

## 📊 Dashboard Mode (Recommended)
**Clean, fixed-position interface with no scrolling**

```bash
python scalping_bot.py --dashboard
```

**Features:**
- ✅ Real-time position tracking
- ✅ Account balance and P&L
- ✅ Market data for watchlist symbols  
- ✅ System status and performance metrics
- ✅ No scrolling logs - easy to follow
- ✅ Updates every second

**Perfect for:** Production trading, monitoring performance, clean interface

---

## 📋 Traditional Mode
**Standard output with scrolling logs**

```bash
python scalping_bot.py
```

**Features:**
- ✅ Detailed logging output
- ✅ Full debugging information
- ✅ Strategy execution details
- ⚠️ Scrolling interface (harder to follow)

**Perfect for:** Development, debugging, detailed analysis

---

## 🧪 Test Mode
**Test strategies without executing trades**

```bash
python scalping_bot.py --test IONQ
```

**Features:**
- ✅ Strategy signal generation
- ✅ No actual order execution
- ✅ Quick strategy validation
- ✅ Market data testing

**Perfect for:** Strategy testing, market analysis

---

## 📝 Log Viewer (Optional)
**Separate log viewer for debugging**

```bash
python log_viewer.py
```

**Features:**
- ✅ Real-time log tailing
- ✅ Multiple log file monitoring
- ✅ Timestamp addition
- ✅ Can run alongside dashboard

**Perfect for:** Debugging while using dashboard mode

---

## 🔧 Advanced Options

### Timeframe Selection
```bash
python scalping_bot.py --timeframe 1Min    # 1-minute scalping
python scalping_bot.py --timeframe 2Min    # 2-minute scalping  
python scalping_bot.py --timeframe 5Min    # 5-minute scalping
```

### Dry Run Mode
```bash
python scalping_bot.py --dry-run          # No actual trades
python scalping_bot.py --dashboard --dry-run  # Dashboard + no trades
```

### Environment Validation
```bash
python scalping_bot.py --validate-only    # Check setup and exit
```

---

## 💡 Recommended Usage

**For Production Trading:**
```bash
python scalping_bot.py --dashboard
```

**For Development/Debugging:**
```bash
# Terminal 1: Dashboard
python scalping_bot.py --dashboard

# Terminal 2: Log viewer (optional)
python log_viewer.py
```

**For Testing:**
```bash
python scalping_bot.py --test IONQ --dashboard
```

---

## 🚨 Position Management

The enhanced system now prevents position accumulation by:

- ✅ **Checking actual broker positions** before new orders
- ✅ **Preventing same-direction accumulation** 
- ✅ **Closing opposite positions** properly
- ✅ **Synchronizing with broker** every trading cycle
- ✅ **Comprehensive wash trade handling**

**Dashboard shows real positions from broker, not just internal tracking!**

---

## 🛠️ Troubleshooting

**Problem:** Too many scrolling logs
**Solution:** Use `--dashboard` mode

**Problem:** Need to see detailed logs
**Solution:** Run `log_viewer.py` in separate terminal

**Problem:** Position accumulation  
**Solution:** Already fixed! New system prevents this

**Problem:** Can't follow bot status
**Solution:** Dashboard mode shows everything clearly

---

## 📞 Quick Reference

| Command | Purpose |
|---------|---------|
| `python scalping_bot.py --dashboard` | Clean interface mode |
| `python scalping_bot.py --test IONQ` | Test strategies |
| `python log_viewer.py` | View logs separately |
| `python position_cleanup.py` | Check/close positions |
| `python position_cleanup.py cleanup` | Emergency close all |

The dashboard mode is the **recommended** way to run the bot for production trading! 🎯
