"""Tests para core.video_processor"""
import subprocess
from pathlib import Path
import pytest
from src.core.video_processor import VideoProcessor, VideoSpec


@pytest.fixture
def sample_video(tmp_path):
    """Genera un mp4 de 2 segundos con FFmpeg para tests"""
    out = tmp_path / "sample.mp4"
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", "color=c=red:s=320x240:d=2:r=30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(out),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except FileNotFoundError:
        pytest.skip("FFmpeg no encontrado en PATH")
    if result.returncode != 0:
        pytest.skip(f"FFmpeg no disponible: {result.stderr[:200]}")
    return out


def test_get_video_info_real_file(tmp_path, sample_video):
    proc = VideoProcessor(temp_dir=tmp_path)
    info = proc.get_video_info(str(sample_video))
    assert info is not None
    assert info["width"] == 320
    assert info["height"] == 240
    assert info["fps"] == 30
    assert 1.9 <= info["duration"] <= 2.1


def test_get_video_info_missing_file(tmp_path):
    proc = VideoProcessor(temp_dir=tmp_path)
    assert proc.get_video_info("/nope/missing.mp4") is None


def test_video_spec_defaults():
    spec = VideoSpec(width=1920, height=1080, fps=30, bitrate="8000k")
    assert spec.codec == "libx264"
    assert spec.preset == "medium"
