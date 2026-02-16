import requests
from datetime import datetime
import pytz

# --- KONFIGURASI FIX (SUDAH DITES BERHASIL) ---
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

        # 2. LOGIKA INDIKATOR
        d_range = h - l
        vwap = qv / v if v != 0 else p
        rsi = ((p - l) / d_range) * 100 if d_range != 0 else 50
        z_score = (p - ((h+l+o+p)/4)) / (max(d_range/4, 0.01))

        # 3. SCORING MATRIX
        score = 0
        logs = []
        if z_score < -1.8: score += 30; logs.append("Z-Score: Murah")
        if p < vwap: score += 20; logs.append("VWAP: Discount")
        if rsi < 30: score += 20; logs.append("RSI: Oversold")
        if m_cp < -2.0: score += 30; logs.append("Safe Haven Active")

        wib = pytz.timezone('Asia/Jakarta')
        tabel_waktu = datetime.now(wib).strftime('%H:%M:%S')
        
        if score >= 70:
            status_text = (
                f"🔱 **SINYAL OMNISCIENT: GACOR!**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🕒 TIME: {tabel_waktu} WIB\n"
                f"💵 PRICE: ${p:.2f}\n"
                f"📊 SCORE: {score}/100\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"⚡ **ACTION: BUY NOW**\n"
                f"🎯 TP: ${p+8:.2f} | 🛡️ SL: ${p-4:.2f}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"💡 *Logic:* {', '.join(logs)}"
            )
        else:
            status_text = (
                f"📡 **OMNISCIENT STATUS: STANDBY**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🕒 TIME: {tabel_waktu} WIB\n"
                f"💵 PRICE: ${p:.2f}\n"
                f"📊 SCORE: {score}/100\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"⚠️ **KETERANGAN:**\n"
                f"Market belum ideal untuk trending. Bot Standby.\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🔍 RSI {rsi:.1f} | Z-Score {z_score:.2f}"
            )

        # KIRIM KE TELEGRAM
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": status_text, "parse_mode": "Markdown"})

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
        
