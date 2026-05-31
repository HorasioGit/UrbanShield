"use client";

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Polygon, Circle, useMap } from 'react-leaflet';
import L from 'leaflet';

// Fix Leaflet Default Icon Issue in Next.js
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
});

const truckIcon = new L.Icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/1048/1048313.png',
    iconSize: [40, 40],
    iconAnchor: [20, 40],
    popupAnchor: [0, -40]
});

// Component to dynamically fit bounds
function MapUpdater({ routeCoords }) {
    const map = useMap();
    useEffect(() => {
        if (routeCoords && routeCoords.length > 0) {
            const bounds = L.latLngBounds(routeCoords);
            map.fitBounds(bounds, { padding: [50, 50] });
        }
    }, [routeCoords, map]);
    return null;
}

export default function Map({ routeData }) {
    const [isMounted, setIsMounted] = useState(false);

    useEffect(() => {
        setIsMounted(true);
    }, []);

    if (!isMounted) return <div className="h-full w-full bg-zinc-900/50 animate-pulse rounded-xl flex items-center justify-center text-zinc-400">Memuat Peta Satelit...</div>;

    // Default view if no route data
    if (!routeData) {
        return (
            <MapContainer center={[-6.2088, 106.8456]} zoom={11} className="h-full w-full rounded-xl z-0" zoomControl={false}>
                <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" attribution='&copy; CARTO' />
            </MapContainer>
        );
    }

    const { origin_coords, destination_coords, route_coords, status, avoid_box, extra_flood_zones } = routeData;
    const isDanger = status === "REROUTED_AVOID_FLOOD";

    return (
        <MapContainer center={origin_coords || [-6.2088, 106.8456]} zoom={12} className="h-full w-full rounded-xl z-0" zoomControl={false}>
            <TileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            />
            
            {origin_coords && (
                <Marker position={origin_coords} icon={truckIcon}>
                    <Popup>Keberangkatan Armada</Popup>
                </Marker>
            )}
            
            {destination_coords && (
                <Marker position={destination_coords}>
                    <Popup>Tujuan Logistik</Popup>
                </Marker>
            )}

            {/* Flood Box (Fix: Azure returns [lon, lat], Leaflet needs [lat, lon]) */}
            {avoid_box && (
                <Polygon positions={avoid_box.map(coord => [coord[1], coord[0]])} pathOptions={{ color: '#ef4444', fillColor: '#ef4444', fillOpacity: 0.3 }}>
                    <Popup>Zona Blokade Rute (Prediksi AI)</Popup>
                </Polygon>
            )}

            {/* Extra Citywide Flood Zones */}
            {extra_flood_zones && extra_flood_zones.map((coord, idx) => (
                <Circle 
                    key={idx} 
                    center={coord} 
                    radius={1500} 
                    pathOptions={{ color: '#ef4444', fillColor: '#ef4444', fillOpacity: 0.2 }}
                >
                    <Popup>Titik Banjir Ekstrem Terpantau</Popup>
                </Circle>
            ))}

            {/* Active Route Polyline */}
            {route_coords && route_coords.length > 0 && (
                <Polyline 
                    positions={route_coords} 
                    color="#3b82f6" 
                    weight={6} 
                    opacity={0.85}
                />
            )}

            <MapUpdater routeCoords={route_coords} />
        </MapContainer>
    );
}
