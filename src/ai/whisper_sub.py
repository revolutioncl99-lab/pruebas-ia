"""Transcripción automática de video con Whisper AI."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Callable


class WhisperTranscriber:
    """Carga un modelo Whisper y transcribe audio extraído de video."""

    def __init__(self, model_size: str = "medium"):
        import whisper  # importación diferida para arranque rápido
        self._model = whisper.load_model(model_size)

    # ------------------------------------------------------------------
    # Métodos públicos
    # ------------------------------------------------------------------

    def transcribe(
        self,
        video_path: str,
        language: str | None = None,
        progress_callback: Callable[[int], None] | None = None,
    ) -> list[dict]:
        """
        Transcribe el video y devuelve segmentos con timestamps.

        Retorna lista de dicts:
          {"start": float, "end": float, "text": str, "words": list[dict]}
        """
        audio_path = self._extract_audio(video_path)
        try:
            options: dict = {"word_timestamps": True}
            if language:
                options["language"] = language

            result = self._model.transcribe(audio_path, **options)
            segments = self._parse_segments(result["segments"])
            if progress_callback:
                progress_callback(100)
            return segments
        finally:
            Path(audio_path).unlink(missing_ok=True)

    def transcribe_word_by_word(
        self,
        video_path: str,
        progress_callback: Callable[[int], None] | None = None,
    ) -> list[dict]:
        """
        Transcribe con timestamps por palabra para efecto estilo TikTok/CapCut.

        Retorna lista de dicts por palabra:
          {"start": float, "end": float, "text": str, "words": [{"word": str,
           "start": float, "end": float}]}
        Los segmentos son los mismos que transcribe(), word_timestamps=True
        ya incluye las palabras en cada segmento.
        """
        return self.transcribe(
            video_path, language=None, progress_callback=progress_callback
        )

    def export_srt(self, segments: list[dict], output_path: str) -> None:
        """Genera archivo .srt estándar a partir de los segmentos."""
        lines: list[str] = []
        for i, seg in enumerate(segments, start=1):
            lines.append(str(i))
            lines.append(
                f"{self._fmt_srt(seg['start'])} --> {self._fmt_srt(seg['end'])}"
            )
            lines.append(seg["text"].strip())
            lines.append("")
        Path(output_path).write_text("\n".join(lines), encoding="utf-8")

    def export_vtt(self, segments: list[dict], output_path: str) -> None:
        """Genera archivo .vtt para web a partir de los segmentos."""
        lines: list[str] = ["WEBVTT", ""]
        for seg in segments:
            lines.append(
                f"{self._fmt_vtt(seg['start'])} --> {self._fmt_vtt(seg['end'])}"
            )
            lines.append(seg["text"].strip())
            lines.append("")
        Path(output_path).write_text("\n".join(lines), encoding="utf-8")

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _extract_audio(self, video_path: str) -> str:
        """Extrae audio del video a WAV mono 16kHz en un archivo temporal."""
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            tmp.name,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg audio extract falló: {result.stderr[:400]}")
        return tmp.name

    @staticmethod
    def _parse_segments(raw_segments: list) -> list[dict]:
        """Convierte segmentos de Whisper al formato interno."""
        out: list[dict] = []
        for seg in raw_segments:
            words: list[dict] = []
            for w in seg.get("words", []):
                words.append({
                    "word": w.get("word", "").strip(),
                    "start": float(w.get("start", seg["start"])),
                    "end": float(w.get("end", seg["end"])),
                })
            out.append({
                "start": float(seg["start"]),
                "end": float(seg["end"]),
                "text": seg["text"].strip(),
                "words": words,
            })
        return out

    @staticmethod
    def _fmt_srt(seconds: float) -> str:
        """Formatea segundos a HH:MM:SS,mmm para SRT."""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int(round((seconds - int(seconds)) * 1000))
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    @staticmethod
    def _fmt_vtt(seconds: float) -> str:
        """Formatea segundos a HH:MM:SS.mmm para VTT."""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int(round((seconds - int(seconds)) * 1000))
        return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
