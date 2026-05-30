import pandas as pd
import numpy as np

# ─────────────────────────────────────────────────────────────────
# NOWCAST FEATURES — sync dengan notebook final (40 fitur)
# ─────────────────────────────────────────────────────────────────
NOWCAST_FEATURES = [
    'temperature_2m', 'relative_humidity_2m', 'surface_pressure', 'wind_speed_10m', 'wind_direction_10m', 'weather_code', 'soil_temperature_0_to_7cm', 'precipitation', 'precip_3h_sum', 'precip_6h_sum', 'precip_12h_sum', 'bogor_rain', 'bogor_rain_lag1', 'bogor_rain_roll3', 'bogor_x_precip', 'kota_encoded', 'hour', 'month', 'day_of_week', 'musim', 'is_weekend', 'precip_ratio_3_12', 'precip_ratio_6_12', 'precip_intensity', 'rain_score', 'saturation_idx', 'heat_index', 'wind_energy', 'is_raining', 'heavy_rain', 'rain_x_humidity', 'high_rain_flag', 'rain_persistence', 'consec_rain_approx', 'precip_max_3h', 'precip_max_6h', 'hour_sin', 'hour_cos', 'month_sin', 'month_cos'
]

# ─────────────────────────────────────────────────────────────────
# FORECAST FEATURES — dari make_forecast_features notebook
# ─────────────────────────────────────────────────────────────────
FORECAST_FEATURES = [
    'temperature_2m', 'relative_humidity_2m', 'surface_pressure', 'wind_speed_10m', 'wind_direction_10m', 'weather_code', 'soil_temperature_0_to_7cm', 'precipitation', 'bogor_rain', 'precip_3h_sum', 'precip_6h_sum', 'precip_12h_sum', 'hour', 'month', 'day_of_week', 'day_of_year', 'is_weekend', 'musim', 'kota_encoded', 'hour_sin', 'hour_cos', 'month_sin', 'month_cos', 'precip_ratio_3_12', 'precip_ratio_6_12', 'precip_intensity', 'rain_score', 'saturation_idx', 'heat_index', 'wind_energy', 'is_raining', 'heavy_rain', 'rain_x_humidity', 'bogor_x_precip', 'high_rain_flag', 'rain_persistence', 'consec_rain_approx', 'bogor_rain_lag1', 'bogor_rain_roll3', 'precip_max_3h', 'precip_max_6h', 'precipitation_lag1', 'precipitation_lag3', 'precipitation_lag6', 'precipitation_lag12', 'precip_3h_sum_lag1', 'precip_3h_sum_lag3', 'precip_3h_sum_lag6', 'precip_3h_sum_lag12', 'precip_6h_sum_lag1', 'precip_6h_sum_lag3', 'precip_6h_sum_lag6', 'precip_6h_sum_lag12', 'precip_12h_sum_lag1', 'precip_12h_sum_lag3', 'precip_12h_sum_lag6', 'precip_12h_sum_lag12', 'bogor_rain_lag3', 'bogor_rain_lag6', 'bogor_rain_lag12', 'status_banjir_lag1', 'status_banjir_lag3', 'status_banjir_lag6', 'status_banjir_lag12', 'temperature_2m_lag1', 'temperature_2m_lag3', 'temperature_2m_lag6', 'relative_humidity_2m_lag1', 'relative_humidity_2m_lag3', 'relative_humidity_2m_lag6', 'surface_pressure_lag1', 'surface_pressure_lag3', 'surface_pressure_lag6', 'wind_speed_10m_lag1', 'wind_speed_10m_lag3', 'wind_speed_10m_lag6', 'soil_temperature_0_to_7cm_lag1', 'soil_temperature_0_to_7cm_lag3', 'soil_temperature_0_to_7cm_lag6', 'weather_code_lag1', 'weather_code_lag3', 'weather_code_lag6', 'precipitation_roll3_mean', 'precipitation_roll3_max', 'precipitation_roll3_std', 'precipitation_roll6_mean', 'precipitation_roll6_max', 'precipitation_roll6_std', 'precipitation_roll12_mean', 'precipitation_roll12_max', 'precipitation_roll12_std', 'precip_3h_sum_roll3_mean', 'precip_3h_sum_roll3_max', 'precip_3h_sum_roll3_std', 'precip_3h_sum_roll6_mean', 'precip_3h_sum_roll6_max', 'precip_3h_sum_roll6_std', 'precip_3h_sum_roll12_mean', 'precip_3h_sum_roll12_max', 'precip_3h_sum_roll12_std', 'precip_6h_sum_roll3_mean', 'precip_6h_sum_roll3_max', 'precip_6h_sum_roll3_std', 'precip_6h_sum_roll6_mean', 'precip_6h_sum_roll6_max', 'precip_6h_sum_roll6_std', 'precip_6h_sum_roll12_mean', 'precip_6h_sum_roll12_max', 'precip_6h_sum_roll12_std', 'precip_12h_sum_roll3_mean', 'precip_12h_sum_roll3_max', 'precip_12h_sum_roll3_std', 'precip_12h_sum_roll6_mean', 'precip_12h_sum_roll6_max', 'precip_12h_sum_roll6_std', 'precip_12h_sum_roll12_mean', 'precip_12h_sum_roll12_max', 'precip_12h_sum_roll12_std', 'bogor_rain_roll3_mean', 'bogor_rain_roll3_max', 'bogor_rain_roll3_std', 'bogor_rain_roll6_mean', 'bogor_rain_roll6_max', 'bogor_rain_roll6_std', 'bogor_rain_roll12_mean', 'bogor_rain_roll12_max', 'bogor_rain_roll12_std', 'relative_humidity_2m_roll3_mean', 'relative_humidity_2m_roll6_mean', 'temperature_2m_roll3_mean', 'temperature_2m_roll6_mean', 'precip_trend_3h', 'precip_trend_6h', 'rain_acceleration', 'consec_rain'
]


def _compute_engineered(df, precip, precip_3h, precip_6h, precip_12h,
                         humidity, temperature, bogor):
    """Hitung semua fitur engineered dari raw input."""

    # Rain score (weighted accumulation) — formula resmi dari notebook
    df.at[0, 'rain_score'] = (
        precip * 0.4 + precip_3h * 0.3 + precip_6h * 0.2 + precip_12h * 0.1
    )

    # Saturation index — formula non-redundan (bukan hanya precip * humidity)
    df.at[0, 'saturation_idx'] = humidity * (1 - np.exp(-precip / 5)) if precip > 0 else 0.0

    # Heat index
    df.at[0, 'heat_index'] = temperature * humidity / 100

    # Precip ratios
    df.at[0, 'precip_ratio_3_12']  = precip_3h  / (precip_12h + 0.001)
    df.at[0, 'precip_ratio_6_12']  = precip_6h  / (precip_12h + 0.001)
    df.at[0, 'precip_intensity']   = precip      / (precip_3h  + 0.001)

    # Wind energy
    wind = float(df.at[0, 'wind_speed_10m'])
    df.at[0, 'wind_energy'] = wind ** 2

    # Rain flags
    df.at[0, 'is_raining']  = 1.0 if precip > 0 else 0.0
    df.at[0, 'heavy_rain']  = 1.0 if precip >= 10 else 0.0

    # Bogor interactions
    df.at[0, 'bogor_x_precip']  = bogor * precip
    df.at[0, 'rain_x_humidity'] = precip * humidity

    # Rain persistence & flag
    df.at[0, 'rain_persistence'] = precip_6h  / (precip_12h + 0.001)
    df.at[0, 'high_rain_flag']   = 1.0 if precip_12h > 5.0 else 0.0  # threshold approx Q85

    # Consecutive rain (approximate dari 3 window)
    df.at[0, 'consec_rain_approx'] = (
        (1 if precip_3h  > 0 else 0) +
        (1 if precip_6h  > 0 else 0) +
        (1 if precip_12h > 0 else 0)
    )

    # Rolling max approximation (pakai precip_3h / precip_6h sebagai proxy)
    df.at[0, 'precip_max_3h'] = precip_3h
    df.at[0, 'precip_max_6h'] = precip_6h

    return df


def prepare_nowcast_features(input_data: dict) -> pd.DataFrame:
    """
    Siapkan feature vector untuk model nowcasting (prediksi saat ini).
    Semua fitur diinisialisasi 0, lalu diisi dari input_data dan
    fitur engineered dihitung ulang secara benar.
    """
    df = pd.DataFrame(0.0, index=[0], columns=NOWCAST_FEATURES)

    # Override dengan input_data yang tersedia
    for key, val in input_data.items():
        if key in NOWCAST_FEATURES:
            df.at[0, key] = float(val)

    # Ambil nilai raw untuk kalkulasi engineered
    precip     = float(input_data.get('precipitation',      0.0))
    precip_3h  = float(input_data.get('precip_3h_sum',      0.0))
    precip_6h  = float(input_data.get('precip_6h_sum',      0.0))
    precip_12h = float(input_data.get('precip_12h_sum',     0.0))
    humidity   = float(input_data.get('relative_humidity_2m', 80.0))
    temperature= float(input_data.get('temperature_2m',     27.0))
    bogor      = float(input_data.get('bogor_rain',          0.0))

    df = _compute_engineered(df, precip, precip_3h, precip_6h, precip_12h,
                              humidity, temperature, bogor)

    return df.astype(float)


def prepare_forecast_features(input_data: dict) -> pd.DataFrame:
    """
    Siapkan feature vector untuk model forecasting (+3h/+6h/+12h).
    Lag & rolling features diambil dari input_data jika tersedia,
    atau default 0 (asumsi: tidak ada riwayat = kondisi kering).
    """
    df = pd.DataFrame(0.0, index=[0], columns=FORECAST_FEATURES)

    for key, val in input_data.items():
        if key in FORECAST_FEATURES:
            df.at[0, key] = float(val)

    precip     = float(input_data.get('precipitation',      0.0))
    precip_3h  = float(input_data.get('precip_3h_sum',      0.0))
    precip_6h  = float(input_data.get('precip_6h_sum',      0.0))
    precip_12h = float(input_data.get('precip_12h_sum',     0.0))
    humidity   = float(input_data.get('relative_humidity_2m', 80.0))
    temperature= float(input_data.get('temperature_2m',     27.0))
    bogor      = float(input_data.get('bogor_rain',          0.0))

    df = _compute_engineered(df, precip, precip_3h, precip_6h, precip_12h,
                              humidity, temperature, bogor)

    return df.astype(float)
