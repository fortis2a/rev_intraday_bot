#!/usr/bin/env python3
"""
Debug script to test the main engine run method
"""

import sys
import traceback
from utils.logger import setup_logger
from main import IntradayEngine

def test_engine_run():
    """Test the IntradayEngine run method"""
    logger = setup_logger('debug_engine')
    logger.info("Testing IntradayEngine run method...")
    
    try:
        logger.info("1. Creating IntradayEngine...")
        engine = IntradayEngine(mode='LIVE')
        logger.info("✓ IntradayEngine created successfully")
        
        logger.info("2. Testing is_market_hours...")
        market_hours = engine.is_market_hours()
        logger.info(f"✓ Market hours check: {market_hours}")
        
        logger.info("3. Testing config access...")
        from config import config
        check_interval = config.get('CHECK_INTERVAL', 30)
        logger.info(f"✓ Check interval: {check_interval}")
        
        logger.info("4. Testing one trading cycle (if market open)...")
        if market_hours:
            logger.info("Market is open - testing trading_cycle...")
            engine.trading_cycle()
            logger.info("✓ Trading cycle completed")
        else:
            logger.info("Market is closed - skipping trading cycle test")
        
        logger.info("🎉 ENGINE TESTS PASSED!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in engine test: {e}")
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_engine_run()
