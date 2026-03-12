import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="ROSIT GOLD AI PRO", page_icon="💰", layout="wide")

# 2. CSS CUSTOM UNTUK TAMPILAN PREMIUM (MIRIP FOTO)
st.markdown("""
    <style>
    /* Background Utama */
    .main { background-color: #000000; }
    
    /* Header Emas */
    .gold-header {
        background: linear-gradient(90deg, #bf953f, #fcf6ba, #b38728, #fbf5b7, #aa771c);
        padding: 20px;
        border-radius: 0px 0px 20px 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    .gold-header h1 { color: #000 !important; margin: 0; font-size: 28px; font-weight: 800; }
    .gold-header p { color: #333 !important; margin: 0; font-weight: 600; font-size: 12px; }

    /* Gaya Tabs (Menu) */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 8px; 
        background-color: #111;
        padding: 10px;
        border-radius: 15px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e1e1e;
        border-radius: 10px;
        color: white;
        padding: 10px 20px;
        border: 1px solid #333;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff9900 !important;
        color: black !important;
        border: none !important;
    }

    /* Card Stats */
    .stat-card {
        background-color: #161a1e;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #2a2e33;
        text-align: center;
    }
    
    /* Live Signal Box */
    .live-signal {
        background-color: #0d1f12;
        border: 1px solid #00ff00;
        padding: 15px;
        border-radius: 15px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER EMAS ---
st.markdown("""
    <div class="gold-header">
        <h1>ROSIT GOLD AI</h1>
        <p>Proprietary Quantitative Trading Intelligence</p>
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
    
    # Hitung Performa
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

    # --- MENU SISTEM TABS ---
    tab1, tab2, tab3 = st.tabs(["🏠 DASHBOARD", "📈 ANALYSIS", "📜 HISTORY"])

    with tab1:
        # LIVE PRICE & MOMENTUM
        col_p1, col_p2 = st.columns([1, 1])
        with col_p1:
            st.markdown(f"""
                <div class="stat-card">
                    <p style='color:grey; margin:0;'>XAU/USD (GOLD)</p>
                    <h2 style='color:white; margin:0;'>${last_row['Harga']:,.2f}</h2>
                    <p style='color:#00ff00; margin:0;'>▲ +1.12%</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col_p2:
            # Gauge RSI Minimalis
            fig_rsi = go.Figure(go.Indicator(
                mode = "gauge+number", value = last_row['RSI_M1'],
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#ff9900"}, 'bgcolor': "#222"},
                domain = {'x': [0, 1], 'y': [0, 1]}
            ))
            fig_rsi.update_layout(height=120, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
            st.plotly_chart(fig_rsi, use_container_width=True)

        # WIN RATE STATS
        st.write("")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='stat-card'><small>WIN RATE</small><br><b style='color:#ff9900; font-size:20px;'>{wr:.1f}%</b></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='stat-card'><small>TOTAL WIN</small><br><b style='color:#00ff00; font-size:20px;'>{wins}</b></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='stat-card'><small>TOTAL LOSS</small><br><b style='color:#ff4b4b; font-size:20px;'>{losses}</b></div>", unsafe_allow_html=True)

        # LIVE SIGNAL BOX
        status_c = "#00FF00" if "BUY" in last_row['Signal'] else "#FF4B4B" if "SELL" in last_row['Signal'] else "#FFA500"
        st.markdown(f"""
            <div class="live-signal">
                <p style='color:#00ff00; margin:0; font-weight:bold;'>📡 LIVE AI SIGNAL</p>
                <p style='color:white; margin:5px 0;'>SIGNAL: <b style='color:{status_c}'>{last_row['Signal']}</b> @ {last_row['Harga']}</p>
                <div style='background:#ff9900; color:black; text-align:center; border-radius:10px; padding:5px; font-weight:bold;'>EXECUTE TRADE</div>
            </div>
        """, unsafe_allow_html=True)

    with tab2:
        # GRAFIK ANALISIS
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['Timestamp'], y=data['Harga'], mode='lines', name='Price', line=dict(color='#ff9900', width=2), fill='tozeroy', fillcolor='rgba(255,153,0,0.05)'))
        
        buys = data[data['Signal'].str.contains("BUY", na=False)]
        fig.add_trace(go.Scatter(x=buys['Timestamp'], y=buys['Harga'], mode='markers', name='BUY', marker=dict(symbol='triangle-up', size=15, color='#00FF00')))
        
        sells = data[data['Signal'].str.contains("SELL", na=False)]
        fig.add_trace(go.Scatter(x=sells['Timestamp'], y=sells['Harga'], mode='markers', name='SELL', marker=dict(symbol='triangle-down', size=15, color='#FF4B4B')))
        
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='black', plot_bgcolor='black')
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.markdown("### 📜 Trade History Log")
        st.dataframe(data.sort_values(by='Timestamp', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Syncing with Rosit AI Engine... {e}")

st.markdown("<p style='text-align: center; font-size: 10px; color: #444; margin-top:30px;'>ROSIT GOLD AI - GLOBAL EDITION v3.0</p>", unsafe_allow_html=True)
