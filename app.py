import streamlit as st
import pandas as pd

# =====================
# Konfigurasi Halaman
# =====================
st.set_page_config(
    page_title="Dashboard Prioritas Pertanian 2026",
    layout="wide"
)

# Sembunyikan menu streamlit
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
    df = pd.read_csv("sampel_2026.csv", sep=";", decimal=",")

    # produksi negatif menjadi 0
    df["prediksi_produksi_2026"] = (
        df["prediksi_produksi_2026"]
        .clip(lower=0)
    )

    return df

df = load_data()

# =====================
# Judul
# =====================
st.title("🌾 Dashboard Prioritas Komoditas Pertanian 2026")

# =====================
# Pilih Wilayah
# =====================
wilayah = st.selectbox(
    "Pilih Wilayah",
    sorted(df["provinsi"].unique())
)

# Filter wilayah
df_wilayah = df[df["provinsi"] == wilayah]

st.markdown(f"## 📍 {wilayah}")

# =====================
# Tampilkan Top 3 per Subsektor
# =====================

subsektor_urut = [
    "Pangan",
    "Hortikultura",
    "Perkebunan"
]

for subsektor in subsektor_urut:

    data_sub = df_wilayah[
        df_wilayah["subsektor"] == subsektor
    ]

    if len(data_sub) == 0:
        continue

    top3 = (
        data_sub
        .nsmallest(3, "ranking_topsis_global")
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