import requests
from datetime import datetime
import pytz

# --- KONFIGURASI FINAL ---
# Token bot kamu dan ID asli Rosit (7425438429)
TOKEN = "7864440626:AAH_Qz67CNo5XW1iXW9o17l1xR0YpD7G5mI"
CHAT_ID = "7425438429"

def main():
    try:
        # 1. AMBIL DATA DARI BINANCE
        # Mengambil data Emas (PAXG) dan Bitcoin (BTC) untuk analisis korelasi
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGUSDT").json()
        btc = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT").json()
        
        p = float(res['lastPrice'])
        h = float(res['highPrice'])
        l = float(res['lowPrice'])
        o = float(res['openPrice'])
        v = float(res['volume'])
        qv = float(res['quoteVolume'])
        m_cp = float(btc['priceChangePercent'])

        # 2. LOGIKA MATEMATIKA (INDIKATOR)
        d_range = h - l
        vwap = qv / v if v != 0 else p
        # RSI Sederhana (Mendeteksi Jenuh Jual)
        rsi = ((p - l) / d_range) * 100 if d_range != 0 else 50
        # Z-Score (Mendeteksi Harga Murah secara Statistik)
        z_score = (p - ((h+l+o+p)/4)) / (max(d_range/4, 0.01))

        # 3. SCORING MATRIX (FITUR OMNISCIENT)
        score = 0
        logs = []
        if z_score < -1.8: score += 30; logs.append("Z-Score: Murah")
        if p < vwap: score += 20; logs.append("VWAP: Discount")
        if rsi < 30: score += 20; logs.append("RSI: Oversold")
        if m_cp < -2.0: score += 30; logs.append("Safe Haven Aktif (BTC Drop)")

        # 4. WAKTU INDONESIA (WIB)
        wib = pytz.timezone('Asia/Jakarta')
        tabel_waktu = datetime.now(wib).strftime('%H:%M:%S')
        
        # 5. PENENTUAN PESAN (GACOR VS STANDBY)
        if score >= 70:
            # Jika skor tinggi, kirim instruksi trading
            action = "🚀 BUY NOW"
            tp = 8.0 # Take Profit $8
            sl = 4.0 # Stop Loss $4
            status_text = (
                f"🔱 **SINYAL OMNISCIENT: GACOR!**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🕒 TIME: {tabel_waktu} WIB\n"
                f"💵 PRICE: ${p:.2f}\n"
                f"📊 SCORE: {score}/100 (KUAT)\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"⚡ **ACTION: {action}**\n"
                f"🎯 TARGET PROFIT: ${p+tp:.2f}\n"
                f"🛡️ STOP LOSS: ${p-sl:.2f}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"💡 *Alasan:* {', '.join(logs)}"
            )
        else:
            # Jika skor rendah, kirim laporan standby (Heartbeat)
            status_text = (
                f"📡 **OMNISCIENT STATUS: STANDBY**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🕒 TIME: {tabel_waktu} WIB\n"
                f"💵 PRICE: ${p:.2f}\n"
                f"📊 SCORE: {score}/100\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"⚠️ **KETERANGAN:**\n"
                f"Market belum cukup bagus. Bot sedang menunggu momen akurasi tinggi. Sabar ya, Rosit!\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🔍 *Analisa:* RSI {rsi:.1f} | Z-Score {z_score:.2f}"
            )

        # 6. KIRIM KE TELEGRAM
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": status_text, "parse_mode": "Markdown"}
        requests.post(url, json=payload)

    except Exception as e:
        print(f"Terjadi kesalahan teknis: {e}")

if __name__ == "__main__":
    main()
        
