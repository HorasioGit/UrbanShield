import pandas as pd
import re
import os

print("Memulai proses Data Engineering...")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'raw_dataset')

def parse_dates_generic(row):
    periode_str = str(row['periode_data'])
    if len(periode_str) == 6:
        year = periode_str[:4]
        month = periode_str[4:]
    else:
        return []
        
    tanggal_str = str(row['tanggal_kejadian'])
    if pd.isna(tanggal_str) or str(tanggal_str).lower() == 'nan':
        return []
    
    dates = []
    for y in ['2017', '2019', '2020', '2023']:
        tanggal_str = tanggal_str.replace(y, "")
        
    parts = str(tanggal_str).split(',')
    for part in parts:
        if '-' in part:
            subparts = part.split('-')
            if len(subparts) == 2:
                try:
                    start_match = re.search(r'\d+', subparts[0])
                    end_match = re.search(r'\d+', subparts[1])
                    if start_match and end_match:
                        start = int(start_match.group())
                        end = int(end_match.group())
                        for d in range(start, end + 1):
                             if 1 <= d <= 31:
                                 dates.append(f"{year}-{month}-{str(d).zfill(2)}")
                except:
                    pass
        else:
            nums = re.findall(r'\b(\d{1,2})\b', part)
            for n in nums:
                if 1 <= int(n) <= 31:
                    dates.append(f"{year}-{month}-{str(n).zfill(2)}")
    return list(set(dates))

flood_files = [
    'Filedata Data Kejadian Bencana Banjir di Provinsi DKI Jakarta Tahun 2017.csv',
    'Filedata Data Kejadian Bencana Banjir di Provinsi DKI Jakarta Tahun 2019.csv',
    'Filedata Data Kejadian Bencana Banjir di Provinsi DKI Jakarta Tahun 2020.csv'
]

df_list = []
for file in flood_files:
    file_path = os.path.join(RAW_DATA_DIR, file)
    if os.path.exists(file_path):
        df_temp = pd.read_csv(file_path)
        df_list.append(df_temp)

df_all = pd.concat(df_list, ignore_index=True)
df_all['parsed_dates'] = df_all.apply(parse_dates_generic, axis=1)
df_exploded = df_all.explode('parsed_dates').dropna(subset=['parsed_dates'])

df_exploded['kota_administrasi'] = df_exploded['kota_administrasi'].astype(str).str.lower().str.strip()
df_exploded['kota_administrasi'] = df_exploded['kota_administrasi'].replace({
    'jakarta urata': 'jakarta utara', 'jaksel': 'jakarta selatan', 'jaktim': 'jakarta timur',
    'jakpus': 'jakarta pusat', 'jakbar': 'jakarta barat', 'jakut': 'jakarta utara'
})

flood_events = df_exploded[['parsed_dates', 'kota_administrasi']].drop_duplicates()
flood_events = flood_events.rename(columns={'parsed_dates': 'tanggal'})
flood_events['status_banjir'] = 1

years = [2017, 2019, 2020]
master_df_list = []
cities = ['jakarta selatan', 'jakarta timur', 'jakarta utara', 'jakarta pusat', 'jakarta barat']
city_df = pd.DataFrame({'kota_administrasi': cities})

for y in years:
    date_rng = pd.date_range(start=f'{y}-01-01', end=f'{y}-12-31 23:00:00', freq='h')
    tmp_df = pd.DataFrame(date_rng, columns=['datetime'])
    tmp_df['tanggal'] = tmp_df['datetime'].dt.strftime('%Y-%m-%d')
    tmp_df['jam'] = tmp_df['datetime'].dt.strftime('%H:00')
    tmp_df = tmp_df.merge(city_df, how='cross')
    master_df_list.append(tmp_df)

flood_master = pd.concat(master_df_list, ignore_index=True)
flood_master = flood_master.merge(flood_events, on=['tanggal', 'kota_administrasi'], how='left')
flood_master['status_banjir'] = flood_master['status_banjir'].fillna(0).astype(int)

weather_files = {
    'jakarta_timur_meteo.csv': 'jakarta timur',
    'jakarta_selatan_meteo.csv': 'jakarta selatan',
    'jakarta_pusat_meteo.csv': 'jakarta pusat',
    'jakarta_barat_meteo.csv': 'jakarta barat',
    'jakarta_utara_meteo.csv': 'jakarta utara'
}

weather_list = []
for file, city in weather_files.items():
    file_path = os.path.join(RAW_DATA_DIR, file)
    if os.path.exists(file_path):
        w_df = pd.read_csv(file_path)
        w_df['kota_administrasi'] = city
        try:
            w_df['date'] = pd.to_datetime(w_df['date']).dt.tz_convert('Asia/Jakarta').dt.tz_localize(None)
        except AttributeError:
            w_df['date'] = pd.to_datetime(w_df['date']).dt.tz_localize('UTC').dt.tz_convert('Asia/Jakarta').dt.tz_localize(None)
        weather_list.append(w_df)

weather_master = pd.concat(weather_list, ignore_index=True)
weather_master = weather_master.rename(columns={'date': 'datetime'})
weather_master = weather_master[weather_master['datetime'].dt.year.isin([2017, 2019, 2020])]

final_abt = pd.merge(weather_master, flood_master, on=['datetime', 'kota_administrasi'], how='left')
final_abt['status_banjir'] = final_abt['status_banjir'].fillna(0).astype(int)

final_abt['tanggal'] = final_abt['datetime'].dt.strftime('%Y-%m-%d')
final_abt['jam'] = final_abt['datetime'].dt.strftime('%H:00')

final_abt = final_abt.sort_values(by=['kota_administrasi', 'datetime']).reset_index(drop=True)

final_abt['precip_3h_sum'] = final_abt.groupby('kota_administrasi')['precipitation'].transform(lambda x: x.rolling(3, min_periods=1).sum())
final_abt['precip_6h_sum'] = final_abt.groupby('kota_administrasi')['precipitation'].transform(lambda x: x.rolling(6, min_periods=1).sum())
final_abt['precip_12h_sum'] = final_abt.groupby('kota_administrasi')['precipitation'].transform(lambda x: x.rolling(12, min_periods=1).sum())

final_abt = final_abt.sort_values(by=['datetime', 'kota_administrasi']).reset_index(drop=True)

cols = ['datetime', 'tanggal', 'jam', 'kota_administrasi', 
        'temperature_2m', 'relative_humidity_2m', 'surface_pressure', 
        'wind_speed_10m', 'wind_direction_10m', 'weather_code', 'soil_temperature_0_to_7cm',
        'precipitation', 'precip_3h_sum', 'precip_6h_sum', 'precip_12h_sum', 'status_banjir']
final_abt = final_abt[[c for c in cols if c in final_abt.columns]]

output_file = os.path.join(RAW_DATA_DIR, 'UrbanShield_ABT_Final.csv')
final_abt.to_csv(output_file, index=False)
print(f"SUKSES! Dataset final berisi {'{:,}'.format(len(final_abt))} baris berhasil dibuat.")