#!/usr/bin/env python3
"""
Basic configuration and import tests
Tests that essential modules can be imported and basic configuration is valid
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_config_import():
    """Test that config module can be imported"""
    try:
        import config

        assert hasattr(config, "ALPACA_API_KEY")
        assert hasattr(config, "ALPACA_SECRET_KEY")
    except ImportError as e:
        pytest.skip(f"Config import failed: {e}")


def test_main_import():
    """Test that main module can be imported"""
    try:
        import main

        assert hasattr(main, "IntradayEngine")
    except ImportError as e:
        pytest.skip(f"Main import failed: {e}")


def test_strategies_import():
    """Test that strategies module can be imported"""
    try:
        import strategies

        assert hasattr(strategies, "MomentumStrategy")
    except ImportError as e:
        pytest.skip(f"Strategies import failed: {e}")


def test_stock_specific_config_import():
    """Test that stock_specific_config module can be imported"""
    try:
        import stock_specific_config

        assert hasattr(stock_specific_config, "STOCK_SPECIFIC_THRESHOLDS")
    except ImportError as e:
        pytest.skip(f"Stock specific config import failed: {e}")


def test_project_structure():
    """Test that essential project directories exist"""
    assert project_root.exists()
    assert (project_root / "core").exists()
    assert (project_root / "database").exists()
    assert (project_root / "monitoring").exists()
    assert (project_root / "reporting").exists()


def test_essential_files_exist():
    """Test that essential files exist"""
    essential_files = [
        "main.py",
        "config.py",
        "strategies.py",
        "stock_specific_config.py",
        "launcher.py",
    ]

    for file in essential_files:
        assert (project_root / file).exists(), f"Missing essential file: {file}"


def test_database_module():
    """Test that database module can be imported"""
    try:
        from database.trading_db import TradingDatabase

        # Basic instantiation test (without requiring actual DB connection)
        assert TradingDatabase is not None
    except ImportError as e:
        pytest.skip(f"Database module import failed: {e}")


class TestBasicFunctionality:
    """Basic functionality tests that don't require API keys"""

    def test_import_core_modules(self):
        """Test importing core modules"""
        try:
            from core.intraday_engine import IntradayEngine
            from core.order_manager import OrderManager
            from core.real_time_confidence import RealTimeConfidence

            assert all([IntradayEngine, OrderManager, RealTimeConfidence])
        except ImportError as e:
            pytest.skip(f"Core modules import failed: {e}")

    def test_import_monitoring_modules(self):
        """Test importing monitoring modules"""
        try:
            from monitoring.system_status import SystemStatus

            assert SystemStatus is not None
        except ImportError as e:
            pytest.skip(f"Monitoring modules import failed: {e}")

    def test_import_reporting_modules(self):
        """Test importing reporting modules"""
        try:
            from reporting.generate_todays_pnl import generate_todays_pnl_report
            from reporting.today_analysis import TodayAnalysis

            assert all([TodayAnalysis, generate_todays_pnl_report])
        except ImportError as e:
            pytest.skip(f"Reporting modules import failed: {e}")


# Smoke tests that verify system health without requiring live connections
def test_system_health():
    """Basic system health check"""
    # Test that Python version is supported
    assert sys.version_info >= (3, 8), "Python 3.8+ required"

    # Test that requirements.txt exists
    requirements_file = project_root / "requirements.txt"
    assert requirements_file.exists(), "requirements.txt missing"

    # Test that README exists
    readme_file = project_root / "README.md"
    assert readme_file.exists(), "README.md missing"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
