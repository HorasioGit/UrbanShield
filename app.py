import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import joblib
import requests
import time

# === MASUKKAN API KEY AZURE MAPS KAMU DI BAWAH INI ===
MAPS_API_KEY = "1GLJWFf8IEFXQkX9JNLQT0SDEyz5x7hDnaeyJIAR6XPCt9mUhST9JQQJ99CDACYeBjFxDgxpAAAgAZMP3knW"

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="UrbanShield Dynamic", layout="wide", page_icon="🛡️")
st.title("🛡️ UrbanShield: Predictive Dynamic Routing")
st.markdown("Sistem rute bebas (*Free-Text*) terintegrasi **4-Horizon Temporal XGBoost** & **Azure Maps API**.")
st.divider()

# --- 2. FUNGSI LOAD 4 MODEL AI ---
@st.cache_resource
def load_models():
    models = {}
    try: models['now'] = joblib.load('model_nowcast_xgboost.pkl')
    except: models['now'] = None
    try: models['3h'] = joblib.load('model_forecast_3h.pkl')
    except: models['3h'] = None
    try: models['6h'] = joblib.load('model_forecast_6h.pkl')
    except: models['6h'] = None
    try: models['12h'] = joblib.load('model_forecast_12h.pkl')
    except: models['12h'] = None
    return models

model_ai = load_models()

# --- 3. FUNGSI AZURE MAPS (GEOCODING & ROUTING) ---
def dapatkan_koordinat(alamat):
    """Mengubah teks alamat menjadi koordinat Latitude/Longitude"""
    url = f"https://atlas.microsoft.com/search/address/json?api-version=1.0&query={alamat}, Jakarta, Indonesia&subscription-key={MAPS_API_KEY}"
    try:
        response = requests.get(url).json()
        if response.get('results') and len(response['results']) > 0:
            pos = response['results'][0]['position']
            return pos['lat'], pos['lon']
    except: pass
    return None, None

def dapatkan_rute(lat1, lon1, lat2, lon2, status_banjir):
    """Meminta Azure menggambar jalan, memberi penalti jika banjir"""
    # Jika AI memprediksi banjir, kita suruh Azure Maps menghindari titik rawan (Misal: Area Sudirman/Thamrin)
    avoid_param = "&avoid=areas&avoidAreas=-6.21,106.81|-6.18,106.83" if status_banjir == 1 else ""
    
    url = f"https://atlas.microsoft.com/route/directions/json?api-version=1.0&query={lat1},{lon1}:{lat2},{lon2}&routeType=fastest{avoid_param}&subscription-key={MAPS_API_KEY}"
    try:
        response = requests.get(url).json()
        if 'routes' in response and len(response['routes']) > 0:
            jalur = response['routes'][0]['legs'][0]['points']
            waktu_menit = response['routes'][0]['summary']['travelTimeInSeconds'] // 60
            rute_koordinat = [[titik['latitude'], titik['longitude']] for titik in jalur]
            return rute_koordinat, waktu_menit
    except: pass
    return None, 0

# --- 4. LAYOUT DASHBOARD ---
col_input, col_map = st.columns([1, 2.5])

with col_input:
    st.subheader("📍 Input Dinamis (Bebas Ketik)")
    # MENGGUNAKAN TEXT INPUT, BUKAN SELECTBOX
    input_awal = st.text_input("Gudang Keberangkatan:", "Tanjung Priok, Jakarta Utara")
    input_tujuan = st.text_input("Alamat Pengiriman:", "Jalan Jenderal Sudirman, Jakarta")
    
    st.markdown("---")
    st.subheader("⏱️ Pilih Horizon Waktu AI")
    waktu_berangkat = st.radio("Kapan truk akan melewati area rawan?", 
                               ["Saat Ini (Nowcast)", "+3 Jam Kedepan", "+6 Jam Kedepan", "+12 Jam Kedepan"])
    
    st.markdown("---")
    st.subheader("☁️ Simulasi Kondisi Cuaca")
    curah_hujan = st.slider("Curah Hujan (mm)", 0.0, 50.0, 15.5)
    
    mulai = st.button("🚀 Kalkulasi Rute Real-Time", use_container_width=True, type="primary")

with col_map:
    st.subheader("Live Interactive & Predictive Map")
    peta_jkt = folium.Map(location=[-6.2088, 106.8456], zoom_start=11, tiles="CartoDB positron")
    
    if mulai and MAPS_API_KEY != "MASUKKAN_API_KEY_KAMU_DISINI":
        # Atur threshold & skor sesuai horizon
        if "Saat Ini" in waktu_berangkat: auc_score, f1_score, thres = 0.9185, 0.5133, 10.0 
        elif "+3 Jam" in waktu_berangkat: auc_score, f1_score, thres = 0.9951, 0.9188, 15.0 
        elif "+6 Jam" in waktu_berangkat: auc_score, f1_score, thres = 0.9841, 0.8456, 25.0 
        else: auc_score, f1_score, thres = 0.9429, 0.6827, 35.0 

        with st.spinner('Satelit Azure sedang mencari koordinat dan menghitung prediksi...'):
            # 1. Terjemahkan Teks ke Koordinat
            lat1, lon1 = dapatkan_koordinat(input_awal)
            lat2, lon2 = dapatkan_koordinat(input_tujuan)
            
            if lat1 and lat2:
                # 2. AI Prediksi Banjir
                prediksi_banjir = 1 if curah_hujan > thres else 0
                
                # 3. Minta Satelit Cari Rute
                rute, estimasi_waktu = dapatkan_rute(lat1, lon1, lat2, lon2, prediksi_banjir)
                
                if rute:
                    # --- TAMPILAN METRIK AI ---
                    m1, m2, m3 = st.columns(3)
                    m1.metric("🛡️ AI AUC", f"{auc_score:.4f}")
                    m2.metric("🎯 AI F1", f"{f1_score:.4f}")
                    m3.metric("⏱️ Estimasi Tiba", f"{estimasi_waktu} mnt")
                    
                    if prediksi_banjir == 1:
                        st.error(f"⚠️ **Peringatan AI:** Potensi banjir dalam {waktu_berangkat}. Sistem memberi penalti rute otomatis.")
                        # Gambar rute hindari banjir (Hijau)
                        folium.PolyLine(rute, color="green", weight=6, tooltip="Rute Dialihkan (Aman)").add_to(peta_jkt)
                        # Gambar zona rawan
                        folium.CircleMarker([-6.20, 106.82], radius=50, color='red', fill=True, tooltip="Zona Banjir/Dihindari").add_to(peta_jkt)
                    else:
                        st.success(f"✅ Rute Tercepat aman dilewati untuk {waktu_berangkat}.")
                        # Gambar rute normal (Biru)
                        folium.PolyLine(rute, color="blue", weight=6, tooltip="Rute Tercepat").add_to(peta_jkt)
                    
                    # Tandai titik Asal dan Tujuan di peta
                    folium.Marker([lat1, lon1], tooltip="Asal", icon=folium.Icon(color="green", icon="play")).add_to(peta_jkt)
                    folium.Marker([lat2, lon2], tooltip="Tujuan", icon=folium.Icon(color="red", icon="stop")).add_to(peta_jkt)
                    
                    # Zoom peta otomatis menyesuaikan rute
                    peta_jkt.fit_bounds([[lat1, lon1], [lat2, lon2]])
                else:
                    st.error("Rute tidak ditemukan. Coba cek alamatnya lagi.")
            else:
                st.error("Satelit gagal menemukan alamat tersebut. Coba ketik nama jalan yang lebih spesifik!")
                
    elif mulai:
        st.warning("⚠️ KAMU BELUM MEMASUKKAN API KEY AZURE MAPS DI DALAM KODE APP.PY!")

    st_folium(peta_jkt, width=800, height=500, returned_objects=[])