import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. KONFIGURASI TAMPILAN (DIPERBAIKI UNTUK HP)
st.set_page_config(
    page_title="ROSIT GOLD AI v2.0",
    page_icon="💰",
    layout="wide"
)

# Custom CSS agar tulisan statistik terlihat jelas di HP (Background Terang/Gelap tetap muncul)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { 
        background-color: #1e2130 !important; 
        padding: 10px !important; 
        border-radius: 10px !important; 
        border: 1px solid #3e4255 !important;
    }
    div[data-testid="stMetricValue"] { font-size: 22px !important; color: #00d4ff !important; }
    div[data-testid="stMetricLabel"] { color: #ffffff !important; font-weight: bold !important; }
    h1, h2, h3 { color: #ff9900 !important; }
    </style>
    """, unsafe_allow_html=True)

# Header
st.markdown("<h1 style='text-align: center;'>🛰️ ROSIT GOLD AI TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Premium Auto-Trading Analytics</p>", unsafe_allow_html=True)

# 2. LOAD DATA
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ygHIdUszMkTGiG0WZKe3l39tkIdFmid86WP6KTErlPo/export?format=csv"

@st.cache_data(ttl=20)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = ['Timestamp', 'Waktu', 'Harga', 'RSI_M1', 'RSI_H1', 'Signal']
    df['Harga'] = pd.to_numeric(df['Harga'], errors='coerce')
    df = df.dropna(subset=['Harga'])
    return df

try:
    data = load_data()
    last_row = data.iloc[-1]
    
    # --- LOGIKA WIN RATE (DIPERBAIKI) ---
    wins, losses = 0, 0
    in_position = False
    entry_price = 0

    for index, row in data.iterrows():
        sig = str(row['Signal']).upper()
        if "BUY" in sig and not in_position:
            in_position = True
            entry_price = row['Harga']
        elif "SELL" in sig and in_position:
            in_position = False
            if row['Harga'] > entry_price: wins += 1
            else: losses += 1

    total_trades = wins + losses
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

    # 3. STATISTIK UTAMA (DIJAMIN MUNCUL)
    st.subheader("🏆 AI Performance Stats")
    # Menggunakan columns agar rapi di HP
    w_col1, w_col2 = st.columns(2)
    with w_col1:
        st.metric("🔥 WIN RATE", f"{win_rate:.1f}%")
        st.metric("✅ CUAN", f"{wins} Kali")
    with w_col2:
        st.metric("🔄 TOTAL TRADE", f"{total_trades}")
        st.metric("❌ LOSS", f"{losses} Kali")
    
    st.divider()

    # 4. MONITORING HARGA & RSI
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.metric("BTC PRICE", f"${last_row['Harga']:,.2f}")
        st.write(f"⏱️ {last_row['Timestamp']}")
    with col_b:
        status_color = "#00FF00" if "BUY" in last_row['Signal'] else "#FF4B4B" if "SELL" in last_row['Signal'] else "#FFA500"
        st.markdown(f"<div style='background: #1e2130; padding: 15px; border-radius: 10px; border-left: 5px solid {status_color};'>"
                    f"<p style='color: white; margin:0;'>ACTION: <b style='color:{status_color};'>{last_row['Signal']}</b></p></div>", unsafe_allow_html=True)

    # 5. CHART
    st.subheader("📈 Market Intelligence Map")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Timestamp'], y=data['Harga'], mode='lines', name='Price', line=dict(color='#ff9900', width=2)))
    
    # Tambah Marker
    buys = data[data['Signal'].str.contains("BUY", na=False)]
    fig.add_trace(go.Scatter(x=buys['Timestamp'], y=buys['Harga'], mode='markers', name='BUY', marker=dict(symbol='triangle-up', size=12, color='#00FF00')))
    
    sells = data[data['Signal'].str.contains("SELL", na=False)]
    fig.add_trace(go.Scatter(x=sells['Timestamp'], y=sells['Harga'], mode='markers', name='SELL', marker=dict(symbol='triangle-down', size=12, color='#FF4B4B')))

    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")

st.markdown("<p style='text-align: center; font-size: 10px; color: #444;'>ROSIT GOLD AI v2.0</p>", unsafe_allow_html=True)
