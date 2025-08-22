🎛️ LAUNCHER.PY vs MAIN.PY - The Control Hierarchy
launcher.py - Master Control Center
Purpose: Controls and orchestrates ALL trading system components
Functionality: Menu-driven interface with multiple options
Controls: main.py, dashboards, P&L monitors, reports, etc.
Features: Process management, monitoring, restart capabilities

main.py - Single Trading Engine
Purpose: Just the core trading engine
Functionality: Only intraday trading logic
Limited: No control over other components
Scope: Single-purpose execution