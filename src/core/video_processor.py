"""Procesamiento y metadata de video via ffmpeg-python"""
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
import ffmpeg


@dataclass
class VideoSpec:
    """Especificación de video"""
    width: int
    height: int
    fps: int
    bitrate: str
    codec: str = "libx264"
    preset: str = "medium"  # ultrafast, fast, medium, slow, slower


class VideoProcessor:
    """Lectura de metadata y operaciones FFmpeg"""

    def __init__(self, temp_dir: Path):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def get_video_info(self, path: str) -> Optional[Dict[str, Any]]:
        """Devuelve dict con width, height, fps, duration. None si falla."""
        if not Path(path).exists():
            return None
        try:
            probe = ffmpeg.probe(path)
        except ffmpeg.Error:
            return None
        video_stream = next(
            (s for s in probe["streams"] if s["codec_type"] == "video"),
            None,
        )
        if video_stream is None:
            return None
        fps_str = video_stream.get("r_frame_rate", "30/1")
        num, den = fps_str.split("/")
        fps = int(round(float(num) / float(den))) if float(den) != 0 else 30
        return {
            "width": int(video_stream["width"]),
            "height": int(video_stream["height"]),
            "fps": fps,
            "duration": float(probe["format"].get("duration", 0.0)),
            "codec": video_stream.get("codec_name", "unknown"),
        }

    def trim(self, input_path: str, output_path: str, start: float, duration: float) -> bool:
        """Recortar video (stub)"""
        return True

    def resize(self, input_path: str, output_path: str, width: int, height: int) -> bool:
        """Redimensionar video (stub)"""
        return True

    def render(self, timeline, spec: VideoSpec, output_path: str) -> bool:
        """Renderizar timeline a video (stub)"""
        return True
