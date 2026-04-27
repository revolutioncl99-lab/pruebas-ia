"""Smoke test TimelineWidget"""
import pytest
from PyQt6.QtWidgets import QApplication
from src.core.timeline import Timeline, Track, Clip, TrackType


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_timeline_widget_renders_tracks_and_clips(app, qtbot):
    from src.ui.timeline_widget import TimelineWidget
    tl = Timeline()
    tl.add_track(Track(id="v1", name="Video", type=TrackType.VIDEO))
    tl.add_track(Track(id="a1", name="Audio", type=TrackType.AUDIO))
    tl.add_clip("v1", Clip(id="c1", name="clip1", source="/x.mp4",
                           start=0.0, duration=5.0, track_id="v1"))
    w = TimelineWidget(tl)
    qtbot.addWidget(w)
    assert "c1" in w._clip_items
    assert w._playhead_item is not None


def test_timeline_widget_zoom_via_refresh(app, qtbot):
    from src.ui.timeline_widget import TimelineWidget
    tl = Timeline()
    tl.add_track(Track(id="v1", name="Video", type=TrackType.VIDEO))
    tl.add_clip("v1", Clip(id="c1", name="x", source="/x.mp4",
                           start=0.0, duration=2.0, track_id="v1"))
    w = TimelineWidget(tl)
    qtbot.addWidget(w)
    initial_x = w._clip_items["c1"].rect().width()
    w.zoom = 2.0
    w.refresh()
    new_x = w._clip_items["c1"].rect().width()
    assert new_x > initial_x


def test_timeline_widget_set_playhead(app, qtbot):
    from src.ui.timeline_widget import TimelineWidget
    tl = Timeline()
    tl.add_track(Track(id="v1", name="V", type=TrackType.VIDEO))
    w = TimelineWidget(tl)
    qtbot.addWidget(w)
    w.set_playhead(7.5)
    assert tl.playhead == 7.5
