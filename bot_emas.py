import requests
import os

# --- KONFIGURASI ---
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def get_gold_price():
    url = "https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGUSDT"
    try:
        response = requests.get(url)
        data = response.json()
        return {
            "price": float(data['lastPrice']),
            "high": float(data['highPrice']),
            "low": float(data['lowPrice'])
        }
    except Exception as e:
        print(f"Error ambil data: {e}")
        return None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def main():
    gold_data = get_gold_price()
    if not gold_data:
        return

    current_price = gold_data['price']
    high_24h = gold_data['high']
    low_24h = gold_data['low']

    # HITUNG FIBONACCI (Golden Ratio 61.8%)
    fibo_618 = high_24h - (0.618 * (high_24h - low_24h))

    # --- LOGIKA SINYAL DINAMIS ---
    action = None
    if current_price <= fibo_618:
        # AREA BUY
        status = "🚀 SINYAL BUY (AREA DISKON)"
        analisis = "Harga di bawah Golden Ratio. Potensi pantulan naik!"
        tp_price = current_price + 6.0
        sl_price = current_price - 4.0
        emoji = "🟢"
        action = "BUY"
    elif current_price >= high_24h * 0.998:
        # AREA SELL
        status = "🔥 SINYAL SELL (AREA PUNCAK)"
        analisis = "Harga mendekati titik tertinggi harian. Potensi koreksi turun!"
        tp_price = current_price - 6.0
        sl_price = current_price + 4.0
        emoji = "🔴"
        action = "SELL"
    else:
        # Jika tidak ada momen, bot diam (tidak kirim ke Telegram)
        print(f"Monitoring... Harga saat ini ${current_price:.2f} (Belum ada momen)")
        return 

    # --- PENYUSUNAN PESAN (Hanya terkirim jika ada Action) ---
    pesan = (
        f"{emoji} **ROSIT GOLD AI: MOMEN TERDETEKSI!**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💵 Harga: ${current_price:.2f}\n"
        f"📊 Status: {status}\n"
        f"🧐 Analisis: {analisis}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📝 **STRATEGI SCALPING:**\n"
        f"✅ ENTRY : {action} di ${current_price:.2f}\n"
        f"🎯 TARGET TP: ${tp_price:.2f}\n"
        f"🛡️ STOP LOSS: ${sl_price:.2f}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔥 *Sikat cepat, amankan profit!*"
    )
    
    send_telegram(pesan)

if __name__ == "__main__":
    main()
