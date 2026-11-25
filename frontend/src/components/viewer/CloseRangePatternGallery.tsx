import React, { useState } from 'react';
import {
  Focus,
  Sparkles,
  Maximize2,
  X,
  Layers,
  ArrowRight,
  TrendingUp,
  SlidersHorizontal,
} from 'lucide-react';
import { useEnhanceStore } from '../../store/useEnhanceStore';
import { CloseRangePatternImage } from '../../types';

export const CloseRangePatternGallery: React.FC = () => {
  const { jobStatus } = useEnhanceStore();
  const closeRangeImages = jobStatus?.close_range_images;

  const [selectedCrop, setSelectedCrop] = useState<CloseRangePatternImage | null>(null);
  const [activeViews, setActiveViews] = useState<{ [id: string]: 'enhanced' | 'original' }>({});

  if (!closeRangeImages || closeRangeImages.length === 0) {
    return null;
  }

  const toggleViewMode = (id: string) => {
    setActiveViews((prev) => ({
      ...prev,
      [id]: prev[id] === 'original' ? 'enhanced' : 'original',
    }));
  };

  return (
    <div className="cyber-panel rounded-2xl p-6 shadow-2xl space-y-6 border border-amber-500/30">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
            <Focus className="w-5 h-5 text-amber-400 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm sm:text-base font-bold text-white uppercase tracking-wider font-mono">
                Close-Range Macro Detail Inspection Gallery
              </h3>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
                {closeRangeImages.length} PATTERNS RECOGNIZED
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              The model analyzed structural patterns in the image and generated ultra-magnified close-range macro views.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 text-xs font-mono text-cyan-400">
          <Layers className="w-3.5 h-3.5 text-cyan-400" />
          <span>Macro Real-ESRGAN + Micro-Detail Shock</span>
        </div>
      </div>

      {/* Grid of Close-Range Pattern Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {closeRangeImages.map((crop, idx) => {
          const currentMode = activeViews[crop.id] || 'enhanced';
          const displayUrl = currentMode === 'enhanced' ? crop.enhanced_crop_url : crop.original_crop_url;

          return (
            <div
              key={crop.id}
              className="bg-slate-900/90 rounded-xl border border-slate-800 hover:border-amber-500/50 transition-all p-4 space-y-3.5 shadow-xl flex flex-col justify-between group"
            >
              {/* Card Header */}
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">
                      PATTERN #{idx + 1}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400 uppercase">
                      {crop.category}
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-white font-mono mt-1 group-hover:text-amber-300 transition-colors">
                    {crop.label}
                  </h4>
                </div>

                {/* Acuity Gain Chip */}
                <div className="flex items-center space-x-1 px-2 py-1 rounded-lg bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 text-[10px] font-mono font-bold shadow-md">
                  <TrendingUp className="w-3 h-3 text-emerald-400" />
                  <span>+{crop.detail_gain.toLocaleString()}% Acuity</span>
                </div>
              </div>

              {/* Close-Range Macro Viewer Stage */}
              <div className="relative w-full h-[220px] rounded-lg overflow-hidden bg-slate-950 border border-slate-800 flex items-center justify-center">
                <img
                  src={displayUrl}
                  alt={crop.label}
                  className="w-full h-full object-contain transition-transform duration-200 group-hover:scale-105"
                  draggable={false}
                />

                {/* Badge Overlay */}
                <div className="absolute top-2 left-2 px-2 py-0.5 rounded bg-black/80 backdrop-blur-md border border-white/10 text-[9px] font-mono font-bold text-white">
                  {currentMode === 'enhanced' ? (
                    <span className="text-amber-400 flex items-center space-x-1">
                      <Sparkles className="w-2.5 h-2.5" />
                      <span>CLOSE-RANGE ENHANCED (MACRO)</span>
                    </span>
                  ) : (
                    <span className="text-slate-400">ORIGINAL RESOLUTION CROP</span>
                  )}
                </div>

                {/* Quick Toggle Controls */}
                <div className="absolute bottom-2 right-2 flex items-center space-x-1.5">
                  <button
                    type="button"
                    onClick={() => toggleViewMode(crop.id)}
                    className="px-2.5 py-1 rounded bg-slate-900/90 hover:bg-slate-800 border border-slate-700 text-[10px] font-mono text-slate-200 shadow-md backdrop-blur-md transition-all flex items-center space-x-1"
                  >
                    <SlidersHorizontal className="w-2.5 h-2.5 text-amber-400" />
                    <span>{currentMode === 'enhanced' ? 'Show Original' : 'Show Enhanced'}</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setSelectedCrop(crop)}
                    className="p-1.5 rounded bg-slate-900/90 hover:bg-slate-800 border border-slate-700 text-slate-200 shadow-md backdrop-blur-md transition-all"
                    title="Inspect Macro (Full View)"
                  >
                    <Maximize2 className="w-3 h-3 text-cyan-400" />
                  </button>
                </div>
              </div>

              {/* Description & Engineering Audit */}
              <p className="text-xs text-slate-300 font-sans leading-relaxed">
                {crop.description}
              </p>

              {/* Footer CTA */}
              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-400">
                <span>Box: [{crop.bounding_box.map((b) => b.toFixed(2)).join(', ')}]</span>
                <button
                  type="button"
                  onClick={() => setSelectedCrop(crop)}
                  className="text-amber-400 hover:text-amber-300 font-bold flex items-center space-x-1 transition-colors"
                >
                  <span>1:1 Diagnostic Zoom</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal for 1:1 Diagnostic Close-Range Inspection */}
      {selectedCrop && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fade-in">
          <div className="relative w-full max-w-4xl bg-slate-950 border border-amber-500/50 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-900/80">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-lg bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400">
                  <Focus className="w-4 h-4 text-amber-400" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wide">
                    {selectedCrop.label} — 1:1 Diagnostic Close-Range Analysis
                  </h3>
                  <span className="text-[11px] text-slate-400 font-mono">
                    {selectedCrop.category} • Detail Gain: +{selectedCrop.detail_gain.toLocaleString()}%
                  </span>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setSelectedCrop(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body: Side-by-Side Close-Range Comparison */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Left: Original Crop */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-400">ORIGINAL DEGRADED CROP</span>
                    <span className="text-slate-500">Unprocessed</span>
                  </div>
                  <div className="h-[340px] bg-slate-900 rounded-xl overflow-hidden border border-slate-800 flex items-center justify-center p-2">
                    <img
                      src={selectedCrop.original_crop_url}
                      alt="Original Crop"
                      className="w-full h-full object-contain"
                    />
                  </div>
                </div>

                {/* Right: Macro Enhanced Crop */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-amber-400 font-bold flex items-center space-x-1">
                      <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                      <span>CLOSE-RANGE ENHANCED MACRO</span>
                    </span>
                    <span className="text-emerald-400 font-bold">Real-ESRGAN + Micro-Detail</span>
                  </div>
                  <div className="h-[340px] bg-slate-900 rounded-xl overflow-hidden border border-amber-500/40 flex items-center justify-center p-2 glow-amber">
                    <img
                      src={selectedCrop.enhanced_crop_url}
                      alt="Enhanced Macro Crop"
                      className="w-full h-full object-contain"
                    />
                  </div>
                </div>
              </div>

              <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 text-xs text-slate-300 font-sans space-y-1.5">
                <span className="font-bold text-white font-mono uppercase text-[11px]">
                  Pattern Diagnostic Notes:
                </span>
                <p>{selectedCrop.description}</p>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-3.5 border-t border-slate-800 bg-slate-900/60 flex items-center justify-end">
              <button
                type="button"
                onClick={() => setSelectedCrop(null)}
                className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-mono font-semibold text-white transition-colors"
              >
                Close Diagnostic View
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
