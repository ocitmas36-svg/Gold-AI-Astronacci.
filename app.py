import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. SETTING HALAMAN
st.set_page_config(page_title="ROSIT GOLD AI PRO", page_icon="💰", layout="wide")

# CSS Agar Mirip App Asli
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        height: 45px; white-space: pre-wrap; background-color: #1e2130;
        border-radius: 10px; color: white; padding: 10px 20px; border: 1px solid #3e4255;
    }
    .stTabs [aria-selected="true"] { border: 1px solid #ff9900 !important; color: #ff9900 !important; }
    .stMetric { background-color: #1e2130 !important; border-radius: 10px; border: 1px solid #3e4255; padding: 10px; }
    h1 { color: #ff9900; text-align: center; font-size: 24px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🛰️ ROSIT GOLD AI PRO</h1>", unsafe_allow_html=True)

# 2. LOAD DATA
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
    
    # Hitung Win Rate
    wins, losses = 0, 0
    in_pos = False
    entry = 0
    for i, r in data.iterrows():
        sig = str(r['Signal']).upper()
        if "BUY" in sig and not in_pos: in_pos, entry = True, r['Harga']
        elif "SELL" in sig and in_pos:
            in_pos = False
            if r['Harga'] > entry: wins += 1
            else: losses += 1
    wr = (wins/(wins+losses)*100) if (wins+losses) > 0 else 0

    # --- MENU TAB PROFESIONAL ---
    tab1, tab2, tab3 = st.tabs(["🏠 DASHBOARD", "📈 ANALYSIS", "📜 HISTORY"])

    # TAB 1: DASHBOARD (Ringkasan Cepat)
    with tab1:
        st.markdown("### Market Status")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("BTC PRICE", f"${last_row['Harga']:,.2f}")
        with c2:
            sc = "#00FF00" if "BUY" in last_row['Signal'] else "#FF4B4B" if "SELL" in last_row['Signal'] else "#FFA500"
            st.markdown(f"<div style='background:#1e2130; padding:10px; border-radius:10px; border-left:5px solid {sc};'>"
                        f"<small>SIGNAL</small><br><b style='color:{sc}; font-size:20px;'>{last_row['Signal']}</b></div>", unsafe_allow_html=True)
        
        st.write("")
        st.markdown("### AI Performance")
        m1, m2 = st.columns(2)
        m1.metric("WIN RATE", f"{wr:.1f}%")
        m2.metric("TOTAL WIN", f"{wins} Trades")

    # TAB 2: ANALYSIS (Grafik & Indikator)
    with tab2:
        st.subheader("Technical Chart")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['Timestamp'], y=data['Harga'], mode='lines', name='Price', line=dict(color='#ff9900', width=2)))
        
        # Penanda Buy/Sell
        buys = data[data['Signal'].str.contains("BUY", na=False)]
        fig.add_trace(go.Scatter(x=buys['Timestamp'], y=buys['Harga'], mode='markers', name='BUY', marker=dict(symbol='triangle-up', size=12, color='#00FF00')))
        sells = data[data['Signal'].str.contains("SELL", na=False)]
        fig.add_trace(go.Scatter(x=sells['Timestamp'], y=sells['Harga'], mode='markers', name='SELL', marker=dict(symbol='triangle-down', size=12, color='#FF4B4B')))
        
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        st.metric("RSI MOMENTUM", f"{last_row['RSI_M1']}")

    # TAB 3: HISTORY (Data Riwayat)
    with tab3:
        st.subheader("Trade Logs")
        st.dataframe(data.sort_values(by='Timestamp', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Connecting to AI... {e}")

st.markdown("<p style='text-align: center; font-size: 10px; color: #444; margin-top:50px;'>ROSIT GOLD AI PRO v2.1</p>", unsafe_allow_html=True)
