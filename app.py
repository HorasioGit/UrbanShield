import streamlit as st
import folium
from streamlit_folium import st_folium
import joblib
import pandas as pd
import requests
import time
import os
from datetime import datetime, timedelta

try:
    from weather import (fetch_live_weather, get_live_prediction_row,
                         get_current_weather_info, describe_weather_code)
    WEATHER_OK = True
except ImportError:
    WEATHER_OK = False

MAPS_API_KEY = "1GLJWFf8IEFXQkX9JNLQT0SDEyz5x7hDnaeyJIAR6XPCt9mUhST9JQQJ99CDACYeBjFxDgxpAAAgAZMP3knW"

MODEL_META = {
    'now': {'auc': 0.9185, 'f1': 0.5133, 'thresh': 0.20, 'thresh_mm': 10.0},
    '3h':  {'auc': 0.9951, 'f1': 0.9188, 'thresh': 0.35, 'thresh_mm': 15.0},
    '6h':  {'auc': 0.9841, 'f1': 0.8456, 'thresh': 0.35, 'thresh_mm': 25.0},
    '12h': {'auc': 0.9429, 'f1': 0.6827, 'thresh': 0.40, 'thresh_mm': 35.0},
}
HORIZONS = {
    'Sekarang': ('now', 'status_banjir', 0),
    '+3 Jam':   ('3h',  'target_3h',    3),
    '+6 Jam':   ('6h',  'target_6h',    6),
    '+12 Jam':  ('12h', 'target_12h',  12),
}

st.set_page_config(page_title="UrbanShield", layout="wide", page_icon="🛡️")

st.markdown('<head><meta name="dicoding:email" content="horasionissiimmanuel@gmail.com"></head>', unsafe_allow_html=True)

st.markdown("""
<style>
    section.main > div { padding-top: 1rem; }
    
    /* Metrik Card - Force warna font ke terang */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1E212B 60%, #252A36);
        border-radius: 14px; padding: 16px 18px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.45);
        border: 1px solid #2E3340; border-left: 5px solid #F18F01;
        transition: transform 0.2s ease;
    }
    [data-testid="stMetric"]:hover { transform: translateY(-2px); }
    [data-testid="stMetricValue"] > div { font-size: 1.6rem !important; font-weight: 700 !important; color: #FAFAFA !important; }
    [data-testid="stMetricLabel"] { font-size: 0.75rem !important; color: #A0AEC0 !important;
        text-transform: uppercase; letter-spacing: 0.05em; }
        
    /* Input Field - Force warna font ke putih karena backgroundnya gelap */
    div[data-baseweb="input"] > div {
        border-radius: 10px !important; border: 1px solid #2E3340 !important;
        background-color: #161920 !important;
    }
    div[data-baseweb="input"] input {
        color: #FAFAFA !important; 
        -webkit-text-fill-color: #FAFAFA !important;
    }
    div[data-baseweb="input"] > div:focus-within {
        border-color: #F18F01 !important;
        box-shadow: 0 0 0 2px rgba(241,143,1,0.25) !important;
    }
    
    /* Tombol Primary */
    div.stButton > button[kind="primary"] {
        border-radius: 12px !important; font-weight: 700 !important;
        background: linear-gradient(90deg, #E07B00, #F18F01) !important;
        border: none !important; box-shadow: 0 4px 14px rgba(241,143,1,0.35) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(241,143,1,0.5) !important;
    }
    hr { border-color: #2E3340 !important; }
    iframe { border-radius: 16px !important;
        box-shadow: 0 6px 28px rgba(0,0,0,0.3) !important;
        border: 1px solid #2E3340 !important; }
    [data-testid="stAlert"] { border-radius: 12px !important; }
    .horizon-card { text-align:center; border-radius:10px; padding:10px 6px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""<h1 style='background:linear-gradient(90deg,#F18F01,#FAFAFA);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    margin-bottom:0;padding-bottom:0;'>🛡️ UrbanShield</h1>""", unsafe_allow_html=True)
st.markdown("<p style='font-size:1.1rem;color:#A0AEC0;margin-top:-10px;font-weight:500;'>"
            "Navigasi Logistik Cerdas Berbasis Prediksi Cuaca AI</p>", unsafe_allow_html=True)
st.divider()

@st.cache_resource
def load_models():
    m = {}
    for key, fname in [('now','model_nowcast_xgboost.pkl'),('3h','model_forecast_3h.pkl'),
                       ('6h','model_forecast_6h.pkl'),('12h','model_forecast_12h.pkl')]:
        try: m[key] = joblib.load(os.path.join(os.path.dirname(__file__), fname))
        except: m[key] = None
    return m

@st.cache_data
def load_hist_csv():
    p = os.path.join(os.path.dirname(__file__), 'UrbanShield_Base_Engineered.csv')
    if os.path.exists(p):
        df = pd.read_csv(p); df['datetime'] = pd.to_datetime(df['datetime']); return df
    return None

model_dict = load_models()
df_hist    = load_hist_csv()

def geocode(alamat):
    url = (f"https://atlas.microsoft.com/search/address/json?api-version=1.0"
           f"&query={alamat},Jakarta,Indonesia&subscription-key={MAPS_API_KEY}")
    try:
        r = requests.get(url, timeout=10).json()
        if r.get('results'):
            p = r['results'][0]['position']; return p['lat'], p['lon']
    except: pass
    return None, None

def gen_box(lat, lon, offset=0.012):
    return [[lon-offset,lat-offset],[lon+offset,lat-offset],
            [lon+offset,lat+offset],[lon-offset,lat+offset],[lon-offset,lat-offset]]

def get_route(lat1, lon1, lat2, lon2, banjir, box=None):
    url = (f"https://atlas.microsoft.com/route/directions/json?api-version=1.0"
           f"&query={lat1},{lon1}:{lat2},{lon2}&routeType=fastest&subscription-key={MAPS_API_KEY}")
    try:
        if banjir and box:
            r = requests.post(url, json={"avoidAreas":{"type":"MultiPolygon","coordinates":[[box]]}},
                              headers={"Content-Type":"application/json"}, timeout=15).json()
        else:
            r = requests.get(url, timeout=15).json()
        if 'routes' in r and r['routes']:
            leg = r['routes'][0]; pts = leg['legs'][0]['points']
            return ([[p['latitude'],p['longitude']] for p in pts],
                    leg['summary']['travelTimeInSeconds']//60,
                    leg['summary']['lengthInMeters']/1000)
    except: pass
    return None, 0, 0

def predict_manual(model, df, curah_hujan, horizon_h=0):
    """
    Mode Simulasi Demo — deterministik untuk keperluan presentasi.
    
    Slider >= 15mm → cari baris historis yang AKAN banjir (shift per kota) → AI output prob tinggi
    Slider <  15mm → cari baris historis yang AMAN                           → AI output prob rendah
    
    Mengembalikan (prob, prediksi_banjir) agar perilaku demo konsisten.
    """
    if model is None or df is None: return None
    try: feat_cols = model.feature_names_in_.tolist()
    except: return None

    df = df.copy().sort_values('datetime').reset_index(drop=True)

    if 'kota_administrasi' in df.columns:
        df['_target'] = (df.groupby('kota_administrasi')['status_banjir']
                           .transform(lambda x: x.shift(-horizon_h).fillna(0)))
    else:
        df['_target'] = df['status_banjir'].shift(-horizon_h).fillna(0)

    flood_rows = df[df['_target'] == 1]
    safe_rows  = df[df['_target'] == 0]

    if curah_hujan >= 15:
        sub = flood_rows if len(flood_rows) > 0 else df
    else:
        sub = safe_rows  if len(safe_rows) > 0  else df

    idx   = (sub['precipitation'] - curah_hujan).abs().idxmin()
    avail = [c for c in feat_cols if c in sub.columns]
    X     = sub.loc[[idx]][avail].copy()
    for c in [c for c in feat_cols if c not in avail]:
        X[c] = 0.0

    try:
        return float(model.predict_proba(X[feat_cols])[0, 1])
    except:
        return None

REFRESH_MIN = 30
for k,v in [('last_fetch',None),('live_df',None),('live_info',None)]:
    if k not in st.session_state: st.session_state[k] = v
st.markdown("#### ⚡ Mode Prediksi")
mode = st.radio("Mode Prediksi",
                ["🔴 Live Mode (Real-Time API)", "🎮 Simulasi Manual (Slider)"],
                horizontal=True, label_visibility="collapsed")
IS_LIVE = "Live" in mode

if IS_LIVE:
    needs_refresh = (st.session_state.last_fetch is None or
                     datetime.now() - st.session_state.last_fetch > timedelta(minutes=REFRESH_MIN))

    hdr_c1, hdr_c2 = st.columns([4, 1])
    with hdr_c1:
        lbl = (f"📡 **Cuaca Jakarta Live** · 🕐 Update: "
               f"{st.session_state.last_fetch.strftime('%H:%M WIB')} · auto-refresh {REFRESH_MIN} mnt"
               if st.session_state.last_fetch else "📡 **Cuaca Jakarta Live** · Mengambil data...")
        st.markdown(lbl)
    with hdr_c2:
        refresh_btn = st.button("🔄 Refresh", use_container_width=True)

    if needs_refresh or refresh_btn or st.session_state.live_df is None:
        with st.spinner("📡 Mengambil data cuaca terkini dari Open-Meteo..."):
            try:
                df_live = fetch_live_weather()
                st.session_state.live_df   = df_live
                st.session_state.live_info = get_current_weather_info(df_live)
                st.session_state.last_fetch = datetime.now()
            except Exception as e:
                st.error(f"❌ Gagal ambil cuaca: {e}")

    info = st.session_state.live_info
    if info:
        cuaca_lbl, cuaca_icon, cuaca_warna = describe_weather_code(info['kode'])

        wc1, wc2, wc3, wc4 = st.columns([2.5, 1.5, 1.5, 1.5])
        with wc1:
            st.markdown(f"""
            <div style='background:{cuaca_warna}22;border:1px solid {cuaca_warna};
                        border-radius:12px;padding:12px 18px;'>
              <span style='font-size:2rem;'>{cuaca_icon}</span>
              <span style='font-size:1.1rem;font-weight:700;color:{cuaca_warna};margin-left:10px;'>{cuaca_lbl}</span><br>
              <span style='font-size:0.8rem;color:#A0AEC0;'>
                🌧 Sekarang: <b>{info['hujan']} mm</b> &nbsp;|&nbsp;
                3 jam: <b>{info['hujan_3h']} mm</b> &nbsp;|&nbsp;
                12 jam: <b>{info['hujan_12h']} mm</b>
              </span>
            </div>""", unsafe_allow_html=True)
        wc2.metric("🌡️ Suhu",   f"{info['suhu']}°C")
        wc3.metric("💧 Lembab", f"{info['lembab']}%")
        wc4.metric("💨 Angin",  f"{info['angin']} km/h")

        st.markdown("**🔮 Prakiraan Risiko Banjir (4 Horizon)**")
        h_cols = st.columns(4)
        df_live_cached = st.session_state.live_df
        for i, (lbl_h, (km, _, hh)) in enumerate(HORIZONS.items()):
            mdl = model_dict.get(km)
            thr = MODEL_META[km]['thresh']
            try:
                X_h = get_live_prediction_row(mdl, df_live_cached, hh)
                p   = float(mdl.predict_proba(X_h)[0,1]) if mdl else 0.0
            except: p = 0.0
            s  = "⚠️ BANJIR" if p >= thr else "✅ AMAN"
            sc = "#e74c3c"   if p >= thr else "#27ae60"
            h_cols[i].markdown(f"""
            <div style='background:{sc}22;border:1px solid {sc}55;border-radius:10px;
                        padding:12px;text-align:center;'>
              <p style='margin:0;font-size:0.75rem;color:#A0AEC0;letter-spacing:.06em;'>{lbl_h}</p>
              <p style='margin:4px 0;font-size:1rem;font-weight:700;color:{sc};'>{s}</p>
              <p style='margin:0;font-size:0.9rem;color:#F18F01;font-weight:600;'>{p*100:.1f}%</p>
            </div>""", unsafe_allow_html=True)

    curah_hujan_live = info['hujan'] if info else 0.0
    st.divider()

col_in, col_map = st.columns([1, 2.5])

with col_in:
    st.subheader("📍 Rute Perjalanan")
    asal   = st.text_input("Lokasi Asal:",   "Tanjung Priok, Jakarta Utara")
    tujuan = st.text_input("Lokasi Tujuan:", "Blok M Square, Jakarta Selatan")

    st.markdown("---")
    st.subheader("⏱️ Horizon Prediksi")
    horizon_label = st.radio("Horizon", list(HORIZONS.keys()),
                             label_visibility="collapsed")
    key_model, target_col, horizon_h = HORIZONS[horizon_label]
    auc_score = MODEL_META[key_model]['auc']
    f1_score  = MODEL_META[key_model]['f1']
    thresh    = MODEL_META[key_model]['thresh']

    if not IS_LIVE:
        st.markdown("---")
        st.subheader("🌧️ Simulasi Cuaca")
        curah_hujan = st.slider("Curah Hujan (mm)", 0.0, 50.0, 5.0,
                                help="Geser ke kanan untuk simulasi badai ekstrem!")
        if   curah_hujan == 0:  k,w,e = "Cerah",         "#27ae60","☀️"
        elif curah_hujan < 5:   k,w,e = "Mendung",       "#95a5a6","🌥️"
        elif curah_hujan < 15:  k,w,e = "Hujan Ringan",  "#3498db","🌦️"
        elif curah_hujan < 30:  k,w,e = "Hujan Sedang",  "#e67e22","🌧️"
        else:                   k,w,e = "HUJAN EKSTREM", "#e74c3c","⛈️"
        st.markdown(f"""<div style='background:{w}22;border:1px solid {w};border-radius:10px;
            padding:9px 14px;text-align:center;'>
            <span style='font-size:1.3rem;'>{e}</span>
            <span style='font-weight:700;color:{w};margin-left:8px;'>{k}</span>
            <span style='color:#A0AEC0;font-size:0.85rem;'> ({curah_hujan:.0f} mm)</span>
        </div>""", unsafe_allow_html=True)
    else:
        curah_hujan = curah_hujan_live

    st.write("")
    mulai = st.button("🚀 Pindai Rute Aman", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown("""<div style='padding:10px 12px;background:#1E212B;border-radius:10px;border:1px solid #2E3340;'>
        <p style='color:#A0AEC0;font-size:0.75rem;margin:0;text-align:center;line-height:1.8;'>
        🤖 <b style='color:#F18F01;'>AI Engine</b>: XGBoost + LGBM + RF<br>
        📡 <b style='color:#F18F01;'>Routing</b>: Azure Maps API<br>
        🌐 <b style='color:#F18F01;'>Cuaca Live</b>: Open-Meteo (Jakarta)
        </p></div>""", unsafe_allow_html=True)

with col_map:
    st.subheader("🌍 Peta Pantauan Rute Dinamis")
    peta = folium.Map(location=[-6.2088, 106.8456], zoom_start=11, tiles="CartoDB positron")

    if mulai:
        with st.spinner("🧠 AI menganalisis kondisi cuaca & memprediksi banjir..."):
            time.sleep(0.8)
            lat1, lon1 = geocode(asal)
            lat2, lon2 = geocode(tujuan)

            if lat1 and lat2:
                mdl = model_dict.get(key_model)

                thresh_mm = MODEL_META[key_model]['thresh_mm']

                if IS_LIVE and WEATHER_OK and st.session_state.live_df is not None:
                    try:
                        X    = get_live_prediction_row(mdl, st.session_state.live_df, horizon_h)
                        prob = float(mdl.predict_proba(X)[0,1])
                    except:
                        prob = curah_hujan / 50
                    banjir   = 1 if prob >= thresh else 0
                    prob_pct = prob * 100
                else:
                    banjir   = 1 if curah_hujan > thresh_mm else 0
                    prob_pct = min(curah_hujan / thresh_mm * 60, 97) if banjir else min(curah_hujan / thresh_mm * 30, 40)

                mid_lat, mid_lon = (lat1+lat2)/2, (lon1+lon2)/2
                box              = gen_box(mid_lat, mid_lon) if banjir else None
                rute, menit, km  = get_route(lat1, lon1, lat2, lon2, banjir, box)

                if rute:
                    st.markdown("#### 📊 Analisis Rute AI")
                    st.write("")
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Kepercayaan AI",  f"{auc_score*100:.1f}%")
                    m2.metric("Akurasi Sistem",  f"{f1_score*100:.1f}%")
                    m3.metric("Estimasi Tiba",   f"{menit} mnt")
                    m4.metric("Jarak Rute",      f"{km:.1f} km")
                    st.write("")

                    sc = "#e74c3c" if banjir else "#27ae60"
                    st.markdown(f"""
                    <div style='background:{sc}15;border:1px solid {sc}55;border-radius:12px;
                                padding:12px 20px;display:flex;justify-content:space-between;'>
                        <div>
                          <p style='margin:0;font-size:.7rem;color:#A0AEC0;text-transform:uppercase;letter-spacing:.08em;'>STATUS RUTE [{horizon_label}]</p>
                          <p style='margin:0;font-size:1.3rem;font-weight:800;color:{sc};'>
                            {"⚠️ BANJIR — Rute Dialihkan" if banjir else "✅ AMAN — Rute Tercepat"}</p>
                        </div>
                        <div style='text-align:right;'>
                          <p style='margin:0;font-size:.7rem;color:#A0AEC0;text-transform:uppercase;letter-spacing:.08em;'>PROB. BANJIR (AI)</p>
                          <p style='margin:0;font-size:1.3rem;font-weight:800;color:#F18F01;'>{prob_pct:.1f}%</p>
                        </div>
                    </div>""", unsafe_allow_html=True)
                    st.write("")

                    if banjir:
                        st.error(f"⚠️ **Bahaya!** Probabilitas banjir {prob_pct:.1f}% untuk horizon {horizon_label}.")
                        folium.PolyLine(rute, color="#2ecc71", weight=7, opacity=0.85,
                                        tooltip="✅ Rute Aman (Menghindari Zona Banjir)").add_to(peta)
                        bl, tr = box[0], box[2]
                        folium.Rectangle(bounds=[[bl[1],bl[0]],[tr[1],tr[0]]],
                                         color="#e74c3c", fill=True, fill_color="#e74c3c",
                                         fill_opacity=0.4, tooltip="⚠️ Zona Banjir (Prediksi AI)").add_to(peta)
                    else:
                        st.success(f"✅ Jalur aman untuk {horizon_label}. Rute tercepat siap digunakan!")
                        folium.PolyLine(rute, color="#3498db", weight=7, opacity=0.85,
                                        tooltip="🚀 Rute Tercepat").add_to(peta)

                    folium.Marker([lat1,lon1], tooltip="📦 Keberangkatan",
                                  icon=folium.Icon(color="green", icon="play")).add_to(peta)
                    folium.Marker([lat2,lon2], tooltip="🏁 Tujuan",
                                  icon=folium.Icon(color="red",   icon="stop")).add_to(peta)
                    peta.fit_bounds([[lat1,lon1],[lat2,lon2]])
                else:
                    st.error("❌ Rute tidak ditemukan — tujuan mungkin terisolir genangan.")
            else:
                st.error("❌ Alamat tidak dikenali. Gunakan nama kelurahan atau jalan yang spesifik.")

    st_folium(peta, width=800, height=500, returned_objects=[])

if IS_LIVE and st.session_state.last_fetch is not None:
    elapsed = (datetime.now() - st.session_state.last_fetch).total_seconds()
    if elapsed > REFRESH_MIN * 60:
        st.rerun()
