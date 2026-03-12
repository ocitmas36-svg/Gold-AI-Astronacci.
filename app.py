import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. SETTING HALAMAN
st.set_page_config(page_title="ROSIT GOLD AI PRO", page_icon="💰", layout="wide")

# 2. FULL CUSTOM CSS (MIRIP UI APLIKASI DUNIA)
st.markdown("""
    <style>
    /* Background Hitam Pekat */
    .main { background-color: #000000; }
    
    /* Header Emas Mewah */
    .gold-header {
        background: linear-gradient(90deg, #bf953f, #fcf6ba, #b38728, #fbf5b7, #aa771c);
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid #ff9900;
    }
    .gold-header h1 { color: #000 !important; margin: 0; font-size: 24px; font-weight: 900; }
    .gold-header p { color: #333 !important; margin: 0; font-size: 11px; font-weight: bold; }

    /* Card Statistik */
    .stat-card {
        background-color: #111111;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #222;
        text-align: center;
        margin-bottom: 10px;
    }
    .stat-label { color: #888; font-size: 10px; text-transform: uppercase; font-weight: bold; }
    .stat-value { color: #ffffff; font-size: 18px; font-weight: bold; }

    /* Box Signal Hijau */
    .signal-box {
        background: linear-gradient(145deg, #0d1f12, #050a06);
        border: 1px solid #00ff00;
        padding: 15px;
        border-radius: 15px;
        margin: 15px 0;
        text-align: center;
    }
    
    /* Tombol Execute */
    .btn-execute {
        background-color: #ff9900;
        color: black;
        padding: 10px;
        border-radius: 10px;
        font-weight: bold;
        text-align: center;
        margin-top: 10px;
        font-size: 14px;
    }

    /* Hilangkan Spasi Berlebih Streamlit */
    .block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER EMAS ---
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
    
    # Perhitungan Win Rate
    wins, losses = 0, 0
    in_pos, entry = False, 0
    for i, r in data.iterrows():
        sig = str(r['Signal']).upper()
        if "BUY" in sig and not in_pos: in_pos, entry = True, r['Harga']
        elif "SELL" in sig and in_pos:
            in_pos = False
            if r['Harga'] > entry: wins += 1
            else: losses += 1
    wr = (wins/(wins+losses)*100) if (wins+losses) > 0 else 0

    # --- BARIS 1: HARGA & MOMENTUM ---
    c_price, c_mom = st.columns(2)
    with c_price:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">XAU/USD (GOLD)</div>
                <div class="stat-value" style="font-size:24px;">${last_row['Harga']:,.2f}</div>
                <div style="color:#00ff00; font-size:12px;">▲ LIVE MARKET</div>
            </div>
        """, unsafe_allow_html=True)
    with c_mom:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">MOMENTUM RSI</div>
                <div class="stat-value" style="color:#ff9900;">{last_row['RSI_M1']:.1f}</div>
                <div style="color:#444; font-size:12px;">TREND: BULLISH</div>
            </div>
        """, unsafe_allow_html=True)

    # --- BARIS 2: GRAFIK (TENGAH) ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Timestamp'], y=data['Harga'], mode='lines', line=dict(color='#ff9900', width=2), fill='tozeroy', fillcolor='rgba(255,153,0,0.05)'))
    
    # Marker Sinyal
    buys = data[data['Signal'].str.contains("BUY", na=False)]
    fig.add_trace(go.Scatter(x=buys['Timestamp'], y=buys['Harga'], mode='markers', marker=dict(symbol='triangle-up', size=12, color='#00ff00')))
    sells = data[data['Signal'].str.contains("SELL", na=False)]
    fig.add_trace(go.Scatter(x=sells['Timestamp'], y=sells['Harga'], mode='markers', marker=dict(symbol='triangle-down', size=12, color='#ff4b4b')))
    
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='black', plot_bgcolor='black', showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # --- BARIS 3: WIN RATE STATS ---
    st.write("")
    s1, s2, s3 = st.columns(3)
    s1.markdown(f"<div class='stat-card'><div class='stat-label'>WIN RATE</div><div class='stat-value'>{wr:.1f}%</div></div>", unsafe_allow_html=True)
    s2.markdown(f"<div class='stat-card'><div class='stat-label'>TOTAL WIN</div><div class='stat-value' style='color:#00ff00;'>{wins}</div></div>", unsafe_allow_html=True)
    s3.markdown(f"<div class='stat-card'><div class='stat-label'>TOTAL LOSS</div><div class='stat-value' style='color:#ff4b4b;'>{losses}</div></div>", unsafe_allow_html=True)

    # --- BARIS 4: LIVE SIGNAL BOX ---
    sig_color = "#00FF00" if "BUY" in last_row['Signal'] else "#FF4B4B" if "SELL" in last_row['Signal'] else "#FFA500"
    st.markdown(f"""
        <div class="signal-box">
            <div style="color:#00ff00; font-size:10px; font-weight:bold; letter-spacing:2px;">📡 LIVE AI SIGNAL</div>
            <div style="color:white; font-size:20px; margin:10px 0;">{last_row['Signal']} @ {last_row['Harga']}</div>
            <div class="btn-execute">EXECUTE TRADE NOW</div>
        </div>
    """, unsafe_allow_html=True)

    # --- BARIS 5: HISTORY (DI BAWAH SENDIRI) ---
    with st.expander("📜 VIEW TRADE HISTORY LOG"):
        st.dataframe(data.sort_values(by='Timestamp', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Syncing... {e}")

st.markdown("<p style='text-align: center; font-size: 9px; color: #333;'>ROSIT GOLD AI - V3.0 GLOBAL</p>", unsafe_allow_html=True)
