import requests
import os

# --- AMBIL KUNCI ---
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def main():
    try:
        # 1. Ambil harga BTC dari Binance
        res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=10).json()
        p = float(res['price'])
        
        # 2. Hitung TP/SL Sederhana
        tp = p + 450
        sl = p - 300
        
        # 3. Susun pesan
        msg = (
            f"🟠 **BTCUSDm REPORT** 🟠\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💵 **HARGA PLATFORM**: `${p:,.2f}`\n"
            f"🎯 **TARGET TP**: `${tp:,.2f}`\n"
            f"🛡️ **STOP LOSS**: `${sl:,.2f}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📢 **STATUS**: `BOT AKTIF & SINKRON`\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        
        # 4. Kirim ke Telegram
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        kirim = requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        
        if kirim.status_code == 200:
            print("✅ BERHASIL! Cek HP kamu, Sit!")
        else:
            print(f"❌ GAGAL! Telegram bilang: {kirim.text}")

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    main()