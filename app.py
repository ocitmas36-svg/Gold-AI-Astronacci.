import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="ROSIT GOLD AI PRO", page_icon="💰", layout="wide")

# 2. FULL CUSTOM CSS (DESAIN PREMIUM HITAM-EMAS)
st.markdown("""
    <style>
    /* Background Hitam Pekat */
    .main { background-color: #000000; }
    
    /* Header Emas Metalik */
    .gold-header {
        background: linear-gradient(90deg, #bf953f, #fcf6ba, #b38728, #fbf5b7, #aa771c);
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 15px;
        border: 1px solid #ff9900;
        box-shadow: 0px 4px 15px rgba(255, 153, 0, 0.3);
    }
    .gold-header h1 { color: #000 !important; margin: 0; font-size: 22px; font-weight: 900; }
    .gold-header p { color: #333 !important; margin: 0; font-size: 10px; font-weight: bold; letter-spacing: 1px; }

    /* Card Box Statistik */
    .stat-card {
        background-color: #111111;
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #222;
        text-align: center;
        margin-bottom: 10px;
    }
    .stat-label { color: #888; font-size: 9px; text-transform: uppercase; font-weight: bold; margin-bottom: 5px; }
    .stat-value { color: #ffffff; font-size: 18px; font-weight: bold; }

    /* Box Signal Hijau (Floating Style) */
    .signal-box {
        background: linear-gradient(145deg, #0d1f12, #050a06);
        border: 1px solid #00ff00;
        padding: 20px;
        border-radius: 20px;
        margin: 15px 0;
        text-align: center;
        box-shadow: 0px 0px 20px rgba(0, 255, 0, 0.2);
    }
    
    /* Tombol Action */
    .btn-execute {
        background: linear-gradient(90deg, #ff9900, #ffcc00);
        color: black;
        padding: 12px;
        border-radius: 12px;
        font-weight: 900;
        text-align: center;
        margin-top: 15px;
        font-size: 14px;
        text-transform: uppercase;
    }

    /* Tabel Riwayat (Dibuat Dark & Slim) */
    .stDataFrame { border: 1px solid #222; border-radius: 10px; }
    
    /* Hilangkan padding berlebih */
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER PREMIUM ---
st.markdown("""
    <div class="gold-header">
        <h1>ROSIT GOLD AI</h1>
        <p>PROPRIETARY QUANTITATIVE TRADING INTELLIGENCE</p>
    </div>
    """, unsafe_allow_html=True)

# 3. LOAD DATA
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ygHIdUszMkTGiG0WZKe3l39tkIdFmid86WP6KTErlPo/export?format=csv"

@st.cache_data(ttl=20)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = ['Timestamp', 'Waktu', 'Harga', 'RSI_M1', 'RSI_H1', 'Signal']
    df['Harga'] = pd.to_numeric(df['Harga'], errors='coerce')
    df['RSI_M1'] = pd.to_numeric(df['RSI_M1'], errors='coerce')
    return df.dropna(subset=['Harga'])

try:
    data = load_data()
    last_row = data.iloc[-1]
    
    # Hitung Win Rate & Score
    wins, losses = 0, 0
    in_pos, entry = False, 0
    for i, r in data.iterrows():
        sig = str(r['Signal']).upper()
        if "BUY" in sig and not in_pos: in_pos, entry = True, r['Harga']
        elif "SELL" in sig and in_pos:
            in_pos = False
            if r['Harga'] > entry: wins += 1
            else: losses += 1
    total = wins + losses
    wr = (wins / total * 100) if total > 0 else 0

    # --- BAGIAN 1: HARGA & MOMENTUM (DASHBOARD) ---
    c_price, c_mom = st.columns(2)
    with c_price:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">XAU/USD (GOLD)</div>
                <div class="stat-value" style="font-size:22px; color:#ff9900;">${last_row['Harga']:,.2f}</div>
                <div style="color:#00ff00; font-size:11px;">● LIVE MARKET</div>
            </div>
        """, unsafe_allow_html=True)
    with c_mom:
        trend = "BULLISH" if last_row['RSI_M1'] > 50 else "BEARISH"
        trend_col = "#00ff00" if trend == "BULLISH" else "#ff4b4b"
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">MOMENTUM RSI</div>
                <div class="stat-value">{last_row['RSI_M1']:.1f}</div>
                <div style="color:{trend_col}; font-size:11px;">TREND: {trend}</div>
            </div>
        """, unsafe_allow_html=True)

    # --- BAGIAN 2: GRAFIK ANALISIS (ANALYSIS) ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['Timestamp'], y=data['Harga'], 
        mode='lines', line=dict(color='#ff9900', width=2), 
        fill='tozeroy', fillcolor='rgba(255,153,0,0.05)'
    ))
    
    # Marker Sinyal Buy/Sell
    buys = data[data['Signal'].str.contains("BUY", na=False)]
    fig.add_trace(go.Scatter(x=buys['Timestamp'], y=buys['Harga'], mode='markers', name='BUY', marker=dict(symbol='triangle-up', size=12, color='#00ff00')))
    sells = data[data['Signal'].str.contains("SELL", na=False)]
    fig.add_trace(go.Scatter(x=sells['Timestamp'], y=sells['Harga'], mode='markers', name='SELL', marker=dict(symbol='triangle-down', size=12, color='#ff4b4b')))
    
    fig.update_layout(
        template="plotly_dark", height=350, 
        margin=dict(l=0,r=0,t=10,b=0), 
        paper_bgcolor='black', plot_bgcolor='black', 
        showlegend=False,
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- BAGIAN 3: SKOR PERFORMA (RIWAYAT RINGKAS) ---
    s1, s2, s3 = st.columns(3)
    s1.markdown(f"<div class='stat-card'><div class='stat-label'>WIN RATE</div><div class='stat-value' style='color:#ffcc00;'>{wr:.1f}%</div></div>", unsafe_allow_html=True)
    s2.markdown(f"<div class='stat-card'><div class='stat-label'>TOTAL WIN</div><div class='stat-value' style='color:#00ff00;'>{wins}</div></div>", unsafe_allow_html=True)
    s3.markdown(f"<div class='stat-card'><div class='stat-label'>TOTAL LOSS</div><div class='stat-value' style='color:#ff4b4b;'>{losses}</div></div>", unsafe_allow_html=True)

    # --- BAGIAN 4: LIVE AI SIGNAL BOX ---
    sig_color = "#00FF00" if "BUY" in last_row['Signal'] else "#FF4B4B" if "SELL" in last_row['Signal'] else "#FFA500"
    st.markdown(f"""
        <div class="signal-box">
            <div style="color:#00ff00; font-size:10px; font-weight:bold; letter-spacing:2px; margin-bottom:10px;">📡 LIVE AI SIGNAL</div>
            <div style="color:white; font-size:24px; font-weight:900;">{last_row['Signal']}</div>
            <div style="color:#888; font-size:14px;">ENTRY AT ${last_row['Harga']:,.2f}</div>
            <div class="btn-execute">EXECUTE TRADE NOW</div>
        </div>
    """, unsafe_allow_html=True)

    # --- BAGIAN 5: TABEL DATA LENGKAP ---
    with st.expander("📜 VIEW FULL TRANSACTION LOGS"):
        st.dataframe(data.sort_values(by='Timestamp', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Syncing AI Terminal... {e}")

st.markdown("<p style='text-align: center; font-size: 9px; color: #444; margin-top:20px;'>ROSIT GOLD AI - V3.0 GLOBAL EDITION</p>", unsafe_allow_html=True)
