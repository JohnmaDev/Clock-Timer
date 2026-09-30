#!/usr/bin/env python3
"""
Punto de entrada principal para la aplicación de Reloj y Temporizador Flotante.
Desarrollada en Python + PyQt6 para Ubuntu / Linux (y compatible con Windows).
"""
import sys
import os
import signal

# En Linux bajo sesión Wayland con XWayland activo, preferir 'xcb' con fallback a 'wayland' ("xcb;wayland")
# para que 'WindowStaysOnTopHint' (Always On Top) y el reposicionamiento de ventana funcionen en GNOME Mutter
if sys.platform.startswith("linux") and "QT_QPA_PLATFORM" not in os.environ:
    if os.environ.get("WAYLAND_DISPLAY") and os.environ.get("DISPLAY"):
        os.environ["QT_QPA_PLATFORM"] = "xcb;wayland"

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from app.window import FloatingClockTimerWindow

APP_ID = "io.github.JohnmaDev.Clock-Timer"

def get_app_icon_info():
    # 1. Rutas candidatas locales o empaquetadas prioritarias (para icon path en notify-send)
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(base_dir, "assets", "icons", "io.github.JohnmaDev.Clock-Timer.png"),
        os.path.join(base_dir, "icon.png"),
        os.path.join(base_dir, "io.github.JohnmaDev.Clock-Timer.png"),
        f"/app/share/icons/hicolor/512x512/apps/{APP_ID}.png",
        f"/usr/share/icons/hicolor/512x512/apps/{APP_ID}.png",
    ]
    for path in candidates:
        if os.path.exists(path):
            icon = QIcon(path)
            if not icon.isNull():
                return icon, path

    # 2. Intentar desde el tema del sistema (estándar FreeDesktop / Flatpak)
    theme_icon = QIcon.fromTheme(APP_ID)
    if not theme_icon.isNull():
        return theme_icon, APP_ID

    return QIcon(), None

def main():
    # Permite cerrar la aplicación limpiamente con Ctrl+C en la terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setApplicationName("ClockTimer")
    app.setApplicationDisplayName("Clock & Timer")
    app.setDesktopFileName(APP_ID)

    # Cargar icono de la aplicación (formato estándar circular con transparencia)
    app_icon, icon_path = get_app_icon_info()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    # Crear e instanciar la ventana flotante
    window = FloatingClockTimerWindow()
    window.setWindowTitle("Clock & Timer")
    window.icon_path = icon_path
    if not app_icon.isNull():
        window.setWindowIcon(app_icon)
        window.init_tray_icon(app_icon, icon_path)
    window.show()

    # Ejecutar el bucle de eventos principal de la aplicación
    sys.exit(app.exec())



if __name__ == "__main__":
    main()
