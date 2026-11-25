import React from 'react';
import { Loader2, CheckCircle, Clock } from 'lucide-react';
import { useEnhanceStore } from '../../store/useEnhanceStore';

export const JobProgressBar: React.FC = () => {
  const { jobStatus, isEnhancing } = useEnhanceStore();

  if (!jobStatus || (!isEnhancing && jobStatus.status === 'completed')) {
    return null;
  }

  const pct = Math.round(jobStatus.progress * 100);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 shadow-sm space-y-3 transition-colors">
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2">
          {jobStatus.status === 'completed' ? (
            <CheckCircle className="w-4 h-4 text-emerald-500" />
          ) : (
            <Loader2 className="w-4 h-4 text-brand-500 animate-spin" />
          )}
          <span className="font-semibold text-slate-900 dark:text-slate-100">
            {jobStatus.current_stage || 'Processing image...'}
          </span>
        </div>
        <span className="font-mono font-bold text-brand-600 dark:text-brand-400 text-xs">
          {pct}%
        </span>
      </div>

      {/* Progress bar container */}
      <div className="w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
        <div
          className="bg-brand-500 h-full rounded-full transition-all duration-200 ease-out"
          style={{ width: `${pct}%` }}
        />
      </div>

      {/* Step pills */}
      {jobStatus.stages && jobStatus.stages.length > 0 && (
        <div className="flex flex-wrap gap-1.5 pt-1">
          {jobStatus.stages.map((stg) => {
            let badgeBg = 'bg-slate-100 dark:bg-slate-800 text-slate-400';
            if (stg.status === 'completed') badgeBg = 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-medium';
            if (stg.status === 'in_progress') badgeBg = 'bg-brand-500/15 text-brand-600 dark:text-brand-400 font-semibold animate-pulse';

            return (
              <span
                key={stg.stage}
                className={`text-[10px] font-mono px-2 py-0.5 rounded-full capitalize border border-transparent ${badgeBg}`}
              >
                {stg.stage.replace('_', ' ')}
                {stg.status === 'in_progress' && ` (${Math.round(stg.progress * 100)}%)`}
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
};
