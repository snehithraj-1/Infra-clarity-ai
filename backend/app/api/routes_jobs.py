import asyncio
import json
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse

from app.jobs.manager import manager
from app.jobs.storage import storage
from app.schemas import JobStatus

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/{job_id}", response_model=JobStatus)
def get_job_status(job_id: str):
    job = manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job


@router.get("/{job_id}/result")
def get_job_result(
    job_id: str,
    format: Optional[str] = Query(None, description="png or jpeg"),
    quality: int = Query(95, ge=1, le=100),
    match_original: bool = Query(False, description="Scale output back to original image dimensions"),
):
    job = manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    if job.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job is in state '{job.status}', result not ready yet",
        )

    result_path = storage.get_result_path(job_id)
    if not result_path or not result_path.is_file():
        raise HTTPException(status_code=404, detail="Result file missing from storage")

    # If requested to match original input image resolution exactly
    if match_original:
        orig_path = storage.get_original_path(job_id)
        if orig_path and orig_path.is_file():
            import cv2
            from fastapi.responses import Response

            orig_img = cv2.imread(str(orig_path))
            res_img = cv2.imread(str(result_path))
            if orig_img is not None and res_img is not None:
                orig_h, orig_w = orig_img.shape[:2]
                res_h, res_w = res_img.shape[:2]
                if (res_h, res_w) != (orig_h, orig_w):
                    res_img = cv2.resize(res_img, (orig_w, orig_h), interpolation=cv2.INTER_AREA)
                    ext = ".jpg" if format == "jpeg" or result_path.suffix.lower() in (".jpg", ".jpeg") else ".png"
                    media_type = "image/jpeg" if ext == ".jpg" else "image/png"
                    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality] if ext == ".jpg" else []
                    success, buffer = cv2.imencode(ext, res_img, encode_params)
                    if success:
                        return Response(
                            content=buffer.tobytes(),
                            media_type=media_type,
                            headers={"Content-Disposition": f'inline; filename="enhanced_{job_id}_matched{ext}"'},
                        )

    media_type = "image/jpeg" if result_path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    return FileResponse(
        path=result_path,
        media_type=media_type,
        filename=f"enhanced_{job_id}{result_path.suffix}",
    )


@router.get("/{job_id}/original")
def get_job_original(job_id: str):
    job = manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    orig_path = storage.get_original_path(job_id)
    if not orig_path or not orig_path.is_file():
        raise HTTPException(status_code=404, detail="Original input image not found")

    media_type = "image/jpeg" if orig_path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    return FileResponse(
        path=orig_path,
        media_type=media_type,
        filename=f"original_{job_id}{orig_path.suffix}",
    )


@router.get("/{job_id}/crops/{crop_id}/original")
def get_job_crop_original(job_id: str, crop_id: str):
    job = manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    crop_path = storage.get_job_dir(job_id) / "crops" / f"{crop_id}_orig.png"
    if not crop_path.is_file():
        raise HTTPException(status_code=404, detail=f"Original crop '{crop_id}' not found")

    return FileResponse(path=crop_path, media_type="image/png", filename=f"{crop_id}_orig.png")


@router.get("/{job_id}/crops/{crop_id}/enhanced")
def get_job_crop_enhanced(job_id: str, crop_id: str):
    job = manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    crop_path = storage.get_job_dir(job_id) / "crops" / f"{crop_id}_enh.png"
    if not crop_path.is_file():
        raise HTTPException(status_code=404, detail=f"Enhanced crop '{crop_id}' not found")

    return FileResponse(path=crop_path, media_type="image/png", filename=f"{crop_id}_enh.png")


@router.get("/{job_id}/events")
async def stream_job_events(job_id: str):
    job = manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    queue = manager.subscribe_events(job_id)

    async def event_generator():
        # First send the initial current state immediately
        initial_payload = {
            "job_id": job.job_id,
            "status": job.status,
            "current_stage": job.current_stage,
            "progress": job.progress,
            "stages": [s.model_dump() for s in job.stages],
            "report": job.report.model_dump() if job.report else None,
            "metrics": job.metrics.model_dump() if job.metrics else None,
            "close_range_images": [c.model_dump() for c in job.close_range_images],
            "error": job.error,
            "result_url": job.result_url,
            "ai_analysis": job.ai_analysis,
            "ai_engine": job.ai_engine,
        }
        yield {"event": "progress", "data": json.dumps(initial_payload)}

        if job.status in ("completed", "failed"):
            return

        try:
            while True:
                # Wait for next event or timeout to send keep-alive ping
                try:
                    event_data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield {"event": "progress", "data": json.dumps(event_data)}
                    if event_data.get("status") in ("completed", "failed"):
                        break
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": "keep-alive"}
        finally:
            manager.unsubscribe_events(job_id, queue)

    return EventSourceResponse(event_generator())
