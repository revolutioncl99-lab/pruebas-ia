"""Panel lateral izquierdo con herramientas principales."""
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel


class ToolsPanel(QWidget):
    """Sidebar izquierdo: import, cut, text, efects, audio."""

    importRequested = pyqtSignal()
    cutRequested = pyqtSignal()
    textRequested = pyqtSignal()
    efectsRequested = pyqtSignal()
    audioRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        layout.addWidget(QLabel("HERRAMIENTAS"))

        buttons = [
            ("📁  Importar", self.importRequested),
            ("✂️  Cortar", self.cutRequested),
            ("T   Texto", self.textRequested),
            ("✨  Efectos", self.efectsRequested),
            ("🎵  Audio", self.audioRequested),
        ]
        for label, signal in buttons:
            btn = QPushButton(label)
            btn.setMinimumHeight(32)
            btn.clicked.connect(signal.emit)
            layout.addWidget(btn)

        layout.addStretch(1)
        self.setMinimumWidth(180)
        self.setMaximumWidth(220)
