#!/usr/bin/env python3
"""
Punto de entrada principal para la aplicación de Reloj y Temporizador Flotante.
Desarrollada en Python + PyQt6 para Ubuntu / Linux (y compatible con Windows).
"""
import sys
import os
import signal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from app.window import FloatingClockTimerWindow

APP_ID = "io.github.JohnmaDev.ClockTimer"

def get_app_icon():
    # 1. Intentar desde el tema del sistema (estándar FreeDesktop / Flatpak)
    theme_icon = QIcon.fromTheme(APP_ID)
    if not theme_icon.isNull():
        return theme_icon
    
    # 2. Rutas candidatas locales o empaquetadas
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(base_dir, "icon.png"),
        os.path.join(base_dir, "io.github.JohnmaDev.ClockTimer.png"),
        os.path.join(base_dir, "assets", "icons", "io.github.JohnmaDev.ClockTimer.png"),
        f"/app/share/icons/hicolor/512x512/apps/{APP_ID}.png",
        f"/usr/share/icons/hicolor/512x512/apps/{APP_ID}.png",
    ]
    for path in candidates:
        if os.path.exists(path):
            icon = QIcon(path)
            if not icon.isNull():
                return icon
    return QIcon()

def main():
    # Permite cerrar la aplicación limpiamente con Ctrl+C en la terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setApplicationName("ClockTimer")
    app.setApplicationDisplayName("Clock & Timer")
    app.setDesktopFileName(APP_ID)

    # Cargar icono de la aplicación (formato estándar circular con transparencia)
    app_icon = get_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    # Crear e instanciar la ventana flotante
    window = FloatingClockTimerWindow()
    if not app_icon.isNull():
        window.setWindowIcon(app_icon)
    window.show()

    # Ejecutar el bucle de eventos principal de la aplicación
    sys.exit(app.exec())



if __name__ == "__main__":
    main()
