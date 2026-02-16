import yfinance as yf
import telebot
import pandas as pd
from datetime import datetime

# --- DATA RESMI ROSIT GOLD AI (UPDATED ID) ---
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"  # ID asli Rosit yang baru
bot = telebot.TeleBot(TOKEN)

def analyze_market():
    # 1. Ambil data emas terbaru
    gold = yf.Ticker("GC=F")
    df = gold.history(period="2d", interval="1h")
    
    if df.empty:
        return "⚠️ Data pasar tidak tersedia. Coba lagi nanti."

    # 2. Ambil Harga & Fibonacci 0.618
    current_price = df['Close'].iloc[-1]
    high_24h = df['High'].max()
    low_24h = df['Low'].min()
    fibo_618 = high_24h - (0.618 * (high_24h - low_24h))

    status = "WAIT AND SEE ⏳"
    reason = ""

    # 3. Logika Analisis & Penyebab
    if current_price <= fibo_618 * 1.0005:
        status = "🚀 SINYAL BUY (ASTRONACCI)"
        reason = "Harga masuk area DISKON Golden Ratio 0.618. Ini momen beli terbaik karena harga sudah murah secara teknis."
    elif current_price >= high_24h * 0.999:
        status = "🔥 SINYAL SELL (RESISTANCE)"
        reason = "Harga berada di puncak tertinggi harian. Sangat berisiko buat beli sekarang, rawan koreksi turun."
    else:
        # Penjelasan kenapa jangan entry
        if current_price > fibo_618:
            reason = "Harga masih di area 'tanggung'. Belum masuk harga diskon Fibonacci, risiko rugi lebih besar daripada potensi untung."
        else:
            reason = "Belum ada konfirmasi pola yang kuat. Menunggu momen yang pas adalah bagian dari profit."

    # 4. Susun Pesan
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
        f"💡 _Disiplin adalah kunci sukses trading, Rosit!_"
    )
    return message

if __name__ == "__main__":
    try:
        content = analyze_market()
        bot.send_message(CHAT_ID, content, parse_mode="Markdown")
        print(f"Laporan sukses dikirim ke ID {CHAT_ID}!")
    except Exception as e:
        print(f"Gagal: {e}")
