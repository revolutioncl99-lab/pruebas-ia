"""Renderizado de subtítulos en video usando filtros drawtext de FFmpeg."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Any


class SubtitleRenderer:
    """Quema subtítulos en video con varios estilos visuales."""

    STYLES: dict[str, dict[str, Any]] = {
        "clasico": {
            "font": "Arial",
            "size": 48,
            "color": "white",
            "outline_color": "black",
            "outline_width": 2,
            "position": "bottom_center",
            "background": False,
            "word_by_word": False,
        },
        "capcut": {
            "font": "Arial",
            "size": 52,
            "active_color": "#FFD700",
            "inactive_color": "white",
            "outline_color": "black",
            "outline_width": 2,
            "background": True,
            "background_color": "black@0.6",
            "position": "bottom_center",
            "word_by_word": True,
        },
        "tiktok": {
            "font": "Impact",
            "size": 60,
            "color": "white",
            "outline_color": "black",
            "outline_width": 3,
            "shadow": True,
            "position": "center",
            "background": False,
            "word_by_word": False,
        },
        "minimal": {
            "font": "Arial",
            "size": 40,
            "color": "white",
            "outline_color": "",
            "outline_width": 0,
            "opacity": 0.9,
            "position": "bottom_center",
            "background": False,
            "word_by_word": False,
        },
        "bold_cinematic": {
            "font": "Arial Bold",
            "size": 56,
            "color": "#FFFFFF",
            "outline_color": "#000000",
            "outline_width": 3,
            "position": "bottom_center",
            "background": False,
            "word_by_word": False,
        },
    }

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def render_subtitles(
        self,
        input_video: str,
        segments: list[dict],
        style_name: str,
        output_video: str,
    ) -> bool:
        """Aplica subtítulos al video usando drawtext y guarda el resultado."""
        style = self.STYLES.get(style_name, self.STYLES["clasico"])
        vf = self._build_drawtext_filter(segments, style)
        cmd = [
            "ffmpeg", "-y",
            "-i", input_video,
            "-vf", vf,
            "-c:a", "copy",
            output_video,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return result.returncode == 0

    def preview_frame(self, video_path: str, frame_number: int, segment: dict,
                      style_name: str, fps: float = 30.0) -> bytes:
        """
        Genera un frame PNG con el subtítulo aplicado.
        Retorna bytes PNG para mostrar en el panel de preview.
        """
        style = self.STYLES.get(style_name, self.STYLES["clasico"])
        timestamp = frame_number / fps

        # Segmento ficticio válido para el timestamp actual
        seg_wrapped = [{
            "start": timestamp,
            "end": timestamp + 0.04,
            "text": segment.get("text", ""),
            "words": segment.get("words", []),
        }]
        vf = self._build_drawtext_filter(seg_wrapped, style)

        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp.close()
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(timestamp),
            "-i", video_path,
            "-vf", vf,
            "-vframes", "1",
            tmp.name,
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        if result.returncode != 0:
            Path(tmp.name).unlink(missing_ok=True)
            return b""
        data = Path(tmp.name).read_bytes()
        Path(tmp.name).unlink(missing_ok=True)
        return data

    # ------------------------------------------------------------------
    # Construcción de filtros FFmpeg
    # ------------------------------------------------------------------

    def _build_drawtext_filter(self, segments: list[dict], style: dict) -> str:
        """Construye el filtro vf completo (cadena de drawtext separados por ,)."""
        parts: list[str] = []
        word_by_word = style.get("word_by_word", False)

        if word_by_word:
            parts = self._build_capcut_filter(segments, style)
        else:
            parts = self._build_classic_filter(segments, style)

        return ",".join(parts) if parts else "null"

    def _build_classic_filter(self, segments: list[dict], style: dict) -> list[str]:
        """Un drawtext por segmento completo."""
        parts: list[str] = []
        x_expr, y_expr = self._position_exprs(style.get("position", "bottom_center"))
        font = style.get("font", "Arial")
        size = style.get("size", 48)
        color = style.get("color", "white")
        outline_color = style.get("outline_color", "black")
        outline_width = style.get("outline_width", 2)

        for seg in segments:
            text = seg["text"].strip().replace("'", "\\'").replace(":", "\\:")
            if not text:
                continue
            dt = (
                f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                f":text='{text}'"
                f":fontsize={size}"
                f":fontcolor={color}"
                f":bordercolor={outline_color}"
                f":borderw={outline_width}"
                f":x={x_expr}:y={y_expr}"
                f":enable='between(t,{seg['start']:.3f},{seg['end']:.3f})'"
            )
            parts.append(dt)
        return parts

    def _build_capcut_filter(self, segments: list[dict], style: dict) -> list[str]:
        """Un drawtext por palabra: palabra activa en dorado, resto en blanco."""
        parts: list[str] = []
        x_expr, y_expr = self._position_exprs(style.get("position", "bottom_center"))
        font_size = style.get("size", 52)
        active_color = style.get("active_color", "#FFD700")
        inactive_color = style.get("inactive_color", "white")
        outline_color = style.get("outline_color", "black")
        outline_width = style.get("outline_width", 2)

        for seg in segments:
            words = seg.get("words", [])
            if not words:
                # sin timestamps por palabra → tratar como clásico
                text = seg["text"].strip().replace("'", "\\'").replace(":", "\\:")
                if text:
                    parts.append(
                        f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                        f":text='{text}':fontsize={font_size}"
                        f":fontcolor={inactive_color}"
                        f":bordercolor={outline_color}:borderw={outline_width}"
                        f":x={x_expr}:y={y_expr}"
                        f":enable='between(t,{seg['start']:.3f},{seg['end']:.3f})'"
                    )
                continue

            for word in words:
                w_text = word["word"].replace("'", "\\'").replace(":", "\\:")
                if not w_text:
                    continue
                w_start = word["start"]
                w_end = word["end"]
                seg_start = seg["start"]
                seg_end = seg["end"]

                # Palabra activa (dorado) durante su ventana
                parts.append(
                    f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                    f":text='{w_text}':fontsize={font_size}"
                    f":fontcolor={active_color}"
                    f":bordercolor={outline_color}:borderw={outline_width}"
                    f":x={x_expr}:y={y_expr}"
                    f":enable='between(t,{w_start:.3f},{w_end:.3f})'"
                )
                # Misma palabra en blanco fuera de su ventana (dentro del segmento)
                parts.append(
                    f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                    f":text='{w_text}':fontsize={font_size}"
                    f":fontcolor={inactive_color}"
                    f":bordercolor={outline_color}:borderw={outline_width}"
                    f":x={x_expr}:y={y_expr}"
                    f":enable='between(t,{seg_start:.3f},{w_start:.3f})+between(t,{w_end:.3f},{seg_end:.3f})'"
                )
        return parts

    @staticmethod
    def _position_exprs(position: str) -> tuple[str, str]:
        """Convierte nombre de posición a expresiones x/y para drawtext."""
        mapping = {
            "bottom_center": ("(w-text_w)/2", "h-text_h-30"),
            "top_center": ("(w-text_w)/2", "30"),
            "center": ("(w-text_w)/2", "(h-text_h)/2"),
            "bottom_left": ("20", "h-text_h-30"),
            "bottom_right": ("w-text_w-20", "h-text_h-30"),
            "top_left": ("20", "30"),
            "top_right": ("w-text_w-20", "30"),
        }
        return mapping.get(position, mapping["bottom_center"])
