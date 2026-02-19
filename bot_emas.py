import requests
from datetime import datetime
import pytz
import json

# --- KONFIGURASI ROSIT ---
TELE_TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"
GEMINI_API_KEY = "AIzaSyBQCQMct2uSDHEIGGUUFoYYmXu38arf98Y"

def get_ai_analysis(p, change, area, volatility):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    # AI dikasih tahu kondisi volatilitas pasar saat ini
    v_status = "Tinggi (Liar)" if volatility > 1.5 else "Rendah (Tenang)"
    prompt = f"Rosit tanya: Harga ${p:.2f}, Area {area:.1f}, Volatilitas {v_status}. Berikan saran trading tegas 2 kalimat panggil Rosit."
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return f"Rosit, market lagi {v_status.lower()}. Pantau area {area:.1f} untuk keputusan entry."

def main():
    try:
        # 1. AMBIL DATA LENGKAP
        url_data = "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=PAXG&tsyms=USD"
        res = requests.get(url_data).json()
        data = res['RAW']['PAXG']['USD']
        
        p = data['PRICE']
        low = data['LOW24HOUR']
        high = data['HIGH24HOUR']
        change = data['CHANGEPCT24HOUR']
        
        # 2. HITUNG VOLATILITAS ( Momentum Pasar )
        # Mengukur jarak High-Low dalam persen
        volatility = ((high - low) / low) * 100
        
        # 3. SET TP & SL ADAPTIF ( MENYESUAIKAN MOMENTUM )
        # Jika market liar, SL diperlebar agar tidak kena 'noise'
        # Jika market tenang, SL diperketat agar profit lebih presisi
        if volatility > 1.5: # Market Liar
            sl_percent = 0.008 # 0.8%
            tp_percent = 0.015 # 1.5%
            momen = "⚠️ MOMENTUM: TINGGI (VOLATIL)"
        else: # Market Tenang
            sl_percent = 0.004 # 0.4%
            tp_percent = 0.008 # 0.8%
            momen = "⚖️ MOMENTUM: STABIL (TENANG)"

        sl = p * (1 - sl_percent)
        tp = p * (1 + tp_percent)
        area = ((p - low) / (high - low)) * 100 if (high - low) != 0 else 50

        # 4. ANALISA AI
        ai_msg = get_ai_analysis(p, change, area, volatility)

        # 5. WAKTU JAKARTA
        tz = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz).strftime('%H:%M:%S')

        # 6. KIRIM TELEGRAM
        emoji = "🔥" if area < 35 else "📡"
        msg = (
            f"{emoji} **OMNISCIENT MOMENTUM** {emoji}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🕒 **WAKTU** : {waktu} WIB\n"
            f"💵 **GOLD** : `${p:.2f}` ({change:.2f}%)\n"
            f"📊 **AREA** : {area:.1f}/100\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🧠 **ANALISA AI:**\n_{ai_msg.strip()}_\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎯 **ADAPTIVE TP**: `${tp:.2f}`\n"
            f"🛡️ **ADAPTIVE SL**: `${sl:.2f}`\n"
            f"💡 **INFO**: {momen}\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
