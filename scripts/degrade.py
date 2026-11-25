#!/usr/bin/env python3
"""
InfraClarity AI - Synthetic Degradation Generator
Simulates realistic drone inspection degradation conditions:
1. Atmospheric haze (Koschmieder atmospheric scattering model)
2. Motion & vibration blur (directional kernel)
3. Sensor & ISO shot noise (additive Gaussian noise)
4. Low light / underexposure (gamma attenuation + shadow noise)
5. Downscaling (distance resolution loss)
6. Combined realistic adverse weather drone conditions
"""

import argparse
import os
from pathlib import Path
import cv2
import numpy as np


def apply_haze(image: np.ndarray, severity: float = 0.65, airlight: float = 0.92) -> np.ndarray:
    """
    Koschmieder atmospheric scattering model:
        I(x) = J(x) * t(x) + A * (1 - t(x))
    Simulates distance-dependent atmospheric attenuation.
    """
    h, w = image.shape[:2]
    # Linear vertical depth map simulating drone looking out across horizon
    y = np.linspace(0.2, 1.0, h, dtype=np.float32)[:, np.newaxis]
    depth = np.tile(y, (1, w))
    beta = 1.2 * severity
    transmission = np.exp(-beta * depth)[:, :, np.newaxis]
    t0 = 0.1
    transmission = np.maximum(transmission, t0)

    hazy = image * transmission + airlight * (1.0 - transmission)
    return np.clip(hazy, 0.0, 1.0)


def apply_motion_blur(image: np.ndarray, kernel_size: int = 15, angle: float = 45.0) -> np.ndarray:
    """
    Simulates drone gimbal jitter and telephoto camera movement blur.
    """
    kernel = np.zeros((kernel_size, kernel_size), dtype=np.float32)
    center = kernel_size // 2
    theta = np.deg2rad(angle)
    dx = np.cos(theta)
    dy = np.sin(theta)

    for i in range(-center, center + 1):
        x = int(round(center + i * dx))
        y = int(round(center + i * dy))
        if 0 <= x < kernel_size and 0 <= y < kernel_size:
            kernel[y, x] = 1.0

    kernel_sum = np.sum(kernel)
    if kernel_sum > 0:
        kernel /= kernel_sum
    else:
        kernel[center, center] = 1.0

    return cv2.filter2D(image, -1, kernel)


def apply_gaussian_noise(image: np.ndarray, sigma_255: float = 25.0) -> np.ndarray:
    """
    Simulates high-gain drone camera sensor shot noise.
    """
    sigma = sigma_255 / 255.0
    noise = np.random.normal(0.0, sigma, image.shape).astype(np.float32)
    return np.clip(image + noise, 0.0, 1.0)


def apply_low_light(image: np.ndarray, gamma: float = 1.8, attenuation: float = 0.35) -> np.ndarray:
    """
    Simulates underexposed dawn/dusk or overcast shadow conditions.
    """
    attenuated = (image * attenuation) ** gamma
    # Add dark-current sensor noise in shadows
    noise = np.random.normal(0.0, 0.02, image.shape).astype(np.float32)
    return np.clip(attenuated + noise, 0.0, 1.0)


def apply_downscale(image: np.ndarray, scale: float = 0.5) -> np.ndarray:
    """
    Simulates standoff distance optical resolution loss.
    """
    h, w = image.shape[:2]
    small = cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    upscaled_back = cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)
    return upscaled_back


def synthesize_degradations(clean_image: np.ndarray, degradation_type: str, seed: int = 42) -> np.ndarray:
    np.random.seed(seed)
    img_float = clean_image.astype(np.float32) / 255.0 if clean_image.dtype == np.uint8 else clean_image

    if degradation_type == "haze":
        degraded = apply_haze(img_float, severity=0.7)
    elif degradation_type == "blur":
        degraded = apply_motion_blur(img_float, kernel_size=19, angle=35.0)
    elif degradation_type == "noise":
        degraded = apply_gaussian_noise(img_float, sigma_255=28.0)
    elif degradation_type == "low_light":
        degraded = apply_low_light(img_float)
    elif degradation_type == "downscale":
        degraded = apply_downscale(img_float, scale=0.4)
    elif degradation_type == "combined":
        # Realistic multi-degradation: overcast haze + distance downscale + camera vibration + sensor noise
        step1 = apply_haze(img_float, severity=0.55)
        step2 = apply_motion_blur(step1, kernel_size=11, angle=25.0)
        step3 = apply_gaussian_noise(step2, sigma_255=16.0)
        degraded = step3
    else:
        raise ValueError(f"Unknown degradation type: {degradation_type}")

    return (np.clip(degraded, 0.0, 1.0) * 255.0).astype(np.uint8)


def main():
    parser = argparse.ArgumentParser(description="Synthesize realistic inspection degradations")
    parser.add_argument("--input-dir", default="samples/clean", help="Folder containing clean reference images")
    parser.add_argument("--output-dir", default="samples/degraded", help="Output folder for degraded images")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    types = ["haze", "blur", "noise", "low_light", "downscale", "combined"]
    clean_files = list(input_dir.glob("*.png")) + list(input_dir.glob("*.jpg"))

    if not clean_files:
        print(f"No reference images found in {input_dir}")
        return

    print(f"Generating synthetic degradations with seed={args.seed} ...")
    count = 0
    for img_path in clean_files:
        clean_img = cv2.imread(str(img_path))
        if clean_img is None:
            continue
        clean_rgb = cv2.cvtColor(clean_img, cv2.COLOR_BGR2RGB)

        for deg_type in types:
            degraded_rgb = synthesize_degradations(clean_rgb, deg_type, seed=args.seed)
            out_filename = f"{img_path.stem}_{deg_type}.png"
            out_path = output_dir / out_filename
            cv2.imwrite(str(out_path), cv2.cvtColor(degraded_rgb, cv2.COLOR_RGB2BGR))
            count += 1

    print(f"Successfully generated {count} degraded images in {output_dir}")


if __name__ == "__main__":
    main()
