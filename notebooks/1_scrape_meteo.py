import openmeteo_requests
import pandas as pd
import requests_cache
import os
from retry_requests import retry

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '../data/raw_dataset')

cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

locations = {
    'jakarta_pusat'  : {'latitude': -6.1805, 'longitude': 106.8284},
    'jakarta_utara'  : {'latitude': -6.1214, 'longitude': 106.8926},
    'jakarta_barat'  : {'latitude': -6.1683, 'longitude': 106.7588},
    'jakarta_selatan': {'latitude': -6.2615, 'longitude': 106.8106},
    'jakarta_timur'  : {'latitude': -6.2250, 'longitude': 106.9004},
    'bogor_hulu'     : {'latitude': -6.6333, 'longitude': 106.8167}
}

years = [2017, 2018, 2019, 2020]

url = 'https://archive-api.open-meteo.com/v1/archive'

hourly_variables = [
    'temperature_2m',
    'weather_code',
    'precipitation',
    'soil_temperature_0_to_7cm',
    'relative_humidity_2m',
    'surface_pressure',
    'wind_speed_10m',
    'wind_direction_10m',
]

for loc_name, coords in locations.items():
    print(f'Scraping: {loc_name.upper()}')
    print(f"  Koordinat: {coords['latitude']}, {coords['longitude']}")

    all_years_df = []

    for year in years:
        params = {
            'latitude' : coords['latitude'],
            'longitude': coords['longitude'],
            'start_date': f'{year}-01-01',
            'end_date'  : f'{year}-12-31',
            'hourly'    : hourly_variables,
            'timezone'  : 'Asia/Bangkok',
        }

        responses = openmeteo.weather_api(url, params=params)
        response  = responses[0]

        hourly = response.Hourly()

        hourly_data = {'date': pd.date_range(
            start     = pd.to_datetime(hourly.Time()    + response.UtcOffsetSeconds(), unit='s', utc=True),
            end       = pd.to_datetime(hourly.TimeEnd() + response.UtcOffsetSeconds(), unit='s', utc=True),
            freq      = pd.Timedelta(seconds=hourly.Interval()),
            inclusive = 'left',
        )}

        for i, var in enumerate(hourly_variables):
            hourly_data[var] = hourly.Variables(i).ValuesAsNumpy()

        df_year = pd.DataFrame(data=hourly_data)
        all_years_df.append(df_year)
        print(f'  [{year}] OK -> {len(df_year)} baris')

    df_combined = pd.concat(all_years_df, ignore_index=True)
    df_combined = df_combined.sort_values('date').reset_index(drop=True)

    output_file = os.path.join(DATA_DIR, f'{loc_name}_meteo.csv')
    df_combined.to_csv(output_file, index=False)
    print(f'  Saved  -> {output_file}  (total {len(df_combined)} baris)')

print('SELESAI! File CSV berhasil dibuat (2017-2020).')
