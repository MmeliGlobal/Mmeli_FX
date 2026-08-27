"""
WhatsApp Integration - Twilio API (No WhatsApp Web needed!)
"""

import logging
import requests
from datetime import datetime
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER, WHATSAPP_PHONE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppTwilio:
    def __init__(self):
        self.account_sid = TWILIO_ACCOUNT_SID
        self.auth_token = TWILIO_AUTH_TOKEN
        self.from_number = TWILIO_WHATSAPP_NUMBER
        self.to_number = WHATSAPP_PHONE
        
        self.enabled = (
            self.account_sid and 
            self.auth_token and 
            self.from_number and 
            self.to_number and
            self.account_sid != ''
        )
        
        if self.enabled:
            logger.info(f"📱 Twilio WhatsApp enabled for {self.to_number}")
        else:
            logger.info("📱 Twilio not configured")
    
    def send_signal(self, signal):
        if not self.enabled:
            return False
        
        try:
            message = self._format_signal_message(signal)
            
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
            auth = (self.account_sid, self.auth_token)
            
            data = {
                'From': self.from_number,
                'To': self.to_number,
                'Body': message
            }
            
            response = requests.post(url, auth=auth, data=data)
            
            if response.status_code == 201:
                logger.info(f"✅ Signal sent to {self.to_number}")
                return True
            else:
                logger.error(f"❌ Twilio error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to send: {e}")
            return False
    
    def _format_signal_message(self, signal):
        action = signal.get('action', 'UNKNOWN')
        symbol = signal.get('symbol', 'UNKNOWN')
        price = signal.get('entry', 0)
        sl = signal.get('stop_loss', 0)
        tp = signal.get('take_profit', 0)
        rr = signal.get('risk_reward', 0)
        pattern = signal.get('pattern', 'UNKNOWN')
        strength = signal.get('strength', 'MEDIUM')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        emoji = '📈' if action == 'BUY' else '📉'
        color = '🟢' if action == 'BUY' else '🔴'
        
        return f"""
╔═══════════════════════════════════╗
║     📡 Mmeli_FX SIGNAL           ║
╠═══════════════════════════════════╣
║  {emoji} {color} {action} {symbol}      ║
║  📊 Pattern: {pattern} ({strength})    ║
║  💰 Entry: {price:.5f}                 ║
║  🛑 Stop: {sl:.5f}                     ║
║  🎯 Target: {tp:.5f}                   ║
║  📈 RR: 1:{rr}                         ║
║  ⏰ {timestamp}                        ║
╚═══════════════════════════════════╝
"""