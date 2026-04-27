"""Overlay transparente que renderiza subtítulos sobre el preview en tiempo real."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QFont, QPen
from PyQt6.QtWidgets import QWidget

from src.core.subtitle_renderer import SubtitleRenderer


# Factores de posición normalizados (x_rel, y_rel) respecto al área del widget
_POSITION_MAP = {
    "bottom_center": (0.5, 0.88),
    "top_center": (0.5, 0.08),
    "center": (0.5, 0.5),
    "bottom_left": (0.05, 0.88),
    "bottom_right": (0.95, 0.88),
    "top_left": (0.05, 0.08),
    "top_right": (0.95, 0.08),
}


class SubtitlePreviewOverlay(QWidget):
    """
    Widget transparente que se superpone sobre QVideoWidget.
    Renderiza el segmento activo con QPainter en sync con el timecode.
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        # Transparente y sin capturar eventos de ratón
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self._segments: list[dict] = []
        self._style_name: str = "clasico"
        self._current_time: float = 0.0
        self._active_seg: dict | None = None

        # Ajustarse al tamaño del padre al inicio
        if parent:
            self.resize(parent.size())
            self.raise_()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def set_segments(self, segments: list[dict], style_name: str | None = None) -> None:
        self._segments = segments
        if style_name:
            self._style_name = style_name
        self._find_active_segment()
        self.update()

    def set_style(self, style_name: str) -> None:
        self._style_name = style_name
        self.update()

    def set_current_time(self, t: float) -> None:
        self._current_time = t
        self._find_active_segment()
        self.update()

    # ------------------------------------------------------------------
    # Eventos Qt
    # ------------------------------------------------------------------

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)

    def paintEvent(self, event) -> None:
        if not self._active_seg:
            return

        style = SubtitleRenderer.STYLES.get(
            self._style_name, SubtitleRenderer.STYLES["clasico"]
        )
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if style.get("word_by_word"):
            self._paint_word_by_word(painter, self._active_seg, style)
        else:
            self._paint_segment(painter, self._active_seg, style)

        painter.end()

    # ------------------------------------------------------------------
    # Helpers de renderizado
    # ------------------------------------------------------------------

    def _paint_segment(self, painter: QPainter, seg: dict, style: dict) -> None:
        text = seg.get("text", "").strip()
        if not text:
            return

        font = self._make_font(style)
        painter.setFont(font)

        color = QColor(style.get("color", "white"))
        outline_color = QColor(style.get("outline_color", "black") or "black")
        outline_w = style.get("outline_width", 2)
        position = style.get("position", "bottom_center")

        rect = self._text_rect(painter, text, position)

        # Outline (dibuja el texto desplazado en las 8 direcciones)
        if outline_w > 0:
            painter.setPen(QPen(outline_color))
            for dx in range(-outline_w, outline_w + 1):
                for dy in range(-outline_w, outline_w + 1):
                    if dx == 0 and dy == 0:
                        continue
                    r = rect.translated(dx, dy)
                    painter.drawText(r, Qt.AlignmentFlag.AlignCenter, text)

        painter.setPen(QPen(color))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

    def _paint_word_by_word(self, painter: QPainter, seg: dict, style: dict) -> None:
        """Pinta palabras del segmento, resaltando la activa en dorado."""
        words = seg.get("words", [])
        if not words:
            self._paint_segment(painter, seg, style)
            return

        font = self._make_font(style)
        painter.setFont(font)
        position = style.get("position", "bottom_center")
        active_color = QColor(style.get("active_color", "#FFD700"))
        inactive_color = QColor(style.get("inactive_color", "white"))
        outline_color = QColor(style.get("outline_color", "black") or "black")
        outline_w = style.get("outline_width", 2)

        full_text = " ".join(w["word"] for w in words)
        rect = self._text_rect(painter, full_text, position)

        # Construye texto con palabra activa resaltada como bloque
        t = self._current_time
        parts: list[tuple[str, bool]] = []
        for w in words:
            is_active = w["start"] <= t < w["end"]
            parts.append((w["word"], is_active))

        # Dibuja el texto completo con colores mixtos
        # Simplificación: pintamos todo en inactivo primero, luego la palabra activa
        if outline_w > 0:
            painter.setPen(QPen(outline_color))
            for dx in range(-outline_w, outline_w + 1):
                for dy in range(-outline_w, outline_w + 1):
                    if dx == 0 and dy == 0:
                        continue
                    painter.drawText(
                        rect.translated(dx, dy), Qt.AlignmentFlag.AlignCenter, full_text
                    )

        painter.setPen(QPen(inactive_color))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, full_text)

        # Superpone la palabra activa en dorado usando el mismo rect base
        for w, is_active in parts:
            if is_active:
                active_rect = self._text_rect(painter, w, position)
                if outline_w > 0:
                    painter.setPen(QPen(outline_color))
                    for dx in range(-outline_w, outline_w + 1):
                        for dy in range(-outline_w, outline_w + 1):
                            if dx == 0 and dy == 0:
                                continue
                            painter.drawText(
                                active_rect.translated(dx, dy),
                                Qt.AlignmentFlag.AlignCenter, w,
                            )
                painter.setPen(QPen(active_color))
                painter.drawText(active_rect, Qt.AlignmentFlag.AlignCenter, w)
                break

    def _text_rect(self, painter: QPainter, text: str, position: str):
        fm = painter.fontMetrics()
        text_w = fm.horizontalAdvance(text)
        text_h = fm.height()
        W = self.width()
        H = self.height()
        x_rel, y_rel = _POSITION_MAP.get(position, (0.5, 0.88))
        cx = int(W * x_rel)
        cy = int(H * y_rel)
        from PyQt6.QtCore import QRect
        return QRect(cx - text_w // 2, cy - text_h // 2, text_w + 10, text_h + 4)

    @staticmethod
    def _make_font(style: dict) -> QFont:
        font_name = style.get("font", "Arial").replace(" Bold", "")
        bold = "Bold" in style.get("font", "")
        size = style.get("size", 48)
        f = QFont(font_name, max(8, size // 2))  # dividir entre 2 aprox para preview
        f.setBold(bold)
        return f

    # ------------------------------------------------------------------
    # Búsqueda de segmento activo
    # ------------------------------------------------------------------

    def _find_active_segment(self) -> None:
        t = self._current_time
        self._active_seg = None
        for seg in self._segments:
            if seg["start"] <= t < seg["end"]:
                self._active_seg = seg
                return
