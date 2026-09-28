from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QStackedWidget, QSizeGrip, QLabel, QSlider
)
from PyQt6.QtCore import Qt, QPoint, QEvent, QTimer
from PyQt6.QtGui import QCursor


from .clock_widget import ClockWidget
from .timer_widget import TimerWidget
from .draggable_widgets import DraggableTabButton
from .styles import MAIN_STYLE
from .i18n import i18n

BORDER_MARGIN = 8


class FloatingClockTimerWindow(QWidget):
    """
    Ventana flotante redimensionable para Ubuntu / Linux y Windows.
    Características:
      - 'Always on Top' permanente (siempre por encima de cualquier app).
      - Redimensionable desde los bordes o con el grip inferior.
      - Arrastrable haciendo clic en la barra superior o fondo.
      - Control de transparencia/opacidad con barra visual y rueda del ratón.
      - Alternancia fluida entre Reloj y Temporizador.
      - Aspecto oscuro moderno sin marcos toscos del sistema.
    """
    def __init__(self):
        super().__init__()
        self.always_on_top = True
        self.old_pos = None
        self.is_mini_mode = False

        self.init_window_flags()
        self.init_ui()

    def init_window_flags(self):
        """Configura los flags de ventana para que sea flotante y sin marco feo."""
        # WA_TranslucentBackground permite bordes redondeados limpios y elegantes
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)

        # Flags: Tipo Dialog (inmune a reordenamiento de mosaico Aero Snap) + Sin marco + Siempre Flotante (Always On Top)
        flags = Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        # Dimensiones iniciales y mínimas: Cuadrado compacto y cómodo
        self.resize(285, 255)
        self.setMinimumSize(210, 185)


    def init_ui(self):
        # Layout raíz que deja espacio transparente para el borde
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(6, 6, 6, 6)
        root_layout.setSpacing(0)

        # Contenedor principal con fondo oscuro y bordes redondeados
        self.container = QWidget(self)
        self.container.setObjectName("MainContainer")
        self.container.setStyleSheet(MAIN_STYLE)
        self.container.setMouseTracking(True)
        self.container.setCursor(Qt.CursorShape.ArrowCursor)
        self.container.installEventFilter(self)
        root_layout.addWidget(self.container)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(10, 8, 10, 8)
        container_layout.setSpacing(4)

        # 1. Barra de título y controles
        self.title_bar = QWidget(self.container)
        self.title_bar.setObjectName("TitleBar")
        self.title_bar.setToolTip("Arrastra para mover • Rueda del mouse para ajustar opacidad")
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(2, 2, 2, 2)
        title_layout.setSpacing(4)

        # Botones para cambiar entre Reloj y Temporizador (con arrastre dual estilo GNOME)
        self.btn_clock_tab = DraggableTabButton("Reloj", self.title_bar)
        self.btn_clock_tab.setProperty("class", "NavButton")
        self.btn_clock_tab.setCheckable(True)
        self.btn_clock_tab.setChecked(True)
        self.btn_clock_tab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clock_tab.clicked.connect(self.show_clock)

        self.btn_timer_tab = DraggableTabButton("Timer", self.title_bar)
        self.btn_timer_tab.setProperty("class", "NavButton")
        self.btn_timer_tab.setCheckable(True)
        self.btn_timer_tab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_timer_tab.clicked.connect(self.show_timer)

        title_layout.addWidget(self.btn_clock_tab)
        title_layout.addWidget(self.btn_timer_tab)
        title_layout.addStretch()

        # Botón Modo Mini-HUD / Enfoque (en normal muestra ↙ para compactar)
        self.btn_mini_hud = QPushButton("↙", self.title_bar)
        self.btn_mini_hud.setProperty("class", "WindowControl")
        self.btn_mini_hud.setObjectName("MiniHudButton")
        self.btn_mini_hud.clicked.connect(self.toggle_mini_hud)
        title_layout.addWidget(self.btn_mini_hud)

        # Botón Pin (Always on top toggle)
        self.btn_pin = QPushButton("📌", self.title_bar)
        self.btn_pin.setProperty("class", "WindowControl")
        self.btn_pin.setObjectName("PinButton")
        self.btn_pin.setCheckable(True)
        self.btn_pin.setChecked(True)
        self.btn_pin.setToolTip("Siempre al frente (Activado)")
        self.btn_pin.clicked.connect(self.toggle_pin)
        title_layout.addWidget(self.btn_pin)

        # Botón Ajustes (Opacidad e Idioma unificados)
        self.btn_settings = QPushButton("⚙", self.title_bar)
        self.btn_settings.setProperty("class", "WindowControl")
        self.btn_settings.setObjectName("SettingsButton")
        self.btn_settings.setCheckable(True)
        self.btn_settings.clicked.connect(self.toggle_settings_panel)
        title_layout.addWidget(self.btn_settings)

        # Botón Cerrar
        self.btn_close = QPushButton("✕", self.title_bar)
        self.btn_close.setProperty("class", "WindowControl")
        self.btn_close.setObjectName("CloseButton")
        self.btn_close.setToolTip("Cerrar")
        self.btn_close.clicked.connect(self.close)
        title_layout.addWidget(self.btn_close)

        container_layout.addWidget(self.title_bar)

        # 2. Panel desplegable unificado de Ajustes (Opacidad e Idioma)
        self.settings_panel = QWidget(self.container)
        self.settings_panel.setObjectName("SettingsPanel")
        self.settings_panel.hide()

        panel_layout = QVBoxLayout(self.settings_panel)
        panel_layout.setContentsMargins(8, 6, 8, 6)
        panel_layout.setSpacing(6)

        # Fila 1: Control de Opacidad
        op_row = QHBoxLayout()
        op_row.setSpacing(6)
        self.lbl_op = QLabel(self.settings_panel)
        self.lbl_op.setObjectName("OpacityLabel")

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal, self.settings_panel)
        self.opacity_slider.setRange(30, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.on_opacity_slider_changed)

        self.lbl_opacity_value = QLabel("100%", self.settings_panel)
        self.lbl_opacity_value.setObjectName("OpacityValue")

        btn_p50 = QPushButton("50%", self.settings_panel)
        btn_p50.setProperty("class", "OpacityPreset")
        btn_p50.clicked.connect(lambda: self.opacity_slider.setValue(50))

        btn_p75 = QPushButton("75%", self.settings_panel)
        btn_p75.setProperty("class", "OpacityPreset")
        btn_p75.clicked.connect(lambda: self.opacity_slider.setValue(75))

        btn_p100 = QPushButton("100%", self.settings_panel)
        btn_p100.setProperty("class", "OpacityPreset")
        btn_p100.clicked.connect(lambda: self.opacity_slider.setValue(100))

        op_row.addWidget(self.lbl_op)
        op_row.addWidget(self.opacity_slider, 1)
        op_row.addWidget(self.lbl_opacity_value)
        op_row.addWidget(btn_p50)
        op_row.addWidget(btn_p75)
        op_row.addWidget(btn_p100)
        panel_layout.addLayout(op_row)

        # Fila 2: Idioma
        lang_row = QHBoxLayout()
        lang_row.setSpacing(6)
        self.lbl_lang_setting = QLabel(self.settings_panel)
        self.lbl_lang_setting.setObjectName("SettingsLabel")

        self.btn_lang_es = QPushButton("Español", self.settings_panel)
        self.btn_lang_es.setProperty("class", "LangButton")
        self.btn_lang_es.setCheckable(True)
        self.btn_lang_es.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang_es.clicked.connect(lambda: self.switch_language("es"))

        self.btn_lang_en = QPushButton("English", self.settings_panel)
        self.btn_lang_en.setProperty("class", "LangButton")
        self.btn_lang_en.setCheckable(True)
        self.btn_lang_en.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang_en.clicked.connect(lambda: self.switch_language("en"))

        lang_row.addWidget(self.lbl_lang_setting)
        lang_row.addStretch()
        lang_row.addWidget(self.btn_lang_es)
        lang_row.addWidget(self.btn_lang_en)
        panel_layout.addLayout(lang_row)

        container_layout.addWidget(self.settings_panel)

        # 4. Pila de contenido (Reloj o Temporizador)
        self.stack = QStackedWidget(self.container)
        self.clock_widget = ClockWidget(self.stack)
        self.timer_widget = TimerWidget(self.stack)


        self.stack.addWidget(self.clock_widget)
        self.stack.addWidget(self.timer_widget)
        container_layout.addWidget(self.stack, 1)

        # 5. Barra inferior con SizeGrip para redimensionar con el mouse
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(0, 0, 0, 0)
        bottom_bar.addStretch()

        self.size_grip = QSizeGrip(self.container)
        bottom_bar.addWidget(self.size_grip)
        container_layout.addLayout(bottom_bar)

        # 6. Guardián de capa superior contra reordenamiento de Aero Snap
        self.keep_top_timer = QTimer(self)
        self.keep_top_timer.setInterval(1200)
        self.keep_top_timer.timeout.connect(self._ensure_always_on_top)
        self.keep_top_timer.start()

        # Aplicar textos y traducciones iniciales
        self.retranslate_ui()
        i18n.subscribe(self.retranslate_ui)


    def _ensure_always_on_top(self):
        """Mantiene la ventana al frente de la pila Z incluso si GNOME/Aero Snap reorganiza las capas."""
        if self.always_on_top and not self.isMinimized() and self.isVisible():
            self.raise_()

    def changeEvent(self, event):
        """Garantiza la prioridad superior en eventos de activación o mosaico del sistema."""
        if hasattr(self, 'always_on_top') and self.always_on_top:
            if event.type() in (QEvent.Type.ActivationChange, QEvent.Type.WindowStateChange):
                self.raise_()
        super().changeEvent(event)

    def show_clock(self):
        self.btn_clock_tab.setChecked(True)
        self.btn_timer_tab.setChecked(False)
        self.stack.setCurrentWidget(self.clock_widget)

    def show_timer(self):
        self.btn_clock_tab.setChecked(False)
        self.btn_timer_tab.setChecked(True)
        self.stack.setCurrentWidget(self.timer_widget)

    def toggle_mini_hud(self):
        """Alterna entre el Modo Normal y el Modo Mini-HUD / Enfoque compacto."""
        self.is_mini_mode = not getattr(self, "is_mini_mode", False)
        if self.is_mini_mode:
            self.saved_geometry = self.geometry()

            # Ocultar controles de la vista completa
            self.btn_clock_tab.hide()
            self.btn_timer_tab.hide()
            self.btn_pin.hide()
            self.btn_settings.hide()
            self.settings_panel.hide()
            self.size_grip.hide()

            # En modo mini: flecha ↗ para expandir y volver al tamaño normal
            self.btn_mini_hud.setText("↗")
            self.btn_mini_hud.setToolTip(i18n.t("mini_hud_expand"))

            self.timer_widget.set_mini_mode(True)
            self.clock_widget.set_mini_mode(True)

            self.title_bar.layout().setContentsMargins(4, 2, 4, 0)
            self.container.layout().setContentsMargins(6, 2, 6, 4)
            self.container.layout().setSpacing(0)

            self.setMinimumSize(210, 68)
            self.resize(240, 75)
        else:
            self.btn_clock_tab.show()
            self.btn_timer_tab.show()
            self.btn_pin.show()
            self.btn_settings.show()
            self.size_grip.show()

            # En modo normal: flecha ↙ para contraer al modo mini
            self.btn_mini_hud.setText("↙")
            self.btn_mini_hud.setToolTip(i18n.t("mini_hud_shrink"))

            self.timer_widget.set_mini_mode(False)
            self.clock_widget.set_mini_mode(False)

            self.title_bar.layout().setContentsMargins(2, 2, 2, 2)
            self.container.layout().setContentsMargins(10, 8, 10, 8)
            self.container.layout().setSpacing(4)

            self.setMinimumSize(210, 185)
            if hasattr(self, "saved_geometry"):
                self.setGeometry(self.saved_geometry)
            else:
                self.resize(285, 255)

    def toggle_pin(self):
        """Alterna el modo 'Siempre al frente' (Always on top)."""
        self.always_on_top = self.btn_pin.isChecked()
        flags = self.windowFlags()
        if self.always_on_top:
            flags |= (Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
            self.btn_pin.setToolTip("Siempre al frente (Activado)")
            if hasattr(self, 'keep_top_timer'):
                self.keep_top_timer.start()
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
            self.btn_pin.setToolTip("Modo normal (no fijado)")
            if hasattr(self, 'keep_top_timer'):
                self.keep_top_timer.stop()
        
        # Al cambiar flags en Qt, se debe re-mostrar la ventana
        pos = self.pos()
        self.setWindowFlags(flags)
        self.move(pos)
        self.show()
        if self.always_on_top:
            self.raise_()

    def toggle_settings_panel(self):
        """Muestra u oculta el panel unificado de ajustes (Opacidad e Idioma)."""
        is_visible = self.btn_settings.isChecked()
        self.settings_panel.setVisible(is_visible)

    def switch_language(self, lang):
        """Cambia el idioma global de la aplicación."""
        i18n.set_lang(lang)
        self.retranslate_ui()

    def retranslate_ui(self):
        """Actualiza todos los textos y tooltips de la ventana al idioma actual."""
        current = i18n.get_lang()
        self.btn_lang_es.setChecked(current == "es")
        self.btn_lang_en.setChecked(current == "en")

        self.btn_clock_tab.setText(i18n.t("tab_clock"))
        self.btn_timer_tab.setText(i18n.t("tab_timer"))

        if getattr(self, "is_mini_mode", False):
            self.btn_mini_hud.setToolTip(i18n.t("mini_hud_expand"))
        else:
            self.btn_mini_hud.setToolTip(i18n.t("mini_hud_shrink"))

        if self.always_on_top:
            self.btn_pin.setToolTip(i18n.t("pin_on"))
        else:
            self.btn_pin.setToolTip(i18n.t("pin_off"))

        self.btn_settings.setToolTip(i18n.t("settings_btn"))
        self.btn_close.setToolTip(i18n.t("close"))

        self.lbl_op.setText(i18n.t("opacity_lbl"))
        self.lbl_lang_setting.setText(i18n.t("lang_label"))
        self.size_grip.setToolTip(i18n.t("resize_tooltip"))
        self.title_bar.setToolTip(f"Opacidad: {self.opacity_slider.value()}% • {i18n.t('title_tooltip')}")

    def on_opacity_slider_changed(self, value):
        """Aplica el valor del slider a la opacidad de la ventana."""
        opacity = value / 100.0
        self.setWindowOpacity(opacity)
        self.lbl_opacity_value.setText(f"{value}%")
        self.title_bar.setToolTip(f"Opacidad: {value}% • {i18n.t('title_tooltip')}")


    # --- Filtro de eventos para restaurar el cursor de flecha inmediatamente ---
    def eventFilter(self, watched, event):
        if watched == self.container:
            if event.type() == QEvent.Type.Enter:
                self.unsetCursor()
                self.setCursor(Qt.CursorShape.ArrowCursor)
            elif event.type() == QEvent.Type.MouseMove:
                pos = self.mapFromGlobal(QCursor.pos())
                edge = self._get_edge_at(pos)
                if edge != Qt.Edge(0):
                    self._update_cursor(edge)
                else:
                    self.unsetCursor()
                    self.setCursor(Qt.CursorShape.ArrowCursor)
        return super().eventFilter(watched, event)

    def leaveEvent(self, event):
        """Restaura el cursor cuando el mouse sale de la ventana."""
        self.unsetCursor()
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)

    def start_window_drag(self):
        """Inicia el arrastre nativo de la ventana del sistema (Wayland/X11/Windows)."""
        handle = self.windowHandle()
        if handle and hasattr(handle, "startSystemMove"):
            if handle.startSystemMove():
                return
        self.old_pos = QCursor.pos()

    # --- Manejo de arrastre de la ventana y bordes de redimensionamiento ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            edge = self._get_edge_at(pos)

            if edge != Qt.Edge(0) and hasattr(self.windowHandle(), 'startSystemResize'):
                # Redimensionamiento nativo del sistema
                self.windowHandle().startSystemResize(edge)
            else:
                # Arrastre fluido desde cualquier parte libre o cabecera
                self.start_window_drag()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        edge = self._get_edge_at(pos)
        self._update_cursor(edge)

        if self.old_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.old_pos = None
        super().mouseReleaseEvent(event)

    def _get_edge_at(self, pos):
        """Determina si el cursor está cerca del borde para redimensionar."""
        edge = Qt.Edge(0)
        m = BORDER_MARGIN
        w = self.width()
        h = self.height()

        if pos.x() <= m:
            edge |= Qt.Edge.LeftEdge
        elif pos.x() >= w - m:
            edge |= Qt.Edge.RightEdge

        if pos.y() <= m:
            edge |= Qt.Edge.TopEdge
        elif pos.y() >= h - m:
            edge |= Qt.Edge.BottomEdge

        return edge

    def _update_cursor(self, edge):
        """Cambia el cursor según el borde que se esté tocando o lo restaura si no está en el borde."""
        if edge == (Qt.Edge.TopEdge | Qt.Edge.LeftEdge) or edge == (Qt.Edge.BottomEdge | Qt.Edge.RightEdge):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edge == (Qt.Edge.TopEdge | Qt.Edge.RightEdge) or edge == (Qt.Edge.BottomEdge | Qt.Edge.LeftEdge):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif edge in (Qt.Edge.LeftEdge, Qt.Edge.RightEdge):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif edge in (Qt.Edge.TopEdge, Qt.Edge.BottomEdge):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.unsetCursor()
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def wheelEvent(self, event):
        """Ajusta suavemente la opacidad de la ventana con la rueda del mouse sincronizado con el slider."""
        delta = event.angleDelta().y()
        step = 5 if delta > 0 else -5
        new_val = max(30, min(100, self.opacity_slider.value() + step))
        self.opacity_slider.setValue(new_val)
        super().wheelEvent(event)

    def keyPressEvent(self, event):
        """Atajos de teclado rápidos."""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_Tab:
            # Alternar pestaña con Tab
            if self.stack.currentWidget() == self.clock_widget:
                self.show_timer()
            else:
                self.show_clock()
        elif event.key() == Qt.Key.Key_Space:
            # Barra espaciadora inicia/pausa el temporizador si estamos en esa vista
            if self.stack.currentWidget() == self.timer_widget:
                self.timer_widget.toggle_timer()
        elif event.key() in (Qt.Key.Key_M, Qt.Key.Key_F):
            # 'M' (Mini) o 'F' (Focus) para alternar Modo Mini-HUD
            self.toggle_mini_hud()
        super().keyPressEvent(event)


