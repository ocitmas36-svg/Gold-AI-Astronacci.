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

def deteksi_hammer(open_p, close_p, high_p, low_p):
    """Logika mendeteksi lilin ekor panjang (Hammer)"""
    body = abs(close_p - open_p)
    lower_shadow = min(open_p, close_p) - low_p
    upper_shadow = high_p - max(open_p, close_p)
    # Hammer: Ekor bawah minimal 2x panjang badan, dan hampir tidak ada ekor atas
    return lower_shadow > (2 * body) and upper_shadow < (0.5 * body)

def run_analysis():
    gold = yf.Ticker("GC=F")
    data = gold.history(period="20d", interval="1h")
    
    if data.empty or len(data) < 20: return

    # Hitung Indikator
    data['RSI'] = hitung_rsi(data['Close'])
    
    # Ambil Data Terkini
    last_candle = data.iloc[-1]
    price_now = last_candle['Close']
    rsi_now = last_candle['RSI']
    
    # Deteksi Hammer
    is_hammer = deteksi_hammer(last_candle['Open'], last_candle['Close'], last_candle['High'], last_candle['Low'])
    
    # Hitung Fibonacci
    high_p = data['High'].max()
    low_p = data['Low'].min()
    diff = high_p - low_p
    fib_618 = high_p - (0.382 * diff)
    
    tolerance = 0.0015
    
    # KONFLUENSI TINGGI: Fib + RSI + Hammer
    if abs(price_now - fib_618) / fib_618 <= tolerance:
        status_lilin = "🔨 *Pola Hammer Terdeteksi!*" if is_hammer else "⏳ Menunggu Rejection Lilin..."
        
        # Kirim sinyal hanya jika RSI mendukung (Filter Keamanan)
        if rsi_now < 40:
            pesan = (
                f"🚀 *SINYAL KONFLUENSI ROSIT*\n"
                f"----------------------------------\n"
                f"📍 *Area:* Fibonacci 0.618\n"
                f"📉 *RSI:* {rsi_now:.2f}\n"
                f"{status_lilin}\n\n"
                f"📥 *Entry Buy:* ${round(price_now, 2)}\n"
                f"🎯 *Take Profit:* ${round(high_p, 2)}\n"
                f"🛡️ *Stop Loss:* ${round(fib_618 * 0.994, 2)}\n\n"
                f"⚠️ *Aksi:* Jika Hammer muncul, sinyal ini 90% Valid!"
            )
            kirim_telegram(pesan)

if __name__ == "__main__":
    run_analysis()
