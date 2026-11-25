import React from 'react';
import { Sliders, CloudRain, Radio, Search, Moon, Wand2 } from 'lucide-react';
import { useEnhanceStore } from '../../store/useEnhanceStore';
import { PresetName } from '../../types';

interface PresetItem {
  id: PresetName;
  label: string;
  description: string;
  icon: React.ReactNode;
}

const PRESETS: PresetItem[] = [
  {
    id: 'Auto',
    label: 'Auto (Diagnosis)',
    description: 'Rules-driven pipeline matching optical report',
    icon: <Wand2 className="w-3.5 h-3.5" />,
  },
  {
    id: 'Hazy / Rainy Weather',
    label: 'Hazy / Rainy',
    description: 'Dark Channel Prior + rain particulate noise reduction',
    icon: <CloudRain className="w-3.5 h-3.5" />,
  },
  {
    id: 'Distant Tower',
    label: 'Distant Tower',
    description: 'Atmospheric distance dehazing + telephoto deblur + x2 super-res',
    icon: <Radio className="w-3.5 h-3.5" />,
  },
  {
    id: 'Pipeline Close-up',
    label: 'Pipeline Close-up',
    description: 'High-frequency unsharp mask for hairline cracks & corrosion',
    icon: <Search className="w-3.5 h-3.5" />,
  },
  {
    id: 'Low Light',
    label: 'Low Light',
    description: 'Dynamic range expansion in LAB space + high-ISO chroma denoise',
    icon: <Moon className="w-3.5 h-3.5" />,
  },
];

export const PresetSelector: React.FC = () => {
  const { preset, setPreset, isEnhancing } = useEnhanceStore();

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex items-center space-x-1.5">
          <Sliders className="w-3.5 h-3.5" />
          <span>Inspection Preset</span>
        </label>
        <span className="text-[11px] text-slate-400 font-mono">Select or customize stages</span>
      </div>

      <div className="flex flex-wrap gap-2">
        {PRESETS.map((p) => {
          const active = preset === p.id;
          return (
            <button
              key={p.id}
              type="button"
              disabled={isEnhancing}
              onClick={() => setPreset(p.id)}
              title={p.description}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-150 flex items-center space-x-1.5 border ${
                active
                  ? 'bg-brand-500 text-slate-950 border-brand-600 shadow-sm'
                  : 'bg-white dark:bg-slate-850 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <span>{p.icon}</span>
              <span>{p.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
