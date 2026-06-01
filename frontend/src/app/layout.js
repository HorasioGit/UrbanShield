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
             {/* Ambient Background for entire app */}
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-cyan-600/10 blur-[120px] pointer-events-none z-0"></div>
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-fuchsia-700/10 blur-[120px] pointer-events-none z-0"></div>
            <div className="absolute top-[40%] left-[30%] w-[20%] h-[20%] rounded-full bg-blue-700/5 blur-[100px] pointer-events-none z-0"></div>
            
            <div className="relative z-10 w-full h-full overflow-y-auto custom-scrollbar">
                {children}
            </div>
        </div>
      </body>
    </html>
  );
}
