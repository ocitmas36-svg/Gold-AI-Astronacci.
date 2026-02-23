import requests
from datetime import datetime
import pytz
import os

# --- KONFIGURASI ---
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_analysis(p, area, rsi, signal, support, resistance, tp, sl):
    """Fungsi untuk mendapatkan edukasi trading dari Gemini AI"""
    if not GEMINI_API_KEY:
        return "Rosit, tetap fokus pantau harga ya. Koneksi AI lagi istirahat."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = (
        f"Kamu adalah Guru Trading Profesional untuk Rosit. Aset: BITCOIN (BTC). Harga: ${p:,.2f}. "
        f"Data Teknis: RSI {rsi:.1f}, Area Harga {area:.1f}%. Sinyal: {signal}. "
        f"Garis Penting: Support (Lantai) ${support:,.2f}, Resistance (Atap) ${resistance:,.2f}. "
        f"Rencana: TP di ${tp:,.2f} dan SL di ${sl:,.2f}. "
        f"TUGAS: Jelaskan singkat kenapa kita entry di titik ini (hubungkan RSI & Area). "
        f"Jelaskan kenapa SL & TP ditaruh di angka tersebut (hubungkan dengan Lantai/Atap). "
        f"Gunakan gaya bahasa abang-adik yang akrab, sopan, dan beri semangat buat Rosit yang lagi ngerintis modal dari angkringan."
    )
    
    try:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=payload, timeout=12)
        # Ambil teks dari respon Gemini
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Sinyal masuk, Rosit! Fokus ke angka TP/SL dulu, AI lagi buffering dikit!"

def get_market_data(symbol):
    """Fungsi mengambil data market terkini"""
    try:
        url = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={symbol}&tsym=USD&limit=100"
        res = requests.get(url, timeout=10)
        data = res.json()['Data']['Data']
        prices = [d['close'] for d in data]
        
        p = prices[-1]
        support = min(prices)
        resistance = max(prices)
        
        # RSI 14 Periode
        m_prices = prices[-15:]
        gains = [m_prices[i] - m_prices[i-1] for i in range(1, len(m_prices)) if m_prices[i] > m_prices[i-1]]
        losses = [m_prices[i-1] - m_prices[i] for i in range(1, len(m_prices)) if m_prices[i] < m_prices[i-1]]
        avg_gain = sum(gains)/14 if gains else 0
        avg_loss = sum(losses)/14 if losses else 0.001
        rsi = 100 - (100 / (1 + (avg_gain / avg_loss)))
        
        area = ((p - support) / (resistance - support)) * 100 if (resistance - support) != 0 else 50
        
        moves = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
        avg_speed = sum(moves) / len(moves) if moves else 0.01
        
        return p, rsi, area, avg_speed, support, resistance
    except Exception as e:
        print(f"Error ambil data: {e}")
        return None

def main():
    asset_name = "BITCOIN (BTCUSDm)"
    symbol = "BTC"
    
    # Set zona waktu Jakarta
    tz = pytz.timezone('Asia/Jakarta')
    waktu_skrg = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"[{waktu_skrg}] Memulai analisa {asset_name}...")
    data = get_market_data(symbol)
    
    if not data:
        return

    p, rsi, area, avg_speed, support, resistance = data
    
    # --- LOGIKA SCALPER SENSITIF ---
    if rsi < 40 and area < 40:
        signal = "🟢 GAS BUY (Momen Murah)"
        tp, sl = p * 1.008, p * 0.99
    elif rsi > 60 and area > 60:
        signal = "🔴 GAS SELL (Momen Mahal)"
        tp, sl = p * 0.992, p * 1.01
    else:
        signal = "🟡 NGOPI DULU (Tunggu Momen)"
        # Saat ngopi, TP/SL diarahkan ke atap/lantai terdekat sebagai referensi
        tp, sl = resistance, support

    # Estimasi Waktu
    dist_to_tp = abs(tp - p)
    est_minutes = round(dist_to_tp / avg_speed) if avg_speed > 0 else 0
    est_text = f"{round(est_minutes/60, 1)} Jam" if est_minutes > 60 else f"{est_minutes} Menit"

    ai_msg = get_ai_analysis(p, area, rsi, signal, support, resistance, tp, sl)

    # Format Pesan Telegram
    msg = (
        f"🟠 **{asset_name} REPORT** 🟠\n"
        f"📅 `{waktu_skrg} WIB`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📢 **AKSI**: `{signal}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💵 **HARGA**: `${p:,.2f}`\n"
        f"📊 **RSI**: {rsi:.1f} | **AREA**: {area:.1f}%\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🧱 **LANTAI (S)**: `${support:,.2f}`\n"
        f"🏠 **ATAP (R)**: `${resistance:,.2f}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **TARGET TP**: `${tp:,.2f}`\n"
        f"🛡️ **STOP LOSS**: `${sl:,.2f}`\n"
        f"⏳ **ESTIMASI**: ± {est_text}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📚 **KULIAH GURU AI:**\n{ai_msg}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    
    try:
        url_tele = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(url_tele, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        print(f"✅ Laporan dikirim!")
    except Exception as e:
        print(f"❌ Gagal: {e}")

if __name__ == "__main__":
    main()