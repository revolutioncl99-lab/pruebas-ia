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
