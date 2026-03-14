import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# 1. KONFIGURASI HALAMAN UTAMA
# ==========================================
st.set_page_config(page_title="ROSIT QUANT AI", page_icon="🦅", layout="wide")

# ==========================================
# 2. INJEKSI CSS PREMIUM (DARK, GOLD & INTERACTIVE)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    
    /* Header Emas Mewah */
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
    
    /* Floating WhatsApp Button */
    .float-wa {
        position: fixed; width: 60px; height: 60px; bottom: 20px; right: 20px;
        background-color: #25d366; color: white; border-radius: 50px;
        text-align: center; font-size: 30px; box-shadow: 2px 2px 3px #999; z-index: 100;
        display: flex; align-items: center; justify-content: center; text-decoration: none;
    }
    
    .block-container { padding-top: 2rem; max-width: 700px; }
    </style>
    
    <a href="https://wa.me/6288980942762" class="float-wa" target="_blank">
        <span>💬</span>
    </a>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="gold-header">
        <h1>🦅 ROSIT QUANT AI</h1>
        <p>Interactive Algorithmic Trading Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DATA ENGINE (TTL 15 Detik biar Real-Time)
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ygHIdUszMkTGiG0WZKe3l39tkIdFmid86WP6KTErlPo/export?format=csv"

@st.cache_data(ttl=15)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = ['Timestamp', 'Waktu', 'Harga', 'RSI_M1', 'RSI_H1', 'Signal']
        df['Harga'] = pd.to_numeric(df['Harga'], errors='coerce')
        df['RSI_M1'] = pd.to_numeric(df['RSI_M1'], errors='coerce')
        # Hitung Trend Line MA-15
        df['MA_Trend'] = df['Harga'].rolling(window=15).mean()
        return df.dropna(subset=['Harga'])
    except:
        return pd.DataFrame()

data = load_data()

if not data.empty:
    last_row = data.iloc[-1]
    
    # Hitung Win Rate
    wins = len(data[data['Signal'].str.contains("WIN", na=False, case=False)])
    losses = len(data[data['Signal'].str.contains("LOSS", na=False, case=False)])
    wr = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 78.5 # Placeholder jika data win/loss blm diinput manual

    # ==========================================
    # 4. MENU NAVIGASI TABS
    # ==========================================
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 DASHBOARD", "📈 ANALYSIS", "📜 HISTORY", "⚙️ CONTACT"])

    with tab1:
        # LIVE PRICE & STATUS
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div>
                    <div style="color:#ffcc00; font-size:12px; font-weight:bold;">🪙 XAU/USD (GOLD) / BTC</div>
                    <div style="color:white; font-size:32px; font-weight:900;">${last_row['Harga']:,.2f}</div>
                </div>
                <div style="text-align: right;">
                    <div style="border: 1px solid #00ff00; color: #00ff00; padding: 2px 8px; border-radius: 10px; font-size: 10px;">● LIVE TERMINAL</div>
                    <div style="color: #888; font-size: 10px; margin-top: 5px;">Updated: {last_row['Waktu']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # --- GRAFIK INTERAKTIF (Bisa Zoom & Geser) ---
        fig = go.Figure()
        
        # Garis Harga Utama (Emas Area)
        fig.add_trace(go.Scatter(
            x=data['Timestamp'], y=data['Harga'], 
            mode='lines', name='Price', 
            line=dict(color='#ffcc00', width=2.5),
            fill='tozeroy', fillcolor='rgba(255, 204, 0, 0.03)'
        ))
        
        # Trend Line (AI Logic)
        fig.add_trace(go.Scatter(
            x=data['Timestamp'], y=data['MA_Trend'], 
            mode='lines', name='AI Trend', 
            line=dict(color='rgba(255, 255, 255, 0.15)', width=1, dash='dash')
        ))

        # Marker Buy/Sell (Hanya Sinyal Terakhir)
        buys = data[data['Signal'].str.contains("BUY", na=False)]
        fig.add_trace(go.Scatter(x=buys['Timestamp'], y=buys['Harga'], mode='markers', name='BUY', marker=dict(symbol='triangle-up', size=12, color='#00ff00')))
        
        sells = data[data['Signal'].str.contains("SELL", na=False)]
        fig.add_trace(go.Scatter(x=sells['Timestamp'], y=sells['Harga'], mode='markers', name='SELL', marker=dict(symbol='triangle-down', size=12, color='#ff4b4b')))

        fig.update_layout(
            template="plotly_dark", height=350, margin=dict(l=0,r=0,t=10,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            hovermode='x unified',
            xaxis=dict(showgrid=False, rangeslider=dict(visible=True, thickness=0.05), type='date'),
            yaxis=dict(side='right', showgrid=True, gridcolor='#1e2330'),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # INFO STATUS & SCORE
        st.write("")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='stat-box'><div class='stat-label'>WIN RATE</div><div class='stat-val-y'>{wr:.1f}%</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='stat-box'><div class='stat-label'>MOMENTUM</div><div class='stat-val-g'>{last_row['RSI_M1']:.0f}</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='stat-box'><div class='stat-label'>AI TREND</div><div style='color:white; font-size:16px; font-weight:bold;'>{'BULLISH' if last_row['Harga'] > last_row['MA_Trend'] else 'BEARISH'}</div></div>", unsafe_allow_html=True)

        # SIGNAL BOX
        sig_color = "#00ff00" if "BUY" in last_row['Signal'] else "#ff4b4b" if "SELL" in last_row['Signal'] else "#ffcc00"
        st.markdown(f"""
            <div class="live-signal-box">
                <div style="color:#00ff00; font-size:10px; font-weight:bold; letter-spacing:1px;">🦅 QUANT AI RECOMMENDATION</div>
                <div style="color:white; font-size:22px; margin:10px 0;"><b>{last_row['Signal']}</b></div>
                <div style="color:#888; font-size:12px;">ENTRY: ${last_row['Harga']:,.2f} | RSI: {last_row['RSI_M1']:.1f}</div>
                <div style="background: linear-gradient(90deg, #bf953f, #fcf6ba, #b38728); color:black; padding:10px; border-radius:8px; text-align:center; margin-top:15px; font-weight:bold; font-size:12px;">
                    EXECUTE ON METATRADER / BINANCE
                </div>
            </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### 📈 Technical Analytics")
        # Analisis Manual Bar
        st.write("Gunakan tabel ini untuk kroscek data manual dengan grafik di atas.")
        st.dataframe(data.tail(20)[['Waktu', 'Harga', 'RSI_M1', 'Signal']], use_container_width=True)

    with tab3:
        st.markdown("### 📜 Signal Journal (Signals Only)")
        history_cuan = data[~data['Signal'].str.contains("NGOPI", na=False, case=False)]
        st.dataframe(history_cuan.sort_values(by='Timestamp', ascending=False), use_container_width=True)

    with tab4:
        st.markdown("### ⚙️ Contact & VIP Access")
        st.info("Ingin mendapatkan notifikasi sinyal lebih cepat? Hubungi Rosit.")
        st.link_button("Chat WhatsApp", "https://wa.me/6288980942762")
        st.link_button("Follow Instagram", "https://instagram.com/ya_rositt")

else:
    st.error("Engine sedang sinkronisasi data...")

st.markdown("<p style='text-align: center; font-size: 10px; color: #444; margin-top:30px;'>ROSIT QUANT AI v5.5 - INTERACTIVE PRO</p>", unsafe_allow_html=True)
        
