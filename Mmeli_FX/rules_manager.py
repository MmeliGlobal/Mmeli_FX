"""
Rules Manager - Store and manage trading rules
"""

import json
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_STRATEGY_RULES = [
    {
        'id': 1,
        'name': 'Pin Bar Reversal',
        'category': 'Reversal',
        'indicator': 'Pin Bar Candle',
        'confirmation': 'Support/Resistance + Fib 61.8%',
        'rule': 'When a Pin Bar forms at S/R with confluence, enter with 1:2+ RR',
        'enabled': True,
        'signal_type': 'BOTH'
    },
    {
        'id': 2,
        'name': 'Engulfing Trend Continuation',
        'category': 'Continuation',
        'indicator': 'Engulfing Bar',
        'confirmation': 'Trend + SMA 20',
        'rule': 'Engulfing bar in trend direction with pullback to SMA',
        'enabled': True,
        'signal_type': 'BOTH'
    },
    {
        'id': 3,
        'name': 'Morning Star Reversal',
        'category': 'Reversal',
        'indicator': 'Morning Star (3 Candle)',
        'confirmation': 'Support Level + Fibonacci 50%',
        'rule': '3-candle reversal pattern at key support with 1:2+ RR',
        'enabled': True,
        'signal_type': 'BUY'
    },
    {
        'id': 4,
        'name': 'Evening Star Reversal',
        'category': 'Reversal',
        'indicator': 'Evening Star (3 Candle)',
        'confirmation': 'Resistance Level + Fibonacci 61.8%',
        'rule': '3-candle reversal pattern at key resistance with 1:2+ RR',
        'enabled': True,
        'signal_type': 'SELL'
    },
    {
        'id': 5,
        'name': 'Order Block SMC',
        'category': 'SMC',
        'indicator': 'Order Block (Bullish/Bearish)',
        'confirmation': 'Mitigation + FVG',
        'rule': 'Price returning to order block with FVG confirmation',
        'enabled': True,
        'signal_type': 'BOTH'
    },
    {
        'id': 6,
        'name': 'Liquidity Sweep',
        'category': 'SMC',
        'indicator': 'Liquidity Zone',
        'confirmation': 'Reversal Candle',
        'rule': 'Sweep of previous day high/low with reversal confirmation',
        'enabled': True,
        'signal_type': 'BOTH'
    },
    {
        'id': 7,
        'name': 'Double Bottom Reversal',
        'category': 'Chart Patterns',
        'indicator': 'Double Bottom',
        'confirmation': 'Break of Middle Peak',
        'rule': 'Double bottom formation with break above middle peak',
        'enabled': True,
        'signal_type': 'BUY'
    },
    {
        'id': 8,
        'name': 'Head & Shoulders Reversal',
        'category': 'Chart Patterns',
        'indicator': 'Head & Shoulders',
        'confirmation': 'Neckline Breakdown',
        'rule': 'Head & shoulders formation with neckline breakdown',
        'enabled': True,
        'signal_type': 'SELL'
    },
    {
        'id': 9,
        'name': 'FVG Fill',
        'category': 'SMC',
        'indicator': 'FVG Zone',
        'confirmation': 'Price Reaction',
        'rule': 'Price returning to fill FVG with reversal confirmation',
        'enabled': True,
        'signal_type': 'BOTH'
    }
]

class RulesManager:
    def __init__(self):
        self.rules_file = 'data/rules.json'
        self.rules = []
        self.load_rules()
    
    def load_rules(self):
        try:
            os.makedirs('data', exist_ok=True)
            
            if os.path.exists(self.rules_file):
                with open(self.rules_file, 'r') as f:
                    self.rules = json.load(f)
                logger.info(f"Loaded {len(self.rules)} rules")
            else:
                self.rules = DEFAULT_STRATEGY_RULES.copy()
                self.save_rules()
                logger.info(f"Created {len(self.rules)} default rules")
        except Exception as e:
            logger.error(f"Error loading rules: {e}")
            self.rules = DEFAULT_STRATEGY_RULES.copy()
    
    def save_rules(self):
        try:
            with open(self.rules_file, 'w') as f:
                json.dump(self.rules, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error saving rules: {e}")
            return False
    
    def get_rules(self):
        return self.rules
    
    def get_rule(self, rule_id):
        for rule in self.rules:
            if rule.get('id') == rule_id:
                return rule
        return None
    
    def get_enabled_rules(self):
        return [r for r in self.rules if r.get('enabled', True)]
    
    def get_rules_by_category(self, category):
        return [r for r in self.rules if r.get('category') == category]
    
    def create_rule(self, rule_data):
        try:
            max_id = max([r.get('id', 0) for r in self.rules]) if self.rules else 0
            rule_data['id'] = max_id + 1
            rule_data['created_at'] = datetime.now().isoformat()
            rule_data['enabled'] = True
            
            self.rules.append(rule_data)
            self.save_rules()
            return rule_data
        except Exception as e:
            logger.error(f"Error creating rule: {e}")
            return None
    
    def update_rule(self, rule_id, rule_data):
        try:
            for i, rule in enumerate(self.rules):
                if rule.get('id') == rule_id:
                    rule_data['id'] = rule_id
                    rule_data['updated_at'] = datetime.now().isoformat()
                    if 'created_at' not in rule_data:
                        rule_data['created_at'] = rule.get('created_at', datetime.now().isoformat())
                    self.rules[i] = rule_data
                    self.save_rules()
                    return rule_data
            return None
        except Exception as e:
            logger.error(f"Error updating rule: {e}")
            return None
    
    def delete_rule(self, rule_id):
        try:
            self.rules = [r for r in self.rules if r.get('id') != rule_id]
            self.save_rules()
            return True
        except Exception as e:
            logger.error(f"Error deleting rule: {e}")
            return False
    
    def toggle_rule(self, rule_id):
        try:
            for rule in self.rules:
                if rule.get('id') == rule_id:
                    rule['enabled'] = not rule.get('enabled', True)
                    self.save_rules()
                    return rule
            return None
        except Exception as e:
            logger.error(f"Error toggling rule: {e}")
            return None