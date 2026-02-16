import requests
from datetime import datetime
import pytz

# DATA VALID ROSIT
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"

def main():
    try:
        # 1. AMBIL DATA HARGA
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGUSDT").json()
        p = float(res['lastPrice'])
        h = float(res['highPrice'])
        l = float(res['lowPrice'])
        
        # 2. LOGIKA STANDAR (RSI SEDERHANA)
        rsi = ((p - l) / (h - l)) * 100 if (h - l) != 0 else 50
        
        # 3. WAKTU JAKARTA
        tz = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz).strftime('%H:%M:%S')
        
        # 4. PENENTUAN PESAN (Tanpa Markdown rumit dulu biar pasti masuk)
        if rsi < 30:
            status = "🚀 SINYAL: GACOR (BUY)"
            detail = f"🎯 TP: ${p+8:.2f}\n🛡️ SL: ${p-4:.2f}"
        else:
            status = "📡 STATUS: STANDBY"
            detail = "Market belum cukup murah untuk BUY."

        pesan = (
            f"{status}\n"
            f"--------------------------\n"
            f"🕒 JAM : {waktu} WIB\n"
            f"💵 EMAS: ${p:.2f}\n"
            f"📊 RSI : {rsi:.1f}\n"
            f"--------------------------\n"
            f"{detail}\n"
            f"--------------------------\n"
            f"Laporan Rosit tiap 15 menit."
        )

        # 5. KIRIM KE TELEGRAM (Tanpa Parse Mode biar anti-error)
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": pesan})
        
        print(f"Hasil: {r.status_code}")
        print(f"Respon: {r.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
    
