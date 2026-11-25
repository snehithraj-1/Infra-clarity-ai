export type Severity = 'low' | 'medium' | 'high';

export interface DegradationMetric {
  score: number;
  severity: Severity;
  label: string;
  hint: string;
}

export interface InspectionLoophole {
  id: string;
  title: string;
  severity: Severity;
  category: string;
  vulnerability_in_original: string;
  restoration_fix: string;
  action_required: string;
}

export interface DegradationReport {
  blur: DegradationMetric;
  haze: DegradationMetric;
  noise: DegradationMetric;
  contrast: DegradationMetric;
  resolution_flag: boolean;
  dimensions: [number, number];
  hints: string[];
  loopholes?: InspectionLoophole[];
}

export type PresetName =
  | 'Auto'
  | 'Hazy / Rainy Weather'
  | 'Distant Tower'
  | 'Pipeline Close-up'
  | 'Low Light';

export type StageName = 'dehaze' | 'denoise' | 'deblur' | 'super_resolution';

export interface StageConfig {
  name: StageName;
  enabled: boolean;
  strength: number;
  engine: string;
}

export interface EnhanceOptions {
  preset: PresetName;
  stages?: StageConfig[];
  strip_gps: boolean;
  output_format: 'png' | 'jpeg';
  quality: number;
}

export interface StageProgress {
  stage: string;
  status: 'pending' | 'in_progress' | 'completed' | 'skipped' | 'failed';
  progress: number;
  detail?: string;
}

export interface QualityMetrics {
  detail_gain: number;
  laplacian_gain: number;
  canny_gain: number;
  psnr?: number | null;
  ssim?: number | null;
  niqe?: number | null;
  brisque?: number | null;
  note: string;
}

export interface CloseRangePatternImage {
  id: string;
  label: string;
  category: string;
  description: string;
  bounding_box: [number, number, number, number]; // [ymin, xmin, ymax, xmax] (0.0 - 1.0)
  original_crop_url: string;
  enhanced_crop_url: string;
  detail_gain: number;
  canny_gain: number;
}

export interface JobStatus {
  job_id: string;
  status: 'queued' | 'analyzing' | 'planning' | 'enhancing' | 'completed' | 'failed';
  current_stage?: string;
  progress: number;
  stages: StageProgress[];
  report?: DegradationReport | null;
  metrics?: QualityMetrics | null;
  close_range_images?: CloseRangePatternImage[];
  error?: string | null;
  created_at?: number;
  completed_at?: number;
  result_url?: string | null;
  ai_engine?: string | null;
  ai_analysis?: string | null;
}

export interface Capabilities {
  device: string;
  torch_available: boolean;
  cuda_available: boolean;
  installed_models: Record<string, boolean>;
  available_stages: string[];
}
