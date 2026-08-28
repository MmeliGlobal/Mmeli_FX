"""
Mmeli_FX - Trading Configuration
Using Yahoo Finance (Works everywhere!)
"""

# ============================================
# DATA SOURCE SETTINGS
# ============================================
DATA_SOURCE = 'yahoo'  # Yahoo Finance - works everywhere!

# ============================================
# SYMBOLS TO MONITOR
# ============================================
SYMBOLS = [
    'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 
    'USDCAD', 'NZDUSD', 'USDCHF',
    'XAUUSD', 'XAGUSD'
]

# ============================================
# TIMEFRAME SETTINGS
# ============================================
DEFAULT_HIGH_TF = '1h'
DEFAULT_TRADE_TF = '15m'

AVAILABLE_TFS = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']

# ============================================
# CACHE SETTINGS
# ============================================
CACHE_DURATION = 30
MAX_CACHE_SIZE = 100

# ============================================
# TRADING RULES
# ============================================
DEFAULT_RULES = {
    'pin_bar_ratio': 2.0,
    'engulfing_min_ratio': 1.2,
    'doji_body_threshold': 0.0003,
    'confluence_tolerance': 0.005,
    'sr_lookback': 50,
    'swing_strength': 5,
    'min_risk_reward': 2.0,
    'trend_filter': True
}