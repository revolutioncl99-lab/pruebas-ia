"""Tests para core.project"""
import json
from pathlib import Path
import pytest
from src.core.project import Project
from src.core.timeline import Timeline, Track, Clip, TrackType


def test_project_save_creates_json(tmp_path):
    tl = Timeline(fps=30)
    tl.add_track(Track(id="v1", name="Video 1", type=TrackType.VIDEO))
    tl.add_clip("v1", Clip(id="c1", name="clip1", source="/x.mp4",
                           start=0.0, duration=5.0, track_id="v1"))
    p = Project(name="MyProj", timeline=tl)
    out = tmp_path / "proj.json"
    p.save(out)
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["name"] == "MyProj"
    assert data["timeline"]["tracks"][0]["clips"][0]["id"] == "c1"


def test_project_load_roundtrip(tmp_path):
    tl = Timeline(fps=24, duration=120.0)
    tl.add_track(Track(id="a1", name="Audio", type=TrackType.AUDIO))
    tl.add_clip("a1", Clip(id="ac1", name="bg-music", source="/m.mp3",
                           start=2.0, duration=8.0, track_id="a1", volume=0.6))
    p = Project(name="Test", timeline=tl)
    out = tmp_path / "p.json"
    p.save(out)

    loaded = Project.load(out)
    assert loaded.name == "Test"
    assert loaded.timeline.fps == 24
    assert loaded.timeline.tracks[0].id == "a1"
    assert loaded.timeline.tracks[0].clips[0].volume == 0.6


def test_project_load_invalid_file_raises(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json{{")
    with pytest.raises(ValueError, match="JSON"):
        Project.load(bad)


def test_project_load_missing_version_raises(tmp_path):
    f = tmp_path / "f.json"
    f.write_text(json.dumps({"name": "x", "timeline": {}}))
    with pytest.raises(ValueError, match="version"):
        Project.load(f)
