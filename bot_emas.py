import yfinance as yf
import telebot
import pandas as pd
from datetime import datetime
import pytz

# --- KONFIGURASI BOT ---
TOKEN = "7963242048:AAHOf8G_XhYv1Wp6v8_V3E4H-9Yt8T0A2F8"
CHAT_ID = "1430030501"
bot = telebot.TeleBot(TOKEN)

def get_gold_data():
    try:
        # Mengambil data emas (XAU/USD) dari Yahoo Finance
        gold = yf.Ticker("GC=F")
        df = gold.history(period="2d", interval="1h")
        return df
    except Exception as e:
        print(f"Gagal ambil data: {e}")
        return pd.DataFrame()

def analyze_market():
    df = get_gold_data()
    if df.empty or len(df) < 5:
        return "⚠️ Data pasar sedang tidak tersedia saat ini. Coba lagi nanti."

    # Data Harga Terakhir
    current_price = df['Close'].iloc[-1]
    high_24h = df['High'].max()
    low_24h = df['Low'].min()
    
    # Hitung Fibonacci Retracement (0.618) ala Astronacci
    diff = high_24h - low_24h
    fibo_618 = high_24h - (0.618 * diff)
    
    # Indikator RSI Sederhana (14 period)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs.iloc[-1]))

    # Penentuan Waktu WIB
    timezone = pytz.timezone('Asia/Jakarta')
    waktu_sekarang = datetime.now(timezone).strftime("%H:%M")

    # LOGIKA ANALISIS & PENYEBAB JANGAN ENTRY
    status = "WAIT AND SEE ⏳"
    reason = ""
    
    # Kondisi Sinyal Buy
    if current_price <= fibo_618 * 1.0005: # Jika harga di area 0.618
        status = "🚀 SINYAL BUY (ASTRONACCI)"
        reason = "Harga masuk area Golden Ratio 0.618. Secara teknis, ini adalah titik pantulan naik yang kuat."
    
    # Kondisi Sinyal Sell
    elif rsi > 70:
        status = "🔥 SINYAL SELL (OVERBOUGHT)"
        reason = "Harga sudah terlalu mahal (RSI > 70). Berisiko besar jika maksa Buy sekarang, potensi koreksi turun."

    # Kondisi Kenapa JANGAN Entry (The "Why" Logic)
    else:
        if 45 <= rsi <= 55:
            reason = "Pasar sedang Sideways (datar). Tidak ada tenaga dorongan besar, jika entry sekarang uang kamu hanya akan terombang-ambing tanpa arah."
        elif current_price > fibo_618:
            reason = "Harga berada di area 'tengah-tengah' (No Man's Land). Belum masuk ke diskon Fibonacci, risiko rugi lebih besar daripada potensi untung."
        else:
            reason = "Belum ada pola konfirmasi yang kuat. Dalam trading, diam adalah posisi terbaik daripada membuang modal."

    # Susun Pesan Profesional
    message = (
        f"💰 *LAPORAN BISNIS ROSIT*\n"
        f"📅 Jam: {waktu_sekarang} WIB\n"
        f"💵 Harga Emas: *${current_price:.2f}*\n"
        f"📈 Level Fibo 61.8%: ${fibo_618:.2f}\n"
        f"📊 RSI: {rsi:.1f}\n"
        f"----------------------------\n"
        f"📢 *STATUS: {status}*\n"
        f"🧐 *ANALISIS:* {reason}\n"
        f"----------------------------\n"
        f"💡 _Pesan ini otomatis dikirim setiap jam untuk memantau kemajuan bisnismu._"
    )
    
    return message

if __name__ == "__main__":
    try:
        content = analyze_market()
        bot.send_message(CHAT_ID, content, parse_mode="Markdown")
        print(f"Laporan berhasil dikirim ke Rosit pada jam {datetime.now()}")
    except Exception as e:
        print(f"Terjadi kesalahan saat kirim bot: {e}")
