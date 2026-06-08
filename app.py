import streamlit as st
import pandas as pd

# =====================
# Konfigurasi Halaman
# =====================
st.set_page_config(
    page_title="Dashboard Prioritas Pertanian 2026",
    layout="wide"
)

hide_st_style = """
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# =====================
# Load Data
# =====================
@st.cache_data
def load_data():

    df_wilayah = pd.read_csv(
        "wilayah.csv",
        sep=";",
        decimal=","
    )

    df_komoditas = pd.read_csv(
        "komoditas.csv",
        sep=";",
        decimal=","
    )

    df_wilayah["prediksi_produksi_2026"] = (
        df_wilayah["prediksi_produksi_2026"]
        .clip(lower=0)
    )

    df_komoditas["prediksi_produksi_2026"] = (
        df_komoditas["prediksi_produksi_2026"]
        .clip(lower=0)
    )

    return df_wilayah, df_komoditas


df_wilayah, df_komoditas = load_data()

# =====================
# Judul
# =====================
st.title("🌾 Dashboard Prioritas Komoditas Pertanian 2026")

# =====================
# Tabs
# =====================
tab1, tab2 = st.tabs(
    [
        "📍 Prioritas per Wilayah",
        "🌱 Prioritas per Komoditas"
    ]
)

# =====================================================
# TAB 1 : WILAYAH
# =====================================================
with tab1:

    wilayah = st.selectbox(
        "Pilih Wilayah",
        sorted(df_wilayah["provinsi"].unique()),
        key="wilayah"
    )

    data_wilayah = (
        df_wilayah[
            df_wilayah["provinsi"] == wilayah
        ]
    )

    st.markdown(f"## 📍 {wilayah}")

    subsektor_urut = [
        "Pangan",
        "Hortikultura",
        "Perkebunan"
    ]

    for subsektor in subsektor_urut:

        data_sub = data_wilayah[
            data_wilayah["subsektor"] == subsektor
        ]

        if len(data_sub) == 0:
            continue

        top3 = (
            data_sub
            .nsmallest(
                3,
                "ranking_topsis_global"
            )
            [
                [
                    "subsektor",
                    "komoditas",
                    "prediksi_produksi_2026",
                    "ranking_topsis_global"
                ]
            ]
            .reset_index(drop=True)
        )

        top3.index = top3.index + 1

        st.subheader(f"🌱 {subsektor}")

        st.dataframe(
            top3,
            use_container_width=True
        )

# =====================================================
# TAB 2 : KOMODITAS
# =====================================================
with tab2:

    komoditas = st.selectbox(
        "Pilih Komoditas",
        sorted(df_komoditas["komoditas"].unique()),
        key="komoditas"
    )

    data_komoditas = (
        df_komoditas[
            df_komoditas["komoditas"] == komoditas
        ]
    )

    st.markdown(f"## 🌱 {komoditas}")

    top3 = (
        data_komoditas
        .nsmallest(
            3,
            "ranking_topsis_per_komoditas"
        )
        [
            [
                "provinsi",
                "subsektor",
                "prediksi_produksi_2026",
                "ranking_topsis_per_komoditas"
            ]
        ]
        .reset_index(drop=True)
    )

    top3.index = top3.index + 1

    st.dataframe(
        top3,
        use_container_width=True
    )