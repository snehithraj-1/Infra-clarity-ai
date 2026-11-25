import math
from typing import Callable, List, Optional, Tuple
import cv2
import numpy as np


def create_feather_window(height: int, width: int, overlap: int) -> np.ndarray:
    """
    Creates a 2D cosine-feathered blending window.
    Interior values are 1.0, smoothly tapering to zero across the overlap margin.
    """
    def create_1d_taper(length: int, margin: int) -> np.ndarray:
        if margin <= 0 or margin * 2 >= length:
            return np.hanning(length).astype(np.float32)
        window = np.ones(length, dtype=np.float32)
        ramp = 0.5 * (1.0 - np.cos(np.linspace(0, np.pi, margin, dtype=np.float32)))
        window[:margin] = ramp
        window[-margin:] = ramp[::-1]
        return window

    win_y = create_1d_taper(height, overlap)
    win_x = create_1d_taper(width, overlap)
    window_2d = np.outer(win_y, win_x).astype(np.float32)
    # Ensure strictly positive minimum weight to prevent division by zero
    return np.maximum(window_2d, 1e-4)


class TiledProcessor:
    """
    Handles memory-safe tiled inference with feathered overlap blending for
    very large images (up to 6000x4000 and beyond).
    """

    def __init__(
        self,
        tile_size: int = 512,
        overlap: int = 32,
        min_tile_size: int = 256,
    ):
        self.tile_size = tile_size
        self.overlap = overlap
        self.min_tile_size = min_tile_size

    def compute_tile_grid(
        self,
        height: int,
        width: int,
        tile_size: int,
        overlap: int,
    ) -> List[Tuple[int, int, int, int]]:
        """
        Calculates (y0, y1, x0, x1) coordinates covering the full image dimensions.
        """
        step = tile_size - overlap
        if step <= 0:
            step = tile_size // 2

        tiles = []
        y = 0
        while y < height:
            y1 = min(y + tile_size, height)
            y0 = max(0, y1 - tile_size)
            x = 0
            while x < width:
                x1 = min(x + tile_size, width)
                x0 = max(0, x1 - tile_size)
                tiles.append((y0, y1, x0, x1))
                if x1 >= width:
                    break
                x += step
            if y1 >= height:
                break
            y += step

        # Deduplicate identical tiles
        seen = set()
        unique_tiles = []
        for t in tiles:
            if t not in seen:
                seen.add(t)
                unique_tiles.append(t)
        return unique_tiles

    def process(
        self,
        image: np.ndarray,
        process_fn: Callable[[np.ndarray], np.ndarray],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        scale: float = 1.0,
    ) -> np.ndarray:
        """
        Splits image into overlapping tiles, applies process_fn to each,
        and reconstructs the output with feathered blending.
        """
        h, w = image.shape[:2]
        c = image.shape[2] if image.ndim == 3 else 1

        tile_size = self.tile_size
        overlap = self.overlap

        # Direct execution if image is already smaller than single tile size
        if h <= tile_size and w <= tile_size:
            if progress_callback:
                progress_callback(1, 1, "Processing full image")
            return process_fn(image)

        # Attempt processing with automatic tile size halving on memory pressure
        current_tile_size = tile_size
        while current_tile_size >= self.min_tile_size:
            try:
                return self._run_tiling(
                    image,
                    process_fn,
                    current_tile_size,
                    overlap,
                    progress_callback,
                    scale,
                )
            except MemoryError:
                current_tile_size //= 2
                overlap = max(16, overlap // 2)

        # Final attempt with minimum tile size
        return self._run_tiling(
            image,
            process_fn,
            self.min_tile_size,
            max(16, overlap // 2),
            progress_callback,
            scale,
        )

    def _run_tiling(
        self,
        image: np.ndarray,
        process_fn: Callable[[np.ndarray], np.ndarray],
        tile_size: int,
        overlap: int,
        progress_callback: Optional[Callable[[int, int, str], None]],
        scale: float,
    ) -> np.ndarray:
        h, w = image.shape[:2]
        out_h = int(round(h * scale))
        out_w = int(round(w * scale))
        is_multichannel = image.ndim == 3
        c = image.shape[2] if is_multichannel else 1

        tiles = self.compute_tile_grid(h, w, tile_size, overlap)
        total_tiles = len(tiles)

        # Accumulator buffers for weighted blending
        if is_multichannel:
            accumulator = np.zeros((out_h, out_w, c), dtype=np.float32)
        else:
            accumulator = np.zeros((out_h, out_w), dtype=np.float32)
        weight_sum = np.zeros((out_h, out_w), dtype=np.float32)

        for idx, (y0, y1, x0, x1) in enumerate(tiles):
            tile_crop = image[y0:y1, x0:x1]
            processed_tile = process_fn(tile_crop)

            th, tw = tile_crop.shape[:2]
            pth, ptw = processed_tile.shape[:2]

            tile_win = create_feather_window(pth, ptw, int(round(overlap * scale)))

            out_y0 = int(round(y0 * scale))
            out_x0 = int(round(x0 * scale))
            out_y1 = out_y0 + pth
            out_x1 = out_x0 + ptw

            # Clip bounds to output canvas
            src_y1 = pth - max(0, out_y1 - out_h)
            src_x1 = ptw - max(0, out_x1 - out_w)
            dst_y1 = min(out_y1, out_h)
            dst_x1 = min(out_x1, out_w)

            clipped_win = tile_win[:src_y1, :src_x1]
            clipped_proc = processed_tile[:src_y1, :src_x1]

            if is_multichannel:
                accumulator[out_y0:dst_y1, out_x0:dst_x1] += (
                    clipped_proc * clipped_win[:, :, np.newaxis]
                )
            else:
                accumulator[out_y0:dst_y1, out_x0:dst_x1] += clipped_proc * clipped_win

            weight_sum[out_y0:dst_y1, out_x0:dst_x1] += clipped_win

            if progress_callback:
                progress_callback(
                    idx + 1,
                    total_tiles,
                    f"Processing tile {idx + 1}/{total_tiles}",
                )

        # Normalize accumulator by total weights
        weight_sum = np.maximum(weight_sum, 1e-6)
        if is_multichannel:
            result = accumulator / weight_sum[:, :, np.newaxis]
        else:
            result = accumulator / weight_sum

        return result.astype(np.float32)
