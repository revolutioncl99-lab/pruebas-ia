"""Ventana principal del editor."""
from __future__ import annotations
import uuid
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QFileDialog, QMessageBox, QWidget, QVBoxLayout,
    QDockWidget,
)

from src.core.config import config
from src.core.timeline import Timeline, Track, TrackType, Clip
from src.core.video_processor import VideoProcessor
from src.core.project import Project
from src.core.commands import (
    CommandStack, AddClipCommand, RemoveClipCommand, MoveClipCommand
)
from src.ui.preview_widget import PreviewWidget
from src.ui.tools_panel import ToolsPanel
from src.ui.properties_panel import PropertiesPanel
from src.ui.timeline_widget import TimelineWidget
from src.ui.subtitle_editor import SubtitleEditor
from src.ui.subtitle_preview_overlay import SubtitlePreviewOverlay
from src.ui.text_editor_panel import TextEditorPanel


class MainWindow(QMainWindow):
    """Ventana principal: menubar + splitters (tools | preview/timeline | props)."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor de Video - RevoCL")
        self.resize(1280, 800)

        self.project = self._new_project()
        self.processor = VideoProcessor(temp_dir=config.TEMP_DIR)
        self.cmd_stack = CommandStack()

        self._build_ui()
        self._build_menus()
        self._wire_signals()
        self.setAcceptDrops(True)
        self._load_stylesheet()

    def _new_project(self) -> Project:
        tl = Timeline(fps=config.DEFAULT_FPS)
        tl.add_track(Track(id="titles", name="Titulos", type=TrackType.TEXT))
        tl.add_track(Track(id="v1", name="Video 1", type=TrackType.VIDEO))
        tl.add_track(Track(id="v2", name="Video 2", type=TrackType.VIDEO))
        tl.add_track(Track(id="a1", name="Audio 1", type=TrackType.AUDIO))
        tl.add_track(Track(id="a2", name="Audio 2", type=TrackType.AUDIO))
        tl.add_track(Track(id="sub", name="Subtitulos", type=TrackType.SUBTITLE))
        return Project(name="Untitled", timeline=tl)

    def _build_ui(self) -> None:
        h_split = QSplitter(Qt.Orientation.Horizontal)

        self.tools_panel = ToolsPanel()
        h_split.addWidget(self.tools_panel)

        v_split = QSplitter(Qt.Orientation.Vertical)
        self.preview = PreviewWidget()
        v_split.addWidget(self.preview)

        self.timeline_widget = TimelineWidget(self.project.timeline)
        v_split.addWidget(self.timeline_widget)
        v_split.setStretchFactor(0, 3)
        v_split.setStretchFactor(1, 2)

        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.addWidget(v_split)
        h_split.addWidget(center_container)

        self.properties_panel = PropertiesPanel()
        h_split.addWidget(self.properties_panel)

        h_split.setStretchFactor(0, 0)
        h_split.setStretchFactor(1, 1)
        h_split.setStretchFactor(2, 0)
        h_split.setSizes([180, 880, 220])

        self.setCentralWidget(h_split)

        # Panel de subtítulos IA (dock flotante)
        self.subtitle_editor = SubtitleEditor(
            timeline=self.project.timeline,
            cmd_stack=self.cmd_stack,
            timeline_widget=self.timeline_widget,
        )
        self._subtitle_dock = QDockWidget("Subtítulos IA", self)
        self._subtitle_dock.setWidget(self.subtitle_editor)
        self._subtitle_dock.setMinimumWidth(320)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._subtitle_dock)
        self._subtitle_dock.hide()

        # Panel de texto animado (dock flotante)
        self.text_editor = TextEditorPanel(
            timeline=self.project.timeline,
            cmd_stack=self.cmd_stack,
            timeline_widget=self.timeline_widget,
        )
        self._text_dock = QDockWidget("Texto Animado", self)
        self._text_dock.setWidget(self.text_editor)
        self._text_dock.setMinimumWidth(320)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._text_dock)
        self._text_dock.hide()

        # Overlay de subtítulos sobre el preview
        self.subtitle_overlay = SubtitlePreviewOverlay(self.preview.video_widget)
        self.subtitle_overlay.resize(self.preview.video_widget.size())
        self.subtitle_overlay.raise_()

        self.statusBar().showMessage("Listo")

    def _build_menus(self) -> None:
        mb = self.menuBar()

        m_file = mb.addMenu("&Archivo")
        act_new = QAction("Nuevo proyecto", self, shortcut=QKeySequence.StandardKey.New)
        act_new.triggered.connect(self.action_new_project)
        m_file.addAction(act_new)

        act_open = QAction("Abrir proyecto...", self, shortcut=QKeySequence.StandardKey.Open)
        act_open.triggered.connect(self.action_open_project)
        m_file.addAction(act_open)

        act_save = QAction("Guardar proyecto", self, shortcut=QKeySequence.StandardKey.Save)
        act_save.triggered.connect(self.action_save_project)
        m_file.addAction(act_save)

        m_file.addSeparator()

        act_import = QAction("Importar video...", self, shortcut="Ctrl+I")
        act_import.triggered.connect(self.action_import_video)
        m_file.addAction(act_import)

        m_file.addSeparator()
        act_quit = QAction("Salir", self, shortcut=QKeySequence.StandardKey.Quit)
        act_quit.triggered.connect(self.close)
        m_file.addAction(act_quit)

        m_edit = mb.addMenu("&Editar")
        self.act_undo = QAction("Deshacer", self, shortcut=QKeySequence.StandardKey.Undo)
        self.act_undo.triggered.connect(self.action_undo)
        m_edit.addAction(self.act_undo)

        self.act_redo = QAction("Rehacer", self, shortcut=QKeySequence.StandardKey.Redo)
        self.act_redo.triggered.connect(self.action_redo)
        m_edit.addAction(self.act_redo)

        m_edit.addSeparator()
        self.act_delete = QAction("Eliminar clip", self, shortcut="Delete")
        self.act_delete.triggered.connect(self.action_delete_clip)
        m_edit.addAction(self.act_delete)

        m_play = mb.addMenu("&Reproducion")
        act_play = QAction("Play / Pause", self, shortcut="Space")
        act_play.triggered.connect(self.preview.toggle_play)
        m_play.addAction(act_play)

    def _wire_signals(self) -> None:
        self.tools_panel.importRequested.connect(self.action_import_video)
        self.tools_panel.subtitleRequested.connect(self._subtitle_dock.show)
        self.tools_panel.textAnimRequested.connect(self._text_dock.show)
        self.timeline_widget.clipSelected.connect(self._on_clip_selected)
        self.preview.timeChanged.connect(self.timeline_widget.set_playhead)
        self.preview.timeChanged.connect(self.subtitle_overlay.set_current_time)
        self.subtitle_editor.segmentsChanged.connect(
            lambda segs: self.subtitle_overlay.set_segments(
                segs, self.subtitle_editor.combo_style.currentText()
            )
        )
        self.subtitle_editor.styleChanged.connect(self.subtitle_overlay.set_style)

    def _load_stylesheet(self) -> None:
        qss_path = config.STYLES_DIR / "dark_theme.qss"
        if qss_path.exists():
            self.setStyleSheet(qss_path.read_text())

    # ---------- ACTIONS ----------

    def action_new_project(self) -> None:
        self.project = self._new_project()
        self.cmd_stack = CommandStack()
        self.timeline_widget.timeline = self.project.timeline
        self.timeline_widget.refresh()
        self.properties_panel.set_clip(None)
        self.subtitle_editor._timeline = self.project.timeline
        self.subtitle_editor._cmd_stack = self.cmd_stack
        self.text_editor._timeline = self.project.timeline
        self.text_editor._cmd_stack = self.cmd_stack
        self.setWindowTitle("Editor de Video - RevoCL [Untitled]")

    def action_open_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Abrir proyecto", str(config.PROJECTS_DIR), "Proyecto (*.json)"
        )
        if not path:
            return
        try:
            self.project = Project.load(Path(path))
        except (ValueError, OSError) as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir: {e}")
            return
        self.cmd_stack = CommandStack()
        self.timeline_widget.timeline = self.project.timeline
        self.timeline_widget.refresh()
        self.setWindowTitle(f"Editor de Video - RevoCL [{self.project.name}]")
        self.statusBar().showMessage(f"Proyecto cargado: {path}", 3000)

    def action_save_project(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar proyecto", str(config.PROJECTS_DIR / f"{self.project.name}.json"),
            "Proyecto (*.json)"
        )
        if not path:
            return
        try:
            self.project.save(Path(path))
            self.statusBar().showMessage(f"Guardado en {path}", 3000)
        except OSError as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")

    def action_import_video(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Importar video", "",
            "Video/Audio (*.mp4 *.mov *.avi *.mkv *.webm *.mp3 *.wav)"
        )
        if path:
            self.import_media(path)

    def import_media(self, path: str) -> None:
        ext = Path(path).suffix.lower()
        if ext in config.SUPPORTED_VIDEO:
            track_id = "v1"
        elif ext in config.SUPPORTED_AUDIO:
            track_id = "a1"
        else:
            QMessageBox.warning(self, "No soportado", f"Formato no soportado: {ext}")
            return

        info = self.processor.get_video_info(path) or {"duration": 5.0}
        duration = info.get("duration") or 5.0

        track = self.project.timeline.get_track(track_id)
        last_end = max((c.end for c in track.clips), default=0.0)

        clip = Clip(
            id=uuid.uuid4().hex[:8],
            name=Path(path).stem,
            source=path,
            start=last_end,
            duration=duration,
            track_id=track_id,
        )
        self.cmd_stack.push(AddClipCommand(self.project.timeline, track_id, clip))
        self.timeline_widget.refresh()
        if ext in config.SUPPORTED_VIDEO:
            self.preview.load_video(path)
            self.subtitle_editor.set_video(path)
        self.statusBar().showMessage(f"Importado: {clip.name}", 3000)

    def action_undo(self) -> None:
        if self.cmd_stack.undo():
            self.timeline_widget.refresh()
            self.statusBar().showMessage("Deshacer", 1500)

    def action_redo(self) -> None:
        if self.cmd_stack.redo():
            self.timeline_widget.refresh()
            self.statusBar().showMessage("Rehacer", 1500)

    def action_delete_clip(self) -> None:
        clip = self.properties_panel._current_clip
        if clip is None:
            return
        self.cmd_stack.push(RemoveClipCommand(self.project.timeline, clip.id))
        self.timeline_widget.refresh()
        self.properties_panel.set_clip(None)

    def _on_clip_selected(self, clip_id: str) -> None:
        clip = self.project.timeline.get_clip(clip_id)
        self.properties_panel.set_clip(clip)
        if clip and Path(clip.source).suffix.lower() in config.SUPPORTED_VIDEO:
            self.preview.load_video(clip.source)

    # ---------- DRAG & DROP ----------

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        for url in event.mimeData().urls():
            local = url.toLocalFile()
            if local:
                self.import_media(local)
        event.acceptProposedAction()
