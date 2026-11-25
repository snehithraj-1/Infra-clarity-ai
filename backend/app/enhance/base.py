from abc import ABC, abstractmethod
from typing import Any, Callable, Optional
import numpy as np


def soft_clip(image: np.ndarray, lower: float = 0.0, upper: float = 1.0, knee: float = 0.05) -> np.ndarray:
    """
    Applies soft shoulder compression near the boundaries to preserve highlight
    and shadow gradients without harsh clipping artifacts.
    """
    img = image.copy()
    high_threshold = upper - knee
    high_mask = img > high_threshold
    if np.any(high_mask):
        excess = img[high_mask] - high_threshold
        img[high_mask] = high_threshold + knee * (1.0 - np.exp(-excess / knee))

    low_threshold = lower + knee
    low_mask = img < low_threshold
    if np.any(low_mask):
        deficit = low_threshold - img[low_mask]
        img[low_mask] = low_threshold - knee * (1.0 - np.exp(-deficit / knee))

    return np.clip(img, lower, upper).astype(np.float32)


class Enhancer(ABC):
    """
    Abstract base class for all image restoration and enhancement stages.
    Operates strictly on float32 RGB images normalized to [0.0, 1.0].
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this enhancement stage."""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the engine (classical or deep) can be executed."""
        pass

    @property
    def engine_type(self) -> str:
        """Returns 'classical' or 'deep'."""
        return "classical"

    @abstractmethod
    def run(
        self,
        image: np.ndarray,
        strength: int = 50,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        **kwargs: Any,
    ) -> np.ndarray:
        """
        Executes the enhancement stage.
        Args:
            image: Float32 ndarray of shape (H, W, 3) in [0.0, 1.0] range (RGB).
            strength: Intensity scalar from 0 to 100.
            progress_callback: Optional callable for tile or iteration progress.
        Returns:
            Enhanced float32 ndarray in [0.0, 1.0] range.
        """
        pass
