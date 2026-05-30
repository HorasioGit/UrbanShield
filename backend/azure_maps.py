import os
import requests

# ─────────────────────────────────────────────────────────────────
# API Key dari environment variable (JANGAN hardcode di kode!)
# Set di Azure App Service: Configuration > Application Settings
# Key: AZURE_MAPS_KEY  Value: <your-key>
# Untuk dev lokal: buat file .env atau set environment variable
# ─────────────────────────────────────────────────────────────────
MAPS_API_KEY = os.environ.get("AZURE_MAPS_KEY", "")


def geocode(alamat: str):
    """
    Konversi nama alamat ke koordinat (lat, lon) menggunakan Azure Maps.
    Fallback ke koordinat mock jika API tidak tersedia.
    """
    if MAPS_API_KEY:
        url = (
            f"https://atlas.microsoft.com/search/address/json"
            f"?api-version=1.0"
            f"&query={alamat},Jakarta,Indonesia"
            f"&subscription-key={MAPS_API_KEY}"
        )
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            data = r.json()
            if data.get('results'):
                p = data['results'][0]['position']
                return p['lat'], p['lon']
        except Exception as e:
            print(f"[Azure Maps] Geocode error: {e} — switching to fallback.")

    # ── MOCK FALLBACK (anti-gagal demo) ──
    alamat_lower = alamat.lower()
    fallback_coords = {
        "priok":          (-6.1158, 106.8856),
        "tanjung priok":  (-6.1158, 106.8856),
        "penjaringan":    (-6.1176, 106.8026),
        "pluit":          (-6.1100, 106.7967),
        "kelapa gading":  (-6.1557, 106.9011),
        "cengkareng":     (-6.1628, 106.7371),
        "manggarai":      (-6.2103, 106.8512),
        "katulampa":      (-6.6500, 106.8500),
        "gambir":         (-6.1764, 106.8227),
        "sudirman":       (-6.2146, 106.8187),
    }
    for keyword, coords in fallback_coords.items():
        if keyword in alamat_lower:
            return coords
    # Default: Monas Jakarta
    return (-6.1751, 106.8272)


def gen_box(lat: float, lon: float, offset: float = 0.015):
    """Buat bounding box polygon di sekitar titik koordinat (area flood zone)."""
    return [
        [lon - offset, lat - offset],
        [lon + offset, lat - offset],
        [lon + offset, lat + offset],
        [lon - offset, lat + offset],
        [lon - offset, lat - offset],  # tutup polygon
    ]


def get_route(lat1: float, lon1: float, lat2: float, lon2: float,
              avoid_box=None):
    """
    Dapatkan rute antara dua titik koordinat via Azure Maps.
    Jika avoid_box diberikan, rute akan menghindari area tersebut (flood zone).
    Fallback ke rute mock jika API tidak tersedia.

    Returns:
        (coords, eta_minutes, distance_km)
    """
    if MAPS_API_KEY:
        url = (
            f"https://atlas.microsoft.com/route/directions/json"
            f"?api-version=1.0"
            f"&query={lat1},{lon1}:{lat2},{lon2}"
            f"&routeType=fastest"
            f"&subscription-key={MAPS_API_KEY}"
        )
        try:
            if avoid_box:
                payload = {
                    "avoidAreas": {
                        "type": "MultiPolygon",
                        "coordinates": [[avoid_box]]
                    }
                }
                r = requests.post(
                    url, json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=8
                )
            else:
                r = requests.get(url, timeout=8)

            r.raise_for_status()
            data = r.json()

            if 'routes' in data and data['routes']:
                leg      = data['routes'][0]
                pts      = leg['legs'][0]['points']
                coords   = [[p['latitude'], p['longitude']] for p in pts]
                eta_mins = leg['summary']['travelTimeInSeconds'] // 60
                dist_km  = leg['summary']['lengthInMeters'] / 1000
                return coords, eta_mins, dist_km

        except Exception as e:
            print(f"[Azure Maps] Routing error: {e} — switching to fallback.")

    # ── MOCK FALLBACK ──
    if avoid_box:
        # Rute memutar (detour menghindari banjir)
        coords   = [[lat1, lon1], [-6.1500, 106.9250], [-6.1100, 106.9150], [lat2, lon2]]
        eta_mins = 45
        dist_km  = 14.5
    else:
        # Rute normal
        coords   = [[lat1, lon1], [-6.1350, 106.8950], [lat2, lon2]]
        eta_mins = 25
        dist_km  = 9.2

    return coords, eta_mins, dist_km
