import React, { useState } from 'react';
import { Download, Copy, Check, ShieldCheck, FileText } from 'lucide-react';
import { useEnhanceStore } from '../../store/useEnhanceStore';
import { getResultImageUrl } from '../../api/client';

interface DownloadControlsProps {
  onOpenReport?: () => void;
}

export const DownloadControls: React.FC<DownloadControlsProps> = ({ onOpenReport }) => {
  const {
    jobId,
    jobStatus,
    outputFormat,
    setOutputFormat,
    quality,
    setQuality,
    stripGps,
    setStripGps,
    getEnhanceOptions,
  } = useEnhanceStore();

  const [copied, setCopied] = useState(false);
  const [matchOriginal, setMatchOriginal] = useState(false);

  if (!jobId || jobStatus?.status !== 'completed') {
    return null;
  }

  const handleDownload = (fmt: 'png' | 'jpeg') => {
    const url = getResultImageUrl(jobId, fmt, quality, matchOriginal);
    const a = document.createElement('a');
    a.href = url;
    a.download = `infraclarity_${jobId}${matchOriginal ? '_matched' : ''}.${fmt === 'jpeg' ? 'jpg' : 'png'}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const handleCopySettings = () => {
    const opts = getEnhanceOptions();
    navigator.clipboard.writeText(JSON.stringify(opts, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 shadow-sm space-y-3 transition-colors">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Export & Archival
        </span>
        <div className="flex items-center space-x-4">
          <label className="flex items-center space-x-1.5 text-xs text-slate-600 dark:text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={matchOriginal}
              onChange={(e) => setMatchOriginal(e.target.checked)}
              className="rounded text-brand-500 focus:ring-brand-500 dark:bg-slate-800"
            />
            <span>Same Size (Original Res)</span>
          </label>

          <label className="flex items-center space-x-1.5 text-xs text-slate-600 dark:text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={stripGps}
              onChange={(e) => setStripGps(e.target.checked)}
              className="rounded text-brand-500 focus:ring-brand-500 dark:bg-slate-800"
            />
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
            <span>Strip GPS EXIF</span>
          </label>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {onOpenReport && (
          <button
            type="button"
            onClick={onOpenReport}
            className="flex-1 min-w-[160px] px-3.5 py-2 bg-gradient-to-r from-brand-500 to-amber-500 hover:from-brand-400 hover:to-amber-400 text-slate-950 font-bold rounded-lg text-xs flex items-center justify-center space-x-1.5 shadow-md transition-all active:scale-[0.98]"
          >
            <FileText className="w-3.5 h-3.5 text-slate-950" />
            <span>Field Audit Report (PDF)</span>
          </button>
        )}

        <button
          onClick={() => handleDownload('png')}
          className="flex-1 min-w-[120px] px-3.5 py-2 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-950 rounded-lg text-xs font-semibold hover:bg-slate-800 dark:hover:bg-white transition-colors flex items-center justify-center space-x-1.5 shadow-sm"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Download PNG</span>
        </button>

        <button
          onClick={() => handleDownload('jpeg')}
          className="flex-1 min-w-[120px] px-3.5 py-2 bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-semibold hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors flex items-center justify-center space-x-1.5"
        >
          <Download className="w-3.5 h-3.5 text-brand-500" />
          <span>Download JPEG</span>
        </button>

        <button
          onClick={handleCopySettings}
          className="px-3 py-2 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-medium hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors flex items-center space-x-1"
          title="Copy enhancement parameters as JSON"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
          <span>{copied ? 'Copied' : 'JSON'}</span>
        </button>
      </div>
    </div>
  );
};
