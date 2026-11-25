import os
from pathlib import Path
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.config import config
from app.enhance.registry import registry
from app.schemas import Capabilities

router = APIRouter(tags=["Metadata"])

SAMPLES: List[Dict[str, Any]] = [
    {
        "id": "tower_combined",
        "title": "500kV Transmission Tower Crossarm",
        "asset_type": "Lattice Steel Transmission Tower",
        "degradation": "Severe Motion Blur & Atmospheric Haze",
        "description": "High-altitude aerial capture of crossarm lattice joint degraded by drone vibration and heavy morning fog.",
        "filename": "tower_joint_combined.png",
    },
    {
        "id": "insulator_blur",
        "title": "Suspension Insulator String",
        "asset_type": "Cap-and-Pin Glass Insulator Assembly",
        "degradation": "High-Speed Camera Defocus & Blur",
        "description": "Close-up telephoto inspection of insulator bells with obscured shed skirts and washed-out hardware.",
        "filename": "insulator_string_blur.png",
    },
    {
        "id": "pipeline_haze",
        "title": "High-Pressure Gas Pipeline Weld",
        "asset_type": "API 5L Carbon Steel Pipeline",
        "degradation": "Dense Weather Haze & Contrast Loss",
        "description": "Right-of-way aerial inspection showing surface girth weld obscured by dust, haze, and low dynamic range.",
        "filename": "pipeline_weld_haze.png",
    },
    {
        "id": "tower_haze",
        "title": "Lattice Tower Joint Assembly",
        "asset_type": "Bolted Angle Bracing & Fasteners",
        "degradation": "Airlight Scatter & Low Contrast",
        "description": "Telephoto view of diagonal lattice bracing showing washed-out bolt connections and fastener relief.",
        "filename": "tower_joint_haze.png",
    },
]


@router.get("/health")
def get_health():
    return {
        "status": "ok",
        "app": config.app.name,
        "version": config.app.version,
    }


@router.get("/capabilities", response_model=Capabilities)
def get_capabilities():
    torch_available = False
    cuda_available = False
    device = "cpu"

    try:
        import torch
        torch_available = True
        cuda_available = torch.cuda.is_available()
        device = "cuda" if cuda_available else "cpu"
    except ImportError:
        pass

    weights_dir = Path(config.models.weights_dir)
    if not weights_dir.is_dir():
        weights_dir = Path(__file__).resolve().parent.parent.parent / "weights"

    installed_models = {
        "nafnet_denoise": (weights_dir / "nafnet_denoise.pth").is_file(),
        "nafnet_deblur": (weights_dir / "nafnet_deblur.pth").is_file(),
        "realesrgan_x4": (weights_dir / "realesrgan_x4.pth").is_file() or (weights_dir / "realesr-general-x4v3.pth").is_file(),
    }

    available_stages = list(registry.list_available().keys())

    return Capabilities(
        device=device,
        torch_available=torch_available,
        cuda_available=cuda_available,
        installed_models=installed_models,
        available_stages=available_stages,
    )


@router.get("/samples")
def get_inspection_samples():
    return SAMPLES


@router.get("/samples/{sample_id}/image")
def get_sample_image(sample_id: str):
    match = next((s for s in SAMPLES if s["id"] == sample_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Sample not found")

    sample_dir = Path(__file__).resolve().parent.parent.parent.parent / "samples" / "degraded"
    file_path = sample_dir / match["filename"]
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Sample image file not found")

    return FileResponse(path=file_path, media_type="image/png", filename=match["filename"])
