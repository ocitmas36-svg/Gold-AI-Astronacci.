import requests
from datetime import datetime
import pytz
import os
import urllib.parse

# --- KONFIGURASI (Ganti dengan Token milikmu) ---
TELE_TOKEN = os.getenv("TELE_TOKEN") or "GANTI_TOKEN_BOT_TELE_DI_SINI"
CHAT_ID = os.getenv("CHAT_ID") or "GANTI_CHAT_ID_TELE_DI_SINI"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "GANTI_API_KEY_GEMINI_DI_SINI"

def get_ai_analysis(p, area, rsi_m1, rsi_h1, signal, support, resistance, tp, sl):
    """Fungsi untuk mendapatkan edukasi trading dari Gemini AI"""
    if not GEMINI_API_KEY or "GANTI_" in GEMINI_API_KEY:
        return "Sinyal masuk, Rosit! Fokus ke angka TP/SL dulu, AI lagi buffering dikit!"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = (
        f"Kamu adalah Guru Trading Profesional untuk Rosit. Aset: BITCOIN (BTC). Harga: ${p:,.2f}. "
        f"Data Teknis: RSI Menit {rsi_m1:.1f}, RSI Jam {rsi_h1:.1f}, Area Harga {area:.1f}%. Sinyal: {signal}. "
        f"Garis Penting: Support (Lantai) ${support:,.2f}, Resistance (Atap) ${resistance:,.2f}. "
        f"Rencana: TP di ${tp:,.2f} dan SL di ${sl:,.2f}. "
        f"TUGAS: Jelaskan singkat kenapa kita entry/wait berdasarkan korelasi RSI Menit dan Jam. "
        f"Jelaskan kenapa SL & TP ditaruh di situ. Gunakan gaya bahasa abang-adik yang akrab, "
        f"sopan, dan beri semangat buat Rosit yang lagi ngerintis modal dari angkringan."
    )
    
    try:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=payload, timeout=12)
        res_json = response.json()
        if 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        return "Sinyal masuk, Rosit! Fokus ke angka TP/SL dulu, AI lagi buffering dikit!"
    except:
        return "Sinyal masuk, Rosit! Fokus ke angka TP/SL dulu, AI lagi buffering dikit!"

def get_market_data(symbol, limit=100, timeframe='minute'):
    """Fungsi mengambil data market (bisa minute atau hour)"""
    try:
        tf_url = "histominute" if timeframe == 'minute' else "histohour"
        url = f"https://min-api.cryptocompare.com/data/v2/{tf_url}?fsym={symbol}&tsym=USD&limit={limit}"
        
        res = requests.get(url, timeout=10)
        data = res.json()['Data']['Data']
        prices = [d['close'] for d in data]
        
        p = prices[-1]
        m_prices = prices[-15:]
        gains = [m_prices[i] - m_prices[i-1] for i in range(1, len(m_prices)) if m_prices[i] > m_prices[i-1]]
        losses = [m_prices[i-1] - m_prices[i] for i in range(1, len(m_prices)) if m_prices[i] < m_prices[i-1]]
        avg_gain = sum(gains)/14 if gains else 0
        avg_loss = sum(losses)/14 if losses else 0.001
        rsi = 100 - (100 / (1 + (avg_gain / avg_loss)))
        
        # Hitung volatilitas (avg_speed) untuk estimasi waktu
        moves = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
        avg_speed = sum(moves) / len(moves) if moves else 0.01
        
        return {"price": p, "rsi": rsi, "prices_all": prices, "speed": avg_speed}
    except Exception as e:
        print(f"Error ambil data {timeframe}: {e}")
        return None

def main():
    asset_name = "BITCOIN (BTCUSDm)"
    symbol = "BTC"
    
    # Set zona waktu Jakarta
    tz = pytz.timezone('Asia/Jakarta')
    waktu_skrg = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"[{waktu_skrg}] Memulai analisa Multi-Timeframe {asset_name}...")
    
    # 1. Ambil Data Menit & Jam
    data_m1 = get_market_data(symbol, timeframe='minute')
    data_h1 = get_market_data(symbol, timeframe='hour')
    
    if not data_m1 or not data_h1:
        print("❌ Gagal mengambil data market.")
        return

    p = data_m1['price']
    rsi_m1 = data_m1['rsi']
    rsi_h1 = data_h1['rsi']
    avg_speed = data_m1['speed']
    
    # Support/Resistance dari data menit (Lokal)
    support = min(data_m1['prices_all'])
    resistance = max(data_m1['prices_all'])
    area = ((p - support) / (resistance - support)) * 100 if (resistance - support) != 0 else 50
    
    # --- LOGIKA MULTI-TIMEFRAME MANTAP ---
    # Buy jika menit oversold (<40) tapi Jam tidak sedang crash parah (>35)
    if rsi_m1 < 40 and area < 40 and rsi_h1 > 35:
        signal = "🟢 GAS BUY (Konfirmasi Trend)"
        tp, sl = p * 1.008, p * 0.99
    # Sell jika menit overbought (>60) tapi Jam mulai jenuh (>65)
    elif rsi_m1 > 60 and area > 60 and rsi_h1 > 65:
        signal = "🔴 GAS SELL (Momen Mahal)"
        tp, sl = p * 0.992, p * 1.01
    else:
        signal = "🟡 NGOPI DULU (Tunggu Sinyal Kompak)"
        tp, sl = resistance, support

    # Estimasi Waktu
    dist_to_tp = abs(tp - p)
    est_minutes = round(dist_to_tp / avg_speed) if avg_speed > 0 else 0
    est_text = f"{round(est_minutes/60, 1)} Jam" if est_minutes > 60 else f"{est_minutes} Menit"

    # Analisa AI
    ai_msg = get_ai_analysis(p, area, rsi_m1, rsi_h1, signal, support, resistance, tp, sl)

    # Format Pesan Telegram (Markdown)
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
        print(f"✅ Laporan dikirim ke Telegram!")
    except Exception as e:
        print(f"❌ Gagal kirim Telegram: {e}")

if __name__ == "__main__":
    main()
