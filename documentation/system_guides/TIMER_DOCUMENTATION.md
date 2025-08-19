# Market Timer Feature Documentation

## Overview
The Intraday Trading Bot now includes a comprehensive market timer system that displays the current time and countdown to market open when the market is closed.

## Features

### 1. Automatic Status Display
- **Location**: Main launcher status screen
- **When**: Always visible when market is closed
- **Shows**: 
  - Current time
  - Next market open time (Eastern Time)
  - Countdown in HH:MM:SS format

### 2. Live Timer Mode (Option 14)
- **Access**: Select option 14 from main menu
- **Features**:
  - Full-screen live countdown
  - Updates every second
  - Timezone-aware calculations
  - Press Ctrl+C to return to menu

### 3. Smart Market Detection
- **Market Status**: Automatically detects if market is open/closed
- **Timezone Handling**: All times converted to US/Eastern (market timezone)
- **Weekend Awareness**: Displays appropriate messages for weekends
- **Holiday Support**: Uses Alpaca's market calendar for accurate timing

## Technical Implementation

### Components Added
1. **show_market_countdown()**: Static countdown display for status screen
2. **start_live_timer()**: Interactive live timer with real-time updates
3. **Menu Integration**: Added option 14 to main menu
4. **Error Handling**: Graceful fallbacks for API errors

### Dependencies
- `pytz`: For timezone calculations
- `datetime`: For time manipulation
- `threading`: For live timer updates
- `data_manager`: For market status from Alpaca API

### Code Locations
- **File**: `launcher.py`
- **Methods**: 
  - `show_market_countdown()` (lines ~65-100)
  - `start_live_timer()` (lines ~100-180)
  - Menu integration (lines ~590-600)

## Usage Examples

### 1. Basic Status Display
```
======================================================================
           INTRADAY TRADING SYSTEM STATUS
======================================================================
[CLOSED] Market Status: CLOSED
[TIME] Current Time: 2025-08-13 20:12:45
[COUNTDOWN] Next Market Open: 2025-08-14 09:30:00 EDT
[COUNTDOWN] Time Until Open: 13:17:14
======================================================================
```

### 2. Live Timer Mode
```
======================================================================
           LIVE MARKET TIMER
======================================================================
[LIVE TIME] 2025-08-13 20:11:57
[STATUS] Market is CLOSED
[NEXT OPEN] 2025-08-14 09:30:00 EDT
[COUNTDOWN] 13:18:02
======================================================================
Press Ctrl+C to stop
```

## Menu Integration

The launcher menu now includes:
```
14. Live Market Timer (Shows countdown when closed)
```

## Error Handling

### API Errors
- Graceful fallback if Alpaca API is unavailable
- Clear error messages for debugging
- No crash if market data is unavailable

### Timezone Errors
- Defaults to current system time if timezone conversion fails
- Clear error logging for troubleshooting

### Threading Errors
- Safe thread termination on Ctrl+C
- Prevents hanging processes

## Configuration

### Requirements
- Alpaca API credentials (same as trading bot)
- Python packages: `pytz`, `datetime`, `threading`
- Network access for market data

### Settings
- Update frequency: 1 second for live timer
- Timezone: US/Eastern (hardcoded for stock market)
- Display format: 24-hour time format

## Testing

### Test Scripts
1. **test_timer.py**: Basic functionality test
2. **live_timer_demo.py**: Standalone live timer demo
3. **demo_timer_features.py**: Feature overview

### Test Cases
- ✅ Market closed countdown
- ✅ Market open display
- ✅ Timezone conversion
- ✅ Weekend detection
- ✅ Error handling
- ✅ Live updates
- ✅ Menu integration

## Future Enhancements

### Planned Features
- [ ] Pre-market and after-hours timing
- [ ] Holiday calendar integration
- [ ] Customizable update frequency
- [ ] Sound alerts for market open
- [ ] Email notifications

### Possible Improvements
- [ ] Multiple timezone support
- [ ] Market news integration
- [ ] Economic calendar events
- [ ] Custom countdown targets

## Troubleshooting

### Common Issues

1. **"Unable to determine next market open time"**
   - Check Alpaca API connection
   - Verify network connectivity
   - Check API credentials

2. **Incorrect timezone display**
   - Ensure `pytz` package is installed
   - Check system timezone settings
   - Verify Eastern Time calculation

3. **Timer not updating**
   - Check if live timer thread is running
   - Verify no blocking operations
   - Check for Ctrl+C interruption

### Debug Commands
```bash
# Test basic timer functionality
python test_timer.py

# Test live timer
python live_timer_demo.py

# Test launcher integration
python launcher.py
# Then select option 14
```

## Support

For issues or questions:
1. Check log files in `/logs/` directory
2. Run test scripts to isolate problems
3. Verify Alpaca API connectivity
4. Check Python package installations

---

*Last Updated: August 13, 2025*
*Version: 1.0*
