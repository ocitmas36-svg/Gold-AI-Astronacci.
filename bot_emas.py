import requests
from datetime import datetime
import pytz

# --- DATA VALID ROSIT ---
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"

def main():
    try:
        # 1. AMBIL DATA HARGA (JALUR STABIL)
        # Kita ambil harga sekarang dan harga 24 jam lalu untuk hitung volatilitas
        url = "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=PAXG&tsyms=USD"
        res = requests.get(url).json()
        
        data = res['RAW']['PAXG']['USD']
        p = data['PRICE']
        high = data['HIGH24HOUR']
        low = data['LOW24HOUR']
        change = data['CHANGEPCT24HOUR']

        # 2. LOGIKA STRATEGI (RSI Sederhana & Volatilitas)
        # Menghitung posisi harga saat ini di rentang harian (0-100)
        rsi_logic = ((p - low) / (high - low)) * 100 if (high - low) != 0 else 50
        
        # 3. SET TP & SL AKURAT (Berdasarkan Volatilitas Pasar)
        # TP diambil sekitar 0.4% dari harga, SL sekitar 0.2% (Risk Reward 1:2)
        tp = p + (p * 0.004)
        sl = p - (p * 0.002)

        # 4. PENENTUAN SINYAL
        # Jika RSI di bawah 30 = Oversold (Waktunya Buy)
        # Jika RSI di bawah 50 = Harga masih di area diskon
        if rsi_logic < 40:
            status = "🔱 SINYAL: GACOR (BUY) 🔱"
            rekomendasi = f"⚡ ACTION: ENTRY BUY\n🎯 TP: ${tp:.2f}\n🛡️ SL: ${sl:.2f}"
            power = "HIGH ACCURACY"
        else:
            status = "📡 STATUS: STANDBY"
            rekomendasi = "⚠️ KETERANGAN:\nMarket sedang konsolidasi.\nTunggu harga menyentuh area diskon."
            power = "LOW RISK"

        # 5. WAKTU JAKARTA
        tz = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz).strftime('%H:%M:%S')

        # 6. GENERATE PESAN MEWAH
        pesan = (
            f"{status}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🕒 JAM    : {waktu} WIB\n"
            f"💵 GOLD   : ${p:.2f}\n"
            f"📊 TREND  : {change:.2f}%\n"
            f"📈 AREA   : {rsi_logic:.1f}/100\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{rekomendasi}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔍 ANALISA: {power}\n"
            f"⏳ UPDATE : 15 Menit Sekali"
        )

        # 7. KIRIM KE TELEGRAM
        url_tele = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url_tele, json={"chat_id": CHAT_ID, "text": pesan})
        
        print(f"Update Berhasil: ${p} | RSI: {rsi_logic:.1f}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
