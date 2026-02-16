import yfinance as yf
import telebot
import pandas as pd
from datetime import datetime

# --- DATA RESMI ROSIT GOLD AI ---
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

    # 3. Hitung TP dan SL Otomatis
    tp_price = high_24h  # Target ke puncak harian
    sl_price = low_24h - 5 # Batas rugi 5 point di bawah titik terendah

    status = "WAIT AND SEE ⏳"
    trade_plan = "Belum ada rencana. Tunggu harga masuk area Fibo."
    reason = ""

    # 4. Logika Sinyal & Rencana Tempur
    if current_price <= fibo_618 * 1.0005:
        status = "🚀 SINYAL BUY (ASTRONACCI)"
        reason = "Harga masuk area DISKON Golden Ratio. Titik pantul kuat!"
        trade_plan = (
            f"✅ *ENTRY:* Buy di ${current_price:.2f}\n"
            f"🎯 *TARGET (TP):* ${tp_price:.2f}\n"
            f"🛡️ *STOP LOSS (SL):* ${sl_price:.2f}"
        )
    elif current_price >= high_24h * 0.999:
        status = "🔥 SINYAL SELL (RESISTANCE)"
        reason = "Harga sudah dipuncak harian. Sangat berbahaya untuk beli sekarang."
        trade_plan = "❌ *JANGAN BUY:* Harga terlalu mahal, rawan longsor."
    else:
        if current_price > fibo_618:
            reason = "Harga masih 'menggantung' di area nanggung. Risiko lebih besar dari potensi untung."
        else:
            reason = "Menunggu konfirmasi pola pantulan yang jelas."
        trade_plan = "😴 *SABAR:* Belum ada setup yang aman."

    # 5. Susun Pesan Profesional
    waktu = datetime.now().strftime("%H:%M")
    message = (
        f"💰 *ROSIT GOLD AI REPORT*\n"
        f"📅 Jam: {waktu} WIB (Server Time)\n"
        f"💵 Harga Emas: *${current_price:.2f}*\n"
        f"📈 Level Fibo 61.8%: ${fibo_618:.2f}\n"
        f"----------------------------\n"
        f"📢 *STATUS:* {status}\n"
        f"🧐 *ANALISIS:* {reason}\n"
        f"----------------------------\n"
        f"📝 *TRADE PLAN ROSIT:*\n"
        f"{trade_plan}\n"
        f"----------------------------\n"
        f"💡 _Selalu gunakan Lot kecil (0.01) untuk menjaga modal._"
    )
    return message

if __name__ == "__main__":
    try:
        content = analyze_market()
        bot.send_message(CHAT_ID, content, parse_mode="Markdown")
        print("Laporan Trade Plan sukses terkirim!")
    except Exception as e:
        print(f"Gagal: {e}")
