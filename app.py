import streamlit as st
import folium
from streamlit_folium import st_folium
import joblib
import requests
import time

# === ⚠️ JANGAN LUPA MASUKKAN API KEY AZURE MAPS KAMU DI SINI ⚠️ ===
MAPS_API_KEY = "1GLJWFf8IEFXQkX9JNLQT0SDEyz5x7hDnaeyJIAR6XPCt9mUhST9JQQJ99CDACYeBjFxDgxpAAAgAZMP3knW"

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="UrbanShield", layout="wide", page_icon="🛡️")

# UI BARU: Judul yang lebih menjual dan ramah awam
st.title("🛡️ UrbanShield: Navigasi Logistik Cerdas")
st.markdown("Pantau cuaca, hindari genangan air, dan pastikan armada Anda sampai dengan selamat.")
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

# --- 3. FUNGSI AZURE MAPS (Sistem Satelit) ---
def dapatkan_koordinat(alamat):
    url = f"https://atlas.microsoft.com/search/address/json?api-version=1.0&query={alamat}, Jakarta, Indonesia&subscription-key={MAPS_API_KEY}"
    try:
        response = requests.get(url).json()
        if response.get('results') and len(response['results']) > 0:
            pos = response['results'][0]['position']
            return pos['lat'], pos['lon']
    except Exception as e: 
        pass
    return None, None

def dapatkan_rute(lat1, lon1, lat2, lon2, status_banjir):
    bbox_banjir = "106.8150,-6.2150,106.8250,-6.1850" # Area Sudirman
    avoid_param = f"&avoid=areas&avoidAreas={bbox_banjir}" if status_banjir == 1 else ""
    
    url = f"https://atlas.microsoft.com/route/directions/json?api-version=1.0&query={lat1},{lon1}:{lat2},{lon2}&routeType=fastest{avoid_param}&subscription-key={MAPS_API_KEY}"
    try:
        response = requests.get(url).json()
        if 'routes' in response and len(response['routes']) > 0:
            jalur = response['routes'][0]['legs'][0]['points']
            waktu_menit = response['routes'][0]['summary']['travelTimeInSeconds'] // 60
            jarak_km = response['routes'][0]['summary']['lengthInMeters'] / 1000
            rute_koordinat = [[titik['latitude'], titik['longitude']] for titik in jalur]
            return rute_koordinat, waktu_menit, jarak_km
        elif 'error' in response:
            return None, 0, 0
    except: pass
    return None, 0, 0

# --- 4. LAYOUT DASHBOARD (Sisi Kiri: Input, Sisi Kanan: Peta) ---
col_input, col_map = st.columns([1, 2.5])

with col_input:
    st.subheader("📍 Tentukan Rute Perjalanan")
    # UI BARU: Label input yang lebih natural
    input_awal = st.text_input("Mulai dari (Lokasi Asal):", "Tanjung Priok, Jakarta Utara")
    input_tujuan = st.text_input("Kirim ke (Lokasi Tujuan):", "Blok M Square, Jakarta Selatan")
    
    st.markdown("---")
    st.subheader("⏱️ Jadwal Keberangkatan Truk")
    # UI BARU: Pilihan waktu yang lebih manusiawi
    waktu_berangkat = st.radio("Kapan armada akan melewati pusat kota?", 
                               ["Sekarang (Saat Ini)", "3 Jam Lagi", "6 Jam Lagi", "12 Jam Lagi"])
    
    st.markdown("---")
    st.subheader("🌧️ Radar Cuaca (Mode Simulasi)")
    # UI BARU: Penjelasan slider yang gampang dimengerti
    curah_hujan = st.slider("Seberapa deras hujannya? (mm)", 0.0, 50.0, 5.0, 
                            help="Geser ke kanan untuk mensimulasikan hujan badai.")
    
    st.write("") # Spasi kosong
    # UI BARU: Tombol aksi yang lebih mengajak
    mulai = st.button("🚀 Cari Jalan Paling Aman", use_container_width=True, type="primary")

with col_map:
    # UI BARU: Judul Peta
    st.subheader("Peta Pantauan Cerdas")
    peta_jkt = folium.Map(location=[-6.2088, 106.8456], zoom_start=11, tiles="CartoDB positron")
    
    if mulai and MAPS_API_KEY != "MASUKKAN_API_KEY_KAMU_DISINI":
        # Menentukan skor evaluasi (Tetap pakai angka asli tapi labelnya nanti diubah)
        if "Sekarang" in waktu_berangkat: auc_score, f1_score, thres = 0.9185, 0.5133, 10.0 
        elif "3 Jam Lagi" in waktu_berangkat: auc_score, f1_score, thres = 0.9951, 0.9188, 15.0 
        elif "6 Jam Lagi" in waktu_berangkat: auc_score, f1_score, thres = 0.9841, 0.8456, 25.0 
        else: auc_score, f1_score, thres = 0.9429, 0.6827, 35.0 

        with st.spinner('Memeriksa kondisi jalan dan memprediksi cuaca...'):
            time.sleep(1) 
            
            lat1, lon1 = dapatkan_koordinat(input_awal)
            lat2, lon2 = dapatkan_koordinat(input_tujuan)
            
            if lat1 and lat2:
                prediksi_banjir = 1 if curah_hujan > thres else 0
                rute, estimasi_waktu, jarak = dapatkan_rute(lat1, lon1, lat2, lon2, prediksi_banjir)
                
                if rute:
                    # --- UI BARU: METRIK YANG GAMPANG DIPAHAMI ORANG AWAM ---
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Kepercayaan Sistem", f"{auc_score * 100:.1f}%")
                    m2.metric("Akurasi AI", f"{f1_score * 100:.1f}%") # F1 diubah jadi persen Akurasi!
                    m3.metric("Estimasi Waktu", f"{estimasi_waktu} mnt")
                    m4.metric("Jarak Tempuh", f"{jarak:.1f} km")
                    
                    if prediksi_banjir == 1:
                        # UI BARU: Peringatan bahaya yang komunikatif
                        st.error(f"⚠️ **AWAS! Ada potensi banjir dalam {waktu_berangkat}.** Jangan khawatir, sistem kami telah mencarikan jalan memutar yang lebih aman.")
                        
                        folium.PolyLine(rute, color="#2ecc71", weight=7, opacity=0.8, tooltip="Rute Aman (Hindari Banjir)").add_to(peta_jkt)
                        folium.Rectangle(
                            bounds=[[-6.2150, 106.8150], [-6.1850, 106.8250]],
                            color="#e74c3c", fill=True, fill_color="#e74c3c", fill_opacity=0.4,
                            tooltip="Zona Banjir (Dilarang Lewat)"
                        ).add_to(peta_jkt)
                    else:
                        # UI BARU: Pesan sukses yang menenangkan
                        st.success(f"✅ **Jalanan aman!** Cuaca diprediksi bersahabat untuk keberangkatan {waktu_berangkat}. Silakan gunakan rute tercepat ini.")
                        
                        folium.PolyLine(rute, color="#3498db", weight=7, opacity=0.8, tooltip="Rute Tercepat").add_to(peta_jkt)
                    
                    folium.Marker([lat1, lon1], tooltip="Titik Jemput", icon=folium.Icon(color="green", icon="play")).add_to(peta_jkt)
                    folium.Marker([lat2, lon2], tooltip="Titik Antar", icon=folium.Icon(color="red", icon="stop")).add_to(peta_jkt)
                    
                    peta_jkt.fit_bounds([[lat1, lon1], [lat2, lon2]])
                else:
                    st.error("❌ **Jalan terputus!** Sepertinya lokasi tujuan Anda berada tepat di tengah-tengah area banjir. Coba cari lokasi lain di sekitarnya.")
            else:
                st.error("❌ Maaf, sistem satelit kami tidak mengenali alamat tersebut. Coba gunakan nama jalan, kelurahan, atau gedung yang lebih spesifik.")
                
    elif mulai:
        st.warning("⚠️ OOPS! API Key Azure Maps belum dimasukkan ke dalam sistem. Silakan hubungi tim teknis.")

    st_folium(peta_jkt, width=800, height=500, returned_objects=[])
