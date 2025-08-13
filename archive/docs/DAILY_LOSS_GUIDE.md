# 💰 Daily Loss Limits - Realistic Guidelines

## 🎯 **Your Current Setting: 15% Daily Loss**

You've set your daily loss limit to **15% of portfolio value**. Here's how that compares to professional standards:

## 📊 **Professional Daily Loss Limits**

| Trader Type | Typical Daily Loss Limit | Example ($10K Account) |
|-------------|-------------------------|----------------------|
| **Conservative** | 1-2% | $100-$200 |
| **Moderate** | 3-5% | $300-$500 |
| **Aggressive** | 5-10% | $500-$1,000 |
| **Very Aggressive** | 10-15% | $1,000-$1,500 |
| **Your Setting** | **15%** | **$1,500** |

## ⚠️ **Reality Check**

### **15% Daily Loss is:**
- ✅ **Realistic** for experienced day traders
- ✅ **Higher risk, higher reward** approach
- ⚠️ **Very aggressive** for beginners
- ❌ **Could wipe out account quickly** (6-7 bad days = account gone)

### **Professional Recommendations:**
- **Beginners**: Start with 2-3% daily loss limit
- **Experienced**: 5-8% is common for scalpers
- **Professionals**: Rarely exceed 10%

## 🧮 **Quick Math Examples**

### With $10,000 Account:
- **1% limit**: Lose max $100/day
- **5% limit**: Lose max $500/day  
- **15% limit**: Lose max $1,500/day ⚠️

### Risk Scenarios:
- **3 bad days at 15%**: Down 37% total
- **5 bad days at 15%**: Down 55% total
- **7 bad days at 15%**: Account essentially wiped out

## 🎯 **Recommended Starting Points**

### **For Paper Trading** (Your current mode):
- ✅ **15% is fine** - you're learning with fake money
- ✅ **Great for testing** aggressive strategies
- ✅ **See how it feels** to hit limits

### **For Live Trading:**
- 🟢 **Conservative**: 2-3% daily loss
- 🟡 **Moderate**: 5% daily loss  
- 🔴 **Aggressive**: 8-10% daily loss
- ⚫ **Very High Risk**: 15% daily loss

## 🔧 **How to Change It**

In `config.py`, adjust this line:
```python
MAX_DAILY_LOSS_PCT: float = 15.0  # Your current setting
```

**Recommended alternatives:**
```python
MAX_DAILY_LOSS_PCT: float = 5.0   # Conservative scalping
MAX_DAILY_LOSS_PCT: float = 8.0   # Moderate scalping  
MAX_DAILY_LOSS_PCT: float = 10.0  # Aggressive scalping
```

## 📈 **Scalping-Specific Considerations**

### **Why Scalpers Use Higher Limits:**
- More trades = more opportunities to lose
- Need room for multiple small losses
- Quick recovery potential with next trades

### **But Remember:**
- Scalping profits are typically small (0.1-0.5% per trade)
- Need many winning trades to offset one big loss
- 15% loss = need 30+ winning trades at 0.5% each to recover

## 🎯 **Bottom Line**

**15% is realistic for:**
- ✅ Experienced traders
- ✅ Paper trading/testing
- ✅ High-risk tolerance
- ✅ Adequate account size

**Consider lowering to 5-8% for:**
- 🛡️ Better risk management
- 🛡️ Longer account survival
- 🛡️ Less emotional stress
- 🛡️ More sustainable trading

---

**Your bot is now set to stop trading after losing 15% of your portfolio value in a single day. This scales automatically with your account size!**
