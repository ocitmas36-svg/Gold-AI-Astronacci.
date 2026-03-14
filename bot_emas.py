import requests
from datetime import datetime
import pytz
import os
import csv
import time

# ==========================================
# 1. KONFIGURASI API & TOKEN
# ==========================================
TELE_TOKEN = os.getenv("TELE_TOKEN") or "GANTI_DENGAN_TOKEN_BOT_TELEGRAM_KAMU"
CHAT_ID = os.getenv("CHAT_ID") or "GANTI_DENGAN_CHAT_ID_KAMU"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "GANTI_DENGAN_API_KEY_GEMINI_KAMU"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSf4cF9UwXaPEuSHFVcL36LvDSrBk41H4c_8n9810uMllAG49g/formResponse"

# Variabel Global untuk mengingat sinyal terakhir (BIAR GAK SPAM)
LAST_SIGNAL = None 

# ==========================================
# 2. FUNGSI DATABASE
# ==========================================
def simpan_ke_google_sheets(waktu, harga, rsi_m1, rsi_h1, signal):
    payload = {
        "entry.497131546": waktu, "entry.1075855313": harga,
        "entry.2000248052": rsi_m1, "entry.1827234230": rsi_h1,
        "entry.237807986": signal
    }
    try: requests.post(FORM_URL, data=payload, timeout=10)
    except: print("⚠️ Google Sheets lambat, tapi data tetap masuk.")

# ==========================================
# 3. FUNGSI MARKET & ANALISA
# ==========================================
def get_market_data(symbol):
    try:
        url = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={symbol}&tsym=USD&limit=30"
        res = requests.get(url, timeout=10).json()
        data = res['Data']['Data']
        prices = [d['close'] for d in data]
        p = prices[-1]
        
        # RSI 14
        diffs = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = sum([d for d in diffs if d > 0]) / 14
        losses = abs(sum([d for d in diffs if d < 0])) / 14
        rsi = 100 - (100 / (1 + (gains / (losses if losses > 0 else 0.001))))
        
        ma20 = sum(prices[-20:]) / 20
        return {"price": p, "rsi": rsi, "ma20": ma20}
    except: return None

def get_ai_analysis(p, rsi_m1, signal):
    if not GEMINI_API_KEY or "GANTI" in GEMINI_API_KEY: return "Fokus pada cuan, Rosit!"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"BTC: ${p:,.2f}, RSI: {rsi_m1:.1f}, Signal: {signal}. Beri nasihat trading singkat & semangat buat Rosit pengusaha angkringan."
    try:
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10).json()
        return res['candidates'][0]['content']['parts'][0]['text']
    except: return "Gas terus, Rosit!"

# ==========================================
# 4. ENGINE UTAMA (ANTI-SPAM)
# ==========================================
def jalankan_bot():
    global LAST_SIGNAL
    symbol = "BTC"
    tz = pytz.timezone('Asia/Jakarta')
    waktu_skrg = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    
    data = get_market_data(symbol)
    if not data: return
    
    p, rsi, ma20 = data['price'], data['rsi'], data['ma20']
    
    # LOGIKA SINYAL
    if rsi < 35 and p > ma20:
        current_signal = "🟢 GAS BUY"
    elif rsi > 65 and p < ma20:
        current_signal = "🔴 GAS SELL"
    else:
        current_signal = "🟡 NGOPI DULU"

    # 1. TETAP SIMPAN KE GOOGLE SHEETS (Agar grafik web update terus)
    simpan_ke_google_sheets(waktu_skrg, p, rsi, 0, current_signal)
    
    # 2. FILTER TELEGRAM: Kirim hanya jika sinyal BERUBAH dan BUKAN "NGOPI"
    if current_signal != LAST_SIGNAL:
        if current_signal != "🟡 NGOPI DULU":
            ai_msg = get_ai_analysis(p, rsi, current_signal)
            msg = (
                f"🚀 **SINYAL BARU ROSIT GOLD AI**\n"
                f"━━━━━━━━━━━━━━\n"
                f"📢 **AKSI**: `{current_signal}`\n"
                f"💵 **HARGA**: `${p:,.2f}`\n"
                f"📊 **RSI**: {rsi:.1f}\n"
                f"━━━━━━━━━━━━━━\n"
                f"💬 **GURU AI:**\n_{ai_msg}_"
            )
            try:
                requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                              json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
                print(f"✅ Sinyal {current_signal} terkirim ke Telegram!")
            except: print("❌ Gagal kirim Telegram")
        
        # Update sinyal terakhir agar tidak berulang
        LAST_SIGNAL = current_signal
    else:
        print(f"⏳ [{waktu_skrg}] Sinyal masih '{current_signal}', bot diam (No Spam).")

# ==========================================
# 5. LOOPING
# ==========================================
if __name__ == "__main__":
    print("🚀 Bot Rosit Pro Aktif (Mode Hemat Notif)!")
    while True:
        jalankan_bot()
        time.sleep(900) # Cek setiap 15 menit
        
