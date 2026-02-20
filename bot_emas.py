import requests
from datetime import datetime
import pytz
import os

TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_analysis(p, area, volatility, signal):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = (
        f"Analisa Emas Rosit. Harga ${p:.2f}, Area {area:.1f}/100, Sinyal {signal}, Volatilitas {volatility:.2f}%. "
        f"Berikan saran apakah harus Ikut Arus (Trend) atau Lawan Arus (Reversal). Singkat & tegas untuk Rosit."
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return f"Rosit, harga ${p:.2f}. Strategi: {signal}. Jaga manajemen risiko!"

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
        
        # --- LOGIKA ADAPTIF v90 (ILMU TREND + REVERSAL) ---
        if volatility > 2.0: # Jika market sangat liar (BREAKOUT MODE)
            if area > 85:
                signal = "🚀 STRONG BUY (FOLLOW TREND)"
                tp, sl = p * 1.020, p * 0.990 # Target jauh karena kuat
            elif area < 15:
                signal = "📉 STRONG SELL (FOLLOW TREND)"
                tp, sl = p * 0.980, p * 1.010
            else:
                signal = "🟡 MOMENTUM UNCERTAIN"
                tp, sl = p * 1.005, p * 0.995
        else: # Market Normal (REVERSAL MODE)
            if area > 75:
                signal = "🔴 SELL (SHORT)"
                tp, sl = p * 0.990, p * 1.005
            elif area < 25:
                signal = "🟢 BUY (LONG)"
                tp, sl = p * 1.010, p * 0.995
            else:
                signal = "🟡 STANDBY"
                tp, sl = p * 1.005, p * 0.995

        ai_msg = get_ai_analysis(p, area, volatility, signal)
        tz = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz).strftime('%H:%M:%S')

        msg = (
            f"🔱 **OMNISCIENT ADAPTIVE v90** 🔱\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🕒 **WAKTU** : {waktu} WIB\n"
            f"💵 **PRICE** : `${p:.2f}` ({change:.2f}%)\n"
            f"📊 **AREA** : {area:.1f}/100\n"
            f"📡 **STRATEGY**: **{signal}**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🧠 **AI ADVISOR:**\n_{ai_msg.strip()}_\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎯 **TP**: `${tp:.2f}`\n"
            f"🛡️ **SL**: `${sl:.2f}`\n"
            f"💡 **VOLATILITAS**: {volatility:.2f}% ({'EKSTREM' if volatility > 2.0 else 'NORMAL'})\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
