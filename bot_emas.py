import requests
from datetime import datetime
import pytz

# DATA FIX ROSIT
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"

def main():
    try:
        # Ambil data harga emas (PAXG)
        url_binance = "https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGUSDT"
        data = requests.get(url_binance).json()
        price = float(data['lastPrice'])
        
        # Waktu Jakarta
        wib = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(wib).strftime('%H:%M:%S')
        
        # Pesan Standby (Heartbeat) agar pasti ngirim setiap 15 menit
        pesan = (
            f"📡 **OMNISCIENT LIVE REPORT**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🕒 Waktu: {waktu} WIB\n"
            f"💵 Harga: ${price:.2f}\n"
            f"✅ Status: Sistem Aktif & Memantau\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Sabar ya Rosit, bot akan lapor tiap 15 menit."
        )
        
        # Kirim ke Telegram
        send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}
        
        r = requests.post(send_url, json=payload)
        print(f"Status Kirim: {r.status_code}") # Ini akan muncul di log GitHub Actions

    except Exception as e:
        print(f"Error Terjadi: {e}")

if __name__ == "__main__":
    main()
    
