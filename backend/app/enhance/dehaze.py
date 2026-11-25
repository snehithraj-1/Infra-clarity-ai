from typing import Any, Callable, Optional
import cv2
import numpy as np

from app.enhance.base import Enhancer, soft_clip


def guided_filter(guide: np.ndarray, src: np.ndarray, radius: int = 40, eps: float = 1e-3) -> np.ndarray:
    """
    Fast edge-preserving guided filter (He et al.).
    Refines raw transmission map using grayscale luminance as guidance.
    """
    kernel_size = (2 * radius + 1, 2 * radius + 1)
    mean_i = cv2.boxFilter(guide, cv2.CV_32F, kernel_size)
    mean_p = cv2.boxFilter(src, cv2.CV_32F, kernel_size)
    mean_ip = cv2.boxFilter(guide * src, cv2.CV_32F, kernel_size)
    cov_ip = mean_ip - mean_i * mean_p

    mean_ii = cv2.boxFilter(guide * guide, cv2.CV_32F, kernel_size)
    var_i = mean_ii - mean_i * mean_i

    a = cov_ip / (var_i + eps)
    b = mean_p - a * mean_i

    mean_a = cv2.boxFilter(a, cv2.CV_32F, kernel_size)
    mean_b = cv2.boxFilter(b, cv2.CV_32F, kernel_size)

    return mean_a * guide + mean_b


class DehazeStage(Enhancer):
    """
    Atmospheric dehazing using Dark Channel Prior with guided-filter
    transmission refinement and LAB-space CLAHE local contrast enhancement.
    """

    @property
    def name(self) -> str:
        return "dehaze"

    @property
    def is_available(self) -> bool:
        return True

    @property
    def engine_type(self) -> str:
        return "guided AI"

    def run(
        self,
        image: np.ndarray,
        strength: int = 50,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        **kwargs: Any,
    ) -> np.ndarray:
        if strength <= 0:
            return image.copy()

        alpha = float(np.clip(strength / 100.0, 0.0, 1.0))
        img = np.clip(image, 0.0, 1.0).astype(np.float32)
        h, w = img.shape[:2]

        if progress_callback:
            progress_callback(0.1, "Estimating atmospheric scattering")

        # 1. Dark Channel Prior
        min_channel = np.min(img, axis=2)
        patch_size = 15
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (patch_size, patch_size))
        dark_channel = cv2.erode(min_channel, kernel)

        # 2. Atmospheric light estimation (top 0.1% brightest dark-channel pixels)
        num_pixels = max(1, int(h * w * 0.001))
        flat_dark = dark_channel.reshape(-1)
        flat_img = img.reshape(-1, 3)
        indices = np.argpartition(flat_dark, -num_pixels)[-num_pixels:]
        brightest_idx = indices[np.argmax(np.mean(flat_img[indices], axis=1))]
        airlight = flat_img[brightest_idx]
        airlight = np.maximum(airlight, 0.2)

        # 3. Raw transmission map
        normalized_img = img / airlight
        raw_dark = cv2.erode(np.min(normalized_img, axis=2), kernel)
        omega = 0.50 + 0.35 * alpha
        raw_transmission = 1.0 - omega * raw_dark

        if progress_callback:
            progress_callback(0.4, "Refining transmission boundary")

        # 4. Guided filter refinement with edge-preserving epsilon to prevent boundary halos
        gray_guide = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        refined_transmission = guided_filter(gray_guide, raw_transmission, radius=12, eps=0.04)
        t0 = max(0.10, 0.25 - 0.15 * alpha)
        refined_transmission = np.clip(refined_transmission, t0, 1.0)

        # 5. Scene radiance recovery
        dehazed = np.zeros_like(img)
        for c in range(3):
            dehazed[:, :, c] = (img[:, :, c] - airlight[c]) / refined_transmission + airlight[c]

        dehazed = np.clip(dehazed, 0.0, 1.0)

        if progress_callback:
            progress_callback(0.7, "Enhancing luminance in LAB space")

        # 6. Deep atmospheric fog penetration and contrast expansion in LAB color space
        lab = cv2.cvtColor((dehazed * 255.0).astype(np.uint8), cv2.COLOR_RGB2LAB)
        l_chan, a_chan, b_chan = cv2.split(lab)
        l_f = l_chan.astype(np.float32)

        clahe_clip = 1.8 + 0.6 * alpha
        clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=(8, 8))
        l_clahe = clahe.apply(l_chan).astype(np.float32)

        # Dynamic luminance recovery: recovers obscured structures in deep fog while preventing halos
        l_enhanced = (1.0 - 0.7 * alpha) * l_f + (0.7 * alpha) * l_clahe
        l_stretched = np.clip(l_enhanced, 0.0, 255.0).astype(np.uint8)

        # Restore natural chromatic vibrancy without color noise
        a_f = (a_chan.astype(np.float32) - 128.0) * (1.0 + 0.18 * alpha) + 128.0
        b_f = (b_chan.astype(np.float32) - 128.0) * (1.0 + 0.18 * alpha) + 128.0
        a_boost = np.clip(a_f, 0, 255).astype(np.uint8)
        b_boost = np.clip(b_f, 0, 255).astype(np.uint8)

        lab_enhanced = cv2.merge([l_stretched, a_boost, b_boost])
        rgb_enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2RGB).astype(np.float32) / 255.0

        # Proportional blending strictly honors user strength
        result = (1.0 - alpha) * img + alpha * rgb_enhanced

        if progress_callback:
            progress_callback(1.0, "Dehazing completed")

        return soft_clip(result)
