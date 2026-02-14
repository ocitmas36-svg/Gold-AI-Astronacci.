import yfinance as yf
import requests
import pandas as pd

# ==========================================
# KONFIGURASI BOT (SUDAH DISESUAIKAN)
# ==========================================
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q" 
CHAT_ID = "7425438429"

def kirim_telegram(pesan):
    """Fungsi untuk mengirim pesan ke Telegram @XAU_Rosit_bot"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": pesan,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Gagal mengirim pesan: {e}")

def run_analysis():
    print("Memulai analisis pasar XAU/USD (Gold)...")
    
    # 1. Ambil data Emas dari Yahoo Finance
    # GC=F adalah Gold Futures, standar untuk harga emas dunia
    ticker = "GC=F"
    gold = yf.Ticker(ticker)
    
    # Ambil data 14 hari terakhir dengan interval 1 jam
    data = gold.history(period="14d", interval="1h")
    
    if data.empty or len(data) < 20:
        print("Data tidak cukup atau pasar sedang tutup (Weekend).")
        return

    # 2. Ambil harga saat ini dan hitung High/Low periode ini
    price_now = data['Close'].iloc[-1]
    high_period = data['High'].max()
    low_period = data['Low'].min()
    diff = high_period - low_period
    
    # 3. Rumus Fibonacci Retracement (Logika Astronacci)
    fib_618 = high_period - (0.382 * diff)  # Golden Ratio 0.618
    fib_500 = high_period - (0.500 * diff)  # Middle Level 0.500
    fib_382 = high_period - (0.618 * diff)  # Level 0.382
    
    # 4. Deteksi Sinyal (Toleransi 0.15% dari harga agar akurat)
    alert_msg = ""
    tolerance = 0.0015 
    
    if abs(price_now - fib_618) / fib_618 <= tolerance:
        alert_msg = "🔥 *GOLDEN RATIO 0.618!* (Area Reversal Kuat)"
    elif abs(price_now - fib_500) / fib_500 <= tolerance:
        alert_msg = "⚠️ *LEVEL PSIKOLOGIS 0.500* (Pantauan Rebound)"
    elif abs(price_now - fib_382) / fib_382 <= tolerance:
        alert_msg = "✳️ *LEVEL FIBONACCI 0.382* (Koreksi Normal)"

    # 5. Eksekusi Pengiriman Notifikasi
    if alert_msg:
        pesan_final = (
            f"🔔 *SINYAL EMAS ROSIT*\n"
            f"----------------------------\n"
            f"{alert_msg}\n\n"
            f"💰 *Harga:* ${price_now:.2f}\n"
            f"📈 *High (14hr):* ${high_period:.2f}\n"
            f"📉 *Low (14hr):* ${low_period:.2f}\n\n"
            f"📍 *Analisis:* Harga menyentuh level penting Astronacci. "
            f"Cek chart di HP sekarang!"
        )
        kirim_telegram(pesan_final)
        print("Pesan terkirim ke Telegram!")
    else:
        # Jika tidak ada sinyal, hanya cetak di log GitHub
        print(f"Harga saat ini ${price_now:.2f} belum masuk zona Fibonacci.")

if __name__ == "__main__":
    run_analysis()
