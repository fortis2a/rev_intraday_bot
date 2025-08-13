#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intraday Trading Bot - Main Engine
Clean, production-ready main engine for intraday trading
"""

import os
import sys
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

try:
    from core.intraday_engine import IntradayEngine
    from utils.logger import setup_logger
    import config
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

def main():
    """Main entry point for the trading bot"""
    parser = argparse.ArgumentParser(description='Intraday Trading Bot')
    parser.add_argument('--symbols', type=str, help='Comma-separated list of symbols to trade')
    parser.add_argument('--demo', action='store_true', help='Run in demo mode')
    parser.add_argument('--validate-only', action='store_true', help='Validate environment and exit')
    parser.add_argument('--pnl-report', action='store_true', help='Generate P&L report and exit')
    parser.add_argument('--bypass-market-hours', action='store_true', help='Bypass market hours check')
    
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logger('intraday_main')
    
    try:
        # Initialize the trading engine
        logger.info("Initializing Intraday Trading Engine...")
        
        engine = IntradayEngine(
            demo_mode=args.demo,
            bypass_market_hours=args.bypass_market_hours
        )
        
        if args.validate_only:
            logger.info("Running environment validation...")
            is_valid = engine.validate_environment()
            if is_valid:
                logger.info("Environment validation passed")
                return 0
            else:
                logger.error("Environment validation failed")
                return 1
        
        if args.pnl_report:
            logger.info("Generating P&L report...")
            engine.generate_pnl_report()
            return 0
        
        # Set symbols if provided
        if args.symbols:
            symbols = [s.strip().upper() for s in args.symbols.split(',')]
            logger.info(f"Trading symbols: {symbols}")
        else:
            symbols = config.SYMBOLS
            logger.info(f"Using default symbols: {symbols}")
        
        # Start trading
        logger.info("Starting intraday trading session...")
        engine.start_trading(symbols)
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt - shutting down...")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
