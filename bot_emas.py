import requests
from datetime import datetime
import pytz

# DATA VALID ROSIT
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"

def main():
    print("Menganalisa Market Emas...")
    try:
        # 1. AMBIL HARGA TERBARU (PAXG = EMAS)
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGUSDT").json()
        p = float(res['lastPrice'])
        h = float(res['highPrice'])
        l = float(res['lowPrice'])
        
        # 2. HITUNG INDIKATOR (RSI SEDERHANA)
        rsi = ((p - l) / (h - l)) * 100 if (h - l) != 0 else 50
        
        # 3. WAKTU JAKARTA
        tz = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz).strftime('%H:%M:%S')
        
        # 4. TENTUKAN SINYAL
        if rsi < 40:
            status = "🔱 SINYAL: GACOR (BUY) 🔱"
            action = f"⚡ ACTION: BUY NOW\n🎯 TP: ${p+7:.2f}\n🛡️ SL: ${p-3.5:.2f}"
        else:
            status = "📡 STATUS: STANDBY"
            action = "⚠️ KETERANGAN:\nMarket belum ideal. Menunggu harga diskon."

        pesan = (
            f"{status}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🕒 JAM   : {waktu} WIB\n"
            f"💵 GOLD  : ${p:.2f}\n"
            f"📊 RSI   : {rsi:.1f}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{action}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Laporan Rosit tiap 15 menit."
        )

        # 5. KIRIM KE TELEGRAM
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": pesan})
        print("Pesan Terkirim!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
            
