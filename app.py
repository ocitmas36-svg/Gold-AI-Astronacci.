import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# 1. KONFIGURASI HALAMAN UTAMA
# ==========================================
st.set_page_config(page_title="ROSIT GOLD AI", page_icon="🦅", layout="wide")

# ==========================================
# 2. INJEKSI CSS KELAS DUNIA (DARK MODE & GOLD)
# ==========================================
st.markdown("""
    <style>
    /* Background Hitam Pekat & Font */
    .stApp { background-color: #0b0e14; }
    
    /* Header Emas Mewah */
    .gold-header {
        background: linear-gradient(90deg, #bf953f, #fcf6ba, #b38728, #fbf5b7, #aa771c);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-top: -30px;
        margin-bottom: 15px;
        box-shadow: 0px 5px 20px rgba(191, 149, 63, 0.3);
    }
    .gold-header h1 { color: #000 !important; margin: 0; font-size: 26px; font-weight: 900; letter-spacing: 1px;}
    .gold-header p { color: #222 !important; margin: 0; font-size: 11px; font-weight: bold; }

    /* Custom Menu Tabs (Biar persis di foto) */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; background-color: transparent; justify-content: space-between; padding: 0;}
    .stTabs [data-baseweb="tab"] {
        height: 40px; background-color: #161a25; border-radius: 8px; color: #888;
        padding: 5px 15px; border: 1px solid #2a2e39; font-size: 12px; font-weight: bold; width: 25%;
    }
    .stTabs [aria-selected="true"] { background-color: #1e2330 !important; color: #ffcc00 !important; border-bottom: 3px solid #ffcc00 !important; }

    /* Kotak Harga & Title */
    .price-title { color: #ffcc00; font-size: 14px; font-weight: bold; margin-bottom: -10px; }
    .price-value { color: #ffffff; font-size: 32px; font-weight: 900; }
    .price-change { color: #00ff00; font-size: 16px; font-weight: bold; margin-left: 10px; }

    /* Kotak Statistik Bawah (3 Kolom) */
    .stat-box {
        background-color: #161a25; border: 1px solid #2a2e39;
        border-radius: 12px; padding: 15px 10px; text-align: center;
    }
    .stat-label { color: #888; font-size: 10px; font-weight: bold; margin-bottom: 5px; }
    .stat-val-y { color: #ffcc00; font-size: 20px; font-weight: bold; }
    .stat-val-g { color: #00ff00; font-size: 20px; font-weight: bold; }
    .stat-val-r { color: #ff4b4b; font-size: 20px; font-weight: bold; }

    /* Kotak Sinyal Live (Hijau) */
    .live-signal-box {
        background-color: #081a0b; border: 1px solid #00ff00;
        border-radius: 15px; padding: 20px; margin-top: 15px;
        box-shadow: 0px 0px 15px rgba(0, 255, 0, 0.1);
    }
    .execute-btn {
        background: linear-gradient(90deg, #bf953f, #fcf6ba, #b38728);
        color: black; padding: 12px; border-radius: 8px; font-weight: 900;
        text-align: center; margin-top: 15px; font-size: 14px; letter-spacing: 1px;
    }
    
    /* Hilangkan padding default Streamlit */
    .block-container { padding-top: 2rem; padding-bottom: 0rem; max-width: 600px; } /* max-width agar bentuknya seperti HP di web */
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. HEADER EMAS (MOCKUP)
# ==========================================
st.markdown("""
    <div class="gold-header">
        <h1>🦅 ROSIT GOLD AI</h1>
        <p>Proprietary Quantitative Trading Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. LOAD DATA DARI GOOGLE SHEETS
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ygHIdUszMkTGiG0WZKe3l39tkIdFmid86WP6KTErlPo/export?format=csv"

@st.cache_data(ttl=15)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = ['Timestamp', 'Waktu', 'Harga', 'RSI_M1', 'RSI_H1', 'Signal']
    df['Harga'] = pd.to_numeric(df['Harga'], errors='coerce')
    df['RSI_M1'] = pd.to_numeric(df['RSI_M1'], errors='coerce')
    return df.dropna(subset=['Harga'])

try:
    data = load_data()
    last_row = data.iloc[-1]
    
    # Kalkulasi Performa Bot
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
    # 5. MENU NAVIGASI TABS
    # ==========================================
    tab1, tab2, tab3, tab4 = st.tabs(["DASHBOARD", "ANALYSIS", "HISTORY", "SETTINGS"])

    with tab1:
        # A. Harga Live XAU/USD (Atas Kiri)
        st.markdown(f"""
            <div class="price-title">🪙 XAU/USD (Gold) / BTC</div>
            <div>
                <span class="price-value">${last_row['Harga']:,.2f}</span>
                <span class="price-change">(+1.12%) ↗</span>
            </div>
            <div style="margin-bottom: 10px;"></div>
        """, unsafe_allow_html=True)

        # B. GRAFIK UTAMA & SPEEDOMETER BERSANDINGAN
        col_chart, col_rsi = st.columns([2.5, 1])
        
        with col_chart:
            # Grafik Garis Harga (Kuning Emas)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data['Timestamp'], y=data['Harga'], mode='lines', line=dict(color='#ffcc00', width=2)))
            
            # Marker Buy & Sell
            buys = data[data['Signal'].str.contains("BUY", na=False)]
            fig.add_trace(go.Scatter(x=buys['Timestamp'], y=buys['Harga'], mode='markers', marker=dict(symbol='triangle-up', size=12, color='#00ff00')))
            
            sells = data[data['Signal'].str.contains("SELL", na=False)]
            fig.add_trace(go.Scatter(x=sells['Timestamp'], y=sells['Harga'], mode='markers', marker=dict(symbol='triangle-down', size=12, color='#ff4b4b')))
            
            fig.update_layout(
                template="plotly_dark", height=220, margin=dict(l=0,r=0,t=0,b=0), 
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False,
                xaxis=dict(visible=False), yaxis=dict(visible=False) # Hilangkan grid agar bersih seperti di foto
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_rsi:
            # Speedometer RSI 
            fig_rsi = go.Figure(go.Indicator(
                mode = "gauge+number", value = last_row['RSI_M1'], number={'font':{'size':24, 'color':'white'}},
                gauge = {
                    'axis': {'range': [0, 100], 'visible': False}, 
                    'bar': {'color': "#ffcc00", 'thickness': 0.2},
                    'bgcolor': "#161a25", 'borderwidth': 0
                },
                domain = {'x': [0, 1], 'y': [0, 1]}
            ))
            fig_rsi.update_layout(height=150, margin=dict(l=10,r=10,t=20,b=0), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_rsi, use_container_width=True)
            
            trend_text = "BULLISH" if last_row['RSI_M1'] > 50 else "BEARISH"
            trend_color = "#00ff00" if trend_text == "BULLISH" else "#ff4b4b"
            st.markdown(f"<div style='text-align:center; margin-top:-20px;'><small style='color:#888;'>MOMENTUM</small><br><b style='color:{trend_color}; font-size:12px;'>TREND: {trend_text}</b></div>", unsafe_allow_html=True)

        # C. KOTAK STATISTIK BAWAH (3 Kolom)
        st.write("")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='stat-box'><div class='stat-label'>📊 WIN RATE:</div><div class='stat-val-y'>{wr:.1f}%</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='stat-box'><div class='stat-label'>✅ TOTAL WIN:</div><div class='stat-val-g'>{wins} Trades</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='stat-box'><div class='stat-label'>❌ TOTAL LOSS:</div><div class='stat-val-r'>{losses} Trades</div></div>", unsafe_allow_html=True)

        # D. KOTAK LIVE AI SIGNAL (Eksekusi)
        # Simulasi Target (TP) dan Stop (SL) biar persis di foto
        tp = last_row['Harga'] + 10 if "BUY" in last_row['Signal'] else last_row['Harga'] - 10
        sl = last_row['Harga'] - 5 if "BUY" in last_row['Signal'] else last_row['Harga'] + 5
        sig_color = "#00ff00" if "BUY" in last_row['Signal'] else "#ff4b4b" if "SELL" in last_row['Signal'] else "#ffcc00"
        
        st.markdown(f"""
            <div class="live-signal-box">
                <div style="color:#00ff00; font-size:14px; font-weight:bold; margin-bottom:10px;">LIVE AI SIGNAL</div>
                <div style="color:#bbb; font-size:12px;">
                    SIGNAL: <b style="color:{sig_color};">{last_row['Signal']} @ {last_row['Harga']:,.2f}</b> | TARGET: {tp:,.2f} | STOP: {sl:,.2f}
                </div>
                <div class="execute-btn">EXECUTE TRADE</div>
            </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.info("Pusat Analisis Teknikal mendalam sedang disiapkan.")
        st.dataframe(data.tail(10))

    with tab3:
        st.markdown("### 📜 Buku Besar Riwayat Transaksi")
        st.dataframe(data.sort_values(by='Timestamp', ascending=False), use_container_width=True)
        
    with tab4:
        st.warning("Pengaturan API dan Notifikasi Telegram.")

except Exception as e:
    st.error(f"Menghubungkan ke server satelit... ({e})")

st.markdown("<p style='text-align: center; font-size: 10px; color: #333; margin-top:30px;'>ROSIT GOLD AI - V4.0 ULTIMATE</p>", unsafe_allow_html=True)
    
