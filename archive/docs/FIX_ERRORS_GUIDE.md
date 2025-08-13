# 🔑 Quick Setup Guide - Fix the Errors

## 🚨 **Current Issues:**
1. ❌ Missing Alpaca API credentials
2. ✅ **FIXED** - Updated watchlist to 5 stocks (IONQ, AAPL, TSLA, SPY, QQQ)

## 🔧 **How to Fix API Credentials:**

### **Step 1: Get Alpaca API Keys (FREE)**
1. Go to: https://app.alpaca.markets/signup
2. Sign up for a **FREE** paper trading account
3. Go to: https://app.alpaca.markets/paper/dashboard/overview
4. Click "Generate API Key"
5. Copy your **API Key** and **Secret Key**

### **Step 2: Update .env File**
Open `.env` file and replace:
```env
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
```

With your actual keys:
```env
ALPACA_API_KEY=PKTEST1234567890abcdef  # Your actual key
ALPACA_SECRET_KEY=abcdef1234567890     # Your actual secret
```

### **Step 3: Test the Bot**
```bash
# Test environment
python scalping_bot.py --validate-only

# Test with your quantum stock
python scalping_bot.py --test IONQ

# Run paper trading
python scalping_bot.py --dry-run
```

## 🎯 **Your Current Stock List:**
- **IONQ** - Quantum computing (your choice)
- **AAPL** - Apple (stable, high volume)
- **TSLA** - Tesla (good volatility for scalping)
- **SPY** - S&P 500 ETF (very liquid)
- **QQQ** - NASDAQ ETF (tech exposure)

## ⚠️ **Important Notes:**
- **Paper Trading Only**: Start with paper trading (no real money)
- **FREE Account**: Alpaca paper trading is completely free
- **No Credit Card**: Paper trading requires no payment info
- **Quantum Focus**: IONQ is included as requested, but mixed with stable stocks

## 🚀 **After Setting Up API Keys:**
```bash
# This should work without errors:
python scalping_bot.py --validate-only
```

---
**🎯 Once you add your API keys, the bot will be ready to paper trade!**
