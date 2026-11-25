import React from 'react';
import { Eye, TrendingUp, Info } from 'lucide-react';
import { useEnhanceStore } from '../../store/useEnhanceStore';

export const MetricsCards: React.FC = () => {
  const { jobStatus } = useEnhanceStore();
  const metrics = jobStatus?.metrics;

  if (!metrics) {
    return null;
  }

  return (
    <div className="cyber-panel rounded-2xl p-4 sm:p-5 space-y-4 shadow-2xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-2.5">
        <div className="flex items-center space-x-2">
          <TrendingUp className="w-4 h-4 text-amber-400 flex-shrink-0" />
          <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
            Restoration Quality Telemetry & Frequency Gain
          </h3>
        </div>
        <div className="flex items-center space-x-1.5 text-[11px] text-cyan-400 font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 whitespace-nowrap self-start sm:self-auto">
          <Eye className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
          <span>MICRO-DETAIL ACUITY</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
        {/* Detail Gain */}
        <div className="bg-slate-950/90 p-4 rounded-xl border border-amber-500/30 hover:border-amber-400 transition-colors shadow-lg glow-amber relative overflow-hidden group flex flex-col justify-between">
          <div className="absolute top-0 right-0 w-16 h-16 bg-amber-500/10 rounded-bl-full pointer-events-none" />
          <span className="text-[10px] font-mono font-bold text-amber-400 uppercase tracking-wider">
            COMPOSITE CLARITY GAIN
          </span>
          <div className="flex items-baseline space-x-1 my-2">
            <span className="text-2xl sm:text-3xl font-black font-mono tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-amber-200 truncate">
              {metrics.detail_gain > 0 ? `+${metrics.detail_gain}%` : `${metrics.detail_gain}%`}
            </span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-gradient-to-r from-amber-500 to-amber-300 h-full rounded-full transition-all duration-700"
              style={{ width: `${Math.min(100, Math.max(10, metrics.detail_gain / 25))}%` }}
            />
          </div>
          <p className="text-[10px] font-mono text-slate-400 mt-2">Edge acuity & high-frequency texture</p>
        </div>

        {/* Edge Density Gain */}
        <div className="bg-slate-950/90 p-4 rounded-xl border border-cyan-500/30 hover:border-cyan-400 transition-colors shadow-lg glow-cyan relative overflow-hidden group flex flex-col justify-between">
          <div className="absolute top-0 right-0 w-16 h-16 bg-cyan-500/10 rounded-bl-full pointer-events-none" />
          <span className="text-[10px] font-mono font-bold text-cyan-400 uppercase tracking-wider">
            CANNY EDGE RECOVERY
          </span>
          <div className="flex items-baseline space-x-1 my-2">
            <span className="text-2xl sm:text-3xl font-black font-mono tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-cyan-200 truncate">
              {metrics.canny_gain > 0 ? `+${metrics.canny_gain}%` : `${metrics.canny_gain}%`}
            </span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-gradient-to-r from-cyan-500 to-cyan-300 h-full rounded-full transition-all duration-700"
              style={{ width: `${Math.min(100, Math.max(10, metrics.canny_gain / 25))}%` }}
            />
          </div>
          <p className="text-[10px] font-mono text-slate-400 mt-2">Crack & joint contour visibility</p>
        </div>

        {/* Laplacian High-Frequency Gain */}
        <div className="bg-slate-950/90 p-4 rounded-xl border border-emerald-500/30 hover:border-emerald-400 transition-colors shadow-lg glow-emerald relative overflow-hidden group flex flex-col justify-between sm:col-span-2 lg:col-span-1">
          <div className="absolute top-0 right-0 w-16 h-16 bg-emerald-500/10 rounded-bl-full pointer-events-none" />
          <span className="text-[10px] font-mono font-bold text-emerald-400 uppercase tracking-wider">
            LAPLACIAN ACUITY
          </span>
          <div className="flex items-baseline space-x-1 my-2">
            <span className="text-2xl sm:text-3xl font-black font-mono tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-emerald-200 truncate">
              {metrics.laplacian_gain > 0 ? `+${metrics.laplacian_gain}%` : `${metrics.laplacian_gain}%`}
            </span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-gradient-to-r from-emerald-500 to-emerald-300 h-full rounded-full transition-all duration-700"
              style={{ width: `${Math.min(100, Math.max(10, metrics.laplacian_gain / 35))}%` }}
            />
          </div>
          <p className="text-[10px] font-mono text-slate-400 mt-2">High-frequency gradient sharpness</p>
        </div>
      </div>

      <div className="flex items-start space-x-2 text-[11px] text-slate-400 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
        <Info className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
        <div className="space-y-1">
          <span>
            Mathematical proxy metrics compute high-frequency gradient restoration relative to the degraded capture frame.
          </span>
          {metrics.note && (
            <p className="text-[10px] text-slate-500 font-mono">{metrics.note}</p>
          )}
        </div>
      </div>
    </div>
  );
};
