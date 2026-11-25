import io
import os
import shutil
import time
from pathlib import Path
from typing import Optional, Tuple
import cv2
import numpy as np
from PIL import Image

from app.config import config


class JobStorage:
    """
    Manages local filesystem storage for uploaded inspection imagery and enhanced results.
    Automatically purges expired jobs older than 1 hour.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or config.storage.jobs_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_job_dir(self, job_id: str) -> Path:
        job_dir = self.base_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir

    def save_original(self, job_id: str, file_bytes: bytes, filename: str = "original.png") -> Path:
        job_dir = self.get_job_dir(job_id)
        from PIL import Image, ImageOps
        import io
        try:
            with Image.open(io.BytesIO(file_bytes)) as pil_img:
                transposed = ImageOps.exif_transpose(pil_img)
                ext = Path(filename).suffix.lower()
                clean_name = f"original{ext if ext in ('.jpg', '.jpeg', '.png') else '.png'}"
                file_path = job_dir / clean_name
                if ext in ('.jpg', '.jpeg'):
                    transposed.save(file_path, format="JPEG", quality=98)
                else:
                    transposed.save(file_path, format="PNG")
                return file_path
        except Exception:
            file_path = job_dir / filename
            with open(file_path, "wb") as f:
                f.write(file_bytes)
            return file_path

    def load_original_as_float(self, job_id: str) -> Tuple[np.ndarray, Path]:
        job_dir = self.get_job_dir(job_id)
        candidates = list(job_dir.glob("original.*"))
        if not candidates:
            # Fallback to any image that is not result.*
            all_files = [f for f in job_dir.iterdir() if f.is_file() and not f.name.startswith("result.")]
            if all_files:
                candidates = all_files
        if not candidates:
            raise FileNotFoundError(f"Original image not found for job {job_id}")
        file_path = candidates[0]

        from PIL import Image, ImageOps
        # Read with PIL and ensure orientation is normalized
        with Image.open(file_path) as pil_img:
            transposed = ImageOps.exif_transpose(pil_img)
            pil_rgb = transposed.convert("RGB")
            arr = np.array(pil_rgb, dtype=np.float32) / 255.0
        return arr, file_path

    def save_result(
        self,
        job_id: str,
        image_float: np.ndarray,
        output_format: str = "png",
        quality: int = 95,
        strip_gps: bool = True,
        source_image_path: Optional[Path] = None,
    ) -> Path:
        job_dir = self.get_job_dir(job_id)
        ext = "jpg" if output_format.lower() in ("jpg", "jpeg") else "png"
        out_path = job_dir / f"result.{ext}"

        u8_arr = (np.clip(image_float, 0.0, 1.0) * 255.0).astype(np.uint8)
        pil_img = Image.fromarray(u8_arr)

        # Handle EXIF metadata copying and GPS stripping
        exif = None
        if source_image_path and source_image_path.is_file():
            try:
                with Image.open(source_image_path) as src_pil:
                    src_exif = src_pil.getexif()
                    if src_exif:
                        if strip_gps:
                            # 34853 is the EXIF GPSInfo IFD tag ID
                            if 34853 in src_exif:
                                del src_exif[34853]
                        exif = src_exif
            except Exception:
                exif = None

        save_kwargs = {}
        if ext == "jpg":
            save_kwargs["quality"] = quality
            save_kwargs["subsampling"] = 0  # 4:4:4 high quality chroma
        if exif:
            save_kwargs["exif"] = exif

        pil_img.save(out_path, **save_kwargs)
        return out_path

    def get_result_path(self, job_id: str) -> Optional[Path]:
        job_dir = self.base_dir / job_id
        if not job_dir.is_dir():
            return None
        candidates = list(job_dir.glob("result.*"))
        return candidates[0] if candidates else None

    def get_original_path(self, job_id: str) -> Optional[Path]:
        job_dir = self.base_dir / job_id
        if not job_dir.is_dir():
            return None
        candidates = list(job_dir.glob("original.*"))
        if not candidates:
            all_files = [f for f in job_dir.iterdir() if f.is_file() and not f.name.startswith("result.")]
            if all_files:
                candidates = all_files
        return candidates[0] if candidates else None

    def cleanup_old_jobs(self, max_age_seconds: Optional[int] = None) -> int:
        """
        Deletes job directories older than the configured TTL (default 1 hour).
        """
        max_age = max_age_seconds if max_age_seconds is not None else config.storage.job_ttl_seconds
        now = time.time()
        purged = 0

        if not self.base_dir.is_dir():
            return 0

        for job_folder in self.base_dir.iterdir():
            if job_folder.is_dir():
                try:
                    mtime = job_folder.stat().st_mtime
                    if now - mtime > max_age:
                        shutil.rmtree(job_folder, ignore_errors=True)
                        purged += 1
                except Exception:
                    pass
        return purged


storage = JobStorage()
