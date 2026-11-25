import React from 'react';
import { Sun, Shield, Focus, ZoomIn } from 'lucide-react';
import { useEnhanceStore } from '../../store/useEnhanceStore';
import { StageName } from '../../types';

interface StageMeta {
  name: StageName;
  title: string;
  technique: string;
  icon: React.ReactNode;
}

const STAGES_META: StageMeta[] = [
  {
    name: 'dehaze',
    title: 'Dehaze',
    technique: 'Atmospheric Radiance Recovery & Texture-Gated Contrast',
    icon: <Sun className="w-4 h-4 text-amber-500" />,
  },
  {
    name: 'denoise',
    title: 'Denoise',
    technique: 'Full-Spectrum Sensor Grain & Particulate Removal',
    icon: <Shield className="w-4 h-4 text-sky-500" />,
  },
  {
    name: 'deblur',
    title: 'Deblur',
    technique: 'Real-ESRGAN Blind Deblur + Anti-Ringing Edge Acuity',
    icon: <Focus className="w-4 h-4 text-emerald-500" />,
  },
  {
    name: 'super_resolution',
    title: 'Super-Resolution',
    technique: 'Real-ESRGAN Neural x2 Super-Resolution & Pattern Synthesis',
    icon: <ZoomIn className="w-4 h-4 text-indigo-500" />,
  },
];

export const StageControls: React.FC = () => {
  const { stages, toggleStage, setStageStrength, isEnhancing } = useEnhanceStore();

  return (
    <div className="space-y-3">
      <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
        Pipeline Stages (Enforced Order)
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {STAGES_META.map((meta) => {
          const config = stages.find((s) => s.name === meta.name) || {
            name: meta.name,
            enabled: false,
            strength: 50,
            engine: 'classical',
          };

          return (
            <div
              key={meta.name}
              className={`p-3.5 rounded-xl border transition-colors ${
                config.enabled
                  ? 'bg-white dark:bg-slate-850 border-brand-500/40 shadow-sm'
                  : 'bg-slate-50/60 dark:bg-slate-900/40 border-slate-200 dark:border-slate-800 opacity-70'
              }`}
            >
              {/* Header row */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="p-1 rounded-md bg-slate-100 dark:bg-slate-800">
                    {meta.icon}
                  </div>
                  <div>
                    <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                      {meta.title}
                    </span>
                    <span
                      className={`ml-2 text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase ${
                        config.engine.includes('neural')
                          ? 'bg-indigo-500/15 text-indigo-400 border border-indigo-500/30'
                          : config.engine.includes('guided')
                          ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                          : config.engine.includes('bilateral') || config.engine.includes('NLM')
                          ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-400'
                      }`}
                    >
                      {config.engine}
                    </span>
                  </div>
                </div>

                {/* Toggle switch */}
                <button
                  type="button"
                  role="switch"
                  aria-checked={config.enabled}
                  disabled={isEnhancing}
                  onClick={() => toggleStage(meta.name)}
                  className={`w-9 h-5 flex items-center rounded-full p-0.5 transition-colors cursor-pointer disabled:cursor-not-allowed ${
                    config.enabled ? 'bg-brand-500' : 'bg-slate-300 dark:bg-slate-700'
                  }`}
                >
                  <div
                    className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${
                      config.enabled ? 'translate-x-4' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>

              <p className="text-[10px] text-slate-400 mt-1 font-mono truncate">
                {meta.technique}
              </p>

              {/* Strength slider */}
              <div className="mt-2.5 pt-2 border-t border-slate-100 dark:border-slate-800">
                <div className="flex justify-between text-[11px] text-slate-500 mb-1">
                  <span>Intensity</span>
                  <span className="font-mono font-semibold text-slate-900 dark:text-slate-200">
                    {config.strength}%
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  disabled={!config.enabled || isEnhancing}
                  value={config.strength}
                  onChange={(e) => setStageStrength(meta.name, parseInt(e.target.value, 10))}
                  className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-brand-500 disabled:opacity-40 disabled:cursor-not-allowed"
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
