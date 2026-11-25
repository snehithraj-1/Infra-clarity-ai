import numpy as np
import pytest
from app.enhance.tiling import TiledProcessor, create_feather_window


def test_feather_window_strictly_positive():
    window = create_feather_window(512, 512, 32)
    assert window.shape == (512, 512)
    assert np.all(window > 0.0)
    assert np.max(window) <= 1.0
    # Center area should be 1.0
    assert np.isclose(window[256, 256], 1.0, atol=1e-3)


def test_tiling_identity_reconstruction_within_one_intensity_level():
    """
    Hard requirement:
    Tiling reconstructs an identity-transformed image within 1 intensity level (1/255 = 0.00392).
    """
    np.random.seed(42)
    # Test on a large image requiring multiple tiles in both directions
    h, w, c = 1200, 1500, 3
    # Synthetic image with rich gradients and high-contrast lines
    y, x = np.mgrid[0:h, 0:w]
    base = (0.5 + 0.3 * np.sin(x / 50.0) * np.cos(y / 50.0))[:, :, np.newaxis]
    synthetic_image = (base + 0.1 * np.random.rand(h, w, c)).astype(np.float32)
    synthetic_image = np.clip(synthetic_image, 0.0, 1.0)

    processor = TiledProcessor(tile_size=512, overlap=32)

    # Identity transform: returns tile untouched
    def identity_fn(tile: np.ndarray) -> np.ndarray:
        return tile.copy()

    reconstructed = processor.process(synthetic_image, identity_fn)

    assert reconstructed.shape == synthetic_image.shape
    max_diff = float(np.max(np.abs(reconstructed - synthetic_image)))

    one_intensity_level = 1.0 / 255.0
    assert max_diff < one_intensity_level, f"Max diff {max_diff} exceeded 1 intensity level ({one_intensity_level})"
    # With smooth cosine/Hann tapering, difference should actually be < 1e-4
    assert max_diff < 0.001


def test_tiling_progress_callback():
    image = np.zeros((800, 800, 3), dtype=np.float32)
    processor = TiledProcessor(tile_size=512, overlap=32)

    calls = []

    def callback(current: int, total: int, msg: str):
        calls.append((current, total))

    processor.process(image, lambda t: t, progress_callback=callback)

    assert len(calls) > 0
    # Final call should reach total tiles
    last_current, last_total = calls[-1]
    assert last_current == last_total


def test_tiling_superres_scaling():
    h, w = 600, 800
    image = np.random.rand(h, w, 3).astype(np.float32)
    processor = TiledProcessor(tile_size=512, overlap=32)

    scale = 2.0

    def mock_upscale(tile: np.ndarray) -> np.ndarray:
        import cv2
        th, tw = tile.shape[:2]
        return cv2.resize(tile, (int(tw * scale), int(th * scale)))

    result = processor.process(image, mock_upscale, scale=scale)
    assert result.shape == (int(h * scale), int(w * scale), 3)
