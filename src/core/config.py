"""Configuracion global del editor"""
from pathlib import Path
from typing import Dict, Any, Tuple


class Config:
    """Configuracion de la aplicacion (singleton)"""

    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    TEMP_DIR = PROJECT_ROOT / "temp"
    PROJECTS_DIR = PROJECT_ROOT / "projects"
    ASSETS_DIR = PROJECT_ROOT / "assets"
    STYLES_DIR = ASSETS_DIR / "styles"

    SUPPORTED_VIDEO = (".mp4", ".mov", ".avi", ".mkv", ".webm")
    SUPPORTED_AUDIO = (".mp3", ".wav", ".aac", ".flac")
    SUPPORTED_IMAGE = (".png", ".jpg", ".jpeg", ".gif", ".bmp")

    DEFAULT_FPS = 30
    DEFAULT_RESOLUTION: Tuple[int, int] = (1920, 1080)
    DEFAULT_BITRATE = "8000k"

    def __init__(self):
        self._create_dirs()
        self.preferences: Dict[str, Any] = {
            "theme": "dark",
            "default_fps": self.DEFAULT_FPS,
            "default_resolution": self.DEFAULT_RESOLUTION,
            "default_bitrate": self.DEFAULT_BITRATE,
            "snap_enabled": True,
            "timeline_zoom": 1.0,
        }

    def _create_dirs(self) -> None:
        for d in (self.TEMP_DIR, self.PROJECTS_DIR, self.ASSETS_DIR, self.STYLES_DIR):
            d.mkdir(parents=True, exist_ok=True)


config = Config()
