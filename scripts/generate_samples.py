#!/usr/bin/env python3
"""
Generates procedural reference infrastructure inspection imagery for testing:
1. tower_joint.png - Transmission tower lattice joint with structural bolts and steel trusses
2. pipeline_weld.png - Pipeline steel section with circumferential weld and hairline stress defect
3. insulator_string.png - High-voltage suspension insulator string with ceramic disc sheds
"""

import os
from pathlib import Path
import cv2
import numpy as np


def generate_tower_joint() -> np.ndarray:
    w, h = 800, 600
    # Subtle sky background with vertical luminance gradient
    sky = np.linspace(220, 180, h, dtype=np.float32)[:, np.newaxis]
    img = np.tile(sky, (1, w))
    img = np.stack([img * 0.9, img * 0.95, img], axis=-1).astype(np.uint8)

    # Steel truss elements (dark industrial steel #475569)
    truss_color = (71, 85, 105)
    plate_color = (51, 65, 85)
    highlight_color = (148, 163, 184)
    shadow_color = (30, 41, 59)

    # Main diagonal strut
    cv2.line(img, (50, 550), (750, 50), shadow_color, 42)
    cv2.line(img, (50, 550), (750, 50), truss_color, 36)
    cv2.line(img, (52, 548), (748, 52), highlight_color, 2)

    # Counter diagonal strut
    cv2.line(img, (50, 50), (750, 550), shadow_color, 42)
    cv2.line(img, (50, 50), (750, 550), truss_color, 36)
    cv2.line(img, (52, 52), (748, 548), highlight_color, 2)

    # Horizontal cross-member
    cv2.line(img, (50, 300), (750, 300), shadow_color, 48)
    cv2.line(img, (50, 300), (750, 300), truss_color, 42)

    # Central gusset junction plate (octagon)
    pts = np.array([[330, 240], [470, 240], [530, 300], [470, 360], [330, 360], [270, 300]], np.int32)
    cv2.fillPoly(img, [pts], plate_color)
    cv2.polylines(img, [pts], True, highlight_color, 2)

    # Hexagonal bolts and rivets around gusset plate
    bolt_locs = [
        (350, 265), (400, 255), (450, 265),
        (300, 300), (400, 300), (500, 300),
        (350, 335), (400, 345), (450, 335),
        (200, 200), (600, 200), (200, 400), (600, 400),
    ]
    for bx, by in bolt_locs:
        # Outer bolt shadow
        cv2.circle(img, (bx, by), 11, (20, 25, 35), -1)
        # Bolt head
        cv2.circle(img, (bx, by), 9, (100, 116, 139), -1)
        # Highlight
        cv2.circle(img, (bx - 2, by - 2), 4, (203, 213, 225), -1)
        # Threaded center
        cv2.circle(img, (bx, by), 2, (30, 41, 59), -1)

    return img


def generate_pipeline_weld() -> np.ndarray:
    w, h = 800, 600
    # Steel pipe metallic curvature background
    x = np.linspace(-1.0, 1.0, w, dtype=np.float32)
    cylinder_profile = np.cos(x * (np.pi / 2.4))
    pipe = (cylinder_profile[np.newaxis, :] * 160 + 40).astype(np.float32)
    img = np.stack([pipe * 0.92, pipe * 0.95, pipe * 0.98], axis=-1).astype(np.uint8)

    # Add steel surface rolling texture and mill scale
    np.random.seed(101)
    noise = np.random.normal(0, 5, (h, w, 3)).astype(np.float32)
    img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    # Circumferential weld bead vertically across center
    weld_x = 400
    for y in range(h):
        jitter = int(np.sin(y / 8.0) * 3 + np.cos(y / 3.0) * 2)
        wx = weld_x + jitter
        # Weld crown
        cv2.line(img, (wx - 10, y), (wx + 10, y), (140, 145, 155), 1)
        # Weld ripples
        if y % 6 in (0, 1):
            cv2.line(img, (wx - 8, y), (wx + 8, y), (180, 185, 195), 1)
            cv2.line(img, (wx - 11, y), (wx - 9, y), (60, 65, 75), 1)
            cv2.line(img, (wx + 9, y), (wx + 11, y), (60, 65, 75), 1)

    # Localized surface corrosion / rust pitting patch
    for _ in range(250):
        rx = int(np.random.normal(260, 30))
        ry = int(np.random.normal(320, 40))
        if 0 <= rx < w and 0 <= ry < h:
            radius = np.random.randint(2, 7)
            # Rust color (orange-brown iron oxide: #9a3412)
            cv2.circle(img, (rx, ry), radius, (30, 60, 150), -1)

    # Critical hairline stress crack emanating from heat-affected zone (HAZ)
    crack_pts = [(415, 220), (418, 235), (423, 248), (421, 260), (426, 275), (430, 290)]
    for i in range(len(crack_pts) - 1):
        cv2.line(img, crack_pts[i], crack_pts[i + 1], (15, 15, 20), 2)
        # Micro-fissure branch
        if i == 2:
            cv2.line(img, crack_pts[i], (crack_pts[i][0] + 12, crack_pts[i][1] + 10), (25, 25, 30), 1)

    return img


def generate_insulator_string() -> np.ndarray:
    w, h = 800, 600
    # Overcast outdoor background
    img = np.full((h, w, 3), 195, dtype=np.uint8)

    # Central metal conductor spindle
    cv2.line(img, (400, 30), (400, 570), (70, 75, 85), 12)

    # 5 Ceramic disc insulator sheds
    shed_y_positions = [110, 190, 270, 350, 430]
    for sy in shed_y_positions:
        # Upper ceramic bell shade (toughened amber/brown glass: #78350f)
        cv2.ellipse(img, (400, sy), (130, 35), 0, 0, 360, (40, 70, 140), -1)
        # Highlight rim
        cv2.ellipse(img, (400, sy - 4), (126, 30), 0, 180, 360, (90, 130, 200), 3)
        # Underside shadow and rib grooves
        cv2.ellipse(img, (400, sy + 6), (120, 26), 0, 0, 180, (20, 40, 80), -1)
        # Inter-unit galvanized steel cap & pin coupling
        cv2.rectangle(img, (386, sy + 25), (414, sy + 55), (90, 95, 105), -1)
        cv2.circle(img, (400, sy + 40), 5, (40, 45, 55), -1)

    # Damaged / chipped porcelain defect on shed #3
    chip_center = (490, 275)
    cv2.circle(img, chip_center, 16, (230, 230, 235), -1)  # Exposed white unglazed core
    cv2.circle(img, chip_center, 16, (30, 35, 45), 2)      # Fracture shadow boundary

    return img


def main():
    out_dir = Path("samples/clean")
    out_dir.mkdir(parents=True, exist_ok=True)

    tower = generate_tower_joint()
    pipeline = generate_pipeline_weld()
    insulator = generate_insulator_string()

    cv2.imwrite(str(out_dir / "tower_joint.png"), cv2.cvtColor(tower, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(out_dir / "pipeline_weld.png"), cv2.cvtColor(pipeline, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(out_dir / "insulator_string.png"), cv2.cvtColor(insulator, cv2.COLOR_RGB2BGR))

    print(f"Generated 3 reference inspection images in {out_dir}")


if __name__ == "__main__":
    main()
