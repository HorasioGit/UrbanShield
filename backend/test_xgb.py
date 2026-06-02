import joblib
import os
import pandas as pd
from features import prepare_nowcast_features

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
path = os.path.join(MODEL_DIR, "model_nowcast_xgboost.pkl")

print(f"Memuat {path}")
model = joblib.load(path)
if isinstance(model, dict) and 'model' in model:
    model = model['model']

print("Model ter-load:", type(model))
print("Fitur model:")
try:
    print(model.feature_names_in_)
except:
    pass
    
df = prepare_nowcast_features({"precipitation": 10})
print("\nFitur DF kita:")
print(df.columns.tolist())

try:
    print("\nMencoba prediksi...")
    model.predict_proba(df)
    print("Berhasil!")
except Exception as e:
    print(f"GAGAL: {e}")
