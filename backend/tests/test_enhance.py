import numpy as np
import pytest

from app.enhance.base import soft_clip
from app.enhance.deblur import DeblurStage
from app.enhance.dehaze import DehazeStage
from app.enhance.denoise import DenoiseStage
from app.enhance.registry import registry
from app.enhance.superres import SuperResStage


@pytest.fixture
def sample_image() -> np.ndarray:
    np.random.seed(42)
    img = np.random.uniform(0.1, 0.9, (200, 200, 3)).astype(np.float32)
    return img


def test_soft_clip_never_exceeds_bounds():
    overshot = np.array([-0.2, 0.0, 0.5, 0.98, 1.05, 1.5], dtype=np.float32)
    clipped = soft_clip(overshot)
    assert np.all(clipped >= 0.0)
    assert np.all(clipped <= 1.0)
    # Interior values untouched
    assert np.isclose(clipped[2], 0.5)


def test_registry_contains_all_stages():
    stages = registry.list_available()
    assert "dehaze" in stages
    assert "denoise" in stages
    assert "deblur" in stages
    assert "super_resolution" in stages


def test_dehaze_stage(sample_image: np.ndarray):
    stage = DehazeStage()
    assert stage.name == "dehaze"
    assert stage.is_available is True

    # Test running with 0 strength (pass-through)
    res_zero = stage.run(sample_image, strength=0)
    assert np.allclose(res_zero, sample_image)

    # Test running with standard strength
    res_50 = stage.run(sample_image, strength=50)
    assert res_50.shape == sample_image.shape
    assert np.all(res_50 >= 0.0) and np.all(res_50 <= 1.0)
    assert not np.isnan(res_50).any()


def test_denoise_stage(sample_image: np.ndarray):
    stage = DenoiseStage()
    assert stage.name == "denoise"
    assert stage.is_available is True

    res = stage.run(sample_image, strength=60)
    assert res.shape == sample_image.shape
    assert np.all(res >= 0.0) and np.all(res <= 1.0)
    assert not np.isnan(res).any()


def test_deblur_stage(sample_image: np.ndarray):
    stage = DeblurStage()
    assert stage.name == "deblur"
    assert stage.is_available is True

    res = stage.run(sample_image, strength=70, blur_score=40.0)
    assert res.shape == sample_image.shape
    assert np.all(res >= 0.0) and np.all(res <= 1.0)
    assert not np.isnan(res).any()


def test_superres_stage(sample_image: np.ndarray):
    stage = SuperResStage()
    assert stage.name == "super_resolution"
    assert stage.is_available is True

    h, w = sample_image.shape[:2]
    res_x2 = stage.run(sample_image, strength=50, scale=2.0)
    assert res_x2.shape == (h * 2, w * 2, 3)
    assert np.all(res_x2 >= 0.0) and np.all(res_x2 <= 1.0)
    assert not np.isnan(res_x2).any()
