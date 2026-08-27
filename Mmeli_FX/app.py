"""
Mmeli_FX - Complete Trading Platform
"""

from flask import Flask, render_template, jsonify, request
from broker_api import BrokerAPI
from analysis import TradingAnalyzer
from patterns import CandlePatternDetector, ChartPatternDetector, SMCDetector
from rules_manager import RulesManager
from whatsapp_sender import WhatsAppSender
import logging
import time
from datetime import datetime
from config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize components
broker = BrokerAPI()
logger.info("🔌 Connecting to Yahoo Finance...")
if broker.connect():
    logger.info("✅ Connected to Yahoo Finance!")

analyzer = TradingAnalyzer()
candle_detector = CandlePatternDetector()
chart_detector = ChartPatternDetector()
smc_detector = SMCDetector()
rules_manager = RulesManager()
whatsapp = WhatsAppSender()

# Cache
analysis_cache = {}
signal_history = []
last_update = None

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/analysis/<symbol>')
def get_analysis(symbol):
    """Complete analysis for a symbol"""
    try:
        tf = request.args.get('tf', DEFAULT_LOW_TF)
        if tf not in AVAILABLE_TFS:
            tf = DEFAULT_LOW_TF
        
        # Fetch data
        df = broker.get_historical_data(symbol, tf, 100)
        if df is None or len(df) == 0:
            return jsonify({'status': 'error', 'message': 'No data'}), 404
        
        # Get higher timeframe data
        htf_df = broker.get_historical_data(symbol, DEFAULT_HIGH_TF, 50)
        
        # Get current price
        bid, ask = broker.get_current_price(symbol)
        current_price = ask if ask else df['Close'].iloc[-1]
        
        # Run analysis
        result = analyzer.analyze_symbol(htf_df if htf_df is not None else df, df, current_price)
        
        if result:
            return jsonify({
                'status': 'success',
                'data': result,
                'timestamp': datetime.now().isoformat()
            })
        
        return jsonify({'status': 'error', 'message': 'Analysis failed'}), 500
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/patterns/<symbol>')
def get_patterns(symbol):
    """Get all detected patterns for a symbol"""
    try:
        tf = request.args.get('tf', DEFAULT_LOW_TF)
        df = broker.get_historical_data(symbol, tf, 100)
        
        if df is None or len(df) == 0:
            return jsonify({'status': 'error', 'message': 'No data'}), 404
        
        # Detect all patterns
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
    """Get active signals"""
    try:
        tf = request.args.get('tf', DEFAULT_LOW_TF)
        all_signals = []
        
        for symbol in ALL_SYMBOLS[:5]:
            try:
                df = broker.get_historical_data(symbol, tf, 80)
                if df is not None and len(df) > 0:
                    bid, ask = broker.get_current_price(symbol)
                    current_price = ask if ask else df['Close'].iloc[-1]
                    htf_df = broker.get_historical_data(symbol, DEFAULT_HIGH_TF, 50)
                    result = analyzer.analyze_symbol(htf_df if htf_df is not None else df, df, current_price)
                    
                    if result and result.get('signals'):
                        for signal in result['signals']:
                            signal['symbol'] = symbol
                            all_signals.append(signal)
            except:
                pass
        
        all_signals.sort(key=lambda x: x.get('risk_reward', 0), reverse=True)
        
        return jsonify({
            'status': 'success',
            'signals': all_signals,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/status')
def get_status():
    return jsonify({
        'status': 'running',
        'connected': broker.connected,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/send_signal', methods=['POST'])
def send_signal_whatsapp():
    try:
        data = request.json
        if whatsapp.send_signal(data):
            return jsonify({'status': 'success', 'message': 'Signal sent!'})
        return jsonify({'status': 'error', 'message': 'Failed to send'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    logger.info("="*60)
    logger.info("🚀 Starting Mmeli_FX Trading Platform")
    logger.info(f"📊 Monitoring {len(ALL_SYMBOLS)} symbols")
    logger.info("🌐 Open http://127.0.0.1:5000")
    logger.info("⏰ WhatsApp: +27645471297")
    logger.info("="*60)
    app.run(host='0.0.0.0', port=5000, debug=False)