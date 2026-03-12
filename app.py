import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. KONFIGURASI TAMPILAN (UI PREMIUM)
st.set_page_config(
    page_title="ROSIT GOLD AI v2.0",
    page_icon="💰",
    layout="wide"
)

# Custom CSS untuk tampilan "Full App"
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #00d4ff; }
    .stAlert { background-color: #1e2130; border: 1px solid #3e4255; }
    .css-1kyx600 { background-color: #1e2130; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# Header Apps
st.markdown("<h1 style='text-align: center; color: #ff9900;'>🛰️ ROSIT GOLD AI TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Pro-Grade Automated Trading System</p>", unsafe_allow_html=True)
st.divider()

# 2. LOAD DATA
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ygHIdUszMkTGiG0WZKe3l39tkIdFmid86WP6KTErlPo/export?format=csv"

@st.cache_data(ttl=30)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = ['Timestamp', 'Waktu', 'Harga', 'RSI_M1', 'RSI_H1', 'Signal']
    df['Harga'] = pd.to_numeric(df['Harga'], errors='coerce')
    df['RSI_M1'] = pd.to_numeric(df['RSI_M1'], errors='coerce')
    df = df.dropna(subset=['Harga'])
    return df

try:
    data = load_data()
    last_row = data.iloc[-1]
    
    # 3. TOP PANEL: METRICS & GAUGE
    col_a, col_b, col_c = st.columns([1, 1, 1])
    
    with col_a:
        st.metric("CURRENT BTC PRICE", f"${last_row['Harga']:,.2f}")
        st.write(f"⏱️ {last_row['Timestamp']}")

    with col_b:
        # Gauge Chart untuk RSI (Mirip Spedometer)
        fig_rsi = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = last_row['RSI_M1'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "RSI MOMENTUM", 'font': {'size': 14}},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#00d4ff"},
                'steps': [
                    {'range': [0, 30], 'color': "rgba(0, 255, 0, 0.2)"},
                    {'range': [70, 100], 'color': "rgba(255, 0, 0, 0.2)"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        fig_rsi.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
        st.plotly_chart(fig_rsi, use_container_width=True)

    with col_c:
        status_color = "#00FF00" if "BUY" in last_row['Signal'] else "#FF4B4B" if "SELL" in last_row['Signal'] else "#FFA500"
        st.markdown(f"""
            <div style='background: #1e2130; padding: 20px; border-radius: 15px; border-left: 5px solid {status_color};'>
                <p style='color: grey; margin:0;'>AI RECOMMENDATION</p>
                <h2 style='color: {status_color}; margin:0;'>{last_row['Signal']}</h2>
            </div>
        """, unsafe_allow_html=True)

    # 4. MAIN CHART (WITH BUY/SELL MARKERS)
    st.subheader("📊 Market Intelligence Map")
    
    fig = go.Figure()

    # Line Chart Harga
    fig.add_trace(go.Scatter(
        x=data['Timestamp'], y=data['Harga'],
        mode='lines', name='Price Action',
        line=dict(color='#4169E1', width=3),
        fill='tozeroy', fillcolor='rgba(65, 105, 225, 0.05)'
    ))

    # Markers BUY
    buys = data[data['Signal'].str.contains("BUY", na=False)]
    fig.add_trace(go.Scatter(
        x=buys['Timestamp'], y=buys['Harga'],
        mode='markers+text', name='BUY POINT',
        text=["BUY"]*len(buys), textposition="bottom center",
        marker=dict(symbol='triangle-up', size=18, color='#00FF00', line=dict(width=2, color='white'))
    ))

    # Markers SELL
    sells = data[data['Signal'].str.contains("SELL", na=False)]
    fig.add_trace(go.Scatter(
        x=sells['Timestamp'], y=sells['Harga'],
        mode='markers+text', name='SELL POINT',
        text=["SELL"]*len(sells), textposition="top center",
        marker=dict(symbol='triangle-down', size=18, color='#FF4B4B', line=dict(width=2, color='white'))
    ))

    fig.update_layout(
        template="plotly_dark",
        height=500,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#222')
    )
    st.plotly_chart(fig, use_container_width=True)

    # 5. DATA LOG
    with st.expander("📋 VIEW RAW DATA LOG"):
        st.dataframe(data.sort_values(by='Timestamp', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"🔄 Menghubungkan ke Bot Rosit... ({e})")

st.markdown("<p style='text-align: center; font-size: 12px; color: #444;'>ROSIT GOLD AI SYSTEM v2.0 - Stable Build 2026</p>", unsafe_allow_html=True)
