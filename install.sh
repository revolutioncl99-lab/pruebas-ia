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
