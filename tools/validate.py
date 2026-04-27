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
