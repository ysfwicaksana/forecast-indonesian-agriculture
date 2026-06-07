import streamlit as st
import pandas as pd
import plotly.express as px

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Pemodelan", page_icon="📊", layout="wide")

# --- JUDUL DASHBOARD ---
st.title("📊 Prototype Dashboard Hasil Pemodelan")
st.markdown("""
Dashboard interaktif ini menampilkan hasil gabungan dari pemodelan **XGBoost** (Prediksi), 
**TOPSIS** (Pemeringkatan), dan **K-Means** (Klastering).
""")
st.divider()

# --- FUNGSI LOAD DATA ---
@st.cache_data
def load_data():
    # Pastikan nama file sesuai dengan yang ada di folder Anda
    df_hist = pd.read_csv("2012-2025.csv")
    df_pred = pd.read_csv("2026.csv")
    return df_hist, df_pred

# Memuat data
try:
    df_hist, df_pred = load_data()
except FileNotFoundError:
    st.error("File CSV tidak ditemukan. Pastikan file berada di folder yang sama dengan app.py.")
    st.stop()

# --- TABS NAVIGASI ---
tab1, tab2, tab3 = st.tabs(["📋 Data Historis (2012-2025)", "🔮 Data Prediksi (2026)", "📈 Visualisasi Cepat"])

# --- TAB 1: DATA HISTORIS ---
with tab1:
    st.subheader("Data Historis & Hasil Klastering/Peringkat (2012-2025)")
    st.dataframe(df_hist, use_container_width=True)
    
    st.caption(f"Total baris data: {df_hist.shape[0]}")

# --- TAB 2: DATA PREDIKSI ---
with tab2:
    st.subheader("Hasil Prediksi XGBoost (Tahun 2026)")
    st.dataframe(df_pred, use_container_width=True)
    
    st.caption(f"Total baris data: {df_pred.shape[0]}")

# --- TAB 3: VISUALISASI ---
with tab3:
    st.subheader("Eksplorasi Data Interaktif")
    st.write("Pilih kolom yang ingin divisualisasikan dari data prediksi 2026:")
    
    # Mengambil daftar kolom dari dataframe prediksi
    kolom_tersedia = df_pred.columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        x_axis = st.selectbox("Pilih Kolom Sumbu X:", kolom_tersedia, index=0)
    with col2:
        # Default sumbu Y ke kolom kedua jika ada
        y_index = 1 if len(kolom_tersedia) > 1 else 0
        y_axis = st.selectbox("Pilih Kolom Sumbu Y:", kolom_tersedia, index=y_index)
        
    # Menampilkan Scatter Plot yang berguna untuk melihat sebaran K-Means atau Skor TOPSIS
    if x_axis and y_axis:
        fig = px.scatter(
            df_pred, 
            x=x_axis, 
            y=y_axis, 
            title=f"Hubungan antara {x_axis} dan {y_axis}",
            template="plotly_white",
            # Jika ada kolom klaster, Anda bisa mengaktifkan parameter color di bawah ini:
            # color="Nama_Kolom_Cluster_Anda" 
        )
        st.plotly_chart(fig, use_container_width=True)