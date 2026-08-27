"""
Mmeli_FX - Complete Trading Platform Configuration
"""

import os
from datetime import datetime, time

# ============================================
# SYMBOLS TO MONITOR
# ============================================
SYMBOLS = {
    'Forex': ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF'],
    'Metals': ['XAUUSD', 'XAGUSD'],
    'Indices': ['US30', 'NAS100', 'SPX500', 'UK100', 'GER30'],
    'Crypto': ['BTCUSD', 'ETHUSD', 'SOLUSD', 'ADAUSD']
}

ALL_SYMBOLS = []
for category, symbols in SYMBOLS.items():
    ALL_SYMBOLS.extend(symbols)

# ============================================
# TIMEFRAME SETTINGS
# ============================================
AVAILABLE_TFS = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']

# Timeframe hierarchy for structure analysis
TF_HIERARCHY = {
    '1d': 'Major Trend',
    '4h': 'Trend Confirmation',
    '1h': 'Structure',
    '15m': 'Primary Entry',
    '5m': 'Sculpting',
    '1m': 'Scalping'
}

DEFAULT_HIGH_TF = '4h'        # For trend lines and major structure
DEFAULT_MID_TF = '1h'         # For support/resistance
DEFAULT_LOW_TF = '15m'        # For entries (Primary trading timeframe)
DEFAULT_SCULPT_TF = '5m'      # For scalping/sculpting
DEFAULT_SCALP_TF = '1m'       # For ultra-scalping

# ============================================
# TRADING SESSIONS
# ============================================
SESSIONS = {
    'Asia': {
        'start': time(0, 0),
        'end': time(9, 0),
        'timezone': 'Asia/Tokyo'
    },
    'London': {
        'start': time(8, 0),
        'end': time(17, 0),
        'timezone': 'Europe/London'
    },
    'NewYork': {
        'start': time(13, 0),
        'end': time(22, 0),
        'timezone': 'America/New_York'
    }
}

# ============================================
# PATTERN DETECTION RULES
# ============================================
PATTERN_RULES = {
    # Reversal Patterns
    'MORNING_STAR': {'min_body_ratio': 0.5, 'max_middle_body': 0.3},
    'EVENING_STAR': {'min_body_ratio': 0.5, 'max_middle_body': 0.3},
    'MORNING_DOJI_STAR': {'max_middle_body': 0.05, 'gap_required': True},
    'EVENING_DOJI_STAR': {'max_middle_body': 0.05, 'gap_required': True},
    'BULLISH_ENGULFING': {'min_engulf_ratio': 1.2},
    'BEARISH_ENGULFING': {'min_engulf_ratio': 1.2},
    'BULLISH_HARAMI': {'max_inner_body': 0.5},
    'BEARISH_HARAMI': {'max_inner_body': 0.5},
    'HAMMER': {'wick_to_body_ratio': 2.0, 'max_body_ratio': 0.3},
    'SHOOTING_STAR': {'wick_to_body_ratio': 2.0, 'max_body_ratio': 0.3},
    'HANGING_MAN': {'wick_to_body_ratio': 2.0, 'max_body_ratio': 0.3},
    'PIERCING_LINE': {'min_close_ratio': 0.5},
    'DARK_CLOUD_COVER': {'min_close_ratio': 0.5},
    'THREE_WHITE_SOLDIERS': {'min_candle_ratio': 0.3},
    'THREE_BLACK_CROWS': {'min_candle_ratio': 0.3},
    'TWEEZER_BOTTOM': {'max_price_diff': 0.0003},
    'TWEEZER_TOP': {'max_price_diff': 0.0003},
    'DOJI': {'max_body_ratio': 0.05},
    'DRAGONFLY_DOJI': {'max_body_ratio': 0.05, 'wick_to_body_ratio': 2.0},
    'GRAVESTONE_DOJI': {'max_body_ratio': 0.05, 'wick_to_body_ratio': 2.0},
    'SPINNING_TOP': {'max_body_ratio': 0.3, 'min_wick_ratio': 0.5},
    'MARUBOZU': {'max_wick_ratio': 0.1},
    
    # Chart Patterns
    'DOUBLE_BOTTOM': {'max_price_diff': 0.002, 'min_pullback_ratio': 0.3},
    'DOUBLE_TOP': {'max_price_diff': 0.002, 'min_pullback_ratio': 0.3},
    'HEAD_SHOULDERS': {'head_to_shoulder_ratio': 1.1},
    'INVERTED_HEAD_SHOULDERS': {'head_to_shoulder_ratio': 1.1},
    'BULLISH_CHANNEL': {'min_touches': 2},
    'BEARISH_CHANNEL': {'min_touches': 2},
    'BULL_FLAG': {'min_pole_ratio': 1.5, 'max_flag_ratio': 0.5},
    'BEAR_FLAG': {'min_pole_ratio': 1.5, 'max_flag_ratio': 0.5},
    'BULLISH_TRIANGLE': {'min_touches': 2},
    'BEARISH_TRIANGLE': {'min_touches': 2},
    'BULLISH_WEDGE': {'min_touches': 2},
    'BEARISH_WEDGE': {'min_touches': 2},
    'BULLISH_RECTANGLE': {'min_touches': 2},
    'BEARISH_RECTANGLE': {'min_touches': 2},
}

# ============================================
# SMC / ORDER BLOCK SETTINGS
# ============================================
ORDER_BLOCK_SETTINGS = {
    'min_candle_strength': 1.5,      # Minimum range for order block candle
    'mitigation_tolerance': 0.002,   # 0.2% tolerance for order block zones
    'max_order_block_age': 50,       # Maximum candles before order block expires
    'fvg_min_gap': 0.001,            # Minimum gap for FVG detection
    'liquidity_sweep_tolerance': 0.001,  # 0.1% tolerance for liquidity sweeps
}

# ============================================
# SIGNAL SETTINGS
# ============================================
SIGNAL_SETTINGS = {
    'min_risk_reward': 2.0,
    'max_risk_per_trade': 0.02,      # 2% of account
    'min_pattern_strength': 'MEDIUM',
    'trend_filter': True,
    'confluence_tolerance': 0.005,   # 0.5% price tolerance
    'signal_cooling': 10,            # Minutes before same symbol signal repeats
}

# ============================================
# WHATSAPP SETTINGS
# ============================================
WHATSAPP_ENABLED = True
WHATSAPP_PHONE = '+27645471297'      # YOUR NUMBER
WHATSAPP_RECIPIENTS = ['+27645471297']
WHATSAPP_SCHEDULE = {
    'morning': '08:00',
    'evening': '17:00'
}

# ============================================
# DISPLAY SETTINGS
# ============================================
DISPLAY_SETTINGS = {
    'theme': 'dark',
    'show_trend_lines': True,
    'show_support_resistance': True,
    'show_fibonacci': True,
    'show_sma': True,
    'show_order_blocks': True,
    'show_fvg': True,
    'show_liquidity_zones': True,
    'show_sessions': True,
    'show_psychological_levels': True,
    'show_channel_lines': True,
    'show_fan_trends': True,
    'chart_height': 600,
}

# ============================================
# PATH SETTINGS
# ============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
PATTERNS_DIR = os.path.join(BASE_DIR, 'patterns')

# Create directories if they don't exist
for directory in [DATA_DIR, STATIC_DIR, TEMPLATES_DIR, PATTERNS_DIR]:
    os.makedirs(directory, exist_ok=True)