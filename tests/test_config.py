"""Tests para core.config"""
import pytest
from pathlib import Path
from src.core.config import Config


def test_config_creates_required_dirs(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(Config, "TEMP_DIR", tmp_path / "temp")
    monkeypatch.setattr(Config, "PROJECTS_DIR", tmp_path / "projects")
    monkeypatch.setattr(Config, "ASSETS_DIR", tmp_path / "assets")
    cfg = Config()
    assert (tmp_path / "temp").exists()
    assert (tmp_path / "projects").exists()
    assert (tmp_path / "assets").exists()


def test_config_default_preferences():
    cfg = Config()
    assert cfg.preferences.get("theme") == "dark"
    assert cfg.preferences.get("default_fps") == 30
    assert cfg.preferences.get("default_resolution") == (1920, 1080)


def test_config_supported_formats():
    assert ".mp4" in Config.SUPPORTED_VIDEO
    assert ".mp3" in Config.SUPPORTED_AUDIO
    assert ".png" in Config.SUPPORTED_IMAGE
