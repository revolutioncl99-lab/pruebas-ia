"""Smoke test ToolsPanel"""
import pytest
from PyQt6.QtWidgets import QApplication, QPushButton


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_tools_panel_has_7_buttons(app, qtbot):
    from src.ui.tools_panel import ToolsPanel
    panel = ToolsPanel()
    qtbot.addWidget(panel)
    buttons = panel.findChildren(QPushButton)
    assert len(buttons) == 7


def test_tools_panel_import_signal(app, qtbot):
    from src.ui.tools_panel import ToolsPanel
    panel = ToolsPanel()
    qtbot.addWidget(panel)
    buttons = panel.findChildren(QPushButton)
    with qtbot.waitSignal(panel.importRequested, timeout=500):
        buttons[0].click()
