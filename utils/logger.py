#!/usr/bin/env python3
"""
ASCII-only logging system for Intraday Trading Bot
No Unicode characters to prevent charmap errors
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime

def setup_logger(name, level="INFO"):
    """Setup ASCII-only logger"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers = []
    
    # Create formatters - ASCII only
    date_str = datetime.now().strftime("%Y%m%d")
    file_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '[%(levelname)s] %(asctime)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File handler
    log_file = log_dir / f"intraday_{name}_{date_str}.log"
    file_handler = logging.FileHandler(log_file, encoding='ascii', errors='replace')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

def clean_message(message):
    """Remove any non-ASCII characters from log messages"""
    if isinstance(message, str):
        # Replace common problematic characters
        message = message.replace('✅', '[OK]')
        message = message.replace('❌', '[ERROR]')
        message = message.replace('🚀', '[START]')
        message = message.replace('📊', '[DATA]')
        message = message.replace('💰', '[MONEY]')
        message = message.replace('🎯', '[TARGET]')
        message = message.replace('⚠️', '[WARNING]')
        message = message.replace('🛑', '[STOP]')
        # Ensure ASCII only
        message = message.encode('ascii', errors='replace').decode('ascii')
    return message
