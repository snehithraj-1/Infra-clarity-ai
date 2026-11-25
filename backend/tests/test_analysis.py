import cv2
import numpy as np
import pytest

from app.analysis.degradation import (
    analyze_degradations,
    compute_blur_score,
    compute_contrast_score,
    compute_haze_score,
    compute_noise_estimate,
)
from app.config import AppConfig, load_config
from app.schemas import Severity


@pytest.fixture
def sharp_image() -> np.ndarray:
    # High-contrast checkerboard with sharp edges
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    for i in range(0, 300, 30):
        for j in range(0, 300, 30):
            if (i // 30 + j // 30) % 2 == 0:
                img[i : i + 30, j : j + 30] = 255
    return img


@pytest.fixture
def blurred_image(sharp_image: np.ndarray) -> np.ndarray:
    # Heavily blurred image
    return cv2.GaussianBlur(sharp_image, (41, 41), sigmaX=15.0)


@pytest.fixture
def hazy_image(sharp_image: np.ndarray) -> np.ndarray:
    # Synthesize haze via atmospheric scattering model: I = J*t + A*(1-t)
    norm = sharp_image.astype(np.float32) / 255.0
    t = 0.2  # Low transmission (dense haze)
    airlight = 0.95
    hazy = norm * t + airlight * (1.0 - t)
    return (np.clip(hazy, 0.0, 1.0) * 255.0).astype(np.uint8)


@pytest.fixture
def noisy_image(sharp_image: np.ndarray) -> np.ndarray:
    # Add Gaussian noise with standard deviation of 30 (out of 255)
    np.random.seed(42)
    noise = np.random.normal(0, 30, sharp_image.shape)
    noisy = np.clip(sharp_image.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return noisy


@pytest.fixture
def low_contrast_image() -> np.ndarray:
    # Near-uniform gray image (low dynamic range)
    base = np.full((300, 300, 3), 120, dtype=np.uint8)
    noise = np.random.normal(0, 2, base.shape)
    return np.clip(base.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def test_blur_score_distinguishes_sharp_and_blurred(sharp_image: np.ndarray, blurred_image: np.ndarray):
    sharp_gray = cv2.cvtColor(sharp_image, cv2.COLOR_RGB2GRAY)
    blurred_gray = cv2.cvtColor(blurred_image, cv2.COLOR_RGB2GRAY)

    sharp_score = compute_blur_score(sharp_gray)
    blurred_score = compute_blur_score(blurred_gray)

    assert sharp_score > blurred_score * 10
    assert sharp_score > 500.0
    assert blurred_score < 50.0


def test_haze_score_distinguishes_clear_and_hazy(sharp_image: np.ndarray, hazy_image: np.ndarray):
    clear_norm = sharp_image.astype(np.float32) / 255.0
    hazy_norm = hazy_image.astype(np.float32) / 255.0

    clear_haze = compute_haze_score(clear_norm)
    hazy_haze = compute_haze_score(hazy_norm)

    assert hazy_haze > clear_haze * 2
    assert hazy_haze > 0.4


def test_noise_estimate_distinguishes_clean_and_noisy(sharp_image: np.ndarray, noisy_image: np.ndarray):
    clean_norm = sharp_image.astype(np.float32) / 255.0
    noisy_norm = noisy_image.astype(np.float32) / 255.0

    clean_sigma = compute_noise_estimate(clean_norm)
    noisy_sigma = compute_noise_estimate(noisy_norm)

    assert noisy_sigma > clean_sigma * 2
    assert noisy_sigma > 10.0


def test_contrast_score_identifies_low_contrast(sharp_image: np.ndarray, low_contrast_image: np.ndarray):
    sharp_gray = cv2.cvtColor(sharp_image, cv2.COLOR_RGB2GRAY) / 255.0
    low_gray = cv2.cvtColor(low_contrast_image, cv2.COLOR_RGB2GRAY) / 255.0

    sharp_rms = compute_contrast_score(sharp_gray)
    low_rms = compute_contrast_score(low_gray)

    assert sharp_rms > low_rms * 5
    assert low_rms < 0.05


def test_analyze_degradations_severities(blurred_image: np.ndarray, hazy_image: np.ndarray, noisy_image: np.ndarray):
    cfg = load_config()

    report_blur = analyze_degradations(blurred_image, cfg)
    assert report_blur.blur.severity in (Severity.HIGH, Severity.MEDIUM)

    report_haze = analyze_degradations(hazy_image, cfg)
    assert report_haze.haze.severity in (Severity.HIGH, Severity.MEDIUM)

    report_noise = analyze_degradations(noisy_image, cfg)
    assert report_noise.noise.severity in (Severity.HIGH, Severity.MEDIUM)


def test_resolution_flag():
    cfg = load_config()
    small_img = np.random.randint(50, 200, (800, 600, 3), dtype=np.uint8)
    large_img = np.random.randint(50, 200, (1200, 1600, 3), dtype=np.uint8)

    report_small = analyze_degradations(small_img, cfg)
    report_large = analyze_degradations(large_img, cfg)

    assert report_small.resolution_flag is True
    assert report_large.resolution_flag is False
    assert report_small.dimensions == [600, 800]
    assert report_large.dimensions == [1600, 1200]
