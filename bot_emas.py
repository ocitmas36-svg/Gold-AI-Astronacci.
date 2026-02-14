import yfinance as yf
import requests
import pandas as pd

# ==========================================
# KONFIGURASI BOT
# ==========================================
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q" 
CHAT_ID = "7425438429"

def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def run_analysis():
    gold = yf.Ticker("GC=F")
    # Ambil data lebih panjang (20 hari) untuk swing high/low yang lebih valid
    data = gold.history(period="20d", interval="1h")
    
    if data.empty: return

    price_now = data['Close'].iloc[-1]
    high_p = data['High'].max()
    low_p = data['Low'].min()
    diff = high_p - low_p
    
    # Hitung Level Astronacci
    fib_618 = high_p - (0.382 * diff)
    fib_500 = high_p - (0.500 * diff)
    
    # Logika Entry Strategy (Buy on Retracement)
    # Kita cari posisi buy saat harga turun ke area Golden Ratio
    tolerance = 0.0010 # Toleransi 0.1%
    
    if abs(price_now - fib_618) / fib_618 <= tolerance:
        # STRATEGI ENTRY
        entry_price = round(price_now, 2)
        tp = round(high_p, 2) # TP di High sebelumnya
        sl = round(fib_618 - (0.005 * fib_618), 2) # SL 0.5% di bawah entry
        
        pesan = (
            f"🚀 *SINYAL ENTRY EMAS @ya_rositt*\n"
            f"----------------------------------\n"
            f"🔥 *Status:* Area Golden Ratio 0.618\n\n"
            f"📥 *Entry Buy:* ${entry_price}\n"
            f"🎯 *Take Profit:* ${tp}\n"
            f"🛡️ *Stop Loss:* ${sl}\n\n"
            f"⚠️ *Note:* Gunakan Lot aman (Money Management). "
            f"Pastikan ada rejection (ekor candle bawah) di H1!"
        )
        kirim_telegram(pesan)
    
    elif abs(price_now - fib_500) / fib_500 <= tolerance:
        entry_price = round(price_now, 2)
        tp = round(fib_618, 2)
        sl = round(fib_500 - (0.005 * fib_500), 2)
        
        pesan = (
            f"⚡ *SINYAL ENTRY (AGRESIF)*\n"
            f"----------------------------------\n"
            f"⚠️ *Status:* Level Psikologis 0.500\n\n"
            f"📥 *Entry Buy:* ${entry_price}\n"
            f"🎯 *Take Profit:* ${tp}\n"
            f"🛡️ *Stop Loss:* ${sl}\n\n"
            f"Pantau terus, Bos Rosit!"
        )
        kirim_telegram(pesan)

if __name__ == "__main__":
    run_analysis()
