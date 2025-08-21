
import time
import sys
sys.path.append(".")
from core.data_manager import DataManager
from utils.logger import setup_logger

logger = setup_logger("pnl_monitor")
dm = DataManager()

logger.info("[START] P&L Monitor started")

while True:
    try:
        account = dm.get_account_info()
        positions = dm.get_positions()
        
        if account:
            total_unrealized = sum(p["unrealized_pl"] for p in positions)
            logger.info(f"[PNL] Equity: ${account['equity']:,.2f}")
            logger.info(f"[PNL] Unrealized P&L: ${total_unrealized:,.2f}")
            logger.info(f"[PNL] Positions: {len(positions)}")
            
            if positions:
                for pos in positions:
                    logger.info(f"[POS] {pos['symbol']}: {pos['qty']} shares, P&L: ${pos['unrealized_pl']:,.2f}")
        
        time.sleep(30)  # Update every 30 seconds
    except KeyboardInterrupt:
        logger.info("[STOP] P&L Monitor stopped")
        break
    except Exception as e:
        logger.error(f"[ERROR] P&L monitor error: {e}")
        time.sleep(60)
