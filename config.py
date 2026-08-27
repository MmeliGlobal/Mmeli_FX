"""
Mmeli_FX - Trading Configuration
Public Data Only - No credentials needed!
"""

# ============================================
# DATA SOURCE SETTINGS
# ============================================
DATA_SOURCE = 'deriv_public'

# ============================================
# ALL DERIV FOREX PAIRS
# ============================================
SYMBOLS = [
    # Major Pairs
    'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 
    'USDCAD', 'NZDUSD', 'USDCHF',
    
    # Minor Pairs
    'EURGBP', 'EURJPY', 'EURCHF', 'EURAUD', 'EURCAD', 'EURNZD',
    'GBPJPY', 'GBPAUD', 'GBPCAD', 'GBPNZD', 'GBPCHF',
    'AUDJPY', 'AUDCAD', 'AUDNZD', 'AUDCHF',
    'NZDJPY', 'NZDCAD', 'NZDCHF',
    'CADJPY', 'CHFJPY',
    
    # Exotics
    'USDTRY', 'USDZAR', 'USDMXN', 'USDSGD', 'USDHKD',
    'EURTRY', 'EURZAR', 'EURMXN',
    'GBPTRY', 'GBPZAR',
    'AUDTRY', 'NZDTRY',
    
    # Metals
    'XAUUSD', 'XAGUSD'
]

# ============================================
# TIMEFRAME SETTINGS
# ============================================
DEFAULT_HIGH_TF = '1h'
DEFAULT_TRADE_TF = '15m'

AVAILABLE_TFS = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']

# ============================================
# CACHE SETTINGS (For Speed)
# ============================================
CACHE_DURATION = 30  # Cache data for 30 seconds
MAX_CACHE_SIZE = 100  # Max items in cache

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

# ============================================
# WHATSAPP SETTINGS
# ============================================
WHATSAPP_ENABLED = False
WHATSAPP_PHONE = '+27645471297'