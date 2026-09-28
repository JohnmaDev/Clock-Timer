import subprocess
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QDialog, QSpinBox, QDialogButtonBox, QApplication
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QColor
from .i18n import i18n

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
        self.initial_seconds = 300  # 5 minutos por defecto
        self.remaining_seconds = self.initial_seconds
        self.is_running = False
        self.flash_state = False

        self.init_ui()
        self.init_timers()
        self.update_display()
        i18n.subscribe(self.retranslate_ui)


    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botones rápidos de preajustes (+1m, +5m, +25m Pomodoro)
        self.presets_layout = QHBoxLayout()
        self.presets_layout.setSpacing(4)
        self.presets_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        presets = [("+1m", 60), ("+5m", 300), ("+10m", 600), ("+25m", 1500)]
        for label, secs in presets:
            btn = QPushButton(label, self)
            btn.setProperty("class", "PresetButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, s=secs: self.add_time(s))
            self.presets_layout.addWidget(btn)

        # Botón para limpiar / poner a cero
        btn_clear = QPushButton("00:00", self)
        btn_clear.setProperty("class", "PresetButton")
        btn_clear.setToolTip("Restablecer a 0")
        btn_clear.clicked.connect(self.clear_time)
        self.presets_layout.addWidget(btn_clear)

        layout.addLayout(self.presets_layout)

        # Pantalla con el tiempo restante
        self.time_label = QLabel(self)
        self.time_label.setProperty("class", "TimeDisplay")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.time_label.setToolTip("Haz clic para escribir el tiempo exacto")
        self.time_label.mousePressEvent = self.open_setup_dialog

        layout.addWidget(self.time_label)

        # Subtítulo de estado
        self.status_label = QLabel(self)
        self.status_label.setProperty("class", "SecondaryText")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Controles principales: Iniciar/Pausar y Reiniciar
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_toggle = QPushButton(self)
        self.btn_toggle.setProperty("class", "PrimaryAction")
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.toggle_timer)

        self.btn_reset = QPushButton(self)
        self.btn_reset.setProperty("class", "SecondaryAction")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_timer)

        controls_layout.addWidget(self.btn_toggle)
        controls_layout.addWidget(self.btn_reset)
        layout.addLayout(controls_layout)

        self.retranslate_ui()

    def retranslate_ui(self):
        self.time_label.setToolTip(i18n.t("timer_click_tooltip"))
        self.btn_reset.setText(i18n.t("btn_reset"))
        if self.is_running:
            self.btn_toggle.setText(i18n.t("btn_pause"))
            self.status_label.setText(i18n.t("timer_hint_running"))
        elif self.remaining_seconds < self.initial_seconds and self.remaining_seconds > 0:
            self.btn_toggle.setText(i18n.t("btn_resume"))
            self.status_label.setText(i18n.t("timer_hint_paused"))
        elif self.remaining_seconds == 0:
            self.btn_toggle.setText(i18n.t("btn_start"))
            self.status_label.setText(i18n.t("timer_hint_finished"))
        else:
            self.btn_toggle.setText(i18n.t("btn_start"))
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
        if not self.is_running:
            self.initial_seconds = 0
            self.remaining_seconds = 0
            self.stop_alarm()
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
            return
        self.is_running = True
        self.timer.start()
        self.btn_toggle.setText(i18n.t("btn_pause"))
        self.status_label.setText(i18n.t("timer_hint_running"))
        self.btn_toggle.setStyleSheet("background-color: #ff9f1c; color: #141419;")
        self.time_label.setStyleSheet("color: #00d2ff;")

    def pause_timer(self):
        self.is_running = False
        self.timer.stop()
        self.btn_toggle.setText(i18n.t("btn_resume"))
        self.status_label.setText(i18n.t("timer_hint_paused"))
        self.btn_toggle.setStyleSheet("")
        self.time_label.setStyleSheet("color: #ffffff;")

    def reset_timer(self):
        self.stop_alarm()
        self.timer.stop()
        self.is_running = False
        self.remaining_seconds = self.initial_seconds
        self.btn_toggle.setText(i18n.t("btn_start"))
        self.btn_toggle.setStyleSheet("")
        self.time_label.setStyleSheet("color: #ffffff;")
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
            self.btn_toggle.setStyleSheet("")
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
            self.time_label.setStyleSheet("color: #ff3366; background-color: #331122; border-radius: 8px;")
            QApplication.beep()
        else:
            self.time_label.setStyleSheet("color: #ffffff; background-color: transparent;")

        # Detener la alarma automáticamente tras 12 parpadeos (~5 segundos)
        if self.alarm_count >= 12:
            self.stop_alarm()

    def stop_alarm(self):
        if self.alarm_timer.isActive():
            self.alarm_timer.stop()
            self.time_label.setStyleSheet("color: #ffffff; background-color: transparent;")
            self.status_label.setText(i18n.t("timer_hint_ready"))


    def update_display(self):
        hours = self.remaining_seconds // 3600
        mins = (self.remaining_seconds % 3600) // 60
        secs = self.remaining_seconds % 60

        if hours > 0:
            text = f"{hours:02d}:{mins:02d}:{secs:02d}"
        else:
            text = f"{mins:02d}:{secs:02d}"

        self.time_label.setText(text)

    def resizeEvent(self, event):
        """Ajusta proporcionalmente el tamaño de fuente según el tamaño de la ventana."""
        super().resizeEvent(event)
        w = self.width()
        h = self.height()
        base_size = min(w, h)
        font_size = max(18, int(base_size / 5.5))

        font = self.time_label.font()
        font.setPointSize(font_size)
        font.setBold(True)
        self.time_label.setFont(font)
