"""Panel de edición de subtítulos con transcripción Whisper IA."""
from __future__ import annotations

import json
import uuid
from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QProgressBar, QLabel,
    QFileDialog, QMessageBox, QHeaderView, QSizePolicy,
)

from src.core.config import config
from src.core.subtitle_renderer import SubtitleRenderer
from src.core.workers import WhisperWorker


class SubtitleEditor(QWidget):
    """Panel de edición de subtítulos: lista de segmentos + controles de IA."""

    segmentsChanged = pyqtSignal(list)   # lista de segmentos actualizada
    styleChanged = pyqtSignal(str)       # nombre de estilo seleccionado

    def __init__(self, timeline=None, cmd_stack=None, timeline_widget=None,
                 parent=None):
        super().__init__(parent)
        self._segments: list[dict] = []
        self._timeline = timeline
        self._cmd_stack = cmd_stack
        self._timeline_widget = timeline_widget
        self._worker: WhisperWorker | None = None
        self._current_video: str | None = None
        self._build_ui()

    # ------------------------------------------------------------------
    # Interfaz pública
    # ------------------------------------------------------------------

    def set_video(self, video_path: str) -> None:
        """Informa al editor qué video está cargado para la transcripción."""
        self._current_video = video_path

    def load_segments(self, segments: list[dict]) -> None:
        """Carga segmentos externos (p.ej. desde JSON de clip)."""
        self._segments = segments
        self._populate_table(segments)
        self.segmentsChanged.emit(segments)

    # ------------------------------------------------------------------
    # Construcción de UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        layout.addWidget(QLabel("SUBTÍTULOS"))

        # Controles superiores: modelo, idioma, estilo
        top = QHBoxLayout()
        top.addWidget(QLabel("Modelo:"))
        self.combo_model = QComboBox()
        self.combo_model.addItems(["tiny", "base", "small", "medium", "large"])
        self.combo_model.setCurrentText("medium")
        top.addWidget(self.combo_model)

        top.addWidget(QLabel("Idioma:"))
        self.combo_lang = QComboBox()
        self.combo_lang.addItems([
            "auto", "es", "en", "fr", "de", "it", "pt", "ja", "ko", "zh",
        ])
        top.addWidget(self.combo_lang)
        layout.addLayout(top)

        # Botones de acción
        btn_row = QHBoxLayout()
        self.btn_transcribe = QPushButton("🎙 Transcribir IA")
        self.btn_transcribe.clicked.connect(self._on_transcribe)
        btn_row.addWidget(self.btn_transcribe)

        self.btn_reimport = QPushButton("↺ Re-transcribir")
        self.btn_reimport.clicked.connect(self._on_transcribe)
        btn_row.addWidget(self.btn_reimport)
        layout.addLayout(btn_row)

        btn_row2 = QHBoxLayout()
        self.btn_import_srt = QPushButton("📂 Importar .srt")
        self.btn_import_srt.clicked.connect(self._on_import_srt)
        btn_row2.addWidget(self.btn_import_srt)

        self.btn_export_srt = QPushButton("💾 Exportar .srt")
        self.btn_export_srt.clicked.connect(self._on_export_srt)
        btn_row2.addWidget(self.btn_export_srt)
        layout.addLayout(btn_row2)

        # Selector de estilo visual
        style_row = QHBoxLayout()
        style_row.addWidget(QLabel("Estilo:"))
        self.combo_style = QComboBox()
        self.combo_style.addItems(list(SubtitleRenderer.STYLES.keys()))
        self.combo_style.currentTextChanged.connect(self.styleChanged.emit)
        style_row.addWidget(self.combo_style)
        layout.addLayout(style_row)

        # Barra de progreso (oculta por defecto)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Tabla de segmentos
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["#", "Inicio", "Fin", "Texto"])
        self.table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )
        self.table.setAlternatingRowColors(True)
        self.table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.table, stretch=1)

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

    # ------------------------------------------------------------------
    # Slots privados
    # ------------------------------------------------------------------

    def _on_transcribe(self) -> None:
        if not self._current_video:
            QMessageBox.warning(self, "Sin video", "Importa un video antes de transcribir.")
            return
        if self._worker and self._worker.isRunning():
            return

        model = self.combo_model.currentText()
        lang_sel = self.combo_lang.currentText()
        language = None if lang_sel == "auto" else lang_sel

        self._worker = WhisperWorker(
            video_path=self._current_video,
            model_size=model,
            language=language,
            word_timestamps=True,
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_transcription_done)
        self._worker.error.connect(self._on_transcription_error)

        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.btn_transcribe.setEnabled(False)
        self._worker.start()

    def _on_progress(self, value: int) -> None:
        self.progress_bar.setValue(value)

    def _on_transcription_done(self, segments: list) -> None:
        self.progress_bar.hide()
        self.btn_transcribe.setEnabled(True)
        self._segments = segments
        self._populate_table(segments)
        self._save_and_add_clip(segments)
        self.segmentsChanged.emit(segments)

    def _on_transcription_error(self, msg: str) -> None:
        self.progress_bar.hide()
        self.btn_transcribe.setEnabled(True)
        QMessageBox.critical(self, "Error de transcripción", msg)

    def _on_item_changed(self, item: QTableWidgetItem) -> None:
        """Sincroniza edición inline de la tabla con _segments."""
        row = item.row()
        col = item.column()
        if row >= len(self._segments):
            return
        self.table.blockSignals(True)
        try:
            if col == 1:
                self._segments[row]["start"] = float(item.text())
            elif col == 2:
                self._segments[row]["end"] = float(item.text())
            elif col == 3:
                self._segments[row]["text"] = item.text()
        except ValueError:
            pass
        finally:
            self.table.blockSignals(False)
        self.segmentsChanged.emit(self._segments)

    def _on_import_srt(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Importar SRT", "", "SubRip (*.srt)"
        )
        if not path:
            return
        segments = self._parse_srt(path)
        if not segments:
            QMessageBox.warning(self, "SRT vacío", "No se encontraron segmentos en el archivo.")
            return
        self._segments = segments
        self._populate_table(segments)
        self._save_and_add_clip(segments)
        self.segmentsChanged.emit(segments)

    def _on_export_srt(self) -> None:
        if not self._segments:
            QMessageBox.warning(self, "Sin segmentos", "No hay subtítulos para exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar SRT", "subtitulos.srt", "SubRip (*.srt)"
        )
        if not path:
            return
        from src.ai.whisper_sub import WhisperTranscriber
        # Reutilizamos el método export_srt sin cargar modelo (instancia dummy)
        _export_srt(self._segments, path)
        QMessageBox.information(self, "Exportado", f"Guardado en {path}")

    # ------------------------------------------------------------------
    # Helpers de tabla
    # ------------------------------------------------------------------

    def _populate_table(self, segments: list[dict]) -> None:
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        for i, seg in enumerate(segments):
            self.table.insertRow(i)
            idx_item = QTableWidgetItem(str(i + 1))
            idx_item.setFlags(idx_item.flags() & ~(
                idx_item.flags() & ~idx_item.flags()
            ))
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table.setItem(i, 1, QTableWidgetItem(f"{seg['start']:.2f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{seg['end']:.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem(seg.get("text", "")))
        self.table.blockSignals(False)

    # ------------------------------------------------------------------
    # Persistencia y timeline
    # ------------------------------------------------------------------

    def _save_and_add_clip(self, segments: list[dict]) -> None:
        """Guarda segmentos en JSON y agrega clip al track 'sub' del timeline."""
        if not self._timeline or not self._cmd_stack:
            return

        filename = f"sub_{uuid.uuid4().hex[:8]}.json"
        json_path = config.TEMP_DIR / filename
        style_name = self.combo_style.currentText()
        data = {
            "type": "subtitle",
            "style": style_name,
            "segments": segments,
        }
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

        from src.core.timeline import Clip
        from src.core.commands import AddClipCommand

        duration = max(
            (seg["end"] for seg in segments), default=5.0
        ) - min((seg["start"] for seg in segments), default=0.0)
        start = min((seg["start"] for seg in segments), default=0.0)

        clip = Clip(
            id=uuid.uuid4().hex[:8],
            name=f"Subtítulos ({style_name})",
            source=str(json_path),
            start=start,
            duration=max(duration, 0.1),
            track_id="sub",
        )
        try:
            self._cmd_stack.push(AddClipCommand(self._timeline, "sub", clip))
            if self._timeline_widget:
                self._timeline_widget.refresh()
        except ValueError:
            # Si ya hay un clip solapado, simplemente no agrega
            pass

    # ------------------------------------------------------------------
    # Parser SRT
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_srt(path: str) -> list[dict]:
        """Parsea un archivo .srt y retorna lista de segmentos."""
        text = Path(path).read_text(encoding="utf-8", errors="replace")
        blocks = text.strip().split("\n\n")
        segments: list[dict] = []
        for block in blocks:
            lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
            if len(lines) < 3:
                continue
            # línea 0: índice, línea 1: timestamps, línea 2+: texto
            try:
                times = lines[1].split(" --> ")
                start = _parse_srt_time(times[0])
                end = _parse_srt_time(times[1])
                seg_text = " ".join(lines[2:])
                segments.append({"start": start, "end": end, "text": seg_text, "words": []})
            except (IndexError, ValueError):
                continue
        return segments


# ------------------------------------------------------------------
# Funciones de módulo
# ------------------------------------------------------------------

def _parse_srt_time(s: str) -> float:
    """Convierte HH:MM:SS,mmm a segundos float."""
    s = s.strip().replace(",", ".")
    parts = s.split(":")
    h, m, sec = int(parts[0]), int(parts[1]), float(parts[2])
    return h * 3600 + m * 60 + sec


def _export_srt(segments: list[dict], output_path: str) -> None:
    """Escribe segmentos como archivo SRT sin instanciar Whisper."""
    def fmt(t: float) -> str:
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = int(t % 60)
        ms = int(round((t - int(t)) * 1000))
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines: list[str] = []
    for i, seg in enumerate(segments, start=1):
        lines.append(str(i))
        lines.append(f"{fmt(seg['start'])} --> {fmt(seg['end'])}")
        lines.append(seg.get("text", "").strip())
        lines.append("")
    Path(output_path).write_text("\n".join(lines), encoding="utf-8")
