#!/usr/bin/env bash
# Script para iniciar el Reloj & Temporizador Flotante

# Obtener el directorio donde reside este script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# Verificar si el entorno virtual existe y está sano (detecta actualizaciones de versión de Python)
NEED_SETUP=0
if [ ! -d ".venv" ] || [ ! -x ".venv/bin/python" ]; then
    NEED_SETUP=1
elif ! .venv/bin/python -c "import PyQt6" >/dev/null 2>&1; then
    echo "⚠️  Detectado cambio en la versión de Python del sistema o entorno roto. Reconstruyendo .venv..."
    rm -rf .venv
    NEED_SETUP=1
fi

if [ "$NEED_SETUP" -eq 1 ]; then
    echo "⚡ Configurando entorno virtual..."
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r requirements.txt
fi

# Configurar plataforma Qt para Wayland con soporte Always on Top mediante XWayland
if [ -n "$WAYLAND_DISPLAY" ] && [ -n "$DISPLAY" ] && [ -z "$QT_QPA_PLATFORM" ]; then
    export QT_QPA_PLATFORM="xcb;wayland"
fi

# Ejecutar la aplicación
exec .venv/bin/python main.py "$@"
