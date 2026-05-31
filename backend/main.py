from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import joblib
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from features import prepare_nowcast_features, prepare_forecast_features
from azure_maps import geocode, gen_box, get_route

app = FastAPI(
    title="UrbanShield API",
    description="AI-Powered Flood Prediction & Logistics Advisory System",
    version="2.0.0"
)

# ─────────────────────────────────────────────────────────────────
# CORS — izinkan frontend Next.js (Azure Static Web Apps)
# Untuk produksi, ganti * dengan domain spesifik kamu
# ─────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────
# MODEL LOADING
# Path relatif dari posisi main.py → ../models/
# Bekerja baik di lokal maupun Azure App Service
# ─────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
# Cek apakah folder models ada sejajar (seperti di Azure flattened structure)
MODEL_DIR = os.path.join(BASE_DIR, "models")
if not os.path.exists(MODEL_DIR):
    # Jika tidak ada, naik satu folder (seperti di repo lokal)
    MODEL_DIR = os.path.join(BASE_DIR, "..", "models")

models = {}


def load_model(filename: str):
    path = os.path.join(MODEL_DIR, filename)
    if not os.path.exists(path):
        print(f"[WARNING] Model tidak ditemukan: {path}")
        return None
    try:
        data = joblib.load(path)
        # Jika .pkl adalah dict (metadata + model), ambil key 'model'
        if isinstance(data, dict) and 'model' in data:
            return data['model']
        return data
    except Exception as e:
        print(f"[ERROR] Gagal load {filename}: {e}")
        return None


@app.on_event("startup")
def startup_event():
    print("=" * 50)
    print("UrbanShield API — Starting up...")
    print(f"Model directory: {os.path.abspath(MODEL_DIR)}")
    models['nowcast'] = load_model("model_nowcast_xgboost.pkl")
    models['3h']      = load_model("model_forecast_3h.pkl")
    models['6h']      = load_model("model_forecast_6h.pkl")
    models['12h']     = load_model("model_forecast_12h.pkl")
    loaded = [k for k, v in models.items() if v is not None]
    print(f"Models loaded: {loaded}")
    print("=" * 50)


# ─────────────────────────────────────────────────────────────────
# SCHEMA
# ─────────────────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    # Input cuaca utama
    precipitation:       float = 0.0
    precip_3h_sum:       float = 0.0
    precip_6h_sum:       float = 0.0
    precip_12h_sum:      float = 0.0
    temperature_2m:      float = 27.0
    relative_humidity_2m:float = 80.0
    surface_pressure:    float = 1010.0
    wind_speed_10m:      float = 5.0
    wind_direction_10m:  float = 180.0
    weather_code:        float = 0.0
    soil_temperature_0_to_7cm: float = 26.0
    bogor_rain:          float = 0.0
    kota_encoded:        int   = 1
    is_simulation:       bool  = False
    # Waktu (opsional, default ke jam 12 bulan 1)
    hour:       int = 12
    month:      int = 1
    day_of_week:int = 0
    # Fitur tambahan opsional (lag, dsb)
    dynamic_features: Optional[Dict[str, float]] = None


class AdvisorRequest(BaseModel):
    probability:          float
    distance_km:          float = 15.0
    detour_km:            float = 3.5


class RouteRequest(BaseModel):
    origin:               str
    destination:          str
    probability:          float
    detour_cost_per_km:   float = 15000.0


# ─────────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "UrbanShield API is running 🌊", "version": "2.0.0"}


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "models_loaded": {k: (v is not None) for k, v in models.items()},
        "azure_maps": bool(os.environ.get("AZURE_MAPS_KEY")),
    }


@app.post("/api/predict")
def predict(req: PredictRequest):
    """
    Prediksi probabilitas banjir untuk 4 horizon waktu:
    - 0h  : nowcasting (kondisi saat ini)
    - 3h  : 3 jam ke depan
    - 6h  : 6 jam ke depan
    - 12h : 12 jam ke depan
    """
    # Kumpulkan semua input ke satu dict
    input_data = req.dict(exclude={"dynamic_features"})
    if req.dynamic_features:
        input_data.update(req.dynamic_features)

    # Hitung fitur waktu cyclical (agar konsisten dengan training)
    hour  = input_data.get('hour', 12)
    month = input_data.get('month', 1)
    input_data['musim']      = 1 if month in [11, 12, 1, 2, 3, 4] else 0
    input_data['is_weekend'] = 1 if input_data.get('day_of_week', 0) >= 5 else 0
    input_data['hour_sin']   = float(np.sin(2 * np.pi * hour  / 24))
    input_data['hour_cos']   = float(np.cos(2 * np.pi * hour  / 24))
    input_data['month_sin']  = float(np.sin(2 * np.pi * month / 12))
    input_data['month_cos']  = float(np.cos(2 * np.pi * month / 12))
    input_data['day_of_year']= int(input_data.get('day_of_week', 0))  # approx

    df_now = prepare_nowcast_features(input_data)
    df_fc  = prepare_forecast_features(input_data)

    result = {}
    try:
        if models.get('nowcast'):
            result['0h'] = round(float(models['nowcast'].predict_proba(df_now)[0][1]), 4)

        for horizon in ['3h', '6h', '12h']:
            if models.get(horizon):
                result[horizon] = round(float(models[horizon].predict_proba(df_fc)[0][1]), 4)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

    # =================================================================
    # SUTRADARA DEMO (SIMULATION OVERRIDE)
    # =================================================================
    if req.is_simulation:
        for horizon in result.keys():
            if req.precipitation >= 35:
                # Bahaya (akan memicu avoid_box dan detour karena > 0.6)
                result[horizon] = round(min(0.68, result[horizon] + 0.65), 4)
            elif req.precipitation >= 20:
                # Waspada (probability naik tapi belum sampai detour)
                result[horizon] = round(min(0.49, result[horizon] + 0.35), 4)

    return {"predictions": result}


@app.post("/api/advisor")
def advisor(req: AdvisorRequest):
    """
    AI Logistics Advisor: analisis finansial & rekomendasi tindakan
    berdasarkan probabilitas banjir.
    """
    prob = req.probability

    # Asumsi finansial
    TRUCK_LOSS_COST    = 2_500_000   # Rp 2.5 Juta jika terjebak banjir
    DETOUR_COST_PER_KM = 15_000      # Rp 15 Ribu per KM extra

    detour_cost = req.detour_km * DETOUR_COST_PER_KM
    risk_value  = prob * TRUCK_LOSS_COST

    if prob > 0.6:
        action  = "REROUTE"
        savings = TRUCK_LOSS_COST - detour_cost
        text    = (
            f"🚨 [BAHAYA] Probabilitas banjir sangat tinggi ({prob*100:.1f}%). "
            f"Rute armada telah dialihkan otomatis. "
            f"Keputusan ini menyelamatkan potensi kerugian Rp {TRUCK_LOSS_COST:,.0f} "
            f"dengan biaya tambahan hanya Rp {detour_cost:,.0f}."
        )
    elif prob > 0.35:
        action  = "PROCEED_WITH_CAUTION"
        savings = 0.0
        text    = (
            f"⚠️ [WASPADA] Risiko genangan ringan ({prob*100:.1f}%). "
            f"Perjalanan dapat dilanjutkan dengan ekstra hati-hati."
        )
    else:
        action  = "PROCEED"
        savings = 0.0
        text    = (
            f"✅ [AMAN] Rute terpantau aman dari potensi banjir ({prob*100:.1f}%). "
            f"Silakan lanjutkan perjalanan normal."
        )

    return {
        "text":   text,
        "action": action,
        "financials": {
            "potential_loss": TRUCK_LOSS_COST,
            "detour_cost":    detour_cost,
            "risk_value":     round(risk_value, 0),
            "net_savings":    max(savings, 0),
        }
    }


@app.post("/api/route")
def route(req: RouteRequest):
    """
    Kalkulasi rute logistik dengan integrasi Azure Maps.
    Jika probabilitas banjir > 0.6, rute akan menghindari area banjir.
    """
    lat1, lon1 = geocode(req.origin)
    lat2, lon2 = geocode(req.destination)

    if lat1 is None or lat2 is None:
        raise HTTPException(
            status_code=400,
            detail="Alamat tidak dikenali. Gunakan nama kelurahan/daerah spesifik."
        )

    is_danger = req.probability > 0.6

    # 1. Dapatkan Rute Normal Tercepat Terlebih Dahulu
    # 1. Dapatkan Rute Normal Tercepat Terlebih Dahulu
    route_coords, eta_mins, dist_km_normal = get_route(lat1, lon1, lat2, lon2)

    if not route_coords:
        raise HTTPException(
            status_code=500,
            detail="Gagal mengkalkulasi rute awal."
        )

    box = None
    extra_flood_zones = []
    dist_km_final = dist_km_normal

    if is_danger:
        # Ambil aspal yang benar-benar dilewati truk di tengah perjalanan
        mid_idx = len(route_coords) // 2
        mid_point_asphalt = route_coords[mid_idx]

        # Buat kotak banjir presisi di atas aspal tersebut
        box = gen_box(mid_point_asphalt[0], mid_point_asphalt[1])

        extra_flood_zones = [
            [-6.1557, 106.9011],  # Kelapa Gading
            [-6.1628, 106.7371],  # Cengkareng
            [-6.2103, 106.8512],  # Manggarai
            [-6.2625, 106.8127],  # Kemang
        ]

        # 2. Kalkulasi ulang rute dengan memaksa Azure Maps memutar menghindari aspal tersebut
        # 2. Kalkulasi ulang rute dengan memaksa Azure Maps memutar menghindari aspal tersebut
        route_coords, eta_mins, dist_km_final = get_route(lat1, lon1, lat2, lon2, avoid_box=box)

        if not route_coords:
            raise HTTPException(
                status_code=500,
                detail="Gagal mengkalkulasi rute detour."
            )

    return {
        "status":            "REROUTED_AVOID_FLOOD" if is_danger else "NORMAL_ROUTE",
        "origin_coords":     [lat1, lon1],
        "destination_coords":[lat2, lon2],
        "route_coords":      route_coords,
        "eta_mins":          eta_mins,
        "dist_km":           round(dist_km_final, 2),
        "dist_km_normal":    round(dist_km_normal, 2),
        "detour_km":         round(max(0, dist_km_final - dist_km_normal), 2) if is_danger else 0.0,
        "avoid_box":         box,
        "extra_flood_zones": extra_flood_zones,
    }
