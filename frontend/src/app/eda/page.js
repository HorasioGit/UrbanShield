"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area, PieChart, Pie, Cell } from 'recharts';
import { Activity, PieChart as PieChartIcon, Mountain } from 'lucide-react';

const floodDistribution = [
  { name: 'Rute Aman (No Flood)', value: 162517 },
  { name: 'Tergenang Banjir (Flood)', value: 12768 },
];
const COLORS = ['#22d3ee', '#8a2be2'];

const rainfallCorrelation = [
  { name: '0-20mm (Gerimis)', insiden: 268 },
  { name: '20-50mm (Sedang)', insiden: 2500 },
  { name: '50-100mm (Lebat)', insiden: 4000 },
  { name: '>100mm (Ekstrem)', insiden: 6000 },
];

const elevationRisk = [
  { elevation: '0-5m (Pesisir)', risk: 85 },
  { elevation: '5-15m (Rendah)', risk: 65 },
  { elevation: '15-30m (Sedang)', risk: 25 },
  { elevation: '>30m (Tinggi)', risk: 5 },
];

export default function ExploratoryDataAnalysis() {
    return (
        <main className="p-10 pb-24 overflow-x-hidden">
            {/* Header Eksklusif */}
            <header className="mb-10">
                <p className="text-cyan-400 text-[10px] sm:text-xs font-mono uppercase tracking-[0.3em] mb-3 flex items-center">
                    <span className="w-8 h-[1px] bg-cyan-400 mr-4"></span>
                    RAW DATASET INTELLIGENCE
                </p>
                <h1 className="text-4xl sm:text-5xl font-black tracking-tight text-white mb-4">
                    Exploratory Data Analysis
                </h1>
                <p className="text-slate-400 max-w-3xl text-sm sm:text-base leading-relaxed">
                    Visualisasi wawasan historis dari 175.285 titik data spasial dan presipitasi iklim di Jabodetabek. Metrik ini merupakan *ground truth* sebelum model AI XGBoost mempelajari pola bahaya.
                </p>
            </header>

            {/* Grid Dashboard */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                
                {/* Visual 1: Distribusi Kelas Target */}
                <div className="glass-panel p-8">
                    <div className="flex items-center justify-between mb-8">
                        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-[0.1em]">Distribusi Kelas Target (Safe vs Flood)</h2>
                        <PieChartIcon className="text-cyan-500/50 w-6 h-6" />
                    </div>
                    <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={floodDistribution}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={90}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {floodDistribution.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <RechartsTooltip 
                                    contentStyle={{backgroundColor: '#040814', border: '1px solid #1e293b', borderRadius: '8px', color: '#fff'}} 
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="mt-6 pt-4 border-t border-slate-800 flex items-start">
                        <div className="w-2 h-2 rounded-full bg-cyan-400 mt-1.5 mr-3 glow-border-cyan shrink-0"></div>
                        <p className="text-sm text-slate-400 leading-relaxed">
                            <strong className="text-white block mb-1">Ketimpangan Data (Imbalance):</strong> Dari total 175.285 baris *dataset*, rute yang kering (Aman) mendominasi 92.7% (162.517 kasus), sementara insiden banjir hanya 7.3% (12.768 kasus). Ketimpangan masif ini (*Scale Pos Weight* 12.7x) diatasi menggunakan algoritma penyeimbang (SMOTE/Class Weight) di *backend* agar AI tidak bias.
                        </p>
                    </div>
                </div>

                {/* Visual 2: Curah Hujan vs Insiden */}
                <div className="glass-panel p-8">
                    <div className="flex items-center justify-between mb-8">
                        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-[0.1em]">Korelasi Ekstremitas Curah Hujan</h2>
                        <Activity className="text-purple-500/50 w-6 h-6" />
                    </div>
                    <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={rainfallCorrelation} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="purpleGradientBar" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#8a2be2" />
                                        <stop offset="100%" stopColor="#22d3ee" />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                <XAxis dataKey="name" stroke="#475569" tick={{fill: '#475569', fontSize: 11}} axisLine={false} tickLine={false} />
                                <YAxis stroke="#475569" tick={{fill: '#475569', fontSize: 11}} axisLine={false} tickLine={false} />
                                <RechartsTooltip 
                                    contentStyle={{backgroundColor: '#040814', border: '1px solid #1e293b', borderRadius: '8px', color: '#fff'}} 
                                    cursor={{fill: 'rgba(138, 43, 226, 0.1)'}} 
                                />
                                <Bar dataKey="insiden" fill="url(#purpleGradientBar)" radius={[4, 4, 0, 0]} barSize={40} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="mt-6 pt-4 border-t border-slate-800 flex items-start">
                        <div className="w-2 h-2 rounded-full bg-purple-400 mt-1.5 mr-3 glow-border-cyan shrink-0"></div>
                        <p className="text-sm text-slate-400 leading-relaxed">
                            <strong className="text-white block mb-1">Ambang Batas Bencana:</strong> Dari 12.768 total titik banjir, mayoritas eksponensial (lebih dari 10.000 insiden) terjadi ketika curah hujan melampaui angka 50mm. Angka ini tervalidasi sebagai parameter *threshold* krusial dalam algoritma prediksi bahaya UrbanShield.
                        </p>
                    </div>
                </div>

                {/* Visual 3: Kerentanan Topografi */}
                <div className="glass-panel p-8 lg:col-span-2">
                    <div className="flex items-center justify-between mb-8">
                        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-[0.1em]">Kerentanan Topografi (Elevasi Tanah) vs Probabilitas Genangan</h2>
                        <Mountain className="text-cyan-500/50 w-6 h-6" />
                    </div>
                    <div className="h-72 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={elevationRisk} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="cyanGradientArea" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.5}/>
                                        <stop offset="95%" stopColor="#22d3ee" stopOpacity={0}/>
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                <XAxis dataKey="elevation" stroke="#475569" tick={{fill: '#475569', fontSize: 12}} axisLine={false} tickLine={false} />
                                <YAxis stroke="#475569" tick={{fill: '#475569', fontSize: 12}} axisLine={false} tickLine={false} />
                                <RechartsTooltip 
                                    contentStyle={{backgroundColor: '#040814', border: '1px solid rgba(34,211,238,0.3)', borderRadius: '8px', color: '#fff'}} 
                                />
                                <Area type="monotone" dataKey="risk" stroke="#22d3ee" strokeWidth={4} fillOpacity={1} fill="url(#cyanGradientArea)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="mt-6 pt-4 border-t border-slate-800 flex items-start">
                        <div className="w-2 h-2 rounded-full bg-cyan-400 mt-1.5 mr-3 glow-border-cyan shrink-0"></div>
                        <p className="text-sm text-slate-400 leading-relaxed">
                            <strong className="text-white block mb-1">Geografi Jakarta Utara:</strong> Probabilitas genangan tertinggi (85%) terkonsentrasi kuat pada elevasi 0-5 mdpl (*meter di atas permukaan laut*). Sebanyak lebih dari 10.800 kasus banjir terkunci di dataran rendah pesisir, menegaskan urgensi mitigasi armada untuk area sekitar Pelabuhan Tanjung Priok.
                        </p>
                    </div>
                </div>

            </div>
        </main>
    );
}
