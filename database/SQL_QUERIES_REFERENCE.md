# Trading Database SQL Queries Reference

This document contains useful SQL queries for analyzing your trading database. The database contains trading activities, daily summaries, and collection logs.

## Database Schema

### Tables Overview
- **`trading_activities`**: Individual trading activities (226 rows)
- **`daily_summaries`**: Daily trading performance summaries (5 rows)
- **`collection_log`**: Data collection tracking (5 rows)
- **`sqlite_sequence`**: SQLite internal sequence tracking

## Basic Queries

### Show All Tables
```sql
SELECT name FROM sqlite_master WHERE type='table';
```

### Table Row Counts
```sql
SELECT 
    'trading_activities' as table_name, COUNT(*) as row_count FROM trading_activities
UNION ALL
SELECT 'daily_summaries', COUNT(*) FROM daily_summaries
UNION ALL
SELECT 'collection_log', COUNT(*) FROM collection_log;
```

## Trading Activities Queries

### Recent Trading Activities
```sql
SELECT symbol, side, quantity, price, value, transaction_time
FROM trading_activities 
ORDER BY transaction_time DESC 
LIMIT 20;
```

### Today's Trading Activities
```sql
SELECT symbol, side, quantity, price, value, transaction_time
FROM trading_activities 
WHERE trade_date = '2025-08-22'
ORDER BY transaction_time DESC;
```

### Activities by Symbol
```sql
SELECT symbol, COUNT(*) as activity_count, SUM(value) as total_volume
FROM trading_activities 
GROUP BY symbol 
ORDER BY activity_count DESC;
```

### Buy vs Sell Activities
```sql
SELECT 
    side,
    COUNT(*) as activity_count,
    SUM(value) as total_volume,
    AVG(price) as avg_price
FROM trading_activities 
GROUP BY side
ORDER BY activity_count DESC;
```

### Hourly Trading Pattern
```sql
SELECT 
    hour,
    COUNT(*) as activity_count,
    SUM(value) as volume,
    COUNT(DISTINCT symbol) as unique_symbols
FROM trading_activities 
GROUP BY hour 
ORDER BY hour;
```

### Most Active Trading Hours
```sql
SELECT 
    hour,
    COUNT(*) as activities,
    SUM(value) as volume
FROM trading_activities 
GROUP BY hour 
ORDER BY activities DESC 
LIMIT 5;
```

### Symbol Performance by Day
```sql
SELECT 
    trade_date,
    symbol,
    COUNT(*) as activities,
    SUM(value) as volume,
    MIN(price) as min_price,
    MAX(price) as max_price,
    AVG(price) as avg_price
FROM trading_activities 
GROUP BY trade_date, symbol 
ORDER BY trade_date DESC, volume DESC;
```

### Large Transactions (> $1000)
```sql
SELECT symbol, side, quantity, price, value, transaction_time
FROM trading_activities 
WHERE value > 1000 
ORDER BY value DESC;
```

### Trading Frequency Analysis
```sql
SELECT 
    trade_date,
    COUNT(*) as total_activities,
    COUNT(DISTINCT symbol) as symbols_traded,
    SUM(value) as daily_volume,
    MIN(transaction_time) as first_trade,
    MAX(transaction_time) as last_trade
FROM trading_activities 
GROUP BY trade_date 
ORDER BY trade_date DESC;
```

## Daily Summaries Queries

### All Daily Summaries
```sql
SELECT 
    trade_date,
    total_trades,
    unique_symbols,
    total_volume,
    cash_flow_pnl,
    trading_pnl
FROM daily_summaries 
ORDER BY trade_date DESC;
```

### Best and Worst Trading Days
```sql
-- Best day by P&L
SELECT trade_date, cash_flow_pnl, total_trades, total_volume
FROM daily_summaries 
ORDER BY cash_flow_pnl DESC 
LIMIT 1;

-- Worst day by P&L
SELECT trade_date, cash_flow_pnl, total_trades, total_volume
FROM daily_summaries 
ORDER BY cash_flow_pnl ASC 
LIMIT 1;
```

### Trading Performance Summary
```sql
SELECT 
    COUNT(*) as trading_days,
    SUM(total_trades) as total_trades,
    SUM(total_volume) as total_volume,
    SUM(cash_flow_pnl) as total_pnl,
    AVG(cash_flow_pnl) as avg_daily_pnl,
    MAX(cash_flow_pnl) as best_day,
    MIN(cash_flow_pnl) as worst_day
FROM daily_summaries;
```

### Profitable vs Losing Days
```sql
SELECT 
    CASE 
        WHEN cash_flow_pnl > 0 THEN 'Profitable'
        WHEN cash_flow_pnl < 0 THEN 'Loss'
        ELSE 'Breakeven'
    END as day_type,
    COUNT(*) as day_count,
    AVG(cash_flow_pnl) as avg_pnl,
    SUM(cash_flow_pnl) as total_pnl
FROM daily_summaries 
GROUP BY 
    CASE 
        WHEN cash_flow_pnl > 0 THEN 'Profitable'
        WHEN cash_flow_pnl < 0 THEN 'Loss'
        ELSE 'Breakeven'
    END;
```

## Advanced Analysis Queries

### Symbol Trading Volume Ranking
```sql
SELECT 
    symbol,
    COUNT(*) as total_activities,
    SUM(value) as total_volume,
    COUNT(DISTINCT trade_date) as trading_days,
    SUM(value) / COUNT(DISTINCT trade_date) as avg_daily_volume
FROM trading_activities 
GROUP BY symbol 
ORDER BY total_volume DESC;
```

### Price Range Analysis by Symbol
```sql
SELECT 
    symbol,
    MIN(price) as min_price,
    MAX(price) as max_price,
    MAX(price) - MIN(price) as price_range,
    AVG(price) as avg_price,
    COUNT(*) as activities
FROM trading_activities 
GROUP BY symbol 
ORDER BY price_range DESC;
```

### Trading Intensity by Day
```sql
SELECT 
    trade_date,
    total_trades,
    trading_hours,
    ROUND(total_trades / trading_hours, 2) as trades_per_hour,
    total_volume / total_trades as avg_trade_size
FROM daily_summaries 
WHERE trading_hours > 0
ORDER BY trades_per_hour DESC;
```

### Side-by-Side Activity Comparison
```sql
SELECT 
    ta.symbol,
    ta.trade_date,
    SUM(CASE WHEN ta.side = 'buy' THEN ta.value ELSE 0 END) as buy_volume,
    SUM(CASE WHEN ta.side IN ('sell', 'sell_short') THEN ta.value ELSE 0 END) as sell_volume,
    COUNT(CASE WHEN ta.side = 'buy' THEN 1 END) as buy_count,
    COUNT(CASE WHEN ta.side IN ('sell', 'sell_short') THEN 1 END) as sell_count
FROM trading_activities ta
GROUP BY ta.symbol, ta.trade_date
ORDER BY ta.trade_date DESC, ta.symbol;
```

### Recent High-Volume Symbols
```sql
SELECT 
    symbol,
    SUM(value) as recent_volume,
    COUNT(*) as recent_activities,
    MAX(transaction_time) as last_activity
FROM trading_activities 
WHERE trade_date >= '2025-08-21'
GROUP BY symbol 
ORDER BY recent_volume DESC;
```

## Data Quality Queries

### Check for Missing Data
```sql
SELECT 
    COUNT(*) as total_records,
    COUNT(symbol) as has_symbol,
    COUNT(price) as has_price,
    COUNT(quantity) as has_quantity,
    COUNT(transaction_time) as has_time
FROM trading_activities;
```

### Duplicate Detection
```sql
SELECT 
    id, COUNT(*) as duplicate_count
FROM trading_activities 
GROUP BY id 
HAVING COUNT(*) > 1;
```

### Data Collection Status
```sql
SELECT 
    collection_date,
    activities_fetched,
    status,
    collection_time
FROM collection_log 
ORDER BY collection_date DESC;
```

## Quick Statistics

### Overall Trading Stats
```sql
SELECT 
    COUNT(*) as total_activities,
    COUNT(DISTINCT symbol) as unique_symbols,
    COUNT(DISTINCT trade_date) as trading_days,
    SUM(value) as total_volume,
    MIN(transaction_time) as first_trade,
    MAX(transaction_time) as last_trade
FROM trading_activities;
```

### Symbol Activity Summary
```sql
SELECT 
    symbol,
    COUNT(*) as activities,
    SUM(value) as volume,
    MIN(price) as min_price,
    MAX(price) as max_price,
    COUNT(DISTINCT trade_date) as active_days
FROM trading_activities 
GROUP BY symbol 
ORDER BY volume DESC;
```

## Usage Notes

### Running Queries
1. Connect to the database: `sqlite3 data/trading.db`
2. Copy and paste any query from above
3. End queries with semicolon (`;`)
4. Use `.exit` to quit SQLite

### Common SQLite Commands
- `.tables` - List all tables
- `.schema table_name` - Show table structure
- `.headers on` - Show column headers
- `.mode column` - Column display mode
- `.quit` or `.exit` - Exit SQLite

### Date Formats
- Database stores dates as: `YYYY-MM-DD`
- Timestamps include timezone: `YYYY-MM-DD HH:MM:SS.ssssss+00:00`

### Tips
- Use `LIMIT` to restrict large result sets
- Use `ORDER BY` to sort results
- Use `WHERE` clauses to filter data
- Use `GROUP BY` for aggregations
- Always backup database before running UPDATE/DELETE queries
