from enum import Enum
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DegradationMetric(BaseModel):
    score: float
    severity: Severity
    label: str
    hint: str


class InspectionLoophole(BaseModel):
    id: str
    title: str
    severity: Severity
    category: str
    vulnerability_in_original: str
    restoration_fix: str
    action_required: str


class DegradationReport(BaseModel):
    blur: DegradationMetric
    haze: DegradationMetric
    noise: DegradationMetric
    contrast: DegradationMetric
    resolution_flag: bool
    dimensions: List[int] = Field(description="[width, height]")
    hints: List[str]
    loopholes: List[InspectionLoophole] = Field(default_factory=list)


class PresetName(str, Enum):
    AUTO = "Auto"
    HAZY_RAINY = "Hazy / Rainy Weather"
    DISTANT_TOWER = "Distant Tower"
    PIPELINE_CLOSEUP = "Pipeline Close-up"
    LOW_LIGHT = "Low Light"


class StageName(str, Enum):
    DEHAZE = "dehaze"
    DENOISE = "denoise"
    DEBLUR = "deblur"
    SUPER_RESOLUTION = "super_resolution"


class StageConfig(BaseModel):
    name: StageName
    enabled: bool = True
    strength: int = Field(default=50, ge=0, le=100)
    engine: str = Field(default="classical", description="classical or deep model")


class EnhanceOptions(BaseModel):
    preset: PresetName = PresetName.AUTO
    stages: Optional[List[StageConfig]] = None
    strip_gps: bool = True
    output_format: Literal["png", "jpeg"] = "png"
    quality: int = Field(default=95, ge=1, le=100)
    match_original_resolution: bool = Field(default=False, description="Strictly force output image dimensions to match original input dimensions, disabling upscaling")
    scale: float = Field(default=1.0, ge=1.0, le=4.0)


class StageProgress(BaseModel):
    stage: str
    status: Literal["pending", "in_progress", "completed", "skipped", "failed"]
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    detail: Optional[str] = None


class QualityMetrics(BaseModel):
    detail_gain: float = Field(description="Percentage increase in edge detail proxy")
    laplacian_gain: float = Field(description="Percentage change in high-frequency Laplacian variance")
    canny_gain: float = Field(description="Percentage change in Canny edge density")
    psnr: Optional[float] = None
    ssim: Optional[float] = None
    niqe: Optional[float] = None
    brisque: Optional[float] = None
    note: str = "Proxy for fault visibility, not a detection accuracy claim."


class CloseRangePatternImage(BaseModel):
    id: str
    label: str
    category: str
    description: str
    bounding_box: List[float] = Field(description="[ymin, xmin, ymax, xmax] normalized (0.0 to 1.0)")
    original_crop_url: str
    enhanced_crop_url: str
    detail_gain: float
    canny_gain: float


class JobStatus(BaseModel):
    job_id: str
    status: Literal["queued", "analyzing", "planning", "enhancing", "completed", "failed"]
    current_stage: Optional[str] = None
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    stages: List[StageProgress] = Field(default_factory=list)
    report: Optional[DegradationReport] = None
    metrics: Optional[QualityMetrics] = None
    close_range_images: List[CloseRangePatternImage] = Field(default_factory=list)
    error: Optional[str] = None
    created_at: float
    completed_at: Optional[float] = None
    result_url: Optional[str] = None
    ai_engine: Optional[str] = "Gemini Flash (gemini-flash-lite-latest)"
    ai_analysis: Optional[str] = None


class Capabilities(BaseModel):
    device: str
    torch_available: bool
    cuda_available: bool
    installed_models: Dict[str, bool]
    available_stages: List[str]
