#!/usr/bin/env python3
"""
💰 Enhanced PnL Monitor with Fees, Slippage & Actual Fill Prices
Real-time tracking of true trading profitability including all costs
"""

import sys
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from config import config
from utils.logger import setup_logger
from utils.pnl_tracker import PnLTracker

class EnhancedPnLMonitor:
    """Enhanced PnL monitoring with comprehensive cost tracking"""
    
    def __init__(self):
        """Initialize enhanced PnL monitor"""
        self.logger = setup_logger("enhanced_pnl")
        self.pnl_tracker = PnLTracker()
        
        # Fee structures (Alpaca rates)
        self.fee_structure = {
            'commission_per_share': 0.0,  # Alpaca commission-free
            'regulatory_fees': {
                'sec_fee_rate': 0.000008,  # SEC fee: $0.008 per $1000 of transaction value
                'finra_taf_rate': 0.000145,  # FINRA TAF: $0.145 per $1000 of principal
                'nscc_fee': 0.0000175  # NSCC fee: $0.0175 per $1000
            },
            'market_data_fees': 0.0,  # Using IEX data (free)
            'borrowing_costs': 0.0,  # No short selling costs for long-only
            'minimum_commission': 0.0  # No minimum
        }
        
        # Slippage tracking
        self.slippage_stats = {
            'entry_slippage_total': 0.0,
            'exit_slippage_total': 0.0,
            'trade_count': 0
        }
        
        self.logger.info("💰 Enhanced PnL Monitor initialized with fee tracking")
    
    def calculate_regulatory_fees(self, transaction_value: float, side: str) -> float:
        """Calculate regulatory fees for a transaction
        
        Args:
            transaction_value: Dollar value of the transaction (price * quantity)
            side: 'BUY' or 'SELL'
            
        Returns:
            Total regulatory fees in dollars
        """
        fees = self.fee_structure['regulatory_fees']
        
        # SEC fee applies to all sales
        sec_fee = 0.0
        if side == 'SELL':
            sec_fee = transaction_value * fees['sec_fee_rate']
        
        # FINRA TAF applies to all transactions
        finra_taf = transaction_value * fees['finra_taf_rate']
        
        # NSCC fee applies to all transactions
        nscc_fee = transaction_value * fees['nscc_fee']
        
        total_fees = sec_fee + finra_taf + nscc_fee
        
        self.logger.debug(f"💳 Regulatory fees - SEC: ${sec_fee:.4f}, FINRA: ${finra_taf:.4f}, NSCC: ${nscc_fee:.4f}")
        
        return total_fees
    
    def calculate_slippage(self, expected_price: float, actual_price: float, 
                          quantity: int, side: str) -> Dict[str, float]:
        """Calculate slippage for a trade
        
        Args:
            expected_price: Price expected when order was placed
            actual_price: Actual fill price from broker
            quantity: Number of shares
            side: 'BUY' or 'SELL'
            
        Returns:
            Dictionary with slippage metrics
        """
        if side == 'BUY':
            # For buys, positive slippage = paid more than expected
            price_slippage = actual_price - expected_price
        else:
            # For sells, positive slippage = received less than expected
            price_slippage = expected_price - actual_price
        
        slippage_pct = (price_slippage / expected_price) * 100
        slippage_cost = price_slippage * quantity
        
        return {
            'price_slippage': price_slippage,
            'slippage_pct': slippage_pct,
            'slippage_cost': slippage_cost,
            'expected_price': expected_price,
            'actual_price': actual_price
        }
    
    def record_enhanced_trade_entry(self, trade_data: Dict) -> str:
        """Record trade entry with enhanced cost tracking
        
        Args:
            trade_data: Trade entry data including expected vs actual prices
            
        Returns:
            Trade ID
        """
        # Calculate slippage on entry
        expected_price = trade_data['expected_price']
        actual_price = trade_data['actual_fill_price']
        quantity = trade_data['quantity']
        side = trade_data['side']
        
        slippage_data = self.calculate_slippage(
            expected_price, actual_price, quantity, side
        )
        
        # Calculate regulatory fees
        transaction_value = actual_price * quantity
        regulatory_fees = self.calculate_regulatory_fees(transaction_value, side)
        
        # Enhanced trade data
        enhanced_trade_data = {
            **trade_data,
            'entry_price': actual_price,  # Use actual fill price
            'expected_entry_price': expected_price,
            'entry_slippage_pct': slippage_data['slippage_pct'],
            'entry_slippage_cost': slippage_data['slippage_cost'],
            'entry_regulatory_fees': regulatory_fees,
            'entry_total_costs': abs(slippage_data['slippage_cost']) + regulatory_fees
        }
        
        # Track slippage statistics
        self.slippage_stats['entry_slippage_total'] += abs(slippage_data['slippage_cost'])
        self.slippage_stats['trade_count'] += 1
        
        self.logger.info(
            f"📈 Entry recorded - {trade_data['symbol']}: "
            f"Expected: ${expected_price:.4f}, Actual: ${actual_price:.4f}, "
            f"Slippage: {slippage_data['slippage_pct']:.3f}% (${slippage_data['slippage_cost']:.2f}), "
            f"Fees: ${regulatory_fees:.2f}"
        )
        
        # Record with base PnL tracker
        return self.pnl_tracker.record_trade_entry(enhanced_trade_data)
    
    def record_enhanced_trade_exit(self, trade_id: str, exit_data: Dict):
        """Record trade exit with enhanced cost tracking
        
        Args:
            trade_id: Trade identifier
            exit_data: Exit data including expected vs actual prices
        """
        if trade_id not in self.pnl_tracker.current_positions:
            self.logger.warning(f"⚠️ Trade {trade_id} not found for exit recording")
            return
        
        # Get entry trade data
        entry_trade = self.pnl_tracker.current_positions[trade_id]
        
        # Calculate exit slippage
        expected_exit_price = exit_data['expected_price']
        actual_exit_price = exit_data['actual_fill_price']
        quantity = entry_trade['quantity']
        side = 'SELL' if entry_trade['side'] == 'BUY' else 'BUY'  # Opposite side for exit
        
        exit_slippage = self.calculate_slippage(
            expected_exit_price, actual_exit_price, quantity, side
        )
        
        # Calculate exit regulatory fees
        exit_transaction_value = actual_exit_price * quantity
        exit_regulatory_fees = self.calculate_regulatory_fees(exit_transaction_value, side)
        
        # Calculate total costs
        entry_costs = entry_trade.get('entry_total_costs', 0)
        exit_costs = abs(exit_slippage['slippage_cost']) + exit_regulatory_fees
        total_transaction_costs = entry_costs + exit_costs
        
        # Calculate gross and net PnL
        entry_price = entry_trade['entry_price']
        if entry_trade['side'] == 'BUY':
            gross_pnl = (actual_exit_price - entry_price) * quantity
        else:
            gross_pnl = (entry_price - actual_exit_price) * quantity
        
        net_pnl = gross_pnl - total_transaction_costs
        
        # Enhanced exit data
        enhanced_exit_data = {
            **exit_data,
            'exit_price': actual_exit_price,  # Use actual fill price
            'expected_exit_price': expected_exit_price,
            'exit_slippage_pct': exit_slippage['slippage_pct'],
            'exit_slippage_cost': exit_slippage['slippage_cost'],
            'exit_regulatory_fees': exit_regulatory_fees,
            'total_transaction_costs': total_transaction_costs,
            'gross_pnl': gross_pnl,
            'net_pnl': net_pnl,
            'commission': total_transaction_costs  # For compatibility
        }
        
        # Track exit slippage statistics
        self.slippage_stats['exit_slippage_total'] += abs(exit_slippage['slippage_cost'])
        
        # Calculate impact on returns
        cost_impact_pct = (total_transaction_costs / (entry_price * quantity)) * 100
        
        self.logger.info(
            f"📉 Exit recorded - {entry_trade['symbol']}: "
            f"Expected: ${expected_exit_price:.4f}, Actual: ${actual_exit_price:.4f}, "
            f"Exit Slippage: {exit_slippage['slippage_pct']:.3f}% (${exit_slippage['slippage_cost']:.2f}), "
            f"Exit Fees: ${exit_regulatory_fees:.2f}, "
            f"Total Costs: ${total_transaction_costs:.2f} ({cost_impact_pct:.2f}%), "
            f"Gross PnL: ${gross_pnl:.2f}, Net PnL: ${net_pnl:.2f}"
        )
        
        # Record with base PnL tracker
        self.pnl_tracker.record_trade_exit(trade_id, enhanced_exit_data)
    
    def get_cost_analysis(self) -> Dict:
        """Get comprehensive cost analysis
        
        Returns:
            Dictionary with cost breakdown and impact analysis
        """
        # Get session summary from base tracker
        session_summary = self.pnl_tracker.get_session_summary()
        
        if not session_summary['trades']:
            return {
                'total_trades': 0,
                'total_costs': 0,
                'cost_impact_pct': 0
            }
        
        # Calculate comprehensive costs
        total_slippage_costs = (
            self.slippage_stats['entry_slippage_total'] + 
            self.slippage_stats['exit_slippage_total']
        )
        
        total_regulatory_fees = sum(
            trade.get('commission', 0) for trade in session_summary['trades']
        )
        
        total_costs = total_slippage_costs + total_regulatory_fees
        
        # Calculate gross PnL (before costs)
        gross_pnl = sum(
            trade.get('gross_pnl', trade.get('pnl', 0) + trade.get('commission', 0))
            for trade in session_summary['trades']
        )
        
        # Calculate cost impact
        total_volume = sum(
            abs(trade.get('pnl', 0)) + trade.get('commission', 0)
            for trade in session_summary['trades']
        )
        
        cost_impact_pct = (total_costs / total_volume * 100) if total_volume > 0 else 0
        
        # Calculate average slippage
        avg_entry_slippage = (
            self.slippage_stats['entry_slippage_total'] / 
            self.slippage_stats['trade_count']
        ) if self.slippage_stats['trade_count'] > 0 else 0
        
        avg_exit_slippage = (
            self.slippage_stats['exit_slippage_total'] / 
            len(session_summary['trades'])
        ) if session_summary['trades'] else 0
        
        return {
            'total_trades': len(session_summary['trades']),
            'gross_pnl': gross_pnl,
            'net_pnl': session_summary['net_pnl'],
            'total_costs': total_costs,
            'cost_breakdown': {
                'slippage_costs': total_slippage_costs,
                'regulatory_fees': total_regulatory_fees,
                'entry_slippage_avg': avg_entry_slippage,
                'exit_slippage_avg': avg_exit_slippage
            },
            'cost_impact_pct': cost_impact_pct,
            'efficiency_ratio': (session_summary['net_pnl'] / gross_pnl) if gross_pnl != 0 else 0
        }
    
    def print_cost_report(self):
        """Print comprehensive cost analysis report"""
        analysis = self.get_cost_analysis()
        
        print("=" * 60)
        print("💰 ENHANCED PnL REPORT WITH COSTS")
        print("=" * 60)
        print(f"📊 Total Trades: {analysis['total_trades']}")
        print(f"💹 Gross PnL: ${analysis['gross_pnl']:.2f}")
        print(f"💰 Net PnL: ${analysis['net_pnl']:.2f}")
        print(f"💸 Total Costs: ${analysis['total_costs']:.2f}")
        print(f"📉 Cost Impact: {analysis['cost_impact_pct']:.2f}%")
        print(f"⚡ Efficiency Ratio: {analysis['efficiency_ratio']:.3f}")
        print("\n💸 COST BREAKDOWN:")
        costs = analysis['cost_breakdown']
        print(f"   Slippage Costs: ${costs['slippage_costs']:.2f}")
        print(f"   Regulatory Fees: ${costs['regulatory_fees']:.2f}")
        print(f"   Avg Entry Slippage: ${costs['entry_slippage_avg']:.3f}")
        print(f"   Avg Exit Slippage: ${costs['exit_slippage_avg']:.3f}")
        print("=" * 60)

def main():
    """Example usage"""
    monitor = EnhancedPnLMonitor()
    
    # Example trade recording
    trade_data = {
        'symbol': 'AAPL',
        'strategy': 'momentum_scalp',
        'side': 'BUY',
        'quantity': 100,
        'expected_price': 150.00,  # Price when order was placed
        'actual_fill_price': 150.02,  # Actual fill from Alpaca
        'stop_loss': 149.50,
        'take_profit': 150.50,
        'confidence': 0.8
    }
    
    trade_id = monitor.record_enhanced_trade_entry(trade_data)
    
    # Example exit
    exit_data = {
        'expected_price': 150.40,  # Expected exit price
        'actual_fill_price': 150.38,  # Actual exit fill
        'exit_reason': 'profit_target'
    }
    
    monitor.record_enhanced_trade_exit(trade_id, exit_data)
    monitor.print_cost_report()

if __name__ == "__main__":
    main()
