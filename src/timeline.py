"""Gestión de timeline y clips"""
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class TrackType(Enum):
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"

@dataclass
class Clip:
    """Representa un clip en la timeline"""
    id: str
    name: str
    source: str  # Ruta del archivo
    start: float  # Tiempo inicio en segundos
    duration: float
    track_id: str
    volume: float = 1.0
    opacity: float = 1.0

@dataclass
class Track:
    """Pista de la timeline"""
    id: str
    name: str
    type: TrackType
    clips: List[Clip] = field(default_factory=list)
    visible: bool = True
    locked: bool = False

class Timeline:
    """Gestiona la timeline completa"""

    def __init__(self, fps: int = 30, duration: float = 300.0):
        self.fps = fps
        self.duration = duration
        self.tracks: List[Track] = []
        self.playhead = 0.0

    def add_track(self, track: Track) -> None:
        """Añadir pista"""
        self.tracks.append(track)

    def add_clip(self, track_id: str, clip: Clip) -> None:
        """Añadir clip a una pista"""
        track = next((t for t in self.tracks if t.id == track_id), None)
        if track:
            track.clips.append(clip)
