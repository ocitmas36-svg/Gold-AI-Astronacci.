import requests
import os
from datetime import datetime

# --- KONFIGURASI ---
TOKEN = "7864440626:AAH_Qz67CNo5XW1iXW9o17l1xR0YpD7G5mI"
CHAT_ID = "5378770281"

def get_gold_price():
    url = "https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGUSDT"
    try:
        response = requests.get(url)
        data = response.json()
        return {
            "price": float(data['lastPrice']),
            "high": float(data['highPrice']),
            "low": float(data['lowPrice']),
            "open": float(data['openPrice']),
            "change_percent": float(data['priceChangePercent'])
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def main():
    gold_data = get_gold_price()
    if not gold_data: return

    current_price = gold_data['price']
    high_24h = gold_data['high']
    low_24h = gold_data['low']
    open_price = gold_data['open']
    change = gold_data['change_percent']

    # 1. HITUNG FIBONACCI 61.8%
    fibo_618 = high_24h - (0.618 * (high_24h - low_24h))
    
    # 2. HITUNG RATA-RATA (SMA Sederhana dari High-Low-Open)
    # Sebagai filter: Apakah harga sekarang di atas rata-rata harian?
    sma_filter = (high_24h + low_24h + open_price) / 3

    action = None
    
    # --- LOGIKA GACOR V4.0 ---
    
    # SKENARIO A: BUY (Area Fibo + Tren Sehat)
    if current_price <= fibo_618:
        if current_price > low_24h + 2.0: # Filter: Harga harus sudah mulai mantul dari titik terendah
            status = "🚀 GACOR BUY (REBOUND CONFIRMED)"
            analisis = "Harga di area Fibo & sudah mulai mantul dari bawah. Peluang naik tinggi!"
            tp_price = current_price + 7.0 # Profit dinaikkan jadi $7 karena tren sehat
            sl_price = current_price - 4.0
            action = "BUY"
            emoji = "🟢"
        else:
            print("Sinyal Buy ditahan: Harga masih terlalu dekat dasar, takutnya jebol lagi.")
            return

    # SKENARIO B: SELL (Puncak Jenuh + Filter SMA)
    elif current_price >= high_24h * 0.998:
        status = "🔥 GACOR SELL (TOP REJECTION)"
        analisis = "Harga mentok di atap harian. Saatnya ambil untung dari penurunan!"
        tp_price = current_price - 6.0
        sl_price = current_price + 4.0
        action = "SELL"
        emoji = "🔴"

    # SKENARIO C: SUPER BREAKOUT
    elif current_price > high_24h:
        status = "💎 SUPER BREAKOUT (TREN MONSTER)"
        analisis = "Emas pecah rekor hari ini! Jangan dilawan, ikut terbang!"
        tp_price = current_price + 10.0 # Profit maksimal $10
        sl_price = current_price - 5.0
        action = "BUY"
        emoji = "⚡"

    else:
        # Mode Silent: Tidak ada pesan jika tidak ada momen
        print(f"Monitoring... Price: ${current_price:.2f} | Netral")
        return

    # --- KIRIM PESAN ---
    pesan = (
        f"{emoji} **ROSIT GACOR AI v4.0**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💵 Harga: ${current_price:.2f}\n"
        f"📊 Tren: {'📈 BULLISH' if current_price > sma_filter else '📉 BEARISH'}\n"
        f"🧐 Analisis: {analisis}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📝 **PLAN TRADING:**\n"
        f"✅ ENTRY : {action}\n"
        f"🎯 TARGET TP: ${tp_price:.2f}\n"
        f"🛡️ STOP LOSS: ${sl_price:.2f}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 *Kawal sampai Profit, Rosit!*"
    )
    
    send_telegram(pesan)

if __name__ == "__main__":
    main()
