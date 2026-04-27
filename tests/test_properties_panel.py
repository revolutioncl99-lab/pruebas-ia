"""Smoke test PropertiesPanel"""
import pytest
from PyQt6.QtWidgets import QApplication
from src.core.timeline import Clip


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_properties_panel_disabled_when_no_clip(app, qtbot):
    from src.ui.properties_panel import PropertiesPanel
    p = PropertiesPanel()
    qtbot.addWidget(p)
    assert not p.group.isEnabled()


def test_properties_panel_populates_from_clip(app, qtbot):
    from src.ui.properties_panel import PropertiesPanel
    p = PropertiesPanel()
    qtbot.addWidget(p)
    clip = Clip(id="c1", name="MyClip", source="/x.mp4",
                start=2.5, duration=10.0, track_id="v1",
                volume=0.8, opacity=0.5)
    p.set_clip(clip)
    assert p.name_edit.text() == "MyClip"
    assert p.start_spin.value() == 2.5
    assert p.duration_spin.value() == 10.0
    assert p.volume_spin.value() == 0.8
    assert p.opacity_spin.value() == 0.5
    assert p.group.isEnabled()
