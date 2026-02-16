import requests
from datetime import datetime
import pytz

# DATA VALID ROSIT
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"

def main():
    print("Memulai analisa market...")
    try:
        # 1. AMBIL DATA HARGA
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGUSDT").json()
        p = float(res['lastPrice'])
        h = float(res['highPrice'])
        l = float(res['lowPrice'])
        
        # 2. LOGIKA MATEMATIKA
        rsi = ((p - l) / (h - l)) * 100 if (h - l) != 0 else 50
        
        # 3. WAKTU JAKARTA
        tz = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz).strftime('%H:%M:%S')
        
        # 4. PENENTUAN STATUS (Teks Polos Anti-Gagal)
        if rsi < 40:
            status = "SINYAL: GACOR (BUY)"
            action = f"ACTION: BUY NOW\nTP: ${p+7:.2f}\nSL: ${p-3.5:.2f}"
        else:
            status = "STATUS: STANDBY"
            action = "Keterangan: Market belum ideal."

        pesan = (
            f"--- {status} ---\n"
            f"JAM   : {waktu} WIB\n"
            f"HARGA : ${p:.2f}\n"
            f"RSI   : {rsi:.1f}\n"
            "------------------\n"
            f"{action}\n"
            "------------------\n"
            "Laporan Rosit 15 Menit."
        )

        # 5. KIRIM KE TELEGRAM (Tanpa JSON rumit)
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={requests.utils.quote(pesan)}"
        r = requests.get(url) 
        
        print(f"Status Kirim: {r.status_code}")
        print(f"Respon: {r.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
    
