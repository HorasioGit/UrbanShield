import joblib
import os
import pandas as pd
from features import prepare_nowcast_features, prepare_forecast_features

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
input_data = {'precipitation': 10, 'temperature_2m': 28, 'kota_encoded': 1}

df_now = prepare_nowcast_features(input_data)
df_fc  = prepare_forecast_features(input_data)

def test_model(name, filename, df):
    path = os.path.join(MODEL_DIR, filename)
    model = joblib.load(path)
    if isinstance(model, dict) and 'model' in model:
        model = model['model']
    
    try:
        model.predict_proba(df)
        print(f"[{name}] SUCCESS")
    except Exception as e:
        print(f"[{name}] ERROR: {e}")

test_model("NOWCAST", "model_nowcast_xgboost.pkl", df_now)
test_model("FORECAST 3H", "model_forecast_3h.pkl", df_fc)
test_model("FORECAST 6H", "model_forecast_6h.pkl", df_fc)
test_model("FORECAST 12H", "model_forecast_12h.pkl", df_fc)
