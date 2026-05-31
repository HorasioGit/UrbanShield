"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Database, TrendingUp, Activity, Crosshair } from 'lucide-react';

const featureImportance = [
  { name: 'curah_hujan', weight: 85 },
  { name: 'elevasi_tanah', weight: 65 },
  { name: 'jarak_sungai', weight: 58 },
  { name: 'hujan_lag_3h', weight: 45 },
  { name: 'soil_moisture', weight: 32 },
];

const historicalAccuracy = [
  { month: 'Jan', auc: 0.91, f1: 0.85 },
  { month: 'Feb', auc: 0.94, f1: 0.88 },
  { month: 'Mar', auc: 0.92, f1: 0.86 },
  { month: 'Apr', auc: 0.95, f1: 0.90 },
  { month: 'May', auc: 0.98, f1: 0.94 },
];

export default function DataInsights() {
    return (
        <main className="p-8 pb-20 overflow-x-hidden">
            <header className="mb-8">
                <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center">
                    <Database className="w-8 h-8 mr-3 text-cyan-400" />
                    Data Science & Insights
                </h1>
                <p className="text-slate-400 mt-2">Transparansi model AI XGBoost dan analitik historis performa UrbanShield.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                <div className="glass-panel p-6 border-t-2 border-t-emerald-500/50 flex items-center justify-between">
                    <div>
                        <p className="text-xs text-slate-400 uppercase tracking-widest font-bold mb-1">XGBoost ROC-AUC</p>
                        <p className="text-3xl font-black text-white">0.984 <span className="text-sm text-emerald-400">Excellent</span></p>
                    </div>
                    <Crosshair className="w-10 h-10 text-emerald-500/20" />
                </div>
                <div className="glass-panel p-6 border-t-2 border-t-cyan-500/50 flex items-center justify-between">
                    <div>
                        <p className="text-xs text-slate-400 uppercase tracking-widest font-bold mb-1">F1-Score (Banjir)</p>
                        <p className="text-3xl font-black text-white">0.941 <span className="text-sm text-cyan-400">High Recall</span></p>
                    </div>
                    <TrendingUp className="w-10 h-10 text-cyan-500/20" />
                </div>
                <div className="glass-panel p-6 border-t-2 border-t-amber-500/50 flex items-center justify-between">
                    <div>
                        <p className="text-xs text-slate-400 uppercase tracking-widest font-bold mb-1">Latency Inferensi</p>
                        <p className="text-3xl font-black text-white">12 <span className="text-sm text-amber-400">Milidetik</span></p>
                    </div>
                    <Activity className="w-10 h-10 text-amber-500/20" />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="glass-panel p-6">
                    <h2 className="text-sm font-bold text-slate-300 uppercase tracking-widest mb-6">Top 5 Feature Importance (SHAP Values)</h2>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={featureImportance} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                <XAxis type="number" stroke="#64748b" />
                                <YAxis dataKey="name" type="category" stroke="#64748b" width={100} tick={{fontSize: 12}} />
                                <RechartsTooltip contentStyle={{backgroundColor: '#0f172a', borderColor: '#1e293b'}} cursor={{fill: '#1e293b'}} />
                                <Bar dataKey="weight" fill="#0ea5e9" radius={[0, 4, 4, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="mt-4 text-xs text-slate-400 bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                        <strong>Interpretasi AI:</strong> Grafik SHAP (*Shapley Additive exPlanations*) membuktikan bahwa <span className="text-cyan-400">Curah Hujan</span> dan <span className="text-cyan-400">Elevasi Tanah</span> adalah dua pemicu utama genangan. Ini memvalidasi kerentanan topografi Jakarta yang secara geografis berada di bawah permukaan laut.
                    </div>
                </div>

                <div className="glass-panel p-6">
                    <h2 className="text-sm font-bold text-slate-300 uppercase tracking-widest mb-6">Historical Accuracy (2024 YTD)</h2>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={historicalAccuracy} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                                <defs>
                                    <linearGradient id="colorAuc" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                <XAxis dataKey="month" stroke="#64748b" />
                                <YAxis stroke="#64748b" domain={[0.8, 1]} />
                                <RechartsTooltip contentStyle={{backgroundColor: '#0f172a', borderColor: '#1e293b'}} />
                                <Area type="monotone" dataKey="auc" stroke="#10b981" fillOpacity={1} fill="url(#colorAuc)" strokeWidth={3} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="mt-4 text-xs text-slate-400 bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                        <strong>Performa Pembelajaran:</strong> Skor Akurasi (AUC) model terus meroket dari Januari hingga Mei 2024, mencapai puncaknya di angka <strong>0.98</strong>. Ini menandakan mesin XGBoost kita semakin cerdas mengenali pola cuaca ekstrem seiring bertambahnya pasokan data historis.
                    </div>
                </div>
            </div>
        </main>
    );
}
