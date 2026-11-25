import { create } from 'zustand';
import {
  DegradationReport,
  EnhanceOptions,
  JobStatus,
  PresetName,
  Severity,
  StageConfig,
  StageName,
} from '../types';

interface EnhanceState {
  originalFile: File | null;
  previewUrl: string | null;
  dimensions: [number, number] | null;
  report: DegradationReport | null;
  isAnalyzing: boolean;
  preset: PresetName;
  stages: StageConfig[];
  stripGps: boolean;
  outputFormat: 'png' | 'jpeg';
  quality: number;
  jobId: string | null;
  jobStatus: JobStatus | null;
  enhancedResultUrl: string | null;
  isEnhancing: boolean;
  error: string | null;

  // Actions
  setOriginalFile: (file: File, previewUrl: string, dims: [number, number]) => void;
  setReport: (report: DegradationReport) => void;
  setIsAnalyzing: (analyzing: boolean) => void;
  setPreset: (preset: PresetName) => void;
  toggleStage: (name: StageName, enabled?: boolean) => void;
  setStageStrength: (name: StageName, strength: number) => void;
  setStripGps: (strip: boolean) => void;
  setOutputFormat: (fmt: 'png' | 'jpeg') => void;
  setQuality: (q: number) => void;
  setJobId: (id: string | null) => void;
  setJobStatus: (status: JobStatus | null) => void;
  setEnhancedResultUrl: (url: string | null) => void;
  setIsEnhancing: (enhancing: boolean) => void;
  setError: (err: string | null) => void;
  reset: () => void;
  getEnhanceOptions: () => EnhanceOptions;
}

const DEFAULT_STAGES: StageConfig[] = [
  { name: 'dehaze', enabled: true, strength: 65, engine: 'guided AI' },
  { name: 'denoise', enabled: true, strength: 60, engine: 'bilateral NLM' },
  { name: 'deblur', enabled: true, strength: 70, engine: 'neural AI' },
  { name: 'super_resolution', enabled: true, strength: 75, engine: 'neural AI' },
];

export const useEnhanceStore = create<EnhanceState>((set, get) => ({
  originalFile: null,
  previewUrl: null,
  dimensions: null,
  report: null,
  isAnalyzing: false,
  preset: 'Auto',
  stages: DEFAULT_STAGES,
  stripGps: true,
  outputFormat: 'png',
  quality: 95,
  jobId: null,
  jobStatus: null,
  enhancedResultUrl: null,
  isEnhancing: false,
  error: null,

  setOriginalFile: (file, previewUrl, dims) => {
    set({
      originalFile: file,
      previewUrl,
      dimensions: dims,
      report: null,
      jobId: null,
      jobStatus: null,
      enhancedResultUrl: null,
      error: null,
    });
  },

  setReport: (report) => {
    // When a report arrives, if preset is Auto, automatically update stage suggestions
    const currentPreset = get().preset;
    let nextStages = [...get().stages];

    if (currentPreset === 'Auto') {
      nextStages = nextStages.map((s) => {
        if (s.name === 'dehaze') {
          return {
            ...s,
            enabled: true,
            strength: report.haze.severity === 'high' ? 75 : 50,
            engine: 'guided AI',
          };
        }
        if (s.name === 'denoise') {
          return {
            ...s,
            enabled: true,
            strength: report.noise.severity === 'high' ? 70 : 55,
            engine: 'bilateral NLM',
          };
        }
        if (s.name === 'deblur') {
          return {
            ...s,
            enabled: true,
            strength: report.blur.severity === 'high' ? 75 : 65,
            engine: 'neural AI',
          };
        }
        if (s.name === 'super_resolution') {
          return {
            ...s,
            enabled: true,
            strength: report.resolution_flag ? 75 : 65,
            engine: 'neural AI',
          };
        }
        return s;
      });
    }

    set({ report, stages: nextStages, isAnalyzing: false });
  },

  setIsAnalyzing: (isAnalyzing) => set({ isAnalyzing }),

  setPreset: (preset) => {
    const report = get().report;
    let nextStages = [...get().stages];

    if (preset === 'Hazy / Rainy Weather') {
      nextStages = [
        { name: 'dehaze', enabled: true, strength: 75, engine: 'guided AI' },
        { name: 'denoise', enabled: true, strength: 50, engine: 'bilateral NLM' },
        { name: 'deblur', enabled: true, strength: 40, engine: 'neural AI' },
        { name: 'super_resolution', enabled: report?.resolution_flag || false, strength: 50, engine: 'neural AI' },
      ];
    } else if (preset === 'Distant Tower') {
      nextStages = [
        { name: 'dehaze', enabled: true, strength: 55, engine: 'guided AI' },
        { name: 'denoise', enabled: true, strength: 35, engine: 'bilateral NLM' },
        { name: 'deblur', enabled: true, strength: 60, engine: 'neural AI' },
        { name: 'super_resolution', enabled: true, strength: 65, engine: 'neural AI' },
      ];
    } else if (preset === 'Pipeline Close-up') {
      nextStages = [
        { name: 'dehaze', enabled: false, strength: 0, engine: 'guided AI' },
        { name: 'denoise', enabled: true, strength: 45, engine: 'bilateral NLM' },
        { name: 'deblur', enabled: true, strength: 75, engine: 'neural AI' },
        { name: 'super_resolution', enabled: report?.resolution_flag || false, strength: 50, engine: 'neural AI' },
      ];
    } else if (preset === 'Low Light') {
      nextStages = [
        { name: 'dehaze', enabled: true, strength: 65, engine: 'guided AI' },
        { name: 'denoise', enabled: true, strength: 70, engine: 'bilateral NLM' },
        { name: 'deblur', enabled: true, strength: 45, engine: 'neural AI' },
        { name: 'super_resolution', enabled: report?.resolution_flag || false, strength: 50, engine: 'neural AI' },
      ];
    } else if (preset === 'Auto' && report) {
      nextStages = [
        {
          name: 'dehaze',
          enabled: true,
          strength: report.haze.severity === 'high' ? 75 : 50,
          engine: 'guided AI',
        },
        {
          name: 'denoise',
          enabled: true,
          strength: report.noise.severity === 'high' ? 70 : 55,
          engine: 'bilateral NLM',
        },
        {
          name: 'deblur',
          enabled: true,
          strength: report.blur.severity === 'high' ? 75 : 65,
          engine: 'neural AI',
        },
        {
          name: 'super_resolution',
          enabled: true,
          strength: report.resolution_flag ? 75 : 65,
          engine: 'neural AI',
        },
      ];
    }

    set({ preset, stages: nextStages });
  },

  toggleStage: (name, enabled) => {
    set((state) => ({
      stages: state.stages.map((s) =>
        s.name === name ? { ...s, enabled: enabled !== undefined ? enabled : !s.enabled } : s
      ),
    }));
  },

  setStageStrength: (name, strength) => {
    set((state) => ({
      stages: state.stages.map((s) => (s.name === name ? { ...s, strength } : s)),
    }));
  },

  setStripGps: (stripGps) => set({ stripGps }),
  setOutputFormat: (outputFormat) => set({ outputFormat }),
  setQuality: (quality) => set({ quality }),
  setJobId: (jobId) => set({ jobId }),
  setJobStatus: (jobStatus) => set({ jobStatus, isEnhancing: jobStatus?.status === 'enhancing' || jobStatus?.status === 'analyzing' || jobStatus?.status === 'planning' }),
  setEnhancedResultUrl: (enhancedResultUrl) => set({ enhancedResultUrl }),
  setIsEnhancing: (isEnhancing) => set({ isEnhancing }),
  setError: (error) => set({ error, isEnhancing: false }),

  reset: () => {
    set({
      originalFile: null,
      previewUrl: null,
      dimensions: null,
      report: null,
      isAnalyzing: false,
      preset: 'Auto',
      stages: DEFAULT_STAGES,
      jobId: null,
      jobStatus: null,
      enhancedResultUrl: null,
      isEnhancing: false,
      error: null,
    });
  },

  getEnhanceOptions: () => {
    const { preset, stages, stripGps, outputFormat, quality } = get();
    return {
      preset,
      stages,
      strip_gps: stripGps,
      output_format: outputFormat,
      quality,
    };
  },
}));
