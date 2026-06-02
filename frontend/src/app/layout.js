import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "UrbanShield 2.0 Logistics OS",
  description: "Enterprise Logistics Navigation & AI Flood Prediction",
};

export default function RootLayout({ children }) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex overflow-hidden bg-[#040814]" suppressHydrationWarning>
        <Sidebar />
        <div className="flex-1 flex flex-col h-screen overflow-hidden relative">
            {/* Ambient Animated Background for entire app */}
            <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-cyan-500/20 blur-[150px] pointer-events-none z-0 animate-pulse" style={{ animationDuration: '8s' }}></div>
            <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-emerald-600/10 blur-[150px] pointer-events-none z-0 animate-pulse" style={{ animationDuration: '10s', animationDelay: '1s' }}></div>
            <div className="absolute top-[30%] left-[30%] w-[40%] h-[40%] rounded-full bg-blue-600/10 blur-[140px] pointer-events-none z-0 animate-pulse" style={{ animationDuration: '12s', animationDelay: '2s' }}></div>
            
            <div className="relative z-10 w-full h-full overflow-y-auto custom-scrollbar">
                {children}
            </div>
        </div>
      </body>
    </html>
  );
}
