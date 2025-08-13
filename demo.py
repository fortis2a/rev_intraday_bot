#!/usr/bin/env python3
"""
🎯 Intraday Trading Bot Demo
Quick demonstration mode for testing the intraday trading system
"""

import sys
import time
import signal
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from config import config
from core.intraday_engine import IntradayEngine
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('demo_intraday.log')
    ]
)

logger = logging.getLogger("demo")

class DemoTradingSystem:
    """Demo version of the intraday trading system"""
    
    def __init__(self, duration_seconds: int = 300):
        """Initialize demo system
        
        Args:
            duration_seconds: How long to run the demo (default 5 minutes)
        """
        self.duration = duration_seconds
        self.start_time = time.time()
        self.engine = None
        self.running = False
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"📢 Received signal {signum}, shutting down demo...")
        self.running = False
        
    def run(self):
        """Run the demo trading system"""
        logger.info("🎯 Starting Intraday Trading Bot Demo")
        logger.info(f"⏱️ Demo duration: {self.duration} seconds")
        logger.info(f"📊 Timeframe: {config.TIMEFRAME}")
        logger.info(f"🎯 Profit Target: {config.PROFIT_TARGET_PCT}%")
        logger.info(f"🛑 Stop Loss: {config.STOP_LOSS_PCT}%")
        logger.info(f"📈 Max Positions: {config.MAX_OPEN_POSITIONS}")
        logger.info(f"🚦 Daily Trade Limit: {config.MAX_TRADES_PER_DAY}")
        
        try:
            # Initialize the trading engine
            self.engine = IntradayEngine()
            self.running = True
            
            logger.info("🚀 Demo started - Running intraday trading simulation...")
            
            # Main demo loop
            while self.running and (time.time() - self.start_time) < self.duration:
                try:
                    # Run one trading cycle
                    self.engine.run_cycle()
                    
                    # Sleep between cycles (intraday doesn't need to be as frequent)
                    time.sleep(30)  # 30 second intervals for demo
                    
                    # Show progress
                    elapsed = time.time() - self.start_time
                    remaining = self.duration - elapsed
                    if int(elapsed) % 60 == 0:  # Every minute
                        logger.info(f"⏱️ Demo running... {remaining:.0f}s remaining")
                        
                except KeyboardInterrupt:
                    logger.info("🛑 Demo interrupted by user")
                    break
                except Exception as e:
                    logger.error(f"❌ Error in demo cycle: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Failed to start demo: {e}")
            return False
            
        finally:
            if self.engine:
                logger.info("🔄 Shutting down trading engine...")
                self.engine.shutdown()
                
        logger.info("✅ Demo completed successfully!")
        return True

def main():
    """Main demo entry point"""
    parser = argparse.ArgumentParser(description='Intraday Trading Bot Demo')
    parser.add_argument('--duration', type=int, default=300, 
                       help='Demo duration in seconds (default: 300)')
    parser.add_argument('--mode', type=str, default='intraday',
                       choices=['intraday', 'test'],
                       help='Demo mode (default: intraday)')
    
    args = parser.parse_args()
    
    # Create and run demo
    demo = DemoTradingSystem(duration_seconds=args.duration)
    success = demo.run()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
