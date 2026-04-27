"""Timeline widget: QGraphicsView con tracks horizontales y clips renderizados."""
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPen, QPainter
from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
)
from src.core.timeline import Timeline, TrackType, Clip


TRACK_HEIGHT = 50
TRACK_LABEL_WIDTH = 100
PIXELS_PER_SECOND = 50  # zoom 1.0
PLAYHEAD_WIDTH = 2


TRACK_COLORS = {
    TrackType.VIDEO: QColor("#264f78"),
    TrackType.AUDIO: QColor("#3e7d32"),
    TrackType.TEXT: QColor("#9c5400"),
    TrackType.SUBTITLE: QColor("#7e3e8b"),
    TrackType.EFFECT: QColor("#a83232"),
}


class TimelineWidget(QGraphicsView):
    """Renderiza el Timeline con zoom (mouse wheel + Ctrl) y seleción de clips."""

    clipSelected = pyqtSignal(str)  # clip_id
    playheadChanged = pyqtSignal(float)  # segundos

    def __init__(self, timeline: Timeline, parent=None):
        super().__init__(parent)
        self.timeline = timeline
        self.zoom = 1.0
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setBackgroundBrush(QBrush(QColor("#181818")))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._playhead_item: QGraphicsRectItem | None = None
        self._clip_items: dict[str, QGraphicsRectItem] = {}
        self.refresh()

    def refresh(self) -> None:
        """Redibuja todo el timeline desde el modelo."""
        self._scene.clear()
        self._clip_items.clear()
        self._playhead_item = None

        for i, track in enumerate(self.timeline.tracks):
            y = i * TRACK_HEIGHT
            bg = QGraphicsRectItem(0, y, 10000, TRACK_HEIGHT - 2)
            bg.setBrush(QBrush(QColor("#252526")))
            bg.setPen(QPen(QColor("#3a3a3a")))
            self._scene.addItem(bg)

            label = QGraphicsTextItem(track.name)
            label.setDefaultTextColor(QColor("#e0e0e0"))
            label.setPos(4, y + 4)
            self._scene.addItem(label)

            for clip in track.clips:
                self._add_clip_item(clip, y, track.type)

        self._draw_playhead()
        self._update_scene_rect()

    def _add_clip_item(self, clip: Clip, track_y: float, track_type: TrackType) -> None:
        x = TRACK_LABEL_WIDTH + clip.start * PIXELS_PER_SECOND * self.zoom
        w = clip.duration * PIXELS_PER_SECOND * self.zoom
        item = QGraphicsRectItem(x, track_y + 4, w, TRACK_HEIGHT - 10)
        item.setBrush(QBrush(TRACK_COLORS.get(track_type, QColor("#555"))))
        item.setPen(QPen(QColor("#ffffff"), 1))
        item.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        item.setData(0, clip.id)
        self._scene.addItem(item)

        text = QGraphicsTextItem(clip.name, item)
        text.setDefaultTextColor(QColor("white"))
        text.setPos(x + 4, track_y + 6)

        self._clip_items[clip.id] = item

    def _draw_playhead(self) -> None:
        x = TRACK_LABEL_WIDTH + self.timeline.playhead * PIXELS_PER_SECOND * self.zoom
        height = max(len(self.timeline.tracks), 1) * TRACK_HEIGHT
        self._playhead_item = QGraphicsRectItem(x, 0, PLAYHEAD_WIDTH, height)
        self._playhead_item.setBrush(QBrush(QColor("#ff5050")))
        self._playhead_item.setPen(QPen(Qt.PenStyle.NoPen))
        self._scene.addItem(self._playhead_item)

    def _update_scene_rect(self) -> None:
        height = max(len(self.timeline.tracks), 1) * TRACK_HEIGHT
        width = TRACK_LABEL_WIDTH + max(self.timeline.total_duration(), 30.0) * PIXELS_PER_SECOND * self.zoom + 200
        self._scene.setSceneRect(QRectF(0, 0, width, height))

    def set_playhead(self, seconds: float) -> None:
        self.timeline.playhead = seconds
        if self._playhead_item:
            x = TRACK_LABEL_WIDTH + seconds * PIXELS_PER_SECOND * self.zoom
            self._playhead_item.setX(x)
        self.playheadChanged.emit(seconds)

    def wheelEvent(self, event) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            factor = 1.15 if delta > 0 else 1 / 1.15
            self.zoom = max(0.1, min(10.0, self.zoom * factor))
            self.refresh()
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event) -> None:
        item = self.itemAt(event.pos())
        if item and item.data(0):
            self.clipSelected.emit(str(item.data(0)))
        else:
            scene_x = self.mapToScene(event.pos()).x()
            seconds = max(0.0, (scene_x - TRACK_LABEL_WIDTH) / (PIXELS_PER_SECOND * self.zoom))
            self.set_playhead(seconds)
        super().mousePressEvent(event)
