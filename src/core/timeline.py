"""Gestion de timeline, tracks y clips"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class TrackType(Enum):
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    SUBTITLE = "subtitle"
    EFFECT = "effect"


@dataclass
class Clip:
    id: str
    name: str
    source: str
    start: float
    duration: float
    track_id: str
    volume: float = 1.0
    opacity: float = 1.0

    @property
    def end(self) -> float:
        return self.start + self.duration


@dataclass
class Track:
    id: str
    name: str
    type: TrackType
    clips: List[Clip] = field(default_factory=list)
    visible: bool = True
    locked: bool = False
    muted: bool = False


class Timeline:
    """Timeline: contenedor ordenado de tracks y clips"""

    def __init__(self, fps: int = 30, duration: float = 300.0):
        self.fps = fps
        self.duration = duration
        self.tracks: List[Track] = []
        self.playhead: float = 0.0

    def add_track(self, track: Track) -> None:
        if any(t.id == track.id for t in self.tracks):
            raise ValueError(f"track_id duplicado: {track.id}")
        self.tracks.append(track)

    def get_track(self, track_id: str) -> Optional[Track]:
        return next((t for t in self.tracks if t.id == track_id), None)

    def add_clip(self, track_id: str, clip: Clip) -> None:
        track = self.get_track(track_id)
        if track is None:
            raise ValueError(f"track_id no existe: {track_id}")
        for existing in track.clips:
            if not (clip.end <= existing.start or clip.start >= existing.end):
                raise ValueError(
                    f"clip {clip.id} overlap con {existing.id} en track {track_id}"
                )
        clip.track_id = track_id
        track.clips.append(clip)
        track.clips.sort(key=lambda c: c.start)

    def get_clip(self, clip_id: str) -> Optional[Clip]:
        for t in self.tracks:
            for c in t.clips:
                if c.id == clip_id:
                    return c
        return None

    def remove_clip(self, clip_id: str) -> bool:
        for t in self.tracks:
            for c in list(t.clips):
                if c.id == clip_id:
                    t.clips.remove(c)
                    return True
        return False

    def move_clip(self, clip_id: str, new_start: float) -> None:
        clip = self.get_clip(clip_id)
        if clip is None:
            raise ValueError(f"clip no existe: {clip_id}")
        clip.start = new_start
        track = self.get_track(clip.track_id)
        if track:
            track.clips.sort(key=lambda c: c.start)

    def get_clip_at(self, track_id: str, time: float) -> Optional[Clip]:
        track = self.get_track(track_id)
        if track is None:
            return None
        for c in track.clips:
            if c.start <= time < c.end:
                return c
        return None

    def total_duration(self) -> float:
        max_end = 0.0
        for t in self.tracks:
            for c in t.clips:
                if c.end > max_end:
                    max_end = c.end
        return max_end
