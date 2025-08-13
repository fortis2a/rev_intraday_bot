# 🎯 How to Set Your Trading Stocks - Quick Guide

## 📍 **Where to Configure Stocks**

Your scalping bot reads stocks from: **`stock_watchlist.py`**

## 🚀 **3 Easy Ways to Set Your Stocks**

### **Method 1: Choose a Pre-Built List (Easiest)**

Open `stock_watchlist.py` and uncomment one of these lines:

```python
# Choose ONE of these:
ACTIVE_WATCHLIST = CONSERVATIVE_WATCHLIST    # ✅ Currently active (Safe)
# ACTIVE_WATCHLIST = AGGRESSIVE_WATCHLIST    # High risk/reward
# ACTIVE_WATCHLIST = TECH_FOCUSED           # Tech stocks only
# ACTIVE_WATCHLIST = FINANCE_FOCUSED        # Bank stocks only
# ACTIVE_WATCHLIST = ETF_ONLY               # ETFs only (safest)
# ACTIVE_WATCHLIST = MY_CUSTOM_STOCKS       # Your custom list
```

### **Method 2: Edit the Custom List**

In `stock_watchlist.py`, find this section and add your stocks:

```python
MY_CUSTOM_STOCKS = [
    "AAPL",  # Apple
    "TSLA",  # Tesla  
    "SPY",   # S&P 500 ETF
    "NVDA",  # Add your favorites here
    "MSFT",  # Microsoft
    # Add more...
]
```

Then activate it:
```python
ACTIVE_WATCHLIST = MY_CUSTOM_STOCKS  # Uncomment this line
```

### **Method 3: Direct Edit (Advanced)**

Edit `config.py` directly around line 76 to modify the default list.

## 📊 **Pre-Built Watchlists Available**

| List Name | Stocks | Risk Level | Best For |
|-----------|--------|------------|----------|
| `CONSERVATIVE_WATCHLIST` | 11 stocks | Low | Beginners |
| `AGGRESSIVE_WATCHLIST` | 12 stocks | High | Experienced |
| `TECH_FOCUSED` | 10 stocks | Medium | Tech sector |
| `FINANCE_FOCUSED` | 10 stocks | Medium | Bank sector |
| `ENERGY_FOCUSED` | 8 stocks | High | Energy sector |
| `ETF_ONLY` | 10 ETFs | Low | Safest option |

## 🎯 **Current Active Stocks**

Your bot is currently set to trade: **11 stocks**
- AAPL, MSFT, GOOGL, AMZN (Tech)
- JPM, BAC, V, MA (Finance)  
- SPY, QQQ, IWM (ETFs)

## ⚡ **Quick Stock Changes**

### Want to trade only AAPL and TSLA?
```python
MY_CUSTOM_STOCKS = ["AAPL", "TSLA"]
ACTIVE_WATCHLIST = MY_CUSTOM_STOCKS
```

### Want to trade only ETFs (safest)?
```python
ACTIVE_WATCHLIST = ETF_ONLY  # Uncomment this line
```

### Want high-risk momentum stocks?
```python
ACTIVE_WATCHLIST = AGGRESSIVE_WATCHLIST  # Uncomment this line
```

## 🔍 **Stock Filtering**

The bot automatically filters your watchlist based on:
- ✅ Minimum volume: 1M shares/day
- ✅ Price range: $10 - $200
- ✅ Max spread: 0.1%
- ✅ Volatility: 0.5% - 5.0%

## 🧪 **Test Your Stock List**

```bash
# Test with your stocks
python stock_watchlist.py

# Test bot with current watchlist
python scalping_bot.py --test AAPL

# See current config
python -c "from config import config; print(config.SCALPING_WATCHLIST)"
```

## ⚠️ **Important Notes**

1. **Start Small**: Begin with 3-5 liquid stocks
2. **High Volume**: Choose stocks with 1M+ daily volume
3. **Avoid Penny Stocks**: Stay above $10/share
4. **ETFs are Safer**: SPY, QQQ, IWM are very liquid
5. **Test First**: Always test with paper trading

## 🎯 **Recommended Starting Lists**

### **For Beginners**
```python
MY_CUSTOM_STOCKS = ["SPY", "QQQ", "AAPL"]
```

### **For Experienced Traders**
```python
MY_CUSTOM_STOCKS = ["AAPL", "TSLA", "NVDA", "SPY", "QQQ"]
```

---

**🚀 Ready to customize your trading stocks!**
