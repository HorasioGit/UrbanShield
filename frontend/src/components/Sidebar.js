"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ShieldAlert, Navigation, Truck, CloudLightning, Database, Code, Activity } from 'lucide-react';

export default function Sidebar() {
    const pathname = usePathname();

    const navItems = [
        { name: "Route Simulator", href: "/", icon: Navigation },
        { name: "Meteorology Hub", href: "/meteorology", icon: CloudLightning },
        { name: "Fleet Command", href: "/fleet", icon: Truck },
        { name: "Data Insights", href: "/data", icon: Database },
        { name: "API Portal", href: "/api-portal", icon: Code },
    ];

    return (
        <aside className="w-64 h-screen bg-[#030712] border-r border-slate-800/50 flex flex-col relative z-50 shadow-[5px_0_15px_rgba(0,0,0,0.5)]">
            <div className="p-6 flex items-center space-x-3 border-b border-slate-800/50">
                <div className="p-2 bg-cyan-950/50 rounded-xl border border-cyan-800/50 shadow-[0_0_10px_rgba(34,211,238,0.2)]">
                    <ShieldAlert className="text-cyan-400 w-6 h-6 glow-text-cyan" />
                </div>
                <div>
                    <h1 className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-cyan-300 via-blue-400 to-emerald-400 bg-clip-text text-transparent glow-text-cyan">
                        UrbanShield
                    </h1>
                    <p className="text-slate-500 text-[10px] tracking-widest uppercase font-bold">Logistics OS 2.0</p>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto py-6 px-4 space-y-2">
                <p className="px-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4">Core Modules</p>
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    const Icon = item.icon;
                    return (
                        <Link key={item.name} href={item.href}
                            className={`flex items-center space-x-3 px-3 py-3 rounded-lg transition-all duration-300 ${
                                isActive 
                                ? 'bg-cyan-950/40 text-cyan-300 border border-cyan-800/50 glow-border-cyan shadow-lg' 
                                : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200 border border-transparent'
                            }`}
                        >
                            <Icon className={`w-5 h-5 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                            <span className="text-sm font-semibold">{item.name}</span>
                        </Link>
                    );
                })}
            </div>

            <div className="p-6 border-t border-slate-800/50">
                <div className="glass-panel p-4 rounded-xl text-center">
                    <Activity className="w-6 h-6 text-emerald-400 mx-auto mb-2 animate-pulse" />
                    <p className="text-[10px] font-bold text-slate-300 uppercase tracking-widest">System Status</p>
                    <p className="text-xs text-emerald-400 mt-1 font-mono">SAT-COM: ONLINE</p>
                </div>
            </div>
        </aside>
    );
}
