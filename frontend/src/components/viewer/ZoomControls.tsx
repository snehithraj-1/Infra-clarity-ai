import React from 'react';
import { ZoomIn, ZoomOut, Maximize2, Search, RotateCcw } from 'lucide-react';

interface ZoomControlsProps {
  zoom: number;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onResetZoom: () => void;
  onOneToOne: () => void;
  loupeActive: boolean;
  onToggleLoupe: () => void;
}

export const ZoomControls: React.FC<ZoomControlsProps> = ({
  zoom,
  onZoomIn,
  onZoomOut,
  onResetZoom,
  onOneToOne,
  loupeActive,
  onToggleLoupe,
}) => {
  return (
    <div className="flex items-center space-x-1 bg-white/90 dark:bg-slate-900/90 backdrop-blur border border-slate-200 dark:border-slate-800 rounded-lg p-1 shadow-md text-slate-700 dark:text-slate-300">
      <button
        type="button"
        onClick={onZoomOut}
        title="Zoom Out (or Wheel down)"
        className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded transition-colors"
      >
        <ZoomOut className="w-4 h-4" />
      </button>

      <span className="text-xs font-mono px-1.5 font-semibold text-slate-800 dark:text-slate-200 min-w-[42px] text-center">
        {Math.round(zoom * 100)}%
      </span>

      <button
        type="button"
        onClick={onZoomIn}
        title="Zoom In (or Wheel up)"
        className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded transition-colors"
      >
        <ZoomIn className="w-4 h-4" />
      </button>

      <div className="w-[1px] h-4 bg-slate-200 dark:bg-slate-700 mx-0.5" />

      <button
        type="button"
        onClick={onOneToOne}
        title="1:1 Pixel View"
        className={`px-2 py-1 text-xs font-mono font-bold rounded transition-colors ${
          Math.abs(zoom - 1.0) < 0.05
            ? 'bg-brand-500 text-slate-950'
            : 'hover:bg-slate-100 dark:hover:bg-slate-800'
        }`}
      >
        1:1
      </button>

      <button
        type="button"
        onClick={onResetZoom}
        title="Fit to Container"
        className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded transition-colors"
      >
        <RotateCcw className="w-4 h-4" />
      </button>

      <button
        type="button"
        onClick={onToggleLoupe}
        title={loupeActive ? 'Disable Magnifier Loupe' : 'Enable 3x Magnifier Loupe'}
        className={`p-1.5 rounded transition-colors ${
          loupeActive
            ? 'bg-brand-500 text-slate-950 font-semibold'
            : 'hover:bg-slate-100 dark:hover:bg-slate-800'
        }`}
      >
        <Search className="w-4 h-4" />
      </button>
    </div>
  );
};
