# Auto Sleep/Wake System Documentation

## Overview
The trading bot now includes a comprehensive automatic sleep/wake system that monitors market hours and automatically manages bot operations based on market status.

## ✅ **Auto Sleep/Wake Features**

### 🌙 **Automatic Sleep at Market Close (4:00 PM ET)**
- **When**: Market closes at 4:00 PM Eastern Time
- **Action**: Bot automatically goes to sleep
- **Display**: Shows market closed screen with countdown
- **Behavior**: All trading activities suspended

### 🚀 **Automatic Wake at Market Open (9:30 AM ET)**  
- **When**: Market opens at 9:30 AM Eastern Time
- **Action**: Bot automatically wakes up
- **Display**: Shows market open screen with trading time
- **Behavior**: Resumes all trading activities

### ⏰ **Live Timer & Countdown**
- **Updates**: Every second in real-time
- **Timezone**: US/Eastern (market timezone)
- **Features**: Clear countdown display, weekend detection, holiday awareness
- **Format**: HH:MM:SS countdown format

### 📱 **Market Status Messages**
- **Sleep Mode**: Clear "MARKET CLOSED - BOT SLEEPING" message
- **Wake Mode**: Clear "MARKET OPEN - BOT AWAKENING" message
- **Status Info**: Current time, next open/close, trading time remaining

## 🛠 **Technical Implementation**

### Core Component
- **File**: `core/auto_sleep_wake.py`
- **Class**: `AutoMarketSleepWake`
- **Integration**: Built into main trading engine

### Key Methods
1. **`go_to_sleep()`**: Puts bot to sleep at market close
2. **`wake_up()`**: Wakes bot at market open
3. **`display_market_closed_screen()`**: Shows sleep mode display
4. **`display_market_open_screen()`**: Shows wake mode display
5. **`run_auto_system()`**: Main 24/7 monitoring loop

### Market Status Detection
- **API**: Uses Alpaca market calendar API
- **Fallback**: Time-based checking if API fails
- **Accuracy**: Real-time market status detection
- **Holidays**: Automatically handles market holidays

## 🚀 **How to Use**

### Method 1: Launcher Menu
1. Run: `python launcher.py`
2. Select option **15**: "Auto Sleep/Wake Mode (24/7 with market monitoring)"
3. Bot automatically manages sleep/wake cycles

### Method 2: Standalone Operation
```bash
python core/auto_sleep_wake.py
```

### Method 3: Integrated Trading Engine
- Auto sleep/wake is built into the main trading engine
- When you start trading (options 1-3), it automatically includes sleep/wake
- No additional setup required

## 📊 **Display Examples**

### Market Closed Display
```
================================================================================
                    🌙 MARKET CLOSED - BOT SLEEPING 🌙
================================================================================

[CURRENT TIME] 2025-08-13 20:28:46 EDT
[STATUS] Market is CLOSED - Bot automatically sleeping

[NEXT OPEN] 2025-08-14 09:30:00 EDT
[COUNTDOWN] Time Until Wake: 13:01:13
[INFO] Next trading day is Thursday
[INFO] Market reopens tomorrow morning

================================================================================
[AUTO] Bot will automatically wake up when market opens at 9:30 AM ET
[AUTO] All trading activities are suspended during market closure
[INFO] Press Ctrl+C to stop the auto sleep/wake system
================================================================================
```

### Market Open Display
```
================================================================================
                    🚀 MARKET OPEN - BOT AWAKENING 🚀
================================================================================

[CURRENT TIME] 2025-08-14 09:30:15 EDT
[STATUS] Market is OPEN - Bot automatically awakening

[MARKET CLOSE] 2025-08-14 16:00:00 EDT
[TRADING TIME] 06:29:45 remaining
[INFO] Full trading day ahead

================================================================================
[AUTO] Bot is now active and ready for trading
[AUTO] All trading systems will start automatically
[AUTO] Bot will automatically sleep when market closes at 4:00 PM ET
================================================================================
```

## ⚙️ **Configuration**

### Market Hours
- **Open**: 9:30 AM Eastern Time
- **Close**: 4:00 PM Eastern Time (16:00)
- **Timezone**: Automatically handled (US/Eastern)
- **Weekends**: Automatically detected and handled
- **Holidays**: Uses Alpaca market calendar

### Update Frequency
- **Timer**: Updates every 1 second
- **Market Check**: Continuous monitoring
- **Screen Refresh**: Real-time clearing and updating

## 🔧 **Integration Points**

### Main Trading Engine
- **File**: `main.py`
- **Integration**: `AutoMarketSleepWake` class imported
- **Behavior**: Trading loop includes market transition checks
- **Fallback**: Graceful handling if sleep/wake system fails

### Launcher Integration
- **Menu Option**: Option 15 in main menu
- **Standalone**: Can run independently
- **Error Handling**: Graceful exit on errors

### Logging
- **Logger**: `auto_sleep_wake` logger
- **Events**: Sleep/wake transitions logged
- **Errors**: All errors logged with details

## 🧪 **Testing**

### Demo Script
```bash
python demo_auto_sleep_wake.py
```

### Test Commands
```bash
# Test standalone system
python core/auto_sleep_wake.py

# Test integrated system
python main.py --mode LIVE

# Test launcher integration
python launcher.py
# Select option 15
```

## 🔍 **Monitoring & Logs**

### Log Files
- **Location**: `logs/auto_sleep_wake_YYYYMMDD.log`
- **Events**: Sleep/wake transitions, errors, status changes
- **Format**: Standard log format with timestamps

### Status Indicators
- **Sleep Mode**: 🌙 icon, "BOT SLEEPING" message
- **Wake Mode**: 🚀 icon, "BOT AWAKENING" message
- **Countdown**: Live HH:MM:SS format
- **Market Info**: Next open/close times

## ⚠️ **Error Handling**

### API Failures
- **Fallback**: Time-based market detection
- **Logging**: Error details logged
- **Behavior**: Continues operation with warnings

### Threading Issues
- **Safety**: Safe thread termination
- **Cleanup**: Proper resource cleanup
- **Recovery**: Automatic recovery from thread errors

### Display Issues
- **Fallback**: Text-only display if screen clear fails
- **Compatibility**: Works on Windows, Mac, Linux
- **Terminal**: Handles various terminal types

## 🚀 **Benefits**

### For Users
- ✅ **24/7 Operation**: Set it and forget it
- ✅ **Market Awareness**: Always knows market status
- ✅ **Visual Feedback**: Clear status displays
- ✅ **Time Management**: Accurate countdown timers

### For System
- ✅ **Resource Efficiency**: No unnecessary API calls during closed hours
- ✅ **Risk Management**: Prevents trading during closed markets
- ✅ **Reliability**: Automatic recovery and error handling
- ✅ **Compliance**: Respects market hours and holidays

## 📋 **Status: ✅ COMPLETE**

The auto sleep/wake system is fully implemented and ready for 24/7 operation!

### Current Features
- ✅ Automatic sleep at 4:00 PM ET
- ✅ Automatic wake at 9:30 AM ET  
- ✅ Live countdown timers
- ✅ Market status messages
- ✅ Real-time updates every second
- ✅ Weekend/holiday detection
- ✅ Launcher integration (option 15)
- ✅ Standalone operation
- ✅ Full logging and monitoring

---
*Implemented: August 13, 2025*
*Status: Ready for production use*
*Integration: Complete across all systems*
