import requests
from datetime import datetime
import pytz
import json

# --- KONFIGURASI IDENTITAS ROSIT ---
TELE_TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"
GEMINI_API_KEY = "AIzaSyBQCQMct2uSDHEIGGUUFoYYmXu38arf98Y"

def get_ai_analysis(price, change, area, high, low):
    """Mengirim data ke AI Gemini untuk mendapatkan analisa cerdas"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # Prompt yang lebih instruktif agar AI memberikan jawaban pasti
    prompt = (
        f"Analisa market Emas (PAXG) untuk trader bernama Rosit.\n"
        f"Data: Harga ${price:.2f}, Perubahan {change}%, Posisi Area {area:.1f}/100.\n"
        f"Batas harian: Low ${low:.2f} - High ${high:.2f}.\n"
        f"Berikan saran Buy/Sell/Wait yang tegas dan singkat (maksimal 3 kalimat). "
        f"Gunakan gaya bahasa asisten profesional tapi santai. Sapa Rosit di awal."
    )
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 200,
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
        res_json = response.json()
        if 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Rosit, harga saat ini ${price:.2f}. Secara teknikal area {area:.1f} menunjukkan sinyal pantauan. Tetap waspada!"
    except Exception as e:
        print(f"Detail Error AI: {e}")
        return f"Rosit, market sedang volatil di ${price:.2f}. Gunakan SL ketat dan pantau terus pergerakannya!"

def main():
    try:
        # 1. AMBIL DATA MARKET (PAXG/USD)
        url_data = "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=PAXG&tsyms=USD"
        res = requests.get(url_data, timeout=10).json()
        data = res['RAW']['PAXG']['USD']
        
        p = data['PRICE']
        low = data['LOW24HOUR']
        high = data['HIGH24HOUR']
        change = data['CHANGEPCT24HOUR']
        vol = data['VOLUME24HOURTO']
        
        # 2. HITUNG AREA & STRATEGI
        # Menghitung seberapa murah harga saat ini (0-100)
        area = ((p - low) / (high - low)) * 100 if (high - low) != 0 else 50
        
        # Target Profit 0.8% | Stop Loss 0.6%
        tp = p * 1.008
        sl = p * 0.994

        # 3. AKTIFKAN OTAK AI GEMINI
        ai_message = get_ai_analysis(p, f"{change:.2f}", area, high, low)

        # 4. SETTING WAKTU JAKARTA
        tz = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz).strftime('%H:%M:%S')

        # 5. FORMAT PESAN TELEGRAM
        # Tentukan emoji berdasarkan area
        if area < 30: emoji = "🔥"
        elif area > 70: emoji = "⚠️"
        else: emoji = "📡"

        header = f"{emoji} **OMNISCIENT AI SYSTEM** {emoji}\n"
        line = "━━━━━━━━━━━━━━━━━━\n"
        
        body = (
            f"🕒 **WAKTU** : {waktu} WIB\n"
            f"💵 **GOLD** : `${p:.2f}` ({change:.2f}%)\n"
            f"📈 **AREA** : {area:.1f}/100\n"
            f"{line}"
            f"🧠 **ANALISA AI:**\n{ai_message.strip()}\n"
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
        
        print(f"Sistem Berhasil: Laporan dikirim pada {waktu}")

    except Exception as e:
        print(f"Error pada sistem utama: {e}")

if __name__ == "__main__":
    main()
