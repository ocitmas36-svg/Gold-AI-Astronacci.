import requests
from datetime import datetime
import pytz
import os

# MENGAMBIL DATA DARI GITHUB SECRETS (AMAN)
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_analysis(p, area, volatility, signal):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = (
        f"Analisa Emas Rosit. Harga ${p:.2f}, Area {area:.1f}/100, Sinyal {signal}. "
        f"Berikan saran strategi 2 arah (Buy/Sell) yang tegas untuk Rosit dalam 2 kalimat saja."
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return f"Rosit, sinyal saat ini adalah {signal}. Perhatikan manajemen risiko di area {area:.1f}."

def main():
    try:
        url_data = "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=PAXG&tsyms=USD"
        res = requests.get(url_data).json()
        data = res['RAW']['PAXG']['USD']
        
        p = data['PRICE']
        low = data['LOW24HOUR']
        high = data['HIGH24HOUR']
        change = data['CHANGEPCT24HOUR']
        
        volatility = ((high - low) / low) * 100
        area = ((p - low) / (high - low)) * 100 if (high - low) != 0 else 50
        
        # LOGIKA STRATEGI 2 ARAH (Dinamis)
        if area < 35:
            signal = "🟢 SIGNAL: BUY (LONG)"
            tp = p * 1.010 # Target naik 1%
            sl = p * 0.995 # Batas rugi 0.5%
        elif area > 75:
            signal = "🔴 SIGNAL: SELL (SHORT)"
            tp = p * 0.990 # Target turun 1%
            sl = p * 1.005 # Batas rugi 0.5% (di atas harga sekarang)
        else:
            signal = "🟡 SIGNAL: WAIT & SEE"
            tp = p * 1.005
            sl = p * 0.995

        ai_msg = get_ai_analysis(p, area, volatility, signal)
        tz = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz).strftime('%H:%M:%S')

        msg = (
            f"🔱 **OMNISCIENT BI-DIRECTIONAL v80** 🔱\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🕒 **WAKTU** : {waktu} WIB\n"
            f"💵 **PRICE** : `${p:.2f}` ({change:.2f}%)\n"
            f"📊 **AREA** : {area:.1f}/100\n"
            f"📡 **STRATEGY**: **{signal}**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🧠 **AI ADVISOR:**\n_{ai_msg.strip()}_\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎯 **TARGET PROFIT**: `${tp:.2f}`\n"
            f"🛡️ **STOP LOSS**: `${sl:.2f}`\n"
            f"💡 **MOMENTUM**: {'TINGGI' if volatility > 1.5 else 'STABIL'}\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
