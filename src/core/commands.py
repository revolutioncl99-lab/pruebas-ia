"""Command pattern para undo/redo"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.timeline import Timeline, Clip


class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...
    @abstractmethod
    def undo(self) -> None: ...


class AddClipCommand(Command):
    def __init__(self, timeline: Timeline, track_id: str, clip: Clip):
        self.timeline = timeline
        self.track_id = track_id
        self.clip = clip

    def execute(self) -> None:
        self.timeline.add_clip(self.track_id, self.clip)

    def undo(self) -> None:
        self.timeline.remove_clip(self.clip.id)


class RemoveClipCommand(Command):
    def __init__(self, timeline: Timeline, clip_id: str):
        self.timeline = timeline
        self.clip_id = clip_id
        self._removed: Optional[Clip] = None
        self._track_id: Optional[str] = None

    def execute(self) -> None:
        clip = self.timeline.get_clip(self.clip_id)
        if clip is None:
            raise ValueError(f"clip no existe: {self.clip_id}")
        self._removed = Clip(
            id=clip.id, name=clip.name, source=clip.source,
            start=clip.start, duration=clip.duration, track_id=clip.track_id,
            volume=clip.volume, opacity=clip.opacity,
        )
        self._track_id = clip.track_id
        self.timeline.remove_clip(self.clip_id)

    def undo(self) -> None:
        if self._removed and self._track_id:
            self.timeline.add_clip(self._track_id, self._removed)


class MoveClipCommand(Command):
    def __init__(self, timeline: Timeline, clip_id: str, new_start: float):
        self.timeline = timeline
        self.clip_id = clip_id
        self.new_start = new_start
        self._old_start: Optional[float] = None

    def execute(self) -> None:
        clip = self.timeline.get_clip(self.clip_id)
        if clip is None:
            raise ValueError(f"clip no existe: {self.clip_id}")
        self._old_start = clip.start
        self.timeline.move_clip(self.clip_id, self.new_start)

    def undo(self) -> None:
        if self._old_start is not None:
            self.timeline.move_clip(self.clip_id, self._old_start)


class CommandStack:
    """Stack de comandos con undo/redo."""

    def __init__(self, max_history: int = 100):
        self._undo_stack: List[Command] = []
        self._redo_stack: List[Command] = []
        self.max_history = max_history

    def push(self, cmd: Command) -> None:
        cmd.execute()
        self._undo_stack.append(cmd)
        if len(self._undo_stack) > self.max_history:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self) -> bool:
        if not self._undo_stack:
            return False
        cmd = self._undo_stack.pop()
        cmd.undo()
        self._redo_stack.append(cmd)
        return True

    def redo(self) -> bool:
        if not self._redo_stack:
            return False
        cmd = self._redo_stack.pop()
        cmd.execute()
        self._undo_stack.append(cmd)
        return True

    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    def can_redo(self) -> bool:
        return bool(self._redo_stack)
