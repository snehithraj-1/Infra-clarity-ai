import React, { useRef, useState } from 'react';
import { Layers, UploadCloud, Play, CheckCircle2, AlertCircle, Download, Trash2, Loader2 } from 'lucide-react';
import { submitEnhanceJob, fetchJobStatus, getResultImageUrl, formatApiError } from '../api/client';
import { EnhanceOptions } from '../types';

interface BatchItem {
  id: string;
  file: File;
  previewUrl: string;
  status: 'queued' | 'enhancing' | 'completed' | 'failed';
  jobId?: string;
  detailGain?: number;
  error?: string;
}

export const BatchPage: React.FC = () => {
  const [items, setItems] = useState<BatchItem[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [batchError, setBatchError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFiles = (files: FileList | null) => {
    if (!files) return;
    const newItems: BatchItem[] = [];
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (file.type.startsWith('image/')) {
        newItems.push({
          id: `${file.name}-${Date.now()}-${i}`,
          file,
          previewUrl: URL.createObjectURL(file),
          status: 'queued',
        });
      }
    }
    setItems((prev) => [...prev, ...newItems]);
  };

  const removeItem = (id: string) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
  };

  const clearAll = () => {
    setItems([]);
  };

  const processBatch = async () => {
    setIsProcessing(true);
    setBatchError(null);
    const options: EnhanceOptions = {
      preset: 'Auto',
      strip_gps: true,
      output_format: 'png',
      quality: 95,
    };

    for (const item of items) {
      if (item.status === 'completed') continue;

      setItems((prev) =>
        prev.map((it) => (it.id === item.id ? { ...it, status: 'enhancing', error: undefined } : it))
      );

      try {
        const { job_id } = await submitEnhanceJob(item.file, options);
        // Poll job completion (up to 120 seconds per image)
        let completed = false;
        let attempts = 0;
        while (!completed && attempts < 120) {
          await new Promise((r) => setTimeout(r, 1000));
          attempts++;
          const status = await fetchJobStatus(job_id);
          if (status.status === 'completed') {
            completed = true;
            setItems((prev) =>
              prev.map((it) =>
                it.id === item.id
                  ? {
                      ...it,
                      status: 'completed',
                      jobId: job_id,
                      detailGain: status.metrics?.detail_gain,
                    }
                  : it
              )
            );
          } else if (status.status === 'failed') {
            completed = true;
            const errMsg = status.error || 'Enhancement failed';
            setBatchError(errMsg);
            setItems((prev) =>
              prev.map((it) =>
                it.id === item.id
                  ? { ...it, status: 'failed', error: errMsg }
                  : it
              )
            );
          }
        }

        if (!completed) {
          const timeoutMsg = 'Enhancement timed out (exceeded 2 minutes)';
          setBatchError(timeoutMsg);
          setItems((prev) =>
            prev.map((it) =>
              it.id === item.id
                ? { ...it, status: 'failed', error: timeoutMsg }
                : it
            )
          );
        }
      } catch (err: any) {
        const errMsg = formatApiError(err);
        setBatchError(errMsg);
        setItems((prev) =>
          prev.map((it) =>
            it.id === item.id
              ? { ...it, status: 'failed', error: errMsg }
              : it
          )
        );
      }
    }
    setIsProcessing(false);
  };

  const downloadAll = () => {
    const completedItems = items.filter((it) => it.status === 'completed' && it.jobId);
    completedItems.forEach((it, idx) => {
      setTimeout(() => {
        const a = document.createElement('a');
        a.href = getResultImageUrl(it.jobId!);
        a.download = `enhanced_${it.file.name}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      }, idx * 400);
    });
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Top Banner / Error Toast */}
      {batchError && (
        <div className="bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900/60 p-4 rounded-xl flex items-start space-x-3 text-rose-700 dark:text-rose-300 text-xs shadow-md">
          <AlertCircle className="w-5 h-5 flex-shrink-0 text-rose-500 mt-0.5" />
          <div className="flex-1 space-y-1">
            <span className="font-semibold">Batch Error:</span> {batchError}
            {batchError.includes('Backend offline') && (
              <p className="text-[11px] text-rose-600/90 dark:text-rose-400 font-mono mt-1">
                Tip: Run <code className="bg-rose-100 dark:bg-rose-900/80 px-1 py-0.5 rounded font-bold">npm run dev</code> from your terminal to launch both the backend on port 8000 and the frontend.
              </p>
            )}
          </div>
          <button
            onClick={() => setBatchError(null)}
            className="text-rose-400 hover:text-rose-600 font-bold"
          >
            ×
          </button>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center space-x-2">
            <Layers className="w-5 h-5 text-brand-500" />
            <span>Batch Inspection Queue</span>
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Process multiple drone survey frames sequentially with auto-diagnosis and tiled enhancement
          </p>
        </div>

        <div className="flex items-center space-x-2">
          {items.length > 0 && (
            <>
              <button
                type="button"
                onClick={clearAll}
                disabled={isProcessing}
                className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-800 text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors disabled:opacity-50"
              >
                Clear Queue
              </button>

              <button
                type="button"
                onClick={downloadAll}
                disabled={!items.some((it) => it.status === 'completed')}
                className="px-3.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs font-semibold text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors flex items-center space-x-1.5 disabled:opacity-40"
              >
                <Download className="w-3.5 h-3.5 text-brand-500" />
                <span>Download All</span>
              </button>

              <button
                type="button"
                onClick={processBatch}
                disabled={isProcessing || !items.some((it) => it.status === 'queued')}
                className="px-4 py-1.5 rounded-lg bg-brand-500 hover:bg-brand-400 text-slate-950 text-xs font-bold transition-all shadow-sm flex items-center space-x-1.5 disabled:opacity-50"
              >
                {isProcessing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                <span>{isProcessing ? 'Processing Queue...' : 'Enhance All'}</span>
              </button>
            </>
          )}
        </div>
      </div>

      {/* Upload Dropzone */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="image/png,image/jpeg,image/webp,image/tiff"
        onChange={(e) => handleFiles(e.target.files)}
        className="hidden"
      />

      <div
        onClick={() => fileInputRef.current?.click()}
        className="border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-brand-500 rounded-xl p-8 text-center cursor-pointer bg-slate-50/50 dark:bg-slate-900/50 transition-colors"
      >
        <UploadCloud className="w-8 h-8 text-brand-500 mx-auto mb-2" />
        <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">
          Click or drag multiple inspection images to add to the queue
        </span>
        <p className="text-[11px] text-slate-400 mt-1 font-mono">PNG, JPEG, WebP, TIFF up to 50 MB each</p>
      </div>

      {/* Items List */}
      {items.length > 0 && (
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 divide-y divide-slate-100 dark:divide-slate-800 overflow-hidden shadow-sm">
          {items.map((item) => (
            <div key={item.id} className="p-3.5 flex items-center justify-between space-x-4">
              <div className="flex items-center space-x-3 min-w-0">
                <img
                  src={item.previewUrl}
                  alt={item.file.name}
                  className="w-12 h-12 rounded object-cover border border-slate-200 dark:border-slate-800 flex-shrink-0"
                />
                <div className="min-w-0">
                  <p className="text-xs font-semibold text-slate-900 dark:text-slate-100 truncate">
                    {item.file.name}
                  </p>
                  <p className="text-[10px] text-slate-400 font-mono">
                    {(item.file.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                {/* Status indicator */}
                {item.status === 'queued' && (
                  <span className="text-[11px] font-mono font-medium px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500">
                    Queued
                  </span>
                )}
                {item.status === 'enhancing' && (
                  <span className="text-[11px] font-mono font-semibold px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-600 dark:text-brand-400 flex items-center space-x-1 animate-pulse">
                    <Loader2 className="w-3 h-3 animate-spin" />
                    <span>Enhancing...</span>
                  </span>
                )}
                {item.status === 'completed' && (
                  <div className="flex items-center space-x-2">
                    <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center space-x-1">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>{item.detailGain ? `+${item.detailGain}%` : 'Done'}</span>
                    </span>
                    {item.jobId && (
                      <a
                        href={getResultImageUrl(item.jobId)}
                        download={`enhanced_${item.file.name}`}
                        className="p-1 rounded text-slate-400 hover:text-slate-800 dark:hover:text-slate-200"
                        title="Download Enhanced Image"
                      >
                        <Download className="w-4 h-4" />
                      </a>
                    )}
                  </div>
                )}
                {item.status === 'failed' && (
                  <div className="flex items-center space-x-2">
                    <span
                      className="text-[11px] font-mono font-semibold px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-500 flex items-center space-x-1 cursor-help"
                      title={item.error || 'Enhancement failed'}
                    >
                      <AlertCircle className="w-3 h-3 flex-shrink-0" />
                      <span className="truncate max-w-[140px] sm:max-w-[200px]">
                        {item.error ? item.error.replace('Backend offline: ', '') : 'Failed'}
                      </span>
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        setItems((prev) =>
                          prev.map((it) =>
                            it.id === item.id ? { ...it, status: 'queued', error: undefined } : it
                          )
                        );
                      }}
                      className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 hover:bg-amber-500/30 transition-colors"
                      title="Re-queue this image for enhancement"
                    >
                      Retry
                    </button>
                  </div>
                )}

                <button
                  onClick={() => removeItem(item.id)}
                  disabled={isProcessing && item.status === 'enhancing'}
                  className="p-1.5 text-slate-400 hover:text-rose-500 rounded transition-colors disabled:opacity-30"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
