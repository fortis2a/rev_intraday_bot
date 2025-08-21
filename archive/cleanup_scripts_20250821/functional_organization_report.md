# Functional Organization Report
Date: 2025-08-21 18:00:57

## Summary
- Files organized: 13
- Directories created: 4
- Files remaining in root: 6
- Errors: 0

## Organization Structure

### Core System Files (Root Directory)
Essential trading system components that remain in root:
- config.py (8.4KB)
- launcher.py (43.6KB)
- main.py (33.2KB)
- organize_by_function.py (11.0KB)
- stock_specific_config.py (18.2KB)
- strategies.py (17.6KB)

### Monitoring Directory
Monitoring & Dashboard Files - Live system monitoring
- launch_dashboard.py (2.1KB)
- live_dashboard.py (69.8KB)
- realtime_status_monitor.py (12.3KB)
- system_status.py (0.8KB)

### Reporting Directory
Reporting & Analysis Files - P&L and trading analysis
- enhanced_daily_analysis.py (13.7KB)
- generate_todays_pnl.py (6.0KB)
- market_close_report.py (100.5KB)
- today_analysis.py (10.7KB)

### Emergency Directory
Emergency & Position Control - Critical trading controls
- check_and_force_close.py (3.9KB)
- emergency_close_all.py (3.5KB)
- force_close_all.py (3.5KB)

### Utilities Directory
Trading Utilities - Support tools and helpers
- check_positions_orders.py (1.4KB)
- start_intraday.py (1.7KB)

## Files Moved
- live_dashboard.py → monitoring/
- launch_dashboard.py → monitoring/
- realtime_status_monitor.py → monitoring/
- system_status.py → monitoring/
- market_close_report.py → reporting/
- enhanced_daily_analysis.py → reporting/
- generate_todays_pnl.py → reporting/
- today_analysis.py → reporting/
- emergency_close_all.py → emergency/
- force_close_all.py → emergency/
- check_and_force_close.py → emergency/
- check_positions_orders.py → utilities/
- start_intraday.py → utilities/
