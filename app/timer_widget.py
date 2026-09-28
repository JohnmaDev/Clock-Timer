import subprocess
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QDialog, QSpinBox, QDialogButtonBox, QApplication
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QColor
from .i18n import i18n
from .draggable_widgets import DualActionLabel

class TimeSetupDialog(QDialog):
    """Diálogo modal para configurar minutos y segundos con precisión."""
    def __init__(self, current_seconds, parent=None):
        super().__init__(parent)
        self.setWindowTitle(i18n.t("dialog_title"))
        self.setFixedSize(240, 160)

        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a24;
                color: #ffffff;
                border-radius: 12px;
                border: 1px solid #333348;
            }
            QLabel {
                color: #e0e0ec;
                font-size: 13px;
                font-weight: bold;
            }
            QSpinBox {
                background-color: #242434;
                color: #00d2ff;
                border: 1px solid #444458;
                border-radius: 6px;
                font-size: 16px;
                padding: 4px;
                min-width: 60px;
            }
            QPushButton {
                background-color: #00d2ff;
                color: #0a0e17;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #38e1ff;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Contenedor de inputs
        inputs_layout = QHBoxLayout()
        inputs_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Minutos
        v_min = QVBoxLayout()
        lbl_min = QLabel(i18n.t("dialog_min"))
        self.spin_min = QSpinBox()
        self.spin_min.setRange(0, 999)
        self.spin_min.setValue(current_seconds // 60)
        v_min.addWidget(lbl_min)
        v_min.addWidget(self.spin_min)

        # Segundos
        v_sec = QVBoxLayout()
        lbl_sec = QLabel(i18n.t("dialog_sec"))
        self.spin_sec = QSpinBox()
        self.spin_sec.setRange(0, 59)
        self.spin_sec.setValue(current_seconds % 60)
        v_sec.addWidget(lbl_sec)
        v_sec.addWidget(self.spin_sec)


        inputs_layout.addLayout(v_min)
        inputs_layout.addLayout(v_sec)
        layout.addLayout(inputs_layout)

        # Botones de Aceptar / Cancelar
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def get_total_seconds(self):
        return (self.spin_min.value() * 60) + self.spin_sec.value()


class TimerWidget(QWidget):
    """
    Widget de temporizador configurable con inicio, pausa, reinicio,
    preajustes rápidos y alarma visual/sonora al finalizar.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initial_seconds = 0  # Inicia en 00:00 por defecto
        self.remaining_seconds = 0
        self.is_running = False
        self.flash_state = False

        self.init_ui()
        self.init_timers()
        self.update_display()
        i18n.subscribe(self.retranslate_ui)


    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # --- VISTA NORMAL ---
        self.view_normal = QWidget(self)
        normal_layout = QVBoxLayout(self.view_normal)
        normal_layout.setContentsMargins(10, 6, 10, 6)
        normal_layout.setSpacing(4)
        normal_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botones rápidos de preajustes (+1m, +5m, +15m, +25m, +1h)
        self.presets_widget = QWidget(self.view_normal)
        self.presets_layout = QHBoxLayout(self.presets_widget)
        self.presets_layout.setContentsMargins(0, 0, 0, 0)
        self.presets_layout.setSpacing(4)
        self.presets_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        presets = [("+1m", 60), ("+5m", 300), ("+15m", 900), ("+25m", 1500), ("+1h", 3600)]
        for label, secs in presets:
            btn = QPushButton(label, self.presets_widget)
            btn.setProperty("class", "PresetButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, s=secs: self.add_time(s))
            self.presets_layout.addWidget(btn)

        normal_layout.addWidget(self.presets_widget)

        # Pantalla con el tiempo restante (efecto dual: clic para configurar, arrastre para mover)
        self.time_label = DualActionLabel("", self.view_normal, on_click=self.open_setup_dialog)
        self.time_label.setProperty("class", "TimeDisplay")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.time_label.setToolTip("Haz clic para escribir el tiempo exacto")
        normal_layout.addWidget(self.time_label)

        # Subtítulo de estado
        self.status_label = QLabel(self.view_normal)
        self.status_label.setProperty("class", "SecondaryText")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        normal_layout.addWidget(self.status_label)

        # Controles principales: Iniciar/Pausar, Reiniciar y Borrar/Papelera
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(6)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_toggle = QPushButton(self.view_normal)
        self.btn_toggle.setProperty("class", "PrimaryAction")
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.toggle_timer)

        self.btn_reset = QPushButton(self.view_normal)
        self.btn_reset.setProperty("class", "SecondaryAction")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_timer)

        self.btn_clear = QPushButton(self.view_normal)
        self.btn_clear.setProperty("class", "SecondaryAction")
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.clicked.connect(self.clear_time)

        controls_layout.addWidget(self.btn_toggle)
        controls_layout.addWidget(self.btn_reset)
        controls_layout.addWidget(self.btn_clear)
        normal_layout.addLayout(controls_layout)

        root_layout.addWidget(self.view_normal)

        # --- VISTA MINI-HUD (Horizontal compacta) ---
        self.view_mini = QWidget(self)
        self.view_mini.hide()
        mini_layout = QHBoxLayout(self.view_mini)
        mini_layout.setContentsMargins(10, 2, 10, 2)
        mini_layout.setSpacing(10)
        mini_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botón Play/Pause circular compacto
        self.btn_mini_toggle = QPushButton("▶", self.view_mini)
        self.btn_mini_toggle.setProperty("class", "MiniAction")
        self.btn_mini_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mini_toggle.setToolTip("Iniciar / Pausar")
        self.btn_mini_toggle.clicked.connect(self.toggle_timer)
        mini_layout.addWidget(self.btn_mini_toggle)

        # Tiempo centrado (efecto dual: clic para pausar/reanudar, arrastre para mover)
        self.mini_time_label = DualActionLabel("", self.view_mini, on_click=self.toggle_timer)
        self.mini_time_label.setProperty("class", "TimeDisplay")
        self.mini_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mini_time_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mini_time_label.setToolTip("Clic para pausar / reanudar")
        mini_layout.addWidget(self.mini_time_label, 1)

        # Botón Reset circular compacto
        self.btn_mini_reset = QPushButton("↺", self.view_mini)
        self.btn_mini_reset.setProperty("class", "MiniReset")
        self.btn_mini_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mini_reset.setToolTip("Reiniciar")
        self.btn_mini_reset.clicked.connect(self.reset_timer)
        mini_layout.addWidget(self.btn_mini_reset)

        root_layout.addWidget(self.view_mini)

        self.retranslate_ui()

    def retranslate_ui(self):
        self.time_label.setToolTip(i18n.t("timer_click_tooltip"))
        self.btn_reset.setText(i18n.t("btn_reset"))
        self.btn_clear.setText("🗑 " + i18n.t("btn_clear"))
        self.btn_clear.setToolTip(i18n.t("btn_clear_tooltip"))
        if self.is_running:
            self.btn_toggle.setText(i18n.t("btn_pause"))
            self.btn_mini_toggle.setText("⏸")
            self.status_label.setText(i18n.t("timer_hint_running"))
        elif self.remaining_seconds < self.initial_seconds and self.remaining_seconds > 0:
            self.btn_toggle.setText(i18n.t("btn_resume"))
            self.btn_mini_toggle.setText("▶")
            self.status_label.setText(i18n.t("timer_hint_paused"))
        elif self.remaining_seconds == 0:
            self.btn_toggle.setText(i18n.t("btn_start"))
            self.btn_mini_toggle.setText("▶")
            self.status_label.setText(i18n.t("timer_hint_idle") if self.initial_seconds == 0 else i18n.t("timer_hint_finished"))
        else:
            self.btn_toggle.setText(i18n.t("btn_start"))
            self.btn_mini_toggle.setText("▶")
            self.status_label.setText(i18n.t("timer_hint_idle"))


    def init_timers(self):
        # Timer de cuenta regresiva
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.tick)

        # Timer de alarma / parpadeo visual
        self.alarm_timer = QTimer(self)
        self.alarm_timer.setInterval(400)
        self.alarm_timer.timeout.connect(self.flash_alarm)
        self.alarm_count = 0

    def add_time(self, seconds):
        if self.is_running:
            self.remaining_seconds += seconds
        else:
            self.initial_seconds += seconds
            self.remaining_seconds = self.initial_seconds
        self.stop_alarm()
        self.update_display()

    def clear_time(self):
        self.stop_alarm()
        self.timer.stop()
        self.is_running = False
        self.initial_seconds = 0
        self.remaining_seconds = 0
        self.btn_toggle.setText(i18n.t("btn_start"))
        self.btn_mini_toggle.setText("▶")
        self.btn_toggle.setStyleSheet("")
        self.btn_mini_toggle.setStyleSheet("")
        self.time_label.setStyleSheet("color: #ffffff;")
        self.mini_time_label.setStyleSheet("color: #ffffff;")
        self.status_label.setText(i18n.t("timer_hint_idle"))
        self.update_display()

    def open_setup_dialog(self, event=None):
        if self.is_running:
            return
        dialog = TimeSetupDialog(self.remaining_seconds, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            total = dialog.get_total_seconds()
            self.initial_seconds = total
            self.remaining_seconds = total
            self.stop_alarm()
            self.update_display()

    def toggle_timer(self):
        if self.alarm_timer.isActive():
            self.stop_alarm()
            return

        if self.is_running:
            self.pause_timer()
        else:
            self.start_timer()

    def start_timer(self):
        if self.remaining_seconds <= 0:
            self.open_setup_dialog()
            return
        self.is_running = True
        self.timer.start()
        self.btn_toggle.setText(i18n.t("btn_pause"))
        self.btn_mini_toggle.setText("⏸")
        self.status_label.setText(i18n.t("timer_hint_running"))
        self.btn_toggle.setStyleSheet("background-color: #ff9f1c; color: #141419;")
        self.btn_mini_toggle.setStyleSheet("background-color: #ff9f1c; color: #141419;")
        self.time_label.setStyleSheet("color: #00d2ff;")
        self.mini_time_label.setStyleSheet("color: #00d2ff;")

    def pause_timer(self):
        self.is_running = False
        self.timer.stop()
        self.btn_toggle.setText(i18n.t("btn_resume"))
        self.btn_mini_toggle.setText("▶")
        self.status_label.setText(i18n.t("timer_hint_paused"))
        self.btn_toggle.setStyleSheet("")
        self.btn_mini_toggle.setStyleSheet("")
        self.time_label.setStyleSheet("color: #ffffff;")
        self.mini_time_label.setStyleSheet("color: #ffffff;")

    def reset_timer(self):
        self.stop_alarm()
        self.timer.stop()
        self.is_running = False
        self.remaining_seconds = self.initial_seconds
        self.btn_toggle.setText(i18n.t("btn_start"))
        self.btn_mini_toggle.setText("▶")
        self.btn_toggle.setStyleSheet("")
        self.btn_mini_toggle.setStyleSheet("")
        self.time_label.setStyleSheet("color: #ffffff;")
        self.mini_time_label.setStyleSheet("color: #ffffff;")
        self.status_label.setText(i18n.t("timer_hint_idle"))
        self.update_display()

    def tick(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_display()
        else:
            self.timer.stop()
            self.is_running = False
            self.btn_toggle.setText(i18n.t("btn_start"))
            self.btn_mini_toggle.setText("▶")
            self.btn_toggle.setStyleSheet("")
            self.btn_mini_toggle.setStyleSheet("")
            self.status_label.setText(i18n.t("timer_hint_finished"))
            self.trigger_alarm()

    def trigger_alarm(self):
        self.alarm_count = 0
        self.alarm_timer.start()

        # Sonido nativo del sistema
        QApplication.beep()

        # Notificación de escritorio en Ubuntu/Linux
        if shutil.which("notify-send"):
            try:
                subprocess.Popen([
                    "notify-send", 
                    "-u", "critical", 
                    "-t", "5000", 
                    i18n.t("notif_title"), 
                    i18n.t("notif_msg")
                ])
            except Exception:
                pass


    def flash_alarm(self):
        self.alarm_count += 1
        self.flash_state = not self.flash_state
        if self.flash_state:
            alert_style = "color: #ff3366; background-color: #331122; border-radius: 8px;"
            self.time_label.setStyleSheet(alert_style)
            self.mini_time_label.setStyleSheet(alert_style)
            QApplication.beep()
        else:
            self.time_label.setStyleSheet("color: #ffffff; background-color: transparent;")
            self.mini_time_label.setStyleSheet("color: #ffffff; background-color: transparent;")

        # Detener la alarma automáticamente tras 12 parpadeos (~5 segundos)
        if self.alarm_count >= 12:
            self.stop_alarm()

    def stop_alarm(self):
        if self.alarm_timer.isActive():
            self.alarm_timer.stop()
            self.time_label.setStyleSheet("color: #ffffff; background-color: transparent;")
            self.mini_time_label.setStyleSheet("color: #ffffff; background-color: transparent;")
            self.status_label.setText(i18n.t("timer_hint_ready"))


    def update_display(self):
        hours = self.remaining_seconds // 3600
        mins = (self.remaining_seconds % 3600) // 60
        secs = self.remaining_seconds % 60

        if hours > 0:
            text = f"{hours:02d}:{mins:02d}:{secs:02d}"
        else:
            text = f"{mins:02d}:{secs:02d}"

        old_text = self.mini_time_label.text()
        self.time_label.setText(text)
        self.mini_time_label.setText(text)

        # Si cambió el formato (ej. de MM:SS a HH:MM:SS o viceversa), reajustar fuente al instante
        if len(text) != len(old_text):
            self.resizeEvent(None)

    def set_mini_mode(self, enabled: bool):
        self.is_mini_mode = enabled
        self.view_normal.setVisible(not enabled)
        self.view_mini.setVisible(enabled)
        self.btn_mini_toggle.setText("⏸" if self.is_running else "▶")
        self.resizeEvent(None)

    def resizeEvent(self, event):
        """Ajusta proporcionalmente el tamaño de fuente según el tamaño de la ventana."""
        if event is not None:
            super().resizeEvent(event)
        w = self.width()
        h = self.height()
        if getattr(self, "is_mini_mode", False):
            text = self.mini_time_label.text()
            if len(text) > 5:
                # Tiempo largo con horas (ej: 01:39:51 tiene 8 caracteres) -> tamaño legible y balanceado
                font_size = max(15, min(20, int(h * 0.45)))
            else:
                # Tiempo normal (ej: 05:00 tiene 5 caracteres)
                font_size = max(18, min(26, int(h * 0.55)))
            font = self.mini_time_label.font()
            font.setPointSize(font_size)
            font.setBold(True)
            self.mini_time_label.setFont(font)
        else:
            base_size = min(w, h)
            font_size = max(18, int(base_size / 5.5))
            font = self.time_label.font()
            font.setPointSize(font_size)
            font.setBold(True)
            self.time_label.setFont(font)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            win = self.window()
            if hasattr(win, "start_window_drag"):
                win.start_window_drag()
        super().mousePressEvent(event)
