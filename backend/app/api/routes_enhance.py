import json
from typing import Optional
import cv2
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
import numpy as np
from PIL import Image

from app.analysis.degradation import analyze_degradations
from app.config import config
from app.jobs.manager import manager
from app.jobs.storage import storage
from app.schemas import DegradationReport, EnhanceOptions

router = APIRouter(tags=["Enhancement"])

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/tiff",
    "image/bmp",
}
MAX_FILE_BYTES = config.storage.max_upload_size_mb * 1024 * 1024


def validate_image_file(file: UploadFile, contents: bytes) -> None:
    if len(contents) > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Image size exceeds maximum limit of {config.storage.max_upload_size_mb} MB",
        )
    if file.content_type and file.content_type.lower() not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}. Supported types: PNG, JPEG, WebP, TIFF.",
        )
    # Validate image can be parsed by PIL
    try:
        from io import BytesIO
        with Image.open(BytesIO(contents)) as img:
            img.verify()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Uploaded file is corrupted or not a valid image: {e}",
        )


@router.post("/enhance")
async def create_enhance_job(
    image: UploadFile = File(...),
    options: Optional[str] = Form(None),
):
    contents = await image.read()
    validate_image_file(image, contents)

    # Parse JSON options if provided
    parsed_options = EnhanceOptions()
    if options:
        try:
            opts_dict = json.loads(options)
            parsed_options = EnhanceOptions(**opts_dict)
        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid JSON in 'options' parameter: {e}",
            )

    job_id = manager.create_job(parsed_options)
    from pathlib import Path
    ext = Path(image.filename or "image.png").suffix or ".png"
    storage.save_original(job_id, contents, filename=f"original{ext}")
    manager.submit_job(job_id, parsed_options)

    return {"job_id": job_id, "status": "queued"}


@router.post("/analyze", response_model=DegradationReport)
async def analyze_image(
    image: UploadFile = File(...),
):
    contents = await image.read()
    validate_image_file(image, contents)

    from io import BytesIO
    with Image.open(BytesIO(contents)) as pil_img:
        rgb_img = pil_img.convert("RGB")
        img_arr = np.array(rgb_img, dtype=np.float32) / 255.0

    report = analyze_degradations(img_arr, config)
    return report
