# Pattern Day Trading (PDT) Rules Analysis for Intraday Trading Bot

**Date:** August 12, 2025  
**System:** Intraday Trading Bot - Swing Trading System  
**Current Status:** Paper Trading ($97,299.26 Alpaca Account)  

---

## 🚨 Pattern Day Trading (PDT) Rules Overview

### **PDT Rule Basics:**
- **Threshold:** Accounts with less than $25,000 are restricted to **3 day trades in any rolling 5-business-day period**
- **Day Trade Definition:** Buying and selling (or selling and buying) the same security on the same trading day
- **Violation Consequences:** Account flagged as PDT → 90-day trading restriction to closing positions only

### **Key Points:**
- PDT rules apply to **margin accounts only**
- **Cash accounts** are exempt from PDT rules but have T+2 settlement requirements
- The $25,000 minimum must be maintained at all times (not just at account opening)

---

## 📊 How PDT Works with Your 5-Stock Strategy

**Current Watchlist:** IONQ, PG, QBTS, RGTI, JNJ (Quantum Computing Focus)

### **Scenario 1: Conservative Approach (Within PDT Limits)**
```
Monday: Buy/Sell IONQ (Day Trade #1)
Tuesday: Buy/Sell PG (Day Trade #2)  
Wednesday: Buy/Sell QBTS (Day Trade #3)
Thursday: CANNOT day trade - PDT limit reached
Friday: CANNOT day trade - PDT limit reached
```
**Result:** Only 3 day trades per week across all 5 stocks

### **Scenario 2: Swing Trading Adaptation**
```
Monday: Buy IONQ (hold overnight)
Tuesday: Buy PG (hold overnight), Sell IONQ next day
Wednesday: Buy QBTS (hold overnight), Sell PG next day
Thursday: Buy RGTI (hold overnight), Sell QBTS next day
Friday: Buy JNJ (hold overnight), Sell RGTI next day
```
**Result:** No PDT violations because positions held overnight

---

## ⚙️ Impact on Your Current Intraday Bot

### **Current Bot Settings (15Min timeframe):**
- ✅ **Max Hold Time:** 28,800s (8 hours) - Could work for swing trades
- ❌ **Daily Trade Limit:** 6 trades - **EXCEEDS PDT LIMIT**
- ✅ **Risk Management:** 0.45% stops, 1.2% targets - Appropriate for swings
- ✅ **Timeframe:** 15Min signals suitable for swing entries

### **PDT-Compliant Modifications Needed:**
1. **Reduce daily trades** from 6 to 3 maximum
2. **Implement overnight holding** strategy
3. **Position sizing** - larger positions per trade (since fewer trades)
4. **Enhanced stock selection** - prioritize best setups only

---

## 🎯 Strategic Options Under $25K

### **Option 1: Pure Swing Trading** ⭐ RECOMMENDED
- **Hold positions:** 1-3 days
- **Entry signals:** Use your 15Min signals for entries
- **Exit strategy:** Profit targets or predetermined time-based exits
- **✅ Advantage:** No PDT restrictions, overnight trend continuation
- **⚠️ Disadvantage:** Overnight gap risk

### **Option 2: Selective Day Trading**
- **Weekly limit:** Use only 3 best setups per week
- **Position sizing:** Higher capital allocation per trade
- **Entry criteria:** Very strict signal confirmation
- **✅ Advantage:** Intraday risk control, no overnight gaps
- **⚠️ Disadvantage:** Limited opportunities, timing pressure

### **Option 3: Cash Account Trading**
- **Account type:** Switch from margin to cash account
- **PDT rules:** **No PDT rules apply to cash accounts**
- **Settlement:** Must wait T+2 before reusing funds
- **✅ Advantage:** Unlimited day trades
- **⚠️ Disadvantage:** Capital efficiency reduced, fund rotation delays

---

## 📈 Bot Configuration Analysis

### **PDT-Friendly Aspects:**
- ✅ **15Min timeframe** suitable for swing trades
- ✅ **8-hour max hold time** allows overnight positions
- ✅ **Conservative stops/targets** appropriate for longer holds
- ✅ **Multi-strategy approach** provides flexibility
- ✅ **Real PnL monitoring** works for any timeframe

### **PDT-Problematic Aspects:**
- ❌ **6 daily trades limit** exceeds PDT allowance
- ❌ **Multi-stock rotation** could trigger multiple day trades
- ❌ **Intraday focus** conflicts with overnight holding needs
- ❌ **High frequency mindset** not compatible with PDT limits

---

## 🔧 Recommended Configuration Changes

### **For Accounts Under $25K:**

#### **Config Modifications:**
```python
# Reduce daily trade frequency
MAX_DAILY_TRADES = 3  # Down from 6

# Enable overnight holding
ALLOW_OVERNIGHT_POSITIONS = True
MAX_OVERNIGHT_HOLD_DAYS = 3

# Larger position sizes (fewer trades, more capital per trade)
POSITION_SIZE_MULTIPLIER = 2.0  # Double position sizes

# Stricter entry criteria
MIN_SIGNAL_CONFIDENCE = 0.8  # Up from 0.6
```

#### **Strategy Adjustments:**
1. **Best Setup Priority:** Only trade highest-confidence signals
2. **Position Management:** Hold winning positions 1-3 days
3. **Exit Strategy:** Target 2-5% gains instead of 1.2%
4. **Risk Management:** Wider stops (0.75% instead of 0.45%) for overnight holds

### **For Accounts Over $25K:**
- Current configuration is optimal
- No PDT restrictions
- Can utilize full 6 daily trades
- Maintain intraday focus

---

## 📊 Weekly Trading Examples

### **PDT-Compliant Week (Under $25K):**
```
Monday: Buy IONQ at $12.50 (Hold overnight)
Tuesday: IONQ gaps up to $13.10, Hold for continuation
Wednesday: Sell IONQ at $13.45 (+7.6% gain) (Day Trade #1)
         Buy PG at $164.20 (Hold overnight)
Thursday: PG steady, Hold position
Friday: Buy QBTS at $8.90 (Day Trade #2 if sell same day)
        OR Hold QBTS overnight
```

### **Traditional Day Trading Week (Over $25K):**
```
Monday: IONQ (Day Trade #1), PG (Day Trade #2)
Tuesday: QBTS (Day Trade #3), RGTI (Day Trade #4)
Wednesday: JNJ (Day Trade #5), IONQ (Day Trade #6)
Thursday: Continue with all 5 stocks
Friday: Full rotation possible
```

---

## 🎯 Quantum Stock Considerations

### **Your Watchlist Analysis:**
- **IONQ, QBTS, RGTI:** High volatility quantum plays - good for swing trading
- **PG, JNJ:** Stable large caps - good for overnight holds
- **Mixed approach:** Quantum stocks for momentum, large caps for stability

### **PDT-Optimized Rotation:**
1. **Week 1:** Focus on IONQ and PG (2 trades max)
2. **Week 2:** Focus on QBTS and JNJ (2 trades max)  
3. **Week 3:** Focus on RGTI and best performer (2 trades max)
4. **Flexible trade:** Save 1 trade for unexpected opportunities

---

## 🚀 Implementation Recommendations

### **Immediate Actions:**
1. **Determine account size** and PDT status
2. **Choose strategy approach** (swing vs. selective day trading vs. cash account)
3. **Modify bot configuration** for chosen approach
4. **Test with paper trading** to validate new parameters

### **Bot Modifications Needed:**
- Add PDT compliance tracking
- Implement overnight position management
- Modify position sizing for fewer, larger trades
- Add swing trading exit logic

### **Risk Management:**
- **Gap risk mitigation** for overnight positions
- **Position size calculation** for 3-trade weekly limit
- **Capital allocation** across limited opportunities

---

## 📝 Summary

**Your current intraday bot configuration is actually well-positioned for PDT compliance with minor adjustments.** The 15-minute timeframe and 8-hour hold capability make it ideal for swing trading adaptation.

**Key Decision Point:** Choose between:
1. **Swing Trading Adaptation** (recommended) - modify current system
2. **Cash Account Switch** - unlimited day trades but T+2 settlement
3. **Build to $25K** - maintain current intraday focus

The quantum-focused watchlist provides good diversification between high-volatility plays (quantum stocks) and stable overnight holds (PG, JNJ), making it well-suited for PDT-compliant swing trading.

---

**📄 Document Status:** Complete analysis for future reference  
**🔄 Next Steps:** Review and decide on implementation approach based on account funding timeline
