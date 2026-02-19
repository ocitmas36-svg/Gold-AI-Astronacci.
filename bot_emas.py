import requests
from datetime import datetime
import pytz
import json

# --- KONFIGURASI ROSIT ---
TELE_TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"
GEMINI_API_KEY = "AIzaSyBQCQMct2uSDHEIGGUUFoYYmXu38arf98Y"

def get_ai_analysis(p, change, area):
    """Fungsi Otak AI dengan cadangan logika cerdas"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"Rosit tanya: Harga emas sekarang ${p:.2f}, area {area:.1f}. Berikan saran trading singkat 2 kalimat saja panggil nama Rosit."
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        res_json = response.json()
        # Jika sukses ambil dari Gemini
        return res_json['candidates'][0]['content']['parts'][0]['text']
    except:
        # JALUR CADANGAN: Logika Otomatis jika API Gemini ngadat
        if area < 35:
            return f"Halo Rosit! Area {area:.1f} ini diskon besar. Secara teknikal ini momen Buy yang cakep. Sikat tipis-tipis!"
        elif area > 65:
            return f"Rosit, hati-hati ya, harga sudah di area {area:.1f} (mahal). Mending jangan kejar atas, rawan longsor!"
        else:
            return f"Market lagi anteng di area {area:.1f} nih Rosit. Mending Wait & See dulu sampai ada pergerakan liar."

def main():
    try:
        # 1. DATA HARGA
        url_data = "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=PAXG&tsyms=USD"
        res = requests.get(url_data).json()
        data = res['RAW']['PAXG']['USD']
        
        p = data['PRICE']
        low = data['LOW24HOUR']
        high = data['HIGH24HOUR']
        change = data['CHANGEPCT24HOUR']
        
        # 2. LOGIKA TRADING
        area = ((p - low) / (high - low)) * 100 if (high - low) != 0 else 50
        tp = p * 1.008
        sl = p * 0.994

        # 3. AMBIL ANALISA
        ai_msg = get_ai_analysis(p, change, area)

        # 4. WAKTU JAKARTA
        tz = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz).strftime('%H:%M:%S')

        # 5. KIRIM TELEGRAM
        emoji = "🔥" if area < 35 else "📡"
        msg = (
            f"{emoji} **OMNISCIENT AI SYSTEM** {emoji}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🕒 **WAKTU** : {waktu} WIB\n"
            f"💵 **GOLD** : `${p:.2f}` ({change:.2f}%)\n"
            f"📈 **AREA** : {area:.1f}/100\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🧠 **ANALISA:**\n_{ai_msg.strip()}_\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎯 **TP**: `${tp:.2f}`\n"
            f"🛡️ **SL**: `${sl:.2f}`\n"
        )
        
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
