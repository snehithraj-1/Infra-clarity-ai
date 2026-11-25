from app.config import load_config, AppConfig


def test_load_config_defaults():
    cfg = load_config()
    assert isinstance(cfg, AppConfig)
    assert cfg.app.name == "InfraClarity AI"
    assert cfg.analysis.blur.severe_threshold > 0
    assert cfg.analysis.haze.severe_threshold > 0
    assert cfg.tiling.tile_size == 512
    assert cfg.tiling.overlap == 32
