# 📁 Scalping Bot System - Workspace Organization

## 🗂️ **Directory Structure**

```
Scalping Bot System/
├── 📁 core/                    # Core trading engine components
│   ├── scalping_engine.py      # Main trading engine
│   ├── risk_manager.py         # Risk management system
│   ├── order_manager.py        # Order execution system
│   └── data_manager.py         # Market data management
│
├── 📁 strategies/              # Trading strategy implementations
│   ├── momentum_scalp.py       # Momentum-based scalping
│   ├── mean_reversion.py       # Mean reversion strategy
│   └── vwap_bounce.py          # VWAP bounce strategy
│
├── 📁 utils/                   # Utility modules
│   ├── alpaca_trader.py        # Alpaca broker integration
│   └── logger.py               # Logging configuration
│
├── 📁 reports/                 # Trading reports and analysis
│   ├── trading_analysis_baseline_2025-07-28.md  # Baseline analysis
│   └── *.csv                   # Trading data exports
│
├── 📁 logs/                    # System logs
│   └── *.log                   # Daily trading logs
│
├── 📁 analysis/                # 🆕 Analysis scripts and tools
│   ├── rule_violation_analysis.py      # Rule compliance analysis
│   ├── execution_flaw_analysis.py      # Execution bug analysis
│   ├── qbts_strategy_analysis.py       # QBTS trade analysis
│   ├── pnl_discrepancy_analysis.py     # P&L calculation analysis
│   └── trading_analysis.py             # General trading analysis
│
├── 📁 tests/                   # 🆕 Testing and validation
│   └── validate_bug_fixes.py           # Bug fix validation tests
│
├── 📁 docs/                    # 🆕 Documentation
│   ├── BUG_FIX_SUMMARY.md              # Critical bug fix documentation
│   └── CRITICAL_BUG_ANALYSIS.md        # Detailed bug analysis
│
├── 📁 temp_files/             # 🆕 Temporary and debug files
│   └── debug_orders.py                 # Debug utilities
│
├── 📁 data/                   # Market data storage
├── 📁 Futures Scalping Bot/   # Futures trading system
├── config.py                  # Configuration settings
├── scalping_bot.py           # Main bot launcher
└── README.md                 # Project documentation
```

## 🎯 **Folder Purposes**

### 📊 **analysis/** 
Contains scripts for analyzing trading performance, investigating issues, and validating strategy effectiveness.

- **Purpose**: Post-trade analysis, performance investigation, bug detection
- **Usage**: Run these scripts to understand trading patterns and identify issues
- **Key Files**: 
  - `rule_violation_analysis.py` - Checks compliance with trading rules
  - `execution_flaw_analysis.py` - Analyzes order execution problems
  - `qbts_strategy_analysis.py` - Deep dive into QBTS trading issues

### 🧪 **tests/**
Contains validation scripts and test suites for ensuring system reliability.

- **Purpose**: System testing, bug fix validation, integration testing
- **Usage**: Run before deploying changes to validate fixes
- **Key Files**:
  - `validate_bug_fixes.py` - Tests critical bug fixes

### 📚 **docs/**
Contains comprehensive documentation about bugs, fixes, and system analysis.

- **Purpose**: Knowledge base, bug tracking, system documentation
- **Usage**: Reference for understanding issues and solutions
- **Key Files**:
  - `BUG_FIX_SUMMARY.md` - Executive summary of critical fixes
  - `CRITICAL_BUG_ANALYSIS.md` - Detailed technical analysis

### 🗃️ **temp_files/**
Contains temporary scripts, debug utilities, and experimental code.

- **Purpose**: Development utilities, debugging tools, temporary scripts
- **Usage**: Development and debugging support
- **Key Files**:
  - `debug_orders.py` - Order debugging utilities

## 🚀 **Quick Navigation**

| Task | Go To |
|------|-------|
| **Analyze trading performance** | `analysis/` folder |
| **Test bug fixes** | `tests/` folder |
| **Read documentation** | `docs/` folder |
| **Debug issues** | `temp_files/` folder |
| **Check trading reports** | `reports/` folder |
| **Review system logs** | `logs/` folder |
| **Modify core logic** | `core/` folder |
| **Adjust strategies** | `strategies/` folder |
| **Configure settings** | `config.py` |

## 📋 **Best Practices**

### **For Analysis**:
1. Add new analysis scripts to `analysis/` folder
2. Include clear documentation and output formatting
3. Use consistent naming: `[topic]_analysis.py`

### **For Testing**:
1. Add validation scripts to `tests/` folder
2. Include comprehensive test coverage
3. Use naming: `test_[feature].py` or `validate_[feature].py`

### **For Documentation**:
1. Add technical docs to `docs/` folder
2. Use markdown format for readability
3. Include implementation details and examples

### **For Debugging**:
1. Use `temp_files/` for experimental scripts
2. Clean up regularly to avoid clutter
3. Move stable utilities to appropriate folders

---

*Last Updated: July 28, 2025*  
*Workspace reorganized for better maintainability and navigation*
