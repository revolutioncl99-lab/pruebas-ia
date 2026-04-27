"""Tests para core.text_animator."""
import pytest
from src.core.text_animator import TextAnimator


def test_animations_dict_has_required_keys():
    required = {
        "fade_in", "slide_bottom", "slide_top", "slide_left", "slide_right",
        "zoom_in", "typewriter", "bounce", "glitch_in",
        "fade_out", "slide_out_bottom", "zoom_out",
        "pulse", "shake", "wave", "none",
    }
    assert required.issubset(set(TextAnimator.ANIMATIONS.keys()))


def test_animation_types_are_valid():
    valid_types = {"entrada", "salida", "loop"}
    for name, anim in TextAnimator.ANIMATIONS.items():
        assert anim["type"] in valid_types, f"{name} tiene tipo inválido: {anim['type']}"


def test_build_animation_filter_fade_in():
    a = TextAnimator()
    result = a._build_animation_filter("fade_in", 3.0, "in")
    assert "t/" in result
    assert "0.5" in result or "0.500" in result


def test_build_animation_filter_fade_out():
    a = TextAnimator()
    result = a._build_animation_filter("fade_out", 3.0, "out")
    assert "gt(t," in result


def test_build_animation_filter_shake():
    a = TextAnimator()
    result = a._build_animation_filter("shake", 2.0, "loop")
    assert "sin" in result


def test_build_animation_filter_unknown_returns_one():
    a = TextAnimator()
    result = a._build_animation_filter("nonexistent", 2.0, "in")
    assert result == "1"


def test_anim_duration_auto():
    a = TextAnimator()
    d = a._anim_duration("typewriter", 4.0)
    assert 0 < d <= 1.2  # min(4.0 * 0.3, 1.0) = 1.0


def test_anim_duration_fixed():
    a = TextAnimator()
    d = a._anim_duration("fade_in", 10.0)
    assert abs(d - 0.5) < 0.001


def test_position_x_center():
    result = TextAnimator._position_x("center", 1920)
    assert "w-text_w" in result


def test_position_y_bottom_center():
    result = TextAnimator._position_y("bottom_center", 1080)
    assert "h-text_h" in result


def test_resolve_font_known():
    a = TextAnimator()
    path = a._resolve_font("Arial Bold")
    assert "DejaVuSans-Bold" in path


def test_resolve_font_unknown_returns_default():
    a = TextAnimator()
    path = a._resolve_font("Unknown Font XYZ")
    assert "DejaVuSans.ttf" in path


def test_build_animation_exprs_fade_in_alpha():
    a = TextAnimator()
    x, y, alpha = a._build_animation_exprs(
        "fade_in", "fade_out", 3.0, 1920, 1080, "(w-text_w)/2", "(h-text_h)/2"
    )
    assert "lt(t," in alpha  # fade_in
    assert "gt(t," in alpha  # fade_out
    assert "min(" in alpha   # combinados


def test_build_animation_exprs_slide_bottom_y():
    a = TextAnimator()
    x, y, alpha = a._build_animation_exprs(
        "slide_bottom", "none", 2.0, 1920, 1080, "(w-text_w)/2", "(h-text_h)/2"
    )
    assert "lt(t," in y  # expresión condicional de entrada
