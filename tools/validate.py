#!/usr/bin/env python3
"""Tool: Validar estructura y estado del código"""
import sys
from pathlib import Path

def validate_project():
    """Validar integridad del proyecto"""
    required = ["src/config.py", "src/timeline.py", "src/video_processor.py", "GRAPH_REPORT.md"]
    root = Path(__file__).parent.parent

    missing = [f for f in required if not (root / f).exists()]
    if missing:
        print(f"[FAIL] Archivos faltantes: {missing}")
        return False

    print("[OK] Estructura validada")
    return True

if __name__ == "__main__":
    sys.exit(0 if validate_project() else 1)
