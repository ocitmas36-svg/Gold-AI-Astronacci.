import yfinance as yf
import telebot
import pandas as pd
import os
from datetime import datetime

# Konfigurasi Bot
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN" # Ganti dengan Token kamu
CHAT_ID = "YOUR_CHAT_ID" # Ganti dengan Chat ID kamu
bot = telebot.TeleBot(TOKEN)

def get_gold_data():
    # Mengambil data emas (XAU/USD)
    gold = yf.Ticker("GC=F")
    df = gold.history(period="5d", interval="1h")
    return df

def analyze_market():
    df = get_gold_data()
    if df.empty:
        return "Data tidak tersedia"

    current_price = df['Close'].iloc[-1]
    high_price = df['High'].max()
    low_price = df['Low'].min()
    
    # Hitung Fibonacci Retracement (0.618)
    diff = high_price - low_price
    fibo_618 = high_price - (0.618 * diff)
    
    # Indikator Sederhana untuk Alasan (RSI Standar)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs.iloc[-1]))

    # Logika Sinyal Astronacci
    status = "WAIT AND SEE ⏳"
    reason = ""
    signal_msg = ""

    # 1. Cek Sinyal Buy
    if current_price <= fibo_618 * 1.001: # Toleransi 0.1%
        status = "🚀 SINYAL BUY (ASTRONACCI)"
        reason = "Harga menyentuh Golden Ratio Fibonacci 0.618. Potensi pantulan naik sangat besar!"
    # 2. Cek Sinyal Sell (Jika RSI Jenuh Beli)
    elif rsi > 70:
        status = "🔥 SINYAL SELL (OVERBOUGHT)"
        reason = "Harga sudah terlalu mahal (RSI > 70). Waktunya ambil untung atau cari posisi turun."
    # 3. Kondisi Jangan Entry
    else:
        if rsi > 45 and rsi < 55:
            reason = "Pasar sedang Sideways (datar). Memaksakan entry sekarang berisiko terjebak di harga yang sama dalam waktu lama."
        elif current_price > fibo_618:
            reason = "Harga berada di area 'No Man's Land' (tengah-tengah). Terlalu jauh dari level Fibonacci 0.618, risiko rugi lebih besar dari potensi untung."
        else:
            reason = "Volume pasar rendah atau pola belum terkonfirmasi sesuai standar Astronacci."

    # Susun Pesan
    waktu = datetime.now().strftime("%H:%M")
    message = (
        f"💰 *LAPORAN BISNIS ROSIT*\n"
        f"📅 Jam: {waktu} WIB\n"
        f"💵 Harga Emas: *${current_price:.2f}*\n"
        f"📈 Fibo 61.8%: ${fibo_618:.2f}\n"
        f"📊 RSI: {rsi:.2f}\n"
        f"----------------------------\n"
        f"📢 *STATUS: {status}*\n"
        f"🧐 *ANALISIS:* {reason}\n"
        f"----------------------------\n"
        f"💡 _Tetap disiplin pada plan, Rosit!_"
    )
    
    return message

if __name__ == "__main__":
    try:
        pesan = analyze_market()
        bot.send_message(CHAT_ID, pesan, parse_mode="Markdown")
        print("Laporan berhasil dikirim!")
    except Exception as e:
        print(f"Error: {e}")
