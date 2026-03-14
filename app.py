import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. KONFIGURASI HALAMAN UTAMA
# ==========================================
st.set_page_config(page_title="ROSIT QUANT AI", page_icon="🦅", layout="wide")

# ==========================================
# 2. INJEKSI CSS PREMIUM (DARK, GOLD & FLOATING BUTTON)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    
    /* Header Emas */
    .gold-header {
        background: linear-gradient(90deg, #bf953f, #fcf6ba, #b38728, #fbf5b7, #aa771c);
        padding: 20px; border-radius: 15px; text-align: center;
        margin-top: -30px; margin-bottom: 15px;
        box-shadow: 0px 5px 20px rgba(191, 149, 63, 0.3);
    }
    .gold-header h1 { color: #000 !important; margin: 0; font-size: 26px; font-weight: 900; }
    .gold-header p { color: #222 !important; margin: 0; font-size: 11px; font-weight: bold; }

    /* Custom Menu Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 45px; background-color: #161a25; border-radius: 10px; color: #888;
        padding: 5px 15px; border: 1px solid #2a2e39; font-size: 12px; font-weight: bold;
    }
    .stTabs [aria-selected="true"] { background-color: #1e2330 !important; color: #ffcc00 !important; border-bottom: 3px solid #ffcc00 !important; }

    /* Kotak Statistik */
    .stat-box {
        background-color: #161a25; border: 1px solid #2a2e39;
        border-radius: 12px; padding: 15px 10px; text-align: center; margin-bottom: 10px;
    }
    .stat-label { color: #888; font-size: 10px; font-weight: bold; }
    .stat-val-y { color: #ffcc00; font-size: 20px; font-weight: bold; }
    .stat-val-g { color: #00ff00; font-size: 20px; font-weight: bold; }

    /* Live Signal Box */
    .live-signal-box {
        background-color: #081a0b; border: 1px solid #00ff00;
        border-radius: 15px; padding: 20px; margin-top: 15px;
    }
    
    /* Market Health Badge */
    .health-badge {
        display: inline-block; padding: 2px 10px; border-radius: 20px;
        font-size: 10px; font-weight: bold; margin-bottom: 10px;
    }

    /* Floating WhatsApp Button */
    .float-wa {
        position: fixed; width: 60px; height: 60px; bottom: 20px; right: 20px;
        background-color: #25d366; color: white; border-radius: 50px;
        text-align: center; font-size: 30px; box-shadow: 2px 2px 3px #999; z-index: 100;
    }
    
    .block-container { padding-top: 2rem; max-width: 700px; }
    </style>
    
    <a href="https://wa.me/6288980942762" class="float-wa" target="_blank">
        <i style="margin-top:16px; display:inline-block;">💬</i>
    </a>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="gold-header">
        <h1>🦅 ROSIT QUANT AI</h1>
        <p>Advanced Algorithmic Trading Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DATA ENGINE
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ygHIdUszMkTGiG0WZKe3l39tkIdFmid86WP6KTErlPo/export?format=csv"

@st.cache_data(ttl=15)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = ['Timestamp', 'Waktu', 'Harga', 'RSI_M1', 'RSI_H1', 'Signal']
        df['Harga'] = pd.to_numeric(df['Harga'], errors='coerce')
        df['RSI_M1'] = pd.to_numeric(df['RSI_M1'], errors='coerce')
        # Tambahkan Trend Line (Moving Average)
        df['MA_Trend'] = df['Harga'].rolling(window=15).mean()
        return df.dropna(subset=['Harga'])
    except:
        return pd.DataFrame()

data = load_data()

if not data.empty:
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
    wr = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0

    # ==========================================
    # 4. MENU NAVIGASI TABS
    # ==========================================
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 DASHBOARD", "📈 ANALYSIS", "📜 HISTORY", "⚙️ CONTACT"])

    with tab1:
        # MARKET HEALTH INDICATOR
        volatility = abs(data['Harga'].iloc[-1] - data['Harga'].iloc[-5])
        health_status = "TRENDY" if volatility > 2 else "SIDEWAYS"
        health_color = "#00ff00" if health_status == "TRENDY" else "#ffcc00"
        
        st.markdown(f"""
            <div class="health-badge" style="border: 1px solid {health_color}; color: {health_color};">
                MARKET STATUS: {health_status}
            </div>
        """, unsafe_allow_html=True)

        # LIVE PRICE
        st.markdown(f"""
            <div style="color:#ffcc00; font-size:14px; font-weight:bold;">🪙 XAU/USD (GOLD) / BTC</div>
            <div style="margin-bottom:15px;">
                <span style="color:white; font-size:32px; font-weight:900;">${last_row['Harga']:,.2f}</span>
                <span style="color:#00ff00; font-size:16px; font-weight:bold; margin-left:10px;">↗ LIVE</span>
            </div>
        """, unsafe_allow_html=True)

        # GRAFIK DENGAN TREND LINE (MA)
        col_chart, col_rsi = st.columns([2.5, 1])
        
        with col_chart:
            fig = go.Figure()
            # Harga Utama
            fig.add_trace(go.Scatter(x=data['Timestamp'].tail(40), y=data['Harga'].tail(40), 
                                     mode='lines', name='Price', line=dict(color='#ffcc00', width=3)))
            # Trend Line (MA) - Menunjukkan "Otak" Bot
            fig.add_trace(go.Scatter(x=data['Timestamp'].tail(40), y=data['MA_Trend'].tail(40), 
                                     mode='lines', name='Trend', line=dict(color='#444', width=1, dash='dash')))
            
            # Sinyal Markers
            buys = data[data['Signal'].str.contains("BUY", na=False)].tail(5)
            fig.add_trace(go.Scatter(x=buys['Timestamp'], y=buys['Harga'], mode='markers', marker=dict(symbol='triangle-up', size=15, color='#00ff00')))
            
            fig.update_layout(template="plotly_dark", height=200, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False))
            st.plotly_chart(fig, use_container_width=True)

        with col_rsi:
            fig_rsi = go.Figure(go.Indicator(
                mode = "gauge+number", value = last_row['RSI_M1'], number={'font':{'size':18, 'color':'white'}},
                gauge = {'axis': {'range': [0, 100], 'visible': False}, 'bar': {'color': "#ffcc00", 'thickness': 0.2}, 'bgcolor': "#161a25"}
            ))
            fig_rsi.update_layout(height=130, margin=dict(l=5,r=5,t=20,b=0), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_rsi, use_container_width=True)
            st.markdown("<p style='text-align:center; color:#888; font-size:9px; margin-top:-15px;'>MOMENTUM</p>", unsafe_allow_html=True)

        # KOTAK SKOR
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='stat-box'><div class='stat-label'>WIN RATE</div><div class='stat-val-y'>{wr:.1f}%</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='stat-box'><div class='stat-label'>TOTAL WIN</div><div class='stat-val-g'>{wins}</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='stat-box'><div class='stat-label'>TREND</div><div style='color:white; font-size:18px;'>{'UP' if last_row['Harga'] > last_row['MA_Trend'] else 'DOWN'}</div></div>", unsafe_allow_html=True)

        # LIVE SIGNAL BOX & AI NOTE
        sig_color = "#00ff00" if "BUY" in last_row['Signal'] else "#ff4b4b" if "SELL" in last_row['Signal'] else "#ffcc00"
        st.markdown(f"""
            <div class="live-signal-box">
                <div style="color:#00ff00; font-size:12px; font-weight:bold;">🦅 LIVE AI SIGNAL</div>
                <div style="color:white; font-size:18px; margin:10px 0;"><b>{last_row['Signal']}</b> @ {last_row['Harga']:,.2f}</div>
                <hr style="border: 0.1px solid #222;">
                <p style="color:#888; font-size:11px; font-style:italic;">
                    <b>AI Strategic Note:</b> Market confirms {health_status.lower()} condition. 
                    Signal generated based on Quant Triple-Confirm Logic.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### 📈 Quant Analytics")
        st.table(data.tail(10)[['Waktu', 'Harga', 'Signal', 'RSI_M1']])

    with tab3:
        st.markdown("### 📜 Signal Journal")
        history_cuan = data[~data['Signal'].str.contains("NGOPI", na=False, case=False)]
        st.dataframe(history_cuan.sort_values(by='Timestamp', ascending=False), use_container_width=True)

    with tab4:
        st.markdown("### ⚙️ Contact & VIP Access")
        st.write("Tertarik menggunakan Rosit Quant AI untuk akun pribadi Anda?")
        st.link_button("Chat Admin (WhatsApp)", "https://wa.me/6288980942762")
        st.link_button("Follow Instagram", "https://instagram.com/ya_rositt")

else:
    st.error("Engine sedang sinkronisasi data...")

st.markdown("<p style='text-align: center; font-size: 10px; color: #444; margin-top:30px;'>ROSIT QUANT AI v5.0 - PRO EDITION</p>", unsafe_allow_html=True)
    
