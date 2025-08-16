#!/usr/bin/env python3
"""
Debug script to isolate the initialization crash
"""

import sys
import traceback
from utils.logger import setup_logger

def test_imports():
    """Test all imports step by step"""
    logger = setup_logger('debug_init')
    logger.info("Testing imports...")
    
    try:
        logger.info("1. Testing config import...")
        from config import config, validate_config
        logger.info("✓ Config import successful")
        
        logger.info("2. Testing config validation...")
        validate_config()
        logger.info("✓ Config validation successful")
        
        logger.info("3. Testing DataManager import...")
        from core.data_manager import DataManager
        logger.info("✓ DataManager import successful")
        
        logger.info("4. Testing DataManager initialization...")
        data_manager = DataManager()
        logger.info("✓ DataManager initialization successful")
        
        logger.info("5. Testing OrderManager import...")
        from core.order_manager import OrderManager
        logger.info("✓ OrderManager import successful")
        
        logger.info("6. Testing OrderManager initialization...")
        order_manager = OrderManager(data_manager)
        logger.info("✓ OrderManager initialization successful")
        
        logger.info("🎉 ALL TESTS PASSED!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error at step: {e}")
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_imports()
