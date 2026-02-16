import requests
from datetime import datetime
import pytz
import random

# DATA VALID ROSIT
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"

def main():
    print("Memulai sinkronisasi data...")
    try:
        # 1. AMBIL DATA HARGA
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGUSDT").json()
        p = float(res['lastPrice'])
        
        # 2. WAKTU JAKARTA
        tz = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz).strftime('%H:%M:%S')
        # ID Unik agar tidak dianggap spam oleh Telegram
        uid = random.randint(1000, 9999)
        
        # 3. PESAN DENGAN FORMAT BARU
        pesan = (
            f"ID Laporan: #{uid}\n"
            f"Waktu: {waktu} WIB\n"
            f"Harga Emas Saat Ini: ${p:.2f}\n"
            f"--------------------------\n"
            f"Status Sistem: Berjalan Normal\n"
            f"Update Rosit Otomatis"
        )

        # 4. KIRIM (Cara paling simpel)
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": pesan})
        
        print(f"Hasil: {r.status_code}")
        print(f"Respon: {r.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
