"""Smoke test PreviewWidget"""
import pytest
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_preview_widget_instantiates(app, qtbot):
    from src.ui.preview_widget import PreviewWidget
    w = PreviewWidget()
    qtbot.addWidget(w)
    assert w.btn_play.text() == "▶"
    assert w.slider.value() == 0
