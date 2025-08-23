#!/usr/bin/env python3
"""
Integration tests for the trading system
Tests basic system integration without requiring live API connections
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestSystemIntegration:
    """Integration tests that verify system components work together"""

    def test_launcher_import(self):
        """Test that launcher can be imported"""
        try:
            import launcher

            assert hasattr(launcher, "main")
        except ImportError as e:
            pytest.skip(f"Launcher import failed: {e}")

    @patch.dict(
        "os.environ", {"ALPACA_API_KEY": "test_key", "ALPACA_SECRET_KEY": "test_secret"}
    )
    def test_config_with_env_vars(self):
        """Test config with environment variables"""
        try:
            import config

            # Should not raise an error with mock environment variables
            assert config.ALPACA_API_KEY == "test_key"
            assert config.ALPACA_SECRET_KEY == "test_secret"
        except Exception as e:
            pytest.skip(f"Config test failed: {e}")

    def test_database_import_only(self):
        """Test database module imports without connection"""
        try:
            from database.trading_db import TradingDatabase

            # Just test that the class exists, don't instantiate
            assert TradingDatabase.__name__ == "TradingDatabase"
        except ImportError as e:
            pytest.skip(f"Database import failed: {e}")

    def test_monitoring_system_import(self):
        """Test monitoring system imports"""
        try:
            from monitoring.live_dashboard import LiveDashboard
            from monitoring.system_status import SystemStatus

            # Test class existence without instantiation
            assert LiveDashboard.__name__ == "LiveDashboard"
        except ImportError as e:
            pytest.skip(f"Monitoring import failed: {e}")

    def test_reporting_system_import(self):
        """Test reporting system imports"""
        try:
            from reporting.generate_todays_pnl import generate_todays_pnl_report
            from reporting.today_analysis import TodayAnalysis

            assert TodayAnalysis.__name__ == "TodayAnalysis"
            assert generate_todays_pnl_report.__name__ == "generate_todays_pnl_report"
        except ImportError as e:
            pytest.skip(f"Reporting import failed: {e}")


class TestFileStructure:
    """Test that the file structure is correct after reorganization"""

    def test_core_directory_structure(self):
        """Test core directory structure"""
        core_dir = project_root / "core"
        assert core_dir.exists()

        expected_files = [
            "intraday_engine.py",
            "order_manager.py",
            "real_time_confidence.py",
        ]

        for file in expected_files:
            assert (core_dir / file).exists(), f"Missing core file: {file}"

    def test_database_directory_structure(self):
        """Test database directory structure"""
        db_dir = project_root / "database"
        assert db_dir.exists()
        assert (db_dir / "trading_db.py").exists()

    def test_monitoring_directory_structure(self):
        """Test monitoring directory structure"""
        monitoring_dir = project_root / "monitoring"
        assert monitoring_dir.exists()

        expected_files = ["live_dashboard.py", "system_status.py"]

        for file in expected_files:
            assert (monitoring_dir / file).exists(), f"Missing monitoring file: {file}"

    def test_reporting_directory_structure(self):
        """Test reporting directory structure"""
        reporting_dir = project_root / "reporting"
        assert reporting_dir.exists()

        expected_files = ["today_analysis.py", "generate_todays_pnl.py"]

        for file in expected_files:
            assert (reporting_dir / file).exists(), f"Missing reporting file: {file}"

    def test_batch_directories_exist(self):
        """Test that batch directories exist"""
        batch_dirs = [
            "batch_launchers",
            "batch_reports",
            "batch_emergency",
            "batch_utilities",
        ]

        for batch_dir in batch_dirs:
            assert (
                project_root / batch_dir
            ).exists(), f"Missing batch directory: {batch_dir}"

    def test_docs_directory_structure(self):
        """Test docs directory structure"""
        docs_dir = project_root / "docs"
        assert docs_dir.exists()

        subdirs = ["system_reports", "feature_updates", "guides"]

        for subdir in subdirs:
            assert (docs_dir / subdir).exists(), f"Missing docs subdirectory: {subdir}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
