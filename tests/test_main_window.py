"""Smoke test MainWindow"""
import pytest
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_main_window_instantiates(app, qtbot):
    from src.ui.main_window import MainWindow
    w = MainWindow()
    qtbot.addWidget(w)
    assert w.windowTitle().startswith("Editor de Video")
    assert len(w.project.timeline.tracks) == 5


def test_main_window_has_panels(app, qtbot):
    from src.ui.main_window import MainWindow
    from src.ui.preview_widget import PreviewWidget
    from src.ui.tools_panel import ToolsPanel
    from src.ui.properties_panel import PropertiesPanel
    from src.ui.timeline_widget import TimelineWidget
    w = MainWindow()
    qtbot.addWidget(w)
    assert isinstance(w.preview, PreviewWidget)
    assert isinstance(w.tools_panel, ToolsPanel)
    assert isinstance(w.properties_panel, PropertiesPanel)
    assert isinstance(w.timeline_widget, TimelineWidget)


def test_main_window_undo_redo_with_dummy_clip(app, qtbot):
    from src.ui.main_window import MainWindow
    from src.core.commands import AddClipCommand
    from src.core.timeline import Clip
    w = MainWindow()
    qtbot.addWidget(w)
    clip = Clip(id="test1", name="t", source="/x.mp4",
                start=0.0, duration=3.0, track_id="v1")
    w.cmd_stack.push(AddClipCommand(w.project.timeline, "v1", clip))
    assert w.project.timeline.get_clip("test1") is not None
    w.action_undo()
    assert w.project.timeline.get_clip("test1") is None
    w.action_redo()
    assert w.project.timeline.get_clip("test1") is not None
