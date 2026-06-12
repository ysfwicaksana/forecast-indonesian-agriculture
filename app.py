import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json

# =====================
# Load Data
# =====================
@st.cache_data
def load_data():
    df_global = pd.read_csv("global.csv", sep=";", decimal=",")
    df_cluster = pd.read_csv("cluster_provinces.csv", sep=";", decimal=",")
    
    df_global["prediksi_produksi_2026"] = df_global["prediksi_produksi_2026"].clip(lower=0)
    df_global["prediksi_produktivitas_2026"] = df_global["prediksi_produktivitas_2026"].clip(lower=0)
    
    return df_global, df_cluster

df_global, df_cluster = load_data()

# =====================
# Load GeoJSON
# =====================
with open("38-provinces.json", "r", encoding="utf-8") as f:
    indonesia_geo = json.load(f)

# =====================
# Konfigurasi Halaman
# =====================
st.set_page_config(page_title="Dashboard Prioritas Pertanian 2026", layout="wide")
st.title("🌾 Dashboard Prioritas Komoditas Pertanian 2026")

# =====================
# Tabs
# =====================
tab1, tab2, tab4 = st.tabs([
    "📍 Prioritas per Wilayah",
    "🌱 Prioritas per Komoditas",
    "🗺️ Peta Cluster"
])

# =====================================================
# TAB 1 : WILAYAH
# =====================================================
with tab1:
    wilayah = st.selectbox(
        "Pilih Wilayah",
        sorted(df_global["provinsi"].unique()),
        key="wilayah"
    )

    data_wilayah = df_global[df_global["provinsi"] == wilayah]
    st.markdown(f"## 📍 {wilayah}")

    subsektor_urut = ["Pangan", "Hortikultura", "Perkebunan"]

    for subsektor in subsektor_urut:
        data_sub = data_wilayah[data_wilayah["subsektor"] == subsektor]
        if len(data_sub) == 0:
            continue

        top3 = (
            data_sub
            .nsmallest(3, "ranking_topsis_global")
            [["subsektor", "komoditas", "prediksi_produksi_2026", 
              "prediksi_produktivitas_2026", "ranking_topsis_global"]]
            .reset_index(drop=True)
        )
        top3.index = top3.index + 1
        st.subheader(f"🌱 {subsektor}")
        st.dataframe(top3, use_container_width=True)

# =====================================================
# TAB 2 : KOMODITAS
# =====================================================
with tab2:
    komoditas = st.selectbox(
        "Pilih Komoditas",
        sorted(df_global["komoditas"].unique()),
        key="komoditas"
    )

    data_komoditas = df_global[df_global["komoditas"] == komoditas]
    st.markdown(f"## 🌱 {komoditas}")

    top3 = (
        data_komoditas
        .nsmallest(3, "ranking_topsis_per_komoditas")
        [["provinsi", "subsektor", "prediksi_produksi_2026", 
          "prediksi_produktivitas_2026", "ranking_topsis_per_komoditas"]]
        .reset_index(drop=True)
    )
    top3.index = top3.index + 1
    st.dataframe(top3, use_container_width=True)

# =====================================================
# TAB 4 : PETA CLUSTER (FOLIUM)
# =====================================================
with tab4:
    st.markdown("## 🗺️ Persebaran Cluster Indonesia")

    cluster_selected = st.selectbox(
        "Pilih Cluster",
        sorted(df_cluster["kluster"].unique()),
        key="map_cluster"
    )

    # Buat mapping cluster
    cluster_mapping = {}
    for _, row in df_cluster.iterrows():
        prov = row["provinsi"].strip()
        cluster_mapping[prov] = row["kluster"]

    # Buat Folium Map
    m = folium.Map(
        location=[-2, 113],  # Center Indonesia
        zoom_start=4,
        tiles="OpenStreetMap"
    )

    # Add GeoJSON dengan styling
    for feature in indonesia_geo["features"]:
        prov_name = feature["properties"]["PROVINSI"]
        cluster = cluster_mapping.get(prov_name, None)

        # Tentukan warna
        if cluster == cluster_selected:
            color = "#2e7d32"  # Hijau
            fill_opacity = 0.7
        else:
            color = "#e8e8e8"  # Abu-abu
            fill_opacity = 0.3

        # Add feature ke map
        folium.GeoJson(
            feature,
            style_function=lambda x, col=color, op=fill_opacity: {
                "fillColor": col,
                "color": "black",
                "weight": 1,
                "fillOpacity": op
            },
            tooltip=folium.Tooltip(prov_name)
        ).add_to(m)

    # Display map
    st_folium(m, width=1400, height=650)

    # ====================================
    # List Provinsi
    # ====================================
    st.subheader(f"📍 Provinsi dalam Cluster {cluster_selected}")

    wilayah_cluster = (
        df_cluster[df_cluster["kluster"] == cluster_selected]
        [["provinsi"]]
        .drop_duplicates()
        .sort_values("provinsi")
        .reset_index(drop=True)
    )

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Jumlah Provinsi", len(wilayah_cluster))
    with col2:
        st.metric("Total Provinsi di Dataset", df_cluster["provinsi"].nunique())

    wilayah_cluster.index += 1
    st.dataframe(wilayah_cluster, use_container_width=True)