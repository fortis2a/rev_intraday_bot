#!/usr/bin/env python3
"""
Debug script to test the specific initialization steps that might be causing the crash
"""

import sys
import traceback
from utils.logger import setup_logger
from core.data_manager import DataManager
from core.order_manager import OrderManager

def test_advanced_init():
    """Test the advanced initialization steps"""
    logger = setup_logger('debug_advanced')
    logger.info("Testing advanced initialization...")
    
    try:
        logger.info("1. Creating DataManager...")
        data_manager = DataManager()
        logger.info("✓ DataManager created")
        
        logger.info("2. Creating OrderManager...")
        order_manager = OrderManager(data_manager)
        logger.info("✓ OrderManager created")
        
        logger.info("3. Testing get_account_info...")
        account_info = data_manager.get_account_info()
        if account_info:
            logger.info(f"✓ Account info: Equity=${account_info['equity']:,.2f}")
        else:
            logger.warning("⚠️ No account info returned")
        
        logger.info("4. Testing get_positions...")
        positions = data_manager.get_positions()
        logger.info(f"✓ Positions found: {len(positions) if positions else 0}")
        
        logger.info("🎉 ALL ADVANCED TESTS PASSED!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in advanced test: {e}")
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_advanced_init()
