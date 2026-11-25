import React, { useEffect, useState } from 'react';
import { Play, RotateCcw, AlertCircle, Sparkles } from 'lucide-react';
import { useEnhanceStore } from '../store/useEnhanceStore';
import { submitEnhanceJob, subscribeJobEvents, getResultImageUrl, getOriginalImageUrl, formatApiError } from '../api/client';
import { UploadZone } from '../components/upload/UploadZone';
import { DiagnosisPanel } from '../components/diagnosis/DiagnosisPanel';
import { PresetSelector } from '../components/controls/PresetSelector';
import { StageControls } from '../components/controls/StageControls';
import { ComparisonSlider } from '../components/viewer/ComparisonSlider';
import { JobProgressBar } from '../components/progress/JobProgressBar';
import { CloseRangePatternGallery } from '../components/viewer/CloseRangePatternGallery';
import { MetricsCards } from '../components/metrics/MetricsCards';
import { DownloadControls } from '../components/controls/DownloadControls';
import { InspectionAssistant } from '../components/assistant/InspectionAssistant';
import { InspectionReportModal } from '../components/report/InspectionReportModal';

export const EnhancePage: React.FC = () => {
  const {
    originalFile,
    previewUrl,
    jobId,
    jobStatus,
    enhancedResultUrl,
    isEnhancing,
    error,
    setJobId,
    setJobStatus,
    setEnhancedResultUrl,
    setIsEnhancing,
    setError,
    reset,
    getEnhanceOptions,
  } = useEnhanceStore();

  const [isReportOpen, setIsReportOpen] = useState(false);

  // Subscribe to SSE progress updates when a job is created
  useEffect(() => {
    if (!jobId) return;

    const unsubscribe = subscribeJobEvents(
      jobId,
      (status) => {
        setJobStatus(status);
        if (status.status === 'completed') {
          setEnhancedResultUrl(getResultImageUrl(jobId));
          setIsEnhancing(false);
        } else if (status.status === 'failed') {
          setError(status.error || 'Enhancement failed');
          setIsEnhancing(false);
        }
      },
      (err) => {
        console.warn('SSE subscription warning:', err);
      }
    );

    return () => {
      unsubscribe();
    };
  }, [jobId, setJobStatus, setEnhancedResultUrl, setIsEnhancing, setError]);

  const handleStartEnhance = async () => {
    if (!originalFile) return;

    try {
      setError(null);
      setEnhancedResultUrl(null);
      setIsEnhancing(true);
      const options = getEnhanceOptions();
      const res = await submitEnhanceJob(originalFile, options);
      setJobId(res.job_id);
    } catch (err: any) {
      console.error('Failed to submit job:', err);
      setIsEnhancing(false);
      setError(formatApiError(err));
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Top Banner / Error Toast */}
      {error && (
        <div className="bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900/60 p-4 rounded-xl flex items-start space-x-3 text-rose-700 dark:text-rose-300 text-xs shadow-md">
          <AlertCircle className="w-5 h-5 flex-shrink-0 text-rose-500 mt-0.5" />
          <div className="flex-1 space-y-1">
            <span className="font-semibold">Error:</span> {error}
            {error.includes('Backend offline') && (
              <p className="text-[11px] text-rose-600/90 dark:text-rose-400 font-mono mt-1">
                Tip: Run <code className="bg-rose-100 dark:bg-rose-900/80 px-1 py-0.5 rounded font-bold">npm run dev</code> in your terminal so both the FastAPI backend and frontend run together.
              </p>
            )}
          </div>
          <button
            onClick={() => setError(null)}
            className="text-rose-400 hover:text-rose-600 font-bold"
          >
            ×
          </button>
        </div>
      )}

      {/* If no image uploaded yet, show Upload Zone */}
      {!previewUrl ? (
        <div className="space-y-6">
          <UploadZone />

          {/* Quick Info Box */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-slate-500 dark:text-slate-400">
            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
              <span className="font-semibold text-slate-800 dark:text-slate-200">Domain-Tuned Restoration</span>
              <p>Optimized for corrosion, hairline weld cracks, damaged glass insulators, and transmission line sag.</p>
            </div>
            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
              <span className="font-semibold text-slate-800 dark:text-slate-200">Tiled Inference</span>
              <p>Processes 24MP+ drone images up to 6000×4000 on laptop CPUs without memory overflow.</p>
            </div>
            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
              <span className="font-semibold text-slate-800 dark:text-slate-200">Zero Crash Guarantee</span>
              <p>Classical computer vision fallbacks operate immediately without pre-downloaded deep weights.</p>
            </div>
          </div>
        </div>
      ) : (
        /* Image is loaded: show full enhancement workbench */
        <div className="space-y-6">
          {/* Top Action Bar */}
          <div className="flex items-center justify-between p-3.5 cyber-panel rounded-2xl shadow-xl">
            <button
              type="button"
              onClick={reset}
              disabled={isEnhancing}
              className="px-3.5 py-2 rounded-xl border border-slate-800 bg-slate-900/80 text-xs font-mono font-semibold text-slate-300 hover:text-white hover:border-slate-700 transition-all flex items-center space-x-2 disabled:opacity-50"
            >
              <RotateCcw className="w-3.5 h-3.5 text-amber-400" />
              <span>LOAD NEW CAPTURE</span>
            </button>

            <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>INSPECTION WORKBENCH READY</span>
            </div>
          </div>

          {/* 1. Autonomous Optical Telemetry Matrix (Inspectors: Diagnosis) */}
          <DiagnosisPanel />

          {/* 2. Pipeline Presets & Stage Sliders (Inspectors: Presets & Controls above image) */}
          <div className="cyber-panel rounded-2xl p-6 shadow-2xl space-y-6 border border-slate-800/80">
            <PresetSelector />
            <StageControls />
          </div>

          {/* 3. Enhance Button directly below inspectors & above the image */}
          <div className="p-4 cyber-panel rounded-2xl shadow-2xl border border-amber-500/40 bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-5 h-5 text-amber-400 animate-pulse" />
              </div>
              <div>
                <h4 className="text-xs font-mono font-bold text-amber-400 uppercase tracking-wider">
                  Ready to Restore Asset Acuity
                </h4>
                <p className="text-[11px] text-slate-400 font-mono">
                  {isEnhancing
                    ? 'Processing through deep Real-ESRGAN Compact neural model...'
                    : 'Adjust parameters above and click to execute high-impact enhancement.'}
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={handleStartEnhance}
              disabled={isEnhancing}
              className="w-full sm:w-auto px-8 py-3 rounded-xl bg-gradient-to-r from-amber-500 via-amber-400 to-amber-500 hover:from-amber-400 hover:to-amber-300 text-slate-950 font-black text-sm tracking-wide shadow-2xl glow-amber hover:scale-105 active:scale-95 transition-all flex items-center justify-center space-x-2.5 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Sparkles className="w-4 h-4 text-slate-950 animate-pulse" />
              <span>{isEnhancing ? 'ENHANCING WITH REAL-ESRGAN NEURAL AI...' : 'START ENHANCE IMAGE'}</span>
            </button>
          </div>

          {/* 4. Interactive Before / After Comparison Viewer */}
          <ComparisonSlider
            beforeUrl={jobId && enhancedResultUrl ? getOriginalImageUrl(jobId) : (previewUrl || '')}
            afterUrl={enhancedResultUrl}
            beforeLabel="ORIGINAL INSPECTION"
            afterLabel="INFRACLARITY ENHANCED"
            isEnhancing={isEnhancing}
          />

          {/* 5. Real-time Progress Bar */}
          <JobProgressBar />

          {/* 6. Close-Range Macro Pattern Gallery (Autonomous Pattern Recognition) */}
          <CloseRangePatternGallery />

          {/* 7. Quality Metrics Cards (when completed) */}
          <MetricsCards />

          {/* 7. AI Inspection Assistant Copilot */}
          <InspectionAssistant />

          {/* 8. Export & Download Controls */}
          <DownloadControls onOpenReport={() => setIsReportOpen(true)} />

          {/* Certified Field Audit Report Modal */}
          <InspectionReportModal
            isOpen={isReportOpen}
            onClose={() => setIsReportOpen(false)}
            beforeUrl={previewUrl}
            afterUrl={enhancedResultUrl}
          />
        </div>
      )}
    </div>
  );
};
