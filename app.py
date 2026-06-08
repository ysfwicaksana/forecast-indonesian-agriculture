import streamlit as st
import pandas as pd
import plotly.express as px

# Sembunyikan ikon GitHub dan badge Streamlit
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            #GithubIcon {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.set_page_config(page_title="Dashboard Prioritas Pertanian 2026", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("2026.csv", sep=";")
    # Ubah nilai minus jadi 0
    df['prediksi_produksi_2026'] = df['prediksi_produksi_2026'].clip(lower=0)
    return df

df = load_data()

st.title("🌾 Dashboard Prioritas Komoditas Pertanian 2026")

# --- Tampilan Utama ---
tab1, tab2, tab3, tab4 = st.tabs(["Wilayah → Komoditas", "Komoditas → Wilayah", "Top 5 Global", "Top 5 per Komoditas"])

# ===== TAB 1: PILIH WILAYAH =====
with tab1:
    st.subheader("🗺️ Pilih Wilayah")
    wilayah = st.selectbox("Pilih Wilayah:", sorted(df['provinsi'].unique()), key="wil")
    
    # Filter data berdasarkan wilayah
    data_wil = df[df['provinsi'] == wilayah][['komoditas', 'kluster', 'prediksi_produksi_2026', 'ranking_topsis_global']].sort_values('ranking_topsis_global')
    
    st.dataframe(data_wil.reset_index(drop=True), use_container_width=True)
    st.caption(f"Total komoditas di {wilayah}: {len(data_wil)}")

# ===== TAB 2: PILIH KOMODITAS =====
with tab2:
    st.subheader("🌾 Pilih Komoditas")
    komoditas = st.selectbox("Pilih Komoditas:", sorted(df['komoditas'].unique()), key="kom")
    
    # Filter data berdasarkan komoditas
    data_kom = df[df['komoditas'] == komoditas][['provinsi', 'kluster', 'prediksi_produksi_2026', 'ranking_topsis_global']].sort_values('ranking_topsis_global')
    
    st.dataframe(data_kom.reset_index(drop=True), use_container_width=True)
    st.caption(f"Total wilayah untuk {komoditas}: {len(data_kom)}")

# ===== TAB 3: TOP 5 GLOBAL =====
with tab3:
    st.subheader("🏆 Top 5 Prioritas Global (Ranking TOPSIS Global)")
    
    # Ambil top 5 berdasarkan ranking_topsis_global (nilai terkecil)
    top5_global = df.nsmallest(5, 'ranking_topsis_global')[['ranking_topsis_global', 'komoditas', 'provinsi', 'kluster', 'prediksi_produksi_2026']].reset_index(drop=True)
    top5_global.index = top5_global.index + 1  # Nomor urut dari 1
    
    st.dataframe(top5_global, use_container_width=True)
    
    # Visualisasi
    fig = px.bar(
        top5_global.reset_index(), 
        x='ranking_topsis_global', 
        y='index',
        orientation='h',
        text='komoditas',
        title="Top 5 Prioritas Global (Ranking TOPSIS)",
        labels={'ranking_topsis_global': 'Skor Ranking', 'index': 'Urutan'},
        color='ranking_topsis_global',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

# ===== TAB 4: TOP 5 PER KOMODITAS =====
with tab4:
    st.subheader("📊 Top 5 Prioritas Tiap Komoditas")
    
    # Dapatkan daftar komoditas unik
    komoditas_list = sorted(df['komoditas'].unique())
    st.info(f"Total komoditas: {len(komoditas_list)}")
    
    # Loop untuk setiap komoditas
    for komoditas_item in komoditas_list:
        with st.expander(f"🌾 {komoditas_item}"):
            # Ambil top 5 per komoditas berdasarkan ranking_topsis_per_komoditas
            top5_per_kom = df[df['komoditas'] == komoditas_item].nsmallest(5, 'ranking_topsis_per_komoditas')[
                ['provinsi', 'kluster', 'prediksi_produksi_2026', 'ranking_topsis_per_komoditas']
            ].reset_index(drop=True)
            
            top5_per_kom.index = top5_per_kom.index + 1  # Nomor urut dari 1
            
            st.dataframe(top5_per_kom, use_container_width=True)