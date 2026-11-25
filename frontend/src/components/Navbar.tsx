import React, { useEffect, useState } from 'react';
import { Activity, Layers, Info, Moon, Sun, Cpu, Sparkles, ShieldCheck } from 'lucide-react';
import { useThemeStore } from '../store/useThemeStore';
import { fetchCapabilities } from '../api/client';
import { Capabilities } from '../types';

interface NavbarProps {
  activeTab: 'enhance' | 'batch' | 'about';
  setActiveTab: (tab: 'enhance' | 'batch' | 'about') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const { effectiveTheme, setMode } = useThemeStore();
  const [capabilities, setCapabilities] = useState<Capabilities | null>(null);

  useEffect(() => {
    fetchCapabilities()
      .then(setCapabilities)
      .catch((err) => console.warn('Could not load capabilities:', err));
  }, []);

  const toggleTheme = () => {
    setMode(effectiveTheme === 'dark' ? 'light' : 'dark');
  };

  return (
    <header className="border-b border-slate-800/80 bg-slate-950/85 backdrop-blur-xl sticky top-0 z-50 transition-all shadow-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo with Cyber Glow */}
        <div className="flex items-center space-x-3 cursor-pointer group" onClick={() => setActiveTab('enhance')}>
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500/20 via-cyan-500/10 to-amber-500/5 border border-amber-500/40 flex items-center justify-center text-amber-400 group-hover:border-amber-400 group-hover:scale-105 transition-all shadow-lg glow-amber">
              <Activity className="w-5 h-5 text-amber-400 stroke-[2.4]" />
            </div>
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-emerald-400 border-2 border-slate-950 cyber-ping" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-lg text-white tracking-tight">
                InfraClarity<span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-cyan-400"> AI</span>
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 font-bold border border-amber-500/30">
                PRO 1.0
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono tracking-wide hidden sm:block">
              High-Acuity Infrastructure Image Enhancer
            </p>
          </div>
        </div>

        {/* Navigation Tabs with High-Tech Pill Selector */}
        <nav className="flex items-center space-x-1 sm:space-x-1.5 p-1 rounded-xl bg-slate-900/90 border border-slate-800">
          <button
            onClick={() => setActiveTab('enhance')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all flex items-center space-x-2 ${
              activeTab === 'enhance'
                ? 'bg-gradient-to-r from-amber-500 to-amber-400 text-slate-950 font-bold shadow-md glow-amber'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>ENHANCE</span>
          </button>

          <button
            onClick={() => setActiveTab('batch')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all flex items-center space-x-2 ${
              activeTab === 'batch'
                ? 'bg-gradient-to-r from-amber-500 to-amber-400 text-slate-950 font-bold shadow-md glow-amber'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>BATCH QUEUE</span>
          </button>

          <button
            onClick={() => setActiveTab('about')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all flex items-center space-x-2 ${
              activeTab === 'about'
                ? 'bg-gradient-to-r from-amber-500 to-amber-400 text-slate-950 font-bold shadow-md glow-amber'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Info className="w-3.5 h-3.5" />
            <span>SYSTEM</span>
          </button>
        </nav>

        {/* Right side live telemetry pills & theme toggle */}
        <div className="flex items-center space-x-2.5">
          {/* Gemini AI Status Badge */}
          <div className="hidden lg:flex items-center space-x-1.5 px-2.5 py-1 rounded-lg text-[11px] font-mono bg-cyan-950/60 border border-cyan-500/30 text-cyan-300">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 cyber-ping" />
            <span>REAL-ESRGAN AI + GEMINI</span>
          </div>

          {capabilities && (
            <div className="hidden md:flex items-center space-x-1.5 px-2.5 py-1 rounded-lg text-[11px] font-mono bg-slate-900 border border-slate-700/80 text-slate-300">
              <Cpu className="w-3 h-3 text-amber-400" />
              <span>{capabilities.device.toUpperCase()}</span>
            </div>
          )}

          <button
            onClick={toggleTheme}
            aria-label="Toggle color theme"
            className="p-2 rounded-xl text-slate-400 hover:text-amber-400 hover:bg-slate-900 border border-transparent hover:border-slate-800 transition-colors"
          >
            {effectiveTheme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </header>
  );
};
