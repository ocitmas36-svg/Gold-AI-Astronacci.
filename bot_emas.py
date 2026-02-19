import requests
from datetime import datetime
import pytz

# DATA VALID ROSIT
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"

def main():
    print("Mencoba ambil harga emas via jalur alternatif...")
    try:
        # Gunakan API CryptoCompare (Lebih stabil untuk bot GitHub)
        url = "https://min-api.cryptocompare.com/data/price?fsym=PAXG&tsyms=USD"
        res = requests.get(url).json()
        
        # Ambil harga
        p = res.get('USD', 0)
        
        # WAKTU JAKARTA
        tz = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz).strftime('%H:%M:%S')

        if p > 0:
            pesan = (
                f"🔱 OMNISCIENT UPDATE 🔱\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🕒 JAM   : {waktu} WIB\n"
                f"💵 GOLD  : ${p:.2f}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"Status: Jalur Alternatif Aktif ✅"
            )
        else:
            pesan = f"⚠️ Sistem aktif pada {waktu}, tapi API sedang limit. Coba lagi nanti."

        # KIRIM KE TELEGRAM
        url_tele = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        r = requests.post(url_tele, json={"chat_id": CHAT_ID, "text": pesan})
        
        print(f"Harga didapat: {p}")
        print(f"Respon Telegram: {r.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
