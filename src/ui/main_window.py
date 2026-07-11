from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, \
    QProgressBar, QFrame
from PyQt6.QtCore import pyqtSlot
import darkdetect

from src.core.state_machine import UIState, StateMachine
from src.core.commands import FetchDataCommand
from src.core.engine import AsyncEngine
from src.ui.styles import DARK_STYLE, LIGHT_STYLE


class MainWindow(QMainWindow):
    def __init__(self, engine: AsyncEngine, state_machine: StateMachine, api_proxy):
        super().__init__()
        self.engine = engine
        self.state_machine = state_machine
        self.api_proxy = api_proxy

        self.setWindowTitle("The Resilience Architect - Dashboard")
        self.resize(600, 400)

        self._init_ui()
        self._setup_connections()
        self._apply_theme()

    def _init_ui(self):
        # Contenedor Central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)

        # Barra Superior de Control
        top_layout = QHBoxLayout()
        self.city_selector = QComboBox()
        self.city_selector.addItems(["CDMX", "Monterrey", "Guadalajara"])

        self.fetch_btn = QPushButton("Consultar Clima")
        top_layout.addWidget(QLabel("Seleccionar Ubicación:"))
        top_layout.addWidget(self.city_selector)
        top_layout.addWidget(self.fetch_btn)
        main_layout.addLayout(top_layout)

        # Barra de Progreso (Feedback de Asincronía)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Modo indeterminado / Shimmer effect conceptual
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        # Tarjeta de Datos (Empty State / Success State / Error State)
        self.card = QFrame()
        self.card.setObjectName("card")
        card_layout = QVBoxLayout(self.card)

        self.display_title = QLabel("Bienvenido al Arquitecto de Resiliencia")
        self.display_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.display_metrics = QLabel("Selecciona una ciudad para iniciar la consulta.")

        card_layout.addWidget(self.display_title)
        card_layout.addWidget(self.display_metrics)
        main_layout.addWidget(self.card)

        # Barra de Estado Inferior
        self.status_bar_layout = QHBoxLayout()
        self.engine_status = QLabel("Sistema Listo (Online)")
        self.engine_status.setObjectName("status_label")
        self.status_bar_layout.addWidget(self.engine_status)
        main_layout.addLayout(self.status_bar_layout)

    def _setup_connections(self):
        # Evento de Botón -> Dispara arquitectura desacoplada
        self.fetch_btn.clicked.connect(self._on_fetch_requested)

        # Patrón Observer: Escuchar cambios de estado globales
        self.state_machine.state_changed.connect(self.update_ui_state)

        # Escuchar bus de señales del motor asíncrono
        self.engine.slow_connection_detected.connect(self._on_slow_connection)

    def _apply_theme(self):
        # Easter Egg Bonus: Detectar automáticamente el modo del sistema operativo
        if darkdetect.isDark():
            self.setStyleSheet(DARK_STYLE)
        else:
            self.setStyleSheet(LIGHT_STYLE)

    def _on_fetch_requested(self):
        selected_city = self.city_selector.currentText()
        # Creamos el comando encapsulando la acción
        command = FetchDataCommand(self.api_proxy, selected_city, self.state_machine)

        # Le delegamos la ejecución asíncrona segura al motor con Exponential Backoff
        import asyncio
        asyncio.create_task(self.engine.run_command_with_retry(command))

    @pyqtSlot(str)
    def _on_slow_connection(self, message: str):
        self.engine_status.setText(message)
        self.engine_status.setStyleSheet("background-color: #FFB100; color: #121212;")

    @pyqtSlot(UIState, dict)
    def update_ui_state(self, state: UIState, payload: dict):
        """Mapeo reactivo de estados a elementos visuales de la UI (Cero parpadeos)"""
        if state == UIState.LOADING:
            self.progress_bar.show()
            self.fetch_btn.setEnabled(False)
            self.engine_status.setText("Cargando datos remotos...")
            self.engine_status.setStyleSheet("background-color: #1F1F1F; color: #E0E0E0;")

        elif state == UIState.SUCCESS:
            self.progress_bar.hide()
            self.fetch_btn.setEnabled(True)
            data = payload.get("data", {})
            self.display_title.setText(f"Clima en {self.city_selector.currentText()}")
            self.display_metrics.setText(
                f"Temperatura: {data.get('temp')}°C\nVelocidad Viento: {data.get('windspeed')} km/h")

            status = data.get("status", "Online")
            self.engine_status.setText(f"Estado: {status}")
            if "Offline" in status:
                self.engine_status.setStyleSheet("background-color: #533483; color: white;")  # Alerta caché
            else:
                self.engine_status.setStyleSheet("background-color: #00ADB5; color: #121212;")

        elif state == UIState.ERROR:
            self.progress_bar.hide()
            self.fetch_btn.setEnabled(True)
            error_msg = str(payload.get("error", "Error Desconocido"))

            self.display_title.setText("⚠️ Error de Recuperación")
            self.display_metrics.setText(f"No se pudieron sincronizar los datos.\nDetalle: {error_msg}")
            self.engine_status.setText("Fallo Crítico: Interfaz Protegida.")
            self.engine_status.setStyleSheet("background-color: #FF0055; color: white;")