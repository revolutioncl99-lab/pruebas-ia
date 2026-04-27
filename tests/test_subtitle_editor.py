"""Tests para ui.subtitle_editor."""
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def editor(qtbot):
    from src.ui.subtitle_editor import SubtitleEditor
    w = SubtitleEditor()
    qtbot.addWidget(w)
    return w


def test_subtitle_editor_creates_without_error(editor):
    assert editor is not None


def test_table_starts_empty(editor):
    assert editor.table.rowCount() == 0


def test_populate_table_fills_rows(editor):
    segments = [
        {"start": 0.0, "end": 2.0, "text": "Hola", "words": []},
        {"start": 2.5, "end": 4.0, "text": "Mundo", "words": []},
    ]
    editor._populate_table(segments)
    assert editor.table.rowCount() == 2


def test_populate_table_text_column(editor):
    segments = [{"start": 1.0, "end": 2.0, "text": "Test segmento", "words": []}]
    editor._populate_table(segments)
    assert editor.table.item(0, 3).text() == "Test segmento"


def test_populate_table_timing_columns(editor):
    segments = [{"start": 1.5, "end": 3.75, "text": "Timing test", "words": []}]
    editor._populate_table(segments)
    assert float(editor.table.item(0, 1).text()) == pytest.approx(1.5, abs=0.01)
    assert float(editor.table.item(0, 2).text()) == pytest.approx(3.75, abs=0.01)


def test_style_combobox_has_all_styles(editor):
    from src.core.subtitle_renderer import SubtitleRenderer
    expected = set(SubtitleRenderer.STYLES.keys())
    actual = {editor.combo_style.itemText(i) for i in range(editor.combo_style.count())}
    assert expected.issubset(actual)


def test_model_combobox_has_medium(editor):
    items = [editor.combo_model.itemText(i) for i in range(editor.combo_model.count())]
    assert "medium" in items


def test_load_segments_emits_signal(editor, qtbot):
    segments = [{"start": 0.0, "end": 1.0, "text": "Señal", "words": []}]
    with qtbot.waitSignal(editor.segmentsChanged, timeout=1000):
        editor.load_segments(segments)


def test_style_change_emits_signal(editor, qtbot):
    with qtbot.waitSignal(editor.styleChanged, timeout=1000):
        editor.combo_style.setCurrentIndex(1)


def test_transcribe_without_video_shows_no_crash(editor, qtbot):
    """Clic en transcribir sin video no debe crashear — muestra warning."""
    editor._current_video = None
    # No debe lanzar excepción; la función muestra un QMessageBox
    # En tests headless esto no es interactivo, usamos monkeypatch
    from unittest.mock import patch
    with patch("src.ui.subtitle_editor.QMessageBox.warning"):
        editor._on_transcribe()


def test_parse_srt_basic():
    from src.ui.subtitle_editor import SubtitleEditor
    import tempfile, os
    content = "1\n00:00:01,000 --> 00:00:03,500\nHola mundo\n\n2\n00:00:04,000 --> 00:00:05,000\nAdiós\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".srt", delete=False) as f:
        f.write(content)
        path = f.name
    try:
        segs = SubtitleEditor._parse_srt(path)
        assert len(segs) == 2
        assert abs(segs[0]["start"] - 1.0) < 0.01
        assert abs(segs[0]["end"] - 3.5) < 0.01
        assert segs[1]["text"] == "Adiós"
    finally:
        os.unlink(path)
