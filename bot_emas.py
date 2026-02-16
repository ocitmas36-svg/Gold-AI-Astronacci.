import yfinance as yf
import telebot
import pandas as pd
from datetime import datetime

# --- KONFIGURASI ---
TOKEN = "7963242048:AAHOf8G_XhYv1Wp6v8_V3E4H-9Yt8T0A2F8"
CHAT_ID = "1430030501"
bot = telebot.TeleBot(TOKEN)

def analyze_market():
    # Ambil data emas (Gold Futures)
    gold = yf.Ticker("GC=F")
    df = gold.history(period="2d", interval="1h")
    
    if df.empty:
        return "⚠️ Data pasar tidak tersedia."

    # Harga saat ini dan Fibonacci 0.618
    current_price = df['Close'].iloc[-1]
    high_24h = df['High'].max()
    low_24h = df['Low'].min()
    fibo_618 = high_24h - (0.618 * (high_24h - low_24h))

    status = "WAIT AND SEE ⏳"
    reason = ""

    # Logika Astronacci & Alasan
    if current_price <= fibo_618 * 1.001:
        status = "🚀 SINYAL BUY (ASTRONACCI)"
        reason = "Harga sudah menyentuh Golden Ratio 0.618. Ini adalah area 'diskon' terbaik untuk melakukan pembelian."
    elif current_price >= high_24h * 0.999:
        status = "🔥 SINYAL SELL (RESISTANCE)"
        reason = "Harga sudah dipuncak tertinggi. Sangat berisiko untuk beli sekarang, rawan koreksi turun tajam."
    else:
        # Penjelasan kenapa jangan entry
        if current_price > fibo_618:
            reason = "Harga masih 'menggantung' di tengah. Belum cukup murah untuk beli, tapi terlalu tanggung untuk jual. Sabar adalah bagian dari profit."
        else:
            reason = "Pergerakan harga belum mengonfirmasi pola pantulan yang kuat. Lebih baik menunggu daripada terjebak."

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
        f"💡 _Jangan dipaksa, pasar emas selalu buka setiap hari._"
    )
    return message

if __name__ == "__main__":
    try:
        content = analyze_market()
        bot.send_message(CHAT_ID, content, parse_mode="Markdown")
        print("Laporan berhasil terkirim!")
    except Exception as e:
        print(f"Error: {e}")
