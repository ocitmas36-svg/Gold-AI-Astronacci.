import requests
from datetime import datetime
import pytz

# DATA VALID ROSIT
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"

def main():
    print("Memulai sinkronisasi data via jalur cadangan...")
    try:
        # Gunakan API publik tanpa blokir untuk ambil harga Gold (PAXG)
        # Kita pakai link ticker simpel agar tidak kena filter 'lastPrice'
        url_price = "https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT"
        res = requests.get(url_price).json()
        
        # Validasi apakah data ada
        if 'price' in res:
            p = float(res['price'])
            print(f"Harga berhasil didapat: {p}")
        else:
            print(f"Gagal ambil harga. Respon: {res}")
            p = 0.0

        # WAKTU JAKARTA
        tz = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz).strftime('%H:%M:%S')

        if p > 0:
            status = "SISTEM AKTIF"
            pesan = (
                f"✅ OMNISCIENT TERHUBUNG!\n"
                f"--------------------------\n"
                f"🕒 JAM   : {waktu} WIB\n"
                f"💵 GOLD  : ${p:.2f}\n"
                f"--------------------------\n"
                f"Status: Monitoring Aman."
            )
        else:
            pesan = f"⚠️ Warning: Bot aktif pada {waktu} tapi gagal ambil data harga."

        # KIRIM KE TELEGRAM
        url_tele = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        r = requests.post(url_tele, json={"chat_id": CHAT_ID, "text": pesan})
        
        print(f"Respon Telegram: {r.text}")

    except Exception as e:
        print(f"Kesalahan Fatal: {e}")

if __name__ == "__main__":
    main()
