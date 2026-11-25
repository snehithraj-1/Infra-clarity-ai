import cv2
import numpy as np


def compute_canny_edge_density(image_uint8: np.ndarray, low_thresh: int = 50, high_thresh: int = 150) -> float:
    """
    Computes the fraction of edge pixels detected by Canny operator:
        Density = count(Canny(gray) > 0) / (H * W)
    """
    if image_uint8.ndim == 3:
        gray = cv2.cvtColor(image_uint8, cv2.COLOR_RGB2GRAY)
    else:
        gray = image_uint8
    edges = cv2.Canny(gray, low_thresh, high_thresh)
    total_pixels = gray.shape[0] * gray.shape[1]
    if total_pixels == 0:
        return 0.0
    return float(np.count_nonzero(edges)) / float(total_pixels)


def compute_laplacian_variance(image_uint8: np.ndarray) -> float:
    """
    Computes high-frequency variance using Laplacian operator.
    """
    if image_uint8.ndim == 3:
        gray = cv2.cvtColor(image_uint8, cv2.COLOR_RGB2GRAY)
    else:
        gray = image_uint8
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    return float(lap.var())


def compute_detail_gains(
    original_float: np.ndarray,
    enhanced_float: np.ndarray,
) -> dict:
    """
    Computes detail gain ratios between enhanced and original images.
    Detail gain is reported as a percentage increase.
    Proxy for defect/fault visibility, not an automated detection claim.
    """
    orig_u8 = (np.clip(original_float, 0.0, 1.0) * 255.0).astype(np.uint8)
    enh_u8 = (np.clip(enhanced_float, 0.0, 1.0) * 255.0).astype(np.uint8)

    # Resize original to match enhanced if super-resolution scaled the image
    if orig_u8.shape[:2] != enh_u8.shape[:2]:
        orig_u8 = cv2.resize(
            orig_u8,
            (enh_u8.shape[1], enh_u8.shape[0]),
            interpolation=cv2.INTER_LINEAR,
        )

    # 1. Canny edge density gain
    canny_before = compute_canny_edge_density(orig_u8)
    canny_after = compute_canny_edge_density(enh_u8)
    canny_ratio = (canny_after / canny_before) if canny_before > 1e-6 else 1.0
    canny_gain_pct = (canny_ratio - 1.0) * 100.0

    # 2. Laplacian high-frequency variance gain
    lap_before = compute_laplacian_variance(orig_u8)
    lap_after = compute_laplacian_variance(enh_u8)
    lap_ratio = (lap_after / lap_before) if lap_before > 1e-6 else 1.0
    lap_gain_pct = (lap_ratio - 1.0) * 100.0

    # Composite detail gain: balanced geometric mean of edge density & gradient variance
    composite_gain_pct = 0.5 * (canny_gain_pct + lap_gain_pct)

    return {
        "detail_gain": round(float(composite_gain_pct), 2),
        "canny_gain": round(float(canny_gain_pct), 2),
        "laplacian_gain": round(float(lap_gain_pct), 2),
        "note": "Proxy for fault visibility, not a detection accuracy claim.",
    }
