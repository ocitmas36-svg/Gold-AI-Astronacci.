import yfinance as yf
import telebot
import pandas as pd
from datetime import datetime

# --- DATA RESMI ROSIT GOLD AI (MODE SCALPING) ---
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"
bot = telebot.TeleBot(TOKEN)

def analyze_market():
    # 1. Ambil data emas terbaru
    gold = yf.Ticker("GC=F")
    df = gold.history(period="2d", interval="1h")
    
    if df.empty or len(df) < 2:
        return "⚠️ Data pasar tidak tersedia atau pasar sedang libur."

    # 2. Ambil Harga & Data Teknis
    current_price = df['Close'].iloc[-1]
    high_24h = df['High'].max()
    low_24h = df['Low'].min()
    fibo_618 = high_24h - (0.618 * (high_24h - low_24h))

    # 3. Hitung TP dan SL Otomatis (MODE SCALPING - JARAK PENDEK)
    # Target Untung (TP) dibuat sekitar $8 dari harga saat ini
    tp_price = current_price + 8
    # Batas Rugi (SL) dibuat sekitar $5 di bawah harga saat ini
    sl_price = current_price - 5

    status = "WAIT AND SEE ⏳"
    trade_plan = "Belum ada rencana. Tunggu harga masuk area Fibo."
    reason = ""

    # 4. Logika Sinyal & Rencana Tempur
    if current_price <= fibo_618 * 1.001:
        status = "🚀 SINYAL BUY (SCALPING)"
        reason = "Harga masuk area Golden Ratio. Bagus untuk ambil untung cepat (Scalping)!"
        trade_plan = (
            f"✅ *ENTRY:* Buy di ${current_price:.2f}\n"
            f"🎯 *TARGET TP:* ${tp_price:.2f}\n"
            f"🛡️ *STOP LOSS:* ${sl_price:.2f}"
        )
    elif current_price >= high_24h * 0.999:
        status = "🔥 SINYAL SELL (PUNCAK)"
        reason = "Harga sudah dipuncak harian. Hati-hati koreksi turun."
        trade_plan = "❌ *JANGAN BUY:* Harga terlalu mahal."
    else:
        reason = "Harga berada di tengah. Sabar menunggu harga masuk ke area diskon Fibonacci."
        trade_plan = "😴 *SABAR:* Belum ada setup scalping yang aman."

    # 5. Susun Pesan Profesional
    waktu = datetime.now().strftime("%H:%M")
    message = (
        f"💰 *ROSIT GOLD AI (SCALPING MODE)*\n"
        f"📅 Jam: {waktu} WIB (Server Time)\n"
        f"💵 Harga Emas: *${current_price:.2f}*\n"
        f"📈 Level Fibo 61.8%: ${fibo_618:.2f}\n"
        f"----------------------------\n"
        f"📢 *STATUS:* {status}\n"
        f"🧐 *ANALISIS:* {reason}\n"
        f"----------------------------\n"
        f"📝 *TRADE PLAN SCALPING:*\n"
        f"{trade_plan}\n"
        f"----------------------------\n"
        f"💡 _Mode Scalping: Target lebih dekat, untung lebih cepat!_"
    )
    return message

if __name__ == "__main__":
    try:
        content = analyze_market()
        bot.send_message(CHAT_ID, content, parse_mode="Markdown")
        print("Laporan Scalping sukses terkirim!")
    except Exception as e:
        print(f"Gagal: {e}")
    
