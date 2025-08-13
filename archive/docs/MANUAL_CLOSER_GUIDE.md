# Manual Trade Closer - Usage Guide

## 🔄 Manual Trade Closer

Interactive tool for manually closing open trading positions with full control over quantity and confirmation.

### 🚀 Quick Start

#### 1. Interactive Mode (Recommended)
```bash
python manual_closer.py
```
- Shows all open positions with P&L
- Select which position to close
- Choose quantity (all, half, or specific amount)
- Confirm before executing

#### 2. Close Specific Symbol
```bash
python manual_closer.py --symbol IONQ --batch
```
- Closes all positions for IONQ symbol
- No interactive prompts

#### 3. Close ALL Positions (Use with Caution!)
```bash
python manual_closer.py --close-all --batch
```
- Closes every open position
- Emergency use only

### 📊 Features

**Position Display:**
- Real-time P&L calculation
- Entry price vs current price
- Percentage gains/losses
- Total portfolio P&L

**Quantity Options:**
- `all` - Close entire position
- `half` - Close 50% of position  
- `25` - Close specific number of shares
- `q` - Cancel and return

**Safety Features:**
- Confirmation required for each trade
- Shows estimated P&L impact
- Graceful cancellation (Ctrl+C)
- Error handling and logging

**Order Types:**
- Market orders for immediate execution
- Handles wash trade conflicts
- Manages insufficient quantity errors
- Proper price rounding for compliance

### 🛡️ Error Handling

The script automatically handles:
- **Wash Trade Errors**: Cancels conflicting orders and retries
- **Insufficient Quantity**: Uses available quantity for partial closes
- **Connection Issues**: Graceful retry and error reporting
- **Sub-penny Pricing**: Rounds to valid tick increments

### ⚠️ Important Notes

1. **Market Orders**: All closes use market orders for immediate execution
2. **Paper Trading**: Respects your current Alpaca environment setting
3. **Logging**: All activities are logged for audit trail
4. **Position Refresh**: Positions are refreshed before each operation
5. **Partial Closes**: Supports closing part of a position

### 🎯 Example Interactive Session

```
📊 CURRENT OPEN POSITIONS
================================================================================
#   Symbol   Side   Qty      Entry      Current    P&L          P&L%
--------------------------------------------------------------------------------
1   IONQ     LONG   50       $46.50     $46.39     🔴 $-5.50     -0.2%
2   AAPL     SHORT  25       $183.50    $183.49    🟢 $+0.25     +0.0%
================================================================================

🎯 Select position to close (1-2) or 'q' to quit: 1

📊 Position: IONQ - LONG 50 shares
💰 Current P&L: $-5.50 (-0.2%)

🔢 Quantity to close:
   • Enter number (1-50)
   • Enter 'all' to close entire position
   • Enter 'half' to close half position
   • Enter 'q' to cancel

Quantity: 25

🔍 TRADE CONFIRMATION
==================================================
Symbol: IONQ
Action: SELL 25 shares
Current Position: LONG 50 shares
Market Price: $46.39
Estimated P&L: $-2.75
Remaining Position: LONG 25 shares
==================================================

Execute this trade? (y/n): y

🚀 Executing SELL order for 25 shares of IONQ...
✅ Order submitted successfully!
   Order ID: 12345678-1234-1234-1234-123456789012
   Symbol: IONQ
   Side: SELL
   Quantity: 25
   Type: MARKET
```

### 🔧 Integration

The script integrates with your existing trading system:
- Uses the same OrderManager as the main bot
- Inherits all error handling improvements
- Respects configuration settings
- Works with both paper and live trading
