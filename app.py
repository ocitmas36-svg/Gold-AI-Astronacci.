import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Rosit Gold AI Dashboard",
    page_icon="🚀",
    layout="wide"
)

# Judul Utama
st.title("🚀 Rosit Gold AI - Trading Dashboard")
st.markdown("---")

# 2. LINK DATABASE (GOOGLE SHEETS CSV)
# Menggunakan ID Sheets milik Rosit yang sudah dikonversi ke format export CSV
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ygHIdUszMkTGiG0WZKe3l39tkIdFmid86WP6KTErlPo/export?format=csv"

@st.cache_data(ttl=60)  # Data akan diperbarui setiap 60 detik
def load_data():
    # Membaca data dari Google Sheets
    df = pd.read_csv(SHEET_URL)
    
    # Menyesuaikan nama kolom sesuai dengan struktur Google Form/Sheets Rosit
    # Urutan: Timestamp, Waktu, Harga, RSI_M1, RSI_H1, Signal
    df.columns = ['Timestamp', 'Waktu', 'Harga', 'RSI_M1', 'RSI_H1', 'Signal']
    
    # Pastikan kolom Harga dan RSI adalah angka
    df['Harga'] = pd.to_numeric(df['Harga'], errors='coerce')
    df['RSI_M1'] = pd.to_numeric(df['RSI_M1'], errors='coerce')
    df['RSI_H1'] = pd.to_numeric(df['RSI_H1'], errors='coerce')
    
    # Menghapus baris yang kosong jika ada
    df = df.dropna(subset=['Harga'])
    return df

try:
    data = load_data()
    last_row = data.iloc[-1]  # Data paling baru (baris terakhir)

    # 3. BAGIAN ATAS: INDIKATOR UTAMA (METRICS)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💵 Harga BTC Terakhir", f"${last_row['Harga']:,.2f}")
    
    with col2:
        st.metric("📊 RSI (M1)", f"{last_row['RSI_M1']}")
        
    with col3:
        # Memberi warna pada teks sinyal
        signal_text = last_row['Signal']
        if "BUY" in signal_text:
            color = "#00ff00" # Hijau
        elif "SELL" in signal_text:
            color = "#ff4b4b" # Merah
        else:
            color = "#ffa500" # Orange (Ngopi)
        
        st.markdown(f"**📢 AKSI TERAKHIR:**")
        st.markdown(f"<h3 style='color:{color}; margin-top:-15px;'>{signal_text}</h3>", unsafe_allow_html=True)
        
    with col4:
        st.write(f"📅 **Update Terakhir:**")
        st.write(f"{last_row['Timestamp']}")

    st.markdown("---")

    # 4. BAGIAN TENGAH: GRAFIK VISUAL
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📈 Pergerakan Harga Bitcoin")
        fig = go.Figure()
        
        # Garis Harga
        fig.add_trace(go.Scatter(
            x=data['Timestamp'], 
            y=data['Harga'], 
            mode='lines+markers', 
            name='Harga BTC', 
            line=dict(color='#ff9900', width=3)
        ))
        
        fig.update_layout(
            template="plotly_dark", 
            xaxis_title="Waktu", 
            yaxis_title="Harga (USD)",
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("📋 Status Terkini")
        st.info(f"""
        **Detail Analisa:**
        - **Asset:** Bitcoin (BTC)
        - **RSI H1:** {last_row['RSI_H1']}
        - **Status:** Sistem sedang memantau market setiap 15 menit via GitHub Actions.
        """)
        
        if "BUY" in last_row['Signal']:
            st.success("Saran: Momentum bagus untuk akumulasi!")
        elif "SELL" in last_row['Signal']:
            st.error("Saran: Waspada, market mulai jenuh beli!")
        else:
            st.warning("Saran: Wait and see, jangan fomo dulu.")

    st.markdown("---")

    # 5. BAGIAN BAWAH: TABEL RIWAYAT
    st.subheader("📜 Riwayat Sinyal Rosit Gold AI")
    # Tampilkan tabel dengan urutan terbaru di atas
    st.dataframe(data.sort_values(by='Timestamp', ascending=False), use_container_width=True)

except Exception as e:
    st.error("⚠️ Gagal memuat data dashboard.")
    st.write(f"Pesan Error: {e}")
    st.info("Saran: Pastikan Google Sheets kamu sudah di-share 'Anyone with the link can view' dan sudah ada datanya.")

# Footer
st.markdown("<p style='text-align: center; color: grey;'>Built with ❤️ by Rosit Gold AI Engine</p>", unsafe_allow_html=True)
