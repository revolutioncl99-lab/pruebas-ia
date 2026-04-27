# Editor de Video - Fase 1: Base + UI + Timeline + Import

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar un editor de video desktop funcional (PyQt6, dark mode) que abre, permite importar videos por drag & drop, los muestra en un timeline multi-track navegable, y guarda/carga proyectos en JSON. Sin render aún — solo el esqueleto editable.

**Architecture:** App Python con `src/` como paquete principal, separado en `core/` (modelo de datos, lógica pura testeable con TDD estricto) y `ui/` (widgets PyQt6 con smoke tests vía `pytest-qt`). El timeline usa `QGraphicsView` para zoom/pan/rendering eficiente. Estado del proyecto centralizado en `Project` (timeline + metadata) con patrón Command para undo/redo. Configuración global en `core/config.py` (singleton). Entry point en `src/main.py`.

**Tech Stack:** Python 3.11+, PyQt6 6.6+, ffmpeg-python (metadata), pytest + pytest-qt (testing), pydantic v2 (validación), QSS (dark mode).

---

## File Structure (estado al final de Fase 1)

```
EDITOR DE VIDEO/
├── src/
│   ├── __init__.py                  # NEW: paquete
│   ├── main.py                      # NEW: entry point QApplication
│   ├── core/
│   │   ├── __init__.py              # NEW
│   │   ├── config.py                # MOVED desde src/config.py
│   │   ├── timeline.py              # MOVED desde src/timeline.py + ampliado
│   │   ├── video_processor.py       # MOVED desde src/video_processor.py + metadata real
│   │   ├── project.py               # NEW: save/load JSON
│   │   └── commands.py              # NEW: command pattern undo/redo
│   ├── ui/
│   │   ├── __init__.py              # NEW
│   │   ├── main_window.py           # NEW: QMainWindow + layout
│   │   ├── timeline_widget.py       # NEW: QGraphicsView timeline
│   │   ├── preview_widget.py        # NEW: QVideoWidget + controles
│   │   ├── tools_panel.py           # NEW: sidebar izquierdo
│   │   └── properties_panel.py      # NEW: sidebar derecho
│   ├── ai/__init__.py               # NEW: stub vacío (Fase 3)
│   └── effects/__init__.py          # NEW: stub vacío (Fase 4)
├── assets/
│   └── styles/dark_theme.qss        # NEW: stylesheet dark mode
├── tests/
│   ├── __init__.py                  # NEW
│   ├── test_timeline.py             # NEW
│   ├── test_project.py              # NEW
│   ├── test_commands.py             # NEW
│   ├── test_video_processor.py      # NEW
│   └── test_main_window.py          # NEW: smoke tests UI
├── projects/                        # NEW: empty (user data)
├── install.bat                      # NEW: Windows installer
├── install.sh                       # NEW: macOS/Linux installer
├── requirements.txt                 # EXPANDED
└── README.md                        # exists (no tocar en Fase 1)
```

**Decisión de estructura:** El proyecto YA usa `src/` como root (no `video_editor/` como en spec). Se respeta esa convención. Los archivos existentes (`src/config.py`, `src/timeline.py`, `src/video_processor.py`) son stubs que se mueven a `src/core/` y se amplían. Esto es DRY (no duplicar) y respeta lo establecido.

---

## Task 0: Inicializar repositorio git (precondición)

**Files:** ninguno

**Justificación:** El plan usa commits frecuentes como técnica TDD. El proyecto actual NO es repositorio git (verificado en environment). Sin esto, todos los `git commit` y `git mv` fallarán.

- [ ] **Step 1: Verificar si ya hay repo git**

```bash
git status
```

Si responde "fatal: not a git repository" → continuar al Step 2. Si ya hay repo → saltar al Task 1.

- [ ] **Step 2: Inicializar git**

```bash
git init
git config user.email "revolutioncl99@gmail.com"
git config user.name "RevoCL"
```

- [ ] **Step 3: Verificar `.gitignore` excluye archivos correctos**

```bash
cat .gitignore
```

Debe contener al menos: `venv/`, `__pycache__/`, `*.pyc`, `temp/`, `projects/`, `.pytest_cache/`. Si falta algo, agregarlo:

```bash
cat > .gitignore <<'EOF'
__pycache__/
*.pyc
*.pyo
venv/
.venv/
temp/
projects/
.pytest_cache/
.coverage
htmlcov/
*.egg-info/
build/
dist/
.DS_Store
graphify-out/cache/
EOF
```

- [ ] **Step 4: Commit inicial del estado actual**

```bash
git add -A
git commit -m "chore: snapshot inicial pre-Fase 1"
```

Expected: `git log --oneline` muestra el primer commit.

---

## Task 1: Reestructurar directorios y mover archivos existentes a `src/core/`

**Files:**
- Create: `src/__init__.py`, `src/core/__init__.py`, `src/ui/__init__.py`, `src/ai/__init__.py`, `src/effects/__init__.py`, `tests/__init__.py`
- Move: `src/config.py` → `src/core/config.py`
- Move: `src/timeline.py` → `src/core/timeline.py`
- Move: `src/video_processor.py` → `src/core/video_processor.py`

- [ ] **Step 1: Crear directorios e `__init__.py` vacíos**

```bash
mkdir -p src/core src/ui src/ai src/effects assets/styles tests projects
touch src/__init__.py src/core/__init__.py src/ui/__init__.py src/ai/__init__.py src/effects/__init__.py tests/__init__.py
```

- [ ] **Step 2: Mover archivos existentes a `src/core/`**

```bash
git mv src/config.py src/core/config.py 2>/dev/null || mv src/config.py src/core/config.py
git mv src/timeline.py src/core/timeline.py 2>/dev/null || mv src/timeline.py src/core/timeline.py
git mv src/video_processor.py src/core/video_processor.py 2>/dev/null || mv src/video_processor.py src/core/video_processor.py
```

- [ ] **Step 3: Verificar que la estructura quedó correcta**

```bash
ls -la src/ src/core/
```

Expected: `src/` contiene `__init__.py`, `core/`, `ui/`, `ai/`, `effects/`. `src/core/` contiene `__init__.py`, `config.py`, `timeline.py`, `video_processor.py`.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "refactor: reorganizar src/ en subpaquetes core/ui/ai/effects"
```

---

## Task 2: Expandir `requirements.txt` con todas las deps de Fase 1

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Sobrescribir requirements.txt**

```text
# === Core ===
ffmpeg-python==0.2.1
pydantic==2.6.4
numpy==1.26.4
pillow==10.2.0

# === UI ===
PyQt6==6.6.1
PyQt6-Qt6==6.6.1

# === Testing ===
pytest==8.1.1
pytest-qt==4.4.0
pytest-cov==4.1.0
```

- [ ] **Step 2: Instalar dependencias en venv local**

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

Expected: instalación termina sin errores. `pip list` muestra PyQt6 6.6.1.

- [ ] **Step 3: Verificar PyQt6 importa correctamente**

```bash
python -c "from PyQt6.QtWidgets import QApplication; print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add requirements.txt
git commit -m "chore: añadir PyQt6, pytest-qt y deps de UI"
```

---

## Task 3: Script de instalación Windows (`install.bat`)

**Files:**
- Create: `install.bat`

- [ ] **Step 1: Crear `install.bat`**

```batch
@echo off
REM Instalador automatico - Editor de Video RevoCL (Windows)
setlocal

echo === Verificando Python ===
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado. Instala Python 3.11+ desde python.org
    exit /b 1
)

echo === Verificando FFmpeg ===
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ADVERTENCIA: FFmpeg no esta en PATH. Descarga desde https://ffmpeg.org y agregalo al PATH.
    echo La aplicacion no podra renderizar sin FFmpeg.
)

echo === Creando entorno virtual ===
if not exist venv (
    python -m venv venv
)

echo === Activando venv e instalando dependencias ===
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo === Instalacion completa ===
echo Para ejecutar el editor: venv\Scripts\activate ^&^& python -m src.main
endlocal
```

- [ ] **Step 2: Verificar sintaxis ejecutando con `--help` (no aplica para .bat, solo run)**

```bash
# En Windows, ejecutar:
install.bat
```

Expected: pasa por todas las verificaciones e instala. (Si ya está instalado, reinstala sin error.)

- [ ] **Step 3: Commit**

```bash
git add install.bat
git commit -m "feat: agregar install.bat para Windows"
```

---

## Task 4: Script de instalación macOS/Linux (`install.sh`)

**Files:**
- Create: `install.sh`

- [ ] **Step 1: Crear `install.sh`**

```bash
#!/usr/bin/env bash
# Instalador automatico - Editor de Video RevoCL (macOS/Linux)
set -e

echo "=== Verificando Python ==="
if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 no encontrado. Instala Python 3.11+."
    exit 1
fi

echo "=== Verificando FFmpeg ==="
if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "ADVERTENCIA: FFmpeg no encontrado. Instala con:"
    echo "  macOS:  brew install ffmpeg"
    echo "  Linux:  sudo apt install ffmpeg"
fi

echo "=== Creando entorno virtual ==="
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

echo "=== Instalando dependencias ==="
# shellcheck disable=SC1091
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=== Instalacion completa ==="
echo "Para ejecutar: source venv/bin/activate && python -m src.main"
```

- [ ] **Step 2: Hacer ejecutable**

```bash
chmod +x install.sh
```

- [ ] **Step 3: Commit**

```bash
git add install.sh
git commit -m "feat: agregar install.sh para macOS/Linux"
```

---

## Task 5: Ampliar `core/config.py` con paths completos y preferencias

**Files:**
- Modify: `src/core/config.py`

- [ ] **Step 1: Escribir test failing — verifica nuevas paths y preferencias por default**

Crear `tests/test_config.py`:

```python
"""Tests para core.config"""
import pytest
from pathlib import Path
from src.core.config import Config

def test_config_creates_required_dirs(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(Config, "TEMP_DIR", tmp_path / "temp")
    monkeypatch.setattr(Config, "PROJECTS_DIR", tmp_path / "projects")
    monkeypatch.setattr(Config, "ASSETS_DIR", tmp_path / "assets")
    cfg = Config()
    assert (tmp_path / "temp").exists()
    assert (tmp_path / "projects").exists()
    assert (tmp_path / "assets").exists()

def test_config_default_preferences():
    cfg = Config()
    assert cfg.preferences.get("theme") == "dark"
    assert cfg.preferences.get("default_fps") == 30
    assert cfg.preferences.get("default_resolution") == (1920, 1080)

def test_config_supported_formats():
    assert ".mp4" in Config.SUPPORTED_VIDEO
    assert ".mp3" in Config.SUPPORTED_AUDIO
    assert ".png" in Config.SUPPORTED_IMAGE
```

- [ ] **Step 2: Ejecutar test — debe fallar**

```bash
pytest tests/test_config.py -v
```

Expected: FAIL en `test_config_default_preferences` (preferences vacío) y `test_config_creates_required_dirs` (ASSETS_DIR no existe).

- [ ] **Step 3: Implementar — actualizar `src/core/config.py`**

```python
"""Configuracion global del editor"""
from pathlib import Path
from typing import Dict, Any, Tuple

class Config:
    """Configuracion de la aplicacion (singleton)"""

    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    TEMP_DIR = PROJECT_ROOT / "temp"
    PROJECTS_DIR = PROJECT_ROOT / "projects"
    ASSETS_DIR = PROJECT_ROOT / "assets"
    STYLES_DIR = ASSETS_DIR / "styles"

    SUPPORTED_VIDEO = (".mp4", ".mov", ".avi", ".mkv", ".webm")
    SUPPORTED_AUDIO = (".mp3", ".wav", ".aac", ".flac")
    SUPPORTED_IMAGE = (".png", ".jpg", ".jpeg", ".gif", ".bmp")

    DEFAULT_FPS = 30
    DEFAULT_RESOLUTION: Tuple[int, int] = (1920, 1080)
    DEFAULT_BITRATE = "8000k"

    def __init__(self):
        self._create_dirs()
        self.preferences: Dict[str, Any] = {
            "theme": "dark",
            "default_fps": self.DEFAULT_FPS,
            "default_resolution": self.DEFAULT_RESOLUTION,
            "default_bitrate": self.DEFAULT_BITRATE,
            "snap_enabled": True,
            "timeline_zoom": 1.0,
        }

    def _create_dirs(self) -> None:
        for d in (self.TEMP_DIR, self.PROJECTS_DIR, self.ASSETS_DIR, self.STYLES_DIR):
            d.mkdir(parents=True, exist_ok=True)

config = Config()
```

- [ ] **Step 4: Ejecutar tests — deben pasar**

```bash
pytest tests/test_config.py -v
```

Expected: 3 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/core/config.py tests/test_config.py
git commit -m "feat(core): ampliar Config con preferences y assets dir"
```

---

## Task 6: Ampliar `core/timeline.py` — métodos remove, move, get_clip_at, validar overlaps

**Files:**
- Modify: `src/core/timeline.py`
- Test: `tests/test_timeline.py`

- [ ] **Step 1: Escribir tests failing**

Crear `tests/test_timeline.py`:

```python
"""Tests para core.timeline"""
import pytest
from src.core.timeline import Clip, Track, Timeline, TrackType

def make_clip(cid="c1", start=0.0, duration=5.0, track_id="t1"):
    return Clip(id=cid, name=cid, source="/x.mp4", start=start, duration=duration, track_id=track_id)

def test_timeline_add_track():
    tl = Timeline()
    tl.add_track(Track(id="t1", name="Video 1", type=TrackType.VIDEO))
    assert len(tl.tracks) == 1
    assert tl.get_track("t1").name == "Video 1"

def test_timeline_add_clip_to_existing_track():
    tl = Timeline()
    tl.add_track(Track(id="t1", name="V1", type=TrackType.VIDEO))
    tl.add_clip("t1", make_clip())
    assert len(tl.get_track("t1").clips) == 1

def test_timeline_add_clip_to_missing_track_raises():
    tl = Timeline()
    with pytest.raises(ValueError, match="track_id"):
        tl.add_clip("nope", make_clip())

def test_timeline_remove_clip():
    tl = Timeline()
    tl.add_track(Track(id="t1", name="V1", type=TrackType.VIDEO))
    tl.add_clip("t1", make_clip(cid="c1"))
    tl.remove_clip("c1")
    assert len(tl.get_track("t1").clips) == 0

def test_timeline_move_clip():
    tl = Timeline()
    tl.add_track(Track(id="t1", name="V1", type=TrackType.VIDEO))
    tl.add_clip("t1", make_clip(cid="c1", start=0.0, duration=5.0))
    tl.move_clip("c1", new_start=10.0)
    assert tl.get_clip("c1").start == 10.0

def test_timeline_get_clip_at():
    tl = Timeline()
    tl.add_track(Track(id="t1", name="V1", type=TrackType.VIDEO))
    tl.add_clip("t1", make_clip(cid="c1", start=2.0, duration=3.0))
    assert tl.get_clip_at("t1", 3.5).id == "c1"
    assert tl.get_clip_at("t1", 10.0) is None

def test_timeline_clips_overlap_detected():
    tl = Timeline()
    tl.add_track(Track(id="t1", name="V1", type=TrackType.VIDEO))
    tl.add_clip("t1", make_clip(cid="c1", start=0.0, duration=5.0))
    with pytest.raises(ValueError, match="overlap"):
        tl.add_clip("t1", make_clip(cid="c2", start=3.0, duration=4.0))

def test_timeline_total_duration():
    tl = Timeline()
    tl.add_track(Track(id="t1", name="V1", type=TrackType.VIDEO))
    tl.add_clip("t1", make_clip(cid="c1", start=0.0, duration=5.0))
    tl.add_clip("t1", make_clip(cid="c2", start=10.0, duration=3.0))
    assert tl.total_duration() == 13.0
```

- [ ] **Step 2: Ejecutar tests — deben fallar**

```bash
pytest tests/test_timeline.py -v
```

Expected: múltiples FAIL (`get_track`, `remove_clip`, `move_clip`, `get_clip_at`, `total_duration` no existen).

- [ ] **Step 3: Implementar — sobrescribir `src/core/timeline.py`**

```python
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
```

- [ ] **Step 4: Ejecutar tests — deben pasar**

```bash
pytest tests/test_timeline.py -v
```

Expected: 8 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/core/timeline.py tests/test_timeline.py
git commit -m "feat(core): ampliar Timeline con remove/move/get_clip_at + overlap detection"
```

---

## Task 7: Implementar `core/video_processor.py` con metadata real (ffmpeg-python)

**Files:**
- Modify: `src/core/video_processor.py`
- Test: `tests/test_video_processor.py`

- [ ] **Step 1: Escribir test failing**

Crear `tests/test_video_processor.py`:

```python
"""Tests para core.video_processor"""
import subprocess
from pathlib import Path
import pytest
from src.core.video_processor import VideoProcessor, VideoSpec

@pytest.fixture
def sample_video(tmp_path):
    """Genera un mp4 de 2 segundos con FFmpeg para tests"""
    out = tmp_path / "sample.mp4"
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", "color=c=red:s=320x240:d=2:r=30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(out),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        pytest.skip(f"FFmpeg no disponible: {result.stderr[:200]}")
    return out

def test_get_video_info_real_file(tmp_path, sample_video):
    proc = VideoProcessor(temp_dir=tmp_path)
    info = proc.get_video_info(str(sample_video))
    assert info is not None
    assert info["width"] == 320
    assert info["height"] == 240
    assert info["fps"] == 30
    assert 1.9 <= info["duration"] <= 2.1

def test_get_video_info_missing_file(tmp_path):
    proc = VideoProcessor(temp_dir=tmp_path)
    assert proc.get_video_info("/nope/missing.mp4") is None

def test_video_spec_defaults():
    spec = VideoSpec(width=1920, height=1080, fps=30, bitrate="8000k")
    assert spec.codec == "libx264"
    assert spec.preset == "medium"
```

- [ ] **Step 2: Ejecutar test — debe fallar**

```bash
pytest tests/test_video_processor.py -v
```

Expected: `test_get_video_info_real_file` FAIL (devuelve stub con duration=0.0).

- [ ] **Step 3: Implementar — sobrescribir `src/core/video_processor.py`**

```python
"""Procesamiento y metadata de video via ffmpeg-python"""
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
import ffmpeg

@dataclass
class VideoSpec:
    width: int
    height: int
    fps: int
    bitrate: str
    codec: str = "libx264"
    preset: str = "medium"

class VideoProcessor:
    """Lectura de metadata y operaciones FFmpeg"""

    def __init__(self, temp_dir: Path):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def get_video_info(self, path: str) -> Optional[Dict[str, Any]]:
        """Devuelve dict con width, height, fps, duration. None si falla."""
        if not Path(path).exists():
            return None
        try:
            probe = ffmpeg.probe(path)
        except ffmpeg.Error:
            return None
        video_stream = next(
            (s for s in probe["streams"] if s["codec_type"] == "video"),
            None,
        )
        if video_stream is None:
            return None
        fps_str = video_stream.get("r_frame_rate", "30/1")
        num, den = fps_str.split("/")
        fps = int(round(float(num) / float(den))) if float(den) != 0 else 30
        return {
            "width": int(video_stream["width"]),
            "height": int(video_stream["height"]),
            "fps": fps,
            "duration": float(probe["format"].get("duration", 0.0)),
            "codec": video_stream.get("codec_name", "unknown"),
        }
```

- [ ] **Step 4: Ejecutar tests**

```bash
pytest tests/test_video_processor.py -v
```

Expected: 3 PASSED (asumiendo FFmpeg en PATH; sino el primero hace skip).

- [ ] **Step 5: Commit**

```bash
git add src/core/video_processor.py tests/test_video_processor.py
git commit -m "feat(core): VideoProcessor.get_video_info con ffmpeg.probe real"
```

---

## Task 8: Crear `core/project.py` — save/load proyecto en JSON

**Files:**
- Create: `src/core/project.py`
- Test: `tests/test_project.py`

- [ ] **Step 1: Escribir tests failing**

Crear `tests/test_project.py`:

```python
"""Tests para core.project"""
import json
from pathlib import Path
import pytest
from src.core.project import Project
from src.core.timeline import Timeline, Track, Clip, TrackType

def test_project_save_creates_json(tmp_path):
    tl = Timeline(fps=30)
    tl.add_track(Track(id="v1", name="Video 1", type=TrackType.VIDEO))
    tl.add_clip("v1", Clip(id="c1", name="clip1", source="/x.mp4",
                           start=0.0, duration=5.0, track_id="v1"))
    p = Project(name="MyProj", timeline=tl)
    out = tmp_path / "proj.json"
    p.save(out)
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["name"] == "MyProj"
    assert data["timeline"]["tracks"][0]["clips"][0]["id"] == "c1"

def test_project_load_roundtrip(tmp_path):
    tl = Timeline(fps=24, duration=120.0)
    tl.add_track(Track(id="a1", name="Audio", type=TrackType.AUDIO))
    tl.add_clip("a1", Clip(id="ac1", name="bg-music", source="/m.mp3",
                           start=2.0, duration=8.0, track_id="a1", volume=0.6))
    p = Project(name="Test", timeline=tl)
    out = tmp_path / "p.json"
    p.save(out)

    loaded = Project.load(out)
    assert loaded.name == "Test"
    assert loaded.timeline.fps == 24
    assert loaded.timeline.tracks[0].id == "a1"
    assert loaded.timeline.tracks[0].clips[0].volume == 0.6

def test_project_load_invalid_file_raises(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json{{")
    with pytest.raises(ValueError, match="JSON"):
        Project.load(bad)

def test_project_load_missing_version_raises(tmp_path):
    f = tmp_path / "f.json"
    f.write_text(json.dumps({"name": "x", "timeline": {}}))
    with pytest.raises(ValueError, match="version"):
        Project.load(f)
```

- [ ] **Step 2: Ejecutar tests — deben fallar**

```bash
pytest tests/test_project.py -v
```

Expected: ImportError o FAIL (`Project` no existe).

- [ ] **Step 3: Implementar `src/core/project.py`**

```python
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
```

- [ ] **Step 4: Ejecutar tests — deben pasar**

```bash
pytest tests/test_project.py -v
```

Expected: 4 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/core/project.py tests/test_project.py
git commit -m "feat(core): Project con save/load JSON versionado"
```

---

## Task 9: Crear `core/commands.py` — Command pattern para undo/redo

**Files:**
- Create: `src/core/commands.py`
- Test: `tests/test_commands.py`

- [ ] **Step 1: Escribir tests failing**

Crear `tests/test_commands.py`:

```python
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
```

- [ ] **Step 2: Ejecutar tests — deben fallar**

```bash
pytest tests/test_commands.py -v
```

Expected: ImportError (`commands` no existe).

- [ ] **Step 3: Implementar `src/core/commands.py`**

```python
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
```

- [ ] **Step 4: Ejecutar tests — deben pasar**

```bash
pytest tests/test_commands.py -v
```

Expected: 6 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/core/commands.py tests/test_commands.py
git commit -m "feat(core): Command pattern (Add/Remove/Move) + CommandStack undo/redo"
```

---

## Task 10: Crear stylesheet `assets/styles/dark_theme.qss`

**Files:**
- Create: `assets/styles/dark_theme.qss`

- [ ] **Step 1: Crear archivo QSS**

```css
/* Dark theme profesional - Editor de Video RevoCL */

QMainWindow, QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

QMenuBar {
    background-color: #252526;
    color: #e0e0e0;
    border-bottom: 1px solid #3a3a3a;
}
QMenuBar::item:selected {
    background-color: #3a3a3a;
}

QMenu {
    background-color: #252526;
    color: #e0e0e0;
    border: 1px solid #3a3a3a;
}
QMenu::item:selected {
    background-color: #094771;
}

QToolBar {
    background-color: #252526;
    border: none;
    spacing: 4px;
    padding: 4px;
}

QPushButton {
    background-color: #2d2d30;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    padding: 6px 12px;
    color: #e0e0e0;
}
QPushButton:hover {
    background-color: #3a3a3a;
}
QPushButton:pressed {
    background-color: #094771;
}
QPushButton:disabled {
    color: #666;
    background-color: #252526;
}

QSplitter::handle {
    background-color: #3a3a3a;
}

QDockWidget {
    color: #e0e0e0;
    titlebar-close-icon: url(none);
}
QDockWidget::title {
    background-color: #252526;
    padding: 4px;
}

QScrollBar:vertical, QScrollBar:horizontal {
    background: #252526;
    width: 10px;
    height: 10px;
}
QScrollBar::handle {
    background: #4a4a4a;
    border-radius: 4px;
}
QScrollBar::handle:hover {
    background: #5a5a5a;
}

QGraphicsView {
    background-color: #181818;
    border: 1px solid #3a3a3a;
}

QListWidget, QTreeWidget {
    background-color: #1e1e1e;
    border: 1px solid #3a3a3a;
    color: #e0e0e0;
}
QListWidget::item:selected, QTreeWidget::item:selected {
    background-color: #094771;
}

QLabel {
    color: #e0e0e0;
}

QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #2d2d30;
    border: 1px solid #3a3a3a;
    border-radius: 3px;
    padding: 4px;
    color: #e0e0e0;
}

QStatusBar {
    background-color: #007acc;
    color: white;
}
```

- [ ] **Step 2: Verificar archivo creado**

```bash
ls -la assets/styles/
```

Expected: `dark_theme.qss` presente.

- [ ] **Step 3: Commit**

```bash
git add assets/styles/dark_theme.qss
git commit -m "feat(ui): stylesheet dark mode profesional"
```

---

## Task 11: Crear `ui/preview_widget.py` — reproductor de video básico

**Files:**
- Create: `src/ui/preview_widget.py`

- [ ] **Step 1: Implementar widget**

```python
"""Reproductor de preview de video con controles play/pause y tiempo."""
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel
)


class PreviewWidget(QWidget):
    """Preview con play/pause, slider de tiempo, label de duracion."""

    timeChanged = pyqtSignal(float)  # segundos

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(240)
        layout.addWidget(self.video_widget, stretch=1)

        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.video_widget)

        controls = QHBoxLayout()
        self.btn_play = QPushButton("▶")
        self.btn_play.setFixedWidth(40)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        self.lbl_time = QLabel("00:00 / 00:00")
        self.lbl_time.setMinimumWidth(110)

        controls.addWidget(self.btn_play)
        controls.addWidget(self.slider, stretch=1)
        controls.addWidget(self.lbl_time)
        layout.addLayout(controls)

    def _connect_signals(self) -> None:
        self.btn_play.clicked.connect(self.toggle_play)
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.slider.sliderMoved.connect(self.player.setPosition)

    def load_video(self, path: str) -> None:
        self.player.setSource(QUrl.fromLocalFile(path))

    def toggle_play(self) -> None:
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.btn_play.setText("▶")
        else:
            self.player.play()
            self.btn_play.setText("⏸")

    def _on_position_changed(self, pos_ms: int) -> None:
        self.slider.setValue(pos_ms)
        self._update_time_label(pos_ms, self.player.duration())
        self.timeChanged.emit(pos_ms / 1000.0)

    def _on_duration_changed(self, dur_ms: int) -> None:
        self.slider.setRange(0, dur_ms)
        self._update_time_label(self.player.position(), dur_ms)

    @staticmethod
    def _fmt(ms: int) -> str:
        s = ms // 1000
        return f"{s // 60:02d}:{s % 60:02d}"

    def _update_time_label(self, pos: int, dur: int) -> None:
        self.lbl_time.setText(f"{self._fmt(pos)} / {self._fmt(dur)}")
```

- [ ] **Step 2: Smoke test — verifica que se instancia sin errores**

Crear `tests/test_preview_widget.py`:

```python
"""Smoke test PreviewWidget"""
import pytest
from PyQt6.QtWidgets import QApplication

@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])

def test_preview_widget_instantiates(app, qtbot):
    from src.ui.preview_widget import PreviewWidget
    w = PreviewWidget()
    qtbot.addWidget(w)
    assert w.btn_play.text() == "▶"
    assert w.slider.value() == 0
```

- [ ] **Step 3: Ejecutar test**

```bash
pytest tests/test_preview_widget.py -v
```

Expected: PASSED.

- [ ] **Step 4: Commit**

```bash
git add src/ui/preview_widget.py tests/test_preview_widget.py
git commit -m "feat(ui): PreviewWidget con QMediaPlayer + controles play/pause/slider"
```

---

## Task 12: Crear `ui/tools_panel.py` — sidebar izquierdo con botones

**Files:**
- Create: `src/ui/tools_panel.py`

- [ ] **Step 1: Implementar widget**

```python
"""Panel lateral izquierdo con herramientas principales."""
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel


class ToolsPanel(QWidget):
    """Sidebar izquierdo: import, cut, text, effects, audio."""

    importRequested = pyqtSignal()
    cutRequested = pyqtSignal()
    textRequested = pyqtSignal()
    effectsRequested = pyqtSignal()
    audioRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        layout.addWidget(QLabel("HERRAMIENTAS"))

        buttons = [
            ("📁  Importar", self.importRequested),
            ("✂️  Cortar", self.cutRequested),
            ("T   Texto", self.textRequested),
            ("✨  Efectos", self.effectsRequested),
            ("🎵  Audio", self.audioRequested),
        ]
        for label, signal in buttons:
            btn = QPushButton(label)
            btn.setMinimumHeight(32)
            btn.clicked.connect(signal.emit)
            layout.addWidget(btn)

        layout.addStretch(1)
        self.setMinimumWidth(180)
        self.setMaximumWidth(220)
```

- [ ] **Step 2: Smoke test**

Crear `tests/test_tools_panel.py`:

```python
"""Smoke test ToolsPanel"""
import pytest
from PyQt6.QtWidgets import QApplication

@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])

def test_tools_panel_emits_import(app, qtbot):
    from src.ui.tools_panel import ToolsPanel
    panel = ToolsPanel()
    qtbot.addWidget(panel)
    with qtbot.waitSignal(panel.importRequested, timeout=500):
        # primer botón es Importar
        panel.findChildren(type(panel.findChild(__import__("PyQt6.QtWidgets", fromlist=["QPushButton"]).QPushButton)))[0].click()
```

- [ ] **Step 3: Simplificar el test (versión más limpia)**

Sobrescribir `tests/test_tools_panel.py`:

```python
"""Smoke test ToolsPanel"""
import pytest
from PyQt6.QtWidgets import QApplication, QPushButton

@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])

def test_tools_panel_has_5_buttons(app, qtbot):
    from src.ui.tools_panel import ToolsPanel
    panel = ToolsPanel()
    qtbot.addWidget(panel)
    buttons = panel.findChildren(QPushButton)
    assert len(buttons) == 5

def test_tools_panel_import_signal(app, qtbot):
    from src.ui.tools_panel import ToolsPanel
    panel = ToolsPanel()
    qtbot.addWidget(panel)
    buttons = panel.findChildren(QPushButton)
    with qtbot.waitSignal(panel.importRequested, timeout=500):
        buttons[0].click()
```

- [ ] **Step 4: Ejecutar test**

```bash
pytest tests/test_tools_panel.py -v
```

Expected: 2 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/ui/tools_panel.py tests/test_tools_panel.py
git commit -m "feat(ui): ToolsPanel con 5 acciones (import/cut/text/effects/audio)"
```

---

## Task 13: Crear `ui/properties_panel.py` — sidebar derecho

**Files:**
- Create: `src/ui/properties_panel.py`

- [ ] **Step 1: Implementar widget**

```python
"""Panel lateral derecho: propiedades del clip seleccionado."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QDoubleSpinBox, QGroupBox
)
from src.core.timeline import Clip


class PropertiesPanel(QWidget):
    """Muestra y permite editar propiedades del clip seleccionado."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_clip: Clip | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(QLabel("PROPIEDADES"))

        self.group = QGroupBox("Clip")
        form = QFormLayout(self.group)

        self.name_edit = QLineEdit()
        self.name_edit.setReadOnly(True)
        form.addRow("Nombre:", self.name_edit)

        self.start_spin = QDoubleSpinBox()
        self.start_spin.setRange(0.0, 99999.0)
        self.start_spin.setSuffix(" s")
        form.addRow("Inicio:", self.start_spin)

        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.01, 99999.0)
        self.duration_spin.setSuffix(" s")
        form.addRow("Duracion:", self.duration_spin)

        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(0.0, 2.0)
        self.volume_spin.setSingleStep(0.1)
        form.addRow("Volumen:", self.volume_spin)

        self.opacity_spin = QDoubleSpinBox()
        self.opacity_spin.setRange(0.0, 1.0)
        self.opacity_spin.setSingleStep(0.05)
        form.addRow("Opacidad:", self.opacity_spin)

        layout.addWidget(self.group)
        layout.addStretch(1)

        self.setMinimumWidth(220)
        self.setMaximumWidth(280)
        self.set_clip(None)

    def set_clip(self, clip: Clip | None) -> None:
        self._current_clip = clip
        enabled = clip is not None
        self.group.setEnabled(enabled)
        if clip:
            self.name_edit.setText(clip.name)
            self.start_spin.setValue(clip.start)
            self.duration_spin.setValue(clip.duration)
            self.volume_spin.setValue(clip.volume)
            self.opacity_spin.setValue(clip.opacity)
        else:
            self.name_edit.setText("")
            self.start_spin.setValue(0.0)
            self.duration_spin.setValue(0.0)
            self.volume_spin.setValue(1.0)
            self.opacity_spin.setValue(1.0)
```

- [ ] **Step 2: Smoke test**

Crear `tests/test_properties_panel.py`:

```python
"""Smoke test PropertiesPanel"""
import pytest
from PyQt6.QtWidgets import QApplication
from src.core.timeline import Clip

@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])

def test_properties_panel_disabled_when_no_clip(app, qtbot):
    from src.ui.properties_panel import PropertiesPanel
    p = PropertiesPanel()
    qtbot.addWidget(p)
    assert not p.group.isEnabled()

def test_properties_panel_populates_from_clip(app, qtbot):
    from src.ui.properties_panel import PropertiesPanel
    p = PropertiesPanel()
    qtbot.addWidget(p)
    clip = Clip(id="c1", name="MyClip", source="/x.mp4",
                start=2.5, duration=10.0, track_id="v1",
                volume=0.8, opacity=0.5)
    p.set_clip(clip)
    assert p.name_edit.text() == "MyClip"
    assert p.start_spin.value() == 2.5
    assert p.duration_spin.value() == 10.0
    assert p.volume_spin.value() == 0.8
    assert p.opacity_spin.value() == 0.5
    assert p.group.isEnabled()
```

- [ ] **Step 3: Ejecutar test**

```bash
pytest tests/test_properties_panel.py -v
```

Expected: 2 PASSED.

- [ ] **Step 4: Commit**

```bash
git add src/ui/properties_panel.py tests/test_properties_panel.py
git commit -m "feat(ui): PropertiesPanel con campos de clip seleccionado"
```

---

## Task 14: Crear `ui/timeline_widget.py` — QGraphicsView de tracks y clips

**Files:**
- Create: `src/ui/timeline_widget.py`

- [ ] **Step 1: Implementar widget**

```python
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
    """Renderiza el Timeline con zoom (mouse wheel + Ctrl) y selección de clips."""

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
```

- [ ] **Step 2: Smoke test**

Crear `tests/test_timeline_widget.py`:

```python
"""Smoke test TimelineWidget"""
import pytest
from PyQt6.QtWidgets import QApplication
from src.core.timeline import Timeline, Track, Clip, TrackType

@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])

def test_timeline_widget_renders_tracks_and_clips(app, qtbot):
    from src.ui.timeline_widget import TimelineWidget
    tl = Timeline()
    tl.add_track(Track(id="v1", name="Video", type=TrackType.VIDEO))
    tl.add_track(Track(id="a1", name="Audio", type=TrackType.AUDIO))
    tl.add_clip("v1", Clip(id="c1", name="clip1", source="/x.mp4",
                           start=0.0, duration=5.0, track_id="v1"))
    w = TimelineWidget(tl)
    qtbot.addWidget(w)
    assert "c1" in w._clip_items
    assert w._playhead_item is not None

def test_timeline_widget_zoom_via_refresh(app, qtbot):
    from src.ui.timeline_widget import TimelineWidget
    tl = Timeline()
    tl.add_track(Track(id="v1", name="Video", type=TrackType.VIDEO))
    tl.add_clip("v1", Clip(id="c1", name="x", source="/x.mp4",
                           start=0.0, duration=2.0, track_id="v1"))
    w = TimelineWidget(tl)
    qtbot.addWidget(w)
    initial_x = w._clip_items["c1"].rect().width()
    w.zoom = 2.0
    w.refresh()
    new_x = w._clip_items["c1"].rect().width()
    assert new_x > initial_x

def test_timeline_widget_set_playhead(app, qtbot):
    from src.ui.timeline_widget import TimelineWidget
    tl = Timeline()
    tl.add_track(Track(id="v1", name="V", type=TrackType.VIDEO))
    w = TimelineWidget(tl)
    qtbot.addWidget(w)
    w.set_playhead(7.5)
    assert tl.playhead == 7.5
```

- [ ] **Step 3: Ejecutar test**

```bash
pytest tests/test_timeline_widget.py -v
```

Expected: 3 PASSED.

- [ ] **Step 4: Commit**

```bash
git add src/ui/timeline_widget.py tests/test_timeline_widget.py
git commit -m "feat(ui): TimelineWidget (QGraphicsView) con tracks/clips/playhead/zoom"
```

---

## Task 15: Crear `ui/main_window.py` — ventana principal con layout completo

**Files:**
- Create: `src/ui/main_window.py`

- [ ] **Step 1: Implementar `MainWindow`**

```python
"""Ventana principal del editor."""
from __future__ import annotations
import uuid
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QFileDialog, QMessageBox, QWidget, QVBoxLayout
)

from src.core.config import config
from src.core.timeline import Timeline, Track, TrackType, Clip
from src.core.video_processor import VideoProcessor
from src.core.project import Project
from src.core.commands import (
    CommandStack, AddClipCommand, RemoveClipCommand, MoveClipCommand
)
from src.ui.preview_widget import PreviewWidget
from src.ui.tools_panel import ToolsPanel
from src.ui.properties_panel import PropertiesPanel
from src.ui.timeline_widget import TimelineWidget


class MainWindow(QMainWindow):
    """Ventana principal: menubar + splitters (tools | preview/timeline | props)."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor de Video - RevoCL")
        self.resize(1280, 800)

        self.project = self._new_project()
        self.processor = VideoProcessor(temp_dir=config.TEMP_DIR)
        self.cmd_stack = CommandStack()

        self._build_ui()
        self._build_menus()
        self._wire_signals()
        self.setAcceptDrops(True)
        self._load_stylesheet()

    def _new_project(self) -> Project:
        tl = Timeline(fps=config.DEFAULT_FPS)
        tl.add_track(Track(id="v1", name="Video 1", type=TrackType.VIDEO))
        tl.add_track(Track(id="v2", name="Video 2", type=TrackType.VIDEO))
        tl.add_track(Track(id="a1", name="Audio 1", type=TrackType.AUDIO))
        tl.add_track(Track(id="a2", name="Audio 2", type=TrackType.AUDIO))
        tl.add_track(Track(id="sub", name="Subtitulos", type=TrackType.SUBTITLE))
        return Project(name="Untitled", timeline=tl)

    def _build_ui(self) -> None:
        # Splitter horizontal: tools | center | properties
        h_split = QSplitter(Qt.Orientation.Horizontal)

        self.tools_panel = ToolsPanel()
        h_split.addWidget(self.tools_panel)

        # Center: preview arriba, timeline abajo
        v_split = QSplitter(Qt.Orientation.Vertical)
        self.preview = PreviewWidget()
        v_split.addWidget(self.preview)

        self.timeline_widget = TimelineWidget(self.project.timeline)
        v_split.addWidget(self.timeline_widget)
        v_split.setStretchFactor(0, 3)
        v_split.setStretchFactor(1, 2)

        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.addWidget(v_split)
        h_split.addWidget(center_container)

        self.properties_panel = PropertiesPanel()
        h_split.addWidget(self.properties_panel)

        h_split.setStretchFactor(0, 0)
        h_split.setStretchFactor(1, 1)
        h_split.setStretchFactor(2, 0)
        h_split.setSizes([180, 880, 220])

        self.setCentralWidget(h_split)
        self.statusBar().showMessage("Listo")

    def _build_menus(self) -> None:
        mb = self.menuBar()

        m_file = mb.addMenu("&Archivo")
        act_new = QAction("Nuevo proyecto", self, shortcut=QKeySequence.StandardKey.New)
        act_new.triggered.connect(self.action_new_project)
        m_file.addAction(act_new)

        act_open = QAction("Abrir proyecto...", self, shortcut=QKeySequence.StandardKey.Open)
        act_open.triggered.connect(self.action_open_project)
        m_file.addAction(act_open)

        act_save = QAction("Guardar proyecto", self, shortcut=QKeySequence.StandardKey.Save)
        act_save.triggered.connect(self.action_save_project)
        m_file.addAction(act_save)

        m_file.addSeparator()

        act_import = QAction("Importar video...", self, shortcut="Ctrl+I")
        act_import.triggered.connect(self.action_import_video)
        m_file.addAction(act_import)

        m_file.addSeparator()
        act_quit = QAction("Salir", self, shortcut=QKeySequence.StandardKey.Quit)
        act_quit.triggered.connect(self.close)
        m_file.addAction(act_quit)

        m_edit = mb.addMenu("&Editar")
        self.act_undo = QAction("Deshacer", self, shortcut=QKeySequence.StandardKey.Undo)
        self.act_undo.triggered.connect(self.action_undo)
        m_edit.addAction(self.act_undo)

        self.act_redo = QAction("Rehacer", self, shortcut=QKeySequence.StandardKey.Redo)
        self.act_redo.triggered.connect(self.action_redo)
        m_edit.addAction(self.act_redo)

        m_edit.addSeparator()
        self.act_delete = QAction("Eliminar clip", self, shortcut="Delete")
        self.act_delete.triggered.connect(self.action_delete_clip)
        m_edit.addAction(self.act_delete)

        m_play = mb.addMenu("&Reproduccion")
        act_play = QAction("Play / Pause", self, shortcut="Space")
        act_play.triggered.connect(self.preview.toggle_play)
        m_play.addAction(act_play)

    def _wire_signals(self) -> None:
        self.tools_panel.importRequested.connect(self.action_import_video)
        self.timeline_widget.clipSelected.connect(self._on_clip_selected)
        self.preview.timeChanged.connect(self.timeline_widget.set_playhead)

    def _load_stylesheet(self) -> None:
        qss_path = config.STYLES_DIR / "dark_theme.qss"
        if qss_path.exists():
            self.setStyleSheet(qss_path.read_text())

    # ---------- ACTIONS ----------

    def action_new_project(self) -> None:
        self.project = self._new_project()
        self.cmd_stack = CommandStack()
        self.timeline_widget.timeline = self.project.timeline
        self.timeline_widget.refresh()
        self.properties_panel.set_clip(None)
        self.setWindowTitle("Editor de Video - RevoCL [Untitled]")

    def action_open_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Abrir proyecto", str(config.PROJECTS_DIR), "Proyecto (*.json)"
        )
        if not path:
            return
        try:
            self.project = Project.load(Path(path))
        except (ValueError, OSError) as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir: {e}")
            return
        self.cmd_stack = CommandStack()
        self.timeline_widget.timeline = self.project.timeline
        self.timeline_widget.refresh()
        self.setWindowTitle(f"Editor de Video - RevoCL [{self.project.name}]")
        self.statusBar().showMessage(f"Proyecto cargado: {path}", 3000)

    def action_save_project(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar proyecto", str(config.PROJECTS_DIR / f"{self.project.name}.json"),
            "Proyecto (*.json)"
        )
        if not path:
            return
        try:
            self.project.save(Path(path))
            self.statusBar().showMessage(f"Guardado en {path}", 3000)
        except OSError as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")

    def action_import_video(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Importar video", "",
            "Video/Audio (*.mp4 *.mov *.avi *.mkv *.webm *.mp3 *.wav)"
        )
        if path:
            self.import_media(path)

    def import_media(self, path: str) -> None:
        ext = Path(path).suffix.lower()
        if ext in config.SUPPORTED_VIDEO:
            track_id = "v1"
        elif ext in config.SUPPORTED_AUDIO:
            track_id = "a1"
        else:
            QMessageBox.warning(self, "No soportado", f"Formato no soportado: {ext}")
            return

        info = self.processor.get_video_info(path) or {"duration": 5.0}
        duration = info.get("duration") or 5.0

        track = self.project.timeline.get_track(track_id)
        last_end = max((c.end for c in track.clips), default=0.0)

        clip = Clip(
            id=uuid.uuid4().hex[:8],
            name=Path(path).stem,
            source=path,
            start=last_end,
            duration=duration,
            track_id=track_id,
        )
        self.cmd_stack.push(AddClipCommand(self.project.timeline, track_id, clip))
        self.timeline_widget.refresh()
        if ext in config.SUPPORTED_VIDEO:
            self.preview.load_video(path)
        self.statusBar().showMessage(f"Importado: {clip.name}", 3000)

    def action_undo(self) -> None:
        if self.cmd_stack.undo():
            self.timeline_widget.refresh()
            self.statusBar().showMessage("Deshacer", 1500)

    def action_redo(self) -> None:
        if self.cmd_stack.redo():
            self.timeline_widget.refresh()
            self.statusBar().showMessage("Rehacer", 1500)

    def action_delete_clip(self) -> None:
        clip = self.properties_panel._current_clip
        if clip is None:
            return
        self.cmd_stack.push(RemoveClipCommand(self.project.timeline, clip.id))
        self.timeline_widget.refresh()
        self.properties_panel.set_clip(None)

    def _on_clip_selected(self, clip_id: str) -> None:
        clip = self.project.timeline.get_clip(clip_id)
        self.properties_panel.set_clip(clip)
        if clip and Path(clip.source).suffix.lower() in config.SUPPORTED_VIDEO:
            self.preview.load_video(clip.source)

    # ---------- DRAG & DROP ----------

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        for url in event.mimeData().urls():
            local = url.toLocalFile()
            if local:
                self.import_media(local)
        event.acceptProposedAction()
```

- [ ] **Step 2: Smoke test ventana principal**

Crear `tests/test_main_window.py`:

```python
"""Smoke test MainWindow"""
import pytest
from PyQt6.QtWidgets import QApplication

@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])

def test_main_window_instantiates(app, qtbot):
    from src.ui.main_window import MainWindow
    w = MainWindow()
    qtbot.addWidget(w)
    assert w.windowTitle().startswith("Editor de Video")
    assert len(w.project.timeline.tracks) == 5

def test_main_window_has_panels(app, qtbot):
    from src.ui.main_window import MainWindow
    from src.ui.preview_widget import PreviewWidget
    from src.ui.tools_panel import ToolsPanel
    from src.ui.properties_panel import PropertiesPanel
    from src.ui.timeline_widget import TimelineWidget
    w = MainWindow()
    qtbot.addWidget(w)
    assert isinstance(w.preview, PreviewWidget)
    assert isinstance(w.tools_panel, ToolsPanel)
    assert isinstance(w.properties_panel, PropertiesPanel)
    assert isinstance(w.timeline_widget, TimelineWidget)

def test_main_window_undo_redo_with_dummy_clip(app, qtbot):
    from src.ui.main_window import MainWindow
    from src.core.commands import AddClipCommand
    from src.core.timeline import Clip
    w = MainWindow()
    qtbot.addWidget(w)
    clip = Clip(id="test1", name="t", source="/x.mp4",
                start=0.0, duration=3.0, track_id="v1")
    w.cmd_stack.push(AddClipCommand(w.project.timeline, "v1", clip))
    assert w.project.timeline.get_clip("test1") is not None
    w.action_undo()
    assert w.project.timeline.get_clip("test1") is None
    w.action_redo()
    assert w.project.timeline.get_clip("test1") is not None
```

- [ ] **Step 3: Ejecutar tests**

```bash
pytest tests/test_main_window.py -v
```

Expected: 3 PASSED.

- [ ] **Step 4: Commit**

```bash
git add src/ui/main_window.py tests/test_main_window.py
git commit -m "feat(ui): MainWindow con menubar/panels/drag&drop/import/save/load"
```

---

## Task 16: Crear `src/main.py` — entry point ejecutable

**Files:**
- Create: `src/main.py`

- [ ] **Step 1: Implementar entry point**

```python
"""Editor de Video RevoCL - Entry point"""
import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Editor de Video RevoCL")
    app.setOrganizationName("RevoCL")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Ejecutar manualmente — debe abrir la ventana**

```bash
# Activar venv primero
python -m src.main
```

Expected: ventana se abre con dark mode, 5 tracks visibles, panel izquierdo con 5 botones, panel derecho con propiedades deshabilitadas, área central con preview vacío y timeline.

- [ ] **Step 3: Probar drag & drop manual** — arrastrar un .mp4 desde el explorador a la ventana.

Expected: aparece un clip en el track "Video 1", se ve en el timeline, el preview lo carga.

- [ ] **Step 4: Probar atajos de teclado**:
  - Espacio (con foco en preview) → play/pause
  - Ctrl+Z → deshacer (clip desaparece del timeline)
  - Ctrl+Y o Ctrl+Shift+Z → rehacer
  - Ctrl+I → abre dialogo importar
  - Ctrl+S → abre dialogo guardar
  - Ctrl+O → abre dialogo abrir

Expected: todos funcionan.

- [ ] **Step 5: Probar save/load roundtrip**:
  1. Importar 1-2 videos
  2. Ctrl+S → guardar como `projects/test.json`
  3. Ctrl+N → nuevo proyecto (timeline vacío)
  4. Ctrl+O → abrir `projects/test.json`
  5. Verificar que los clips reaparecen en sus posiciones

- [ ] **Step 6: Commit**

```bash
git add src/main.py
git commit -m "feat: entry point src/main.py — app ejecutable"
```

---

## Task 17: Configurar pytest y verificar suite completa

**Files:**
- Create: `pytest.ini`

- [ ] **Step 1: Crear `pytest.ini`**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -ra -v --tb=short
qt_api = pyqt6
```

- [ ] **Step 2: Ejecutar suite completa**

```bash
pytest
```

Expected: todos los tests PASSED. Algo como:
```
tests/test_commands.py        6 PASSED
tests/test_config.py          3 PASSED
tests/test_main_window.py     3 PASSED
tests/test_preview_widget.py  1 PASSED
tests/test_project.py         4 PASSED
tests/test_properties_panel.py 2 PASSED
tests/test_timeline.py        8 PASSED
tests/test_timeline_widget.py 3 PASSED
tests/test_tools_panel.py     2 PASSED
tests/test_video_processor.py 3 PASSED (o SKIP si no hay ffmpeg)
```

Total ~35 PASSED.

- [ ] **Step 3: Verificar con coverage**

```bash
pytest --cov=src --cov-report=term-missing
```

Expected: cobertura > 70% en `src/core/`.

- [ ] **Step 4: Commit**

```bash
git add pytest.ini
git commit -m "chore: pytest.ini configurado para PyQt6"
```

---

## Task 18: Actualizar `tools/validate.py` para validar la nueva estructura

**Files:**
- Modify: `tools/validate.py` (verificar contenido actual primero, luego ampliar)

- [ ] **Step 1: Leer contenido actual de `tools/validate.py`**

```bash
cat tools/validate.py
```

- [ ] **Step 2: Ampliar para validar nuevos paths**

Sobrescribir `tools/validate.py`:

```python
"""Validacion de integridad del proyecto"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

REQUIRED_DIRS = [
    "src/core",
    "src/ui",
    "src/ai",
    "src/effects",
    "tests",
    "assets/styles",
    "projects",
]

REQUIRED_FILES = [
    "src/__init__.py",
    "src/main.py",
    "src/core/__init__.py",
    "src/core/config.py",
    "src/core/timeline.py",
    "src/core/video_processor.py",
    "src/core/project.py",
    "src/core/commands.py",
    "src/ui/__init__.py",
    "src/ui/main_window.py",
    "src/ui/timeline_widget.py",
    "src/ui/preview_widget.py",
    "src/ui/tools_panel.py",
    "src/ui/properties_panel.py",
    "assets/styles/dark_theme.qss",
    "requirements.txt",
    "install.bat",
    "install.sh",
    "pytest.ini",
]


def main() -> int:
    errors = []
    for d in REQUIRED_DIRS:
        if not (ROOT / d).is_dir():
            errors.append(f"FALTA dir:  {d}")
    for f in REQUIRED_FILES:
        if not (ROOT / f).is_file():
            errors.append(f"FALTA file: {f}")

    if errors:
        print("VALIDACION FALLO:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("VALIDACION OK: estructura de Fase 1 completa.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Ejecutar validación**

```bash
python tools/validate.py
```

Expected: `VALIDACION OK: estructura de Fase 1 completa.`

- [ ] **Step 4: Commit**

```bash
git add tools/validate.py
git commit -m "chore(tools): validate.py actualizado con estructura Fase 1"
```

---

## Task 19: Sincronizar grafo Graphify

**Files:**
- Modify: `graphify-out/` (regenerado)

- [ ] **Step 1: Actualizar grafo**

```bash
python graphify.py update .
```

Expected: regenera `graphify-out/graph.json` y `GRAPH_REPORT.md` con la nueva estructura.

- [ ] **Step 2: Consultar grafo para verificar nuevos nodos**

```bash
python graphify.py query "main_window" --graph graphify-out/graph.json --budget 400
```

Expected: devuelve contexto sobre `MainWindow`, sus métodos y dependencias.

- [ ] **Step 3: Commit**

```bash
git add graphify-out/ GRAPH_REPORT.md
git commit -m "chore: actualizar grafo Graphify post-Fase 1"
```

---

## Task 20: Smoke test end-to-end manual final

**Files:** (ninguno — solo verificación)

- [ ] **Step 1: Limpiar y reinstalar desde cero**

```bash
rm -rf venv
./install.sh    # o install.bat en Windows
```

Expected: instalación limpia sin errores.

- [ ] **Step 2: Lanzar app**

```bash
source venv/bin/activate    # o venv\Scripts\activate
python -m src.main
```

Expected: ventana abre en < 3 segundos con dark mode aplicado.

- [ ] **Step 3: Checklist manual de funcionalidad Fase 1**

Verificar cada uno:
- [ ] Ventana abre en dark mode
- [ ] 5 tracks visibles en timeline (V1, V2, A1, A2, Subtítulos)
- [ ] Panel izquierdo muestra 5 botones (Importar, Cortar, Texto, Efectos, Audio)
- [ ] Panel derecho muestra propiedades deshabilitadas (sin clip seleccionado)
- [ ] Drag & drop de un .mp4 → aparece clip en V1, video se carga en preview
- [ ] Click en preview ▶ → reproduce video con audio
- [ ] Click en clip del timeline → se selecciona (rectángulo destacado), propiedades se llenan
- [ ] Espacio → play/pause en preview
- [ ] Ctrl+Z → último clip importado desaparece
- [ ] Ctrl+Y → reaparece
- [ ] Delete con clip seleccionado → clip desaparece (vía CommandStack)
- [ ] Ctrl+S → guardar como `projects/test.json` funciona
- [ ] Ctrl+N → nuevo proyecto, timeline vacío
- [ ] Ctrl+O → cargar `projects/test.json` restaura los clips
- [ ] Ctrl+rueda en timeline → zoom in/out (clips se hacen más anchos/angostos)
- [ ] Click en zona vacía del timeline → mueve playhead (línea roja)
- [ ] Ctrl+I → abre diálogo importar archivo

Si todos los checks pasan → Fase 1 COMPLETA.

- [ ] **Step 4: Tag final**

```bash
git tag fase1-completa
git log --oneline | head -25
```

---

## Resumen Fase 1

Al completar las 20 tasks, el editor:

✅ Es ejecutable (`python -m src.main`)
✅ Tiene UI dark mode completa con menubar, 3 paneles y timeline
✅ Importa videos (drag & drop o Ctrl+I) → se ven en timeline y preview
✅ Reproduce videos con QMediaPlayer
✅ Muestra propiedades del clip seleccionado
✅ Soporta undo/redo (Command pattern)
✅ Guarda/carga proyectos en JSON versionado
✅ Tiene timeline con tracks múltiples, clips, playhead, zoom (Ctrl+rueda)
✅ Atajos de teclado funcionando (Space, Ctrl+Z/Y/S/O/N/I, Delete)
✅ ~35 tests pasando, > 70% coverage en `core/`
✅ Scripts de instalación para Windows y macOS/Linux
✅ Validate.py confirma estructura

**No incluye (planes posteriores):**
- Render/export FFmpeg → Fase 2
- Cortar clips dentro del timeline → Fase 2
- Subtítulos Whisper → Fase 3
- Texto/animaciones → Fase 4
- Transiciones, efectos, color grading → Fase 4-5
- Upscaling, bg removal → Fase 6-7
- Audio profesional → Fase 8
- Copiar Efecto (Claude Vision) → Fase 9
- Plantillas, batch export → Fase 10
