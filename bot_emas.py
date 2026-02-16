import requests
from datetime import datetime
import pytz

# --- KONFIGURASI ---
TOKEN = "7864440626:AAH_Qz67CNo5XW1iXW9o17l1xR0YpD7G5mI"
CHAT_ID = "5378770281"

def main():
    try:
        # 1. AMBIL DATA
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGUSDT").json()
        btc = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT").json()
        
        p = float(res['lastPrice'])
        h = float(res['highPrice'])
        l = float(res['lowPrice'])
        o = float(res['openPrice'])
        v = float(res['volume'])
        qv = float(res['quoteVolume'])
        c = int(res['count'])
        cp = float(res['priceChangePercent'])
        m_cp = float(btc['priceChangePercent'])

        # 2. LOGIKA MATEMATIKA
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

        # 4. DECISION
        action = None
        if score >= 70: action = "BUY"
        elif rsi > 80: action = "SELL"
        else: return

        # 5. RISK MANAGEMENT
        tp = 8.0
        sl = 4.0
        wib = pytz.timezone('Asia/Jakarta')
        tabel_waktu = datetime.now(wib).strftime('%H:%M:%S')

        # 6. KIRIM PESAN
        text = (
            f"🔱 **THE OMNISCIENT FINAL**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🕒 TIME: {tabel_waktu} WIB\n"
            f"💵 PRICE: ${p:.2f}\n"
            f"📊 SCORE: {score}/100\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⚡ **ACTION: {action}**\n"
            f"🎯 TP: {p+tp if action=='BUY' else p-tp:.2f}\n"
            f"🛡️ SL: {p-sl if action=='BUY' else p+sl:.2f}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💡 *Logic:* {', '.join(logs)}"
        )
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    main()
