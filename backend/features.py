import pandas as pd
import numpy as np

# Exact features from XGBoost models
NOWCAST_FEATURES = ['temperature_2m', 'relative_humidity_2m', 'surface_pressure', 'wind_speed_10m', 'wind_direction_10m', 'weather_code', 'soil_temperature_0_to_7cm', 'precipitation', 'precip_3h_sum', 'precip_6h_sum', 'precip_12h_sum', 'kota_encoded', 'hour', 'month', 'day_of_week', 'musim', 'is_weekend', 'precip_ratio_3_12', 'precip_ratio_6_12', 'precip_intensity', 'rain_score', 'saturation_idx', 'heat_index', 'wind_energy', 'is_raining', 'heavy_rain', 'hour_sin', 'hour_cos', 'month_sin', 'month_cos']

FORECAST_FEATURES = ['temperature_2m', 'relative_humidity_2m', 'surface_pressure', 'wind_speed_10m', 'wind_direction_10m', 'weather_code', 'soil_temperature_0_to_7cm', 'precipitation', 'bogor_rain', 'precip_3h_sum', 'precip_6h_sum', 'precip_12h_sum', 'hour', 'month', 'day_of_week', 'day_of_year', 'is_weekend', 'musim', 'kota_encoded', 'hour_sin', 'hour_cos', 'month_sin', 'month_cos', 'precip_ratio_3_12', 'precip_ratio_6_12', 'precip_intensity', 'rain_score', 'saturation_idx', 'heat_index', 'wind_energy', 'is_raining', 'heavy_rain', 'precipitation_lag1', 'precipitation_lag3', 'precipitation_lag6', 'precipitation_lag12', 'precip_3h_sum_lag1', 'precip_3h_sum_lag3', 'precip_3h_sum_lag6', 'precip_3h_sum_lag12', 'precip_6h_sum_lag1', 'precip_6h_sum_lag3', 'precip_6h_sum_lag6', 'precip_6h_sum_lag12', 'precip_12h_sum_lag1', 'precip_12h_sum_lag3', 'precip_12h_sum_lag6', 'precip_12h_sum_lag12', 'bogor_rain_lag1', 'bogor_rain_lag3', 'bogor_rain_lag6', 'bogor_rain_lag12', 'status_banjir_lag1', 'status_banjir_lag3', 'status_banjir_lag6', 'status_banjir_lag12', 'temperature_2m_lag1', 'temperature_2m_lag3', 'temperature_2m_lag6', 'relative_humidity_2m_lag1', 'relative_humidity_2m_lag3', 'relative_humidity_2m_lag6', 'surface_pressure_lag1', 'surface_pressure_lag3', 'surface_pressure_lag6', 'wind_speed_10m_lag1', 'wind_speed_10m_lag3', 'wind_speed_10m_lag6', 'soil_temperature_0_to_7cm_lag1', 'soil_temperature_0_to_7cm_lag3', 'soil_temperature_0_to_7cm_lag6', 'weather_code_lag1', 'weather_code_lag3', 'weather_code_lag6', 'precipitation_roll3_mean', 'precipitation_roll3_max', 'precipitation_roll3_std', 'precipitation_roll6_mean', 'precipitation_roll6_max', 'precipitation_roll6_std', 'precipitation_roll12_mean', 'precipitation_roll12_max', 'precipitation_roll12_std', 'precip_3h_sum_roll3_mean', 'precip_3h_sum_roll3_max', 'precip_3h_sum_roll3_std', 'precip_3h_sum_roll6_mean', 'precip_3h_sum_roll6_max', 'precip_3h_sum_roll6_std', 'precip_3h_sum_roll12_mean', 'precip_3h_sum_roll12_max', 'precip_3h_sum_roll12_std', 'precip_6h_sum_roll3_mean', 'precip_6h_sum_roll3_max', 'precip_6h_sum_roll3_std', 'precip_6h_sum_roll6_mean', 'precip_6h_sum_roll6_max', 'precip_6h_sum_roll6_std', 'precip_6h_sum_roll12_mean', 'precip_6h_sum_roll12_max', 'precip_6h_sum_roll12_std', 'precip_12h_sum_roll3_mean', 'precip_12h_sum_roll3_max', 'precip_12h_sum_roll3_std', 'precip_12h_sum_roll6_mean', 'precip_12h_sum_roll6_max', 'precip_12h_sum_roll6_std', 'precip_12h_sum_roll12_mean', 'precip_12h_sum_roll12_max', 'precip_12h_sum_roll12_std', 'bogor_rain_roll3_mean', 'bogor_rain_roll3_max', 'bogor_rain_roll3_std', 'bogor_rain_roll6_mean', 'bogor_rain_roll6_max', 'bogor_rain_roll6_std', 'bogor_rain_roll12_mean', 'bogor_rain_roll12_max', 'bogor_rain_roll12_std', 'relative_humidity_2m_roll3_mean', 'relative_humidity_2m_roll6_mean', 'temperature_2m_roll3_mean', 'temperature_2m_roll6_mean', 'precip_trend_3h', 'precip_trend_6h', 'rain_acceleration', 'consec_rain']

def prepare_nowcast_features(input_data):
    df = pd.DataFrame(columns=NOWCAST_FEATURES)
    df.loc[0] = 0.0 # Initialize all as 0.0 (safe default / padding)
    
    # Override with actual input data where available
    for key, val in input_data.items():
        if key in NOWCAST_FEATURES:
            df.at[0, key] = val
            
    # Simulate some basic engineered features from raw input
    precip = float(input_data.get('precipitation', 0))
    df.at[0, 'precipitation'] = precip
    df.at[0, 'is_raining'] = 1 if precip > 0 else 0
    df.at[0, 'heavy_rain'] = 1 if precip >= 10 else 0
    df.at[0, 'precip_intensity'] = precip / 3.0 # mock
    df.at[0, 'rain_score'] = precip * 1.5 # mock
    
    # Ensure types are correct for XGBoost
    return df.astype(float)

def prepare_forecast_features(input_data):
    df = pd.DataFrame(columns=FORECAST_FEATURES)
    df.loc[0] = 0.0 # Initialize all as 0.0 (safe default / padding)
    
    for key, val in input_data.items():
        if key in FORECAST_FEATURES:
            df.at[0, key] = val
            
    # Basic Feature Engineering
    precip = float(input_data.get('precipitation', 0))
    df.at[0, 'precipitation'] = precip
    df.at[0, 'is_raining'] = 1 if precip > 0 else 0
    df.at[0, 'heavy_rain'] = 1 if precip >= 10 else 0
    df.at[0, 'precip_intensity'] = precip / 3.0
    df.at[0, 'rain_score'] = precip * 1.5
    
    # The lag features (status_banjir_lag1, etc.) remain 0 as per user agreement
    # unless specifically provided via input_data.
    
    return df.astype(float)
