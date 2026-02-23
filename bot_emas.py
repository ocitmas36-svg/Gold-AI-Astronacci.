import requests
import os
from datetime import datetime

# --- KUNCI RAHASIA ---
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def kirim_tele(pesan):
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"})

def get_market_data():
    try:
        # Ambil harga BTC dari Binance (Simpel)
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=10).json()
        p_now = float(res['lastPrice'])
        low_24h = float(res['lowPrice'])
        high_24h = float(res['highPrice'])
        
        # Hitung posisi harga (Area) sederhana berdasarkan range 24 jam
        area = ((p_now - low_24h) / (high_24h - low_24h)) * 100
        
        return p_now, area, low_24h, high_24h
    except Exception as e:
        kirim_tele(f"❌ Error Data: {e}")
        return None

def main():
    data = get_market_data()
    if not data: return

    p, area, support, resistance = data
    
    # Logika Sinyal Sederhana (Biar Gak Error)
    if area < 30:
        signal, emoji = "GAS BUY (Momen Murah)", "🟢"
        tp, sl = p * 1.01, p * 0.99
    elif area > 70:
        signal, emoji = "GAS SELL (Momen Mahal)", "🔴"
        tp, sl = p * 0.99, p * 1.01
    else:
        signal, emoji = "NGOPI DULU (Sabar)", "🟡"
        tp, sl = p, p

    # Format Pesan (Tanpa AI dulu biar pasti masuk!)
    msg = (
        f"🟠 **BITCOIN (BTCUSDm) REPORT** 🟠\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📢 **AKSI**: `{emoji} {signal}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💵 **HARGA**: `${p:,.2f}`\n"
        f"📊 **AREA**: {area:.1f}%\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **TARGET TP**: `${tp:,.2f}`\n"
        f"🛡️ **STOP LOSS**: `${sl:,.2f}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⏰ **WAKTU**: {datetime.now().strftime('%H:%M:%S')} WIB\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    
    kirim_tele(msg)
    print("✅ Berhasil kirim!")

if __name__ == "__main__":
    main()