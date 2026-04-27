"""Workers QThread para procesamiento en background (transcripción y animación)."""
from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal


class WhisperWorker(QThread):
    """Ejecuta WhisperTranscriber en un hilo separado para no bloquear la UI."""

    progress = pyqtSignal(int)   # 0-100
    finished = pyqtSignal(list)  # lista de segmentos dict
    error = pyqtSignal(str)

    def __init__(self, video_path: str, model_size: str = "medium",
                 language: str | None = None, word_timestamps: bool = False):
        super().__init__()
        self.video_path = video_path
        self.model_size = model_size
        self.language = language
        self.word_timestamps = word_timestamps

    def run(self) -> None:
        try:
            from src.ai.whisper_sub import WhisperTranscriber
            transcriber = WhisperTranscriber(self.model_size)
            if self.word_timestamps:
                segments = transcriber.transcribe_word_by_word(
                    self.video_path,
                    progress_callback=lambda p: self.progress.emit(p),
                )
            else:
                segments = transcriber.transcribe(
                    self.video_path,
                    language=self.language,
                    progress_callback=lambda p: self.progress.emit(p),
                )
            self.finished.emit(segments)
        except Exception as exc:  # noqa: BLE001
            self.error.emit(str(exc))


class TextAnimationWorker(QThread):
    """Genera un clip de texto animado con FFmpeg en background."""

    finished = pyqtSignal(str)  # path al clip generado
    error = pyqtSignal(str)

    def __init__(self, text: str, duration: float, animation_in: str,
                 animation_out: str, style: dict, resolution: tuple = (1920, 1080)):
        super().__init__()
        self.text = text
        self.duration = duration
        self.animation_in = animation_in
        self.animation_out = animation_out
        self.style = style
        self.resolution = resolution

    def run(self) -> None:
        try:
            from src.core.text_animator import TextAnimator
            animator = TextAnimator()
            path = animator.generate_text_clip(
                text=self.text,
                duration=self.duration,
                animation_in=self.animation_in,
                animation_out=self.animation_out,
                style=self.style,
                resolution=self.resolution,
            )
            self.finished.emit(path)
        except Exception as exc:  # noqa: BLE001
            self.error.emit(str(exc))
