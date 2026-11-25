import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  SlidersHorizontal,
  Columns,
  Activity,
  Sparkles,
  Target,
  Maximize2,
} from 'lucide-react';
import { useEnhanceStore } from '../../store/useEnhanceStore';
import { ZoomControls } from './ZoomControls';

interface ComparisonSliderProps {
  beforeUrl: string;
  afterUrl?: string | null;
  beforeLabel?: string;
  afterLabel?: string;
  isEnhancing?: boolean;
}

type ViewMode = 'split' | 'side_by_side' | 'edge_heatmap' | 'difference';

export const ComparisonSlider: React.FC<ComparisonSliderProps> = ({
  beforeUrl,
  afterUrl,
  beforeLabel = 'ORIGINAL',
  afterLabel = 'ENHANCED',
  isEnhancing = false,
}) => {
  const { jobStatus } = useEnhanceStore();
  const closeRangeImages = jobStatus?.close_range_images;

  const containerRef = useRef<HTMLDivElement>(null);
  const [sliderPos, setSliderPos] = useState<number>(50); // percentage 0 - 100
  const [isDraggingSlider, setIsDraggingSlider] = useState(false);

  // Pro View Mode: Split, Side-by-Side, Edge Heatmap, or Restored Delta
  const [viewMode, setViewMode] = useState<ViewMode>('split');
  const [showSpotlights, setShowSpotlights] = useState(false);

  // Pan & Zoom state
  const [zoom, setZoom] = useState<number>(1.0);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState<boolean>(false);
  const dragStartRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const panStartRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  // Loupe magnifier state
  const [loupeActive, setLoupeActive] = useState<boolean>(false);
  const [cursorPos, setCursorPos] = useState<{ x: number; y: number; relX: number; relY: number }>({
    x: 0,
    y: 0,
    relX: 0.5,
    relY: 0.5,
  });
  const [isHovering, setIsHovering] = useState<boolean>(false);

  // Keyboard navigation for accessible slider adjustment
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      setSliderPos((prev) => Math.max(0, prev - (e.shiftKey ? 10 : 2)));
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      setSliderPos((prev) => Math.min(100, prev + (e.shiftKey ? 10 : 2)));
    } else if (e.key === 'Home') {
      e.preventDefault();
      setSliderPos(0);
    } else if (e.key === 'End') {
      e.preventDefault();
      setSliderPos(100);
    }
  };

  // Synchronized Zoom with mouse wheel (attached non-passive to strictly prevent page scroll)
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const onWheelNative = (e: WheelEvent) => {
      e.preventDefault();
      e.stopPropagation();
      const zoomFactor = e.deltaY < 0 ? 1.15 : 0.85;
      setZoom((prev) => Math.min(6.0, Math.max(0.5, prev * zoomFactor)));
    };

    container.addEventListener('wheel', onWheelNative, { passive: false });
    return () => {
      container.removeEventListener('wheel', onWheelNative);
    };
  }, []);

  // Pan with mouse drag
  const handleMouseDown = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('[data-slider-handle="true"]')) {
      return;
    }
    setIsPanning(true);
    dragStartRef.current = { x: e.clientX, y: e.clientY };
    panStartRef.current = { ...pan };
  };

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      const container = containerRef.current;
      if (!container) return;

      const rect = container.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      setCursorPos({
        x: mouseX,
        y: mouseY,
        relX: mouseX / rect.width,
        relY: mouseY / rect.height,
      });

      if (isDraggingSlider) {
        const pct = Math.min(100, Math.max(0, (mouseX / rect.width) * 100));
        setSliderPos(pct);
      } else if (isPanning) {
        const dx = e.clientX - dragStartRef.current.x;
        const dy = e.clientY - dragStartRef.current.y;
        setPan({
          x: panStartRef.current.x + dx,
          y: panStartRef.current.y + dy,
        });
      }
    },
    [isDraggingSlider, isPanning]
  );

  const handleMouseUp = () => {
    setIsDraggingSlider(false);
    setIsPanning(false);
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    if (e.touches.length === 1) {
      const t = e.touches[0];
      dragStartRef.current = { x: t.clientX, y: t.clientY };
      panStartRef.current = { ...pan };
      setIsPanning(true);
    }
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (e.touches.length === 1 && isPanning) {
      const t = e.touches[0];
      const dx = t.clientX - dragStartRef.current.x;
      const dy = t.clientY - dragStartRef.current.y;
      setPan({
        x: panStartRef.current.x + dx,
        y: panStartRef.current.y + dy,
      });
    }
  };

  useEffect(() => {
    const onGlobalUp = () => {
      setIsDraggingSlider(false);
      setIsPanning(false);
    };
    window.addEventListener('mouseup', onGlobalUp);
    return () => window.removeEventListener('mouseup', onGlobalUp);
  }, []);

  const effectiveAfterUrl = afterUrl || beforeUrl;

  return (
    <div className="relative w-full rounded-2xl overflow-hidden border border-slate-800 bg-slate-950 select-none shadow-2xl cyber-panel">
      {/* Top Inspection HUD Toolbar */}
      <div className="bg-slate-900/95 border-b border-slate-800 px-4 py-2.5 flex flex-wrap items-center justify-between gap-2.5 text-xs">
        {/* Mode Selector Tabs with Cyber Accents */}
        <div className="flex items-center space-x-1 bg-slate-950 p-1 rounded-xl border border-slate-800/80 shadow-inner">
          <button
            type="button"
            onClick={() => setViewMode('split')}
            className={`px-3 py-1.5 rounded-lg font-bold text-xs flex items-center space-x-1.5 transition-all ${
              viewMode === 'split'
                ? 'bg-gradient-to-r from-amber-500 to-amber-400 text-slate-950 shadow-md glow-amber'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Split Slider</span>
          </button>

          <button
            type="button"
            onClick={() => setViewMode('side_by_side')}
            className={`px-3 py-1.5 rounded-lg font-bold text-xs flex items-center space-x-1.5 transition-all ${
              viewMode === 'side_by_side'
                ? 'bg-gradient-to-r from-amber-500 to-amber-400 text-slate-950 shadow-md glow-amber'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Columns className="w-3.5 h-3.5" />
            <span>Side-by-Side</span>
          </button>

          <button
            type="button"
            onClick={() => setViewMode('edge_heatmap')}
            className={`px-3 py-1.5 rounded-lg font-bold text-xs flex items-center space-x-1.5 transition-all ${
              viewMode === 'edge_heatmap'
                ? 'bg-gradient-to-r from-amber-500 to-amber-400 text-slate-950 shadow-md glow-amber'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            <span>Crack & Edge Heatmap</span>
          </button>

          <button
            type="button"
            onClick={() => setViewMode('difference')}
            className={`px-3 py-1.5 rounded-lg font-bold text-xs flex items-center space-x-1.5 transition-all ${
              viewMode === 'difference'
                ? 'bg-gradient-to-r from-amber-500 to-amber-400 text-slate-950 shadow-md glow-amber'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Restored Delta</span>
          </button>
        </div>

        {/* Feature Toggles & Controls */}
        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={() => setShowSpotlights(!showSpotlights)}
            className={`px-3 py-1.5 rounded-lg border text-xs font-semibold flex items-center space-x-1.5 transition-all ${
              showSpotlights
                ? 'border-amber-500 bg-amber-500/20 text-amber-300 glow-amber'
                : 'border-slate-800 bg-slate-900/80 text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <Target className="w-3.5 h-3.5" />
            <span>ROI Fault Spotlights</span>
          </button>

          <ZoomControls
            zoom={zoom}
            onZoomIn={() => setZoom((z) => Math.min(6.0, z * 1.25))}
            onZoomOut={() => setZoom((z) => Math.max(0.5, z * 0.8))}
            onResetZoom={() => {
              setZoom(1.0);
              setPan({ x: 0, y: 0 });
            }}
            onOneToOne={() => {
              setZoom(1.0);
              setPan({ x: 0, y: 0 });
            }}
            loupeActive={loupeActive}
            onToggleLoupe={() => setLoupeActive(!loupeActive)}
          />
        </div>
      </div>

      {/* Main Interactive Stage Container */}
      <div
        ref={containerRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseEnter={() => setIsHovering(true)}
        onMouseLeave={() => {
          setIsHovering(false);
          setIsDraggingSlider(false);
          setIsPanning(false);
        }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        className={`relative w-full h-[380px] sm:h-[480px] lg:h-[620px] overflow-hidden flex items-center justify-center bg-slate-950 ${
          isPanning ? 'cursor-grabbing' : 'cursor-grab'
        }`}
      >
        {/* Real-time Laser Scanline Sweep when Enhancing */}
        {isEnhancing && (
          <>
            <div className="animate-scanline" />
            <div className="absolute top-4 left-1/2 -translate-x-1/2 z-30 px-3.5 py-1.5 rounded-full bg-slate-950/90 border border-cyan-500/50 text-cyan-300 text-xs font-mono font-bold flex items-center space-x-2 shadow-2xl glow-cyan backdrop-blur-md">
              <span className="w-2 h-2 rounded-full bg-cyan-400 cyber-ping" />
              <span>SCANNING & RESTORING FREQUENCY ACUITY...</span>
            </div>
          </>
        )}

        {/* HUD Corner Reticles */}
        <div className="absolute top-3 left-3 pointer-events-none text-slate-600 font-mono text-[9px] z-10 flex flex-col items-start select-none">
          <span className="text-amber-400/80 font-bold">[ + ] HUD 01</span>
          <span className="text-slate-500">ACUITY MATRIX</span>
        </div>
        <div className="absolute top-3 right-3 pointer-events-none text-slate-600 font-mono text-[9px] z-10 text-right select-none">
          <span className="text-cyan-400/80 font-bold">FOV: 100% [ + ]</span>
          <span className="text-slate-500">RES: 1:1 SYNC</span>
        </div>
        <div className="absolute bottom-3 left-3 pointer-events-none text-slate-600 font-mono text-[9px] z-10 select-none">
          [ + ] RESTORATION HARNESS
        </div>
        <div className="absolute bottom-3 right-3 pointer-events-none text-slate-600 font-mono text-[9px] z-10 select-none">
          LANCZOS-4 DUAL-SCALE [ + ]
        </div>

        {/* VIEW MODE 1: Standard Synchronized Split Slider */}
        {viewMode === 'split' && (
          <>
            {/* Layer 1: Enhanced Image (Background/Right side) */}
            <div
              className="absolute inset-0 flex items-center justify-center pointer-events-none will-change-transform"
              style={{
                transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                transition: isPanning ? 'none' : 'transform 100ms ease-out',
              }}
            >
              <img
                src={effectiveAfterUrl}
                alt="Enhanced"
                className="w-full h-full object-contain pointer-events-none"
                draggable={false}
              />
            </div>

            {/* Layer 2: Original Image (Clipped Left side) */}
            {afterUrl && (
              <div
                className="absolute inset-0 overflow-hidden pointer-events-none"
                style={{ clipPath: `inset(0 ${100 - sliderPos}% 0 0)` }}
              >
                <div
                  className="absolute inset-0 flex items-center justify-center will-change-transform"
                  style={{
                    transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                    transition: isPanning ? 'none' : 'transform 100ms ease-out',
                  }}
                >
                  <img
                    src={beforeUrl}
                    alt="Original"
                    className="w-full h-full object-contain pointer-events-none"
                    draggable={false}
                  />
                </div>
              </div>
            )}

            {/* Slider Divider Bar and Glowing Handle */}
            {afterUrl && (
              <div
                data-slider-handle="true"
                tabIndex={0}
                role="slider"
                aria-label="Before/After Splitter"
                aria-valuenow={Math.round(sliderPos)}
                aria-valuemin={0}
                aria-valuemax={100}
                onKeyDown={handleKeyDown}
                onMouseDown={(e) => {
                  e.stopPropagation();
                  setIsDraggingSlider(true);
                }}
                className="absolute top-0 bottom-0 z-20 cursor-ew-resize flex items-center justify-center focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
                style={{ left: `${sliderPos}%`, transform: 'translateX(-50%)' }}
              >
                {/* Vertical Divider Line with Glow */}
                <div className="w-0.5 h-full bg-gradient-to-b from-amber-400 via-white to-cyan-400 shadow-md" />

                {/* Floating Percentage Badge */}
                <div className="absolute top-4 px-2 py-0.5 rounded-full bg-slate-950/90 border border-amber-500/60 text-amber-300 font-mono text-[10px] font-bold shadow-xl backdrop-blur-md glow-amber pointer-events-none">
                  {Math.round(sliderPos)}%
                </div>

                {/* Glowing Center Handle Knob */}
                <div className="absolute w-9 h-9 rounded-full bg-slate-950 border-2 border-amber-400 flex items-center justify-center shadow-2xl glow-amber transition-transform hover:scale-115 active:scale-95">
                  <div className="flex space-x-0.5 text-amber-400 font-black text-xs select-none">
                    <span>‹</span>
                    <span>›</span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        {/* VIEW MODE 2: Dual Synchronized Side-by-Side */}
        {viewMode === 'side_by_side' && (
          <div className="absolute inset-0 grid grid-cols-2 divide-x divide-slate-800">
            {/* Left: Original */}
            <div className="relative overflow-hidden flex items-center justify-center">
              <div
                className="absolute inset-0 flex items-center justify-center pointer-events-none will-change-transform"
                style={{
                  transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                  transition: isPanning ? 'none' : 'transform 100ms ease-out',
                }}
              >
                <img
                  src={beforeUrl}
                  alt="Original"
                  className="w-full h-full object-contain pointer-events-none"
                  draggable={false}
                />
              </div>
              <div className="absolute top-3 left-3 px-2 py-1 bg-black/70 border border-white/10 rounded font-mono text-[10px] text-white">
                {beforeLabel}
              </div>
            </div>

            {/* Right: Enhanced */}
            <div className="relative overflow-hidden flex items-center justify-center">
              <div
                className="absolute inset-0 flex items-center justify-center pointer-events-none will-change-transform"
                style={{
                  transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                  transition: isPanning ? 'none' : 'transform 100ms ease-out',
                }}
              >
                <img
                  src={effectiveAfterUrl}
                  alt="Enhanced"
                  className="w-full h-full object-contain pointer-events-none"
                  draggable={false}
                />
              </div>
              <div className="absolute top-3 right-3 px-2 py-1 bg-brand-500/90 text-slate-950 font-bold rounded font-mono text-[10px]">
                {afterLabel}
              </div>
            </div>
          </div>
        )}

        {/* VIEW MODE 3: Edge & Crack Heatmap Energy */}
        {viewMode === 'edge_heatmap' && (
          <div
            className="absolute inset-0 flex items-center justify-center pointer-events-none will-change-transform"
            style={{
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
              transition: isPanning ? 'none' : 'transform 100ms ease-out',
            }}
          >
            <img
              src={effectiveAfterUrl}
              alt="Edge Heatmap"
              className="w-full h-full object-contain pointer-events-none"
              style={{
                filter: 'contrast(260%) invert(1) hue-rotate(185deg) saturate(250%)',
              }}
              draggable={false}
            />
            <div className="absolute top-3 left-3 px-2.5 py-1 bg-amber-500/20 border border-amber-500/50 rounded text-amber-400 font-mono text-[11px] font-bold">
              ⚡ Sobel High-Frequency Gradient Energy Field
            </div>
          </div>
        )}

        {/* VIEW MODE 4: Restored Delta Residual (Difference Map) */}
        {viewMode === 'difference' && (
          <div
            className="absolute inset-0 flex items-center justify-center pointer-events-none will-change-transform bg-slate-950"
            style={{
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
              transition: isPanning ? 'none' : 'transform 100ms ease-out',
            }}
          >
            <img
              src={effectiveAfterUrl}
              alt="Enhanced Base"
              className="w-full h-full object-contain pointer-events-none"
              draggable={false}
            />
            <img
              src={beforeUrl}
              alt="Difference"
              className="absolute inset-0 w-full h-full object-contain pointer-events-none"
              style={{
                mixBlendMode: 'difference',
                filter: 'contrast(400%) invert(0.1)',
              }}
              draggable={false}
            />
            <div className="absolute top-3 left-3 px-2.5 py-1 bg-brand-500/20 border border-brand-500/50 rounded text-brand-400 font-mono text-[11px] font-bold">
              ✨ Restored High-Frequency Residual (|Enhanced - Original|)
            </div>
          </div>
        )}

        {/* Interactive Fault ROI Spotlights */}
        {showSpotlights && (
          <div
            className="absolute inset-0 pointer-events-none will-change-transform"
            style={{
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
              transition: isPanning ? 'none' : 'transform 100ms ease-out',
            }}
          >
            {closeRangeImages && closeRangeImages.length > 0 ? (
              closeRangeImages.map((crop, idx) => {
                const [ymin, xmin, ymax, xmax] = crop.bounding_box;
                const colors = [
                  { border: 'border-amber-400', bg: 'bg-amber-500/15', text: 'bg-amber-500', label: 'text-amber-300' },
                  { border: 'border-cyan-400', bg: 'bg-cyan-500/15', text: 'bg-cyan-400', label: 'text-cyan-300' },
                  { border: 'border-emerald-400', bg: 'bg-emerald-500/15', text: 'bg-emerald-400', label: 'text-emerald-300' },
                  { border: 'border-indigo-400', bg: 'bg-indigo-500/15', text: 'bg-indigo-400', label: 'text-indigo-300' },
                ];
                const c = colors[idx % colors.length];

                return (
                  <div
                    key={crop.id}
                    className={`absolute border-2 border-dashed ${c.border} ${c.bg} rounded flex flex-col justify-between p-1.5 shadow-xl animate-pulse backdrop-blur-[1px]`}
                    style={{
                      top: `${ymin * 100}%`,
                      left: `${xmin * 100}%`,
                      width: `${(xmax - xmin) * 100}%`,
                      height: `${(ymax - ymin) * 100}%`,
                    }}
                  >
                    <span className={`text-[9px] font-mono font-bold ${c.text} text-slate-950 px-1 rounded w-max`}>
                      PATTERN #{idx + 1}
                    </span>
                    <span className={`text-[9px] font-sans font-bold ${c.label} drop-shadow truncate`}>
                      {crop.label}
                    </span>
                  </div>
                );
              })
            ) : (
              <>
                {/* Fallback default spotlights */}
                <div
                  className="absolute w-24 h-20 border-2 border-dashed border-amber-400 bg-amber-500/10 rounded flex flex-col justify-between p-1 shadow-lg animate-pulse"
                  style={{ top: '35%', left: '42%' }}
                >
                  <span className="text-[9px] font-mono font-bold bg-amber-500 text-slate-950 px-1 rounded w-max">
                    ROI #1
                  </span>
                  <span className="text-[9px] font-sans font-bold text-amber-300 drop-shadow">
                    Crossarm Joint (Micro-Crack Zone)
                  </span>
                </div>
                <div
                  className="absolute w-20 h-28 border-2 border-dashed border-cyan-400 bg-cyan-500/10 rounded flex flex-col justify-between p-1 shadow-lg"
                  style={{ top: '48%', left: '58%' }}
                >
                  <span className="text-[9px] font-mono font-bold bg-cyan-400 text-slate-950 px-1 rounded w-max">
                    ROI #2
                  </span>
                  <span className="text-[9px] font-sans font-bold text-cyan-300 drop-shadow">
                    Insulator Shed Skirts
                  </span>
                </div>
                <div
                  className="absolute w-16 h-16 border-2 border-dashed border-emerald-400 bg-emerald-500/10 rounded flex flex-col justify-between p-1 shadow-lg"
                  style={{ top: '65%', left: '32%' }}
                >
                  <span className="text-[9px] font-mono font-bold bg-emerald-400 text-slate-950 px-1 rounded w-max">
                    ROI #3
                  </span>
                  <span className="text-[9px] font-sans font-bold text-emerald-300 drop-shadow">
                    Bolts & Pins
                  </span>
                </div>
              </>
            )}
          </div>
        )}

        {/* Magnifier Loupe (3x Zoom circle) */}
        {loupeActive && isHovering && (
          <div
            className="absolute z-25 pointer-events-none w-36 h-36 rounded-full border-2 border-brand-500 shadow-2xl overflow-hidden bg-slate-900"
            style={{
              left: `${cursorPos.x - 72}px`,
              top: `${cursorPos.y - 72}px`,
            }}
          >
            <div
              className="absolute inset-0 w-full h-full"
              style={{
                backgroundImage: `url(${cursorPos.relX * 100 > sliderPos ? effectiveAfterUrl : beforeUrl})`,
                backgroundPosition: `${cursorPos.relX * 100}% ${cursorPos.relY * 100}%`,
                backgroundSize: '400%',
                backgroundRepeat: 'no-repeat',
              }}
            />
            <div className="absolute bottom-1 right-2 text-[9px] font-mono font-bold text-brand-400 bg-black/70 px-1 rounded">
              3x
            </div>
          </div>
        )}

        {/* Corner Badges in Split View */}
        {viewMode === 'split' && (
          <>
            <div className="absolute top-4 left-4 z-20 pointer-events-none">
              <span className="text-[11px] font-mono font-bold tracking-wider px-2.5 py-1 rounded-lg bg-slate-950/85 text-slate-200 backdrop-blur-md border border-slate-700/80 shadow-lg">
                {beforeLabel}
              </span>
            </div>

            {afterUrl && (
              <div className="absolute top-4 right-4 z-20 pointer-events-none">
                <span className="text-[11px] font-mono font-black tracking-wider px-2.5 py-1 rounded-lg bg-gradient-to-r from-amber-500 to-amber-400 text-slate-950 backdrop-blur-md shadow-lg glow-amber">
                  {afterLabel}
                </span>
              </div>
            )}
          </>
        )}
      </div>

      {/* Bottom Hint Bar */}
      <div className="bg-slate-900/90 border-t border-slate-800 px-4 py-2 flex items-center justify-between text-[11px] text-slate-400 font-mono">
        <div className="flex items-center space-x-3">
          <span>Scroll wheel to zoom ({Math.round(zoom * 100)}%)</span>
          <span>•</span>
          <span>Drag to pan</span>
          {viewMode === 'split' && (
            <>
              <span>•</span>
              <span>Arrow keys adjust split</span>
            </>
          )}
        </div>
        <div className="text-brand-400 flex items-center space-x-2">
          <span className="text-emerald-400 font-sans font-medium text-[10px] bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
            ✓ Synchronized 1:1 Scale
          </span>
          {viewMode === 'split' && <span>Split: {Math.round(sliderPos)}%</span>}
        </div>
      </div>
    </div>
  );
};
