"use client";

import { CloudLightning, Thermometer, Wind, Droplets, Activity } from 'lucide-react';
import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';

const MapContainer = dynamic(() => import('react-leaflet').then(mod => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import('react-leaflet').then(mod => mod.TileLayer), { ssr: false });
const CircleMarker = dynamic(() => import('react-leaflet').then(mod => mod.CircleMarker), { ssr: false });
const Circle = dynamic(() => import('react-leaflet').then(mod => mod.Circle), { ssr: false });
const Popup = dynamic(() => import('react-leaflet').then(mod => mod.Popup), { ssr: false });

export default function MeteorologyHub() {
    const [isMounted, setIsMounted] = useState(false);
    const [showRain, setShowRain] = useState(true);
    const [showTopography, setShowTopography] = useState(false);
    const [showHistorical, setShowHistorical] = useState(false);
    
    const [realTemp, setRealTemp] = useState("...");
    const [realHumid, setRealHumid] = useState("...");
    const [realWind, setRealWind] = useState("...");
    const [katulampaStatus, setKatulampaStatus] = useState("...");
    
    const initialNodes = [
        { name: "Jakarta Utara (Priok)", lat: -6.1158, lon: 106.8856, rain: 0, color: '#10b981' },
        { name: "Jakarta Pusat (Monas)", lat: -6.1751, lon: 106.8272, rain: 0, color: '#10b981' },
        { name: "Jakarta Selatan (Blok M)", lat: -6.2444, lon: 106.8006, rain: 0, color: '#10b981' },
        { name: "Depok", lat: -6.4025, lon: 106.8227, rain: 0, color: '#10b981' },
        { name: "Bogor (Bendung Katulampa)", lat: -6.6345, lon: 106.8344, rain: 0, color: '#10b981' }
    ];
    
    const [liveNodes, setLiveNodes] = useState(initialNodes);

    useEffect(() => {
        setIsMounted(true);
        fetchRealtimeData();
    }, []);

    const fetchRealtimeData = async () => {
        try {
            // Fetch for Jakarta Center (for the top cards)
            const res = await fetch('https://api.open-meteo.com/v1/forecast?latitude=-6.2088&longitude=106.8456&current=temperature_2m,relative_humidity_2m,wind_speed_10m&timezone=Asia/Jakarta');
            const data = await res.json();
            if (data && data.current) {
                setRealTemp(`${data.current.temperature_2m}°C`);
                setRealHumid(`${data.current.relative_humidity_2m}%`);
                setRealWind(`${data.current.wind_speed_10m} km/h`);
            }
            
            // Fetch for Bogor (Katulampa)
            const bogorRes = await fetch('https://api.open-meteo.com/v1/forecast?latitude=-6.6345&longitude=106.8344&current=precipitation&timezone=Asia/Jakarta');
            const bogorData = await bogorRes.json();
            let bRain = 0;
            if (bogorData && bogorData.current) {
                bRain = bogorData.current.precipitation;
                if (bRain > 50) setKatulampaStatus("Siaga 1");
                else if (bRain > 20) setKatulampaStatus("Siaga 2");
                else if (bRain > 5) setKatulampaStatus("Siaga 3");
                else setKatulampaStatus("Siaga 4 (Aman)");
            }

            // Update Nodes with real precipitation
            const updatedNodes = await Promise.all(initialNodes.map(async (node) => {
                const nRes = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${node.lat}&longitude=${node.lon}&current=precipitation&timezone=Asia/Jakarta`);
                const nData = await nRes.json();
                let rain = 0;
                if (nData && nData.current) {
                    rain = nData.current.precipitation;
                }
                
                let color = '#10b981'; // Green
                if (rain > 10) color = '#f59e0b'; // Yellow
                if (rain > 30) color = '#ef4444'; // Red
                
                return { ...node, rain, color };
            }));
            
            setLiveNodes(updatedNodes);

        } catch (error) {
            console.error("Gagal mengambil data meteo realtime", error);
            setRealTemp("Error");
            setRealHumid("Error");
            setRealWind("Error");
            setKatulampaStatus("Error");
        }
    };

    const topoNodes = [
        { name: "Penjaringan (0.5m mdpl)", lat: -6.1176, lon: 106.8026, elevation: 0.5, radius: 2500 },
        { name: "Tanjung Priok (1.0m mdpl)", lat: -6.1158, lon: 106.8856, elevation: 1.0, radius: 2000 },
        { name: "Kelapa Gading (2.0m mdpl)", lat: -6.1557, lon: 106.9011, elevation: 2.0, radius: 2200 },
        { name: "Cengkareng (3.0m mdpl)", lat: -6.1628, lon: 106.7371, elevation: 3.0, radius: 2800 }
    ];

    const historicalHotspots = [
        { name: "Titik Banjir Sunter Jaya (1.200 Kejadian)", lat: -6.1420, lon: 106.8780, incidents: 1200, radius: 1500 },
        { name: "Titik Banjir Pluit (850 Kejadian)", lat: -6.1100, lon: 106.7967, incidents: 850, radius: 1200 },
        { name: "Titik Banjir Manggarai (2.100 Kejadian)", lat: -6.2103, lon: 106.8512, incidents: 2100, radius: 1800 },
        { name: "Titik Banjir Kemang (950 Kejadian)", lat: -6.2625, lon: 106.8127, incidents: 950, radius: 1400 },
        { name: "Titik Banjir Kampung Melayu (1.800 Kejadian)", lat: -6.2230, lon: 106.8630, incidents: 1800, radius: 1600 }
    ];

    return (
        <main className="p-8 pb-20 overflow-x-hidden flex flex-col h-screen">
            <header className="mb-6 shrink-0 z-10">
                <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center">
                    <CloudLightning className="w-8 h-8 mr-3 text-cyan-400" />
                    Meteorological Radar
                    <span className="ml-4 px-2 py-0.5 text-[10px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/50 rounded-full flex items-center uppercase tracking-widest font-bold">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse mr-1.5"></span>
                        Real-Time Telemetry
                    </span>
                </h1>
                <p className="text-slate-400 mt-2">Pemantauan titik-titik krusial hidrologi secara langsung menggunakan data satelit Open-Meteo.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6 shrink-0 z-10">
                <div className="glass-panel p-4 border-l-2 border-l-cyan-500 flex items-center space-x-4">
                    <Thermometer className="w-8 h-8 text-cyan-400" />
                    <div>
                        <p className="text-[10px] text-slate-400 uppercase tracking-widest font-bold">Rata-Rata Suhu</p>
                        <p className="text-2xl font-black text-white">{realTemp}</p>
                    </div>
                </div>
                <div className="glass-panel p-4 border-l-2 border-l-blue-500 flex items-center space-x-4">
                    <Droplets className="w-8 h-8 text-blue-400" />
                    <div>
                        <p className="text-[10px] text-slate-400 uppercase tracking-widest font-bold">Kelembapan Udara</p>
                        <p className="text-2xl font-black text-white">{realHumid}</p>
                    </div>
                </div>
                <div className="glass-panel p-4 border-l-2 border-l-slate-400 flex items-center space-x-4">
                    <Wind className="w-8 h-8 text-slate-400" />
                    <div>
                        <p className="text-[10px] text-slate-400 uppercase tracking-widest font-bold">Kecepatan Angin</p>
                        <p className="text-2xl font-black text-white">{realWind}</p>
                    </div>
                </div>
                <div className="glass-panel p-4 border-l-2 border-l-rose-500 flex items-center space-x-4">
                    <CloudLightning className={`w-8 h-8 ${katulampaStatus.includes('Aman') ? 'text-emerald-400' : 'text-rose-400 animate-pulse'}`} />
                    <div>
                        <p className={`text-[10px] uppercase tracking-widest font-bold ${katulampaStatus.includes('Aman') ? 'text-emerald-400' : 'text-rose-400'}`}>Status Katulampa</p>
                        <p className={`text-2xl font-black ${katulampaStatus.includes('Aman') ? 'text-emerald-400' : 'text-rose-400'}`}>{katulampaStatus}</p>
                    </div>
                </div>
            </div>

            <div className="flex-1 glass-panel rounded-2xl overflow-hidden border border-slate-700 relative z-10 shadow-2xl">
                {isMounted ? (
                    <div className="relative w-full h-full">
                        {/* Floating Layer Control Panel */}
                        <div className="absolute top-4 right-4 z-[1000] glass-panel p-4 flex flex-col gap-2.5 w-60 border-slate-800/50 shadow-2xl">
                            <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 flex items-center">
                                <Activity className="w-4 h-4 mr-2 text-cyan-400 animate-pulse" />
                                Radar Layer Control
                            </h3>
                            <label className="flex items-center space-x-3 text-xs text-slate-300 cursor-pointer hover:text-slate-100 transition-colors">
                                <input type="checkbox" checked={showRain} onChange={() => setShowRain(!showRain)}
                                    className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-cyan-500 accent-cyan-500 outline-none cursor-pointer" />
                                <span className="font-semibold">Satelit Curah Hujan</span>
                            </label>
                            <label className="flex items-center space-x-3 text-xs text-slate-300 cursor-pointer hover:text-slate-100 transition-colors">
                                <input type="checkbox" checked={showTopography} onChange={() => setShowTopography(!showTopography)}
                                    className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-purple-500 focus:ring-purple-500 accent-purple-500 outline-none cursor-pointer" />
                                <span className="font-semibold">Kerentanan Topografi</span>
                            </label>
                            <label className="flex items-center space-x-3 text-xs text-slate-300 cursor-pointer hover:text-slate-100 transition-colors">
                                <input type="checkbox" checked={showHistorical} onChange={() => setShowHistorical(!showHistorical)}
                                    className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-rose-500 focus:ring-rose-500 accent-rose-500 outline-none cursor-pointer" />
                                <span className="font-semibold">Titik Banjir Historis</span>
                            </label>
                        </div>

                        <MapContainer center={[-6.25, 106.84]} zoom={10} className="h-full w-full" zoomControl={false}>
                            <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />
                            
                            {/* Rainfall Layer */}
                            {showRain && liveNodes.map(node => (
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

                            {/* Topography Layer */}
                            {showTopography && topoNodes.map(node => (
                                <Circle 
                                    key={node.name}
                                    center={[node.lat, node.lon]}
                                    radius={node.radius}
                                    pathOptions={{ color: '#a855f7', fillColor: '#a855f7', fillOpacity: 0.15, weight: 1.5 }}
                                >
                                    <Popup>
                                        <b>{node.name}</b><br/>Elevasi Rendah: {node.elevation}m mdpl<br/>Kerentanan Sangat Tinggi
                                    </Popup>
                                </Circle>
                            ))}

                            {/* Historical Hotspots Layer */}
                            {showHistorical && historicalHotspots.map(node => (
                                <Circle 
                                    key={node.name}
                                    center={[node.lat, node.lon]}
                                    radius={node.radius}
                                    pathOptions={{ color: '#f43f5e', fillColor: '#f43f5e', fillOpacity: 0.2, weight: 2, dashArray: "5, 5" }}
                                >
                                    <Popup>
                                        <b>{node.name}</b><br/>Total Kejadian Historis: {node.incidents} kali
                                    </Popup>
                                </Circle>
                            ))}
                        </MapContainer>
                    </div>
                ) : (
                     <div className="h-full w-full bg-slate-900/50 animate-pulse flex items-center justify-center">Loading Satelit...</div>
                )}
            </div>
        </main>
    );
}
