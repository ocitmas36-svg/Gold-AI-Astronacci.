import requests
from datetime import datetime
import pytz
import os

# MENGAMBIL DATA DARI GITHUB SECRETS (AMAN)
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_analysis(p, area, volatility):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    v_status = "Liar" if volatility > 1.5 else "Tenang"
    prompt = (
        f"Analisa Emas untuk Rosit. Harga ${p:.2f}, Area {area:.1f}/100, Volatilitas {v_status}. "
        f"Berikan saran trading singkat 2 kalimat. Panggil nama Rosit."
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return f"Rosit, harga emas ${p:.2f}. Pantau area {area:.1f} untuk keputusan entry."

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
        
        # Adaptive SL & TP
        if volatility > 1.5:
            sl, tp, status = p * 0.992, p * 1.015, "⚠️ HIGH VOLATILITY"
        else:
            sl, tp, status = p * 0.996, p * 1.008, "⚖️ NORMAL MARKET"

        ai_msg = get_ai_analysis(p, area, volatility)
        tz = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz).strftime('%H:%M:%S')

        signal = "🟢 BUY MOMENTUM" if area < 35 else "🟡 STANDBY"
        if area > 70: signal = "🔴 OVERBOUGHT"

        msg = (
            f"🔱 **OMNISCIENT GOLD v70** 🔱\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🕒 **WAKTU** : {waktu} WIB\n"
            f"💵 **PRICE** : `${p:.2f}` ({change:.2f}%)\n"
            f"📊 **AREA** : {area:.1f}/100\n"
            f"📡 **SIGNAL**: **{signal}**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🧠 **AI ADVISOR:**\n_{ai_msg.strip()}_\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎯 **TP**: `${tp:.2f}`\n"
            f"🛡️ **SL**: `${sl:.2f}`\n"
            f"💡 **MODE**: {status}\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
