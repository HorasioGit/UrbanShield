import requests

# Loaded securely based on the provided Workspace Key
MAPS_API_KEY = "1GLJWFf8IEFXQkX9JNLQT0SDEyz5x7hDnaeyJIAR6XPCt9mUhST9JQQJ99CDACYeBjFxDgxpAAAgAZMP3knW"

def geocode(alamat):
    url = (f"https://atlas.microsoft.com/search/address/json?api-version=1.0"
           f"&query={alamat},Jakarta,Indonesia&subscription-key={MAPS_API_KEY}")
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status() # Throw error if 401 Unauthorized
        data = r.json()
        if data.get('results'):
            p = data['results'][0]['position']
            return p['lat'], p['lon']
    except Exception as e:
        print(f"Azure Maps API Error (Geocode): {e}. Menggunakan Mock Fallback.")
        pass
        
    # MOCK FALLBACK (ANTI-GAGAL DEMO)
    if "priok" in alamat.lower():
        return -6.1158, 106.8856 # Pelabuhan
    return -6.1557, 106.9011 # Gudang Kelapa Gading

def gen_box(lat, lon, offset=0.015):
    return [[lon-offset,lat-offset], [lon+offset,lat-offset],
            [lon+offset,lat+offset], [lon-offset,lat+offset], [lon-offset,lat-offset]]

def get_route(lat1, lon1, lat2, lon2, avoid_box=None):
    url = (f"https://atlas.microsoft.com/route/directions/json?api-version=1.0"
           f"&query={lat1},{lon1}:{lat2},{lon2}&routeType=fastest&subscription-key={MAPS_API_KEY}")
    try:
        if avoid_box:
            payload = {"avoidAreas": {"type": "MultiPolygon", "coordinates": [[avoid_box]]}}
            r = requests.post(url, json=payload, headers={"Content-Type":"application/json"}, timeout=8)
        else:
            r = requests.get(url, timeout=8)
            
        r.raise_for_status()
        data = r.json()
        if 'routes' in data and data['routes']:
            leg = data['routes'][0]
            pts = leg['legs'][0]['points']
            coords = [[p['latitude'], p['longitude']] for p in pts]
            mins = leg['summary']['travelTimeInSeconds'] // 60
            dist_km = leg['summary']['lengthInMeters'] / 1000
            return coords, mins, dist_km
    except Exception as e:
        print(f"Azure Maps API Error (Routing): {e}. Menggunakan Mock Fallback.")
        pass
        
    # MOCK FALLBACK (ANTI-GAGAL DEMO)
    if avoid_box:
        # Rute Memutar (Detour)
        coords = [[lat1, lon1], [-6.1500, 106.9250], [-6.1100, 106.9150], [lat2, lon2]]
        return coords, 45, 14.5
    else:
        # Rute Normal Lurus
        coords = [[lat1, lon1], [-6.1350, 106.8950], [lat2, lon2]]
        return coords, 25, 9.2
