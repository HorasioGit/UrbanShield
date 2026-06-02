import re

with open('frontend/src/app/page.js', 'r', encoding='utf-8') as f:
    content = f.read()

# We want to replace everything from "TOP ROW: Mission Params" (line 236ish) to just before "Persistent History Log" (line 443ish)

start_marker = "{/* TOP ROW: Mission Params & XGBoost Matrix */}"
end_marker = "{/* Persistent History Log */}"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_section = """{/* TOP ROW: Financial Impact & Gen-AI Advisory */}
                <div className="flex flex-col xl:flex-row gap-6 shrink-0">
                    {/* Financial Impact Analysis (TOP ROW VERSION) */}
                    <div className="flex-1 glass-panel glass-accent p-6 flex flex-col justify-center relative overflow-hidden shadow-[0_10px_30px_rgba(0,0,0,0.4)]">
                        <h2 className="text-xs font-bold flex items-center text-cyan-300 uppercase tracking-widest z-10 mb-5">
                            <DollarSign className="w-4 h-4 mr-2" />
                            Financial Impact Analysis
                        </h2>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 z-10 relative">
                            {/* Card 1: Risk */}
                            <div className="bg-gradient-to-br from-rose-950/40 to-slate-900/60 p-5 rounded-xl border border-rose-900/50 flex flex-col justify-center shadow-inner relative overflow-hidden group hover:border-rose-500/50 transition-colors duration-300">
                                <div className="absolute -right-4 -top-4 w-20 h-20 bg-rose-500/20 rounded-full blur-2xl pointer-events-none group-hover:bg-rose-500/30 transition-all"></div>
                                <span className="text-[11px] text-rose-300/70 uppercase tracking-widest font-bold block mb-1">Risk Exposure</span>
                                <span className="font-mono text-rose-400 font-bold text-2xl drop-shadow-[0_0_12px_rgba(244,63,94,0.6)]">Rp {advisor?.financials?.potential_loss?.toLocaleString('id-ID') || '0'}</span>
                            </div>
                            {/* Card 2: Detour */}
                            <div className="bg-gradient-to-br from-amber-950/40 to-slate-900/60 p-5 rounded-xl border border-amber-900/50 flex flex-col justify-center shadow-inner relative overflow-hidden group hover:border-amber-500/50 transition-colors duration-300">
                                <div className="absolute -right-4 -top-4 w-20 h-20 bg-amber-500/20 rounded-full blur-2xl pointer-events-none group-hover:bg-amber-500/30 transition-all"></div>
                                <span className="text-[11px] text-amber-300/70 uppercase tracking-widest font-bold block mb-1">Detour Cost</span>
                                <span className="font-mono text-amber-300 font-bold text-2xl drop-shadow-[0_0_12px_rgba(245,158,11,0.6)]">Rp {advisor?.financials?.detour_cost?.toLocaleString('id-ID') || '0'}</span>
                            </div>
                            {/* Card 3: Net Savings */}
                            <div className="bg-gradient-to-br from-emerald-900/40 to-emerald-950/60 p-6 rounded-xl border border-emerald-500/50 glow-border-emerald flex flex-col justify-center shadow-[0_0_30px_rgba(16,185,129,0.2)] relative overflow-hidden group">
                                <div className="absolute -right-6 -bottom-6 w-32 h-32 bg-emerald-500/30 rounded-full blur-3xl pointer-events-none"></div>
                                <span className="text-xs font-bold text-emerald-300 uppercase tracking-widest block mb-1">Net Savings</span>
                                <span className="font-mono font-black text-emerald-400 text-3xl drop-shadow-[0_0_15px_rgba(16,185,129,1)]">Rp {advisor?.financials?.net_savings?.toLocaleString('id-ID') || '0'}</span>
                            </div>
                        </div>
                    </div>

                    {/* Gen-AI Advisory (TOP ROW VERSION) */}
                    <div className="w-full xl:w-[450px] glass-panel p-6 flex flex-col relative overflow-hidden shrink-0 shadow-[0_10px_30px_rgba(0,0,0,0.4)]">
                        <div className="absolute -right-4 -bottom-4 text-slate-800/30 pointer-events-none">
                            <ShieldAlert className="w-32 h-32" />
                        </div>
                        
                        <h2 className="text-xs font-bold flex items-center text-slate-400 uppercase tracking-widest z-10 mb-4">
                            Gen-AI Advisory
                        </h2>
                        
                        <div className={`p-6 rounded-xl flex-1 flex items-center justify-center text-[13px] leading-relaxed border relative z-10 shadow-2xl font-bold transition-all-slow tracking-wide ${
                            advisor?.action === 'REROUTE' ? 'bg-rose-950/60 border-rose-500/80 text-rose-200 shadow-[inset_0_0_30px_rgba(244,63,94,0.2)]' : 
                            advisor?.action === 'PROCEED_WITH_CAUTION' ? 'bg-amber-950/60 border-amber-500/80 text-amber-200 shadow-[inset_0_0_30px_rgba(245,158,11,0.2)]' :
                            advisor?.action === 'PROCEED' ? 'bg-emerald-950/60 border-emerald-500/80 text-emerald-200 shadow-[inset_0_0_30px_rgba(16,185,129,0.2)]' :
                            'bg-slate-900/60 border-slate-700/80 text-slate-400 text-center shadow-[inset_0_0_20px_rgba(0,0,0,0.5)]'
                        }`}>
                            {isLoading ? (
                                <div className="flex flex-col items-center space-y-3 text-cyan-400 animate-pulse">
                                    <Activity className="w-8 h-8 animate-spin" />
                                    <span className="text-xs uppercase tracking-widest font-bold">Menghitung matriks...</span>
                                </div>
                            ) : (
                                <div className="flex items-start text-left">
                                    {advisor?.action && <Activity className={`w-5 h-5 mr-3 shrink-0 ${advisor?.action === 'REROUTE' ? 'text-rose-400' : advisor?.action === 'PROCEED' ? 'text-emerald-400' : 'text-amber-400'}`} />}
                                    <span>{advisor?.text || "SISTEM STANDBY. Masukkan parameter dan pindai satelit untuk instruksi manuver."}</span>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* BOTTOM ROW: Map & Sidebar */}
                <div className="flex-1 flex flex-col xl:flex-row gap-6 pb-4">
                    {/* MAIN AREA: Dynamic Map */}
                    <div className="flex-grow xl:w-2/3 relative rounded-2xl overflow-hidden border border-cyan-900/50 shadow-[0_0_40px_rgba(8,145,178,0.15)] flex flex-col bg-slate-900/50 group min-h-[500px] xl:min-h-[700px] backdrop-blur-sm">
                        <div className="flex-1 relative h-full">
                            
                            {/* Error Overlay in the middle of Map */}
                            {errorMsg && (
                                <div className="absolute inset-0 z-[2000] flex items-center justify-center bg-slate-900/80 backdrop-blur-md rounded-2xl">
                                    <div className="bg-rose-950/80 border border-rose-500 p-8 rounded-2xl max-w-md text-center shadow-[0_0_60px_rgba(244,63,94,0.3)]">
                                        <ShieldAlert className="w-16 h-16 text-rose-500 mx-auto mb-4 animate-pulse" />
                                        <p className="text-rose-200 text-sm font-mono leading-relaxed">{errorMsg}</p>
                                    </div>
                                </div>
                            )}

                            {routeData && (
                                <div className="absolute top-5 left-5 z-10 glass-panel px-5 py-3 flex items-center space-x-6 border-slate-600/50 shadow-2xl backdrop-blur-xl">
                                    <div>
                                        <p className="text-[9px] text-slate-400 uppercase font-bold tracking-widest mb-1">Estimasi Tiba (ETA)</p>
                                        <p className="text-2xl font-black text-white">{routeData.eta_mins} <span className="text-sm font-medium text-slate-400">Min</span></p>
                                    </div>
                                    <div className="h-10 w-px bg-slate-700"></div>
                                    <div>
                                        <p className="text-[9px] text-slate-400 uppercase font-bold tracking-widest mb-1">Jarak Tempuh</p>
                                        <p className="text-2xl font-black text-cyan-400 glow-text-cyan">{routeData.dist_km.toFixed(1)} <span className="text-sm font-medium text-cyan-700">KM</span></p>
                                    </div>
                                </div>
                            )}
                            <DynamicMap routeData={routeData} />
                            
                            <div className="absolute inset-0 pointer-events-none border-[2px] border-cyan-500/20 rounded-2xl z-20 transition-all duration-700 group-hover:border-cyan-400/40 group-hover:shadow-[inset_0_0_20px_rgba(34,211,238,0.2)]"></div>
                            
                            {/* HUD Corners */}
                            <div className="absolute top-4 left-4 w-8 h-8 border-t-2 border-l-2 border-cyan-500/60 pointer-events-none z-30 opacity-50 group-hover:opacity-100 transition-opacity"></div>
                            <div className="absolute top-4 right-4 w-8 h-8 border-t-2 border-r-2 border-cyan-500/60 pointer-events-none z-30 opacity-50 group-hover:opacity-100 transition-opacity"></div>
                            <div className="absolute bottom-4 left-4 w-8 h-8 border-b-2 border-l-2 border-cyan-500/60 pointer-events-none z-30 opacity-50 group-hover:opacity-100 transition-opacity"></div>
                            <div className="absolute bottom-4 right-4 w-8 h-8 border-b-2 border-r-2 border-cyan-500/60 pointer-events-none z-30 opacity-50 group-hover:opacity-100 transition-opacity"></div>

                            <div className="absolute bottom-6 right-8 pointer-events-none z-20">
                                <div className="text-[10px] font-mono text-cyan-500/50 bg-slate-900/50 px-2 py-1 rounded">SAT-COM: CONNECTED</div>
                            </div>
                        </div>
                    </div>

                    {/* SIDEBAR: Mission Parameters & Matrix */}
                    <div className="xl:w-1/3 w-full flex flex-col space-y-6 h-full">
                        
                        {/* Mission Parameters (SIDEBAR VERSION) */}
                        <div className="glass-panel p-6 border-t-2 border-t-cyan-500/50 flex flex-col shadow-[0_10px_30px_rgba(0,0,0,0.4)] relative shrink-0">
                            <h2 className="text-base font-bold mb-6 flex items-center text-cyan-300 uppercase tracking-widest text-xs">
                                <Navigation className="w-4 h-4 mr-2" />
                                Mission Parameters
                            </h2>
                            
                            <div className="flex flex-col gap-5">
                                <div>
                                    <label className="text-[10px] text-cyan-500/80 mb-2 block font-bold uppercase tracking-widest">Lokasi Keberangkatan</label>
                                    <div className="relative group">
                                        <MapPin className="w-4 h-4 absolute left-3 top-4 text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
                                        <input suppressHydrationWarning type="text" value={origin} onChange={e => setOrigin(e.target.value)}
                                            className="w-full h-12 bg-slate-900/80 border border-slate-700/50 rounded-lg pl-10 pr-3 text-sm focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 outline-none transition-all shadow-inner text-slate-200" />
                                    </div>
                                </div>
                                <div>
                                    <label className="text-[10px] text-cyan-500/80 mb-2 block font-bold uppercase tracking-widest">Tujuan Pengiriman</label>
                                    <div className="relative group">
                                        <MapPin className="w-4 h-4 absolute left-3 top-4 text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
                                        <input suppressHydrationWarning type="text" value={destination} onChange={e => setDestination(e.target.value)}
                                            className="w-full h-12 bg-slate-900/80 border border-slate-700/50 rounded-lg pl-10 pr-3 text-sm focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 outline-none transition-all shadow-inner text-slate-200" />
                                    </div>
                                </div>
                                
                                <div className="grid grid-cols-2 gap-4 mt-2">
                                    <div>
                                        <label className="text-[10px] text-cyan-500/80 mb-2 block font-bold uppercase tracking-widest">Horizon</label>
                                        <select suppressHydrationWarning value={horizon} onChange={e => setHorizon(e.target.value)}
                                            className="w-full h-12 bg-slate-900/80 border border-slate-700/50 rounded-lg px-3 text-sm focus:border-cyan-500 outline-none appearance-none shadow-inner text-slate-200 cursor-pointer">
                                            <option value="0h">Nowcast</option>
                                            <option value="3h">+3 Jam</option>
                                            <option value="6h">+6 Jam</option>
                                            <option value="12h">+12 Jam</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="text-[10px] text-cyan-500/80 mb-2 block font-bold uppercase tracking-widest text-center">Data Source</label>
                                        <div className="flex h-12 bg-slate-900/80 rounded-lg p-1 border border-slate-700/50 shadow-inner">
                                            <button suppressHydrationWarning onClick={() => setIsLiveMode(true)} className={`flex-1 text-[11px] rounded transition-all duration-300 ${isLiveMode ? 'bg-cyan-500 text-slate-900 font-extrabold shadow-[0_0_10px_rgba(6,182,212,0.8)]' : 'text-slate-500 hover:text-cyan-400'}`}>LIVE</button>
                                            <button suppressHydrationWarning onClick={() => setIsLiveMode(false)} className={`flex-1 text-[11px] rounded transition-all duration-300 ${!isLiveMode ? 'bg-amber-500 text-slate-900 font-extrabold shadow-[0_0_10px_rgba(245,158,11,0.8)]' : 'text-slate-500 hover:text-amber-400'}`}>SIM</button>
                                        </div>
                                    </div>
                                </div>

                                <div className="mt-2">
                                    {!isLiveMode ? (
                                        <div className="flex flex-col justify-end pb-2">
                                            <label className="flex justify-between text-[10px] text-cyan-500/80 mb-2 uppercase font-bold tracking-widest">
                                                <span className="flex items-center text-amber-400"><CloudRain className="w-3 h-3 mr-1"/> Hujan Extremity</span>
                                                <span className="font-mono bg-slate-950/80 px-2 py-0.5 rounded border border-amber-900/50 text-amber-400 shadow-inner">{rainIntensity} mm</span>
                                            </label>
                                            <input suppressHydrationWarning 
                                                type="range" min="0" max="50" step="1" value={rainIntensity} onChange={(e) => setRainIntensity(e.target.value)}
                                                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none accent-amber-500 cursor-pointer shadow-inner"
                                            />
                                        </div>
                                    ) : (
                                        <div className="flex items-center justify-center h-12 bg-cyan-950/20 rounded-lg border border-cyan-800/40 shadow-[inset_0_0_15px_rgba(34,211,238,0.1)]">
                                            <span className="text-[11px] text-cyan-300 font-mono flex items-center tracking-widest uppercase font-bold">
                                                <span className="relative flex h-2 w-2 mr-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span><span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span></span>
                                                Open-Meteo Active
                                            </span>
                                        </div>
                                    )}
                                </div>
                                
                                <button suppressHydrationWarning onClick={handleScanRoute} disabled={isLoading}
                                    className="w-full h-14 mt-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-lg font-bold tracking-wider uppercase text-sm shadow-[0_0_20px_rgba(6,182,212,0.4)] hover:shadow-[0_0_30px_rgba(6,182,212,0.7)] transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 flex justify-center items-center">
                                    {isLoading ? <><Activity className="w-5 h-5 mr-2 animate-spin" /> Uplinking...</> : <><Zap className="w-5 h-5 mr-2" /> Pindai Rute & Risiko</>}
                                </button>
                            </div>
                        </div>

                        {/* Forecast Horizon Cards (SIDEBAR VERSION) */}
                        <div className="glass-panel p-6 flex flex-col justify-center shadow-[0_10px_30px_rgba(0,0,0,0.4)] shrink-0">
                            <h2 className="text-xs font-bold mb-4 flex items-center text-slate-400 uppercase tracking-widest">
                                <Clock className="w-4 h-4 mr-2" />
                                Probability Matrix
                            </h2>
                            
                            <div className="grid grid-cols-2 gap-3 h-full">
                                {['0h', '3h', '6h', '12h'].map(h => (
                                    <div key={h} className={`border rounded-xl p-3 flex flex-col justify-center items-center transition-all-slow ${horizon === h ? 'glow-border-cyan bg-cyan-950/20 shadow-[inset_0_0_15px_rgba(34,211,238,0.2)]' : ''} ${horizon !== h ? getDangerBg(predictions[h] || 0) : ''}`}>
                                        <span className="text-slate-500 text-[10px] font-bold uppercase mb-1 tracking-widest">{h === '0h' ? 'Nowcast' : `+${h} Forecast`}</span>
                                        <span className={`text-2xl font-black tracking-tighter ${getDangerColor(predictions[h] || 0)}`}>
                                            {((predictions[h] || 0) * 100).toFixed(0)}%
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        """

    updated_content = content[:start_idx] + new_section + content[end_idx:]
    
    with open('frontend/src/app/page.js', 'w', encoding='utf-8') as fw:
        fw.write(updated_content)
    print("Successfully replaced layout structure.")
else:
    print("Could not find markers.")
    print("Start Marker:", start_idx)
    print("End Marker:", end_idx)
