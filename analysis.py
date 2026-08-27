"""
Trading Analysis Engine
"""

import pandas as pd
import numpy as np
import logging
from patterns import CandlePatternDetector, ChartPatternDetector, SMCDetector
from config import DEFAULT_RULES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingAnalyzer:
    def __init__(self):
        self.rules = DEFAULT_RULES.copy()
        self.pin_bar_ratio = self.rules.get('pin_bar_ratio', 2.0)
        self.engulfing_min_ratio = self.rules.get('engulfing_min_ratio', 1.2)
        self.doji_body_threshold = self.rules.get('doji_body_threshold', 0.0003)
        self.confluence_tolerance = self.rules.get('confluence_tolerance', 0.005)
        self.swing_strength = self.rules.get('swing_strength', 5)
        self.min_risk_reward = self.rules.get('min_risk_reward', 2.0)
        self.trend_filter = self.rules.get('trend_filter', True)
        
        self.candle_detector = CandlePatternDetector()
        self.chart_detector = ChartPatternDetector()
        self.smc_detector = SMCDetector()
        
    def analyze_symbol(self, df_htf, df_ttf, current_price):
        """Complete analysis"""
        try:
            trend = self.identify_trend(df_htf)
            support, resistance = self.find_support_resistance(df_htf)
            fib = self.calculate_fibonacci(df_htf)
            sma20 = df_htf['Close'].rolling(window=20).mean().iloc[-1] if len(df_htf) > 20 else None
            patterns = self.candle_detector.detect_all_patterns(df_ttf)
            signals = self.generate_signals(current_price, patterns, support, resistance, fib, sma20, trend)
            
            chart_data = self.prepare_chart_data(df_ttf, support, resistance, fib, patterns)
            
            return {
                'trend': trend,
                'support_levels': support[-3:],
                'resistance_levels': resistance[-3:],
                'fibonacci': fib,
                'sma': {'sma20': sma20} if sma20 else {},
                'patterns': patterns,
                'signals': signals,
                'chart_data': chart_data,
                'current_price': current_price
            }
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return None
    
    def identify_trend(self, df):
        try:
            recent_high = df['High'].iloc[-10:].values
            recent_low = df['Low'].iloc[-10:].values
            
            higher_highs = all(recent_high[i] < recent_high[i+1] for i in range(len(recent_high)-1))
            higher_lows = all(recent_low[i] < recent_low[i+1] for i in range(len(recent_low)-1))
            
            if higher_highs and higher_lows:
                return 'BULLISH'
            
            lower_highs = all(recent_high[i] > recent_high[i+1] for i in range(len(recent_high)-1))
            lower_lows = all(recent_low[i] > recent_low[i+1] for i in range(len(recent_low)-1))
            
            if lower_highs and lower_lows:
                return 'BEARISH'
            
            recent_close = df['Close'].iloc[-20:].values
            range_pct = (recent_close.max() - recent_close.min()) / recent_close.mean()
            
            if range_pct < 0.02:
                return 'RANGING'
            return 'CHOPPY'
        except:
            return 'RANGING'
    
    def find_support_resistance(self, df):
        try:
            highs = df['High'].values
            lows = df['Low'].values
            strength = self.swing_strength
            
            resistance = []
            support = []
            
            for i in range(strength, len(highs) - strength):
                if all(highs[i] >= highs[i-j] for j in range(1, strength+1)) and \
                   all(highs[i] >= highs[i+j] for j in range(1, strength+1)):
                    resistance.append(highs[i])
                
                if all(lows[i] <= lows[i-j] for j in range(1, strength+1)) and \
                   all(lows[i] <= lows[i+j] for j in range(1, strength+1)):
                    support.append(lows[i])
            
            resistance = sorted(set(resistance), reverse=True)[:3] if resistance else []
            support = sorted(set(support))[:3] if support else []
            
            return support, resistance
        except:
            return [], []
    
    def calculate_fibonacci(self, df):
        try:
            recent_low = df['Low'].min()
            recent_high = df['High'].max()
            diff = recent_high - recent_low
            
            return {
                '23.6': recent_low + diff * 0.236,
                '38.2': recent_low + diff * 0.382,
                '50': recent_low + diff * 0.5,
                '61.8': recent_low + diff * 0.618,
                '78.6': recent_low + diff * 0.786,
                '100': recent_high
            }
        except:
            return {}
    
    def generate_signals(self, current_price, patterns, support, resistance, fib, sma, trend):
        signals = []
        if not patterns:
            return signals
        
        for p in patterns:
            direction = p.get('direction', 'NEUTRAL')
            if direction == 'NEUTRAL':
                continue
            
            near_support = any(abs(current_price - s) / current_price < self.confluence_tolerance for s in support)
            near_resistance = any(abs(current_price - r) / current_price < self.confluence_tolerance for r in resistance)
            near_fib = any(abs(current_price - fib[key]) / current_price < self.confluence_tolerance 
                          for key in ['50', '61.8'] if fib.get(key))
            
            is_bullish = direction == 'BULLISH'
            is_bearish = direction == 'BEARISH'
            
            if self.trend_filter:
                if is_bullish and trend == 'BEARISH':
                    continue
                if is_bearish and trend == 'BULLISH':
                    continue
            
            if is_bullish and (near_support or near_fib):
                sl = support[0] if support else current_price * 0.99
                tp = resistance[0] if resistance else current_price * 1.01
                risk = current_price - sl
                reward = tp - current_price
                if risk > 0 and reward > 0 and reward / risk >= self.min_risk_reward:
                    signals.append({
                        'action': 'BUY',
                        'entry': current_price,
                        'stop_loss': sl,
                        'take_profit': tp,
                        'risk_reward': round(reward / risk, 2),
                        'pattern': p.get('type', 'UNKNOWN'),
                        'strength': p.get('strength', 'MEDIUM'),
                        'rule': self._get_rule_for_pattern(p.get('type', ''))
                    })
            
            if is_bearish and (near_resistance or near_fib):
                sl = resistance[0] if resistance else current_price * 1.01
                tp = support[0] if support else current_price * 0.99
                risk = sl - current_price
                reward = current_price - tp
                if risk > 0 and reward > 0 and reward / risk >= self.min_risk_reward:
                    signals.append({
                        'action': 'SELL',
                        'entry': current_price,
                        'stop_loss': sl,
                        'take_profit': tp,
                        'risk_reward': round(reward / risk, 2),
                        'pattern': p.get('type', 'UNKNOWN'),
                        'strength': p.get('strength', 'MEDIUM'),
                        'rule': self._get_rule_for_pattern(p.get('type', ''))
                    })
        
        return signals
    
    def _get_rule_for_pattern(self, pattern_type):
        rule_map = {
            'BULLISH_PIN_BAR': 'Pin Bar Reversal',
            'BEARISH_PIN_BAR': 'Pin Bar Reversal',
            'BULLISH_ENGULFING': 'Engulfing Trend Continuation',
            'BEARISH_ENGULFING': 'Engulfing Trend Continuation',
            'DOUBLE_BOTTOM': 'Double Bottom Reversal',
            'DOUBLE_TOP': 'Double Top Reversal',
            'DRAGONFLY_DOJI': 'Doji Reversal',
            'GRAVESTONE_DOJI': 'Doji Reversal',
        }
        return rule_map.get(pattern_type, 'Price Action Strategy')
    
    def prepare_chart_data(self, df, support, resistance, fib, patterns):
        try:
            candles = []
            for idx, row in df.tail(80).iterrows():
                candles.append({
                    'time': row['time'].isoformat(),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close'])
                })
            
            return {
                'candles': candles,
                'levels': {
                    'support': [float(s) for s in support],
                    'resistance': [float(r) for r in resistance],
                    'fibonacci': {k: float(v) for k, v in fib.items()}
                }
            }
        except:
            return {'candles': [], 'levels': {}}