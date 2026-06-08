import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Prioritas Pertanian 2026", layout="wide")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("2026.csv",sep=";")
    return df

df = load_data()

st.title("🌾 Dashboard Prioritas Komoditas Pertanian 2026")

# --- Tampilan Utama ---
tab1, tab2, tab3, tab4 = st.tabs(["Wilayah & Komoditas", "Komoditas & Wilayah", "Prioritas Global (Podium)", "Prioritas per Komoditas"])

with tab1:
    st.subheader("Fitur 1: Pilih Wilayah")
    wilayah = st.selectbox("Pilih Wilayah:", sorted(df['provinsi'].unique()), key="wil")
    data_wil = df[df['provinsi'] == wilayah].sort_values('ranking_topsis_global')
    st.dataframe(data_wil[['komoditas', 'prediksi_produksi_2026', 'ranking_topsis_global']], use_container_width=True)

with tab2:
    st.subheader("Fitur 2: Pilih Komoditas")
    komoditas = st.selectbox("Pilih Komoditas:", sorted(df['komoditas'].unique()), key="kom")
    data_kom = df[df['komoditas'] == komoditas].sort_values('ranking_topsis_global')
    st.dataframe(data_kom[['provinsi', 'prediksi_produksi_2026', 'ranking_topsis_global']], use_container_width=True)

with tab3:
    st.subheader("Fitur 3: Top 5 Prioritas Global (Podium)")
    top5 = df.sort_values('ranking_topsis_global').head(5).reset_index(drop=True)
    
    # Visualisasi Podium (Bar Chart yang diatur urutannya)
    fig = px.bar(top5, x='ranking_topsis_global', y='komoditas', orientation='h',
                 color='ranking_topsis_global', text='provinsi',
                 title="Ranking Top 5 Prioritas Global",
                 labels={'ranking_topsis_global': 'Skor', 'komoditas': 'Komoditas'})
    fig.update_layout(yaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(top5[['ranking_topsis_global', 'provinsi', 'komoditas', 'prediksi_produksi_2026']], use_container_width=True)

with tab4:
    st.subheader("Fitur 4: Top 3 Prioritas Tiap Komoditas")
    top3_per = df.sort_values(['komoditas', 'ranking_topsis_per_komoditas']).groupby('komoditas').head(3)
    st.dataframe(top3_per[['komoditas', 'provinsi', 'ranking_topsis_per_komoditas', 'prediksi_produksi_2026']], use_container_width=True)