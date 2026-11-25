import React from 'react';
import { Severity } from '../../types';

interface GaugeMeterProps {
  label: string;
  score: number;
  maxScore?: number;
  severity: Severity;
  severityLabel: string;
  hint: string;
  unit?: string;
  invert?: boolean; // For blur / contrast where higher score indicates better clarity
}

export const GaugeMeter: React.FC<GaugeMeterProps> = ({
  label,
  score,
  maxScore = 100,
  severity,
  severityLabel,
  hint,
  unit = '',
  invert = false,
}) => {
  // Normalize percentage for arc gauge (0 - 100%)
  // If invert=true (e.g. Blur or Contrast), higher score means higher clarity/health
  let percentage: number;
  if (invert) {
    // Quality/Clarity meter: higher score = higher percentage
    percentage = Math.min(100, Math.max(0, (score / maxScore) * 100));
  } else {
    // Degradation meter: higher score = higher degradation
    percentage = Math.min(100, Math.max(0, (score / maxScore) * 100));
  }

  // Exact 180-degree semi-circular arc geometry
  // Arc path: M 14 62 A 46 46 0 0 1 106 62
  // Radius R = 46. Total arc length = PI * 46 = 144.513
  const arcLength = 144.513;
  // Ensure at least a visible 3% indicator if non-zero, capped at 100%
  const effectivePct = percentage > 0 ? Math.max(3, percentage) : 0;
  const strokeDashoffset = arcLength * (1 - effectivePct / 100);

  const getSeverityColors = (sev: Severity) => {
    switch (sev) {
      case 'high':
        return {
          stroke: '#f43f5e', // rose-500
          strokeLight: '#fda4af',
          bg: 'bg-rose-500/15 text-rose-300 border-rose-500/40',
          dot: 'bg-rose-400 shadow-[0_0_8px_#f43f5e]',
          glow: 'rgba(244, 63, 94, 0.4)',
        };
      case 'medium':
        return {
          stroke: '#f59e0b', // amber-500
          strokeLight: '#fde68a',
          bg: 'bg-amber-500/15 text-amber-300 border-amber-500/40',
          dot: 'bg-amber-400 shadow-[0_0_8px_#f59e0b]',
          glow: 'rgba(245, 158, 11, 0.4)',
        };
      case 'low':
      default:
        return {
          stroke: '#10b981', // emerald-500
          strokeLight: '#6ee7b7',
          bg: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40',
          dot: 'bg-emerald-400 shadow-[0_0_8px_#10b981]',
          glow: 'rgba(16, 185, 129, 0.4)',
        };
    }
  };

  const colors = getSeverityColors(severity);
  const gradId = `gauge-grad-${label.toLowerCase().replace(/[^a-z0-9]/g, '-')}`;

  // Formatting score to avoid ugly floating-point tails
  let formattedScore: string;
  if (score >= 100) {
    formattedScore = score.toFixed(1);
  } else if (score >= 10) {
    formattedScore = score.toFixed(1);
  } else if (score >= 1) {
    formattedScore = score.toFixed(2);
  } else {
    formattedScore = score.toFixed(3);
  }

  return (
    <div className="bg-slate-900/90 border border-slate-800 hover:border-slate-700/80 transition-all rounded-xl p-3.5 shadow-md flex flex-col justify-between min-w-0 group">
      {/* Header with zero-overlap flex layout */}
      <div className="flex items-center justify-between gap-1.5 min-w-0 pb-2 border-b border-slate-800/80">
        <div className="flex items-center space-x-1.5 min-w-0">
          <span className={`w-2 h-2 rounded-full flex-shrink-0 ${colors.dot}`} />
          <span
            className="text-[11px] font-mono font-bold text-slate-300 uppercase tracking-wider truncate"
            title={label}
          >
            {label}
          </span>
        </div>
        <span
          className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border flex-shrink-0 whitespace-nowrap shadow-sm ${colors.bg}`}
        >
          {severityLabel}
        </span>
      </div>

      {/* Speedometer Arc Gauge */}
      <div className="flex flex-col items-center justify-center py-2.5 relative">
        <div className="relative w-36 h-20 flex items-center justify-center">
          <svg viewBox="0 0 120 70" className="w-full h-full overflow-visible">
            <defs>
              <linearGradient id={gradId} x1="0%" y1="100%" x2="100%" y2="0%">
                <stop offset="0%" stopColor={colors.stroke} stopOpacity="0.75" />
                <stop offset="100%" stopColor={colors.strokeLight} stopOpacity="1" />
              </linearGradient>
            </defs>

            {/* Background 180° Track */}
            <path
              d="M 14 62 A 46 46 0 0 1 106 62"
              fill="none"
              stroke="#1e293b"
              strokeWidth="7"
              strokeLinecap="round"
              className="opacity-70"
            />

            {/* Active Colored Value Arc */}
            <path
              d="M 14 62 A 46 46 0 0 1 106 62"
              fill="none"
              stroke={`url(#${gradId})`}
              strokeWidth="7"
              strokeLinecap="round"
              strokeDasharray={arcLength}
              strokeDashoffset={strokeDashoffset}
              className="transition-all duration-700 ease-out"
              style={{
                filter: `drop-shadow(0 0 4px ${colors.glow})`,
              }}
            />
          </svg>

          {/* Perfectly Centered Numerical Value Readout */}
          <div className="absolute inset-0 flex flex-col items-center justify-end pb-1.5 pointer-events-none select-none">
            <div className="flex items-baseline justify-center space-x-0.5">
              <span className="text-2xl font-black font-mono tracking-tight text-white drop-shadow-md">
                {formattedScore}
              </span>
              {unit && (
                <span className="text-[11px] font-mono font-bold text-cyan-400 ml-1 px-1 py-0.2 rounded bg-cyan-950/60 border border-cyan-800/40">
                  {unit}
                </span>
              )}
            </div>
            <span
              className="text-[8.5px] font-mono font-bold tracking-widest uppercase mt-0.5"
              style={{ color: colors.stroke }}
            >
              {severity === 'low' ? 'NOMINAL' : severity === 'medium' ? 'ELEVATED' : 'CRITICAL'}
            </span>
          </div>
        </div>
      </div>

      {/* Footer Diagnostic Hint */}
      <div className="mt-auto pt-2 border-t border-slate-800/60">
        <p className="text-[11px] text-slate-400 font-sans leading-relaxed line-clamp-2" title={hint}>
          {hint}
        </p>
      </div>
    </div>
  );
};
