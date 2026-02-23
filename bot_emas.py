import requests
import os

# --- AMBIL KUNCI ---
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def main():
    try:
        # 1. Ambil harga BTC paling gampang
        res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT").json()
        p = float(res['price'])
        
        # 2. Hitung TP dan SL kasar saja biar gak error rumus
        tp_buy = p + 500
        sl_buy = p - 300
        
        # 3. Susun pesan sederhana tapi rapi
        msg = (
            f"🟠 **BTCUSDm REPORT** 🟠\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💵 **HARGA**: `${p:,.2f}`\n"
            f"🎯 **TP**: `${tp_buy:,.2f}`\n"
            f"🛡️ **SL**: `${sl_buy:,.2f}`\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📢 **STATUS**: `BOT AKTIF`\n"
            f"━━━━━━━━━━━━━━━"
        )
        
        # 4. Kirim ke Telegram
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        kirim = requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        
        if kirim.status_code == 200:
            print("✅ BERHASIL! Cek Telegram.")
        else:
            print(f"❌ GAGAL! Respon: {kirim.text}")

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    main()