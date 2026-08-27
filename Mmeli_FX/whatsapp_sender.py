"""
WhatsApp Integration - Send signals and reports
"""

import logging
import time
from datetime import datetime
from config import WHATSAPP_ENABLED, WHATSAPP_PHONE, WHATSAPP_RECIPIENTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import pywhatkit
try:
    import pywhatkit
    PYWHATKIT_AVAILABLE = True
except ImportError:
    PYWHATKIT_AVAILABLE = False
    logger.warning("⚠️ pywhatkit not installed. Install: pip install pywhatkit")

class WhatsAppSender:
    def __init__(self):
        self.enabled = WHATSAPP_ENABLED and PYWHATKIT_AVAILABLE
        self.phone = WHATSAPP_PHONE
        self.recipients = WHATSAPP_RECIPIENTS
        
        if not PYWHATKIT_AVAILABLE:
            logger.info("💡 To enable WhatsApp: pip install pywhatkit")
        if not self.enabled:
            logger.info("📱 WhatsApp integration disabled")
    
    def send_signal(self, signal):
        """Send a trading signal via WhatsApp"""
        if not self.enabled:
            return False
        
        try:
            message = self._format_signal_message(signal)
            
            for recipient in self.recipients:
                self._send_message(recipient, message)
            
            logger.info(f"✅ Signal sent to {len(self.recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send: {e}")
            return False
    
    def send_report(self, stats):
        """Send daily/weekly report"""
        if not self.enabled:
            return False
        
        try:
            message = self._format_report_message(stats)
            
            for recipient in self.recipients:
                self._send_message(recipient, message)
            
            logger.info(f"✅ Report sent to {len(self.recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send report: {e}")
            return False
    
    def _send_message(self, phone, message):
        """Send message to a single recipient"""
        try:
            now = datetime.now()
            hour = now.hour
            minute = now.minute + 2
            
            if minute >= 60:
                minute -= 60
                hour += 1
            if hour >= 24:
                hour = 0
            
            pywhatkit.sendwhatmsg(
                phone,
                message,
                hour,
                minute,
                tab_close=True,
                close_time=10
            )
            
            time.sleep(5)
            
        except Exception as e:
            logger.error(f"Error sending to {phone}: {e}")
    
    def _format_signal_message(self, signal):
        """Format signal as WhatsApp message"""
        action = signal.get('action', 'UNKNOWN')
        symbol = signal.get('symbol', 'UNKNOWN')
        price = signal.get('entry', 0)
        sl = signal.get('stop_loss', 0)
        tp = signal.get('take_profit', 0)
        rr = signal.get('risk_reward', 0)
        pattern = signal.get('pattern', 'UNKNOWN')
        strength = signal.get('strength', 'MEDIUM')
        rule = signal.get('rule', 'N/A')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        emoji = '📈' if action == 'BUY' else '📉'
        color = '🟢' if action == 'BUY' else '🔴'
        
        return f"""
╔═══════════════════════════════════════╗
║        📡 Mmeli_FX SIGNAL            ║
╠═══════════════════════════════════════╣
║  {emoji} {color} {action} {symbol}         ║
╠═══════════════════════════════════════╣
║  📊 Pattern: {pattern} ({strength})       ║
║  📋 Rule: {rule}                          ║
║  💰 Entry: {price:.5f}                    ║
║  🛑 Stop Loss: {sl:.5f}                  ║
║  🎯 Take Profit: {tp:.5f}                ║
║  📈 Risk:Reward: 1:{rr}                  ║
║  ⏰ {timestamp}                          ║
╠═══════════════════════════════════════╣
║  ⚠️ ONLY RISK WHAT YOU CAN AFFORD      ║
╚═══════════════════════════════════════╝
"""
    
    def _format_report_message(self, stats):
        """Format daily report"""
        return f"""
╔═══════════════════════════════════════╗
║     📊 Mmeli_FX DAILY REPORT         ║
╠═══════════════════════════════════════╣
║  📈 Total Signals: {stats.get('total', 0)}        ║
║  ✅ Win Rate: {stats.get('win_rate', 0)}%        ║
║  📊 Avg RR: {stats.get('avg_rr', 0)}             ║
║  💰 P&L: {stats.get('pnl', 0)}                   ║
║  🏆 Best Pattern: {stats.get('best_pattern', 'N/A')} ║
╠═══════════════════════════════════════╣
║  📅 {datetime.now().strftime('%Y-%m-%d')}        ║
╚═══════════════════════════════════════╝
"""

def test_whatsapp():
    """Test WhatsApp integration"""
    sender = WhatsAppSender()
    if sender.enabled:
        print(f"📱 Sending test to {WHATSAPP_PHONE}...")
        print("⚠️ Make sure WhatsApp Web is open in your browser!")
        
        test_signal = {
            'action': 'BUY',
            'symbol': 'EURUSD',
            'entry': 1.09500,
            'stop_loss': 1.09000,
            'take_profit': 1.10500,
            'risk_reward': 2.0,
            'pattern': 'PIN_BAR',
            'strength': 'HIGH',
            'rule': 'SMC Order Block'
        }
        
        sender.send_signal(test_signal)
    else:
        print("❌ WhatsApp not enabled. Check config.py")
        print("   WHATSAPP_ENABLED = True")
        print("   WHATSAPP_PHONE = '+27645471297'")
        print("   pip install pywhatkit")