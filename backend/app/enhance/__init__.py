from app.enhance.base import Enhancer, soft_clip
from app.enhance.deblur import DeblurStage
from app.enhance.dehaze import DehazeStage
from app.enhance.denoise import DenoiseStage
from app.enhance.registry import StageRegistry, registry
from app.enhance.superres import SuperResStage
from app.enhance.tiling import TiledProcessor

# Register default classical enhancement stages
registry.register(DehazeStage())
registry.register(DenoiseStage())
registry.register(DeblurStage())
registry.register(SuperResStage())

__all__ = [
    "Enhancer",
    "soft_clip",
    "TiledProcessor",
    "StageRegistry",
    "registry",
    "DehazeStage",
    "DenoiseStage",
    "DeblurStage",
    "SuperResStage",
]
