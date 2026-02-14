import yfinance as yf
import requests
import pandas as pd

# ==========================================
# KONFIGURASI BOT @XAU_Rosit_bot
# ==========================================
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q" 
CHAT_ID = "7425438429"

def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def hitung_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def run_analysis():
    print("AI Rosit sedang memindai pasar...")
    gold = yf.Ticker("GC=F")
    data = gold.history(period="20d", interval="1h")
    
    if data.empty or len(data) < 20: 
        print("Data belum siap.")
        return

    # Hitung RSI secara manual agar tidak butuh library tambahan yang berat
    data['RSI'] = hitung_rsi(data['Close'])
    rsi_now = data['RSI'].iloc[-1]
    
    # Ambil Harga & Fibonacci
    price_now = data['Close'].iloc[-1]
    high_p = data['High'].max()
    low_p = data['Low'].min()
    diff = high_p - low_p
    
    fib_618 = high_p - (0.382 * diff)
    fib_500 = high_p - (0.500 * diff)
    
    tolerance = 0.0012 # Toleransi harga 0.12%
    status_msg = ""

    # STRATEGI: Fibonacci + RSI Oversold (< 35)
    if abs(price_now - fib_618) / fib_618 <= tolerance and rsi_now < 35:
        sl = round(fib_618 - (0.006 * fib_618), 2)
        status_msg = (
            f"🔥 *SINYAL VALID: GOLDEN RATIO*\n"
            f"📥 *Entry Buy:* ${round(price_now, 2)}\n"
            f"🎯 *Take Profit:* ${round(high_p, 2)}\n"
            f"🛡️ *Stop Loss:* ${sl}\n"
            f"📉 *RSI:* {rsi_now:.2f}"
        )

    if status_msg:
        kirim_telegram(f"🔔 *ANALISIS PRO ROSIT*\n\n{status_msg}")
        print("Sinyal terkirim!")
    else:
        print(f"Harga ${price_now:.2f} (RSI: {rsi_now:.2f}) belum masuk zona entry.")

if __name__ == "__main__":
    run_analysis()
