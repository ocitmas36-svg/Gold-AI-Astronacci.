import yfinance as yf
import telebot
import pandas as pd
from datetime import datetime

# --- DATA RESMI ROSIT GOLD AI ---
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "1430030501"
bot = telebot.TeleBot(TOKEN)

def analyze_market():
    # 1. Ambil data emas terbaru
    gold = yf.Ticker("GC=F")
    df = gold.history(period="2d", interval="1h")
    
    if df.empty:
        return "⚠️ Data pasar tidak tersedia. Coba lagi beberapa saat lagi."

    # 2. Ambil Harga Terakhir & Hitung Fibonacci 61.8%
    current_price = df['Close'].iloc[-1]
    high_24h = df['High'].max()
    low_24h = df['Low'].min()
    fibo_618 = high_24h - (0.618 * (high_24h - low_24h))

    status = "WAIT AND SEE ⏳"
    reason = ""

    # 3. Logika Analisis & Penyebab (Astronacci Based)
    if current_price <= fibo_618 * 1.0005:
        status = "🚀 SINYAL BUY (ASTRONACCI)"
        reason = "Harga sudah masuk area DISKON Golden Ratio 0.618. Ini momen beli terbaik karena harga sudah cukup murah secara teknis."
    elif current_price >= high_24h * 0.999:
        status = "🔥 SINYAL SELL (RESISTANCE)"
        reason = "Harga berada di puncak tertinggi harian. Terlalu berisiko buat beli sekarang, potensi koreksi turun sangat besar."
    else:
        # Penjelasan kenapa jangan entry
        if current_price > fibo_618:
            reason = "Harga masih 'mengambang' di area nanggung. Belum masuk harga diskon Fibonacci, risiko rugi lebih besar daripada potensi untung."
        else:
            reason = "Kondisi pasar sedang tidak menentu. Belum ada konfirmasi pola pantulan yang jelas. Sabar adalah bagian dari profit."

    # 4. Susun Pesan Profesional
    waktu = datetime.now().strftime("%H:%M")
    message = (
        f"💰 *ROSIT GOLD AI REPORT*\n"
        f"🤖 Bot: @XAU_Rosit_bot\n"
        f"📅 Jam: {waktu} WIB (Server Time)\n"
        f"💵 Harga Emas: *${current_price:.2f}*\n"
        f"📈 Level Fibo 61.8%: ${fibo_618:.2f}\n"
        f"----------------------------\n"
        f"📢 *STATUS: {status}*\n"
        f"🧐 *ANALISIS:* {reason}\n"
        f"----------------------------\n"
        f"💡 _Menjaga modal lebih penting daripada mencari profit yang dipaksakan._"
    )
    return message

if __name__ == "__main__":
    try:
        content = analyze_market()
        bot.send_message(CHAT_ID, content, parse_mode="Markdown")
        print("Laporan sukses terkirim ke @XAU_Rosit_bot!")
    except Exception as e:
        print(f"Error: {e}")
