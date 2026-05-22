"use client";

import { Truck, Activity, ShieldAlert, CheckCircle2 } from 'lucide-react';

const fleets = [
    { id: "B 9012 UXI", origin: "Tanjung Priok", dest: "Sunter Jaya", driver: "Ahmad", status: "REROUTED", risk: "85.2%", eta: "45 Min" },
    { id: "B 1234 KCA", origin: "Blok M", dest: "Kemang", driver: "Budi", status: "SAFE", risk: "12.1%", eta: "15 Min" },
    { id: "D 4567 OPA", origin: "Cawang", dest: "Halim", driver: "Tono", status: "WARNING", risk: "45.0%", eta: "25 Min" },
    { id: "B 8899 ZAS", origin: "Pluit", dest: "PIK", driver: "Rudi", status: "SAFE", risk: "8.4%", eta: "10 Min" },
    { id: "F 1122 BGR", origin: "Ciawi", dest: "Sentul", driver: "Joko", status: "REROUTED", risk: "92.7%", eta: "55 Min" },
];

export default function FleetCommand() {
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
                            {fleets.map(f => (
                                <tr key={f.id} className="hover:bg-slate-800/30 transition-colors">
                                    <td className="px-6 py-5 font-mono text-cyan-300">{f.id}</td>
                                    <td className="px-6 py-5 text-slate-300">{f.driver}</td>
                                    <td className="px-6 py-5 text-slate-300">{f.origin} &rarr; {f.dest}</td>
                                    <td className="px-6 py-5">
                                        <span className={`font-black ${f.status === 'REROUTED' ? 'text-rose-400' : f.status === 'WARNING' ? 'text-amber-400' : 'text-emerald-400'}`}>
                                            {f.risk}
                                        </span>
                                    </td>
                                    <td className="px-6 py-5">
                                        {f.status === 'SAFE' && <span className="inline-flex items-center px-2 py-1 bg-emerald-500/10 text-emerald-400 text-[10px] font-bold rounded border border-emerald-500/20 tracking-wider"><CheckCircle2 className="w-3 h-3 mr-1" /> SAFE</span>}
                                        {f.status === 'WARNING' && <span className="inline-flex items-center px-2 py-1 bg-amber-500/10 text-amber-400 text-[10px] font-bold rounded border border-amber-500/20 tracking-wider"><Activity className="w-3 h-3 mr-1" /> WARNING</span>}
                                        {f.status === 'REROUTED' && <span className="inline-flex items-center px-2 py-1 bg-rose-500/10 text-rose-400 text-[10px] font-bold rounded border border-rose-500/20 tracking-wider"><ShieldAlert className="w-3 h-3 mr-1 animate-pulse" /> REROUTED</span>}
                                    </td>
                                    <td className="px-6 py-5 text-slate-300 font-mono">{f.eta}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    );
}
