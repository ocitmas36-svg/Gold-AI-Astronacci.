import yfinance as yf
import telebot
import pandas as pd
from datetime import datetime

# --- KONFIGURASI BOT ---
TOKEN = "7963242048:AAHOf8G_XhYv1Wp6v8_V3E4H-9Yt8T0A2F8"
CHAT_ID = "1430030501"
bot = telebot.TeleBot(TOKEN)

def analyze_market():
    # Ambil data emas
    gold = yf.Ticker("GC=F")
    df = gold.history(period="2d", interval="1h")
    
    if df.empty:
        return "⚠️ Data pasar tidak tersedia saat ini."

    current_price = df['Close'].iloc[-1]
    high_24h = df['High'].max()
    low_24h = df['Low'].min()
    fibo_618 = high_24h - (0.618 * (high_24h - low_24h))

    status = "WAIT AND SEE ⏳"
    reason = "Harga sedang di tengah-tengah. Belum ada momen bagus sesuai strategi Astronacci."

    if current_price <= fibo_618 * 1.001:
        status = "🚀 SINYAL BUY (ASTRONACCI)"
        reason = "Harga masuk area Golden Ratio 0.618. Ini harga murah untuk beli!"
    elif current_price >= high_24h * 0.999:
        status = "🔥 SINYAL SELL (RESISTANCE)"
        reason = "Harga sudah dipuncak tertinggi harian. Terlalu berisiko buat beli sekarang."

    waktu = datetime.now().strftime("%H:%M")
    message = (
        f"💰 *LAPORAN BISNIS ROSIT*\n"
        f"📅 Jam: {waktu} WIB\n"
        f"💵 Harga: *${current_price:.2f}*\n"
        f"----------------------------\n"
        f"📢 *STATUS: {status}*\n"
        f"🧐 *ANALISIS:* {reason}\n"
        f"----------------------------\n"
        f"💡 _Menjaga modal adalah kunci profit._"
    )
    return message

if __name__ == "__main__":
    try:
        content = analyze_market()
        bot.send_message(CHAT_ID, content, parse_mode="Markdown")
        print("Sukses!")
    except Exception as e:
        print(f"Error: {e}")
