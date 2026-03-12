import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Konfigurasi Halaman
st.set_page_config(page_title="Rosit Gold AI Dashboard", layout="wide")

st.title("🚀 Rosit Gold AI - Trading Dashboard")
st.write("Pantau performa bot trading otomatis kamu di sini.")

# 1. AMBIL DATA DARI GOOGLE SHEETS
# Link CSV dari Google Sheets (Ganti dengan link CSV kamu jika berbeda)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ygHIdUszMkTGiG0WZKe3l39tkIdFmid86WP6KTErlPo/export?format=csv"

@st.cache_data(ttl=60) # Update data tiap 1 menit
def load_data():
    df = pd.read_csv(SHEET_URL)
    # Ganti nama kolom jika tidak sesuai dengan header di Sheets kamu
    df.columns = ['Timestamp', 'Waktu', 'Harga', 'RSI_M1', 'RSI_H1', 'Signal']
    df['Harga'] = pd.to_numeric(df['Harga'], errors='coerce')
    return df

try:
    data = load_data()
    last_row = data.iloc[-1]

    # 2. TAMPILAN INDIKATOR UTAMA (METRICS)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Harga Terakhir", f"${last_row['Harga']:,.2f}")
    with col2:
        st.metric("RSI M1", f"{last_row['RSI_M1']}")
    with col3:
        color = "green" if "BUY" in last_row['Signal'] else "red" if "SELL" in last_row['Signal'] else "orange"
        st.markdown(f"**Sinyal Terakhir:** <span style='color:{color}; font-size:20px'>{last_row['Signal']}</span>", unsafe_allow_html=True)
    with col4:
        st.write(f"Update: {last_row['Timestamp']}")

    st.divider()

    # 3. GRAFIK PERGERAKAN HARGA
    st.subheader("📊 Grafik Riwayat Harga BTC")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Timestamp'], y=data['Harga'], mode='lines+markers', name='Harga BTC', line=dict(color='#ff9900')))
    fig.update_layout(template="plotly_dark", xaxis_title="Waktu", yaxis_title="Harga (USD)")
    st.plotly_chart(fig, use_container_width=True)

    # 4. TABEL RIWAYAT LENGKAP
    st.subheader("📜 Log Riwayat Sinyal")
    st.dataframe(data.sort_values(by='Timestamp', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Gagal memuat data: {e}")
    st.info("Pastikan Google Sheets kamu sudah di-share 'Anyone with the link can view'.")

