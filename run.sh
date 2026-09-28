#!/usr/bin/env bash
# Script para iniciar el Reloj & Temporizador Flotante

# Obtener el directorio donde reside este script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# Verificar si el entorno virtual existe, si no, crearlo e instalar dependencias
if [ ! -d ".venv" ]; then
    echo "⚡ Configurando entorno virtual por primera vez..."
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r requirements.txt
fi

# Ejecutar la aplicación
exec .venv/bin/python main.py "$@"
