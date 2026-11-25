import os
from pathlib import Path
from typing import Any, Dict
import yaml
from pydantic import BaseModel, Field


class AppMeta(BaseModel):
    name: str = "InfraClarity AI"
    version: str = "1.0.0"
    description: str = "Infrastructure Inspection Image Enhancer"


class BlurConfig(BaseModel):
    severe_threshold: float = 60.0
    moderate_threshold: float = 180.0


class HazeConfig(BaseModel):
    severe_threshold: float = 0.35
    moderate_threshold: float = 0.18


class NoiseConfig(BaseModel):
    severe_threshold: float = 8.0
    moderate_threshold: float = 2.5


class ContrastConfig(BaseModel):
    severe_threshold: float = 0.15
    moderate_threshold: float = 0.28


class ResolutionConfig(BaseModel):
    min_shorter_side: int = 1080


class AnalysisThresholds(BaseModel):
    blur: BlurConfig = Field(default_factory=BlurConfig)
    haze: HazeConfig = Field(default_factory=HazeConfig)
    noise: NoiseConfig = Field(default_factory=NoiseConfig)
    contrast: ContrastConfig = Field(default_factory=ContrastConfig)
    resolution: ResolutionConfig = Field(default_factory=ResolutionConfig)


class TilingConfig(BaseModel):
    tile_size: int = 512
    overlap: int = 32
    max_dimension: int = 6000
    min_tile_size: int = 256


class StorageConfig(BaseModel):
    jobs_dir: str = "backend/data/jobs"
    max_upload_size_mb: int = 50
    cleanup_interval_seconds: int = 600
    job_ttl_seconds: int = 3600
    strip_gps_default: bool = True


class ModelsConfig(BaseModel):
    weights_dir: str = "backend/weights"
    device: str = "auto"


class AppConfig(BaseModel):
    app: AppMeta = Field(default_factory=AppMeta)
    analysis: AnalysisThresholds = Field(default_factory=AnalysisThresholds)
    tiling: TilingConfig = Field(default_factory=TilingConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    models: ModelsConfig = Field(default_factory=ModelsConfig)


def find_config_path() -> Path:
    candidates = [
        Path(os.environ.get("INFRACLARITY_CONFIG", "")),
        Path("config.yaml"),
        Path("backend/config.yaml"),
        Path(__file__).resolve().parent.parent / "config.yaml",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return Path(__file__).resolve().parent.parent / "config.yaml"


def load_config() -> AppConfig:
    config_path = find_config_path()
    if not config_path.is_file():
        return AppConfig()
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = yaml.safe_load(f) or {}
        return AppConfig(**data)
    except Exception:
        return AppConfig()


config = load_config()
