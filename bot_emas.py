import yfinance as yf
import requests
import pandas as pd
from datetime import datetime

# ==========================================
# KONFIGURASI BOT @XAU_Rosit_bot
# ==========================================
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q" 
CHAT_ID = "7425438429"

def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def run_analysis():
    gold = yf.Ticker("GC=F")
    data = gold.history(period="30d", interval="1h") # Data lebih panjang untuk SNR
    
    if data.empty or len(data) < 20: return

    # 1. Ambil Level Penting
    last_candle = data.iloc[-1]
    price_now = last_candle['Close']
    high_all = data['High'].max()
    low_all = data['Low'].min()
    
    # 2. Support & Resistance Klasik (Pivot Points)
    res_klasik = data['High'].iloc[-20:-1].max() # Resistance 20 jam terakhir
    sup_klasik = data['Low'].iloc[-20:-1].min()  # Support 20 jam terakhir
    
    # 3. Fibonacci 0.618
    fib_618 = high_all - (0.382 * (high_all - low_all))
    
    # 4. Filter Waktu (WIB)
    hour_now = datetime.now().hour + 7 # Penyesuaian ke WIB
    is_active_market = 14 <= hour_now <= 23 # Jam aktif London & NY
    
    status_market = "🔥 *Market Aktif (High Volatility)*" if is_active_market else "💤 *Market Sideways*"
    
    # LOGIKA AKURASI TINGGI: Fib bertemu Support Klasik
    tolerance = 0.0010
    if abs(price_now - fib_618) / fib_618 <= tolerance:
        # Cek apakah ada Support Klasik di dekat situ
        konfluensi_snr = "✅ *Konfirmasi Support Klasik Ditemukan!*" if abs(price_now - sup_klasik) / sup_klasik <= 0.002 else ""
        
        pesan = (
            f"🏆 *SINYAL HIGH PROBABILITY*\n"
            f"----------------------------------\n"
            f"{status_market}\n\n"
            f"📍 *Level:* Fibonacci 0.618\n"
            f"{konfluensi_snr}\n\n"
            f"📥 *Entry Buy:* ${round(price_now, 2)}\n"
            f"🎯 *Take Profit:* ${round(res_klasik, 2)}\n"
            f"🛡️ *Stop Loss:* ${round(price_now - 8, 2)}\n\n"
            f"💪 *Confidence:* Tinggi (Astronacci + SNR)"
        )
        kirim_telegram(pesan)

if __name__ == "__main__":
    run_analysis()
