"""
Mmeli_FX - Complete Trading Platform (Public Data Only)
Fast Loading with Caching
"""

from flask import Flask, render_template, jsonify, request
from broker_api import BrokerAPI
from analysis import TradingAnalyzer
from patterns import CandlePatternDetector, ChartPatternDetector, SMCDetector
from rules_manager import RulesManager
from signal_history import signal_history
import logging
import time
from datetime import datetime
from config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize Broker
broker = BrokerAPI()
logger.info("🔌 Connecting to data source...")
if broker.connect():
    logger.info(f"✅ Connected to {broker.get_data_source()}")
else:
    logger.error("❌ Failed to connect")

analyzer = TradingAnalyzer()
candle_detector = CandlePatternDetector()
chart_detector = ChartPatternDetector()
smc_detector = SMCDetector()
rules_manager = RulesManager()

# Cache for analysis results
analysis_cache = {}
analysis_cache_time = {}
signal_cache = {}
signal_cache_time = {}
CACHE_DURATION = 60  # Cache for 60 seconds

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/signals')
def signals_page():
    return render_template('signals.html')

@app.route('/journal')
def journal_page():
    return render_template('journal.html')

@app.route('/rules')
def rules_page():
    return render_template('rules.html')

@app.route('/history')
def history_page():
    return render_template('history.html')

@app.route('/api/analysis/<symbol>')
def get_analysis(symbol):
    """Complete analysis for a symbol - WITH CACHING"""
    try:
        tf = request.args.get('tf', DEFAULT_TRADE_TF)
        if tf not in AVAILABLE_TFS:
            tf = DEFAULT_TRADE_TF
        
        # Check cache
        cache_key = f"{symbol}_{tf}"
        if cache_key in analysis_cache:
            data, timestamp = analysis_cache[cache_key]
            if (datetime.now() - timestamp).seconds < CACHE_DURATION:
                return jsonify({
                    'status': 'success',
                    'data': data,
                    'timestamp': timestamp.isoformat(),
                    'data_source': broker.get_data_source(),
                    'cached': True
                })
        
        # Fetch data
        df = broker.get_historical_data(symbol, tf, 100)
        if df is None or len(df) == 0:
            return jsonify({'status': 'error', 'message': 'No data'}), 404
        
        htf_df = broker.get_historical_data(symbol, DEFAULT_HIGH_TF, 50)
        bid, ask = broker.get_current_price(symbol)
        current_price = ask if ask else df[-1]['close']
        
        result = analyzer.analyze_symbol(htf_df if htf_df is not None else df, df, current_price)
        
        if result:
            # Store in cache
            analysis_cache[cache_key] = (result, datetime.now())
            
            return jsonify({
                'status': 'success',
                'data': result,
                'timestamp': datetime.now().isoformat(),
                'data_source': broker.get_data_source(),
                'cached': False
            })
        
        return jsonify({'status': 'error', 'message': 'Analysis failed'}), 500
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/patterns/<symbol>')
def get_patterns(symbol):
    """Get all detected patterns"""
    try:
        tf = request.args.get('tf', DEFAULT_TRADE_TF)
        if tf not in AVAILABLE_TFS:
            tf = DEFAULT_TRADE_TF
        
        df = broker.get_historical_data(symbol, tf, 100)
        
        if df is None or len(df) == 0:
            return jsonify({'status': 'error', 'message': 'No data'}), 404
        
        candle_patterns = candle_detector.detect_all_patterns(df)
        chart_patterns = chart_detector.detect_all_patterns(df)
        smc_data = smc_detector.detect_all(df)
        
        return jsonify({
            'status': 'success',
            'data': {
                'candle_patterns': candle_patterns,
                'chart_patterns': chart_patterns,
                'smc': smc_data,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Pattern error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/rules')
def get_rules():
    return jsonify({
        'status': 'success',
        'rules': rules_manager.get_rules()
    })

@app.route('/api/rules/create', methods=['POST'])
def create_rule():
    try:
        data = request.json
        rule = rules_manager.create_rule(data)
        if rule:
            return jsonify({'status': 'success', 'rule': rule})
        return jsonify({'status': 'error', 'message': 'Failed to create'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/rules/update/<int:rule_id>', methods=['PUT'])
def update_rule(rule_id):
    try:
        data = request.json
        rule = rules_manager.update_rule(rule_id, data)
        if rule:
            return jsonify({'status': 'success', 'rule': rule})
        return jsonify({'status': 'error', 'message': 'Rule not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/rules/delete/<int:rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    try:
        if rules_manager.delete_rule(rule_id):
            return jsonify({'status': 'success'})
        return jsonify({'status': 'error', 'message': 'Rule not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/rules/toggle/<int:rule_id>', methods=['POST'])
def toggle_rule(rule_id):
    try:
        rule = rules_manager.toggle_rule(rule_id)
        if rule:
            return jsonify({'status': 'success', 'rule': rule})
        return jsonify({'status': 'error', 'message': 'Rule not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/signals')
def get_signals():
    """Get active signals - WITH CACHING"""
    try:
        tf = request.args.get('tf', DEFAULT_TRADE_TF)
        if tf not in AVAILABLE_TFS:
            tf = DEFAULT_TRADE_TF
        
        # Check cache
        cache_key = f"signals_{tf}"
        if cache_key in signal_cache:
            signals, timestamp = signal_cache[cache_key]
            if (datetime.now() - timestamp).seconds < CACHE_DURATION:
                return jsonify({
                    'status': 'success',
                    'signals': signals,
                    'timestamp': timestamp.isoformat(),
                    'data_source': broker.get_data_source(),
                    'cached': True
                })
        
        all_signals = []
        
        # Analyze symbols for speed
        symbols_to_analyze = SYMBOLS[:10]
        
        for symbol in symbols_to_analyze:
            try:
                df = broker.get_historical_data(symbol, tf, 60)
                if df is not None and len(df) > 0:
                    bid, ask = broker.get_current_price(symbol)
                    current_price = ask if ask else df[-1]['close']
                    htf_df = broker.get_historical_data(symbol, DEFAULT_HIGH_TF, 30)
                    result = analyzer.analyze_symbol(htf_df if htf_df is not None else df, df, current_price)
                    
                    if result and result.get('signals'):
                        for signal in result['signals']:
                            signal['symbol'] = symbol
                            signal['timeframe'] = tf
                            all_signals.append(signal)
            except Exception as e:
                continue
        
        # Sort by risk/reward
        all_signals.sort(key=lambda x: x.get('risk_reward', 0), reverse=True)
        
        # Save signals to history
        for signal in all_signals:
            signal_history.add_signal(signal)
        
        # Store in cache
        signal_cache[cache_key] = (all_signals, datetime.now())
        
        return jsonify({
            'status': 'success',
            'signals': all_signals,
            'timestamp': datetime.now().isoformat(),
            'data_source': broker.get_data_source(),
            'cached': False
        })
        
    except Exception as e:
        logger.error(f"Signals error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/status')
def get_status():
    return jsonify({
        'status': 'running' if broker.connected else 'disconnected',
        'connected': broker.connected,
        'data_source': broker.get_data_source(),
        'timestamp': datetime.now().isoformat(),
        'cache_size': len(analysis_cache) + len(signal_cache)
    })

@app.route('/api/signal_history')
def get_signal_history():
    """Get signal history"""
    try:
        limit = request.args.get('limit', 100, type=int)
        signals = signal_history.get_recent(limit)
        stats = signal_history.get_statistics()
        
        return jsonify({
            'status': 'success',
            'signals': signals,
            'statistics': stats,
            'total': len(signals)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/signal_history/clear', methods=['POST'])
def clear_signal_history():
    try:
        signal_history.clear_history()
        return jsonify({'status': 'success', 'message': 'Signal history cleared'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/journal')
def get_journal():
    """Get trading journal with advanced stats"""
    try:
        signals = signal_history.get_recent(200)
        stats = signal_history.get_statistics()
        
        total = len(signals)
        win_count = sum(1 for s in signals if s.get('status') == 'HIT_TP')
        loss_count = sum(1 for s in signals if s.get('status') == 'HIT_SL')
        pending = sum(1 for s in signals if s.get('status') == 'PENDING')
        
        # Group by symbol
        symbol_stats = {}
        for s in signals:
            sym = s.get('symbol', 'Unknown')
            if sym not in symbol_stats:
                symbol_stats[sym] = {'total': 0, 'wins': 0, 'losses': 0}
            symbol_stats[sym]['total'] += 1
            if s.get('status') == 'HIT_TP':
                symbol_stats[sym]['wins'] += 1
            elif s.get('status') == 'HIT_SL':
                symbol_stats[sym]['losses'] += 1
        
        # Group by pattern
        pattern_stats = {}
        for s in signals:
            pat = s.get('pattern', 'Unknown')
            if pat not in pattern_stats:
                pattern_stats[pat] = {'total': 0, 'wins': 0, 'losses': 0}
            pattern_stats[pat]['total'] += 1
            if s.get('status') == 'HIT_TP':
                pattern_stats[pat]['wins'] += 1
            elif s.get('status') == 'HIT_SL':
                pattern_stats[pat]['losses'] += 1
        
        return jsonify({
            'status': 'success',
            'signals': signals,
            'statistics': stats,
            'total': total,
            'win_count': win_count,
            'loss_count': loss_count,
            'pending': pending,
            'win_rate': round((win_count / (win_count + loss_count) * 100) if (win_count + loss_count) > 0 else 0, 1),
            'symbol_stats': symbol_stats,
            'pattern_stats': pattern_stats
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/switch_source', methods=['POST'])
def switch_source():
    try:
        data = request.json
        source = data.get('source')
        if broker.switch_source(source):
            global analysis_cache, signal_cache
            analysis_cache = {}
            signal_cache = {}
            return jsonify({'status': 'success', 'source': source})
        return jsonify({'status': 'error', 'message': 'Invalid source'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/data_source')
def get_data_source():
    return jsonify({
        'status': 'success',
        'source': broker.get_data_source()
    })

if __name__ == '__main__':
    logger.info("="*60)
    logger.info("🚀 Starting Mmeli_FX Trading Platform")
    logger.info(f"📊 Monitoring {len(SYMBOLS)} symbols")
    logger.info(f"📡 Data Source: {broker.get_data_source() if broker.connected else 'Disconnected'}")
    logger.info("🌐 Open http://127.0.0.1:5000")
    logger.info("⚡ Caching enabled for faster loading")
    logger.info("📜 Signal history tracking enabled")
    logger.info("="*60)
    app.run(host='0.0.0.0', port=5000, debug=False)