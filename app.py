import streamlit as st
import pandas as pd
import json

st.set_page_config(
    page_title="Debug GeoJSON",
    layout="wide"
)

st.title("🔍 Debug GeoJSON & CSV Matching")

st.markdown("""
Script ini membantu Anda debug masalah mapping antara GeoJSON dan CSV.
""")

# =====================
# Load Files
# =====================
try:
    with open("indonesia-38-provinces.geojson", "r", encoding="utf-8") as f:
        indonesia_geo = json.load(f)
    st.success("✅ GeoJSON loaded")
except Exception as e:
    st.error(f"❌ Error loading GeoJSON: {e}")
    st.stop()

try:
    df_cluster = pd.read_csv("cluster_provinces.csv", sep=";", decimal=",")
    st.success("✅ CSV loaded")
except Exception as e:
    st.error(f"❌ Error loading CSV: {e}")
    st.stop()

# =====================
# Tab Debug
# =====================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Struktur Files",
    "🔍 Matching Analysis",
    "🗺️ GeoJSON Properties",
    "📝 CSV Data"
])

# =====================
# TAB 1: STRUKTUR
# =====================
with tab1:
    st.subheader("Struktur GeoJSON")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Features", len(indonesia_geo["features"]))
    with col2:
        st.metric("Type", indonesia_geo["type"])
    
    st.subheader("Properties Key di Feature Pertama")
    first_feature = indonesia_geo["features"][0]
    st.write(f"**Properties:** {first_feature['properties']}")
    
    st.subheader("Struktur CSV")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Rows", len(df_cluster))
    with col2:
        st.metric("Columns", len(df_cluster.columns))
    
    st.write(f"**Columns:** {df_cluster.columns.tolist()}")
    st.dataframe(df_cluster.head(), use_container_width=True)

# =====================
# TAB 2: MATCHING ANALYSIS
# =====================
with tab2:
    st.subheader("Analisis Kecocokan Provinsi")
    
    # Extract dari GeoJSON
    geo_provinces = []
    for feature in indonesia_geo["features"]:
        prov_name = feature["properties"].get("PROVINSI", "UNKNOWN")
        geo_provinces.append(prov_name)
    
    # Extract dari CSV
    csv_provinces = df_cluster["provinsi"].unique().tolist()
    
    # Set operations
    geo_set = set(geo_provinces)
    csv_set = set(csv_provinces)
    
    match_count = len(geo_set & csv_set)
    total_geo = len(geo_set)
    total_csv = len(csv_set)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Provinsi di GeoJSON", total_geo)
    with col2:
        st.metric("Provinsi di CSV", total_csv)
    with col3:
        st.metric("Yang Match", match_count)
    with col4:
        st.metric("Match %", f"{(match_count/max(total_geo, total_csv)*100):.1f}%")
    
    # Provinsi yang tidak match
    st.subheader("⚠️ Provinsi Tidak Match")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Di GeoJSON tapi TIDAK di CSV:**")
        not_in_csv = geo_set - csv_set
        if not_in_csv:
            for prov in sorted(not_in_csv):
                st.write(f"  ❌ `{prov}`")
        else:
            st.write("  ✅ Semua cocok!")
    
    with col2:
        st.write("**Di CSV tapi TIDAK di GeoJSON:**")
        not_in_geo = csv_set - geo_set
        if not_in_geo:
            for prov in sorted(not_in_geo):
                st.write(f"  ❌ `{prov}`")
        else:
            st.write("  ✅ Semua cocok!")
    
    # Coba case-insensitive matching
    st.subheader("🔄 Coba Case-Insensitive Match")
    geo_lower = {str(p).lower().strip(): p for p in geo_provinces}
    csv_lower = {str(p).lower().strip(): p for p in csv_provinces}
    
    case_match = len(set(geo_lower.keys()) & set(csv_lower.keys()))
    st.write(f"**Dengan case-insensitive: {case_match}/{total_geo} match**")
    
    if case_match > match_count:
        st.warning(f"⚠️ Ada {case_match - match_count} provinsi yang hanya cocok dengan case-insensitive!")
        st.write("Ini bisa jadi masalahnya!")

# =====================
# TAB 3: GEOJSON PROPERTIES
# =====================
with tab3:
    st.subheader("Daftar Semua Provinsi di GeoJSON")
    
    geo_df = pd.DataFrame({
        "No": range(1, len(geo_provinces) + 1),
        "Provinsi": geo_provinces
    })
    
    st.dataframe(geo_df, use_container_width=True)

# =====================
# TAB 4: CSV DATA
# =====================
with tab4:
    st.subheader("Daftar Semua Provinsi di CSV")
    
    csv_df = df_cluster[["provinsi", "kluster"]].drop_duplicates().sort_values("provinsi").reset_index(drop=True)
    csv_df.index += 1
    
    st.dataframe(csv_df, use_container_width=True)
    
    st.subheader("Cluster Distribution")
    cluster_dist = df_cluster.groupby("kluster").size().reset_index(name="Jumlah Provinsi")
    st.bar_chart(cluster_dist.set_index("kluster"))

# =====================
# REKOMENDASI
# =====================
st.divider()
st.subheader("📋 Rekomendasi")

if match_count == total_geo:
    st.success("✅ Semua provinsi match! Gunakan **app_fixed_map_v2.py** seharusnya bekerja.")
else:
    st.warning(f"⚠️ Ada {total_geo - match_count} provinsi tidak match!")
    st.markdown(f"""
    **Solusi:**
    1. Periksa tab "Provinsi Tidak Match" di atas
    2. Edit nama di CSV atau GeoJSON agar cocok
    3. Atau gunakan `app_fixed_map_v2.py` yang lebih robust (sudah ada handling untuk case-insensitive)
    
    **Yang paling mungkin jadi masalah:**
    - GeoJSON: UPPERCASE
    - CSV: mixed case atau lowercase
    - Beda spacing atau karakter khusus
    """)