"""
Real-time trade log parser for Command Center
Monitors and parses trade execution logs in real-time
"""

import json
import logging
import os
import re
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd


@dataclass
class TradeExecution:
    """Trade execution data structure"""

    timestamp: datetime
    symbol: str
    action: str  # BUY, SELL
    quantity: int
    price: float
    strategy: str
    confidence: float
    pnl: float
    order_id: str
    execution_details: Dict


class TradeLogParser:
    """Real-time trade log parser"""

    def __init__(self, log_directory: str = None):
        self.logger = self.setup_logger()

        # Set log directory
        if log_directory:
            self.log_directory = Path(log_directory)
        else:
            # Default to workspace logs directory
            workspace_root = Path(__file__).parent.parent
            self.log_directory = workspace_root / "logs"

        # Data storage
        self.trade_executions = []
        self.trade_summary = {}
        self.last_update = datetime.now()

        # File monitoring
        self.monitored_files = {}
        self.file_positions = {}

        # Callbacks
        self.trade_callbacks = []

        # Patterns for parsing different log formats
        self.log_patterns = {
            "trade_execution": [
                r"EXECUTED.*?(\w+).*?(BUY|SELL).*?(\d+).*?shares.*?\$(\d+\.\d+)",
                r"TRADE.*?(\w+).*?(BUY|SELL).*?qty:?\s*(\d+).*?price:?\s*\$?(\d+\.\d+)",
                r"ORDER.*?(\w+).*?(BUY|SELL).*?(\d+).*?@.*?\$(\d+\.\d+).*?FILLED",
            ],
            "strategy_info": [
                r"strategy:?\s*([\w\s]+)",
                r"using\s+([\w\s]+)\s+strategy",
                r"Strategy:\s*([\w\s]+)",
            ],
            "confidence_info": [
                r"confidence:?\s*(\d+\.?\d*)%?",
                r"conf:?\s*(\d+\.?\d*)%?",
            ],
            "pnl_info": [
                r"P[&/]?L:?\s*\$?([+-]?\d+\.?\d*)",
                r"profit:?\s*\$?([+-]?\d+\.?\d*)",
                r"loss:?\s*\$?([+-]?\d+\.?\d*)",
            ],
        }

        self.logger.info(
            f"📊 Trade log parser initialized - monitoring: {self.log_directory}"
        )

    def setup_logger(self):
        """Setup logging for trade parser"""
        logger = logging.getLogger("trade_parser")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def find_log_files(self) -> List[Path]:
        """Find all relevant log files"""
        if not self.log_directory.exists():
            self.logger.warning(f"Log directory does not exist: {self.log_directory}")
            return []

        # Look for scalping-related log files
        patterns = ["scalping_*.log", "*engine*.log", "*order*.log", "*trade*.log"]

        log_files = []
        for pattern in patterns:
            log_files.extend(self.log_directory.glob(pattern))

        # Sort by modification time (newest first)
        log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        self.logger.info(f"Found {len(log_files)} log files to monitor")
        return log_files

    def parse_trade_from_line(
        self, line: str, timestamp: datetime = None
    ) -> Optional[TradeExecution]:
        """Parse a trade execution from a log line"""
        try:
            line = line.strip()
            if not timestamp:
                # Try to extract timestamp from line
                timestamp = self.extract_timestamp(line) or datetime.now()

            # Try different trade execution patterns
            for pattern in self.log_patterns["trade_execution"]:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    symbol = match.group(1).upper()
                    action = match.group(2).upper()
                    quantity = int(match.group(3))
                    price = float(match.group(4))

                    # Extract additional info
                    strategy = self.extract_strategy(line)
                    confidence = self.extract_confidence(line)
                    pnl = self.extract_pnl(line)

                    trade = TradeExecution(
                        timestamp=timestamp,
                        symbol=symbol,
                        action=action,
                        quantity=quantity,
                        price=price,
                        strategy=strategy,
                        confidence=confidence,
                        pnl=pnl,
                        order_id=self.extract_order_id(line),
                        execution_details={"raw_line": line},
                    )

                    return trade

        except Exception as e:
            self.logger.debug(f"Error parsing trade from line: {e}")

        return None

    def extract_timestamp(self, line: str) -> Optional[datetime]:
        """Extract timestamp from log line"""
        # Common timestamp patterns
        patterns = [
            r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})",
            r"(\d{2}:\d{2}:\d{2})",
            r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})",
        ]

        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    timestamp_str = match.group(1)
                    if len(timestamp_str) == 8:  # Just time
                        today = datetime.now().date()
                        time_part = datetime.strptime(timestamp_str, "%H:%M:%S").time()
                        return datetime.combine(today, time_part)
                    else:
                        return datetime.fromisoformat(timestamp_str.replace("T", " "))
                except:
                    continue

        return None

    def extract_strategy(self, line: str) -> str:
        """Extract strategy name from log line"""
        for pattern in self.log_patterns["strategy_info"]:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                strategy = match.group(1).strip()
                # Clean up strategy name
                strategy = re.sub(r"\s+", " ", strategy).title()
                return strategy

        # Default strategies based on keywords
        if "mean" in line.lower() or "reversion" in line.lower():
            return "Mean Reversion"
        elif "momentum" in line.lower() or "scalp" in line.lower():
            return "Momentum Scalp"
        elif "vwap" in line.lower() or "bounce" in line.lower():
            return "VWAP Bounce"
        else:
            return "Unknown"

    def extract_confidence(self, line: str) -> float:
        """Extract confidence from log line"""
        for pattern in self.log_patterns["confidence_info"]:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    confidence = float(match.group(1))
                    # Convert to percentage if needed
                    if confidence > 1:
                        return confidence
                    else:
                        return confidence * 100
                except:
                    continue

        return 0.0

    def extract_pnl(self, line: str) -> float:
        """Extract P&L from log line"""
        for pattern in self.log_patterns["pnl_info"]:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    pnl = float(match.group(1))
                    return pnl
                except:
                    continue

        return 0.0

    def extract_order_id(self, line: str) -> str:
        """Extract order ID from log line"""
        # Look for order ID patterns
        patterns = [
            r"order[_\s]?id:?\s*([a-zA-Z0-9-]+)",
            r"id:?\s*([a-zA-Z0-9-]+)",
            r"order:?\s*([a-zA-Z0-9-]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1)

        return ""

    def monitor_file(self, file_path: Path) -> List[TradeExecution]:
        """Monitor a single log file for new trades"""
        new_trades = []

        try:
            if not file_path.exists():
                return new_trades

            # Get current file position
            current_pos = self.file_positions.get(str(file_path), 0)

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(current_pos)
                new_lines = f.readlines()
                self.file_positions[str(file_path)] = f.tell()

            # Parse new lines for trades
            for line in new_lines:
                trade = self.parse_trade_from_line(line)
                if trade:
                    new_trades.append(trade)
                    self.logger.info(
                        f"📈 New trade detected: {trade.symbol} {trade.action} {trade.quantity}@${trade.price:.2f}"
                    )

        except Exception as e:
            self.logger.error(f"Error monitoring file {file_path}: {e}")

        return new_trades

    def scan_recent_trades(self, hours_back: int = 24) -> List[TradeExecution]:
        """Scan log files for recent trades"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        recent_trades = []

        log_files = self.find_log_files()

        for log_file in log_files:
            try:
                # Check if file was modified recently
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_mtime < cutoff_time:
                    continue

                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()

                for line in lines:
                    trade = self.parse_trade_from_line(line)
                    if trade and trade.timestamp >= cutoff_time:
                        recent_trades.append(trade)

            except Exception as e:
                self.logger.error(f"Error scanning {log_file}: {e}")

        # Sort by timestamp
        recent_trades.sort(key=lambda t: t.timestamp, reverse=True)

        self.logger.info(
            f"Found {len(recent_trades)} recent trades in last {hours_back} hours"
        )
        return recent_trades

    def start_monitoring(self):
        """Start real-time log monitoring"""
        self.logger.info("🔍 Starting real-time trade log monitoring")

        # Initial scan for recent trades
        self.trade_executions = self.scan_recent_trades(24)
        self.update_trade_summary()

        # Get list of files to monitor
        log_files = self.find_log_files()

        # Initialize file positions
        for log_file in log_files:
            if log_file.exists():
                self.file_positions[str(log_file)] = log_file.stat().st_size

        # Start monitoring loop
        def monitor_loop():
            while True:
                try:
                    # Check for new log files
                    current_files = self.find_log_files()
                    new_files = [
                        f for f in current_files if str(f) not in self.file_positions
                    ]

                    for new_file in new_files:
                        self.file_positions[str(new_file)] = 0
                        self.logger.info(f"📁 Monitoring new log file: {new_file.name}")

                    # Monitor all files for new trades
                    new_trades = []
                    for log_file in current_files:
                        trades = self.monitor_file(log_file)
                        new_trades.extend(trades)

                    # Process new trades
                    if new_trades:
                        self.trade_executions.extend(new_trades)
                        # Keep only recent trades (last 1000)
                        self.trade_executions = self.trade_executions[-1000:]
                        self.update_trade_summary()

                        # Notify callbacks
                        for callback in self.trade_callbacks:
                            try:
                                for trade in new_trades:
                                    callback(trade)
                            except Exception as e:
                                self.logger.error(f"Error in trade callback: {e}")

                    self.last_update = datetime.now()
                    time.sleep(2)  # Check every 2 seconds

                except Exception as e:
                    self.logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(5)

        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()

        return monitor_thread

    def update_trade_summary(self):
        """Update trade summary statistics"""
        if not self.trade_executions:
            self.trade_summary = {}
            return

        today_trades = [
            t
            for t in self.trade_executions
            if t.timestamp.date() == datetime.now().date()
        ]

        total_trades = len(today_trades)
        winning_trades = len([t for t in today_trades if t.pnl > 0])
        losing_trades = len([t for t in today_trades if t.pnl < 0])

        total_pnl = sum(t.pnl for t in today_trades)
        avg_win = sum(t.pnl for t in today_trades if t.pnl > 0) / max(1, winning_trades)
        avg_loss = sum(t.pnl for t in today_trades if t.pnl < 0) / max(1, losing_trades)

        win_rate = (winning_trades / max(1, total_trades)) * 100

        self.trade_summary = {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "last_update": self.last_update,
        }

    def register_trade_callback(self, callback):
        """Register callback for new trade events"""
        self.trade_callbacks.append(callback)

    def get_recent_trades(
        self, limit: int = 50, hours: int = None
    ) -> List[TradeExecution]:
        """Get recent trade executions"""
        if hours is not None:
            # Filter by time
            from datetime import datetime, timedelta

            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_trades = [
                t for t in self.trade_executions if t.timestamp >= cutoff_time
            ]
            # Convert to dict format for Command Center compatibility
            return [
                {
                    "timestamp": t.timestamp.strftime("%H:%M:%S"),
                    "symbol": t.symbol,
                    "action": t.action,
                    "quantity": t.quantity,
                    "price": t.price,
                    "pnl": t.pnl if hasattr(t, "pnl") else 0,
                    "strategy": t.strategy,
                }
                for t in recent_trades
            ]
        return self.trade_executions[-limit:] if self.trade_executions else []

    def get_trade_summary(self) -> Dict:
        """Get trade summary statistics"""
        return self.trade_summary.copy()

    def get_trades_by_symbol(self, symbol: str) -> List[TradeExecution]:
        """Get trades for specific symbol"""
        return [t for t in self.trade_executions if t.symbol == symbol]

    def get_trades_by_strategy(self, strategy: str) -> List[TradeExecution]:
        """Get trades for specific strategy"""
        return [
            t for t in self.trade_executions if strategy.lower() in t.strategy.lower()
        ]


# Singleton instance
trade_parser = TradeLogParser()


# Helper functions
def get_recent_trades(limit: int = 50) -> List[TradeExecution]:
    """Get recent trade executions"""
    return trade_parser.get_recent_trades(limit)


def get_trade_summary() -> Dict:
    """Get trade summary statistics"""
    return trade_parser.get_trade_summary()


def start_trade_monitoring():
    """Start trade log monitoring in background thread"""
    return trade_parser.start_monitoring()
