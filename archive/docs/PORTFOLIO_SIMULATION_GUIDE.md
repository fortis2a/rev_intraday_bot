# 🧪 $2,000 Portfolio Simulation - Risk Breakdown

## ✅ **Simulation Active**
Your bot is now using a **$2,000 simulated portfolio** instead of your full Alpaca account balance.

### **📊 Your Risk Parameters with $2,000:**

#### **Daily Loss Limits:**
- **5% daily loss limit** = **$100 max loss per day**
- **Real account**: $102,159 (protected - not being used)
- **Simulated account**: $2,000 (what the bot calculates with)

#### **Position Sizing:**
- **1% risk per trade** = **$20 risk per trade**
- **IONQ at $46.39**:
  - With 0.15% stop loss = $46.32 stop price
  - Risk per share = $0.07
  - **Position size** = $20 ÷ $0.07 = **~285 shares max**
  - **Position value** = 285 × $46.39 = **~$13,221**

#### **Wait - Position Size Issue! ⚠️**

The calculated position size ($13,221) is **much larger than your $2,000 portfolio**! This happens because:

1. **IONQ is expensive** ($46.39/share)
2. **Small stop loss** (0.15% = only $0.07 risk per share)
3. **1% account risk** ($20) ÷ $0.07 = way too many shares

## 🔧 **Let's Fix This!**

I need to adjust the position sizing logic to respect the simulated portfolio size.

### **Realistic Numbers for $2,000 Portfolio:**
- **Max position value**: 40% of portfolio = $800
- **IONQ shares**: $800 ÷ $46.39 = **~17 shares**
- **Risk per trade**: 17 shares × $0.07 = **$1.19**
- **Actual risk %**: $1.19 ÷ $2,000 = **0.06%** (very conservative)

### **Options to Fix:**
1. **Lower the position value limits** in config
2. **Choose cheaper stocks** (under $20/share)
3. **Use wider stop losses** for expensive stocks
4. **Increase risk per trade** to 2-3% for small accounts

---

**The simulation is working, but we need to adjust position sizing for realistic $2,000 trading!**
