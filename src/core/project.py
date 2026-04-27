"""Proyecto: serializacion y deserializacion JSON"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict
from src.core.timeline import Timeline, Track, Clip, TrackType


PROJECT_VERSION = 1


@dataclass
class Project:
    name: str
    timeline: Timeline
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": PROJECT_VERSION,
            "name": self.name,
            "metadata": self.metadata,
            "timeline": {
                "fps": self.timeline.fps,
                "duration": self.timeline.duration,
                "playhead": self.timeline.playhead,
                "tracks": [
                    {
                        "id": t.id,
                        "name": t.name,
                        "type": t.type.value,
                        "visible": t.visible,
                        "locked": t.locked,
                        "muted": t.muted,
                        "clips": [
                            {
                                "id": c.id,
                                "name": c.name,
                                "source": c.source,
                                "start": c.start,
                                "duration": c.duration,
                                "track_id": c.track_id,
                                "volume": c.volume,
                                "opacity": c.opacity,
                            }
                            for c in t.clips
                        ],
                    }
                    for t in self.timeline.tracks
                ],
            },
        }

    def save(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False))

    @classmethod
    def load(cls, path: Path) -> "Project":
        path = Path(path)
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON invalido: {e}") from e
        if "version" not in data:
            raise ValueError("falta campo 'version' en proyecto")
        if data["version"] != PROJECT_VERSION:
            raise ValueError(
                f"version {data['version']} incompatible (esperado {PROJECT_VERSION})"
            )
        tl_data = data["timeline"]
        tl = Timeline(fps=tl_data.get("fps", 30), duration=tl_data.get("duration", 300.0))
        tl.playhead = tl_data.get("playhead", 0.0)
        for t_data in tl_data.get("tracks", []):
            track = Track(
                id=t_data["id"],
                name=t_data["name"],
                type=TrackType(t_data["type"]),
                visible=t_data.get("visible", True),
                locked=t_data.get("locked", False),
                muted=t_data.get("muted", False),
            )
            tl.add_track(track)
            for c_data in t_data.get("clips", []):
                clip = Clip(
                    id=c_data["id"],
                    name=c_data["name"],
                    source=c_data["source"],
                    start=c_data["start"],
                    duration=c_data["duration"],
                    track_id=c_data["track_id"],
                    volume=c_data.get("volume", 1.0),
                    opacity=c_data.get("opacity", 1.0),
                )
                tl.add_clip(track.id, clip)
        return cls(
            name=data.get("name", "Untitled"),
            timeline=tl,
            metadata=data.get("metadata", {}),
        )
