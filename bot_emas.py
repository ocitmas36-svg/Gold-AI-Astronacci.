import requests
from datetime import datetime
import pytz

# --- DATA VALID ROSIT ---
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"

def main():
    try:
        # 1. AMBIL DATA HARGA
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGUSDT").json()
        btc = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT").json()
        
        p = float(res['lastPrice'])
        h = float(res['highPrice'])
        l = float(res['lowPrice'])
        o = float(res['openPrice'])
        v = float(res['volume'])
        qv = float(res['quoteVolume'])
        m_cp = float(btc['priceChangePercent'])

        # 2. LOGIKA MATEMATIKA (OTAK BOT)
        d_range = h - l
        vwap = qv / v if v != 0 else p
        rsi = ((p - l) / d_range) * 100 if d_range != 0 else 50
        z_score = (p - ((h+l+o+p)/4)) / (max(d_range/4, 0.01))

        # 3. SCORING MATRIX
        score = 0
        logs = []
        if z_score < -1.5: score += 30; logs.append("Z-Score Murah")
        if p < vwap: score += 20; logs.append("Dibawah VWAP")
        if rsi < 35: score += 20; logs.append("RSI Oversold")
        if m_cp < -1.5: score += 30; logs.append("Korelasi BTC Aman")

        # 4. WAKTU & PESAN
        tz = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz).strftime('%H:%M:%S')
        
        if score >= 70:
            status = "🔱 **SINYAL OMNISCIENT: GACOR!**"
            action = f"⚡ **ACTION: BUY NOW**\n🎯 TP: ${p+7:.2f} | 🛡️ SL: ${p-3.5:.2f}"
            ket = f"💡 *Analisa:* {', '.join(logs)}"
        else:
            status = "📡 **OMNISCIENT STATUS: STANDBY**"
            action = "⚠️ **KETERANGAN:**\nMarket belum bagus buat trending."
            ket = f"🔍 RSI: {rsi:.1f} | Z-Score: {z_score:.2f}"

        pesan = (
            f"{status}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🕒 JAM : {waktu} WIB\n"
            f"💵 GOLD: ${p:.2f}\n"
            f"📊 SKOR: {score}/100\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{action}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{ket}\n"
            f"Tetap pantau, Rosit! Bot lapor tiap 15 menit."
        )

        # 5. EKSEKUSI KIRIM
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"})
        print(f"Hasil Kirim: {r.status_code}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
    
