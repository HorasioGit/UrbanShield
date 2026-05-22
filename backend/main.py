from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import joblib
import pandas as pd
import numpy as np
import os

from features import prepare_nowcast_features, prepare_forecast_features
from azure_maps import geocode, gen_box, get_route

app = FastAPI(title="UrbanShield 2.0 Backend", description="AI Logistics Advisor & Predictions")

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load XGBoost Models
MODEL_DIR = r"D:\Data Science\Microsoft Elevate\UrbanShield\models"
models = {}

def load_model(name):
    path = os.path.join(MODEL_DIR, name)
    if os.path.exists(path):
        try:
            data = joblib.load(path)
            # Handle if the joblib is a dict with meta, else just return model
            if isinstance(data, dict) and 'model' in data:
                return data['model']
            return data
        except Exception as e:
            print(f"Failed to load {name}: {e}")
            return None
    return None

@app.on_event("startup")
def startup_event():
    print("Loading models...")
    models['nowcast'] = load_model("model_nowcast_xgboost.pkl")
    models['3h'] = load_model("model_forecast_3h.pkl")
    models['6h'] = load_model("model_forecast_6h.pkl")
    models['12h'] = load_model("model_forecast_12h.pkl")
    print(f"Loaded models: {list(models.keys())}")

class PredictRequest(BaseModel):
    # Base input variables that might come from frontend/real-time API
    precipitation: float = 0.0
    temperature_2m: float = 27.0
    kota_encoded: int = 1
    # Allow any other dynamic overrides (like lags)
    dynamic_features: Optional[Dict[str, float]] = None

@app.get("/api/health")
def health():
    return {
        "status": "ok", 
        "models_loaded": {k: (v is not None) for k, v in models.items()}
    }

@app.post("/api/predict")
def predict(req: PredictRequest):
    input_data = req.dict()
    if req.dynamic_features:
        input_data.update(req.dynamic_features)
    
    # Prepare features for XGBoost
    df_now = prepare_nowcast_features(input_data)
    df_fc = prepare_forecast_features(input_data)
    
    res = {}
    try:
        if models.get('nowcast'):
            prob = float(models['nowcast'].predict_proba(df_now)[0][1])
            res['0h'] = prob
            
        for h in ['3h', '6h', '12h']:
            if models.get(h):
                prob = float(models[h].predict_proba(df_fc)[0][1])
                res[h] = prob
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
            
    return {"predictions": res}

class AdvisorRequest(BaseModel):
    probability: float
    distance_km: float = 15.0 # origin to dest route
    detour_km: float = 3.5    # extra distance if reroute

@app.post("/api/advisor")
def advisor(req: AdvisorRequest):
    """
    Logistics Financial Optimizer & AI Advisor Logic
    """
    prob = req.probability
    
    # Financial optimizer assumptions
    TRUCK_LOSS_COST = 2500000    # Rp 2.5 Juta if trapped in flood
    DETOUR_COST_PER_KM = 15000   # Rp 15 Ribu per KM extra fuel/time
    
    detour_total_cost = req.detour_km * DETOUR_COST_PER_KM
    risk_value = prob * TRUCK_LOSS_COST
    
    if prob > 0.6:
        advisor_text = f"🚨 [ADVISORY] Bahaya! Probabilitas banjir sangat tinggi ({(prob*100):.1f}%). Rute armada telah dialihkan otomatis. Keputusan reroute ini menyelamatkan Anda dari potensi kerugian sebesar Rp {TRUCK_LOSS_COST:,.0f} dengan biaya operasional tambahan hanya Rp {detour_total_cost:,.0f}."
        action = "REROUTE"
        savings = TRUCK_LOSS_COST - detour_total_cost
    elif prob > 0.35:
        advisor_text = f"⚠️ [WARNING] Waspada genangan ringan ({(prob*100):.1f}%). Perjalanan dapat dilanjutkan dengan ekstra hati-hati. Kecepatan mungkin melambat."
        action = "PROCEED_WITH_CAUTION"
        savings = 0.0
    else:
        advisor_text = f"✅ [SAFE] Rute logistik terpantau aman dari potensi banjir ({(prob*100):.1f}%). Silakan lanjutkan perjalanan normal."
        action = "PROCEED"
        savings = 0.0
        
    return {
        "text": advisor_text,
        "action": action,
        "financials": {
            "potential_loss": TRUCK_LOSS_COST,
            "detour_cost": detour_total_cost,
            "risk_value": risk_value,
            "net_savings": savings
        }
    }

class RouteRequest(BaseModel):
    origin: str
    destination: str
    probability: float
    detour_cost_per_km: float = 15000

@app.post("/api/route")
def route(req: RouteRequest):
    """
    Real integration with Azure Maps geocoding and routing.
    """
    lat1, lon1 = geocode(req.origin)
    lat2, lon2 = geocode(req.destination)
    
    if not lat1 or not lat2:
        raise HTTPException(status_code=400, detail="Alamat tidak dikenali. Gunakan nama kelurahan/daerah spesifik.")
        
    is_danger = req.probability > 0.6
    
    # Calculate mid point for flood box if danger
    mid_lat, mid_lon = (lat1+lat2)/2, (lon1+lon2)/2
    box = gen_box(mid_lat, mid_lon) if is_danger else None
    
    route_coords, eta_mins, dist_km = get_route(lat1, lon1, lat2, lon2, avoid_box=box)
    
    if not route_coords:
        raise HTTPException(status_code=400, detail="Gagal mengkalkulasi rute dari satelit.")
        
    return {
        "status": "REROUTED_AVOID_FLOOD" if is_danger else "NORMAL_ROUTE",
        "origin_coords": [lat1, lon1],
        "destination_coords": [lat2, lon2],
        "route_coords": route_coords,
        "eta_mins": eta_mins,
        "dist_km": dist_km,
        "avoid_box": box
    }
