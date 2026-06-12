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
# TAB 4 : PETA CLUSTER (SIMPLE VERSION)
# =====================================================
with tab4:

    st.markdown("## 🗺️ Persebaran Cluster Indonesia")

    cluster_selected = st.selectbox(
        "Pilih Cluster",
        sorted(df_cluster["kluster"].unique()),
        key="map_cluster"
    )

    # ====================================
    # Persiapan Data Choropleth
    # ====================================
    
    # Ambil nama provinsi dari GeoJSON
    geojson_provinces = [
        feature["properties"]["PROVINSI"]
        for feature in indonesia_geo["features"]
    ]
    
    # Buat dataframe dengan semua provinsi dari GeoJSON
    map_data = pd.DataFrame({
        "provinsi_geo": geojson_provinces
    })
    
    # Merge dengan data cluster
    map_data = map_data.merge(
        df_cluster,
        left_on="provinsi_geo",
        right_on="provinsi",
        how="left"
    )
    
    # Buat kolom untuk warna (binary: ada di cluster atau tidak)
    map_data["in_cluster"] = map_data.apply(
        lambda row: "Ya" 
        if pd.notna(row["kluster"]) and row["kluster"] == cluster_selected 
        else "Tidak",
        axis=1
    )
    
    map_data["provinsi_display"] = map_data["provinsi"].fillna(map_data["provinsi_geo"])
    
    # ====================================
    # Buat Choropleth
    # ====================================
    fig = px.choropleth(
        map_data,
        geojson=indonesia_geo,
        locations="provinsi_geo",
        featureidkey="properties.PROVINSI",
        color="in_cluster",
        hover_name="provinsi_display",
        hover_data={
            "provinsi_geo": False,
            "kluster": True,
            "provinsi_display": False,
            "in_cluster": False
        },
        color_discrete_map={
            "Ya": "#d32f2f",  # Merah
            "Tidak": "rgba(0,0,0,0)"  # Transparent
        },
        title=f"Persebaran Cluster {cluster_selected}"
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        bgcolor="white"  # Background putih
    )

    fig.update_layout(
        height=650,
        margin=dict(l=0, r=0, t=50, b=0),
        showlegend=True,
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ====================================
    # List Provinsi
    # ====================================
    st.subheader(f"📍 Provinsi dalam Cluster {cluster_selected}")
    
    wilayah_cluster = (
        df_cluster[
            df_cluster["kluster"] == cluster_selected
        ]
        .sort_values("provinsi")
    )

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Jumlah Provinsi",
            len(wilayah_cluster)
        )
    with col2:
        st.metric(
            "Total Provinsi di Dataset",
            df_cluster["provinsi"].nunique()
        )

    daftar = (
        wilayah_cluster[
            ["provinsi"]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    daftar.index += 1

    st.dataframe(daftar, use_container_width=True)