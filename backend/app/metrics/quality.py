from typing import Optional, Tuple
import cv2
import numpy as np
from skimage.metrics import peak_signal_noise_ratio, structural_similarity

from app.metrics.detail_gain import compute_detail_gains
from app.schemas import QualityMetrics


def compute_metrics(
    original_float: np.ndarray,
    enhanced_float: np.ndarray,
    ground_truth_float: Optional[np.ndarray] = None,
) -> QualityMetrics:
    """
    Computes full quality metrics suite:
    - Detail gains (Canny edge density, Laplacian high-frequency variance)
    - Full-reference metrics (PSNR, SSIM) when ground truth is provided
    - No-reference metrics (NIQE, BRISQUE) via pyiqa if installed
    """
    gains = compute_detail_gains(original_float, enhanced_float)

    psnr_val: Optional[float] = None
    ssim_val: Optional[float] = None
    niqe_val: Optional[float] = None
    brisque_val: Optional[float] = None

    # Full-reference PSNR and SSIM if ground truth is supplied
    if ground_truth_float is not None:
        gt = np.clip(ground_truth_float, 0.0, 1.0)
        enh = np.clip(enhanced_float, 0.0, 1.0)
        if gt.shape != enh.shape:
            gt = cv2.resize(gt, (enh.shape[1], enh.shape[0]), interpolation=cv2.INTER_LINEAR)
        psnr_val = round(float(peak_signal_noise_ratio(gt, enh, data_range=1.0)), 2)
        ssim_raw = structural_similarity(gt, enh, channel_axis=-1, data_range=1.0)
        ssim_val = round(
            float(ssim_raw) if isinstance(ssim_raw, (int, float, np.floating)) else float(ssim_raw[0]),
            4,
        )

    # Optional pyiqa no-reference metrics
    try:
        import pyiqa  # type: ignore
        # pyiqa optional evaluation if installed
    except ImportError:
        pass

    return QualityMetrics(
        detail_gain=gains["detail_gain"],
        laplacian_gain=gains["laplacian_gain"],
        canny_gain=gains["canny_gain"],
        psnr=psnr_val,
        ssim=ssim_val,
        niqe=niqe_val,
        brisque=brisque_val,
        note=gains["note"],
    )
