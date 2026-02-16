import requests
from datetime import datetime
import pytz

# DATA VALID ROSIT
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"

def main():
    try:
        # 1. AMBIL HARGA
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGUSDT").json()
        price = float(res['lastPrice'])
        
        # 2. WAKTU JAKARTA
        tz = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz).strftime('%H:%M:%S')
        
        # 3. PESAN POLOS (TANPA BINTANG / GARIS KHUSUS)
        pesan = (
            "LAPORAN PASAR EMAS\n"
            "------------------\n"
            f"JAM   : {waktu} WIB\n"
            f"HARGA : ${price:.2f}\n"
            "------------------\n"
            "Status: Bot Aktif Memantau"
        )

        # 4. KIRIM (TANPA PARSE_MODE)
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": pesan}
        
        r = requests.post(url, json=payload)
        
        # Munculkan di log GitHub untuk kita cek
        print(f"Status: {r.status_code}")
        print(f"Respon Telegram: {r.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
    
