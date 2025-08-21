# Trading Analytics Suite 📊

This suite provides comprehensive trading analysis through both **static reports** and an **interactive dashboard**.

## 🔧 Setup

1. **Install Required Packages:**
   ```bash
   pip install dash plotly dash-bootstrap-components
   ```

2. **Environment Variables:**
   Ensure your `.env` file contains:
   ```
   ALPACA_API_KEY=your_api_key
   ALPACA_SECRET_KEY=your_secret_key
   ALPACA_BASE_URL=https://paper-api.alpaca.markets
   ```

## 📈 Static Market Close Report

### Usage
- **Script:** `market_close_report.py`
- **Launcher:** `generate_market_close_report.bat`

### Features
- Comprehensive end-of-day analysis
- Statistical analysis with advanced metrics
- Risk analysis (Sharpe, Sortino, VaR, Kelly Criterion)
- Trading psychology insights
- Technical terms glossary
- Archived HTML reports

### Generated Files
- `reports/YYYY-MM-DD/market_close_report_YYYYMMDD.html`
- `reports/YYYY-MM-DD/trading_charts_YYYYMMDD.png`
- `reports/YYYY-MM-DD/statistical_analysis_YYYYMMDD.png`

---

## 🚀 Interactive Dashboard

### Usage
- **Script:** `interactive_dashboard.py`
- **Launcher:** `start_interactive_dashboard.bat` or `start_interactive_dashboard.ps1`
- **URL:** http://localhost:8050

### Features

#### 🎯 **Real-Time Interactivity**
- Auto-refresh every 30 seconds
- Live data from Alpaca API
- Responsive design (mobile-friendly)

#### 🔍 **Interactive Filters**
- **Date Range:** 1, 3, 7, 14, or 30 days
- **Symbol Selection:** Filter by specific stocks
- **Trade Side:** All, Long only, or Short only
- **Manual Refresh:** Force data update

#### 📊 **Key Metrics Dashboard**
- Total Orders & Completed Trades
- Total P&L with color coding
- Win Rate percentage
- Total Volume traded
- Number of symbols

#### 📈 **Interactive Charts**

1. **Equity Curve**
   - Real-time cumulative P&L
   - Hover for trade details
   - Zoom and pan capabilities

2. **P&L Distribution**
   - Histogram with mean/median lines
   - Statistical distribution analysis
   - Interactive bins

3. **Symbol Performance**
   - Horizontal bar chart by symbol
   - Color-coded profit/loss
   - Sortable results

4. **Hourly Performance**
   - Trading volume by hour
   - P&L overlay line chart
   - Dual Y-axis display

5. **Trade Size Analysis**
   - Scatter plot: Quantity vs Value
   - Color-coded by trade size
   - Symbol identification on hover

6. **Risk Metrics**
   - Live Sharpe & Sortino ratios
   - Max Drawdown tracking
   - Value at Risk (VaR 95%)

### Navigation
- **Responsive Design:** Works on desktop, tablet, and mobile
- **Zoom Controls:** Click and drag to zoom charts
- **Hover Information:** Detailed data on mouse hover
- **Filter Combinations:** Mix and match filters for detailed analysis

---

## 🔄 Workflow Recommendations

### Daily Routine
1. **Morning:** Launch interactive dashboard for real-time monitoring
2. **Trading Day:** Use dashboard filters to analyze current performance
3. **End of Day:** Generate static report for permanent record

### Analysis Workflow
1. **Quick Check:** Dashboard metrics cards for immediate overview
2. **Performance Review:** Equity curve and P&L distribution
3. **Strategy Analysis:** Symbol and hourly performance charts
4. **Risk Assessment:** Risk metrics and trade size analysis
5. **Documentation:** Static report for detailed records

---

## ⚙️ Technical Details

### Dashboard Architecture
- **Frontend:** Dash/Plotly with Bootstrap components
- **Backend:** Flask server with Alpaca API integration
- **Updates:** WebSocket-based real-time data
- **Caching:** Efficient data fetching and processing

### Static Report Features
- **Charts:** High-resolution PNG exports (300 DPI)
- **Analysis:** 24+ statistical metrics
- **Formatting:** Professional HTML with CSS styling
- **Archival:** Timestamped permanent records

### Performance
- **Dashboard Load Time:** ~2-3 seconds
- **Data Refresh:** 30-second intervals
- **Chart Rendering:** Sub-second updates
- **Memory Usage:** ~50-100MB typical

---

## 🛠️ Troubleshooting

### Common Issues

1. **Dashboard Won't Start**
   ```bash
   # Check if port 8050 is available
   netstat -an | findstr :8050
   
   # Try different port
   python interactive_dashboard.py --port 8051
   ```

2. **No Data Showing**
   - Verify Alpaca API credentials
   - Check date range (try longer periods)
   - Ensure trades exist in selected timeframe

3. **Charts Not Loading**
   - Clear browser cache
   - Try incognito/private browsing mode
   - Check browser console for errors

4. **Static Report Generation Fails**
   - Verify matplotlib installation
   - Check file permissions in reports directory
   - Ensure sufficient disk space

### Support
- Check logs in terminal/command prompt
- Verify API connectivity with test script
- Review error messages for specific issues

---

## 🎯 Feature Comparison

| Feature | Static Report | Interactive Dashboard |
|---------|---------------|----------------------|
| **Data Freshness** | End-of-day snapshot | Real-time updates |
| **Interactivity** | None | Full interactive |
| **Archival** | Permanent HTML files | Session-based |
| **Filtering** | Pre-configured | Dynamic filters |
| **Mobile Support** | Basic | Optimized |
| **Sharing** | File-based | URL-based |
| **Analysis Depth** | Comprehensive | Focused |
| **Performance** | Fast generation | Real-time processing |

Both tools complement each other perfectly for comprehensive trading analysis! 🎉
