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
    
    if df.empty or len(df) < 5:
        return "⚠️ Data pasar sedang tidak tersedia. Pasar mungkin sedang tutup."

    # 2. Data Harga & Fibonacci
    current_price = df['Close'].iloc[-1]
    high_24h = df['High'].max()
    low_24h = df['Low'].min()
    fibo_618 = high_24h - (0.618 * (high_24h - low_24h))

    # 3. Logika Sederhana untuk Analisis (Tanpa RSI agar tidak error)
    status = "WAIT AND SEE ⏳"
    reason = ""

    # Cek Kondisi Sinyal
    if current_price <= fibo_618 * 1.0005:
        status = "🚀 SINYAL BUY (ASTRONACCI)"
        reason = "Harga sudah menyentuh area diskon Fibonacci 0.618. Ini adalah titik pantulan yang kuat secara teknis!"
    elif current_price >= high_24h * 0.999:
        status = "🔥 SINYAL SELL (RESISTANCE)"
        reason = "Harga sudah terlalu dekat dengan puncak tertinggi harian. Sangat berisiko untuk Buy, potensi koreksi turun sangat besar."
    else:
        # Penjelasan kenapa jangan entry
        if current_price > fibo_618:
            reason = "Harga masih menggantung di area 'tengah-tengah'. Belum cukup murah untuk Buy, tapi tanggung untuk Sell. Lebih baik sabar daripada rugi."
        else:
            reason = "Kondisi pasar sedang tidak menentu. Belum ada konfirmasi pola yang jelas sesuai standar trading kita."

    # 4. Susun Pesan
    waktu = datetime.now().strftime("%H:%M")
    message = (
        f"💰 *LAPORAN BISNIS ROSIT*\n"
        f"📅 Jam: {waktu} WIB (Server Time)\n"
        f"💵 Harga Emas: *${current_price:.2f}*\n"
        f"📈 Level Fibo 61.8%: ${fibo_618:.2f}\n"
        f"----------------------------\n"
        f"📢 *STATUS: {status}*\n"
        f"🧐 *ANALISIS:* {reason}\n"
        f"----------------------------\n"
        f"💡 _Pesan otomatis: Menjaga modal lebih penting daripada mencari profit paksa._"
    )
    return message

if __name__ == "__main__":
    try:
        content = analyze_market()
        bot.send_message(CHAT_ID, content, parse_mode="Markdown")
        print("Laporan berhasil dikirim!")
    except Exception as e:
        print(f"Error: {e}")
