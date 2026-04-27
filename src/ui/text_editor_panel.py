"""Panel visual de creación de texto animado."""
from __future__ import annotations

import json
import uuid
from pathlib import Path

from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox,
    QLabel, QTextEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
    QButtonGroup, QGridLayout, QGroupBox, QListWidget, QColorDialog,
    QMessageBox, QSizePolicy, QSplitter,
)
from PyQt6.QtCore import Qt

from src.core.config import config
from src.core.text_animator import TextAnimator
from src.core.workers import TextAnimationWorker


# Plantillas de texto predefinidas
TEMPLATES = {
    "Intro YouTube": {
        "text": "MI CANAL\nEl mejor contenido",
        "anim_in": "zoom_in",
        "anim_out": "fade_out",
        "style": {"font": "Arial Bold", "size": 64, "color": "#FFFFFF",
                  "outline_color": "#000000", "outline_width": 3,
                  "position": "center"},
        "duration": 3.0,
    },
    "Lower third": {
        "text": "Nombre Apellido\nCargo / Empresa",
        "anim_in": "slide_left",
        "anim_out": "fade_out",
        "style": {"font": "Arial", "size": 40, "color": "#FFFFFF",
                  "outline_color": "#000000", "outline_width": 2,
                  "position": "bottom_left"},
        "duration": 4.0,
    },
    "End screen": {
        "text": "¡Suscríbete!\n👍 Dale like",
        "anim_in": "bounce",
        "anim_out": "fade_out",
        "style": {"font": "Arial Bold", "size": 56, "color": "#FFD700",
                  "outline_color": "#000000", "outline_width": 3,
                  "position": "center"},
        "duration": 5.0,
    },
    "Kinetic quote": {
        "text": "\"La imaginación\nes más importante\nque el conocimiento\"",
        "anim_in": "typewriter",
        "anim_out": "fade_out",
        "style": {"font": "Arial", "size": 44, "color": "#FFFFFF",
                  "outline_color": "#000000", "outline_width": 2,
                  "position": "center"},
        "duration": 6.0,
    },
    "Contador": {
        "text": "100",
        "anim_in": "zoom_in",
        "anim_out": "zoom_out",
        "style": {"font": "Arial Bold", "size": 80, "color": "#FF4444",
                  "outline_color": "#000000", "outline_width": 4,
                  "position": "center"},
        "duration": 2.0,
    },
}

# Posiciones como rejilla 3×3
_POSITIONS = [
    ("↖", "top_left"),    ("↑", "top_center"),    ("↗", "top_right"),
    ("←", "middle_left"), ("·", "center"),         ("→", "middle_right"),
    ("↙", "bottom_left"), ("↓", "bottom_center"),  ("↘", "bottom_right"),
]


class TextEditorPanel(QWidget):
    """Panel visual para crear clips de texto animado y agregarlos al timeline."""

    clipReady = pyqtSignal(str)  # path al clip .mov generado

    def __init__(self, timeline=None, cmd_stack=None, timeline_widget=None,
                 parent=None):
        super().__init__(parent)
        self._timeline = timeline
        self._cmd_stack = cmd_stack
        self._timeline_widget = timeline_widget
        self._worker: TextAnimationWorker | None = None
        self._color: str = "#FFFFFF"
        self._outline_color: str = "#000000"
        self._position: str = "center"
        self._preview_timer = QTimer()
        self._preview_timer.setSingleStep = lambda _: None  # no-op
        self._preview_timer.setInterval(300)
        self._preview_timer.setSingleShot(True)
        self._build_ui()

    # ------------------------------------------------------------------
    # Construcción de UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        layout.addWidget(QLabel("TEXTO ANIMADO"))

        splitter = QSplitter(Qt.Orientation.Vertical)

        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(4)

        # Campo de texto
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Escribe tu texto aquí...")
        self.text_edit.setMaximumHeight(80)
        top_layout.addWidget(self.text_edit)

        # Animaciones
        anim_group = QGroupBox("Animaciones")
        anim_layout = QHBoxLayout(anim_group)
        entrada_anims = [k for k, v in TextAnimator.ANIMATIONS.items()
                         if v["type"] in ("entrada", "none")]
        salida_anims = [k for k, v in TextAnimator.ANIMATIONS.items()
                        if v["type"] in ("salida", "none")]

        anim_layout.addWidget(QLabel("Entrada:"))
        self.combo_anim_in = QComboBox()
        self.combo_anim_in.addItems(entrada_anims)
        self.combo_anim_in.setCurrentText("fade_in")
        anim_layout.addWidget(self.combo_anim_in)

        anim_layout.addWidget(QLabel("Salida:"))
        self.combo_anim_out = QComboBox()
        self.combo_anim_out.addItems(salida_anims)
        self.combo_anim_out.setCurrentText("fade_out")
        anim_layout.addWidget(self.combo_anim_out)
        top_layout.addWidget(anim_group)

        # Estilo de texto
        style_group = QGroupBox("Estilo")
        style_layout = QGridLayout(style_group)

        style_layout.addWidget(QLabel("Fuente:"), 0, 0)
        self.combo_font = QComboBox()
        self.combo_font.addItems(["Arial", "Arial Bold", "Impact",
                                   "Helvetica Neue", "Montserrat Bold"])
        style_layout.addWidget(self.combo_font, 0, 1)

        style_layout.addWidget(QLabel("Tamaño:"), 0, 2)
        self.spin_size = QSpinBox()
        self.spin_size.setRange(8, 200)
        self.spin_size.setValue(56)
        style_layout.addWidget(self.spin_size, 0, 3)

        style_layout.addWidget(QLabel("Color:"), 1, 0)
        self.btn_color = QPushButton()
        self.btn_color.setFixedSize(40, 24)
        self._update_color_btn(self.btn_color, self._color)
        self.btn_color.clicked.connect(self._pick_color)
        style_layout.addWidget(self.btn_color, 1, 1)

        style_layout.addWidget(QLabel("Outline:"), 1, 2)
        self.btn_outline_color = QPushButton()
        self.btn_outline_color.setFixedSize(40, 24)
        self._update_color_btn(self.btn_outline_color, self._outline_color)
        self.btn_outline_color.clicked.connect(self._pick_outline_color)
        style_layout.addWidget(self.btn_outline_color, 1, 3)

        style_layout.addWidget(QLabel("Grosor outline:"), 2, 0)
        self.spin_outline = QSpinBox()
        self.spin_outline.setRange(0, 10)
        self.spin_outline.setValue(2)
        style_layout.addWidget(self.spin_outline, 2, 1)

        self.chk_shadow = QCheckBox("Sombra")
        style_layout.addWidget(self.chk_shadow, 2, 2, 1, 2)

        top_layout.addWidget(style_group)

        # Posición
        pos_group = QGroupBox("Posición")
        pos_grid = QGridLayout(pos_group)
        self._pos_buttons: dict[str, QPushButton] = {}
        btn_group = QButtonGroup(self)
        btn_group.setExclusive(True)
        for idx, (label, pos_key) in enumerate(_POSITIONS):
            btn = QPushButton(label)
            btn.setFixedSize(28, 28)
            btn.setCheckable(True)
            if pos_key == "center":
                btn.setChecked(True)
            btn_group.addButton(btn)
            pos_grid.addWidget(btn, idx // 3, idx % 3)
            self._pos_buttons[pos_key] = btn
            btn.clicked.connect(lambda checked, k=pos_key: self._set_position(k))
        top_layout.addWidget(pos_group)

        # Duración
        dur_row = QHBoxLayout()
        dur_row.addWidget(QLabel("Duración:"))
        self.spin_duration = QDoubleSpinBox()
        self.spin_duration.setRange(0.1, 300.0)
        self.spin_duration.setValue(3.0)
        self.spin_duration.setSuffix(" s")
        dur_row.addWidget(self.spin_duration)
        top_layout.addLayout(dur_row)

        # Preview label
        self.lbl_preview = QLabel("Preview aparecerá aquí")
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_preview.setStyleSheet("background:#111;color:#aaa;border:1px solid #444;")
        self.lbl_preview.setMinimumHeight(60)
        top_layout.addWidget(self.lbl_preview)

        # Botón agregar al timeline
        self.btn_add = QPushButton("➕ Agregar al timeline")
        self.btn_add.setMinimumHeight(34)
        self.btn_add.clicked.connect(self._on_add_to_timeline)
        top_layout.addWidget(self.btn_add)

        splitter.addWidget(top_widget)

        # Plantillas
        tpl_group = QGroupBox("Plantillas")
        tpl_layout = QVBoxLayout(tpl_group)
        self.list_templates = QListWidget()
        self.list_templates.addItems(list(TEMPLATES.keys()))
        self.list_templates.itemDoubleClicked.connect(self._on_template_selected)
        tpl_layout.addWidget(self.list_templates)
        splitter.addWidget(tpl_group)

        layout.addWidget(splitter, stretch=1)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

    # ------------------------------------------------------------------
    # Slots privados
    # ------------------------------------------------------------------

    def _pick_color(self) -> None:
        c = QColorDialog.getColor(QColor(self._color), self, "Color de texto")
        if c.isValid():
            self._color = c.name()
            self._update_color_btn(self.btn_color, self._color)

    def _pick_outline_color(self) -> None:
        c = QColorDialog.getColor(QColor(self._outline_color), self, "Color de outline")
        if c.isValid():
            self._outline_color = c.name()
            self._update_color_btn(self.btn_outline_color, self._outline_color)

    def _set_position(self, pos_key: str) -> None:
        self._position = pos_key

    def _on_template_selected(self, item) -> None:
        tpl = TEMPLATES.get(item.text())
        if not tpl:
            return
        self.text_edit.setPlainText(tpl["text"])
        self.combo_anim_in.setCurrentText(tpl.get("anim_in", "fade_in"))
        self.combo_anim_out.setCurrentText(tpl.get("anim_out", "fade_out"))
        style = tpl.get("style", {})
        self.combo_font.setCurrentText(style.get("font", "Arial"))
        self.spin_size.setValue(style.get("size", 56))
        self._color = style.get("color", "#FFFFFF")
        self._outline_color = style.get("outline_color", "#000000")
        self._update_color_btn(self.btn_color, self._color)
        self._update_color_btn(self.btn_outline_color, self._outline_color)
        self.spin_outline.setValue(style.get("outline_width", 2))
        self.spin_duration.setValue(tpl.get("duration", 3.0))
        pos = style.get("position", "center")
        self._position = pos
        if pos in self._pos_buttons:
            self._pos_buttons[pos].setChecked(True)

    def _on_add_to_timeline(self) -> None:
        text = self.text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Sin texto", "Escribe algo de texto primero.")
            return
        if self._worker and self._worker.isRunning():
            return

        style = {
            "font": self.combo_font.currentText(),
            "size": self.spin_size.value(),
            "color": self._color,
            "outline_color": self._outline_color,
            "outline_width": self.spin_outline.value(),
            "position": self._position,
            "shadow": self.chk_shadow.isChecked(),
        }
        self._worker = TextAnimationWorker(
            text=text,
            duration=self.spin_duration.value(),
            animation_in=self.combo_anim_in.currentText(),
            animation_out=self.combo_anim_out.currentText(),
            style=style,
        )
        self._worker.finished.connect(self._on_clip_ready)
        self._worker.error.connect(self._on_clip_error)
        self.btn_add.setEnabled(False)
        self.btn_add.setText("Generando...")
        self._worker.start()

    def _on_clip_ready(self, clip_path: str) -> None:
        self.btn_add.setEnabled(True)
        self.btn_add.setText("➕ Agregar al timeline")
        self._add_clip_to_timeline(clip_path)
        self.clipReady.emit(clip_path)

    def _on_clip_error(self, msg: str) -> None:
        self.btn_add.setEnabled(True)
        self.btn_add.setText("➕ Agregar al timeline")
        QMessageBox.critical(self, "Error al generar clip", msg)

    # ------------------------------------------------------------------
    # Timeline
    # ------------------------------------------------------------------

    def _add_clip_to_timeline(self, clip_path: str) -> None:
        if not self._timeline or not self._cmd_stack:
            return

        from src.core.timeline import Clip
        from src.core.commands import AddClipCommand

        # Guardar metadata del clip en JSON junto al archivo
        meta_path = Path(clip_path).with_suffix(".json")
        meta = {
            "type": "text",
            "text": self.text_edit.toPlainText().strip(),
            "animation_in": self.combo_anim_in.currentText(),
            "animation_out": self.combo_anim_out.currentText(),
            "style": {
                "font": self.combo_font.currentText(),
                "size": self.spin_size.value(),
                "color": self._color,
                "outline_color": self._outline_color,
                "outline_width": self.spin_outline.value(),
                "position": self._position,
            },
            "rendered_clip": clip_path,
        }
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2))

        track = self._timeline.get_track("titles")
        if track is None:
            return
        last_end = max((c.end for c in track.clips), default=0.0)
        duration = self.spin_duration.value()

        clip = Clip(
            id=uuid.uuid4().hex[:8],
            name=self.text_edit.toPlainText().strip()[:30],
            source=str(meta_path),
            start=last_end,
            duration=duration,
            track_id="titles",
        )
        try:
            self._cmd_stack.push(AddClipCommand(self._timeline, "titles", clip))
            if self._timeline_widget:
                self._timeline_widget.refresh()
        except ValueError:
            pass

    # ------------------------------------------------------------------
    # Helpers de UI
    # ------------------------------------------------------------------

    @staticmethod
    def _update_color_btn(btn: QPushButton, color: str) -> None:
        btn.setStyleSheet(
            f"background-color: {color}; border: 1px solid #888;"
        )
