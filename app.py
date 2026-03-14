import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# 1. KONFIGURASI HALAMAN UTAMA
# ==========================================
st.set_page_config(page_title="ROSIT GOLD AI", page_icon="🦅", layout="wide")

# ==========================================
# 2. INJEKSI CSS PREMIUM (DARK MODE & GOLD)
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
    .stat-val-r { color: #ff4b4b; font-size: 20px; font-weight: bold; }

    /* Kotak Sinyal Live */
    .live-signal-box {
        background-color: #081a0b; border: 1px solid #00ff00;
        border-radius: 15px; padding: 20px; margin-top: 15px;
    }
    .execute-btn {
        background: linear-gradient(90deg, #bf953f, #fcf6ba, #b38728);
        color: black; padding: 12px; border-radius: 10px; font-weight: 900;
        text-align: center; margin-top: 15px; font-size: 14px;
    }
    
    .block-container { padding-top: 2rem; max-width: 700px; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="gold-header">
        <h1>🦅 ROSIT GOLD AI</h1>
        <p>Proprietary Quantitative Trading Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LOAD DATA (SYNC GOOGLE SHEETS)
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ygHIdUszMkTGiG0WZKe3l39tkIdFmid86WP6KTErlPo/export?format=csv"

@st.cache_data(ttl=15)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = ['Timestamp', 'Waktu', 'Harga', 'RSI_M1', 'RSI_H1', 'Signal']
        df['Harga'] = pd.to_numeric(df['Harga'], errors='coerce')
        df['RSI_M1'] = pd.to_numeric(df['RSI_M1'], errors='coerce')
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
    total = wins + losses
    wr = (wins / total * 100) if total > 0 else 0

    # ==========================================
    # 4. MENU NAVIGASI TABS
    # ==========================================
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 DASHBOARD", "📈 ANALYSIS", "📜 HISTORY", "⚙️ SETTINGS"])

    with tab1:
        # LIVE PRICE
        st.markdown(f"""
            <div style="color:#ffcc00; font-size:14px; font-weight:bold;">🪙 XAU/USD (GOLD) / BTC</div>
            <div style="margin-bottom:15px;">
                <span style="color:white; font-size:32px; font-weight:900;">${last_row['Harga']:,.2f}</span>
                <span style="color:#00ff00; font-size:16px; font-weight:bold; margin-left:10px;">↗ LIVE</span>
            </div>
        """, unsafe_allow_html=True)

        # GRAFIK & RSI SPEEDO
        col_chart, col_rsi = st.columns([2.5, 1])
        
        with col_chart:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data['Timestamp'].tail(50), y=data['Harga'].tail(50), mode='lines', line=dict(color='#ffcc00', width=2)))
            fig.update_layout(template="plotly_dark", height=200, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False))
            st.plotly_chart(fig, use_container_width=True)

        with col_rsi:
            fig_rsi = go.Figure(go.Indicator(
                mode = "gauge+number", value = last_row['RSI_M1'], number={'font':{'size':20, 'color':'white'}},
                gauge = {'axis': {'range': [0, 100], 'visible': False}, 'bar': {'color': "#ffcc00", 'thickness': 0.2}, 'bgcolor': "#161a25"}
            ))
            fig_rsi.update_layout(height=140, margin=dict(l=10,r=10,t=20,b=0), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_rsi, use_container_width=True)
            st.markdown("<p style='text-align:center; color:#888; font-size:10px; margin-top:-20px;'>MOMENTUM RSI</p>", unsafe_allow_html=True)

        # KOTAK SKOR
        st.write("")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='stat-box'><div class='stat-label'>WIN RATE</div><div class='stat-val-y'>{wr:.1f}%</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='stat-box'><div class='stat-label'>TOTAL WIN</div><div class='stat-val-g'>{wins}</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='stat-box'><div class='stat-label'>TOTAL LOSS</div><div class='stat-val-r'>{losses}</div></div>", unsafe_allow_html=True)

        # LIVE SIGNAL BOX
        sig_color = "#00ff00" if "BUY" in last_row['Signal'] else "#ff4b4b" if "SELL" in last_row['Signal'] else "#ffcc00"
        st.markdown(f"""
            <div class="live-signal-box">
                <div style="color:#00ff00; font-size:12px; font-weight:bold;">📡 LIVE AI SIGNAL</div>
                <div style="color:white; font-size:18px; margin:10px 0;"><b>{last_row['Signal']}</b> @ {last_row['Harga']:,.2f}</div>
                <div class="execute-btn">EXECUTE TRADE</div>
            </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### 📈 Market Analysis")
        st.write("Sinyal terakhir yang terdeteksi oleh sistem:")
        st.table(data.tail(5)[['Waktu', 'Harga', 'Signal']])

    with tab3:
        st.markdown("### 📜 Trading History (Signals Only)")
        # --- FILTER: HANYA BUY & SELL (HAPUS NGOPI) ---
        history_cuan = data[~data['Signal'].str.contains("NGOPI", na=False, case=False)]
        if not history_cuan.empty:
            st.dataframe(history_cuan.sort_values(by='Timestamp', ascending=False), use_container_width=True)
        else:
            st.info("Belum ada transaksi Buy/Sell. Bot masih memantau.")

    with tab4:
        st.markdown("### ⚙️ Settings")
        st.text_input("WhatsApp Number", value="088980942762")
        st.text_input("Telegram Chat ID", value="6979633512")
        st.button("Update Configuration")

else:
    st.error("Gagal mengambil data. Pastikan Google Sheets sudah terisi.")

st.markdown("<p style='text-align: center; font-size: 10px; color: #333; margin-top:30px;'>ROSIT GOLD AI - V4.0 FINAL</p>", unsafe_allow_html=True)
