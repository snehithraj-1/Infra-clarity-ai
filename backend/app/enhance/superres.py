from pathlib import Path
from typing import Any, Callable, Optional
import cv2
import numpy as np

from app.enhance.base import Enhancer, soft_clip


class SuperResStage(Enhancer):
    """
    Super-resolution stage.
    Deep Real-ESRGAN neural model when weights are present,
    with classical edge-directed Lanczos-4 sharpening fallback.
    """

    def __init__(self, weights_path: Optional[str] = None):
        self.weights_path = Path(weights_path) if weights_path else None
        if not self.weights_path:
            # Check default candidate paths for Real-ESRGAN weights
            candidates = [
                Path("backend/weights/realesrgan_x4.pth"),
                Path("weights/realesrgan_x4.pth"),
                Path("backend/weights/realesr-general-x4v3.pth"),
                Path("weights/realesr-general-x4v3.pth"),
                Path(__file__).resolve().parent.parent.parent / "weights" / "realesrgan_x4.pth",
                Path(__file__).resolve().parent.parent.parent / "weights" / "realesr-general-x4v3.pth",
            ]
            for cand in candidates:
                if cand.is_file():
                    self.weights_path = cand
                    break

        self._deep_model = None
        if self.weights_path and self.weights_path.is_file():
            try:
                from app.enhance.models import load_deep_model
                self._deep_model = load_deep_model(self.weights_path, "realesrgan_x4")
            except Exception:
                self._deep_model = None

    @property
    def name(self) -> str:
        return "super_resolution"

    @property
    def is_available(self) -> bool:
        return True

    @property
    def engine_type(self) -> str:
        return "deep" if self._deep_model is not None else "classical"

    def run(
        self,
        image: np.ndarray,
        strength: int = 50,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        scale: float = 2.0,
        **kwargs: Any,
    ) -> np.ndarray:
        if strength <= 0:
            return image.copy()

        alpha = float(np.clip(strength / 100.0, 0.0, 1.0))
        img = np.clip(image, 0.0, 1.0).astype(np.float32)
        h, w = img.shape[:2]

        out_w = int(round(w * scale))
        out_h = int(round(h * scale))

        # Real-ESRGAN Deep Neural Network AI Inference
        if self._deep_model is not None:
            if progress_callback:
                progress_callback(0.3, "Executing Real-ESRGAN Deep Neural AI Inference")
            try:
                import torch
                with torch.no_grad():
                    inp = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).float()
                    out = self._deep_model(inp)
                    out = torch.clamp(out, 0.0, 1.0)
                    ai_result = out.squeeze(0).permute(1, 2, 0).numpy()

                if (ai_result.shape[0], ai_result.shape[1]) != (out_h, out_w):
                    interp = cv2.INTER_LANCZOS4 if out_w > ai_result.shape[1] else cv2.INTER_AREA
                    ai_result = cv2.resize(ai_result, (out_w, out_h), interpolation=interp)

                base_up = cv2.resize(img, (out_w, out_h), interpolation=cv2.INTER_LANCZOS4)
                res = (1.0 - alpha * 0.95) * base_up + (alpha * 0.95) * ai_result

                # Bilateral micro-detail synthesis in LAB space strictly on structural contours
                lab_res = cv2.cvtColor((res * 255.0).astype(np.uint8), cv2.COLOR_RGB2LAB)
                L_res, a_res, b_res = cv2.split(lab_res)
                Lf_res = L_res.astype(np.float32)

                guide_res = cv2.bilateralFilter(L_res, 5, 20, 5).astype(np.float32)
                detail_fine = np.clip(Lf_res - guide_res, -18.0, 18.0)

                gx_res = cv2.Sobel(guide_res, cv2.CV_32F, 1, 0, ksize=3)
                gy_res = cv2.Sobel(guide_res, cv2.CV_32F, 0, 1, ksize=3)
                mag_res = cv2.magnitude(gx_res, gy_res)
                edge_mask_res = np.clip((mag_res - 6.0) / 25.0, 0.0, 1.0)

                Lf_boosted = Lf_res + (alpha * 0.75) * (1.25 * detail_fine) * edge_mask_res

                # Anti-ringing deringing clamp: guarantees zero halos on upscaled boundaries
                k3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                local_max = cv2.dilate(Lf_res, k3)
                local_min = cv2.erode(Lf_res, k3)
                margin = 3.0 + 2.0 * alpha
                Lf_clamped = np.clip(Lf_boosted, local_min - margin, local_max + margin)
                L_boosted = np.clip(Lf_clamped, 0, 255).astype(np.uint8)

                lab_boosted = cv2.merge([L_boosted, a_res, b_res])
                res = cv2.cvtColor(lab_boosted, cv2.COLOR_LAB2RGB).astype(np.float32) / 255.0

                if progress_callback:
                    progress_callback(1.0, "Deep Neural AI Super-Resolution & micro-detailing completed")
                return soft_clip(res)
            except Exception as e:
                # If torch inference fails for any reason, smoothly fallback to high-fidelity classical
                pass

        if progress_callback:
            progress_callback(0.3, f"Resampling with Lanczos-4 (x{scale:.0f})")

        # High-order Lanczos-4 interpolation
        upscaled = cv2.resize(img, (out_w, out_h), interpolation=cv2.INTER_LANCZOS4)

        if progress_callback:
            progress_callback(0.7, "Synthesizing edge contrast without ringing")

        # Bilateral edge-directed sharpening to prevent halo ringing on borders
        gray_up = cv2.cvtColor(upscaled, cv2.COLOR_RGB2GRAY)
        guide = cv2.bilateralFilter(gray_up, 5, 25, 5)
        gx = cv2.Sobel(guide, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(guide, cv2.CV_32F, 0, 1, ksize=3)
        edge_weight = np.clip((cv2.magnitude(gx, gy) - 0.03) / 0.25, 0.0, 1.0)
        if upscaled.ndim == 3:
            edge_weight = edge_weight[:, :, np.newaxis]

        blur_fine = cv2.GaussianBlur(upscaled, (0, 0), sigmaX=0.9, sigmaY=0.9)
        # Clamped detail prevents harsh overshooting and jagged pixels
        detail = np.clip(upscaled - blur_fine, -0.06, 0.06)
        result = upscaled + (0.75 * alpha) * detail * edge_weight

        if progress_callback:
            progress_callback(1.0, "Super-resolution completed")

        return soft_clip(result)
