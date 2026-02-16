import requests
import os
from datetime import datetime

# --- KONFIGURASI LANGSUNG ---
# Token dan ID sudah saya masukkan sesuai data kamu
TOKEN = "7864440626:AAH_Qz67CNo5XW1iXW9o17l1xR0YpD7G5mI"
CHAT_ID = "5378770281"

def get_gold_price():
    # Mengambil data harga emas (XAU/USD) dari API Binance (PAXG/USDT)
    url = "https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGUSDT"
    try:
        response = requests.get(url)
        data = response.json()
        return {
            "price": float(data['lastPrice']),
            "high": float(data['highPrice']),
            "low": float(data['lowPrice']),
            "change_percent": float(data['priceChangePercent'])
        }
    except Exception as e:
        print(f"Error ambil data: {e}")
        return None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error kirim Telegram: {e}")

def main():
    gold_data = get_gold_price()
    if not gold_data:
        return

    current_price = gold_data['price']
    high_24h = gold_data['high']
    low_24h = gold_data['low']
    change = gold_data['change_percent']

    # HITUNG FIBONACCI (Golden Ratio 61.8%)
    fibo_618 = high_24h - (0.618 * (high_24h - low_24h))

    # --- LOGIKA OTAK PREDATOR (ILMU PREDIKSI) ---
    action = None
    
    # 1. SKENARIO BUY (DISKON + FILTER SAFETY)
    if current_price <= fibo_618:
        # Jika harga turun terlalu ekstrem (> 2.5%), bot menahan diri (Filter Anti-Anjlok)
        if change > -2.5:
            status = "🚀 SINYAL BUY (GOLDEN RATIO)"
            analisis = "Harga masuk area diskon Fibonacci. Secara psikologi, ini titik murah untuk beli."
            tp_price = current_price + 6.0
            sl_price = current_price - 4.0
            action = "BUY"
            emoji = "🟢"
        else:
            print("Market terlalu panik (Crash), Bot menahan diri untuk tidak Buy.")
            return

    # 2. SKENARIO BREAKOUT (IKUT TREN KUAT)
    elif current_price >= high_24h:
        status = "⚡ BREAKOUT BUY (TREN SUPER)"
        analisis = "Harga menembus titik tertinggi harian! Pembeli sangat dominan, ikut arus!"
        tp_price = current_price + 8.0 
        sl_price = current_price - 5.0
        action = "BUY"
        emoji = "💎"

    # 3. SKENARIO SELL (PUNCAK KEJENUHAN)
    elif current_price >= high_24h * 0.998:
        status = "🔥 SINYAL SELL (AREA JENUH)"
        analisis = "Harga sudah di pucuk harian. Potensi trader besar mulai ambil untung."
        tp_price = current_price - 6.0
        sl_price = current_price + 4.0
        action = "SELL"
        emoji = "🔴"

    # JIKA TIDAK ADA MOMEN
    else:
        print(f"Monitoring... Harga: ${current_price:.2f} | Change: {change}% (Belum ada momen)")
        return

    # --- PENYUSUNAN PESAN PREDATOR ---
    pesan = (
        f"{emoji} **ROSIT PREDATOR AI v3.0**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💵 Harga: ${current_price:.2f}\n"
        f"📉 Harian: {change}%\n"
        f"📊 Status: {status}\n"
        f"🧐 Analisis: {analisis}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📝 **STRATEGI SCALPING:**\n"
        f"✅ ENTRY : {action} di ${current_price:.2f}\n"
        f"🎯 TARGET TP: ${tp_price:.2f}\n"
        f"🛡️ STOP LOSS: ${sl_price:.2f}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💡 *Saran: Gunakan Lot Aman & Sabar Menunggu!*"
    )
    
    send_telegram(pesan)

if __name__ == "__main__":
    main()
