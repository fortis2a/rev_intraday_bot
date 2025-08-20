# Interactive Trading Dashboard

This folder contains all files related to the Interactive Trading Dashboard system.

## Structure

```
dashboard/
├── interactive_dashboard.py          # Main dashboard application
├── interactive_dashboard_demo.html   # Demo HTML file
├── start_interactive_dashboard.bat   # Windows launcher
├── start_interactive_dashboard.ps1   # PowerShell launcher
├── scripts/                          # Alternative dashboard implementations
│   ├── dash_dashboard.py
│   ├── enhanced_executive_dashboard.py
│   ├── executive_dashboard.py
│   ├── interactive_dashboard_options.py
│   ├── live_dashboard.py
│   ├── simple_readable_dashboard.py
│   └── streamlit_dashboard.py
└── docs/                             # Documentation
    ├── DASHBOARD_IMPLEMENTATION_COMPLETE.md
    ├── DASHBOARD_UPDATE_SUMMARY.md
    └── DATA_DISCREPANCY_ANALYSIS.md
```

## Quick Start

### From Root Directory (Recommended)
```bash
# Launch from project root
python launch_dashboard.py

# Or use batch file
launch_dashboard.bat
```

### Direct Launch
```bash
# From dashboard folder
cd dashboard
python interactive_dashboard.py
```

## Features

- **Real-time Data**: Live connection to Alpaca API
- **Dark Theme**: Professional CYBORG theme with cyan accents
- **Interactive Charts**: Plotly-based charts with zoom, pan, hover
- **Date Filtering**: Calendar picker for single-day or range selection
- **Comprehensive Analytics**: P&L, win rates, risk metrics
- **Auto-refresh**: Updates every 30 seconds
- **Mobile Friendly**: Responsive design

## Access

Once running, the dashboard is available at:
- **Local**: http://localhost:8050
- **Network**: http://192.168.1.65:8050

## Data Sources

- **Account Information**: Live from Alpaca API
- **Trading Data**: Real-time order and position data
- **Market Data**: Current prices and volumes

## Technical Details

- **Framework**: Dash (Plotly)
- **UI Components**: dash-bootstrap-components
- **Theme**: CYBORG (dark theme)
- **Backend**: Python 3.13+
- **Dependencies**: See requirements.txt

## Troubleshooting

1. **Port 8050 in use**: Stop other dashboard instances
2. **Module not found**: Install requirements: `pip install -r requirements.txt`
3. **API connection**: Check Alpaca API credentials in .env file

## Related Files

- **Market Reports**: `market_close_report.py` (static HTML reports)
- **Configuration**: `config.py`, `stock_specific_config.py`
- **Data Management**: `data_manager.py`

## Documentation

See `docs/` folder for detailed implementation notes and troubleshooting guides.
