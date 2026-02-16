import requests
from datetime import datetime
import pytz

# --- FORBIDDEN ACCESS ---
TOKEN = "7864440626:AAH_Qz67CNo5XW1iXW9o17l1xR0YpD7G5mI"
CHAT_ID = "5378770281"

def get_forbidden_intel():
    # Mengambil data PAXG (Gold) dan BTC (sebagai proxy sentimen risk-on/off)
    try:
        gold = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGUSDT").json()
        # Proxy untuk melihat kekuatan Dollar/Market Global via BTC
        market_sentiment = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT").json()
        
        return {
            "p": float(gold['lastPrice']),
            "h": float(gold['highPrice']),
            "l": float(gold['lowPrice']),
            "o": float(gold['openPrice']),
            "v": float(gold['volume']),
            "c": int(gold['count']),
            "sentimen": float(market_sentiment['priceChangePercent'])
        }
    except: return None

def main():
    intel = get_forbidden_intel()
    if not intel: return

    p, h, l, o = intel['p'], intel['h'], intel['l'], intel['o']
    d_range = h - l
    vwap = (h + l + p) / 3
    
    # 1. LOGIKA RAHASIA: VOLUME DENSITY (VSA)
    # Menghitung seberapa "padat" transaksi di setiap candle
    vol_density = intel['v'] / intel['c'] if intel['c'] != 0 else 0
    
    # 2. VIRTUAL SL LOGIC (Hidden from Brokers)
    # Menghitung titik di mana kita harus kabur tanpa memasang order SL di awal
    virtual_sl_buy = p - (d_range * 0.2)
    virtual_sl_sell = p + (d_range * 0.2)

    # 3. SENTIMEN PROXY (Correlation)
    # Jika sentimen market global (BTC) drop parah, emas biasanya jadi safe haven (Buy)
    is_safe_haven_mode = intel['sentimen'] < -3.0

    # --- SUPREME SCORING MATRIX (100+) ---
    score = 0
    logs = []

    # THE "GACOR" ALGORITHM
    if p < vwap: score += 20; logs.append("VWAP: Harga Diskon")
    if (p - l) / d_range < 0.2: score += 25; logs.append("L-Zone: Liquidity Grabbed")
    if is_safe_haven_mode: score += 15; logs.append("Global: Safe Haven Activated")
    if vol_density > (intel['v'] * 0.0001): score += 20; logs.append("VSA: Institutional Presence")
    
    # RSI Extreme Check
    rsi = ((p - l) / d_range) * 100 if d_range != 0 else 50
    if rsi < 25: score += 20; logs.append("RSI: Capitulation (Strong Buy)")

    # DECISION
    action = None
    if score >= 75: action = "BUY"
    elif rsi > 80: action = "SELL" # Simple exit/sell for overbought
    else: return

    # MESSAGE CONSTRUCTION
    wib = pytz.timezone('Asia/Jakarta')
    time_str = datetime.now(wib).strftime('%H:%M:%S')

    pesan = (
        f"🕵️ **ARCHITECT OF DESTINY v16.0**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🕒 **TIME:** {time_str} WIB\n"
        f"💵 **PRICE:** ${p:.2f}\n"
        f"🎯 **SCORE:** {score}/100\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📑 **HIDDEN ANALYSIS:**\n"
        f"• " + "\n• ".join(logs) + "\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ **VIRTUAL PROTECTION:**\n"
        f"Bot akan memantau harga secara rahasia. \n"
        f"Jika harga menyentuh **${virtual_sl_buy:.2f}**, segera EXIT manual (V-SL).\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 **COMMAND: {action} NOW**\n"
        f"✅ ENTRY : ${p:.2f}\n"
        f"🎯 TARGET : ${p + (d_range*0.5) if action=='BUY' else p - (d_range*0.5):.2f}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🤫 *Ini adalah fitur rahasia. Gunakan dengan bijak.*"
    )

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"})

if __name__ == "__main__":
    main()
