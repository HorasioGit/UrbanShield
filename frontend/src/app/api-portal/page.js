"use client";

import { Code, Terminal, CheckCircle2, Copy } from 'lucide-react';

export default function ApiPortal() {
    return (
        <main className="p-8 pb-20 overflow-x-hidden">
            <header className="mb-8">
                <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center">
                    <Code className="w-8 h-8 mr-3 text-rose-400" />
                    Developer API Portal
                </h1>
                <p className="text-slate-400 mt-2">Integrasikan *engine* kecerdasan UrbanShield ke dalam sistem TMS pihak ketiga (B2B) secara mulus.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                
                <div className="col-span-1 lg:col-span-4 space-y-6">
                    <div className="glass-panel p-6 border-l-2 border-l-emerald-500">
                        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest mb-2">Endpoint Status</h3>
                        <div className="flex items-center text-emerald-400 text-sm font-medium">
                            <CheckCircle2 className="w-4 h-4 mr-2" />
                            api.urbanshield.com/v2/route is Online
                        </div>
                    </div>
                    
                    <div className="glass-panel p-6">
                        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest mb-4">Authentication</h3>
                        <p className="text-sm text-slate-400 mb-4">Gunakan Bearer Token di header HTTP Anda untuk mengakses layanan prediksi rute.</p>
                        <div className="bg-slate-900 p-3 rounded-lg border border-slate-800 flex justify-between items-center group cursor-pointer hover:border-slate-600 transition-colors">
                            <code className="text-xs text-rose-300">sk_live_9a8b7c6d5e...</code>
                            <Copy className="w-4 h-4 text-slate-500 group-hover:text-slate-300" />
                        </div>
                    </div>
                </div>

                <div className="col-span-1 lg:col-span-8">
                    <div className="glass-panel rounded-xl overflow-hidden shadow-2xl">
                        <div className="bg-slate-900 px-4 py-3 flex items-center border-b border-slate-800">
                            <Terminal className="w-4 h-4 mr-2 text-slate-500" />
                            <span className="text-xs font-mono text-slate-400">cURL Example - Route Optimization</span>
                        </div>
                        <div className="p-6 bg-[#0d1117] overflow-x-auto">
                            <pre className="text-sm font-mono text-slate-300">
<span className="text-rose-400">curl</span> -X POST https://api.urbanshield.com/v2/route \<br/>
  -H <span className="text-emerald-300">"Authorization: Bearer $URBAN_API_KEY"</span> \<br/>
  -H <span className="text-emerald-300">"Content-Type: application/json"</span> \<br/>
  -d '{"{"}'<br/>
    <span className="text-cyan-300">"origin"</span>: <span className="text-amber-300">"Tanjung Priok, Jakarta"</span>,<br/>
    <span className="text-cyan-300">"destination"</span>: <span className="text-amber-300">"Sunter Jaya, Jakarta"</span>,<br/>
    <span className="text-cyan-300">"horizon"</span>: <span className="text-amber-300">"3h"</span>,<br/>
    <span className="text-cyan-300">"cargo_value"</span>: <span className="text-amber-300">25000000</span><br/>
  '{"}"}'
                            </pre>
                        </div>
                        <div className="bg-slate-900 px-6 py-4 border-t border-slate-800">
                            <p className="text-xs text-slate-500 font-mono">Response: 200 OK - Mengembalikan koordinat polyline, risiko finansial, dan rute memutar otomatis jika terdeteksi banjir.</p>
                        </div>
                    </div>
                </div>

            </div>
        </main>
    );
}
