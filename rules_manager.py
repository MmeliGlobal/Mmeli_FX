"""
Rules Manager - Complete Strategy Rules
Combining all strategies from your document
"""

import json
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_STRATEGY_RULES = [
    # ==========================================
    # ORIGINAL RULES (KEPT - These are good!)
    # ==========================================
    {
        'id': 1,
        'name': 'Pin Bar Reversal',
        'category': 'Reversal',
        'indicator': 'Pin Bar Candle',
        'confirmation': 'Support/Resistance + Fib 61.8%',
        'rule': 'When a Pin Bar forms at S/R with confluence, enter with 1:2+ RR',
        'enabled': True,
        'signal_type': 'BOTH',
        'timeframe': 'H1/H4 zone, M15 entry'
    },
    {
        'id': 2,
        'name': 'Engulfing Trend Continuation',
        'category': 'Continuation',
        'indicator': 'Engulfing Bar',
        'confirmation': 'Trend + SMA 20',
        'rule': 'Engulfing bar in trend direction with pullback to SMA',
        'enabled': True,
        'signal_type': 'BOTH',
        'timeframe': 'H1/H4 trend, M15 entry'
    },
    {
        'id': 3,
        'name': 'Double Bottom Reversal',
        'category': 'Chart Patterns',
        'indicator': 'Double Bottom',
        'confirmation': 'Break of Middle Peak',
        'rule': 'Double bottom formation with break above middle peak',
        'enabled': True,
        'signal_type': 'BUY',
        'timeframe': 'H4 chart, H1 entry'
    },
    {
        'id': 4,
        'name': 'Double Top Reversal',
        'category': 'Chart Patterns',
        'indicator': 'Double Top',
        'confirmation': 'Break of Middle Valley',
        'rule': 'Double top formation with break below middle valley',
        'enabled': True,
        'signal_type': 'SELL',
        'timeframe': 'H4 chart, H1 entry'
    },

    # ==========================================
    # STRATEGY A — TREND PULLBACK (Your Strategy)
    # ==========================================
    {
        'id': 5,
        'name': 'Trend Pullback - Long (50/200 EMA)',
        'category': 'Trend Pullback',
        'indicator': '50 EMA > 200 EMA + Higher highs/higher lows + Price at 50 EMA/Support',
        'confirmation': 'Bullish rejection wick OR Bullish Engulfing OR Pin Bar',
        'rule': 'In bullish trend, price pulls back to 50 EMA or support zone. Enter BUY on bullish confirmation. Stop below swing low. Target next resistance. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'BUY',
        'timeframe': 'H4/H1 for trend, M15/M5 for entry'
    },
    {
        'id': 6,
        'name': 'Trend Pullback - Short (50/200 EMA)',
        'category': 'Trend Pullback',
        'indicator': '50 EMA < 200 EMA + Lower highs/lower lows + Price at 50 EMA/Resistance',
        'confirmation': 'Bearish rejection wick OR Bearish Engulfing OR Pin Bar',
        'rule': 'In bearish trend, price pulls back to 50 EMA or resistance zone. Enter SELL on bearish confirmation. Stop above swing high. Target next support. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'SELL',
        'timeframe': 'H4/H1 for trend, M15/M5 for entry'
    },

    # ==========================================
    # STRATEGY B — BREAKOUT + RETEST (Your Strategy)
    # ==========================================
    {
        'id': 7,
        'name': 'Breakout + Retest - Long',
        'category': 'Breakout',
        'indicator': 'Price breaks above resistance + Closes above zone',
        'confirmation': 'Pullback to resistance-turned-support + Bullish rejection',
        'rule': 'After breakout above resistance, wait for pullback and retest with bullish confirmation. Enter BUY. Stop below retest zone. Target measured move or next resistance.',
        'enabled': True,
        'signal_type': 'BUY',
        'timeframe': 'H1/H4 for zone, M15 for entry'
    },
    {
        'id': 8,
        'name': 'Breakout + Retest - Short',
        'category': 'Breakout',
        'indicator': 'Price breaks below support + Closes below zone',
        'confirmation': 'Pullback to support-turned-resistance + Bearish rejection',
        'rule': 'After breakdown below support, wait for pullback and retest with bearish confirmation. Enter SELL. Stop above retest zone. Target measured move or next support.',
        'enabled': True,
        'signal_type': 'SELL',
        'timeframe': 'H1/H4 for zone, M15 for entry'
    },

    # ==========================================
    # STRATEGY C — SUPPORT/RESISTANCE REVERSAL (Your Strategy)
    # ==========================================
    {
        'id': 9,
        'name': 'Support Reversal - Long',
        'category': 'S/R Reversal',
        'indicator': 'Price at Strong Support Zone',
        'confirmation': 'Bullish rejection (Pin Bar/Engulfing) + Structure break',
        'rule': 'At key support zone with bullish rejection and structure break. Enter BUY. Stop below support. Target next resistance. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'BUY',
        'timeframe': 'H1/H4 zone, M15 for entry'
    },
    {
        'id': 10,
        'name': 'Resistance Reversal - Short',
        'category': 'S/R Reversal',
        'indicator': 'Price at Strong Resistance Zone',
        'confirmation': 'Bearish rejection (Pin Bar/Engulfing) + Structure break',
        'rule': 'At key resistance zone with bearish rejection and structure break. Enter SELL. Stop above resistance. Target next support. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'SELL',
        'timeframe': 'H1/H4 zone, M15 for entry'
    },

    # ==========================================
    # STRATEGY D — RANGE TRADING (Your Strategy)
    # ==========================================
    {
        'id': 11,
        'name': 'Range Trading - Long at Support',
        'category': 'Range',
        'indicator': 'Price at Range Support Boundary + Sideways market',
        'confirmation': 'Bullish rejection (Pin Bar/Engulfing) at support',
        'rule': 'At range support boundary with bullish rejection. Enter BUY. Stop below range. Target range middle or resistance. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'BUY',
        'timeframe': 'H1 for range, M15 for entry'
    },
    {
        'id': 12,
        'name': 'Range Trading - Short at Resistance',
        'category': 'Range',
        'indicator': 'Price at Range Resistance Boundary + Sideways market',
        'confirmation': 'Bearish rejection (Pin Bar/Engulfing) at resistance',
        'rule': 'At range resistance boundary with bearish rejection. Enter SELL. Stop above range. Target range middle or support. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'SELL',
        'timeframe': 'H1 for range, M15 for entry'
    },

    # ==========================================
    # STRATEGY E — LIQUIDITY SWEEP + REVERSAL (Your Strategy)
    # ==========================================
    {
        'id': 13,
        'name': 'Liquidity Sweep - Long',
        'category': 'Liquidity Sweep',
        'indicator': 'Price sweeps below previous low/equal lows + Closes back inside',
        'confirmation': 'Bullish close after sweep + Structure break',
        'rule': 'After liquidity sweep below support with bullish close and structure break. Enter BUY. Stop below sweep low. Target next liquidity zone. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'BUY',
        'timeframe': 'H1/H4 zone, M15 for entry'
    },
    {
        'id': 14,
        'name': 'Liquidity Sweep - Short',
        'category': 'Liquidity Sweep',
        'indicator': 'Price sweeps above previous high/equal highs + Closes back inside',
        'confirmation': 'Bearish close after sweep + Structure break',
        'rule': 'After liquidity sweep above resistance with bearish close and structure break. Enter SELL. Stop above sweep high. Target next liquidity zone. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'SELL',
        'timeframe': 'H1/H4 zone, M15 for entry'
    },

    # ==========================================
    # STRATEGY F — MOVING AVERAGE CONFLUENCE (Your Strategy)
    # ==========================================
    {
        'id': 15,
        'name': 'MA Confluence - Long',
        'category': 'Moving Average',
        'indicator': 'Price at 50 EMA + 200 EMA confluence + Bullish trend',
        'confirmation': 'Bullish rejection at MA confluence zone',
        'rule': 'When price pulls back to 50/200 EMA confluence in bullish trend with rejection. Enter BUY. Stop below MA zone. Target next resistance. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'BUY',
        'timeframe': 'H4 trend, H1 zone, M15 entry'
    },
    {
        'id': 16,
        'name': 'MA Confluence - Short',
        'category': 'Moving Average',
        'indicator': 'Price at 50 EMA + 200 EMA confluence + Bearish trend',
        'confirmation': 'Bearish rejection at MA confluence zone',
        'rule': 'When price pulls back to 50/200 EMA confluence in bearish trend with rejection. Enter SELL. Stop above MA zone. Target next support. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'SELL',
        'timeframe': 'H4 trend, H1 zone, M15 entry'
    },

    # ==========================================
    # STRATEGY G — FIBONACCI RETRACEMENT (Your Strategy)
    # ==========================================
    {
        'id': 17,
        'name': 'Fibonacci 61.8% - Long',
        'category': 'Fibonacci',
        'indicator': 'Price at 61.8% Fibonacci retracement + Bullish trend',
        'confirmation': 'Bullish rejection at Fib 61.8% level',
        'rule': 'When price retraces to 61.8% Fib level in bullish trend with rejection. Enter BUY. Stop below Fib level. Target previous high. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'BUY',
        'timeframe': 'H4 swing, H1 zone, M15 entry'
    },
    {
        'id': 18,
        'name': 'Fibonacci 61.8% - Short',
        'category': 'Fibonacci',
        'indicator': 'Price at 61.8% Fibonacci retracement + Bearish trend',
        'confirmation': 'Bearish rejection at Fib 61.8% level',
        'rule': 'When price retraces to 61.8% Fib level in bearish trend with rejection. Enter SELL. Stop above Fib level. Target previous low. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'SELL',
        'timeframe': 'H4 swing, H1 zone, M15 entry'
    },

    # ==========================================
    # STRATEGY H — CANDLESTICK PATTERNS (Location-based)
    # ==========================================
    {
        'id': 19,
        'name': 'Pin Bar Reversal - Long',
        'category': 'Candlestick',
        'indicator': 'Bullish Pin Bar at Support/Zone',
        'confirmation': 'Structure break + Close above pin bar high',
        'rule': 'Bullish pin bar at key support zone. Enter BUY on structure break. Stop below pin bar low. Target next resistance. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'BUY',
        'timeframe': 'H1/H4 zone, M15 entry'
    },
    {
        'id': 20,
        'name': 'Pin Bar Reversal - Short',
        'category': 'Candlestick',
        'indicator': 'Bearish Pin Bar at Resistance/Zone',
        'confirmation': 'Structure break + Close below pin bar low',
        'rule': 'Bearish pin bar at key resistance zone. Enter SELL on structure break. Stop above pin bar high. Target next support. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'SELL',
        'timeframe': 'H1/H4 zone, M15 entry'
    },
    {
        'id': 21,
        'name': 'Engulfing Reversal - Long',
        'category': 'Candlestick',
        'indicator': 'Bullish Engulfing at Support/Zone',
        'confirmation': 'Structure break + Close above engulfing high',
        'rule': 'Bullish engulfing at key support zone. Enter BUY on structure break. Stop below engulfing low. Target next resistance. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'BUY',
        'timeframe': 'H1/H4 zone, M15 entry'
    },
    {
        'id': 22,
        'name': 'Engulfing Reversal - Short',
        'category': 'Candlestick',
        'indicator': 'Bearish Engulfing at Resistance/Zone',
        'confirmation': 'Structure break + Close below engulfing low',
        'rule': 'Bearish engulfing at key resistance zone. Enter SELL on structure break. Stop above engulfing high. Target next support. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'SELL',
        'timeframe': 'H1/H4 zone, M15 entry'
    },
    {
        'id': 23,
        'name': 'Inside Bar Breakout - Long',
        'category': 'Candlestick',
        'indicator': 'Inside Bar + Bullish Breakout',
        'confirmation': 'Break above mother bar high + Momentum candle',
        'rule': 'Inside bar with breakout above mother bar in bullish context. Enter BUY. Stop below mother bar low. Target next resistance. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'BUY',
        'timeframe': 'H1/H4 zone, M15 entry'
    },
    {
        'id': 24,
        'name': 'Inside Bar Breakout - Short',
        'category': 'Candlestick',
        'indicator': 'Inside Bar + Bearish Breakout',
        'confirmation': 'Break below mother bar low + Momentum candle',
        'rule': 'Inside bar with breakout below mother bar in bearish context. Enter SELL. Stop above mother bar high. Target next support. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'SELL',
        'timeframe': 'H1/H4 zone, M15 entry'
    },

    # ==========================================
    # STRATEGY I — MULTI-TIMEFRAME CONFIRMATION
    # ==========================================
    {
        'id': 25,
        'name': 'Multi-TF Bullish Confluence (A+ Setup)',
        'category': 'Multi-Timeframe',
        'indicator': 'H4 Bullish + H1 Support Zone + M15 Rejection',
        'confirmation': 'M15 bullish rejection + Structure break',
        'rule': 'H4 bullish trend + H1 support zone + M15 bullish confirmation. Enter BUY. Stop below zone. Target H1 resistance. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'BUY',
        'timeframe': 'H4/H1/M15'
    },
    {
        'id': 26,
        'name': 'Multi-TF Bearish Confluence (A+ Setup)',
        'category': 'Multi-Timeframe',
        'indicator': 'H4 Bearish + H1 Resistance Zone + M15 Rejection',
        'confirmation': 'M15 bearish rejection + Structure break',
        'rule': 'H4 bearish trend + H1 resistance zone + M15 bearish confirmation. Enter SELL. Stop above zone. Target H1 support. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'SELL',
        'timeframe': 'H4/H1/M15'
    },

    # ==========================================
    # STRATEGY J — LIQUIDITY + ZONE (Advanced)
    # ==========================================
    {
        'id': 27,
        'name': 'Liquidity + Support - Long',
        'category': 'Liquidity + Zone',
        'indicator': 'Liquidity sweep below + Price at Support',
        'confirmation': 'Bullish close back above support + Structure break',
        'rule': 'Liquidity sweep below support with bullish close and structure break. Enter BUY. Stop below sweep low. Target next resistance. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'BUY',
        'timeframe': 'H1 zone, M15 entry'
    },
    {
        'id': 28,
        'name': 'Liquidity + Resistance - Short',
        'category': 'Liquidity + Zone',
        'indicator': 'Liquidity sweep above + Price at Resistance',
        'confirmation': 'Bearish close back below resistance + Structure break',
        'rule': 'Liquidity sweep above resistance with bearish close and structure break. Enter SELL. Stop above sweep high. Target next support. Min R:R 1:2.',
        'enabled': True,
        'signal_type': 'SELL',
        'timeframe': 'H1 zone, M15 entry'
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
                logger.info(f"Loaded {len(self.rules)} rules from file")
            else:
                self.rules = DEFAULT_STRATEGY_RULES.copy()
                self.save_rules()
                logger.info(f"Created {len(self.rules)} default strategy rules")
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
    
    def get_rules_by_signal_type(self, signal_type):
        return [r for r in self.rules if r.get('signal_type') == signal_type or r.get('signal_type') == 'BOTH']
    
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