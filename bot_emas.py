import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# ==========================================
# KONFIGURASI BOT @XAU_Rosit_bot
# ==========================================
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q" 
CHAT_ID = "7425438429"

def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error kirim Telegram: {e}")

def run_analysis():
    # 1. CEK WAKTU (WIB)
    sekarang = datetime.now()
    hari_ini = sekarang.weekday() # 0=Senin, ..., 5=Sabtu, 6=Minggu
    jam_wib = (sekarang.hour + 7) % 24

    # 2. LOGIKA HARI LIBUR (SABTU & MINGGU)
    if hari_ini >= 5:
        pesan_libur = (
            f"🏝️ *Laporan Akhir Pekan - Bisnis Rosit*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📢 *STATUS:* PASAR SEDANG TUTUP\n"
            f"📅 Hari: {'Sabtu' if hari_ini == 5 else 'Minggu'}\n"
            f"⏰ Jam: {jam_wib}:00 WIB\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"☕ _Tenang saja, Bot tetap siaga di server. Siapkan mental dan modal untuk hari Senin pagi!_"
        )
        kirim_telegram(pesan_libur)
        return 

    # 3. AMBIL DATA EMAS (HARI KERJA)
    try:
        gold = yf.Ticker("GC=F")
        data = gold.history(period="30d", interval="1h") 
        
        if data.empty or len(data) < 20: return

        # ANALISA STRATEGI
        last_candle = data.iloc[-1]
        price_now = float(last_candle['Close'])
        high_all = float(data['High'].max())
        low_all = float(data['Low'].min())
        res_klasik = float(data['High'].iloc[-20:-1].max())
        sup_klasik = float(data['Low'].iloc[-20:-1].min())
        fib_618 = high_all - (0.382 * (high_all - low_all))
        
        is_active_market = 14 <= jam_wib <= 23
        status_market = "🔥 *Market Aktif*" if is_active_market else "💤 *Market Sideways*"
        
        sinyal_pesan = ""
        tolerance = 0.0010
        if abs(price_now - fib_618) / fib_618 <= tolerance:
            sinyal_pesan = (
                f"\n\n🚀 *SINYAL HIGH PROBABILITY*\n"
                f"📥 *Entry:* ${round(price_now, 2)}\n"
                f"🎯 *TP:* ${round(res_klasik, 2)}\n"
                f"🛡️ *SL:* ${round(price_now - 8, 2)}"
            )

        # LAPORAN PER JAM HARI KERJA
        laporan = (
            f"📊 *Laporan Bisnis Rosit*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Harga Emas: *${round(price_now, 2)}*\n"
            f"🏁 {status_market}\n"
            f"⏰ Jam: {jam_wib}:00 WIB\n"
            f"━━━━━━━━━━━━━━━━━━━━"
            f"{sinyal_pesan}"
        )
        kirim_telegram(laporan)

    except Exception as e:
        print(f"Kesalahan teknis: {e}")

if __name__ == "__main__":
    run_analysis()
