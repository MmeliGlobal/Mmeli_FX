"""
Signal History Manager - Track all signals and their outcomes
"""

import json
import os
import logging
from datetime import datetime
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignalHistory:
    def __init__(self):
        self.history_file = 'data/signal_history.json'
        self.signals = []
        self.load_history()
    
    def load_history(self):
        """Load signal history from file"""
        try:
            os.makedirs('data', exist_ok=True)
            
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.signals = json.load(f)
                logger.info(f"Loaded {len(self.signals)} historical signals")
            else:
                self.signals = []
                self.save_history()
                logger.info("Created new signal history file")
        except Exception as e:
            logger.error(f"Error loading signal history: {e}")
            self.signals = []
    
    def save_history(self):
        """Save signal history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.signals, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error saving signal history: {e}")
            return False
    
    def add_signal(self, signal):
        """Add a new signal to history"""
        try:
            # Create a copy to avoid modifying original
            signal_record = signal.copy()
            
            # Add timestamp
            signal_record['created_at'] = datetime.now().isoformat()
            signal_record['status'] = 'PENDING'  # PENDING, HIT_TP, HIT_SL, CLOSED
            signal_record['closed_at'] = None
            signal_record['actual_pnl'] = None
            signal_record['actual_rr'] = None
            
            # Add to history (newest first)
            self.signals.insert(0, signal_record)
            
            # Keep only last 1000 signals
            if len(self.signals) > 1000:
                self.signals = self.signals[:1000]
            
            self.save_history()
            logger.info(f"✅ Signal added to history: {signal.get('symbol')} {signal.get('action')}")
            return signal_record
        except Exception as e:
            logger.error(f"Error adding signal: {e}")
            return None
    
    def update_signal_status(self, signal_id, status, actual_pnl=None, actual_rr=None):
        """Update a signal's status"""
        try:
            for signal in self.signals:
                if signal.get('id') == signal_id:
                    signal['status'] = status
                    signal['closed_at'] = datetime.now().isoformat()
                    if actual_pnl is not None:
                        signal['actual_pnl'] = actual_pnl
                    if actual_rr is not None:
                        signal['actual_rr'] = actual_rr
                    self.save_history()
                    return signal
            return None
        except Exception as e:
            logger.error(f"Error updating signal: {e}")
            return None
    
    def get_statistics(self):
        """Get signal statistics"""
        total = len(self.signals)
        
        if total == 0:
            return {
                'total': 0,
                'pending': 0,
                'hit_tp': 0,
                'hit_sl': 0,
                'closed': 0,
                'win_rate': 0,
                'avg_rr': 0,
                'best_pattern': 'N/A',
                'worst_pattern': 'N/A',
                'best_symbol': 'N/A',
                'worst_symbol': 'N/A'
            }
        
        # Count by status
        pending = sum(1 for s in self.signals if s.get('status') == 'PENDING')
        hit_tp = sum(1 for s in self.signals if s.get('status') == 'HIT_TP')
        hit_sl = sum(1 for s in self.signals if s.get('status') == 'HIT_SL')
        closed = sum(1 for s in self.signals if s.get('status') == 'CLOSED')
        
        # Calculate win rate
        closed_trades = hit_tp + hit_sl
        win_rate = round((hit_tp / closed_trades * 100) if closed_trades > 0 else 0, 1)
        
        # Calculate average RR
        completed = [s for s in self.signals if s.get('status') in ['HIT_TP', 'HIT_SL']]
        avg_rr = round(sum(s.get('risk_reward', 0) for s in completed) / len(completed) if completed else 0, 1)
        
        # Best and worst patterns
        pattern_counts = defaultdict(lambda: {'total': 0, 'won': 0})
        for s in self.signals:
            pattern = s.get('pattern', 'Unknown')
            pattern_counts[pattern]['total'] += 1
            if s.get('status') == 'HIT_TP':
                pattern_counts[pattern]['won'] += 1
        
        best_pattern = 'N/A'
        worst_pattern = 'N/A'
        best_rate = 0
        worst_rate = 100
        
        for pattern, data in pattern_counts.items():
            if data['total'] >= 3:  # Only consider patterns with 3+ signals
                rate = (data['won'] / data['total'] * 100)
                if rate > best_rate:
                    best_rate = rate
                    best_pattern = pattern
                if rate < worst_rate:
                    worst_rate = rate
                    worst_pattern = pattern
        
        # Best and worst symbols
        symbol_counts = defaultdict(lambda: {'total': 0, 'won': 0})
        for s in self.signals:
            symbol = s.get('symbol', 'Unknown')
            symbol_counts[symbol]['total'] += 1
            if s.get('status') == 'HIT_TP':
                symbol_counts[symbol]['won'] += 1
        
        best_symbol = 'N/A'
        worst_symbol = 'N/A'
        best_sym_rate = 0
        worst_sym_rate = 100
        
        for symbol, data in symbol_counts.items():
            if data['total'] >= 3:
                rate = (data['won'] / data['total'] * 100)
                if rate > best_sym_rate:
                    best_sym_rate = rate
                    best_symbol = symbol
                if rate < worst_sym_rate:
                    worst_sym_rate = rate
                    worst_symbol = symbol
        
        return {
            'total': total,
            'pending': pending,
            'hit_tp': hit_tp,
            'hit_sl': hit_sl,
            'closed': closed,
            'win_rate': win_rate,
            'avg_rr': avg_rr,
            'best_pattern': best_pattern,
            'worst_pattern': worst_pattern,
            'best_symbol': best_symbol,
            'worst_symbol': worst_symbol
        }
    
    def get_recent(self, limit=50):
        """Get recent signals"""
        return self.signals[:limit]
    
    def get_by_symbol(self, symbol):
        """Get signals for a specific symbol"""
        return [s for s in self.signals if s.get('symbol') == symbol]
    
    def clear_history(self):
        """Clear all signal history"""
        self.signals = []
        self.save_history()
        logger.info("Signal history cleared")

# Create global instance
signal_history = SignalHistory()