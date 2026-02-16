import requests
from datetime import datetime
import pytz

# --- DATA VALID ROSIT ---
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"

def main():
    try:
        # 1. AMBIL DATA DARI BINANCE
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
        # RSI Sederhana (Relativity to Daily Range)
        rsi = ((p - l) / d_range) * 100 if d_range != 0 else 50
        # Z-Score (Mendeteksi harga 'terlalu murah')
        z_score = (p - ((h+l+o+p)/4)) / (max(d_range/4, 0.01))

        # 3. SCORING MATRIX
        score = 0
        logs = []
        if z_score < -1.2: score += 30; logs.append("Harga Undervalue")
        if p < vwap: score += 20; logs.append("Discount Area")
        if rsi < 40: score += 20; logs.append("Oversold")
        if m_cp < -1.0: score += 30; logs.append("Safe Haven Active")

        # 4. SET WAKTU JAKARTA
        tz = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz).strftime('%H:%M:%S')
        
        # 5. GENERATE PESAN
        if score >= 70:
            header = "🔱 SINYAL OMNISCIENT: GACOR! 🔱"
            action = f"⚡ ACTION: BUY NOW\n🎯 TP: ${p+7:.2f}\n🛡️ SL: ${p-3.50:.2f}"
            footer = f"💡 Analisa: {', '.join(logs)}"
        else:
            header = "📡 OMNISCIENT STATUS: STANDBY"
            action = "⚠️ KETERANGAN:\nMarket belum ideal. Tunggu momen akurasi tinggi."
            footer = f"🔍 RSI: {rsi:.1f} | Z-Score: {z_score:.2f}"

        pesan = (
            f"{header}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🕒 JAM   : {waktu} WIB\n"
            f"💵 GOLD  : ${p:.2f}\n"
            f"📊 SCORE : {score}/100\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{action}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{footer}\n\n"
            f"Pantau terus, Rosit! Laporan tiap 15 menit."
        )

        # 6. KIRIM KE TELEGRAM
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": pesan})
        
        print(f"Status: {r.status_code}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
        
