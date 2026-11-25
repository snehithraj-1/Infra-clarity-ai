import React, { useEffect, useRef, useState } from 'react';
import { UploadCloud, Camera, Image as ImageIcon, Sparkles, Loader2 } from 'lucide-react';
import { useEnhanceStore } from '../../store/useEnhanceStore';
import { analyzeImage, fetchInspectionSamples, getSampleImageUrl, InspectionSample } from '../../api/client';

export const UploadZone: React.FC = () => {
  const { setOriginalFile, setReport, setIsAnalyzing, isAnalyzing, setError } = useEnhanceStore();
  const [isDragOver, setIsDragOver] = useState(false);
  const [samples, setSamples] = useState<InspectionSample[]>([]);
  const [loadingSampleId, setLoadingSampleId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchInspectionSamples()
      .then((data) => setSamples(data))
      .catch((err) => console.warn('Could not load inspection samples list:', err));
  }, []);

  const processUploadedFile = async (file: File) => {
    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file (PNG, JPEG, WebP, TIFF).');
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      setError('Selected image exceeds the 50 MB size limit.');
      return;
    }

    try {
      // 1. Create downscaled client preview bitmap to eliminate UI lag on large drone photos
      let previewUrl = '';
      let dims: [number, number] = [0, 0];

      if (typeof window !== 'undefined' && 'createImageBitmap' in window) {
        const bmp = await createImageBitmap(file);
        dims = [bmp.width, bmp.height];

        const maxPreviewSize = 1600;
        let pW = bmp.width;
        let pH = bmp.height;
        if (pW > maxPreviewSize || pH > maxPreviewSize) {
          if (pW > pH) {
            pH = Math.round((pH * maxPreviewSize) / pW);
            pW = maxPreviewSize;
          } else {
            pW = Math.round((pW * maxPreviewSize) / pH);
            pH = maxPreviewSize;
          }
        }

        const canvas = document.createElement('canvas');
        canvas.width = pW;
        canvas.height = pH;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.drawImage(bmp, 0, 0, pW, pH);
          previewUrl = canvas.toDataURL('image/jpeg', 0.92);
        } else {
          previewUrl = URL.createObjectURL(file);
        }
        bmp.close();
      } else {
        previewUrl = URL.createObjectURL(file);
      }

      setOriginalFile(file, previewUrl, dims);
      setIsAnalyzing(true);

      // 2. Immediate async analysis call
      const report = await analyzeImage(file);
      setReport(report);
    } catch (err: any) {
      console.error('Error processing upload:', err);
      setIsAnalyzing(false);
      setError(err.message || 'Failed to analyze inspection image.');
    }
  };

  const handleLoadSample = async (sample: InspectionSample) => {
    setLoadingSampleId(sample.id);
    try {
      const url = getSampleImageUrl(sample.id);
      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to load sample image');
      const blob = await res.blob();
      const file = new File([blob], sample.filename, { type: 'image/png' });
      await processUploadedFile(file);
    } catch (err: any) {
      console.error('Failed to load demo sample:', err);
      setError('Failed to load sample inspection imagery.');
    } finally {
      setLoadingSampleId(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processUploadedFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processUploadedFile(e.target.files[0]);
    }
  };

  return (
    <div className="space-y-6">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-2xl p-8 sm:p-12 text-center transition-all duration-300 cyber-panel overflow-hidden ${
          isDragOver
            ? 'border-amber-400 bg-amber-500/10 scale-[1.01] glow-amber'
            : 'border-slate-800 hover:border-amber-500/40 hover:bg-slate-900/80'
        }`}
      >
        {/* HUD Corner Reticles */}
        <div className="absolute top-3 left-3 text-slate-700 font-mono text-[9px] pointer-events-none select-none">
          [ + ] DROPZONE_INLET
        </div>
        <div className="absolute top-3 right-3 text-slate-700 font-mono text-[9px] pointer-events-none select-none">
          MAX 50MB [ + ]
        </div>
        <div className="absolute bottom-3 left-3 text-slate-700 font-mono text-[9px] pointer-events-none select-none">
          [ + ] AUTO_TILED_INFERENCE
        </div>
        <div className="absolute bottom-3 right-3 text-slate-700 font-mono text-[9px] pointer-events-none select-none">
          MULTI-MODAL READY [ + ]
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/png,image/jpeg,image/webp,image/tiff"
          onChange={handleFileChange}
          className="hidden"
        />
        <input
          ref={cameraInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          onChange={handleFileChange}
          className="hidden"
        />

        <div className="max-w-md mx-auto space-y-4 relative z-10">
          <div className="relative mx-auto w-16 h-16">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-amber-500/20 via-cyan-500/10 to-amber-500/5 border border-amber-500/40 flex items-center justify-center text-amber-400 shadow-xl glow-amber">
              <UploadCloud className="w-8 h-8 text-amber-400" />
            </div>
            <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-cyan-400 cyber-ping" />
          </div>

          <div>
            <h3 className="text-lg font-extrabold text-white tracking-tight">
              Upload Inspection Imagery or Field Notes
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Drag & drop drone captures, telephoto shots, or handwritten calculation sheets
            </p>
          </div>

          <div className="flex items-center justify-center gap-3 pt-2">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="px-5 py-2.5 bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-400 hover:to-amber-300 text-slate-950 rounded-xl text-xs font-bold tracking-wide transition-all shadow-lg glow-amber flex items-center space-x-2"
            >
              <ImageIcon className="w-4 h-4" />
              <span>SELECT IMAGE</span>
            </button>

            <button
              type="button"
              onClick={() => cameraInputRef.current?.click()}
              className="px-4 py-2.5 bg-slate-900/90 text-slate-200 border border-slate-700/80 rounded-xl text-xs font-semibold hover:border-amber-500/50 hover:bg-slate-800 transition-all flex items-center space-x-2"
            >
              <Camera className="w-4 h-4 text-amber-400" />
              <span>CAMERA CAPTURE</span>
            </button>
          </div>

          <div className="flex items-center justify-center space-x-3 text-[11px] text-slate-400 font-mono pt-1">
            <span>50 MB MAX</span>
            <span className="text-slate-700">•</span>
            <span>UP TO 6000×4000</span>
            <span className="text-slate-700">•</span>
            <span>SHOCK PEAKING</span>
          </div>
        </div>
      </div>

      {/* Quick Demo Inspection Gallery */}
      {samples.length > 0 && (
        <div className="cyber-panel rounded-2xl p-5 space-y-4 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <h4 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
                Field Inspection Demo Gallery (1-Click Evaluation)
              </h4>
            </div>
            <span className="text-[10px] font-mono text-cyan-400">
              ⚡ Pre-loaded real inspection degradation telemetry
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {samples.map((s) => (
              <div
                key={s.id}
                onClick={() => handleLoadSample(s)}
                className={`p-3.5 rounded-xl border transition-all text-left cursor-pointer group flex flex-col justify-between space-y-2.5 ${
                  loadingSampleId === s.id
                    ? 'border-amber-500 bg-amber-500/15 glow-amber'
                    : 'border-slate-800/90 bg-slate-900/80 hover:border-amber-500/60 hover:bg-slate-800/80 hover:scale-[1.02]'
                }`}
              >
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 font-bold border border-amber-500/30">
                      {s.asset_type.split(' ')[0]}
                    </span>
                    {loadingSampleId === s.id ? (
                      <Loader2 className="w-3.5 h-3.5 text-amber-400 animate-spin" />
                    ) : (
                      <span className="text-[10px] font-mono text-slate-500 group-hover:text-amber-400 font-bold transition-colors">
                        LOAD →
                      </span>
                    )}
                  </div>
                  <h5 className="text-xs font-bold text-slate-200 group-hover:text-amber-300 line-clamp-1 transition-colors">
                    {s.title}
                  </h5>
                  <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                    {s.description}
                  </p>
                </div>

                <div className="pt-2 border-t border-slate-800 text-[10px] text-amber-400 font-mono flex items-center space-x-1">
                  <span>⚡</span>
                  <span className="line-clamp-1">{s.degradation}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
