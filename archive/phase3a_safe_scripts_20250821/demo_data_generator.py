"""
🎯 Demo Data Generator - Realistic Trading Simulation
Creates realistic trading data that reflects actual Thursday performance:
- INTC: Profitable (75% win rate) 
- SOXL, SOFI, TQQQ: Unprofitable (35-45% win rates)
- Other symbols: Mixed performance (60-65% win rates)
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

class DemoDataGenerator:
    def __init__(self):
        """Initialize demo data generator with realistic parameters"""
        self.symbols = {
            # High performers (profitable on Thursday)
            'INTC': {'win_rate': 0.75, 'avg_profit': 0.85, 'avg_loss': -0.45, 'trade_count': 18},
            
            # Poor performers (unprofitable on Thursday)
            'SOXL': {'win_rate': 0.35, 'avg_profit': 0.65, 'avg_loss': -0.75, 'trade_count': 22},
            'SOFI': {'win_rate': 0.40, 'avg_profit': 0.55, 'avg_loss': -0.85, 'trade_count': 16},
            'TQQQ': {'win_rate': 0.45, 'avg_profit': 0.70, 'avg_loss': -0.90, 'trade_count': 20},
            
            # Mixed performers
            'AAPL': {'win_rate': 0.62, 'avg_profit': 0.75, 'avg_loss': -0.60, 'trade_count': 14},
            'TSLA': {'win_rate': 0.58, 'avg_profit': 1.20, 'avg_loss': -0.95, 'trade_count': 12},
            'NVDA': {'win_rate': 0.68, 'avg_profit': 0.90, 'avg_loss': -0.55, 'trade_count': 15},
        }
        
        self.strategies = ['momentum_scalp', 'mean_reversion', 'vwap_bounce']
        
        # Thursday's base time (yesterday)
        self.base_date = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0) - timedelta(days=1)
        
    def generate_realistic_trades(self) -> List[Dict[str, Any]]:
        """Generate realistic trade data reflecting Thursday's actual performance"""
        trades = []
        
        for symbol, params in self.symbols.items():
            symbol_trades = self._generate_symbol_trades(symbol, params)
            trades.extend(symbol_trades)
            
        # Sort by timestamp
        trades.sort(key=lambda x: x['filled_at'])
        
        return trades
    
    def _generate_symbol_trades(self, symbol: str, params: Dict) -> List[Dict[str, Any]]:
        """Generate trades for a specific symbol with realistic patterns"""
        trades = []
        trade_count = params['trade_count']
        win_rate = params['win_rate']
        
        for i in range(trade_count):
            # Generate realistic timestamp throughout trading day
            minutes_offset = random.randint(0, 390)  # 6.5 hour trading day
            timestamp = self.base_date + timedelta(minutes=minutes_offset)
            
            # Determine if this trade is a winner
            is_winner = random.random() < win_rate
            
            # Generate trade details
            trade = self._create_trade(symbol, timestamp, is_winner, params, i)
            trades.append(trade)
            
        return trades
    
    def _create_trade(self, symbol: str, timestamp: datetime, is_winner: bool, params: Dict, trade_index: int) -> Dict[str, Any]:
        """Create a single realistic trade"""
        # Random strategy selection
        strategy = random.choice(self.strategies)
        
        # Random side (buy/sell to open position)
        side = random.choice(['buy', 'sell'])
        
        # Realistic share quantities (varying by price level)
        if symbol in ['INTC', 'SOFI']:
            qty = random.randint(50, 200)  # Lower priced stocks
        elif symbol in ['SOXL', 'TQQQ']:
            qty = random.randint(30, 150)  # Mid-range ETFs
        else:
            qty = random.randint(10, 50)   # Higher priced stocks
            
        # Base price (realistic for each symbol)
        base_prices = {
            'INTC': 32.50, 'SOXL': 28.75, 'SOFI': 8.25, 'TQQQ': 42.30,
            'AAPL': 185.20, 'TSLA': 245.80, 'NVDA': 435.60
        }
        
        fill_price = base_prices.get(symbol, 50.0) + random.uniform(-2.0, 2.0)
        
        # Calculate P&L based on performance
        if is_winner:
            pnl_percent = random.uniform(0.1, params['avg_profit'])
        else:
            pnl_percent = random.uniform(params['avg_loss'], -0.1)
            
        pnl_amount = fill_price * qty * (pnl_percent / 100)
        
        # Generate unique trade ID
        trade_id = str(uuid.uuid4())[:8]
        order_id = str(uuid.uuid4())
        
        return {
            'id': trade_id,
            'order_id': order_id,
            'symbol': symbol,
            'side': side,
            'qty': str(qty),
            'filled_qty': str(qty),
            'filled_at': timestamp.isoformat(),
            'filled_avg_price': str(round(fill_price, 2)),
            'status': 'filled',
            'strategy': strategy,
            'pnl': round(pnl_amount, 2),
            'pnl_percent': round(pnl_percent, 3),
            'commission': round(qty * 0.005, 2),  # Realistic commission
            'time_in_force': 'day',
            'order_class': 'simple'
        }
    
    def save_demo_data(self, filename: str = None) -> str:
        """Generate and save demo trading data"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"demo_trades_{timestamp}.json"
            
        trades = self.generate_realistic_trades()
        
        # Add summary statistics
        demo_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'description': 'Realistic demo data reflecting Thursday trading performance',
                'total_trades': len(trades),
                'date_simulated': self.base_date.date().isoformat(),
                'note': 'INTC profitable, SOXL/SOFI/TQQQ unprofitable as per actual Thursday results'
            },
            'trades': trades,
            'summary': self._calculate_summary(trades)
        }
        
        # Save to file
        filepath = f"c:\\Users\\will7\\OneDrive - Sygma Data Analytics\\Stock Trading\\Scalping Bot System\\data\\{filename}"
        with open(filepath, 'w') as f:
            json.dump(demo_data, f, indent=2)
            
        return filepath
    
    def _calculate_summary(self, trades: List[Dict]) -> Dict[str, Any]:
        """Calculate summary statistics for the trades"""
        if not trades:
            return {}
            
        total_pnl = sum(trade['pnl'] for trade in trades)
        total_commission = sum(trade['commission'] for trade in trades)
        net_pnl = total_pnl - total_commission
        
        winners = [t for t in trades if t['pnl'] > 0]
        losers = [t for t in trades if t['pnl'] < 0]
        
        # Per-symbol summary
        symbol_summary = {}
        for symbol in set(trade['symbol'] for trade in trades):
            symbol_trades = [t for t in trades if t['symbol'] == symbol]
            symbol_winners = [t for t in symbol_trades if t['pnl'] > 0]
            
            symbol_summary[symbol] = {
                'total_trades': len(symbol_trades),
                'winners': len(symbol_winners),
                'win_rate': len(symbol_winners) / len(symbol_trades) if symbol_trades else 0,
                'total_pnl': sum(t['pnl'] for t in symbol_trades),
                'avg_pnl_per_trade': sum(t['pnl'] for t in symbol_trades) / len(symbol_trades) if symbol_trades else 0
            }
        
        return {
            'total_trades': len(trades),
            'winners': len(winners),
            'losers': len(losers),
            'win_rate': len(winners) / len(trades) if trades else 0,
            'total_gross_pnl': round(total_pnl, 2),
            'total_commission': round(total_commission, 2),
            'net_pnl': round(net_pnl, 2),
            'avg_pnl_per_trade': round(total_pnl / len(trades), 2) if trades else 0,
            'best_trade': max(trades, key=lambda x: x['pnl'])['pnl'] if trades else 0,
            'worst_trade': min(trades, key=lambda x: x['pnl'])['pnl'] if trades else 0,
            'symbol_breakdown': symbol_summary
        }

def main():
    """Generate demo data and print summary"""
    generator = DemoDataGenerator()
    
    print("🎯 Generating Realistic Demo Trading Data...")
    print("📊 Reflecting Thursday's Performance:")
    print("   ✅ INTC: Profitable (75% win rate)")
    print("   ❌ SOXL, SOFI, TQQQ: Unprofitable (35-45% win rates)")
    print("   📈 Others: Mixed performance (60-65% win rates)")
    print()
    
    # Generate and save data
    filepath = generator.save_demo_data()
    
    # Load and display summary
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    summary = data['summary']
    
    print(f"📁 Demo data saved to: {filepath}")
    print(f"📊 Generated {summary['total_trades']} trades for {len(summary['symbol_breakdown'])} symbols")
    print(f"💰 Net P&L: ${summary['net_pnl']:,.2f}")
    print(f"🎯 Overall Win Rate: {summary['win_rate']:.1%}")
    print()
    
    print("📈 Symbol Performance:")
    for symbol, stats in summary['symbol_breakdown'].items():
        status = "✅" if stats['total_pnl'] > 0 else "❌"
        print(f"   {status} {symbol}: {stats['win_rate']:.1%} win rate, ${stats['total_pnl']:+.2f} P&L ({stats['total_trades']} trades)")
    
if __name__ == "__main__":
    main()
