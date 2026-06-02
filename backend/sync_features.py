import joblib
import os
import re

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

# 1. Ekstrak dari Nowcast
m_nowcast = joblib.load(os.path.join(MODEL_DIR, "model_nowcast_xgboost.pkl"))
if isinstance(m_nowcast, dict) and 'model' in m_nowcast: m_nowcast = m_nowcast['model']
nowcast_features = list(m_nowcast.feature_names_in_)

# 2. Ekstrak dari Forecast (ambil 3h sebagai referensi)
m_forecast = joblib.load(os.path.join(MODEL_DIR, "model_forecast_3h.pkl"))
if isinstance(m_forecast, dict) and 'model' in m_forecast: m_forecast = m_forecast['model']
forecast_features = list(m_forecast.feature_names_in_)

print(f"Nowcast features: {len(nowcast_features)}")
print(f"Forecast features: {len(forecast_features)}")

# 3. Update features.py
filepath = os.path.join(os.path.dirname(__file__), "features.py")
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace list
def format_list(lst):
    return "[\n    " + ", ".join([f"'{x}'" for x in lst]) + "\n]"

content = re.sub(r"NOWCAST_FEATURES\s*=\s*\[.*?\]", f"NOWCAST_FEATURES = {format_list(nowcast_features)}", content, flags=re.DOTALL)
content = re.sub(r"FORECAST_FEATURES\s*=\s*\[.*?\]", f"FORECAST_FEATURES = {format_list(forecast_features)}", content, flags=re.DOTALL)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ features.py berhasil disinkronisasi 100% dengan model PKL!")
