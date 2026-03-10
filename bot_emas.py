import requests
from datetime import datetime
import pytz
import os
import csv

# ==========================================
# 1. KONFIGURASI API & TOKEN
# ==========================================
# Ganti teks di dalam tanda kutip dengan milikmu jika tidak pakai Environment Variables
TELE_TOKEN = os.getenv("TELE_TOKEN") or "GANTI_DENGAN_TOKEN_BOT_TELEGRAM_KAMU"
CHAT_ID = os.getenv("CHAT_ID") or "GANTI_DENGAN_CHAT_ID_KAMU"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "GANTI_DENGAN_API_KEY_GEMINI_KAMU"

# URL FormResponse Google Sheets milik Rosit
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSf4cF9UwXaPEuSHFVcL36LvDSrBk41H4c_8n9810uMllAG49g/formResponse"

# ==========================================
# 2. FUNGSI DATABASE (LOKAL & CLOUD)
# ==========================================
def simpan_log_hp(waktu, harga, rsi_m1, rsi_h1, signal):
    """Mencatat histori ke file CSV di memori HP"""
    file_exists = os.path.isfile('history_trading.csv')
    try:
        with open('history_trading.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Waktu', 'Harga', 'RSI_M1', 'RSI_H1', 'Sinyal'])
            writer.writerow([waktu, harga, rsi_m1, rsi_h1, signal])
    except Exception as e:
        print(f"⚠️ Gagal simpan CSV Lokal: {e}")

def simpan_ke_google_sheets(waktu, harga, rsi_m1, rsi_h1, signal):
    """Mengirim data ke Google Sheets via Google Form (Cloud)"""
    payload = {
        "entry.497131546": waktu,
        "entry.1075855313": harga,
        "entry.2000248052": rsi_m1,
        "entry.1827234230": rsi_h1,
        "entry.237807986": signal
    }
    try:
        requests.post(FORM_URL, data=payload)
        print("☁️ Data berhasil terbang ke Google Sheets!")
    except Exception as e:
        print(f"❌ Gagal sinkron ke Cloud: {e}")

# ==========================================
# 3. FUNGSI AI & DATA MARKET
# ==========================================
def get_ai_analysis(p, area, rsi_m1, rsi_h1, signal, support, resistance, tp, sl):
    """Meminta analisa gaya abang-adik dari Gemini AI"""
    if not GEMINI_API_KEY or "GANTI_DENGAN" in GEMINI_API_KEY:
        return "Sinyal masuk, Rosit! Fokus ke angka TP/SL dulu, AI lagi buffering dikit!"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = (
        f"Kamu adalah Guru Trading Profesional untuk Rosit. Aset: BITCOIN (BTC). Harga: ${p:,.2f}. "
        f"RSI Menit: {rsi_m1:.1f}, RSI Jam: {rsi_h1:.1f}, Area Harga: {area:.1f}%. Sinyal: {signal}. "
        f"Support (Lantai): ${support:,.2f}, Resistance (Atap): ${resistance:,.2f}. "
        f"TUGAS: Jelaskan singkat kenapa kita {signal} berdasarkan RSI Menit (scalping) dan Jam (trend). "
        f"Jelaskan juga penempatan TP/SL. Gunakan gaya bahasa abang-adik yang akrab, "
        f"sopan, dan beri semangat buat Rosit yang lagi ngerintis modal dari angkringan!"
    )
    
    try:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=payload, timeout=12)
        res_json = response.json()
        if 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        return "Fokus ke plan awal ya, Rosit. AI butuh waktu buat mikir."
    except:
        return "Koneksi AI agak lambat, amankan modal dulu, Bos!"

def get_market_data(symbol, timeframe='minute'):
    """Mengambil data harga dan menghitung indikator teknikal"""
    try:
        tf_url = "histominute" if timeframe == 'minute' else "histohour"
        url = f"https://min-api.cryptocompare.com/data/v2/{tf_url}?fsym={symbol}&tsym=USD&limit=100"
        
        res = requests.get(url, timeout=10)
        data = res.json()['Data']['Data']
        prices = [d['close'] for d in data]
        
        p = prices[-1]
        m_prices = prices[-15:]
        
        # Hitung RSI
        gains = [m_prices[i] - m_prices[i-1] for i in range(1, len(m_prices)) if m_prices[i] > m_prices[i-1]]
        losses = [m_prices[i-1] - m_prices[i] for i in range(1, len(m_prices)) if m_prices[i] < m_prices[i-1]]
        avg_gain = sum(gains)/14 if gains else 0
        avg_loss = sum(losses)/14 if losses else 0.001
        rsi = 100 - (100 / (1 + (avg_gain / avg_loss)))
        
        # Hitung Volatilitas (Kecepatan pergerakan)
        moves = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
        avg_speed = sum(moves) / len(moves) if moves else 0.01
        
        return {"price": p, "rsi": rsi, "prices_all": prices, "speed": avg_speed}
    except Exception as e:
        print(f"Error ambil data {timeframe}: {e}")
        return None

# ==========================================
# 4. PROGRAM UTAMA (MAIN ENGINE)
# ==========================================
def main():
    asset_name = "BITCOIN (BTCUSDm)"
    symbol = "BTC"
    
    # Set waktu ke Jakarta
    tz = pytz.timezone('Asia/Jakarta')
    waktu_skrg = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"[{waktu_skrg}] Menjalankan Rosit Gold AI Engine...")
    
    # Ambil Data
    data_m1 = get_market_data(symbol, timeframe='minute')
    data_h1 = get_market_data(symbol, timeframe='hour')
    
    if not data_m1 or not data_h1:
        print("❌ Gagal mengambil data dari market.")
        return

    p = data_m1['price']
    rsi_m1 = data_m1['rsi']
    rsi_h1 = data_h1['rsi']
    avg_speed = data_m1['speed']
    
    # Hitung Support & Resistance Area
    support = min(data_m1['prices_all'])
    resistance = max(data_m1['prices_all'])
    area = ((p - support) / (resistance - support)) * 100 if (resistance - support) != 0 else 50
    
    # --- LOGIKA TRADING MULTI-TIMEFRAME ---
    if rsi_m1 < 40 and area < 40 and rsi_h1 > 35:
        signal = "🟢 GAS BUY (Konfirmasi Trend)"
        tp, sl = p * 1.008, p * 0.99
    elif rsi_m1 > 60 and area > 60 and rsi_h1 > 65:
        signal = "🔴 GAS SELL (Momen Mahal)"
        tp, sl = p * 0.992, p * 1.01
    else:
        signal = "🟡 NGOPI DULU (Sinyal Belum Kompak)"
        tp, sl = resistance, support

    # Eksekusi Database
    simpan_log_hp(waktu_skrg, p, round(rsi_m1, 2), round(rsi_h1, 2), signal)
    simpan_ke_google_sheets(waktu_skrg, p, round(rsi_m1, 2), round(rsi_h1, 2), signal)

    # Dapatkan Pesan AI & Estimasi Waktu
    dist_to_tp = abs(tp - p)
    est_minutes = round(dist_to_tp / avg_speed) if avg_speed > 0 else 0
    est_text = f"{round(est_minutes/60, 1)} Jam" if est_minutes > 60 else f"{est_minutes} Menit"
    ai_msg = get_ai_analysis(p, area, rsi_m1, rsi_h1, signal, support, resistance, tp, sl)

    # Format Pesan Telegram
    msg = (
        f"🟠 **{asset_name} REPORT** 🟠\n"
        f"📅 `{waktu_skrg} WIB`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📢 **AKSI**: `{signal}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💵 **HARGA**: `${p:,.2f}`\n"
        f"📊 **RSI (M1|H1)**: {rsi_m1:.1f} | {rsi_h1:.1f}\n"
        f"📉 **AREA**: {area:.1f}%\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🧱 **LANTAI (S)**: `${support:,.2f}`\n"
        f"🏠 **ATAP (R)**: `${resistance:,.2f}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **TARGET TP**: `${tp:,.2f}`\n"
        f"🛡️ **STOP LOSS**: `${sl:,.2f}`\n"
        f"⏳ **ESTIMASI**: ± {est_text}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📚 **KULIAH GURU AI:**\n_{ai_msg}_\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    
    # Kirim ke Telegram
    try:
        url_tele = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(url_tele, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        print(f"✅ Laporan sukses dikirim ke Telegram!")
    except Exception as e:
        print(f"❌ Gagal kirim Telegram: {e}")

if __name__ == "__main__":
    main()
