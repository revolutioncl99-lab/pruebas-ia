"""Tests para core.subtitle_renderer."""
import pytest
from src.core.subtitle_renderer import SubtitleRenderer


def test_styles_dict_has_required_keys():
    required = {"clasico", "capcut", "tiktok", "minimal", "bold_cinematic"}
    assert required.issubset(set(SubtitleRenderer.STYLES.keys()))


def test_clasico_style_not_word_by_word():
    style = SubtitleRenderer.STYLES["clasico"]
    assert style["word_by_word"] is False


def test_capcut_style_is_word_by_word():
    style = SubtitleRenderer.STYLES["capcut"]
    assert style["word_by_word"] is True
    assert "active_color" in style
    assert "inactive_color" in style


def test_build_drawtext_filter_empty_segments():
    r = SubtitleRenderer()
    result = r._build_drawtext_filter([], SubtitleRenderer.STYLES["clasico"])
    assert result == "null"


def test_build_drawtext_filter_classic_single_segment():
    r = SubtitleRenderer()
    segments = [{"start": 1.0, "end": 3.0, "text": "Hola mundo", "words": []}]
    result = r._build_drawtext_filter(segments, SubtitleRenderer.STYLES["clasico"])
    assert "drawtext=" in result
    assert "Hola mundo" in result
    assert "between(t,1.000,3.000)" in result


def test_build_drawtext_filter_capcut_with_words():
    r = SubtitleRenderer()
    segments = [{
        "start": 0.0,
        "end": 2.0,
        "text": "Hola mundo",
        "words": [
            {"word": "Hola", "start": 0.0, "end": 1.0},
            {"word": "mundo", "start": 1.0, "end": 2.0},
        ],
    }]
    result = r._build_drawtext_filter(segments, SubtitleRenderer.STYLES["capcut"])
    # Debe haber múltiples drawtext (activo + inactivo por cada palabra)
    assert result.count("drawtext=") >= 4


def test_position_exprs_bottom_center():
    x, y = SubtitleRenderer._position_exprs("bottom_center")
    assert "w-text_w" in x
    assert "h-text_h" in y


def test_position_exprs_unknown_defaults_to_bottom_center():
    x, y = SubtitleRenderer._position_exprs("invalid_pos")
    default_x, default_y = SubtitleRenderer._position_exprs("bottom_center")
    assert x == default_x
    assert y == default_y


def test_drawtext_escapes_apostrophe():
    r = SubtitleRenderer()
    segments = [{"start": 0.0, "end": 1.0, "text": "it's fine", "words": []}]
    result = r._build_drawtext_filter(segments, SubtitleRenderer.STYLES["clasico"])
    assert "\\'" in result


def test_srt_export(tmp_path):
    """Verifica que el módulo subtitle_editor exporta SRT correctamente."""
    from src.ui.subtitle_editor import _export_srt
    segments = [
        {"start": 0.0, "end": 2.5, "text": "Primer segmento"},
        {"start": 3.0, "end": 5.0, "text": "Segundo segmento"},
    ]
    out = str(tmp_path / "output.srt")
    _export_srt(segments, out)

    content = open(out).read()
    assert "Primer segmento" in content
    assert "Segundo segmento" in content
    assert "00:00:00,000 --> 00:00:02,500" in content


def test_srt_parse_roundtrip(tmp_path):
    """Parsear un SRT generado debe devolver los segmentos originales."""
    from src.ui.subtitle_editor import _export_srt, SubtitleEditor
    segments = [
        {"start": 1.0, "end": 3.0, "text": "Hola mundo"},
        {"start": 4.0, "end": 6.0, "text": "Bye bye"},
    ]
    srt_path = str(tmp_path / "test.srt")
    _export_srt(segments, srt_path)

    parsed = SubtitleEditor._parse_srt(srt_path)
    assert len(parsed) == 2
    assert abs(parsed[0]["start"] - 1.0) < 0.01
    assert abs(parsed[0]["end"] - 3.0) < 0.01
    assert parsed[0]["text"] == "Hola mundo"
