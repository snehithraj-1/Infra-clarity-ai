import React, { useState } from 'react';
import { AlertTriangle, CheckCircle2, Sparkles, ShieldAlert, ChevronDown, ChevronUp, EyeOff } from 'lucide-react';
import { useEnhanceStore } from '../../store/useEnhanceStore';
import { GaugeMeter } from './GaugeMeter';

export const DiagnosisPanel: React.FC = () => {
  const { report, isAnalyzing, dimensions, jobStatus } = useEnhanceStore();
  const [showLoopholes, setShowLoopholes] = useState(true);

  if (isAnalyzing) {
    return (
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-4 animate-pulse">
        <div className="flex items-center space-x-3">
          <div className="w-5 h-5 rounded-full bg-brand-500/20" />
          <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-48" />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 bg-slate-100 dark:bg-slate-800/60 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  if (!report) {
    return null;
  }

  const [w, h] = dimensions || report.dimensions;

  return (
    <div className="cyber-panel rounded-2xl p-6 space-y-5 shadow-2xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2.5 min-w-0">
          <div className="w-7 h-7 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 flex-shrink-0">
            <Sparkles className="w-4 h-4 text-amber-400" />
          </div>
          <div className="min-w-0">
            <h3 className="text-xs sm:text-sm font-bold text-white uppercase tracking-wider font-mono truncate">
              Autonomous Optical Telemetry Matrix
            </h3>
            <p className="text-[10px] text-slate-400 font-mono">
              REAL-TIME SENSOR DEGRADATION AUDIT
            </p>
          </div>
        </div>
        <div className="text-xs font-mono text-cyan-400 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 whitespace-nowrap self-start sm:self-auto">
          Source Frame: {w} × {h} px
        </div>
      </div>

      {/* 4 Gauges */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        <GaugeMeter
          label="Blur"
          score={report.blur.score}
          maxScore={300}
          severity={report.blur.severity}
          severityLabel={report.blur.label}
          hint={report.blur.hint}
          invert={true}
        />
        <GaugeMeter
          label="Atmospheric Haze"
          score={report.haze.score}
          maxScore={0.6}
          severity={report.haze.severity}
          severityLabel={report.haze.label}
          hint={report.haze.hint}
        />
        <GaugeMeter
          label="Sensor Noise"
          score={report.noise.score}
          maxScore={20}
          severity={report.noise.severity}
          severityLabel={report.noise.label}
          hint={report.noise.hint}
          unit="σ"
        />
        <GaugeMeter
          label="RMS Contrast"
          score={report.contrast.score}
          maxScore={0.5}
          severity={report.contrast.severity}
          severityLabel={report.contrast.label}
          hint={report.contrast.hint}
          invert={true}
        />
      </div>

      {/* Synthesis Recommendations */}
      <div className="bg-slate-900/90 p-4 rounded-xl border border-slate-800/90 text-xs text-slate-300 space-y-2">
        <div className="font-bold text-amber-300 flex items-center space-x-2 font-mono text-[11px]">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>ALGORITHMIC RESTORATION PRESCRIPTION:</span>
        </div>
        <ul className="list-disc list-inside space-y-1 text-slate-400 pl-1 font-sans text-xs">
          {report.hints.map((hint, idx) => (
            <li key={idx} className="leading-relaxed">{hint}</li>
          ))}
        </ul>

        {report.resolution_flag && (
          <div className="mt-2 pt-2 border-t border-slate-800 flex items-center space-x-2 text-amber-400 font-medium">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>Shorter side is below 1080px. Super-resolution recommended to resolve hairline defects.</span>
          </div>
        )}
      </div>

      {/* Gemini AI Scene Diagnosis & Blindspot Audit */}
      {jobStatus?.ai_analysis && (
        <div className="bg-gradient-to-r from-amber-500/15 via-cyan-500/10 to-amber-500/10 border border-amber-500/40 rounded-xl p-4 space-y-2 shadow-lg glow-amber">
          <div className="flex items-center space-x-2 text-xs font-bold text-amber-400">
            <Sparkles className="w-4 h-4 text-amber-400 animate-pulse" />
            <span className="font-mono tracking-wide">GEMINI AI SCENE DIAGNOSIS & BLINDSPOT AUDIT</span>
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-300 border border-cyan-500/40">
              gemini-flash-lite
            </span>
          </div>
          <div className="text-xs text-slate-200 leading-relaxed font-sans whitespace-pre-line">
            {jobStatus.ai_analysis}
          </div>
        </div>
      )}

      {/* Identified Loopholes & Inspection Blindspots in Original Image */}
      {report.loopholes && report.loopholes.length > 0 && (
        <div className="bg-slate-900/80 border border-amber-500/30 rounded-xl p-4 space-y-3">
          <div
            onClick={() => setShowLoopholes(!showLoopholes)}
            className="flex items-center justify-between cursor-pointer select-none"
          >
            <div className="flex items-center space-x-2">
              <EyeOff className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-bold text-amber-300 uppercase tracking-wide font-mono">
                Identified Optical Loopholes & Structural Blindspots ({report.loopholes.length})
              </span>
            </div>
            <div className="flex items-center space-x-1.5 text-xs text-amber-400 font-mono font-semibold">
              <span>{showLoopholes ? 'COLLAPSE' : 'EXPAND'}</span>
              {showLoopholes ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </div>
          </div>

          {showLoopholes && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
              {report.loopholes.map((lp) => (
                <div
                  key={lp.id}
                  className="bg-slate-950/90 p-3.5 rounded-xl border border-slate-800 hover:border-amber-500/40 transition-colors shadow-md space-y-1.5 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-100 flex items-center space-x-1.5">
                      <span className="text-amber-400">⚡</span>
                      <span>{lp.title}</span>
                    </span>
                    <span
                      className={`text-[9px] font-mono font-bold uppercase px-2 py-0.5 rounded-full ${
                        lp.severity === 'high'
                          ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                          : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                      }`}
                    >
                      {lp.severity} Risk
                    </span>
                  </div>
                  <p className="text-slate-400 text-[11px] leading-relaxed">
                    <span className="font-semibold text-rose-400">Original Defect:</span>{' '}
                    {lp.vulnerability_in_original}
                  </p>
                  <p className="text-slate-400 text-[11px] leading-relaxed">
                    <span className="font-semibold text-emerald-400">Restoration:</span>{' '}
                    {lp.restoration_fix}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
