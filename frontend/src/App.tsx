import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { EnhancePage } from './pages/EnhancePage';
import { BatchPage } from './pages/BatchPage';
import { AboutPage } from './pages/AboutPage';

export function App() {
  const [activeTab, setActiveTab] = useState<'enhance' | 'batch' | 'about'>('enhance');

  return (
    <div className="min-h-screen cyber-bg text-slate-100 flex flex-col font-sans relative overflow-x-hidden">
      {/* Top Ambient Glow Orb */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[240px] bg-gradient-to-b from-amber-500/15 via-cyan-500/5 to-transparent blur-3xl pointer-events-none -z-10" />

      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-12 relative z-10">
        {activeTab === 'enhance' && <EnhancePage />}
        {activeTab === 'batch' && <BatchPage />}
        {activeTab === 'about' && <AboutPage />}
      </main>

      <footer className="border-t border-slate-800/80 bg-slate-950/80 backdrop-blur-md py-4 text-xs text-slate-400 font-mono">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2.5">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 cyber-ping" />
            <span className="font-semibold text-slate-300">InfraClarity Mission Engine v1.0</span>
            <span className="text-slate-600">|</span>
            <span className="text-slate-400">Energy, Grid & Structural Inspection</span>
          </div>
          <div className="flex items-center space-x-3 text-[11px] text-slate-400">
            <span className="px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300">
              ⚡ Multi-Scale Luminance Shock Peaking
            </span>
            <span className="px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-300">
              🤖 Gemini Flash-Lite Copilot
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
