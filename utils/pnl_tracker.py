#!/usr/bin/env python3
"""
📊 PnL Tracker - Real-time P&L tracking and reporting
Tracks trades, positions, and performance metrics in real-time
"""

import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import threading
import time
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config import config
from utils.logger import setup_scalping_loggers

class PnLTracker:
    """Real-time P&L tracking and database management"""
    
    def __init__(self):
        """Initialize PnL tracker"""
        self.loggers = setup_scalping_loggers()
        self.logger = self.loggers['pnl_tracker']
        
        # Database setup
        self.db_path = Path(__file__).parent.parent / "data" / "trading_history.db"
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Initialize session data first
        self.current_positions = {}
        self.session_trades = []
        self.session_start_time = datetime.now()
        self.session_start_balance = config.SIMULATED_PORTFOLIO_VALUE if config.SIMULATE_PORTFOLIO else 0
        
        self._init_database()
        self._init_session()
        
        self.logger.info("📊 PnL Tracker initialized")
    
    def _init_database(self):
        """Initialize SQLite database for trade history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Trading sessions table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS trading_sessions (
                        session_id TEXT PRIMARY KEY,
                        date TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        start_balance REAL NOT NULL,
                        end_balance REAL,
                        total_pnl REAL,
                        total_trades INTEGER DEFAULT 0,
                        winning_trades INTEGER DEFAULT 0,
                        losing_trades INTEGER DEFAULT 0,
                        max_drawdown REAL DEFAULT 0,
                        max_profit REAL DEFAULT 0,
                        sharpe_ratio REAL,
                        strategy_breakdown TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Individual trades table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS trades (
                        trade_id TEXT PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        symbol TEXT NOT NULL,
                        strategy TEXT NOT NULL,
                        side TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        entry_price REAL NOT NULL,
                        exit_price REAL,
                        expected_entry_price REAL,
                        expected_exit_price REAL,
                        entry_time TEXT NOT NULL,
                        exit_time TEXT,
                        pnl REAL DEFAULT 0,
                        gross_pnl REAL DEFAULT 0,
                        commission REAL DEFAULT 0,
                        regulatory_fees REAL DEFAULT 0,
                        entry_slippage_cost REAL DEFAULT 0,
                        exit_slippage_cost REAL DEFAULT 0,
                        total_transaction_costs REAL DEFAULT 0,
                        status TEXT DEFAULT 'OPEN',
                        stop_loss REAL,
                        take_profit REAL,
                        confidence REAL,
                        hold_time_seconds INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES trading_sessions (session_id)
                    )
                """)
                
                # Daily performance metrics
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS daily_performance (
                        date TEXT PRIMARY KEY,
                        total_pnl REAL NOT NULL,
                        total_trades INTEGER NOT NULL,
                        win_rate REAL NOT NULL,
                        max_drawdown REAL NOT NULL,
                        sharpe_ratio REAL,
                        portfolio_value REAL NOT NULL,
                        best_trade REAL NOT NULL,
                        worst_trade REAL NOT NULL,
                        avg_trade REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                self.logger.info("✅ Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"❌ Database initialization error: {e}")
            raise
    
    def _init_session(self):
        """Initialize new trading session"""
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_date = datetime.now().strftime('%Y-%m-%d')
        self.session_start_time = datetime.now()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO trading_sessions 
                    (session_id, date, start_time, start_balance)
                    VALUES (?, ?, ?, ?)
                """, (
                    self.session_id,
                    self.session_date,
                    self.session_start_time.isoformat(),
                    self.session_start_balance
                ))
                conn.commit()
                
            self.logger.info(f"📈 New trading session started: {self.session_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Session initialization error: {e}")
    
    def record_trade_entry(self, trade_data: Dict) -> str:
        """Record trade entry"""
        trade_id = f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        try:
            trade_record = {
                'trade_id': trade_id,
                'session_id': self.session_id,
                'symbol': trade_data['symbol'],
                'strategy': trade_data.get('strategy', 'Unknown'),
                'side': trade_data['side'],  # BUY/SELL
                'quantity': trade_data['quantity'],
                'entry_price': trade_data['entry_price'],
                'expected_entry_price': trade_data.get('expected_entry_price', trade_data['entry_price']),
                'entry_time': datetime.now().isoformat(),
                'stop_loss': trade_data.get('stop_loss'),
                'take_profit': trade_data.get('take_profit'),
                'confidence': trade_data.get('confidence', 0.5)
            }
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO trades 
                    (trade_id, session_id, symbol, strategy, side, quantity, 
                     entry_price, expected_entry_price, entry_time, stop_loss, take_profit, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trade_record['trade_id'], trade_record['session_id'],
                    trade_record['symbol'], trade_record['strategy'],
                    trade_record['side'], trade_record['quantity'],
                    trade_record['entry_price'], trade_record['expected_entry_price'],
                    trade_record['entry_time'], trade_record['stop_loss'], 
                    trade_record['take_profit'], trade_record['confidence']
                ))
                conn.commit()
            
            # Add to current positions
            self.current_positions[trade_id] = trade_record
            
            self.logger.info(f"📊 Trade entry recorded: {trade_id} - {trade_data['symbol']} {trade_data['side']} {trade_data['quantity']}@${trade_data['entry_price']:.2f}")
            return trade_id
            
        except Exception as e:
            self.logger.error(f"❌ Trade entry recording error: {e}")
            return None
    
    def record_trade_exit(self, trade_id: str, exit_data: Dict):
        """Record trade exit and calculate P&L"""
        try:
            if trade_id not in self.current_positions:
                self.logger.warning(f"⚠️ Trade {trade_id} not found in current positions")
                return
            
            entry_trade = self.current_positions[trade_id]
            entry_time = datetime.fromisoformat(entry_trade['entry_time'])
            exit_time = datetime.now()
            hold_time = (exit_time - entry_time).total_seconds()
            
            # Calculate P&L
            entry_price = entry_trade['entry_price']
            exit_price = exit_data['exit_price']
            quantity = entry_trade['quantity']
            
            if entry_trade['side'] == 'BUY':
                gross_pnl = (exit_price - entry_price) * quantity
            else:  # SELL
                gross_pnl = (entry_price - exit_price) * quantity
            
            # Enhanced cost tracking
            commission = exit_data.get('commission', 0)
            regulatory_fees = exit_data.get('regulatory_fees', 0)
            entry_slippage_cost = exit_data.get('entry_slippage_cost', 0)
            exit_slippage_cost = exit_data.get('exit_slippage_cost', 0)
            total_transaction_costs = exit_data.get('total_transaction_costs', commission)
            
            # Net PnL after all costs
            net_pnl = gross_pnl - total_transaction_costs
            
            # Update database with enhanced cost tracking
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE trades 
                    SET exit_price = ?, expected_exit_price = ?, exit_time = ?, 
                        pnl = ?, gross_pnl = ?, commission = ?, regulatory_fees = ?,
                        entry_slippage_cost = ?, exit_slippage_cost = ?, 
                        total_transaction_costs = ?, status = 'CLOSED', hold_time_seconds = ?
                    WHERE trade_id = ?
                """, (
                    exit_price, exit_data.get('expected_exit_price', exit_price), 
                    exit_time.isoformat(), net_pnl, gross_pnl, commission, 
                    regulatory_fees, entry_slippage_cost, exit_slippage_cost,
                    total_transaction_costs, int(hold_time), trade_id
                ))
                conn.commit()
            
            # Add to session trades and remove from current positions
            trade_summary = {
                **entry_trade,
                'exit_price': exit_price,
                'expected_exit_price': exit_data.get('expected_exit_price', exit_price),
                'exit_time': exit_time.isoformat(),
                'pnl': net_pnl,
                'gross_pnl': gross_pnl,
                'commission': commission,
                'regulatory_fees': regulatory_fees,
                'entry_slippage_cost': entry_slippage_cost,
                'exit_slippage_cost': exit_slippage_cost,
                'total_transaction_costs': total_transaction_costs,
                'hold_time_seconds': int(hold_time)
            }
            
            self.session_trades.append(trade_summary)
            del self.current_positions[trade_id]
            
            self.logger.info(f"💰 Trade exit recorded: {trade_id} - P&L: ${net_pnl:.2f} (Hold: {hold_time:.0f}s)")
            
        except Exception as e:
            self.logger.error(f"❌ Trade exit recording error: {e}")
    
    def get_current_session_pnl(self) -> Dict:
        """Get current session P&L summary"""
        try:
            # Calculate completed trades P&L
            total_pnl = sum(trade['pnl'] for trade in self.session_trades)
            total_trades = len(self.session_trades)
            winning_trades = len([t for t in self.session_trades if t['pnl'] > 0])
            losing_trades = len([t for t in self.session_trades if t['pnl'] < 0])
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            avg_trade = (total_pnl / total_trades) if total_trades > 0 else 0
            
            best_trade = max([t['pnl'] for t in self.session_trades], default=0)
            worst_trade = min([t['pnl'] for t in self.session_trades], default=0)
            
            # Calculate drawdown
            running_pnl = []
            cumulative = 0
            for trade in self.session_trades:
                cumulative += trade['pnl']
                running_pnl.append(cumulative)
            
            max_profit = max(running_pnl, default=0)
            max_drawdown = 0
            if running_pnl:
                peak = running_pnl[0]
                for pnl in running_pnl:
                    if pnl > peak:
                        peak = pnl
                    drawdown = peak - pnl
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown
            
            # Current portfolio value
            current_balance = self.session_start_balance + total_pnl
            
            return {
                'session_id': self.session_id,
                'session_date': self.session_date,
                'start_balance': self.session_start_balance,
                'current_balance': current_balance,
                'total_pnl': total_pnl,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'avg_trade': avg_trade,
                'best_trade': best_trade,
                'worst_trade': worst_trade,
                'max_drawdown': max_drawdown,
                'max_profit': max_profit,
                'open_positions': len(self.current_positions),
                'session_duration': str(datetime.now() - self.session_start_time).split('.')[0]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Session P&L calculation error: {e}")
            return {}
    
    def close_session(self):
        """Close current trading session"""
        try:
            session_summary = self.get_current_session_pnl()
            end_time = datetime.now()
            
            # Calculate strategy breakdown
            strategy_pnl = {}
            for trade in self.session_trades:
                strategy = trade['strategy']
                if strategy not in strategy_pnl:
                    strategy_pnl[strategy] = {'pnl': 0, 'trades': 0}
                strategy_pnl[strategy]['pnl'] += trade['pnl']
                strategy_pnl[strategy]['trades'] += 1
            
            # Update session in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE trading_sessions 
                    SET end_time = ?, end_balance = ?, total_pnl = ?,
                        total_trades = ?, winning_trades = ?, losing_trades = ?,
                        max_drawdown = ?, max_profit = ?, strategy_breakdown = ?
                    WHERE session_id = ?
                """, (
                    end_time.isoformat(),
                    session_summary['current_balance'],
                    session_summary['total_pnl'],
                    session_summary['total_trades'],
                    session_summary['winning_trades'],
                    session_summary['losing_trades'],
                    session_summary['max_drawdown'],
                    session_summary['max_profit'],
                    json.dumps(strategy_pnl),
                    self.session_id
                ))
                
                # Update or insert daily performance
                conn.execute("""
                    INSERT OR REPLACE INTO daily_performance
                    (date, total_pnl, total_trades, win_rate, max_drawdown,
                     portfolio_value, best_trade, worst_trade, avg_trade)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.session_date,
                    session_summary['total_pnl'],
                    session_summary['total_trades'],
                    session_summary['win_rate'],
                    session_summary['max_drawdown'],
                    session_summary['current_balance'],
                    session_summary['best_trade'],
                    session_summary['worst_trade'],
                    session_summary['avg_trade']
                ))
                
                conn.commit()
            
            self.logger.info(f"📊 Trading session closed: {self.session_id}")
            self.logger.info(f"💰 Final P&L: ${session_summary['total_pnl']:.2f} ({session_summary['total_trades']} trades)")
            
            return session_summary
            
        except Exception as e:
            self.logger.error(f"❌ Session closing error: {e}")
            return {}
    
    def get_historical_performance(self, days: int = 30) -> pd.DataFrame:
        """Get historical performance data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT * FROM daily_performance 
                    WHERE date >= date('now', '-{} days')
                    ORDER BY date DESC
                """.format(days)
                
                df = pd.read_sql_query(query, conn)
                return df
                
        except Exception as e:
            self.logger.error(f"❌ Historical performance query error: {e}")
            return pd.DataFrame()
    
    def get_trade_history(self, days: int = 7) -> pd.DataFrame:
        """Get recent trade history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT t.*, s.date as session_date
                    FROM trades t
                    JOIN trading_sessions s ON t.session_id = s.session_id
                    WHERE s.date >= date('now', '-{} days')
                    AND t.status = 'CLOSED'
                    ORDER BY t.entry_time DESC
                """.format(days)
                
                df = pd.read_sql_query(query, conn)
                return df
                
        except Exception as e:
            self.logger.error(f"❌ Trade history query error: {e}")
            return pd.DataFrame()

# Global PnL tracker instance
pnl_tracker = None

def get_pnl_tracker() -> PnLTracker:
    """Get or create global PnL tracker instance"""
    global pnl_tracker
    if pnl_tracker is None:
        pnl_tracker = PnLTracker()
    return pnl_tracker

if __name__ == "__main__":
    """Test the PnL tracker when run directly"""
    print("🧪 Testing PnL Tracker...")
    
    try:
        tracker = get_pnl_tracker()
        print("✅ PnL Tracker initialized successfully")
        
        # Test session summary
        summary = tracker.get_current_session_pnl()
        print(f"📊 Current session: {summary.get('session_id', 'Unknown')}")
        print(f"💰 Start balance: ${summary.get('start_balance', 0):,.2f}")
        print(f"📈 Current P&L: ${summary.get('total_pnl', 0):,.2f}")
        print(f"🔢 Total trades: {summary.get('total_trades', 0)}")
        
        # Test historical data
        history = tracker.get_historical_performance(30)
        print(f"📊 Historical data: {len(history)} days available")
        
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
