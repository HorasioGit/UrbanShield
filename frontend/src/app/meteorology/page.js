"use client";

import { CloudLightning, Thermometer, Wind, Droplets } from 'lucide-react';
import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';

const MapContainer = dynamic(() => import('react-leaflet').then(mod => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import('react-leaflet').then(mod => mod.TileLayer), { ssr: false });
const CircleMarker = dynamic(() => import('react-leaflet').then(mod => mod.CircleMarker), { ssr: false });
const Popup = dynamic(() => import('react-leaflet').then(mod => mod.Popup), { ssr: false });

export default function MeteorologyHub() {
    const [isMounted, setIsMounted] = useState(false);

    useEffect(() => {
        setIsMounted(true);
    }, []);

    const nodes = [
        { name: "Jakarta Utara (Priok)", lat: -6.1158, lon: 106.8856, rain: 45, color: '#ef4444' },
        { name: "Jakarta Pusat (Monas)", lat: -6.1751, lon: 106.8272, rain: 15, color: '#f59e0b' },
        { name: "Jakarta Selatan (Blok M)", lat: -6.2444, lon: 106.8006, rain: 2, color: '#10b981' },
        { name: "Depok", lat: -6.4025, lon: 106.8227, rain: 0, color: '#10b981' },
        { name: "Bogor (Bendung Katulampa)", lat: -6.6345, lon: 106.8344, rain: 60, color: '#ef4444' }
    ];

    return (
        <main className="p-8 pb-20 overflow-x-hidden flex flex-col h-screen">
            <header className="mb-6 shrink-0 z-10">
                <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center">
                    <CloudLightning className="w-8 h-8 mr-3 text-cyan-400" />
                    Meteorological Radar
                    <span className="ml-4 px-2 py-0.5 text-[10px] bg-amber-500/20 text-amber-400 border border-amber-500/50 rounded-full flex items-center uppercase tracking-widest font-bold">
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse mr-1.5"></span>
                        Simulated Telemetry
                    </span>
                </h1>
                <p className="text-slate-400 mt-2">Pemantauan titik-titik krusial hidrologi dari Jakarta hingga Bendung Katulampa Bogor (Purwarupa Demonstrasi).</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6 shrink-0 z-10">
                <div className="glass-panel p-4 border-l-2 border-l-cyan-500 flex items-center space-x-4">
                    <Thermometer className="w-8 h-8 text-cyan-400" />
                    <div>
                        <p className="text-[10px] text-slate-400 uppercase tracking-widest font-bold">Rata-Rata Suhu</p>
                        <p className="text-2xl font-black text-white">28.5°C</p>
                    </div>
                </div>
                <div className="glass-panel p-4 border-l-2 border-l-blue-500 flex items-center space-x-4">
                    <Droplets className="w-8 h-8 text-blue-400" />
                    <div>
                        <p className="text-[10px] text-slate-400 uppercase tracking-widest font-bold">Kelembapan Udara</p>
                        <p className="text-2xl font-black text-white">82%</p>
                    </div>
                </div>
                <div className="glass-panel p-4 border-l-2 border-l-slate-400 flex items-center space-x-4">
                    <Wind className="w-8 h-8 text-slate-400" />
                    <div>
                        <p className="text-[10px] text-slate-400 uppercase tracking-widest font-bold">Kecepatan Angin</p>
                        <p className="text-2xl font-black text-white">14 km/h</p>
                    </div>
                </div>
                <div className="glass-panel p-4 border-l-2 border-l-rose-500 flex items-center space-x-4">
                    <CloudLightning className="w-8 h-8 text-rose-400 animate-pulse" />
                    <div>
                        <p className="text-[10px] text-rose-400 uppercase tracking-widest font-bold">Status Katulampa</p>
                        <p className="text-2xl font-black text-rose-400">Siaga 2</p>
                    </div>
                </div>
            </div>

            <div className="flex-1 glass-panel rounded-2xl overflow-hidden border border-slate-700 relative z-10 shadow-2xl">
                {isMounted ? (
                    <MapContainer center={[-6.25, 106.84]} zoom={10} className="h-full w-full" zoomControl={false}>
                        <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />
                        {nodes.map(node => (
                            <CircleMarker 
                                key={node.name}
                                center={[node.lat, node.lon]}
                                pathOptions={{ color: node.color, fillColor: node.color }}
                                radius={node.rain > 30 ? 30 : node.rain > 10 ? 15 : 8}
                                fillOpacity={0.4}
                            >
                                <Popup>
                                    <b>{node.name}</b><br/>Curah Hujan: {node.rain} mm
                                </Popup>
                            </CircleMarker>
                        ))}
                    </MapContainer>
                ) : (
                     <div className="h-full w-full bg-slate-900/50 animate-pulse flex items-center justify-center">Loading Satelit...</div>
                )}
            </div>
        </main>
    );
}
