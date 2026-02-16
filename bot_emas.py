import yfinance as yf
import telebot
import pandas as pd
from datetime import datetime

# --- KONFIGURASI TERBARU (TOKEN UPDATE) ---
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "1430030501"
bot = telebot.TeleBot(TOKEN)

def analyze_market():
    # 1. Ambil data emas
    gold = yf.Ticker("GC=F")
    df = gold.history(period="2d", interval="1h")
    
    if df.empty:
        return "⚠️ Data pasar tidak tersedia. Mungkin pasar sedang tutup."

    # 2. Ambil Harga & Level Fibonacci
    current_price = df['Close'].iloc[-1]
    high_24h = df['High'].max()
    low_24h = df['Low'].min()
    fibo_618 = high_24h - (0.618 * (high_24h - low_24h))

    status = "WAIT AND SEE ⏳"
    reason = ""

    # 3. Logika Analisis & Penyebab
    if current_price <= fibo_618 * 1.001:
        status = "🚀 SINYAL BUY (ASTRONACCI)"
        reason = "Harga masuk area Golden Ratio 0.618. Ini harga murah untuk beli!"
    elif current_price >= high_24h * 0.999:
        status = "🔥 SINYAL SELL (RESISTANCE)"
        reason = "Harga sudah dipuncak tertinggi harian. Terlalu berisiko buat beli sekarang."
    else:
        if current_price > fibo_618:
            reason = "Harga masih di area 'tanggung'. Belum cukup murah untuk beli, tapi terlalu nanggung untuk jual."
        else:
            reason = "Belum ada konfirmasi pola yang kuat. Menunggu momen yang pas adalah bagian dari profit."

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
        f"💡 _Pesan ini otomatis dikirim setiap jam._"
    )
    return message

if __name__ == "__main__":
    try:
        content = analyze_market()
        bot.send_message(CHAT_ID, content, parse_mode="Markdown")
        print("Laporan sukses dikirim dengan TOKEN BARU!")
    except Exception as e:
        print(f"Error: {e}")
