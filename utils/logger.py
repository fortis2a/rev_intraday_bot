#!/usr/bin/env python3
"""
📝 Logger Setup for Scalping Bot
Configurable logging system with file and console output
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

def clean_message_for_console(message: str) -> str:
    """Remove emojis from log messages for Windows console compatibility"""
    if os.name == 'nt':  # Windows
        # Simple emoji removal for common ones used in the bot
        emoji_map = {
            '🔍': '[SEARCH]',
            '❌': '[ERROR]',
            '✅': '[OK]',
            '⚠️': '[WARNING]',
            '📊': '[DATA]',
            '💰': '[MONEY]',
            '📈': '[CHART]',
            '🎯': '[TARGET]',
            '🛑': '[STOP]',
            '💎': '[PROFIT]',
            '📋': '[LIST]',
            '🔗': '[LINK]',
            '⏱️': '[TIME]',
            '📝': '[NOTE]',
            '🚀': '[LAUNCH]',
            '🔧': '[SETUP]',
            '⚡': '[FAST]',
            '🎉': '[SUCCESS]'
        }
        for emoji, replacement in emoji_map.items():
            message = message.replace(emoji, replacement)
    return message

def setup_logger(name: str, log_level: str = "INFO", 
                log_file: Optional[str] = None, 
                console_output: bool = True) -> logging.Logger:
    """Setup logger with file and console handlers"""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create custom formatter that cleans emoji for console
    class EmojiSafeFormatter(logging.Formatter):
        def format(self, record):
            # Format the record normally first
            formatted = super().format(record)
            # Clean emojis for console output
            return clean_message_for_console(formatted)
    
    # Create formatters
    console_formatter = EmojiSafeFormatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler with proper encoding
    if console_output:
        # Use UTF-8 encoding for console output to handle emojis
        import io
        console_handler = logging.StreamHandler(
            io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        )
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Create logs directory
        log_path = Path(__file__).parent.parent / "logs"
        log_path.mkdir(exist_ok=True)
        
        # Create log file with timestamp
        if not log_file.endswith('.log'):
            timestamp = datetime.now().strftime('%Y%m%d')
            log_file = f"{log_file}_{timestamp}.log"
        
        file_path = log_path / log_file
        
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # File gets all logs
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def setup_scalping_loggers() -> dict:
    """Setup all loggers for scalping bot components"""
    
    loggers = {}
    
    # Main components
    components = [
        "intraday_engine",
        "risk_manager", 
        "data_manager",
        "order_manager",
        "momentum_strategy",
        "mean_reversion_strategy",
        "vwap_strategy",
        "pnl_tracker",
        "pnl_report",
        "live_pnl"
    ]
    
    for component in components:
        loggers[component] = setup_logger(
            name=component,
            log_level="INFO",
            log_file=f"scalping_{component}",
            console_output=True
        )
    
    return loggers

if __name__ == "__main__":
    # Test logging setup
    logger = setup_logger("test_logger", "DEBUG", "test_log")
    
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    print("✅ Logger test complete")
