"use client";

import { useState, useEffect } from 'react';
import { Truck, Activity, ShieldAlert, CheckCircle2, Play, RefreshCw } from 'lucide-react';

const initialFleets = [
    { id: "B 9012 UXI", origin: "Tanjung Priok", dest: "Sunter Jaya", driver: "Ahmad", status: "STANDBY", risk: "TBD", eta: "TBD", finalStatus: "REROUTED", finalRisk: "85.2%", finalEta: "45 Min" },
    { id: "B 1234 KCA", origin: "Blok M", dest: "Kemang", driver: "Budi", status: "STANDBY", risk: "TBD", eta: "TBD", finalStatus: "SAFE", finalRisk: "12.1%", finalEta: "15 Min" },
    { id: "D 4567 OPA", origin: "Cawang", dest: "Halim", driver: "Tono", status: "STANDBY", risk: "TBD", eta: "TBD", finalStatus: "WARNING", finalRisk: "45.0%", finalEta: "25 Min" },
    { id: "B 8899 ZAS", origin: "Pluit", dest: "PIK", driver: "Rudi", status: "STANDBY", risk: "TBD", eta: "TBD", finalStatus: "SAFE", finalRisk: "8.4%", finalEta: "10 Min" },
    { id: "F 1122 BGR", origin: "Ciawi", dest: "Sentul", driver: "Joko", status: "STANDBY", risk: "TBD", eta: "TBD", finalStatus: "REROUTED", finalRisk: "92.7%", finalEta: "55 Min" },
];

export default function FleetCommand() {
    const [fleetList, setFleetList] = useState(initialFleets);
    const [isDispatching, setIsDispatching] = useState(false);
    const [activeIndex, setActiveIndex] = useState(-1);
    const [progress, setProgress] = useState(0);

    const handleStartDispatch = () => {
        setIsDispatching(true);
        setActiveIndex(0);
        setProgress(0);
        
        // Reset all to STANDBY
        setFleetList(initialFleets.map(f => ({
            ...f,
            status: "STANDBY",
            risk: "TBD",
            eta: "TBD"
        })));
    };

    useEffect(() => {
        if (!isDispatching || activeIndex < 0 || activeIndex >= fleetList.length) {
            if (activeIndex >= fleetList.length) {
                setIsDispatching(false);
                setActiveIndex(-1);
            }
            return;
        }

        // Simulate 1.5 seconds scan per truck
        const timer = setTimeout(() => {
            setFleetList(prevList => {
                const newList = [...prevList];
                const target = newList[activeIndex];
                newList[activeIndex] = {
                    ...target,
                    status: target.finalStatus,
                    risk: target.finalRisk,
                    eta: target.finalEta
                };
                return newList;
            });
            setProgress(Math.round(((activeIndex + 1) / fleetList.length) * 100));
            setActiveIndex(prev => prev + 1);
        }, 1500);

        return () => clearTimeout(timer);
    }, [isDispatching, activeIndex, fleetList.length]);

    return (
        <main className="p-8 pb-20 overflow-x-hidden relative">
            <header className="mb-8 z-10 relative">
                <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center">
                    <Truck className="w-8 h-8 mr-3 text-emerald-400" />
                    Fleet Command Center
                </h1>
                <p className="text-slate-400 mt-2">Pemantauan massal probabilitas risiko logistik untuk seluruh armada aktif secara simultan.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8 z-10 relative">
                <div className="glass-panel p-5 text-center">
                    <p className="text-xs text-slate-400 uppercase font-bold tracking-widest mb-2">Total Active Fleet</p>
                    <p className="text-4xl font-black text-cyan-400 glow-text-cyan">245</p>
                </div>
                <div className="glass-panel p-5 text-center border-b-2 border-emerald-500">
                    <p className="text-xs text-slate-400 uppercase font-bold tracking-widest mb-2">Safe Route</p>
                    <p className="text-4xl font-black text-emerald-400">212</p>
                </div>
                <div className="glass-panel p-5 text-center border-b-2 border-amber-500">
                    <p className="text-xs text-slate-400 uppercase font-bold tracking-widest mb-2">Warning Level</p>
                    <p className="text-4xl font-black text-amber-400">21</p>
                </div>
                <div className="glass-panel p-5 text-center border-b-2 border-rose-500 glow-border-rose">
                    <p className="text-xs text-slate-400 uppercase font-bold tracking-widest mb-2">Auto-Rerouted</p>
                    <p className="text-4xl font-black text-rose-400 animate-pulse">12</p>
                </div>
            </div>

            <div className="glass-panel rounded-xl overflow-hidden z-10 relative shadow-2xl">
                <div className="px-6 py-4 border-b border-slate-800 bg-slate-900/50 flex justify-between items-center">
                    <h2 className="text-sm font-bold text-slate-300 uppercase tracking-widest">Live Convoy Status</h2>
                    <span className="flex h-3 w-3 relative">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                    </span>
                </div>

                {/* Dispatch Simulation Panel */}
                <div className="p-4 bg-slate-900/60 border-b border-slate-800/80 flex flex-col md:flex-row justify-between items-center gap-4">
                    <div className="flex items-center space-x-4 w-full md:w-auto">
                        <button suppressHydrationWarning onClick={handleStartDispatch} disabled={isDispatching}
                            className="px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:opacity-50 text-white rounded-lg font-bold text-xs tracking-wider uppercase shadow-[0_0_15px_rgba(16,185,129,0.3)] transition-all flex items-center shrink-0">
                            {isDispatching ? (
                                <><RefreshCw className="w-3.5 h-3.5 mr-2 animate-spin" /> Uplinking satelit...</>
                            ) : (
                                <><Play className="w-3.5 h-3.5 mr-2" /> Mulai Dispatch Konvoi</>
                            )}
                        </button>
                        {isDispatching && (
                            <div className="text-xs text-slate-400 font-mono">
                                Memindai Armada: <span className="text-emerald-400 font-bold">{activeIndex + 1}</span> / {fleetList.length}
                            </div>
                        )}
                    </div>
                    
                    {isDispatching && (
                        <div className="w-full md:w-64 bg-slate-950 border border-slate-800 rounded-full h-3 overflow-hidden p-0.5 shadow-inner">
                            <div className="bg-gradient-to-r from-emerald-500 to-cyan-500 h-full rounded-full transition-all duration-500" style={{ width: `${progress}%` }}></div>
                        </div>
                    )}
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm text-slate-400">
                        <thead className="text-xs uppercase bg-[#0d1117] text-slate-500 border-b border-slate-800">
                            <tr>
                                <th className="px-6 py-4 font-bold tracking-wider">No. Polisi</th>
                                <th className="px-6 py-4 font-bold tracking-wider">Supir</th>
                                <th className="px-6 py-4 font-bold tracking-wider">Destinasi</th>
                                <th className="px-6 py-4 font-bold tracking-wider">AI Flood Risk</th>
                                <th className="px-6 py-4 font-bold tracking-wider">Status Mitigasi</th>
                                <th className="px-6 py-4 font-bold tracking-wider">ETA</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/50">
                            {fleetList.map((f, idx) => {
                                const isScanning = isDispatching && activeIndex === idx;
                                return (
                                    <tr key={f.id} className={`hover:bg-slate-800/30 transition-colors ${f.status === 'STANDBY' && !isScanning ? 'opacity-55' : 'opacity-100'} ${isScanning ? 'bg-cyan-950/20 border-l-2 border-l-cyan-500' : ''}`}>
                                        <td className="px-6 py-5 font-mono text-cyan-300">{f.id}</td>
                                        <td className="px-6 py-5 text-slate-300">{f.driver}</td>
                                        <td className="px-6 py-5 text-slate-300">{f.origin} &rarr; {f.dest}</td>
                                        <td className="px-6 py-5">
                                            <span className={`font-black ${isScanning ? 'text-cyan-400 animate-pulse' : f.status === 'REROUTED' ? 'text-rose-400' : f.status === 'WARNING' ? 'text-amber-400' : f.status === 'SAFE' ? 'text-emerald-400' : 'text-slate-600'}`}>
                                                {isScanning ? "SCANNING..." : f.risk}
                                            </span>
                                        </td>
                                        <td className="px-6 py-5">
                                            {isScanning ? (
                                                <span className="inline-flex items-center px-2 py-1 bg-cyan-500/10 text-cyan-400 text-[10px] font-bold rounded border border-cyan-500/25 tracking-wider"><RefreshCw className="w-3 h-3 mr-1 animate-spin" /> SCANNING</span>
                                            ) : (
                                                <>
                                                    {f.status === 'STANDBY' && <span className="inline-flex items-center px-2 py-1 bg-slate-800/80 text-slate-500 text-[10px] font-bold rounded border border-slate-700/50 tracking-wider">STANDBY</span>}
                                                    {f.status === 'SAFE' && <span className="inline-flex items-center px-2 py-1 bg-emerald-500/10 text-emerald-400 text-[10px] font-bold rounded border border-emerald-500/20 tracking-wider"><CheckCircle2 className="w-3 h-3 mr-1" /> SAFE</span>}
                                                    {f.status === 'WARNING' && <span className="inline-flex items-center px-2 py-1 bg-amber-500/10 text-amber-400 text-[10px] font-bold rounded border border-amber-500/20 tracking-wider"><Activity className="w-3 h-3 mr-1" /> WARNING</span>}
                                                    {f.status === 'REROUTED' && <span className="inline-flex items-center px-2 py-1 bg-rose-500/10 text-rose-400 text-[10px] font-bold rounded border border-rose-500/20 tracking-wider"><ShieldAlert className="w-3 h-3 mr-1 animate-pulse" /> REROUTED</span>}
                                                </>
                                            )}
                                        </td>
                                        <td className="px-6 py-5 text-slate-300 font-mono">
                                            {isScanning ? "CALCULATING..." : f.eta}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    );
}
