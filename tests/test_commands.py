"""Tests para command pattern undo/redo"""
import pytest
from src.core.timeline import Timeline, Track, Clip, TrackType
from src.core.commands import (
    AddClipCommand, RemoveClipCommand, MoveClipCommand, CommandStack
)


@pytest.fixture
def tl():
    t = Timeline()
    t.add_track(Track(id="v1", name="Video", type=TrackType.VIDEO))
    return t


def make_clip(cid="c1", start=0.0, duration=5.0):
    return Clip(id=cid, name=cid, source="/x.mp4", start=start, duration=duration, track_id="v1")


def test_add_clip_command_executes(tl):
    cmd = AddClipCommand(tl, "v1", make_clip())
    cmd.execute()
    assert tl.get_clip("c1") is not None


def test_add_clip_command_undo(tl):
    cmd = AddClipCommand(tl, "v1", make_clip())
    cmd.execute()
    cmd.undo()
    assert tl.get_clip("c1") is None


def test_remove_clip_command_undo_restores(tl):
    tl.add_clip("v1", make_clip())
    cmd = RemoveClipCommand(tl, "c1")
    cmd.execute()
    assert tl.get_clip("c1") is None
    cmd.undo()
    assert tl.get_clip("c1") is not None


def test_move_clip_command_undo_restores_position(tl):
    tl.add_clip("v1", make_clip(cid="c1", start=0.0))
    cmd = MoveClipCommand(tl, "c1", new_start=20.0)
    cmd.execute()
    assert tl.get_clip("c1").start == 20.0
    cmd.undo()
    assert tl.get_clip("c1").start == 0.0


def test_command_stack_undo_redo(tl):
    stack = CommandStack()
    stack.push(AddClipCommand(tl, "v1", make_clip(cid="a")))
    stack.push(AddClipCommand(tl, "v1", make_clip(cid="b", start=10.0)))
    assert tl.get_clip("a") and tl.get_clip("b")
    stack.undo()
    assert tl.get_clip("a") and tl.get_clip("b") is None
    stack.undo()
    assert tl.get_clip("a") is None
    stack.redo()
    assert tl.get_clip("a") is not None


def test_command_stack_push_clears_redo(tl):
    stack = CommandStack()
    stack.push(AddClipCommand(tl, "v1", make_clip(cid="a")))
    stack.undo()
    stack.push(AddClipCommand(tl, "v1", make_clip(cid="b", start=10.0)))
    assert not stack.can_redo()
