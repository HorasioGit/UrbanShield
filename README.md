# 🛡️ UrbanShield
### *Navigasi Logistik Cerdas Berbasis Prediksi Cuaca AI*

> Sistem peringatan dini banjir dan rekomendasi rute evakuasi real-time untuk wilayah DKI Jakarta — dibangun untuk **AI Impact Challenge · Microsoft Elevate × Dicoding 2026**

[![Live App](https://img.shields.io/badge/🚀_Live_App-Azure_App_Service-0078D4?style=for-the-badge)](https://urbanshield-live-c6dmdaa8hmepd3bq.canadacentral-01.azurewebsites.net/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![XGBoost](https://img.shields.io/badge/XGBoost-189AB4?style=for-the-badge)](https://xgboost.readthedocs.io)

---

## 📌 Latar Belakang

Jakarta adalah salah satu kota dengan risiko banjir tertinggi di Asia Tenggara. Setiap tahunnya, banjir menyebabkan kerugian ekonomi dan menghambat mobilitas warga secara masif — namun sistem peringatan yang tersedia sering kali bersifat reaktif, bukan prediktif.

**UrbanShield** hadir sebagai solusi *early warning system* berbasis AI yang tidak hanya memprediksi potensi banjir, tetapi juga **secara aktif merekomendasikan rute evakuasi alternatif** yang menghindari area berisiko tinggi — menjawab kebutuhan nyata warga: *"Lewat mana kalau banjir?"*

---

## 🎯 Fitur Utama

| Fitur | Deskripsi |
|---|---|
| 🔴 **Live Flood Prediction** | Prediksi risiko banjir real-time dari data cuaca Open-Meteo API |
| ⏱️ **Multi-Horizon Forecast** | Prakiraan banjir untuk Nowcast, +3 Jam, +6 Jam, dan +12 Jam ke depan |
| 🗺️ **Smart Route Avoidance** | Rute perjalanan otomatis menghindari zona banjir via Azure Maps |
| 🎮 **Simulasi Manual** | Mode slider curah hujan untuk demo dan eksplorasi skenario |
| 📊 **Model Interpretability** | Transparansi prediksi berbasis SHAP feature importance |

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA SOURCES (Input)                     │
│  Open-Meteo API (real-time)  │  BPBD Jakarta (histori)     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                  FEATURE ENGINEERING                        │
│  Lag features · Rolling sum · Rain streak · Composite idx  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│               MODEL 1 — FLOOD PREDICTOR                    │
│   XGBoost (4 model): Nowcast │ +3h │ +6h │ +12h           │
│   Output: P(banjir) per horizon → zona risiko              │
└────────────────┬────────────────────────────────────────────┘
                 │ bobot zona risiko
                 ▼
┌─────────────────────────────────────────────────────────────┐
│               MODEL 2 — ROUTING ENGINE                     │
│   Azure Maps Route API + avoidAreas polygon                │
│   Output: Rute optimal menghindari zona banjir             │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              STREAMLIT APP (deployed on Azure)              │
│   Live Mode │ Simulasi Manual │ Peta Interaktif            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 Model Machine Learning

Empat model XGBoost ditraining secara terpisah dengan target horizon prediksi berbeda:

| Model | File | AUC | F1-Score | Threshold |
|---|---|---|---|---|
| Nowcast (T+0) | `model_nowcast_xgboost.pkl` | 0.9185 | 0.5133 | 0.20 |
| Forecast +3 Jam | `model_forecast_3h.pkl` | 0.9951 | 0.9188 | 0.35 |
| Forecast +6 Jam | `model_forecast_6h.pkl` | 0.9841 | 0.8456 | 0.35 |
| Forecast +12 Jam | `model_forecast_12h.pkl` | 0.9429 | 0.6827 | 0.40 |

**Data training:** Rekap kejadian banjir BPBD Jakarta (2017, 2019, 2020) digabungkan dengan data cuaca per jam dari Open-Meteo.  
**Split strategy:** Time-based split — 2017 & 2019 sebagai train set, 2020 sebagai test set (*unseen data*).  
**Imbalance handling:** `scale_pos_weight` pada XGBoost (rasio ~12.6:1).

### Fitur Utama Model
- **Lag features:** `precip_lag_1h`, `precip_lag_3h`, `precip_lag_6h`
- **Rolling sum:** `precip_3h_sum`, `precip_6h_sum`, `precip_12h_sum`, `precip_rolling_24h`
- **Temporal:** `month`, `hour_sin`, `hour_cos`, `is_rainy_season`, `is_weekend`
- **Composite:** `rain_score`, `saturation_idx`, `consec_rain`, `rain_acceleration`
- **Weather:** `temperature_2m`, `relative_humidity_2m`, `weather_code` (WMO ordinal), `wind_speed_10m`

---

## ☁️ Layanan Microsoft Azure

| Layanan | Fungsi dalam UrbanShield |
|---|---|
| **Azure App Service** | Hosting aplikasi Streamlit + model AI (Python runtime) |
| **Azure App Service Plan** | Alokasi CPU & RAM untuk server production |
| **Azure Maps — Geocoding API** | Konversi nama lokasi/alamat ke koordinat lat/lon |
| **Azure Maps — Route Directions API** | Kalkulasi rute optimal dengan avoidAreas polygon zona banjir |
| **Azure Resource Group** | Manajemen terpusat semua layanan di atas |

---

## 📂 Struktur Repositori

```
UrbanShield/
│
├── 1_scrap_meteo.ipynb          # Scraping data cuaca Open-Meteo per jam
├── 2_datathon_prepros.py        # Preprocessing & agregasi ABT dataset
├── 3_UrbanShield_Code.ipynb     # EDA, Feature Engineering, dan Modeling lengkap
│
├── app.py                       # Aplikasi Streamlit utama
├── weather.py                   # Modul Live Weather API & feature engineering
│
├── model_nowcast_xgboost.pkl    # Model prediksi banjir T+0
├── model_forecast_3h.pkl        # Model prediksi banjir T+3 jam
├── model_forecast_6h.pkl        # Model prediksi banjir T+6 jam
├── model_forecast_12h.pkl       # Model prediksi banjir T+12 jam
│
├── UrbanShield_ABT_Final.csv    # Dataset ABT hasil agregasi (bahan training)
├── UrbanShield_Base_Engineered.csv  # Dataset setelah feature engineering
│
├── raw_dataset/                 # Dataset mentah sebelum preprocessing
├── requirements.txt             # Dependensi Python
└── .github/workflows/           # CI/CD pipeline (GitHub Actions)
```

---

## 🚀 Cara Menjalankan Lokal

### 1. Clone repositori
```bash
git clone https://github.com/HorasioGit/UrbanShield.git
cd UrbanShield
```

### 2. Install dependensi
```bash
pip install -r requirements.txt
```

### 3. Set environment variable
```bash
# Windows
set AZURE_MAPS_KEY=your_azure_maps_key_here

# Linux/Mac
export AZURE_MAPS_KEY=your_azure_maps_key_here
```

### 4. Jalankan aplikasi
```bash
streamlit run app.py
```

Aplikasi akan terbuka di `http://localhost:8501`

---

## 📊 Dataset

| Dataset | Sumber | Periode | Keterangan |
|---|---|---|---|
| Rekap Kejadian Banjir | BPBD Jakarta / Satu Data Jakarta | 2017, 2019, 2020 | Label target per hari per wilayah |
| Data Cuaca Per Jam | Open-Meteo Historical API | 2017, 2019, 2020 | Scraping per jam, 5 koordinat Jakarta |

> **Catatan keterbatasan data:** Data banjir tahun 2018 dan di luar periode di atas tidak digunakan karena format rekap tidak konsisten (fitur tidak lengkap, agregasi bulanan). Label banjir dari BPBD bersifat per hari, kemudian dipetakan ke level jam menggunakan intensitas curah hujan sebagai proxy temporal.

---

## 👥 Tim

| Nama | GitHub |
|---|---|
| Horasio Nissi Immanuel | [@HorasioGit](https://github.com/HorasioGit) |
| [Rizki Piji Fathoni] | [@Rizki0907](https://github.com/Rizki0907) |

---

## 📄 Lisensi

Project ini dibuat untuk keperluan kompetisi **AI Impact Challenge — Microsoft Elevate × Dicoding 2026**.

---

<p align="center">
  <img src="https://img.shields.io/badge/Made_with-❤️_&_XGBoost-FF4B4B?style=flat-square" />
  <img src="https://img.shields.io/badge/Powered_by-Microsoft_Azure-0078D4?style=flat-square&logo=microsoftazure" />
  <img src="https://img.shields.io/badge/Data-BPBD_Jakarta_×_Open--Meteo-27AE60?style=flat-square" />
</p>