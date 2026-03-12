import requests
from datetime import datetime
import pytz
import os
import csv
import time

# ==========================================
# 1. KONFIGURASI API & TOKEN (Tetap Sama)
# ==========================================
TELE_TOKEN = os.getenv("TELE_TOKEN") or "GANTI_DENGAN_TOKEN_BOT_TELEGRAM_KAMU"
CHAT_ID = os.getenv("CHAT_ID") or "GANTI_DENGAN_CHAT_ID_KAMU"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "GANTI_DENGAN_API_KEY_GEMINI_KAMU"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSf4cF9UwXaPEuSHFVcL36LvDSrBk41H4c_8n9810uMllAG49g/formResponse"

# ==========================================
# 2. FUNGSI DATABASE
# ==========================================
def simpan_log_hp(waktu, harga, rsi_m1, rsi_h1, signal):
    file_exists = os.path.isfile('history_trading.csv')
    try:
        with open('history_trading.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Waktu', 'Harga', 'RSI_M1', 'RSI_H1', 'Sinyal'])
            writer.writerow([waktu, harga, rsi_m1, rsi_h1, signal])
    except: pass

def simpan_ke_google_sheets(waktu, harga, rsi_m1, rsi_h1, signal):
    payload = {
        "entry.497131546": waktu, "entry.1075855313": harga,
        "entry.2000248052": rsi_m1, "entry.1827234230": rsi_h1,
        "entry.237807986": signal
    }
    try: requests.post(FORM_URL, data=payload, timeout=10)
    except: print("⚠️ Cloud agak lemot, tapi aman.")

# ==========================================
# 3. FUNGSI ANALISA & MARKET DATA (Upgrade MA-20)
# ==========================================
def get_ai_analysis(p, rsi_m1, rsi_h1, signal, ma20):
    if not GEMINI_API_KEY or "GANTI" in GEMINI_API_KEY: return "AI sedang offline."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    status_trend = "DI ATAS MA-20 (Bullish)" if p > ma20 else "DI BAWAH MA-20 (Bearish)"
    
    prompt = (
        f"Guru Trading Rosit. BTC: ${p:,.2f}. RSI M1:{rsi_m1:.1f}, H1:{rsi_h1:.1f}. "
        f"Trend: {status_trend}. Sinyal: {signal}. "
        f"Tugas: Beri nasihat singkat gaya abang-adik yang akrab & semangat buat Rosit si pengusaha angkringan."
    )
    try:
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10).json()
        return res['candidates'][0]['content']['parts'][0]['text']
    except: return "Tetap fokus pada rencana, Rosit!"

def get_market_data(symbol, timeframe='minute'):
    try:
        tf_url = "histominute" if timeframe == 'minute' else "histohour"
        url = f"https://min-api.cryptocompare.com/data/v2/{tf_url}?fsym={symbol}&tsym=USD&limit=30"
        res = requests.get(url, timeout=10).json()
        data = res['Data']['Data']
        prices = [d['close'] for d in data]
        
        # RSI Calculation
        p = prices[-1]
        diffs = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = sum([d for d in diffs if d > 0]) / 14
        losses = abs(sum([d for d in diffs if d < 0])) / 14
        rsi = 100 - (100 / (1 + (gains / (losses if losses > 0 else 0.001))))
        
        # MA-20 (Moving Average 20 periode)
        ma20 = sum(prices[-20:]) / 20
        
        return {"price": p, "rsi": rsi, "ma20": ma20, "max": max(prices), "min": min(prices)}
    except: return None

# ==========================================
# 4. ENGINE UTAMA
# ==========================================
def jalankan_bot():
    symbol = "BTC"
    tz = pytz.timezone('Asia/Jakarta')
    waktu_skrg = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    
    data_m1 = get_market_data(symbol, 'minute')
    data_h1 = get_market_data(symbol, 'hour')
    
    if not data_m1 or not data_h1: return
    
    p, rsi_m1, ma20 = data_m1['price'], data_m1['rsi'], data_m1['ma20']
    rsi_h1 = data_h1['rsi']
    
    # LOGIKA UPGRADE: RSI + TREND MA-20
    # Buy jika: Murah (RSI < 35) DAN harga mulai di atas MA-20 (Mulai Naik)
    if rsi_m1 < 35 and p > ma20:
        signal = "🟢 GAS BUY (Konfirmasi Naik)"
        tp, sl = p * 1.01, p * 0.99
    # Sell jika: Mahal (RSI > 65) DAN harga mulai di bawah MA-20 (Mulai Turun)
    elif rsi_m1 > 65 and p < ma20:
        signal = "🔴 GAS SELL (Konfirmasi Turun)"
        tp, sl = p * 0.99, p * 1.01
    else:
        signal = "🟡 NGOPI DULU"
        tp, sl = data_m1['max'], data_m1['min']

    # Simpan data
    simpan_log_hp(waktu_skrg, p, rsi_m1, rsi_h1, signal)
    simpan_ke_google_sheets(waktu_skrg, p, rsi_m1, rsi_h1, signal)
    
    # Kirim Telegram
    ai_msg = get_ai_analysis(p, rsi_m1, rsi_h1, signal, ma20)
    msg = (
        f"🤖 **ROSIT GOLD AI v2.0**\n"
        f"📅 `{waktu_skrg} WIB`\n"
        f"━━━━━━━━━━━━━━\n"
        f"📢 **AKSI**: `{signal}`\n"
        f"💵 **HARGA**: `${p:,.2f}`\n"
        f"📊 **RSI M1**: {rsi_m1:.1f}\n"
        f"📈 **MA-20**: `${ma20:,.2f}`\n"
        f"━━━━━━━━━━━━━━\n"
        f"🎯 **TP**: `${tp:,.2f}` | **SL**: `${sl:,.2f}`\n"
        f"━━━━━━━━━━━━━━\n"
        f"💬 **GURU AI:**\n_{ai_msg}_"
    )
    
    try:
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        print(f"✅ [{waktu_skrg}] Laporan Terkirim!")
    except: print("❌ Gagal kirim Telegram")

# ==========================================
# 5. LOOPING OTOMATIS
# ==========================================
if __name__ == "__main__":
    print("🚀 Bot Rosit Gold AI v2.0 Aktif!")
    print("Bot akan mengecek market setiap 15 menit. Tekan CTRL+C untuk stop.")
    
    while True:
        jalankan_bot()
        # Menunggu 15 menit (900 detik)
        time.sleep(900)
    
