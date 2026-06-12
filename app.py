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

# hide_st_style = """
# <style>
# #MainMenu {visibility:hidden;}
# footer {visibility:hidden;}
# header {visibility:hidden;}
# </style>
# """
# st.markdown(hide_st_style, unsafe_allow_html=True)

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

    # df_wilayah = pd.read_csv(
    #     "wilayah.csv",
    #     sep=";",
    #     decimal=","
    # )

    # df_komoditas = pd.read_csv(
    #     "komoditas.csv",
    #     sep=";",
    #     decimal=","
    # )

    df_cluster = pd.read_csv(
        "cluster_provinces.csv",
        sep=";",
        decimal=","
    )

    df_global["prediksi_produksi_2026"] = (
        df_global["prediksi_produksi_2026"]
        .clip(lower=0)
    )

    # df_komoditas["prediksi_produksi_2026"] = (
    #     df_komoditas["prediksi_produksi_2026"]
    #     .clip(lower=0)
    # )

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
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📍 Prioritas per Wilayah",
        "🌱 Prioritas per Komoditas",
        "🌳 Prioritas per Cluster",
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
# TAB 3 : CLUSTER
# =====================================================
with tab3:
    
    st.markdown("## 🌳 Analisis Cluster per Subsektor")
    
    # Pilih subsektor
    subsektor = st.selectbox(
        "Pilih Subsektor",
        sorted(df_global["subsektor"].unique()),
        key="subsektor_cluster"
    )
    
    # Filter data berdasarkan subsektor
    data_cluster = (
        df_cluster[
            df_cluster["subsektor"] == subsektor
        ]
    )
    
    # ===== TABEL PROVINSI PER CLUSTER =====
    st.subheader(f"📊 Provinsi dalam {subsektor} berdasarkan Cluster")
    
    # Urutkan berdasarkan cluster
    data_cluster_sorted = (
        data_cluster
        .sort_values("kluster")
        [["provinsi", "kluster"]]
        .reset_index(drop=True)
    )
    
    data_cluster_sorted.index = data_cluster_sorted.index + 1
    
    st.dataframe(
        data_cluster_sorted,
        use_container_width=True
    )
    
    st.caption(f"Total provinsi: {len(data_cluster_sorted)}")
    
    st.divider()
    
    # ===== BAR CHART SUMMARY CLUSTER =====
    st.subheader(f"📈 Summary Cluster - {subsektor}")
    
    # Hitung jumlah provinsi per cluster
    cluster_summary = (
        data_cluster
        .groupby("kluster")
        .size()
        .reset_index(name="jumlah_provinsi")
        .sort_values("kluster")
    )
    
    # Buat bar chart
    fig = px.bar(
        cluster_summary,
        x="kluster",
        y="jumlah_provinsi",
        title=f"Total Provinsi per Cluster - {subsektor}",
        labels={
            "kluster": "Cluster",
            "jumlah_provinsi": "Jumlah Provinsi"
        },
        text="jumlah_provinsi",
        color="kluster",
        color_continuous_scale="Viridis",
        height=400
    )
    
    fig.update_traces(textposition="auto")
    fig.update_layout(
        showlegend=False,
        xaxis_title="Cluster",
        yaxis_title="Jumlah Provinsi"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistik ringkas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Cluster",
            cluster_summary["kluster"].nunique()
        )
    
    with col2:
        st.metric(
            "Total Provinsi",
            cluster_summary["jumlah_provinsi"].sum()
        )
    
    with col3:
        st.metric(
            "Rata-rata Provinsi/Cluster",
            f"{cluster_summary['jumlah_provinsi'].mean():.1f}"
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

    fig = px.choropleth(
        map_data,
        geojson=indonesia_geo,
        locations="provinsi",
        featureidkey="properties.PROVINSI",
        color="status",
        hover_name="provinsi",
        title=f"Persebaran Cluster {cluster}"
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