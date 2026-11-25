import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import logging
import os
import time
import uuid
from typing import Any, AsyncGenerator, Dict, List, Optional
import httpx
import cv2
import numpy as np

from app.analysis.degradation import analyze_degradations
from app.config import config
from app.enhance.registry import registry
from app.enhance.tiling import TiledProcessor
from app.jobs.storage import storage
from app.metrics.quality import compute_metrics
from app.planner.planner import create_pipeline_plan
from app.schemas import (
    CloseRangePatternImage,
    DegradationReport,
    EnhanceOptions,
    JobStatus,
    PresetName,
    QualityMetrics,
    StageName,
    StageProgress,
)

logger = logging.getLogger("infraclarity.jobs")


class JobManager:
    """
    Asynchronous job coordinator using a background thread pool and SSE event streams.
    Executes the full pipeline: Upload -> Analysis -> Planning -> Tiled Enhancement -> Metrics.
    """

    def __init__(self, max_workers: int = 2):
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="EnhanceWorker")
        self._jobs: Dict[str, JobStatus] = {}
        self._event_queues: Dict[str, List[asyncio.Queue]] = {}
        self._tiled_processor = TiledProcessor(
            tile_size=config.tiling.tile_size,
            overlap=config.tiling.overlap,
            min_tile_size=config.tiling.min_tile_size,
        )

    def create_job(self, options: Optional[EnhanceOptions] = None) -> str:
        job_id = str(uuid.uuid4())
        initial_status = JobStatus(
            job_id=job_id,
            status="queued",
            current_stage="queued",
            progress=0.0,
            stages=[],
            created_at=time.time(),
        )
        self._jobs[job_id] = initial_status
        self._event_queues[job_id] = []
        logger.info(f"[{job_id}] Created enhancement job with preset: {options.preset.value if options else 'Auto'}")
        return job_id

    def get_job(self, job_id: str) -> Optional[JobStatus]:
        return self._jobs.get(job_id)

    def _broadcast_event(self, job_id: str, event_data: dict) -> None:
        queues = self._event_queues.get(job_id, [])
        for q in list(queues):
            try:
                q.put_nowait(event_data)
            except Exception:
                pass

    def subscribe_events(self, job_id: str) -> asyncio.Queue:
        if job_id not in self._event_queues:
            self._event_queues[job_id] = []
        q: asyncio.Queue = asyncio.Queue()
        self._event_queues[job_id].append(q)
        return q

    def unsubscribe_events(self, job_id: str, q: asyncio.Queue) -> None:
        if job_id in self._event_queues:
            try:
                self._event_queues[job_id].remove(q)
            except ValueError:
                pass

    def submit_job(self, job_id: str, options: EnhanceOptions) -> None:
        loop = asyncio.get_event_loop()
        self.executor.submit(self._run_job_sync, job_id, options, loop)

    def _update_progress(
        self,
        job_id: str,
        loop: asyncio.AbstractEventLoop,
        status: str,
        current_stage: Optional[str] = None,
        progress: float = 0.0,
        stages: Optional[List[StageProgress]] = None,
        report: Optional[DegradationReport] = None,
        metrics: Optional[QualityMetrics] = None,
        close_range_images: Optional[List[CloseRangePatternImage]] = None,
        error: Optional[str] = None,
        result_url: Optional[str] = None,
        ai_analysis: Optional[str] = None,
        ai_engine: Optional[str] = None,
    ) -> None:
        job = self._jobs.get(job_id)
        if not job:
            return

        job.status = status  # type: ignore
        job.progress = round(float(np.clip(progress, 0.0, 1.0)), 3)
        if current_stage is not None:
            job.current_stage = current_stage
        if stages is not None:
            job.stages = stages
        if report is not None:
            job.report = report
        if metrics is not None:
            job.metrics = metrics
        if close_range_images is not None:
            job.close_range_images = close_range_images
        if error is not None:
            job.error = error
        if result_url is not None:
            job.result_url = result_url
            job.completed_at = time.time()
        if ai_analysis is not None:
            job.ai_analysis = ai_analysis
        if ai_engine is not None:
            job.ai_engine = ai_engine

        event_payload = {
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

        if loop is not None and not loop.is_closed():
            try:
                loop.call_soon_threadsafe(self._broadcast_event, job_id, event_payload)
            except RuntimeError:
                pass

    def _run_job_sync(
        self,
        job_id: str,
        options: EnhanceOptions,
        loop: asyncio.AbstractEventLoop,
    ) -> None:
        logger.info(f"[{job_id}] Starting processing pipeline")
        try:
            # 1. Load original image
            original_float, source_path = storage.load_original_as_float(job_id)
            h, w = original_float.shape[:2]

            # 2. Degradation Analysis
            self._update_progress(job_id, loop, status="analyzing", current_stage="Analyzing degradation & optical telemetry", progress=0.05)
            report = analyze_degradations(original_float, config)
            logger.info(f"[{job_id}] Analysis complete: blur={report.blur.severity.value}, haze={report.haze.severity.value}, noise={report.noise.severity.value}")

            # 2.5 Gemini AI Scene & Restoration Analysis & Automated Pipeline Planning
            self._update_progress(job_id, loop, status="analyzing", current_stage="Gemini AI analyzing scene & prescribing plan", progress=0.08, report=report)
            gemini_analysis: Optional[str] = None
            gemini_engine: str = "gemini-flash-lite-latest"
            gemini_plan: Optional[Dict[str, Any]] = None
            gemini_key = os.environ.get("GEMINI_API_KEY", "")

            try:
                gemini_prompt = (
                    f"You are InfraClarity AI, an elite infrastructure inspection and image restoration AI. "
                    f"Optical Telemetry for inspection image ({w}x{h}px): "
                    f"Blur score={report.blur.score:.1f} ({report.blur.severity.value}), "
                    f"Airlight Haze={report.haze.score:.3f} ({report.haze.severity.value}), "
                    f"Noise Sigma={report.noise.score:.2f} ({report.noise.severity.value}), "
                    f"RMS Contrast={report.contrast.score:.3f} ({report.contrast.severity.value}). "
                    f"Task: 1. Identify what equipment or structures are in the scene. "
                    f"2. Audit hidden loopholes, micro-cracks, corrosion, or blindspots masked by blur/haze. "
                    f"3. Prescribe optimal enhancement parameters for a close-range, noise-free, fog-free crystal-clear view (all 4 stages 'dehaze', 'denoise', 'deblur', 'super_resolution' must have 'enabled': true). "
                    f"Respond in valid JSON format with keys: "
                    f"'scene_analysis' (string: 2 sentences describing the asset and scene), "
                    f"'blindspot_audit' (string: 2 sentences auditing masked defects or loopholes), "
                    f"'plan' (object with keys 'dehaze', 'denoise', 'deblur', 'super_resolution', each having 'enabled' bool and 'strength' 40-100 int)."
                )
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={gemini_key}"
                payload = {
                    "contents": [{"parts": [{"text": gemini_prompt}]}],
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "temperature": 0.2,
                    },
                }
                with httpx.Client(timeout=12.0) as http_client:
                    res = http_client.post(url, json=payload)
                    if res.status_code == 200:
                        raw_json_str = res.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        parsed_ai = json.loads(raw_json_str)
                        scene_txt = parsed_ai.get("scene_analysis")
                        if isinstance(scene_txt, dict):
                            scene_txt = scene_txt.get("assessment") or str(scene_txt)
                        audit_txt = parsed_ai.get("blindspot_audit")
                        if isinstance(audit_txt, dict):
                            audit_txt = audit_txt.get("recommendation") or str(audit_txt)
                        gemini_plan = parsed_ai.get("plan")
                        gemini_analysis = (
                            f"🔍 **Gemini Scene Identification**: {scene_txt}\n\n"
                            f"⚠️ **Loophole & Blindspot Audit**: {audit_txt}"
                        )
                        logger.info(f"[{job_id}] Gemini AI generated plan & analysis successfully")
            except Exception as e:
                logger.warning(f"[{job_id}] Gemini live scene analysis fallback: {e}")
                gemini_engine = "expert-heuristic"

            if not gemini_analysis:
                gemini_analysis = (
                    f"🔍 **Scene Analysis**: {w}x{h}px infrastructure frame under field inspection. "
                    f"Optical telemetry confirms {report.blur.severity.value.upper()} blur ({report.blur.score:.1f}) and {report.haze.severity.value.upper()} haze ({report.haze.score:.3f}).\n\n"
                    f"⚠️ **Loophole Audit**: Heavy optical scatter obscures fine surface detail, masking potential hairline cracks and joint fastener looseness. "
                    f"Luminance shock peaking and dehazing recover micro-edge definition."
                )

            # 3. Pipeline Planning
            self._update_progress(job_id, loop, status="planning", current_stage="Planning enhancement stages with Gemini AI", progress=0.10, report=report, ai_analysis=gemini_analysis, ai_engine=gemini_engine)
            plan = create_pipeline_plan(report, options)

            # If Gemini prescribed a plan and preset is Auto, apply Gemini's intelligent tuning
            if gemini_plan and options.preset == PresetName.AUTO:
                for stage in plan.stages:
                    s_name = stage.name.value
                    if s_name in gemini_plan and isinstance(gemini_plan[s_name], dict):
                        g_conf = gemini_plan[s_name]
                        # All 4 core stages are enforced to TRUE for close-range noise-free clarity
                        stage.enabled = True
                        if "strength" in g_conf and not any(o.name.value == s_name for o in (options.stages or [])):
                            stage.strength = int(np.clip(float(g_conf["strength"]), 40, 100))
                            stage.reason = f"Gemini AI prescribed strength ({stage.strength}%) based on optical telemetry"

            # In AUTO preset, enforce full-spectrum close-range clarity (all 4 stages active to eliminate all noise & fog)
            if options.preset == PresetName.AUTO:
                for stage in plan.stages:
                    stage.enabled = True

            active_stages = [s for s in plan.stages if s.enabled]

            stage_progress_list = [
                StageProgress(
                    stage=s.name.value,
                    status="pending" if s.enabled else "skipped",
                    progress=0.0,
                    detail=s.reason,
                )
                for s in plan.stages
            ]
            self._update_progress(job_id, loop, status="enhancing", current_stage="Preparing stages", progress=0.15, stages=stage_progress_list)

            # 4. Sequential Enhancement via Tiled Processor
            current_image = original_float.copy()
            num_active = len(active_stages)

            for stage_idx, planned_stage in enumerate(active_stages):
                stage_name_str = planned_stage.name.value
                stage_instance = registry.get_stage(stage_name_str)
                if not stage_instance or not stage_instance.is_available:
                    continue

                # Mark stage in progress
                for sp in stage_progress_list:
                    if sp.stage == stage_name_str:
                        sp.status = "in_progress"
                        sp.progress = 0.0

                stage_base_progress = 0.15 + (stage_idx / max(1, num_active)) * 0.70
                stage_weight = 0.70 / max(1, num_active)

                def tile_callback(cur_tile: int, tot_tiles: int, msg: str):
                    tile_frac = cur_tile / max(1, tot_tiles)
                    overall = stage_base_progress + tile_frac * stage_weight
                    for sp in stage_progress_list:
                        if sp.stage == stage_name_str:
                            sp.progress = round(tile_frac, 2)
                    self._update_progress(
                        job_id,
                        loop,
                        status="enhancing",
                        current_stage=f"{stage_name_str.replace('_', ' ').title()} ({cur_tile}/{tot_tiles})",
                        progress=overall,
                        stages=stage_progress_list,
                    )

                logger.info(f"[{job_id}] Executing stage: {stage_name_str} (strength={planned_stage.strength})")

                # Run through tiled processor
                if planned_stage.name == StageName.SUPER_RESOLUTION:
                    # When sub-1080p, determine appropriate magnification scale
                    shorter_side = min(h, w)
                    if shorter_side < 400:
                        computed_scale = 4.0
                    elif shorter_side < 1080:
                        computed_scale = 2.0
                    else:
                        computed_scale = 1.0

                    if hasattr(options, "scale") and options.scale > 1.0:
                        scale = options.scale
                    elif not getattr(options, "match_original_resolution", False) or report.resolution_flag:
                        scale = computed_scale
                    else:
                        scale = 1.0

                    current_image = self._tiled_processor.process(
                        current_image,
                        lambda t, s=stage_instance: s.run(t, strength=planned_stage.strength, scale=scale),
                        progress_callback=tile_callback,
                        scale=scale,
                    )
                else:
                    blur_score = report.blur.score if planned_stage.name == StageName.DEBLUR else None
                    current_image = self._tiled_processor.process(
                        current_image,
                        lambda t, s=stage_instance: s.run(t, strength=planned_stage.strength, blur_score=blur_score),
                        progress_callback=tile_callback,
                    )

                # Mark stage completed
                for sp in stage_progress_list:
                    if sp.stage == stage_name_str:
                        sp.status = "completed"
                        sp.progress = 1.0

            # Ensure final output matches original dimensions only if explicitly required and super_res didn't upscale
            if getattr(options, "match_original_resolution", False) and not report.resolution_flag:
                if (current_image.shape[0], current_image.shape[1]) != (h, w):
                    current_image = cv2.resize(current_image, (w, h), interpolation=cv2.INTER_AREA)

            # 5. Compute Quality Metrics
            self._update_progress(job_id, loop, status="enhancing", current_stage="Calculating quality metrics", progress=0.90, stages=stage_progress_list)
            metrics = compute_metrics(original_float, current_image)
            logger.info(f"[{job_id}] Metrics: detail_gain={metrics.detail_gain}%, canny_gain={metrics.canny_gain}%")

            # 6. Save Enhanced Output
            self._update_progress(job_id, loop, status="enhancing", current_stage="Saving enhanced image", progress=0.94)
            out_path = storage.save_result(
                job_id,
                current_image,
                output_format=options.output_format,
                quality=options.quality,
                strip_gps=options.strip_gps,
                source_image_path=source_path,
            )

            # 6.5 Generate Pattern-Understood Close-Range Macro Enhanced Imagery
            self._update_progress(job_id, loop, status="enhancing", current_stage="Generating close-range pattern enhancements", progress=0.97)
            close_range_list: List[CloseRangePatternImage] = []
            try:
                from app.analysis.patterns import generate_close_range_pattern_images
                crops_dir = storage.get_job_dir(job_id) / "crops"
                superres_inst = registry.get_stage(StageName.SUPER_RESOLUTION.value)
                close_range_list = generate_close_range_pattern_images(
                    job_id=job_id,
                    original_image=original_float,
                    enhanced_image=current_image,
                    crops_dir=crops_dir,
                    report=report,
                    superres_stage=superres_inst,
                )
                logger.info(f"[{job_id}] Generated {len(close_range_list)} close-range pattern enhanced images")
            except Exception as e:
                logger.warning(f"[{job_id}] Close-range pattern generation fallback: {e}")

            result_url = f"/api/v1/jobs/{job_id}/result"
            self._update_progress(
                job_id,
                loop,
                status="completed",
                current_stage="Complete",
                progress=1.0,
                stages=stage_progress_list,
                metrics=metrics,
                close_range_images=close_range_list,
                result_url=result_url,
            )
            logger.info(f"[{job_id}] Enhancement pipeline completed successfully -> {out_path.name}")

        except Exception as e:
            logger.error(f"[{job_id}] Enhancement pipeline failed: {e}", exc_info=True)
            self._update_progress(
                job_id,
                loop,
                status="failed",
                current_stage="Failed",
                progress=1.0,
                error=str(e),
            )


manager = JobManager()
