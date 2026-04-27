"""Panel lateral derecho: propiedades del clip seleccionado."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QDoubleSpinBox, QGroupBox
)
from src.core.timeline import Clip


class PropertiesPanel(QWidget):
    """Muestra y permite editar propiedades del clip seleccionado."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_clip: Clip | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(QLabel("PROPIEDADES"))

        self.group = QGroupBox("Clip")
        form = QFormLayout(self.group)

        self.name_edit = QLineEdit()
        self.name_edit.setReadOnly(True)
        form.addRow("Nombre:", self.name_edit)

        self.start_spin = QDoubleSpinBox()
        self.start_spin.setRange(0.0, 99999.0)
        self.start_spin.setSuffix(" s")
        form.addRow("Inicio:", self.start_spin)

        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.01, 99999.0)
        self.duration_spin.setSuffix(" s")
        form.addRow("Duracion:", self.duration_spin)

        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(0.0, 2.0)
        self.volume_spin.setSingleStep(0.1)
        form.addRow("Volumen:", self.volume_spin)

        self.opacity_spin = QDoubleSpinBox()
        self.opacity_spin.setRange(0.0, 1.0)
        self.opacity_spin.setSingleStep(0.05)
        form.addRow("Opacidad:", self.opacity_spin)

        layout.addWidget(self.group)
        layout.addStretch(1)

        self.setMinimumWidth(220)
        self.setMaximumWidth(280)
        self.set_clip(None)

    def set_clip(self, clip: Clip | None) -> None:
        self._current_clip = clip
        enabled = clip is not None
        self.group.setEnabled(enabled)
        if clip:
            self.name_edit.setText(clip.name)
            self.start_spin.setValue(clip.start)
            self.duration_spin.setValue(clip.duration)
            self.volume_spin.setValue(clip.volume)
            self.opacity_spin.setValue(clip.opacity)
        else:
            self.name_edit.setText("")
            self.start_spin.setValue(0.0)
            self.duration_spin.setValue(0.0)
            self.volume_spin.setValue(1.0)
            self.opacity_spin.setValue(1.0)
