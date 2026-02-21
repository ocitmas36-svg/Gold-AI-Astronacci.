import requests
import os

# --- AMBIL DATA DARI SECRETS ---
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_market_data(symbol, timeframe_min):
    url = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={symbol}&tsym=USD&limit=50&aggregate={timeframe_min}"
    try:
        data = requests.get(url).json()['Data']['Data']
        prices = [d['close'] for d in data]
        p_now = prices[-1]
        
        # Hitung RSI Sederhana
        m_prices = prices[-15:]
        gains = [m_prices[i] - m_prices[i-1] for i in range(1, len(m_prices)) if m_prices[i] > m_prices[i-1]]
        losses = [m_prices[i-1] - m_prices[i] for i in range(1, len(m_prices)) if m_prices[i] < m_prices[i-1]]
        avg_gain = sum(gains)/14 if gains else 0
        avg_loss = sum(losses)/14 if losses else 0.001
        rsi = 100 - (100 / (1 + (avg_gain / avg_loss)))
        
        return p_now, rsi, min(prices), max(prices)
    except:
        return None

def main():
    assets = [
        {"name": "BITCOIN", "symbol": "BTC", "emoji": "🟠"},
        {"name": "GOLD (PAXG)", "symbol": "PAXG", "emoji": "🔱"}
    ]
    
    for asset in assets:
        data_h1 = get_market_data(asset['symbol'], 60)
        data_m5 = get_market_data(asset['symbol'], 5)
        
        if not data_h1 or not data_m5: continue

        p_h1, rsi_h1, sup_h1, res_h1 = data_h1
        p_m5, rsi_m5, sup_m5, res_m5 = data_m5
        
        # LOGIKA SINYAL
        if rsi_h1 > 45 and rsi_m5 < 35:
            signal, tp, sl = "🚀 GAS BUY! (Beli Murah)", res_m5, sup_m5 - (p_m5 * 0.001)
        elif rsi_h1 < 55 and rsi_m5 > 65:
            signal, tp, sl = "📉 GAS SELL! (Jual Mahal)", sup_m5, res_m5 + (p_m5 * 0.001)
        else:
            signal, tp, sl = "☕ NGOPI DULU", p_m5, p_m5

        # PESAN SINGKAT & PADAT
        msg = (
            f"{asset['emoji']} **{asset['name']}** {asset['emoji']}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🗺️ **PETA H1**: `{'NAIK' if rsi_h1 > 50 else 'TURUN'}`\n"
            f"🎯 **Sinyal M5**: `{signal}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💵 **Harga**: `${p_m5:,.2f}`\n"
            f"🎯 **TP**: `${tp:,.2f}`\n"
            f"🛡️ **SL**: `${sl:,.2f}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💡 *Saran: Entry pas M5 kena Lantai/Atap. Tetap sopan & bahagia!*"
        )
        
        # Kirim ke Telegram
        url_tele = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(url_tele, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    main()
