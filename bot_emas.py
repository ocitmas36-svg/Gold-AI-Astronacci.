import yfinance as yf
import requests
import pandas as pd
import pandas_ta as ta

# ==========================================
# KONFIGURASI BOT @XAU_Rosit_bot
# ==========================================
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q" 
CHAT_ID = "7425438429"

def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error kirim Telegram: {e}")

def run_analysis():
    print("AI sedang menganalisis konfluensi Fibonacci + RSI...")
    
    # 1. Ambil data Emas (GC=F)
    gold = yf.Ticker("GC=F")
    data = gold.history(period="20d", interval="1h")
    
    if data.empty or len(data) < 14: 
        print("Data tidak cukup.")
        return

    # 2. Hitung Indikator RSI (Periode 14) menggunakan pandas_ta
    data['RSI'] = ta.rsi(data['Close'], length=14)
    rsi_now = data['RSI'].iloc[-1]
    
    # 3. Hitung Level Fibonacci
    price_now = data['Close'].iloc[-1]
    high_p = data['High'].max()
    low_p = data['Low'].min()
    diff = high_p - low_p
    
    fib_618 = high_p - (0.382 * diff)
    fib_500 = high_p - (0.500 * diff)
    
    # 4. Filter Sinyal: Harga di Fib DAN RSI di bawah 35 (Oversold)
    tolerance = 0.0012
    status_msg = ""
    
    # Logika Entry di Golden Ratio (0.618)
    if abs(price_now - fib_618) / fib_618 <= tolerance and rsi_now < 35:
        entry = round(price_now, 2)
        tp = round(high_p, 2)
        sl = round(fib_618 - (0.006 * fib_618), 2)
        status_msg = (
            f"🔥 *SINYAL VALID: GOLDEN RATIO + RSI*\n"
            f"----------------------------------\n"
            f"📥 *Entry Buy:* ${entry}\n"
            f"🎯 *Take Profit:* ${tp}\n"
            f"🛡️ *Stop Loss:* ${sl}\n"
            f"📉 *RSI:* {rsi_now:.2f} (Oversold)"
        )

    # Logika Entry di Level 0.500
    elif abs(price_now - fib_500) / fib_500 <= tolerance and rsi_now < 30:
        entry = round(price_now, 2)
        tp = round(fib_618, 2)
        sl = round(fib_500 - (0.006 * fib_500), 2)
        status_msg = (
            f"⚡ *SINYAL AGRESIF: LEVEL 0.500*\n"
            f"----------------------------------\n"
            f"📥 *Entry Buy:* ${entry}\n"
            f"🎯 *Take Profit:* ${tp}\n"
            f"🛡️ *Stop Loss:* ${sl}\n"
            f"📉 *RSI:* {rsi_now:.2f} (Sangat Murah)"
        )

    # 5. Eksekusi
    if status_msg:
        pesan_final = (
            f"🔔 *ANALISIS PRO ROSIT*\n\n"
            f"{status_msg}\n\n"
            f"💰 Harga Saat Ini: ${price_now:.2f}\n"
            f"📍 Analisis: Konfluensi tercapai. Gas tipis-tipis!"
        )
        kirim_telegram(pesan_final)
        print("Sinyal Valid Terkirim!")
    else:
        print(f"Harga ${price_now:.2f} & RSI {rsi_now:.2f}. Belum ada konfluensi sinyal.")

if __name__ == "__main__":
    run_analysis()
