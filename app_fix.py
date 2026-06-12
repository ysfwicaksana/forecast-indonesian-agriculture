import streamlit as st
import pandas as pd
import plotly.express as px
import json

# =====================
# Konfigurasi Halaman
# =====================
st.set_page_config(
    page_title="Dashboard Prioritas Pertanian 2026",
    layout="wide"
)

# =====================
# Fungsi untuk normalize nama provinsi
# =====================
def normalize_province_name(name):
    """
    Normalisasi nama provinsi:
    - Ubah ke lowercase
    - Hapus spasi ganda
    - Strip whitespace awal/akhir
    """
    if pd.isna(name):
        return ""
    return str(name).strip().lower()

# =====================
# Load Data
# =====================
@st.cache_data
def load_data():

    df_global = pd.read_csv(
        "global.csv",
        sep=";",
        decimal=","
    )

    df_cluster = pd.read_csv(
        "cluster_provinces.csv",
        sep=";",
        decimal=","
    )

    df_global["prediksi_produksi_2026"] = (
        df_global["prediksi_produksi_2026"]
        .clip(lower=0)
    )

    df_global["prediksi_produktivitas_2026"] = (
        df_global["prediksi_produktivitas_2026"]
        .clip(lower=0)
    )

    return df_global, df_cluster


df_global, df_cluster = load_data()

# =====================
# Load GeoJSON
# =====================
with open(
    "indonesia-38-provinces.geojson",
    "r",
    encoding="utf-8"
) as f:
    indonesia_geo = json.load(f)

# Normalize nama provinsi di GeoJSON
for feature in indonesia_geo["features"]:
    original_name = feature["properties"]["PROVINSI"]
    feature["properties"]["PROVINSI_NORMALIZED"] = normalize_province_name(original_name)

# Normalize nama provinsi di dataframe
df_cluster["provinsi_normalized"] = df_cluster["provinsi"].apply(normalize_province_name)

# =====================
# Judul
# =====================
st.title("🌾 Dashboard Prioritas Komoditas Pertanian 2026")

# =====================
# Tabs
# =====================
tab1, tab2, tab4 = st.tabs(
    [
        "📍 Prioritas per Wilayah",
        "🌱 Prioritas per Komoditas",
        "🗺️ Peta Cluster"
    ]
)

# =====================================================
# TAB 1 : WILAYAH
# =====================================================
with tab1:

    wilayah = st.selectbox(
        "Pilih Wilayah",
        sorted(df_global["provinsi"].unique()),
        key="wilayah"
    )

    data_wilayah = (
        df_global[
            df_global["provinsi"] == wilayah
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
                    "prediksi_produktivitas_2026",
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
        sorted(df_global["komoditas"].unique()),
        key="komoditas"
    )

    data_komoditas = (
        df_global[
            df_global["komoditas"] == komoditas
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
                "prediksi_produktivitas_2026",
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


# =====================================================
# TAB 4 : PETA CLUSTER
# =====================================================
with tab4:

    st.markdown("## 🗺️ Persebaran Cluster Indonesia")

    cluster = st.selectbox(
        "Pilih Cluster",
        sorted(df_cluster["kluster"].unique()),
        key="map_cluster"
    )

    # ====================================
    # DATA PETA
    # ====================================

    map_data = df_cluster.copy()

    map_data["status"] = "Cluster Lain"

    map_data.loc[
        map_data["kluster"] == cluster,
        "status"
    ] = f"Cluster {cluster}"

    # Gunakan provinsi_normalized untuk location matching
    fig = px.choropleth(
        map_data,
        geojson=indonesia_geo,
        locations="provinsi_normalized",
        featureidkey="properties.PROVINSI_NORMALIZED",
        color="status",
        hover_name="provinsi",  # Tampilkan nama asli saat hover
        title=f"Persebaran Cluster {cluster}",
        color_discrete_map={
            f"Cluster {cluster}": "#1f77b4",
            "Cluster Lain": "#d3d3d3"
        }
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False
    )

    fig.update_layout(
        height=650,
        margin=dict(
            l=0,
            r=0,
            t=50,
            b=0
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ====================================
    # LIST PROVINSI
    # ====================================

    wilayah_cluster = (
        df_cluster[
            df_cluster["kluster"] == cluster
        ]
        .sort_values("provinsi")
    )

    st.subheader(
        f"📍 Provinsi dalam Cluster {cluster}"
    )

    st.metric(
        "Jumlah Provinsi",
        len(wilayah_cluster)
    )

    daftar = (
        wilayah_cluster[
            ["provinsi"]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    daftar.index += 1

    st.dataframe(
        daftar,
        use_container_width=True
    )

    # Debug info (bisa dihapus nanti)
    with st.expander("🔍 Debug Info"):
        st.write(f"Jumlah provinsi yang match dengan GeoJSON: {len(wilayah_cluster)}")
        st.write(f"Total provinsi di CSV: {len(df_cluster['provinsi'].unique())}")