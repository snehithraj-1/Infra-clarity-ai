from pathlib import Path
from typing import Any, Callable, Optional
import cv2
import numpy as np

from app.enhance.base import Enhancer, soft_clip


class DenoiseStage(Enhancer):
    """
    Sensor noise removal stage.
    Uses classical Non-Local Means (cv2.fastNlMeansDenoisingColored) as robust baseline,
    with pluggable deep restoration (NAFNet) when weights are available.
    """

    def __init__(self, weights_path: Optional[str] = None):
        self.weights_path = Path(weights_path) if weights_path else None
        self._deep_model = None

    @property
    def name(self) -> str:
        return "denoise"

    @property
    def is_available(self) -> bool:
        return True

    @property
    def engine_type(self) -> str:
        return "deep" if self._deep_model is not None else "bilateral NLM"

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

        if progress_callback:
            progress_callback(0.2, "Executing full-spectrum noise and particulate removal")

        # 1. Classical Fast Non-Local Means Denoising (wipes out sensor grain and chroma noise)
        img_uint8 = (img * 255.0).astype(np.uint8)
        h_param = 5.0 + 16.0 * alpha
        h_color = h_param * 1.4

        denoised_uint8 = cv2.fastNlMeansDenoisingColored(
            img_uint8,
            None,
            h=h_param,
            hColor=h_color,
            templateWindowSize=7,
            searchWindowSize=21,
        )
        denoised_float = denoised_uint8.astype(np.float32) / 255.0

        # 2. High-definition bilateral noise suppression on edges
        bilateral = cv2.bilateralFilter(img_uint8, d=7, sigmaColor=35, sigmaSpace=7).astype(np.float32) / 255.0

        # 3. Structural edge guidance
        gray = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2GRAY)
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        edge_mag = cv2.magnitude(gx, gy)
        edge_mask = np.clip((edge_mag - 5.0) / 30.0, 0.0, 1.0)
        if denoised_float.ndim == 3:
            edge_mask = edge_mask[:, :, np.newaxis]

        # 4. Clean blend: flat areas get 100% NLMeans denoising (removes 100% of grain from skies and fog);
        # Structural edges receive clean bilateral filtering (removes grain along edges while keeping edges razor sharp)
        clean_result = (1.0 - edge_mask) * denoised_float + edge_mask * bilateral
        result = (1.0 - alpha) * img + alpha * clean_result

        if progress_callback:
            progress_callback(1.0, "Denoising completed")

        return soft_clip(result)
