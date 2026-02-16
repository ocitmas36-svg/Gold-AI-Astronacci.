import requests
from datetime import datetime
import pytz

# DATA VALID ROSIT
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"

def main():
    print("Sistem Memulai Analisa...") # Ini agar log tidak 0 detik
    try:
        # AMBIL HARGA
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGUSDT").json()
        p = float(res['lastPrice'])
        
        # WAKTU JAKARTA
        tz = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz).strftime('%H:%M:%S')
        
        pesan = (
            f"💰 SINYAL EMAS ROSIT\n"
            f"------------------\n"
            f"🕒 JAM   : {waktu} WIB\n"
            f"💵 HARGA : ${p:.2f}\n"
            f"------------------\n"
            f"Status: MONITORING..."
        )

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": pesan})
        
        print(f"Hasil Kirim: {r.status_code}")
        print(f"Respon: {r.text}")

    except Exception as e:
        print(f"Error Terjadi: {e}")

if __name__ == "__main__":
    main()
    
