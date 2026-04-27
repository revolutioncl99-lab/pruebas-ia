"""Reproductor de preview de video con controles play/pause y tiempo."""
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel
)


class PreviewWidget(QWidget):
    """Preview con play/pause, slider de tiempo, label de duracion."""

    timeChanged = pyqtSignal(float)  # segundos

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(240)
        layout.addWidget(self.video_widget, stretch=1)

        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.video_widget)

        controls = QHBoxLayout()
        self.btn_play = QPushButton("▶")
        self.btn_play.setFixedWidth(40)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        self.lbl_time = QLabel("00:00 / 00:00")
        self.lbl_time.setMinimumWidth(110)

        controls.addWidget(self.btn_play)
        controls.addWidget(self.slider, stretch=1)
        controls.addWidget(self.lbl_time)
        layout.addLayout(controls)

    def _connect_signals(self) -> None:
        self.btn_play.clicked.connect(self.toggle_play)
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.slider.sliderMoved.connect(self.player.setPosition)

    def load_video(self, path: str) -> None:
        self.player.setSource(QUrl.fromLocalFile(path))

    def toggle_play(self) -> None:
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.btn_play.setText("▶")
        else:
            self.player.play()
            self.btn_play.setText("⏸")

    def _on_position_changed(self, pos_ms: int) -> None:
        self.slider.setValue(pos_ms)
        self._update_time_label(pos_ms, self.player.duration())
        self.timeChanged.emit(pos_ms / 1000.0)

    def _on_duration_changed(self, dur_ms: int) -> None:
        self.slider.setRange(0, dur_ms)
        self._update_time_label(self.player.position(), dur_ms)

    @staticmethod
    def _fmt(ms: int) -> str:
        s = ms // 1000
        return f"{s // 60:02d}:{s % 60:02d}"

    def _update_time_label(self, pos: int, dur: int) -> None:
        self.lbl_time.setText(f"{self._fmt(pos)} / {self._fmt(dur)}")
