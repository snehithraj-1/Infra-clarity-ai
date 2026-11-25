from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import cv2
import numpy as np

from app.metrics.quality import compute_metrics
from app.schemas import CloseRangePatternImage, DegradationReport


def detect_structural_patterns(
    image_float: np.ndarray,
    report: Optional[DegradationReport] = None,
) -> List[Dict[str, Any]]:
    """
    Analyzes visual patterns, structural density, and gradient salience in the input image.
    Identifies 3 to 4 distinct critical component regions of interest (ROIs).
    """
    h, w = image_float.shape[:2]
    gray = cv2.cvtColor(image_float, cv2.COLOR_RGB2GRAY)
    
    # Compute high-frequency Sobel gradient magnitude
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1)
    mag = cv2.magnitude(gx, gy)

    # Asset aspect ratio heuristic
    aspect = h / max(1, w)
    patterns: List[Dict[str, Any]] = []

    if aspect > 1.2:
        # Vertical Tower / Mast / Tall Insulator Asset
        pattern_templates = [
            {
                "id": "roi_apex_mast",
                "label": "Tower Apex & Mast Head",
                "category": "Overhead Structural Assembly",
                "description": "Close-range macro inspection of top structural rivets, mast connection, and skyward wire brackets.",
                "y_range": (0.04, 0.30),
                "box_aspect": (0.45, 0.22),
            },
            {
                "id": "roi_crossarm_joint",
                "label": "Crossarm Gusset & Bolt Cluster",
                "category": "Mechanical Load-Bearing Joint",
                "description": "Micro-crack audit of crossarm junction, gusset plate, and insulator hanger fasteners.",
                "y_range": (0.28, 0.55),
                "box_aspect": (0.50, 0.24),
            },
            {
                "id": "roi_lattice_splice",
                "label": "Diagonal Lattice Bracing Splice",
                "category": "Structural Member Splice",
                "description": "High-acuity resolution of diagonal member overlap, vibration damper fatigue, and shear bolt threads.",
                "y_range": (0.48, 0.74),
                "box_aspect": (0.52, 0.24),
            },
            {
                "id": "roi_base_flange",
                "label": "Lower Structural Leg & Flange",
                "category": "Primary Compression Member",
                "description": "Close-range inspection of main tower leg section loss, foundation interface, and flange bolts.",
                "y_range": (0.65, 0.88),
                "box_aspect": (0.55, 0.22),
            },
        ]
    elif aspect < 0.8:
        # Horizontal Pipeline / Span / Substation Asset
        pattern_templates = [
            {
                "id": "roi_pipe_weld",
                "label": "Longitudinal Weld Seam & Toe",
                "category": "Weld Integrity & Fissure Zone",
                "description": "High-magnification audit of fusion weld line, HAZ (Heat Affected Zone), and hairline stress cracks.",
                "y_range": (0.20, 0.70),
                "box_aspect": (0.35, 0.40),
            },
            {
                "id": "roi_flange_bolts",
                "label": "Flange Coupling & Fastener Ring",
                "category": "Pressure Boundary Junction",
                "description": "Micro-inspection of bolt tensioning, gasket seal interface, and nut thread engagement.",
                "y_range": (0.20, 0.70),
                "box_aspect": (0.35, 0.45),
            },
            {
                "id": "roi_surface_corrosion",
                "label": "Surface Section Loss & Rust Pitting",
                "category": "Corrosion & Material Loss",
                "description": "Close-range texture recovery separating true metallic pitting from surface scale and flaking.",
                "y_range": (0.25, 0.75),
                "box_aspect": (0.35, 0.38),
            },
        ]
    else:
        # Square / Insulator Disc / General Equipment Frame
        pattern_templates = [
            {
                "id": "roi_upper_hardware",
                "label": "Upper Hardware & Fitting Junction",
                "category": "Mechanical Attachment",
                "description": "Close-range focus on upper mounting pins, cotter keys, and connection clamp integrity.",
                "y_range": (0.08, 0.40),
                "box_aspect": (0.45, 0.32),
            },
            {
                "id": "roi_core_component",
                "label": "Central Core & Shed Skirt Assembly",
                "category": "Primary Dielectric / Structural Core",
                "description": "High-acuity resolution of shed bells, porcelain/glass skirt contours, and surface contamination tracking.",
                "y_range": (0.35, 0.65),
                "box_aspect": (0.48, 0.34),
            },
            {
                "id": "roi_lower_terminal",
                "label": "Lower Terminal & Fastener Clamp",
                "category": "Bottom Termination",
                "description": "Close-range inspection of lower grounding lead clamp, lock nuts, and stress-bearing hardware.",
                "y_range": (0.60, 0.90),
                "box_aspect": (0.45, 0.32),
            },
        ]

    for p in pattern_templates:
        y0_f, y1_f = p["y_range"]
        y0 = int(y0_f * h)
        y1 = max(y0 + 10, int(y1_f * h))
        slice_mag = mag[y0:y1, :]

        if slice_mag.size > 0:
            max_idx = np.unravel_index(np.argmax(slice_mag), slice_mag.shape)
            peak_y = y0 + max_idx[0]
            peak_x = max_idx[1]
        else:
            peak_y = (y0 + y1) // 2
            peak_x = w // 2

        bw_f, bh_f = p["box_aspect"]
        bw = max(32, min(w, int(bw_f * w)))
        bh = max(32, min(h, int(bh_f * h)))

        bx0 = max(0, min(w - bw, peak_x - bw // 2))
        by0 = max(0, min(h - bh, peak_y - bh // 2))
        bx1 = bx0 + bw
        by1 = by0 + bh

        patterns.append({
            "id": p["id"],
            "label": p["label"],
            "category": p["category"],
            "description": p["description"],
            "box_norm": [
                round(by0 / h, 4),
                round(bx0 / w, 4),
                round(by1 / h, 4),
                round(bx1 / w, 4),
            ],
            "box_px": (bx0, by0, bx1, by1),
        })

    return patterns


def generate_close_range_pattern_images(
    job_id: str,
    original_image: np.ndarray,
    enhanced_image: np.ndarray,
    crops_dir: Path,
    report: Optional[DegradationReport] = None,
    superres_stage: Optional[Any] = None,
) -> List[CloseRangePatternImage]:
    """
    Generates high-magnification, close-range macro enhanced images for each detected pattern in the image.
    Crops the original and enhanced image, applies a close-range magnification & micro-detail boost pass,
    and saves the images for interactive gallery inspection.
    """
    crops_dir.mkdir(parents=True, exist_ok=True)
    detected = detect_structural_patterns(original_image, report)

    h_orig, w_orig = original_image.shape[:2]
    h_enh, w_enh = enhanced_image.shape[:2]
    scale_y = h_enh / float(h_orig)
    scale_x = w_enh / float(w_orig)

    close_range_images: List[CloseRangePatternImage] = []

    for item in detected:
        cid = item["id"]
        bx0, by0, bx1, by1 = item["box_px"]

        # 1. Original close-range crop
        orig_crop = original_image[by0:by1, bx0:bx1]

        # 2. Enhanced close-range crop (scaled to enhanced resolution)
        by0_enh = int(round(by0 * scale_y))
        by1_enh = int(round(by1 * scale_y))
        bx0_enh = int(round(bx0 * scale_x))
        bx1_enh = int(round(bx1 * scale_x))

        by0_enh = max(0, min(h_enh - 1, by0_enh))
        by1_enh = max(by0_enh + 10, min(h_enh, by1_enh))
        bx0_enh = max(0, min(w_enh - 1, bx0_enh))
        bx1_enh = max(bx0_enh + 10, min(w_enh, bx1_enh))

        enh_crop = enhanced_image[by0_enh:by1_enh, bx0_enh:bx1_enh]

        # 3. Apply close-range macro super-resolution & micro-detail boost
        if superres_stage and hasattr(superres_stage, "run") and enh_crop.size > 0:
            try:
                macro_crop = superres_stage.run(enh_crop, strength=80, scale=1.5)
            except Exception:
                macro_crop = cv2.resize(enh_crop, (int(enh_crop.shape[1] * 1.5), int(enh_crop.shape[0] * 1.5)), interpolation=cv2.INTER_LANCZOS4)
        else:
            macro_crop = cv2.resize(enh_crop, (int(enh_crop.shape[1] * 1.5), int(enh_crop.shape[0] * 1.5)), interpolation=cv2.INTER_LANCZOS4)

        # 4. Save both original crop and close-range enhanced crop
        orig_save_path = crops_dir / f"{cid}_orig.png"
        enh_save_path = crops_dir / f"{cid}_enh.png"

        orig_bgr = cv2.cvtColor((np.clip(orig_crop, 0.0, 1.0) * 255.0).astype(np.uint8), cv2.COLOR_RGB2BGR)
        enh_bgr = cv2.cvtColor((np.clip(macro_crop, 0.0, 1.0) * 255.0).astype(np.uint8), cv2.COLOR_RGB2BGR)

        cv2.imwrite(str(orig_save_path), orig_bgr)
        cv2.imwrite(str(enh_save_path), enh_bgr)

        # 5. Local quality metrics
        metrics = compute_metrics(orig_crop, macro_crop)

        close_range_images.append(
            CloseRangePatternImage(
                id=cid,
                label=item["label"],
                category=item["category"],
                description=item["description"],
                bounding_box=item["box_norm"],
                original_crop_url=f"/api/v1/jobs/{job_id}/crops/{cid}/original",
                enhanced_crop_url=f"/api/v1/jobs/{job_id}/crops/{cid}/enhanced",
                detail_gain=round(metrics.detail_gain, 1),
                canny_gain=round(metrics.canny_gain, 1),
            )
        )

    return close_range_images
