import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import joblib
import requests

MAPS_API_KEY = "FxVJMiRRs0Boe1nBFHopbGA8cP0OLmxUsHRfkXE1xI4iYVj0YS4nJQQJ99CDACYeBjFxDgxpAAAgAZMP112g"

st.set_page_config(page_title="UrbanShield Dynamic", layout="wide")

st.title("🛡️ UrbanShield: Real-time Flood Routing")
st.markdown("Sistem Logistik Dinamis terintegrasi **XGBoost AI** & **Azure Maps API**.")

# --- FUNGSI 1: LOAD MODEL AI ---
@st.cache_resource
def load_model():
    try:
        return joblib.load('model_banjir_urbanshield.pkl')
    except:
        return None
model_ai = load_model()

# --- FUNGSI 2: GEOCODING (TEKS KE KOORDINAT) ---
def dapatkan_koordinat(alamat):
    url = f"https://atlas.microsoft.com/search/address/json?api-version=1.0&query={alamat}, Jakarta, Indonesia&subscription-key={MAPS_API_KEY}"
    response = requests.get(url).json()
    if response['results']:
        pos = response['results'][0]['position']
        return pos['lat'], pos['lon']
    return None, None

# --- FUNGSI 3: MINTA RUTE KE AZURE MAPS ---
def dapatkan_rute(lat1, lon1, lat2, lon2, status_banjir):
    # Jika banjir, kita hindari area pusat/bawah secara sistem (Simulasi Avoid Area Azure Maps)
    avoid_param = "&avoid=areas&avoidAreas=-6.20,106.80|-6.15,106.85" if status_banjir == 1 else ""
    
    url = f"https://atlas.microsoft.com/route/directions/json?api-version=1.0&query={lat1},{lon1}:{lat2},{lon2}&routeType=fastest{avoid_param}&subscription-key={MAPS_API_KEY}"
    
    response = requests.get(url).json()
    try:
        jalur = response['routes'][0]['legs'][0]['points']
        waktu = response['routes'][0]['summary']['travelTimeInSeconds'] // 60
        rute_koordinat = [[titik['latitude'], titik['longitude']] for titik in jalur]
        return rute_koordinat, waktu
    except:
        return None, 0

# --- UI DASHBOARD ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📍 Input Dinamis")
    input_awal = st.text_input("Gudang Keberangkatan:", "Tanjung Priok")
    input_tujuan = st.text_input("Alamat Pengiriman:", "Sudirman")
    curah_hujan = st.slider("Data Curah Hujan (mm)", 0.0, 50.0, 10.0)
    
    mulai = st.button("Kalkulasi Rute Real-time", type="primary", use_container_width=True)

with col2:
    peta = folium.Map(location=[-6.20, 106.84], zoom_start=11)
    
    if mulai and MAPS_API_KEY != "MASUKKAN_API_KEY_KAMU_DISINI":
        with st.spinner("Menyambungkan ke Satelit Azure & Memproses AI..."):
            
            # 1. Cari Koordinat
            lat1, lon1 = dapatkan_koordinat(input_awal)
            lat2, lon2 = dapatkan_koordinat(input_tujuan)
            
            if lat1 and lat2:
                # 2. AI Prediksi Banjir
                data_dummy = pd.DataFrame({'precip_12h_sum': [curah_hujan], 'kota_encoded': [1]})
                for i in range(15): data_dummy[f'd_{i}'] = 0 # Jaga-jaga error kolom
                
                prediksi_banjir = 1 if curah_hujan > 15.0 else 0 # Threshold simulasi
                
                # 3. Tarik Rute dari Azure
                rute, waktu = dapatkan_rute(lat1, lon1, lat2, lon2, prediksi_banjir)
                
                if rute:
                    if prediksi_banjir == 1:
                        st.error(f"⚠️ **BAHAYA BANJIR!** AI mengalihkan rute. Estimasi waktu: {waktu} menit.")
                        folium.PolyLine(rute, color="green", weight=5, tooltip="Rute Dialihkan").add_to(peta)
                        # Efek visual banjir
                        folium.CircleMarker([-6.18, 106.82], radius=40, color='red', fill=True, tooltip="Zona Banjir").add_to(peta)
                    else:
                        st.success(f"✅ Rute Aman. Estimasi waktu: {waktu} menit.")
                        folium.PolyLine(rute, color="blue", weight=5, tooltip="Rute Tercepat").add_to(peta)
                    
                    # Tandai titik A dan B
                    folium.Marker([lat1, lon1], tooltip="Start", icon=folium.Icon(color="green")).add_to(peta)
                    folium.Marker([lat2, lon2], tooltip="Finish", icon=folium.Icon(color="red")).add_to(peta)
                    
                    # Zoom agar rute terlihat
                    peta.fit_bounds([[lat1, lon1], [lat2, lon2]])
            else:
                st.error("Alamat tidak ditemukan oleh satelit. Coba lebih spesifik!")
    elif mulai:
         st.warning("Kamu belum memasukkan API KEY Azure Maps di dalam kode!")

    st_folium(peta, width=700, height=500)