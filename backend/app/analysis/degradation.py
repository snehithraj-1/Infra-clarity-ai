import cv2
import numpy as np

from app.config import AppConfig, config as default_config
from app.schemas import DegradationMetric, DegradationReport, InspectionLoophole, Severity


def compute_blur_score(gray_uint8: np.ndarray) -> float:
    """
    Computes blur score using variance of the Laplacian:
        Score = Var(cv2.Laplacian(gray)) = (1 / N) * sum((L(x, y) - mu_L)^2)
    Sharp edges yield high second derivatives (high variance), while blurred
    regions produce smooth gradients (low variance).
    Excludes outer border margins to prevent watermarks, metadata banners,
    and synthetic framing from artificially inflating blur scores.
    """
    h, w = gray_uint8.shape[:2]
    my_top = max(1, int(h * 0.05))
    my_bot = max(1, int(h * 0.10))
    mx = max(1, int(w * 0.05))
    if h > (my_top + my_bot + 10) and w > (2 * mx + 10):
        eval_region = gray_uint8[my_top : h - my_bot, mx : w - mx]
    else:
        eval_region = gray_uint8

    laplacian = cv2.Laplacian(eval_region, cv2.CV_64F)
    return float(laplacian.var())


def compute_haze_score(rgb_normalized: np.ndarray, patch_size: int = 15) -> float:
    """
    Computes haze score based on the Dark Channel Prior (He et al.) evaluated on textured scene elements.
    Prevents neutral/gray backgrounds and studio overcast from causing false severe haze diagnoses.
    """
    min_channel = np.min(rgb_normalized, axis=2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (patch_size, patch_size))
    dark_channel = cv2.erode(min_channel, kernel)

    gray = cv2.cvtColor(rgb_normalized, cv2.COLOR_RGB2GRAY)
    grad = cv2.magnitude(cv2.Sobel(gray, cv2.CV_32F, 1, 0), cv2.Sobel(gray, cv2.CV_32F, 0, 1))
    texture_mask = cv2.dilate((grad > 0.035).astype(np.float32), np.ones((patch_size, patch_size), np.uint8))

    if np.sum(texture_mask) > (0.02 * rgb_normalized.shape[0] * rgb_normalized.shape[1]):
        return float(np.mean(dark_channel[texture_mask > 0]))
    return float(np.mean(dark_channel))


def compute_noise_estimate(rgb_normalized: np.ndarray) -> float:
    """
    Estimates standard deviation of additive Gaussian noise from high-frequency
    wavelet residuals using scikit-image's robust MAD estimator:
        sigma_hat = median(|detail_coeffs|) / 0.6745
    If PyWavelets is not present, falls back to Immerkaer's Laplacian mask:
        M = [[1, -2, 1], [-2, 4, -2], [1, -2, 1]]
        sigma = sqrt(pi/2) * (1 / (6*(W-2)*(H-2))) * sum(|I * M|)
    Returned on a 0-255 scale for human-readable sensor noise severity.
    """
    try:
        from skimage.restoration import estimate_sigma

        sigmas = estimate_sigma(rgb_normalized, channel_axis=-1, average_sigmas=False)
        mean_sigma_norm = float(np.mean(sigmas))
        return mean_sigma_norm * 255.0
    except (ImportError, Exception):
        h, w = rgb_normalized.shape[:2]
        if h < 3 or w < 3:
            return 0.0
        kernel = np.array([[1, -2, 1], [-2, 4, -2], [1, -2, 1]], dtype=np.float32)
        channels = [
            rgb_normalized[:, :, c]
            for c in range(rgb_normalized.shape[2])
        ] if rgb_normalized.ndim == 3 else [rgb_normalized]
        sigmas = []
        for ch in channels:
            res = cv2.filter2D(ch, -1, kernel)
            valid_res = res[1 : h - 1, 1 : w - 1]
            sigma = float(np.sum(np.abs(valid_res))) * np.sqrt(0.5 * np.pi) / (6.0 * (w - 2) * (h - 2))
            sigmas.append(sigma)
        return float(np.mean(sigmas)) * 255.0


def compute_contrast_score(gray_normalized: np.ndarray) -> float:
    """
    Computes Root-Mean-Square (RMS) contrast of normalized luminance:
        RMS = sqrt((1 / N) * sum((I(x, y) - mean(I))^2))
    Values near 0 indicate low contrast (washed-out or underexposed imagery),
    while values above 0.25 indicate rich dynamic range.
    """
    return float(np.std(gray_normalized))


def analyze_degradations(
    image: np.ndarray,
    app_config: AppConfig = default_config,
) -> DegradationReport:
    """
    Inspects an input image and calculates blur, haze, noise, contrast,
    and resolution metrics using thresholds specified in config.yaml.
    """
    if image.dtype == np.uint8:
        rgb_norm = image.astype(np.float32) / 255.0
        rgb_uint8 = image
    else:
        rgb_norm = np.clip(image, 0.0, 1.0).astype(np.float32)
        rgb_uint8 = (rgb_norm * 255.0).astype(np.uint8)

    h, w = rgb_uint8.shape[:2]

    if rgb_uint8.ndim == 2:
        gray_uint8 = rgb_uint8
        gray_norm = rgb_norm
        rgb_norm = np.stack([rgb_norm] * 3, axis=-1)
    else:
        gray_uint8 = cv2.cvtColor(rgb_uint8, cv2.COLOR_RGB2GRAY)
        gray_norm = cv2.cvtColor(rgb_norm, cv2.COLOR_RGB2GRAY)

    thresholds = app_config.analysis

    # 1. Blur
    blur_score = compute_blur_score(gray_uint8)
    if blur_score < thresholds.blur.severe_threshold:
        blur_severity = Severity.HIGH
        blur_label = "Severe Blur"
        blur_hint = f"Severe blur detected (score: {blur_score:.1f}); structural cracks and fine edges obscured."
    elif blur_score < thresholds.blur.moderate_threshold:
        blur_severity = Severity.MEDIUM
        blur_label = "Moderate Blur"
        blur_hint = f"Moderate blur detected (score: {blur_score:.1f}); fine defect details are softened."
    else:
        blur_severity = Severity.LOW
        blur_label = "Sharp"
        blur_hint = f"Image focus is sharp (score: {blur_score:.1f})."

    # 2. Haze
    haze_score = compute_haze_score(rgb_norm)
    if haze_score > thresholds.haze.severe_threshold:
        haze_severity = Severity.HIGH
        haze_label = "Heavy Haze"
        haze_hint = f"Dense atmospheric haze/fog detected (score: {haze_score:.3f}); transmission heavily reduced."
    elif haze_score > thresholds.haze.moderate_threshold:
        haze_severity = Severity.MEDIUM
        haze_label = "Moderate Haze"
        haze_hint = f"Moderate atmospheric haze detected (score: {haze_score:.3f}); distant features washed out."
    else:
        haze_severity = Severity.LOW
        haze_label = "Clear"
        haze_hint = f"Clear atmospheric visibility (score: {haze_score:.3f})."

    # 3. Noise
    noise_estimate = compute_noise_estimate(rgb_norm)
    if noise_estimate > thresholds.noise.severe_threshold:
        noise_severity = Severity.HIGH
        noise_label = "Heavy Noise"
        noise_hint = f"High sensor grain / noise detected (sigma: {noise_estimate:.1f})."
    elif noise_estimate > thresholds.noise.moderate_threshold:
        noise_severity = Severity.MEDIUM
        noise_label = "Moderate Noise"
        noise_hint = f"Moderate sensor noise present (sigma: {noise_estimate:.1f})."
    else:
        noise_severity = Severity.LOW
        noise_label = "Clean"
        noise_hint = f"Low noise floor (sigma: {noise_estimate:.1f})."

    # 4. Contrast
    contrast_score = compute_contrast_score(gray_norm)
    if contrast_score < thresholds.contrast.severe_threshold:
        contrast_severity = Severity.HIGH
        contrast_label = "Low Contrast"
        contrast_hint = f"Severe low contrast / underexposure detected (RMS: {contrast_score:.3f})."
    elif contrast_score < thresholds.contrast.moderate_threshold:
        contrast_severity = Severity.MEDIUM
        contrast_label = "Suboptimal Contrast"
        contrast_hint = f"Suboptimal dynamic range (RMS: {contrast_score:.3f})."
    else:
        contrast_severity = Severity.LOW
        contrast_label = "Good Contrast"
        contrast_hint = f"Dynamic range and contrast are balanced (RMS: {contrast_score:.3f})."

    # 5. Resolution flag
    shorter_side = min(h, w)
    resolution_flag = shorter_side < thresholds.resolution.min_shorter_side

    hints = []
    loopholes = []

    if blur_severity in (Severity.HIGH, Severity.MEDIUM):
        hints.append(blur_hint)
        loopholes.append(
            InspectionLoophole(
                id="loophole-blur-cracks",
                title="Masked Micro-Cracks & Weld Fissures",
                severity=blur_severity,
                category="Optical Blindspot",
                vulnerability_in_original=f"Motion blur (variance {blur_score:.1f}) smudges sub-millimeter edges, making hairline crossarm cracks and weld toe fissures invisible in the original photo.",
                restoration_fix="High-frequency pyramidal deconvolution sharpens edge gradients, isolating linear defect boundaries.",
                action_required="Inspect lattice joint gussets and weld seams at 1:1 zoom for dark linear indications.",
            )
        )

    if haze_severity in (Severity.HIGH, Severity.MEDIUM):
        hints.append(haze_hint)
        loopholes.append(
            InspectionLoophole(
                id="loophole-haze-insulators",
                title="Insulator Shed Contamination & Hardware Washout",
                severity=haze_severity,
                category="Atmospheric Blindspot",
                vulnerability_in_original=f"Atmospheric airlight scatter (score {haze_score:.3f}) washes out contrast, concealing insulator bell skirts and shadow gaps under bolt washers.",
                restoration_fix="Dark Channel Prior transmission refinement removes distance haze and restores deep shadow contrast.",
                action_required="Check glass/porcelain bell undersides for salt crust or flashover burn tracking.",
            )
        )

    if noise_severity in (Severity.HIGH, Severity.MEDIUM):
        hints.append(noise_hint)
        loopholes.append(
            InspectionLoophole(
                id="loophole-noise-pitting",
                title="Sensor Noise Masking & False Pitting",
                severity=noise_severity,
                category="Sensor Grain Artifact",
                vulnerability_in_original=f"High ISO sensor grain (sigma {noise_estimate:.1f}) creates false speckle that conceals genuine surface rust flaking.",
                restoration_fix="Non-Local Means denoising suppresses random sensor variance while preserving true metallic contours.",
                action_required="Differentiate between true metal corrosion pitting and camera sensor noise floor.",
            )
        )

    if contrast_severity in (Severity.HIGH, Severity.MEDIUM):
        hints.append(contrast_hint)
        loopholes.append(
            InspectionLoophole(
                id="loophole-contrast-shadows",
                title="Shadow-Clipped Base Corrosion Blindspot",
                severity=contrast_severity,
                category="Dynamic Range Loss",
                vulnerability_in_original=f"Compressed dynamic range (RMS {contrast_score:.3f}) plunges tower base legs and pipeline bottom dead-center into black shadows.",
                restoration_fix="Local contrast CLAHE in LAB space expands shadow details without clipping sky highlights.",
                action_required="Inspect tower base legs and foundation interfaces for soil-line section loss.",
            )
        )

    if resolution_flag:
        hints.append(
            f"Image shorter side is {shorter_side}px (< {thresholds.resolution.min_shorter_side}px); super-resolution recommended."
        )
        loopholes.append(
            InspectionLoophole(
                id="loophole-res-fasteners",
                title="Sub-Millimeter Fastener Disconnection Risk",
                severity=Severity.MEDIUM,
                category="Resolution Limitation",
                vulnerability_in_original=f"Low pixel density ({shorter_side}px shorter edge) prevents reliable confirmation of cotter key spreads and loose nuts.",
                restoration_fix="Tiled 2x Super-Resolution magnifies connection points to full diagnostic inspection resolution.",
                action_required="Verify vibration damper cotter keys and conductor clamp bolts using 3x loupe magnifier.",
            )
        )

    if not hints:
        hints.append("Image is in good optical condition; minimal enhancement required.")

    return DegradationReport(
        blur=DegradationMetric(
            score=round(blur_score, 2),
            severity=blur_severity,
            label=blur_label,
            hint=blur_hint,
        ),
        haze=DegradationMetric(
            score=round(haze_score, 4),
            severity=haze_severity,
            label=haze_label,
            hint=haze_hint,
        ),
        noise=DegradationMetric(
            score=round(noise_estimate, 2),
            severity=noise_severity,
            label=noise_label,
            hint=noise_hint,
        ),
        contrast=DegradationMetric(
            score=round(contrast_score, 4),
            severity=contrast_severity,
            label=contrast_label,
            hint=contrast_hint,
        ),
        resolution_flag=resolution_flag,
        dimensions=[w, h],
        hints=hints,
        loopholes=loopholes,
    )
