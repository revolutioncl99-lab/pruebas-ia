"""Tests para core.timeline"""
import pytest
from src.core.timeline import Clip, Track, Timeline, TrackType


def make_clip(cid="c1", start=0.0, duration=5.0, track_id="t1"):
    return Clip(id=cid, name=cid, source="/x.mp4", start=start, duration=duration, track_id=track_id)


def test_timeline_add_track():
    tl = Timeline()
    tl.add_track(Track(id="t1", name="Video 1", type=TrackType.VIDEO))
    assert len(tl.tracks) == 1
    assert tl.get_track("t1").name == "Video 1"


def test_timeline_add_clip_to_existing_track():
    tl = Timeline()
    tl.add_track(Track(id="t1", name="V1", type=TrackType.VIDEO))
    tl.add_clip("t1", make_clip())
    assert len(tl.get_track("t1").clips) == 1


def test_timeline_add_clip_to_missing_track_raises():
    tl = Timeline()
    with pytest.raises(ValueError, match="track_id"):
        tl.add_clip("nope", make_clip())


def test_timeline_remove_clip():
    tl = Timeline()
    tl.add_track(Track(id="t1", name="V1", type=TrackType.VIDEO))
    tl.add_clip("t1", make_clip(cid="c1"))
    tl.remove_clip("c1")
    assert len(tl.get_track("t1").clips) == 0


def test_timeline_move_clip():
    tl = Timeline()
    tl.add_track(Track(id="t1", name="V1", type=TrackType.VIDEO))
    tl.add_clip("t1", make_clip(cid="c1", start=0.0, duration=5.0))
    tl.move_clip("c1", new_start=10.0)
    assert tl.get_clip("c1").start == 10.0


def test_timeline_get_clip_at():
    tl = Timeline()
    tl.add_track(Track(id="t1", name="V1", type=TrackType.VIDEO))
    tl.add_clip("t1", make_clip(cid="c1", start=2.0, duration=3.0))
    assert tl.get_clip_at("t1", 3.5).id == "c1"
    assert tl.get_clip_at("t1", 10.0) is None


def test_timeline_clips_overlap_detected():
    tl = Timeline()
    tl.add_track(Track(id="t1", name="V1", type=TrackType.VIDEO))
    tl.add_clip("t1", make_clip(cid="c1", start=0.0, duration=5.0))
    with pytest.raises(ValueError, match="overlap"):
        tl.add_clip("t1", make_clip(cid="c2", start=3.0, duration=4.0))


def test_timeline_total_duration():
    tl = Timeline()
    tl.add_track(Track(id="t1", name="V1", type=TrackType.VIDEO))
    tl.add_clip("t1", make_clip(cid="c1", start=0.0, duration=5.0))
    tl.add_clip("t1", make_clip(cid="c2", start=10.0, duration=3.0))
    assert tl.total_duration() == 13.0
