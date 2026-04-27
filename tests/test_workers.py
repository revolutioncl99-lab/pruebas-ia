"""Tests para core.workers (WhisperWorker y TextAnimationWorker)."""
from unittest.mock import MagicMock, patch
import pytest


def test_whisper_worker_emits_finished(qtbot):
    from src.core.workers import WhisperWorker

    fake_segments = [{"start": 0.0, "end": 2.0, "text": "Hola", "words": []}]

    with patch("src.ai.whisper_sub.WhisperTranscriber") as MockT:
        instance = MockT.return_value
        instance.transcribe.return_value = fake_segments

        worker = WhisperWorker(
            video_path="/fake/video.mp4",
            model_size="tiny",
            language="es",
            word_timestamps=False,
        )
        results = []
        worker.finished.connect(results.append)
        with qtbot.waitSignal(worker.finished, timeout=5000):
            worker.start()

    assert results == [fake_segments]


def test_whisper_worker_emits_error_on_exception(qtbot):
    from src.core.workers import WhisperWorker

    with patch("src.ai.whisper_sub.WhisperTranscriber") as MockT:
        MockT.side_effect = RuntimeError("modelo no encontrado")

        worker = WhisperWorker(video_path="/fake/video.mp4", model_size="tiny")
        errors = []
        worker.error.connect(errors.append)
        with qtbot.waitSignal(worker.error, timeout=5000):
            worker.start()

    assert len(errors) == 1
    assert "modelo no encontrado" in errors[0]


def test_text_animation_worker_emits_finished(qtbot, tmp_path):
    from src.core.workers import TextAnimationWorker

    fake_clip = str(tmp_path / "clip.mov")

    with patch("src.core.text_animator.TextAnimator") as MockA:
        instance = MockA.return_value
        instance.generate_text_clip.return_value = fake_clip

        worker = TextAnimationWorker(
            text="Hola mundo",
            duration=2.0,
            animation_in="fade_in",
            animation_out="fade_out",
            style={"font": "Arial", "size": 48, "color": "#FFFFFF"},
        )
        results = []
        worker.finished.connect(results.append)
        with qtbot.waitSignal(worker.finished, timeout=5000):
            worker.start()

    assert results == [fake_clip]


def test_text_animation_worker_emits_error(qtbot):
    from src.core.workers import TextAnimationWorker

    with patch("src.core.text_animator.TextAnimator") as MockA:
        MockA.side_effect = RuntimeError("ffmpeg no disponible")

        worker = TextAnimationWorker(
            text="Test",
            duration=1.0,
            animation_in="none",
            animation_out="none",
            style={},
        )
        errors = []
        worker.error.connect(errors.append)
        with qtbot.waitSignal(worker.error, timeout=5000):
            worker.start()

    assert "ffmpeg no disponible" in errors[0]
