import requests
from datetime import datetime
import pytz

# --- KONFIGURASI IDENTITAS ROSIT ---
TELE_TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"
GEMINI_API_KEY = "AIzaSyBQCQMct2uSDHEIGGUUFoYYmXu38arf98Y"

def get_ai_analysis(price, change, area, high, low):
    """Mengirim data ke AI Gemini untuk mendapatkan analisa cerdas"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = (
        f"Kamu adalah OMNISCIENT AI, asisten trading pribadi Rosit. "
        f"Analisa data Emas (PAXG) berikut:\n"
        f"- Harga Sekarang: ${price}\n"
        f"- Perubahan 24j: {change}%\n"
        f"- Area Harga (0-100): {area:.1f}\n"
        f"- Tertinggi 24j: ${high}\n"
        f"- Terendah 24j: ${low}\n\n"
        f"Tugas: Berikan analisa singkat 2-3 kalimat. Berikan saran tegas (Buy/Sell/Wait) "
        f"dengan gaya bicara yang cerdas, suportif, dan panggil 'Rosit'. Gunakan Bahasa Indonesia santai."
    )
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Rosit, koneksi otak AI saya sedikit terganggu, tapi secara teknikal harga ada di ${price}. Pantau terus ya!"

def main():
    try:
        # 1. AMBIL DATA MARKET (PAXG/USDT)
        url_data = "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=PAXG&tsyms=USD"
        res = requests.get(url_data, timeout=10).json()
        data = res['RAW']['PAXG']['USD']
        
        p = data['PRICE']
        low = data['LOW24HOUR']
        high = data['HIGH24HOUR']
        change = data['CHANGEPCT24HOUR']
        vol = data['VOLUME24HOURTO']
        
        # 2. HITUNG AREA & STRATEGI (Dynamic)
        # Menghitung seberapa murah harga saat ini (0-100)
        area = ((p - low) / (high - low)) * 100 if (high - low) != 0 else 50
        
        # Target Profit 0.8% | Stop Loss 0.5% (Risk Reward Ratio Sehat)
        tp = p * 1.008
        sl = p * 0.995

        # 3. AKTIFKAN OTAK AI GEMINI
        ai_message = get_ai_analysis(p, f"{change:.2f}", area, high, low)

        # 4. SETTING WAKTU JAKARTA
        tz = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz).strftime('%H:%M:%S')

        # 5. FORMAT PESAN TELEGRAM (Markdown)
        status_emoji = "🚀" if area < 40 else "📡"
        header = f"{status_emoji} **OMNISCIENT AI SYSTEM** {status_emoji}\n"
        line = "━━━━━━━━━━━━━━━━━━\n"
        
        body = (
            f"🕒 **WAKTU** : {waktu} WIB\n"
            f"💵 **GOLD** : `${p:.2f}` ({change:.2f}%)\n"
            f"📈 **AREA** : {area:.1f}/100\n"
            f"{line}"
            f"🧠 **ANALISA AI:**\n_{ai_message}_\n"
            f"{line}"
            f"🎯 **TARGET TP**: `${tp:.2f}`\n"
            f"🛡️ **SAFETY SL**: `${sl:.2f}`\n"
            f"{line}"
            f"💰 **VOL 24H**: `${vol/1000000:.1f}M`"
        )
        
        # Kirim ke Telegram
        requests.post(
            f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
            json={"chat_id": CHAT_ID, "text": header + body, "parse_mode": "Markdown"}
        )
        
        print(f"Laporan AI Terkirim: Harga {p}")

    except Exception as e:
        print(f"Error pada sistem utama: {e}")

if __name__ == "__main__":
    main()
