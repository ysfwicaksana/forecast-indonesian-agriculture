import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Prioritas Pertanian 2026", layout="wide")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("2026.csv")
    return df

df = load_data()

st.title("🌾 Dashboard Prioritas Komoditas Pertanian 2026")

# --- FITUR 1: Wilayah -> Komoditas ---
st.sidebar.header("Filter Analisis")
wilayah_terpilih = st.sidebar.selectbox("Fitur 1: Pilih Wilayah", sorted(df['provinsi'].unique()))

# --- FITUR 2: Komoditas -> Wilayah ---
komoditas_terpilih = st.sidebar.selectbox("Fitur 2: Pilih Komoditas", sorted(df['komoditas'].unique()))

# --- Tampilan Utama ---
tab1, tab2, tab3, tab4 = st.tabs(["Wilayah & Komoditas", "Komoditas & Wilayah", "Prioritas Global", "Prioritas per Komoditas"])

with tab1:
    st.subheader(f"Daftar Komoditas Prioritas di {wilayah_terpilih}")
    data_wilayah = df[df['provinsi'] == wilayah_terpilih].sort_values('ranking_topsis_global')
    st.dataframe(data_wilayah[['komoditas', 'prediksi_produksi_2026', 'ranking_topsis_global']], use_container_width=True)

with tab2:
    st.subheader(f"Daftar Wilayah Prioritas untuk {komoditas_terpilih}")
    data_komoditas = df[df['komoditas'] == komoditas_terpilih].sort_values('ranking_topsis_global')
    st.dataframe(data_komoditas[['provinsi', 'prediksi_produksi_2026', 'ranking_topsis_global']], use_container_width=True)

with tab3:
    st.subheader("Fitur 3: Top 5 Prioritas Global")
    top_global = df.sort_values('ranking_topsis_global').head(5)
    
    # Menampilkan tabel
    st.dataframe(top_global[['provinsi', 'komoditas', 'ranking_topsis_global', 'prediksi_produksi_2026']], use_container_width=True)
    
    # Menambahkan Visualisasi Plotly
    import plotly.express as px
    fig = px.bar(top_global, x='komoditas', y='prediksi_produksi_2026', 
                 color='provinsi', title="Visualisasi 5 Besar Prioritas Produksi")
    st.plotly_chart(fig, use_container_width=True)
    
with tab4:
    st.subheader("Fitur 4: Top 3 Prioritas Tiap Komoditas")
    # Mengambil top 3 untuk setiap komoditas
    top_per_komoditas = df.sort_values(['komoditas', 'ranking_topsis_per_komoditas']).groupby('komoditas').head(3)
    st.dataframe(top_per_komoditas[['komoditas', 'provinsi', 'ranking_topsis_per_komoditas', 'prediksi_produksi_2026']], use_container_width=True)