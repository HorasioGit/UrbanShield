import requests
import pandas as pd
import numpy as np
from datetime import datetime

JAKARTA_LAT = -6.2088
JAKARTA_LON = 106.8456

RAIN_COLS    = ['precipitation', 'precip_3h_sum', 'precip_6h_sum', 'precip_12h_sum']
WEATHER_COLS = ['temperature_2m', 'relative_humidity_2m', 'surface_pressure',
                'wind_speed_10m', 'soil_temperature_0_to_7cm', 'weather_code']


def fetch_live_weather(lat=JAKARTA_LAT, lon=JAKARTA_LON):
    """
    Ambil data cuaca jam-jaman real-time dari Open-Meteo API (gratis, tanpa API key).
    Mengambil 3 hari ke belakang + 2 hari ke depan untuk rolling/lag features.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": [
            "precipitation", "temperature_2m", "relative_humidity_2m",
            "surface_pressure", "wind_speed_10m", "weather_code", "soil_temperature_0cm",
        ],
        "past_days": 3, "forecast_days": 2,
        "timezone": "Asia/Jakarta",
    }
    resp = requests.get(url, params=params, timeout=20)
    resp.raise_for_status()
    h = resp.json()['hourly']

    df = pd.DataFrame({
        'datetime':                 pd.to_datetime(h['time']),
        'precipitation':            pd.array(h['precipitation'],        dtype=float),
        'temperature_2m':           pd.array(h['temperature_2m'],       dtype=float),
        'relative_humidity_2m':     pd.array(h['relative_humidity_2m'], dtype=float),
        'surface_pressure':         pd.array(h['surface_pressure'],     dtype=float),
        'wind_speed_10m':           pd.array(h['wind_speed_10m'],       dtype=float),
        'weather_code':             pd.array(h['weather_code'],         dtype=float),
        'soil_temperature_0_to_7cm': pd.array(
            h.get('soil_temperature_0cm', [28.0] * len(h['time'])), dtype=float),
    })

    df['precipitation']              = df['precipitation'].fillna(0.0)
    df['soil_temperature_0_to_7cm']  = df['soil_temperature_0_to_7cm'].fillna(28.0)
    df = df.ffill().bfill()

    # Rolling sum curah hujan (sama dengan training)
    df['precip_3h_sum']  = df['precipitation'].rolling(3,  min_periods=1).sum()
    df['precip_6h_sum']  = df['precipitation'].rolling(6,  min_periods=1).sum()
    df['precip_12h_sum'] = df['precipitation'].rolling(12, min_periods=1).sum()

    # Dummy kolom untuk feature engineering
    df['kota_administrasi'] = 'Jakarta Pusat'
    df['status_banjir']     = 0

    return df.reset_index(drop=True)


def _build_live_features(df, horizon_h):
    """
    Jalankan feature engineering yang identik dengan training (tanpa groupby).
    Kembalikan 1 baris: jam paling terkini yang punya data lengkap.
    """
    df = df.copy().sort_values('datetime').reset_index(drop=True)

    # Fitur waktu & Cyclical
    df['hour']        = df['datetime'].dt.hour
    df['month']       = df['datetime'].dt.month
    df['day_of_week'] = df['datetime'].dt.dayofweek
    df['day_of_year'] = df['datetime'].dt.dayofyear
    df['is_weekend']  = (df['day_of_week'] >= 5).astype(int)
    df['musim']       = df['month'].apply(lambda m: 1 if m in [11, 12, 1, 2, 3, 4] else 0)
    
    df['hour_sin']    = np.sin(2 * np.pi * df['hour']  / 24)
    df['hour_cos']    = np.cos(2 * np.pi * df['hour']  / 24)
    df['month_sin']   = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos']   = np.cos(2 * np.pi * df['month'] / 12)

    # Kota encoded (Jakarta Pusat = 1 sesuai mapping notebook)
    df['kota_encoded'] = 1

    # Lag features — hujan & status
    for col in RAIN_COLS + ['status_banjir']:
        for lag in [1, 3, 6, 12]:
            df[f'{col}_lag{lag}'] = df[col].shift(lag)

    # Lag features — cuaca
    for col in WEATHER_COLS:
        for lag in [1, 3, 6]:
            df[f'{col}_lag{lag}'] = df[col].shift(lag)

    # Rolling features (shift 1 dulu = no leakage)
    for col in RAIN_COLS:
        for win in [3, 6, 12]:
            s = df[col].shift(1)
            df[f'{col}_roll{win}_mean'] = s.rolling(win).mean()
            df[f'{col}_roll{win}_max']  = s.rolling(win).max()
            df[f'{col}_roll{win}_std']  = s.rolling(win).std()

    for col in ['relative_humidity_2m', 'temperature_2m']:
        for win in [3, 6]:
            df[f'{col}_roll{win}_mean'] = df[col].shift(1).rolling(win).mean()

    # Tren & akselerasi hujan
    df['precip_trend_3h']   = df['precipitation'] - df['precipitation'].shift(3)
    df['precip_trend_6h']   = df['precipitation'] - df['precipitation'].shift(6)
    df['rain_acceleration'] = (df['precip_trend_3h'] -
                               df['precipitation'].shift(1).diff(3))

    # Streak hujan berturut-turut
    df['is_raining']  = (df['precipitation'] > 0).astype(int)
    df['consec_rain'] = df['is_raining'].groupby(
        (df['is_raining'] != df['is_raining'].shift()).cumsum()
    ).cumcount()

    # Rasio & Composite features
    df['precip_ratio_3_12']  = df['precip_3h_sum']  / (df['precip_12h_sum'] + 0.001)
    df['precip_ratio_6_12']  = df['precip_6h_sum']  / (df['precip_12h_sum'] + 0.001)
    df['precip_intensity']   = df['precipitation']  / (df['precip_3h_sum']  + 0.001)

    df['rain_score']     = (df['precipitation'] * 0.4 + df['precip_3h_sum'] * 0.3 +
                            df['precip_6h_sum'] * 0.2 + df['precip_12h_sum'] * 0.1)
    df['saturation_idx'] = df['relative_humidity_2m'] * df['precipitation'] / 100
    df['heat_index']     = df['temperature_2m'] * df['relative_humidity_2m'] / 100
    df['wind_energy']    = df['wind_speed_10m'] ** 2
    df['heavy_rain']     = (df['precipitation'] > df['precipitation'].quantile(0.90)).astype(int)

    # Ambil baris paling terkini yang datanya sudah lengkap
    now = pd.Timestamp.now()
    df_past = df[df['datetime'] <= now].dropna(subset=RAIN_COLS)
    return df_past.iloc[[-1]] if len(df_past) > 0 else df.dropna().iloc[[-1]]


def get_live_prediction_row(model, df_raw, horizon_h=0):
    """
    Bangun fitur dari df_raw dan kembalikan X yang siap di-predict_proba.
    """
    row = _build_live_features(df_raw, horizon_h)

    try:
        feat_cols = model.feature_names_in_.tolist()
        available = [c for c in feat_cols if c in row.columns]
        X = row[available].copy()
        for mc in [c for c in feat_cols if c not in row.columns]:
            X[mc] = 0.0
        X = X[feat_cols]
    except AttributeError:
        exclude = {'datetime', 'kota_administrasi', 'status_banjir',
                   'target_3h', 'target_6h', 'target_12h'}
        X = row[[c for c in row.columns if c not in exclude]]

    return X


def get_current_weather_info(df_raw):
    """Ambil ringkasan cuaca jam ini dari df_raw."""
    now = pd.Timestamp.now()
    df_past = df_raw[df_raw['datetime'] <= now]
    r = df_past.iloc[-1] if len(df_past) > 0 else df_raw.iloc[-1]
    return {
        'waktu':     r['datetime'].strftime('%d %b %Y, %H:%M WIB'),
        'hujan':     round(float(r['precipitation']), 1),
        'suhu':      round(float(r['temperature_2m']), 1),
        'lembab':    round(float(r['relative_humidity_2m']), 1),
        'angin':     round(float(r['wind_speed_10m']), 1),
        'hujan_3h':  round(float(r['precip_3h_sum']), 1),
        'hujan_6h':  round(float(r['precip_6h_sum']), 1),
        'hujan_12h': round(float(r['precip_12h_sum']), 1),
        'kode':      int(r['weather_code']),
    }


def describe_weather_code(code):
    """Terjemahkan WMO weather code ke label, emoji, dan warna."""
    if code == 0:   return "Cerah",          "☀️",  "#F9A825"
    if code <= 3:   return "Berawan",         "⛅",  "#90A4AE"
    if code <= 49:  return "Berkabut",        "🌫️", "#B0BEC5"
    if code <= 67:  return "Gerimis",         "🌦️", "#42A5F5"
    if code <= 77:  return "Hujan Ringan",    "🌧️", "#1976D2"
    if code <= 84:  return "Hujan Lebat",     "🌧️", "#0D47A1"
    if code <= 99:  return "Badai Petir ⚡",  "⛈️", "#D32F2F"
    return "Tidak Diketahui", "❓", "#9E9E9E"
