import yfinance as yf
import telebot
import pandas as pd
from datetime import datetime

# --- KONFIGURASI BOT ---
TOKEN = "7963242048:AAHOf8G_XhYv1Wp6v8_V3E4H-9Yt8T0A2F8"
CHAT_ID = "1430030501"
bot = telebot.TeleBot(TOKEN)

def analyze_market():
    # 1. Ambil data emas
    gold = yf.Ticker("GC=F")
    df = gold.history(period="2d", interval="1h")
    
    if df.empty:
        return "⚠️ Data pasar tidak tersedia saat ini."

    # 2. Data Harga & Fibonacci sederhana
    current_price = df['Close'].iloc[-1]
    high_24h = df['High'].max()
    low_24h = df['Low'].min()
    fibo_618 = high_24h - (0.618 * (high_24h - low_24h))

    status = "WAIT AND SEE ⏳"
    reason = ""

    # 3. Logika Analisis Astronacci & Penyebab Jangan Entry
    if current_price <= fibo_618 * 1.001:
        status = "🚀 SINYAL BUY (ASTRONACCI)"
        reason = "Harga sudah masuk area Golden Ratio 61.8%. Ini momen beli terbaik karena harga sudah cukup murah."
    elif current_price >= high_24h * 0.999:
        status = "🔥 SINYAL SELL (RESISTANCE)"
        reason = "Harga berada di puncak tertinggi harian. Sangat berisiko untuk beli sekarang, potensi koreksi turun sangat besar."
    else:
        # Alasan kenapa jangan entry
        if current_price > fibo_618:
            reason = "Harga masih di area 'tanggung'. Belum masuk harga diskon Fibonacci, risiko rugi lebih besar daripada potensi untung."
        else:
            reason = "Belum ada konfirmasi pola yang kuat. Dalam trading, menunggu momen yang pas adalah bagian dari profit."

    # 4. Susun Pesan
    waktu = datetime.now().strftime("%H:%M")
    message = (
        f"💰 *LAPORAN BISNIS ROSIT*\n"
        f"📅 Jam: {waktu} WIB (Server Time)\n"
        f"💵 Harga Emas: *${current_price:.2f}*\n"
        f"----------------------------\n"
        f"📢 *STATUS: {status}*\n"
        f"🧐 *ANALISIS:* {reason}\n"
        f"----------------------------\n"
        f"💡 _Menjaga modal lebih penting daripada entry yang dipaksakan._"
    )
    return message

if __name__ == "__main__":
    try:
        content = analyze_market()
        bot.send_message(CHAT_ID, content, parse_mode="Markdown")
        print("Laporan berhasil dikirim!")
    except Exception as e:
        print(f"Error: {e}")
