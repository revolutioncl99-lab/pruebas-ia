"""Configuración global del editor"""
import os
from pathlib import Path
from typing import Dict, Any

class Config:
    """Configuración de la aplicación"""

    PROJECT_ROOT = Path(__file__).parent.parent
    TEMP_DIR = PROJECT_ROOT / "temp"
    PROJECTS_DIR = PROJECT_ROOT / "projects"

    # Formatos soportados
    SUPPORTED_VIDEO = (".mp4", ".mov", ".avi", ".mkv", ".webm")
    SUPPORTED_AUDIO = (".mp3", ".wav", ".aac", ".flac")
    SUPPORTED_IMAGE = (".png", ".jpg", ".jpeg", ".gif", ".bmp")

    # Configuración de renderizado
    DEFAULT_FPS = 30
    DEFAULT_RESOLUTION = (1920, 1080)
    DEFAULT_BITRATE = "8000k"

    def __init__(self):
        self.create_dirs()
        self.preferences: Dict[str, Any] = {}

    def create_dirs(self):
        """Crear directorios necesarios"""
        self.TEMP_DIR.mkdir(exist_ok=True)
        self.PROJECTS_DIR.mkdir(exist_ok=True)

config = Config()
